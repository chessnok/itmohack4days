import io
import mimetypes
from typing import List

import docx2txt
import pytesseract
from fastapi import APIRouter
from langchain_openai import OpenAIEmbeddings

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pdfreader.types import Image
from pypdf import PdfReader

router = APIRouter()


from app.core.config import settings
from app.core.logging import logger
from app.services.database import database_service


class EmbeddingPipeline:
    """
    Готовит текст, режет на куски, строит эмбеддинги, сохраняет в file_chunks (pgvector).
    """
    def __init__(self):
        self.emb = OpenAIEmbeddings(
            api_key=settings.LLM_API_KEY,
            model=settings.EMBEDDING_MODEL,
            openai_api_base=settings.EVALUATION_BASE_URL
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            length_function=len,
        )

    def _chunks(self, text: str) -> List[str]:
        return self.splitter.split_text(text)


    def index_file(
            self,
            *,
            file_id: str,
            filename: str,
            content_type: str,
            file_bytes: bytes,
    ) -> int:
        """
        Полный цикл: извлечь текст → разбить → создать эмбеддинги → сохранить.
        Возвращает количество сохраненных чанков.
        """
        # 1) извлечь текст
        text = FileTextExtractor.extract(file_bytes, filename, content_type)
        if not text:
            logger.warning("embedding_empty_text", file_id=file_id, filename=filename)
            return 0

        chunks = self._chunks(text)
        if not chunks:
            return 0

        vectors = self.emb.embed_documents(chunks)

        with database_service.get_session_maker() as sql_sess:
            database_service._insert_chunks(sql_sess, file_id, chunks, vectors)

        logger.info("embedding_indexed", file_id=file_id, chunks=len(chunks))
        return len(chunks)

class FileTextExtractor:
    @staticmethod
    def _is_pdf(content_type: str, filename: str) -> bool:
        return (content_type == "application/pdf") or (filename.lower().endswith(".pdf"))

    @staticmethod
    def _is_docx(content_type: str, filename: str) -> bool:
        return (
                content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                or filename.lower().endswith(".docx")
        )

    @staticmethod
    def _is_image(content_type: str, filename: str) -> bool:
        t = content_type or mimetypes.guess_type(filename or "")[0] or ""
        return t.startswith("image/")

    @staticmethod
    def extract(file_bytes: bytes, filename: str, content_type: str) -> str:
        if FileTextExtractor._is_pdf(content_type, filename):
            return FileTextExtractor._extract_pdf(file_bytes)
        if FileTextExtractor._is_docx(content_type, filename):
            return FileTextExtractor._extract_docx(file_bytes)
        if FileTextExtractor._is_image(content_type, filename):
            return FileTextExtractor._extract_image_ocr(file_bytes)
        # fallback – как бинарь не поддерживаем
        raise ValueError(f"Unsupported file type for embeddings: {content_type} / {filename}")

    @staticmethod
    def _extract_pdf(file_bytes: bytes) -> str:
        reader = PdfReader(io.BytesIO(file_bytes))
        texts = []
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                pass
        return "\n".join(t for t in texts if t).strip()

    @staticmethod
    def _extract_docx(file_bytes: bytes) -> str:
        # docx2txt работает с путем, поэтому читаем через NamedTemporaryFile по-хорошему.
        # Но можно через BytesIO -> сохраняем во временный файл.
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".docx") as tmp:
            tmp.write(file_bytes)
            tmp.flush()
            text = docx2txt.process(tmp.name) or ""
        return text.strip()

    @staticmethod
    def _extract_image_ocr(file_bytes: bytes) -> str:
        img = Image.open(io.BytesIO(file_bytes))
        # при желании: img = img.convert("L") для улучшения OCR
        text = pytesseract.image_to_string(img, lang="eng+rus")
        return (text or "").strip()

embedding_pipeline = EmbeddingPipeline()
