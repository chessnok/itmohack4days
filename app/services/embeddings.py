import mimetypes
from typing import List

import docx2txt
import numpy as np
from PIL import ImageOps
from fastapi import APIRouter
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.utils.graph import tokenizer

router = APIRouter()


from app.core.config import settings
from app.core.logging import logger
from app.services.database import database_service


class EmbeddingPipeline:
    """
    Готовит текст, режет на куски, строит эмбеддинги, сохраняет в file_chunks (pgvector).
    """
    def __init__(self):
        if settings.PROVIDER == "YANDEX":
            from app.services.yandex import embeddings
            self.emb = embeddings
        else:
            from langchain_openai import OpenAIEmbeddings

            self.emb = OpenAIEmbeddings(
                api_key=settings.LLM_API_KEY,
                model=settings.EMBEDDING_MODEL,
                openai_api_base=settings.EVALUATION_BASE_URL
            )

        self.splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer = tokenizer,
            chunk_size=1000,
            chunk_overlap=100,
            separators=[
                "\n\n",                # разделы / абзацы
                "СТРАНИЦА",            # иногда встречается при OCR PDF
                "Раздел", "Пункт", "Приложение", "Прил.",  # правовые структуры
                "ПРИЛОЖЕНИЕ", "ПОДПИСИ", "ПОДПИСАНО",
                "ДОГОВОР", "АКТ", "СЧЕТ-ФАКТУРА",
                "Универсальный передаточный документ", "Товарная накладная",
                "\n",                  # строки, если ничего не подошло
                " ",                   # fallback — символы
            ],
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
    ):
        """
        Полный цикл: извлечь текст → разбить → создать эмбеддинги → сохранить.
        Возвращает количество сохраненных чанков.
        """
        # 1) извлечь текст
        text = FileTextExtractor.extract(file_bytes, filename, content_type)
        if not text:
            logger.warning("embedding_empty_text", file_id=file_id, filename=filename)
            return [], ""

        chunks = self._chunks(text)
        if not chunks:
            return [], ""

        vectors = self.emb.embed_documents(chunks)

        with database_service.get_session_maker() as sql_sess:
            database_service._insert_chunks(sql_sess, file_id, chunks, vectors)

        logger.info("embedding_indexed", file_id=file_id, chunks=len(chunks))
        return np.mean(np.array(vectors, dtype=float), axis=0).tolist(), text

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
    def _extract_pdf(file_bytes: bytes, *, ocr_lang: str = "eng+rus", ocr_pages_limit: int = 5) -> str:
        """
        Надёжная экстракция текста из PDF:
        1) PyPDF (быстро, если нормальный текстовый слой)
        2) pdfminer.six (лучше справляется с битой структурой)
        3) OCR через pypdfium2 + pytesseract (на первых N страниц)
        """
        # If это не особо похоже на PDF — сразу в OCR-фоллбек (или возврат "")
        if not _looks_like_pdf(file_bytes):
            return _pdf_ocr_fallback(file_bytes, ocr_lang, ocr_pages_limit)

        # 1) PyPDF
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            texts = []
            for page in reader.pages:
                try:
                    texts.append(page.extract_text() or "")
                except Exception:
                    # Падение на одной странице не должно ломать весь документ
                    continue
            text = "\n".join(t for t in texts if t).strip()
            if text:
                return text
        except (PdfStreamError, Exception):
            # пойдём дальше
            pass

        # 2) pdfminer.six
        try:
            text = pdfminer_extract_text(io.BytesIO(file_bytes)) or ""
            text = text.strip()
            if text:
                return text
        except Exception:
            pass

        # 3) OCR (если доступно)
        return _pdf_ocr_fallback(file_bytes, ocr_lang, ocr_pages_limit)


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
        # 1) Открытие + исправление EXIF-ориентации
        img = Image.open(io.BytesIO(file_bytes))
        img = ImageOps.exif_transpose(img)

        # 2) В градации серого
        img = img.convert("L")

        text = pytesseract.image_to_string(img, lang="rus+eng")
        return (text or "").strip()

embedding_pipeline = EmbeddingPipeline()



import io

from pypdf import PdfReader
from pypdf.errors import PdfStreamError
from pdfminer.high_level import extract_text as pdfminer_extract_text


import pypdfium2 as pdfium

from PIL import Image
import pytesseract


def _looks_like_pdf(data: bytes) -> bool:
    # Простая проверка сигнатуры
    return data.startswith(b"%PDF")


def _pdf_ocr_fallback(file_bytes: bytes, ocr_lang: str, pages_limit: int) -> str:

    try:
        pdf = pdfium.PdfDocument(io.BytesIO(file_bytes))
        n = min(len(pdf), max(1, pages_limit))
        out_texts = []
        for i in range(n):
            page = pdf[i]
            # Рендерим в растровое изображение
            pil_image = page.render(scale=2).to_pil()  # scale>1 для улучшения OCR
            # При желании: pil_image = pil_image.convert("L")
            txt = pytesseract.image_to_string(pil_image, lang=ocr_lang) or ""
            txt = txt.strip()
            if txt:
                out_texts.append(txt)
        return "\n\n".join(out_texts).strip()
    except Exception:
        return ""

