import asyncio
import os
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.api.v1.auth import get_current_user, get_current_session
from app.core.logging import logger
from app.models.session import Session
from app.services import database_service
from app.services.embeddings import embedding_pipeline
from app.services.s3 import s3_service

router = APIRouter()

# Где хранить файлы
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Разрешенные типы и расширения
ALLOWED_CONTENT_TYPES = {
    # images
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    # docs
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".pdf", ".docx"}

# Лимит на размер файла (байты) — 20 MB по умолчанию
MAX_FILE_SIZE = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(20 * 1024 * 1024)))


async def _write_file_async(dest_path: Path, data: bytes) -> None:
    """
    Без зависимости от aiofiles: пишем синхронно в threadpool, чтобы не блокировать event loop.
    """

    def _write():
        with open(dest_path, "wb") as f:
            f.write(data)

    await asyncio.to_thread(_write)


async def _save_upload_file(file: UploadFile, dest_dir: Path) -> dict:
    # Базовая валидация
    ext = Path(file.filename or "").suffix.lower()
    if (file.content_type not in ALLOWED_CONTENT_TYPES) or (ext not in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: content_type={file.content_type}, extension={ext}",
        )

    # Читаем по кускам с контролем размера
    size = 0
    chunks: list[bytes] = []
    while True:
        chunk = await file.read(1024 * 1024)  # 1 MB
        if not chunk:
            break
        size += len(chunk)
        if size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File is too large (>{MAX_FILE_SIZE} bytes)",
            )
        chunks.append(chunk)

    data = b"".join(chunks)

    # Генерим имя, сохраняем расширение
    stored_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = dest_dir / stored_name

    await _write_file_async(dest_path, data)

    # Немного логов
    logger.info(
        "file_uploaded",
        original_name=file.filename,
        stored_name=stored_name,
        content_type=file.content_type,
        size=size,
        path=str(dest_path),
    )

    # Вернем метаданные и относительный URL (подстрой под свой статику/проксирование)
    return {
        "original_name": file.filename,
        "stored_name": stored_name,
        "content_type": file.content_type,
        "size": size,
        "url": f"/static/uploads/{stored_name}",  # например, если Nginx/StaticFiles отдают эту папку
        "path": str(dest_path),  # внутренний путь (можно не отдавать наружу)
    }


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload files (docx, pdf, images)",
)
async def upload_files(
        current_session: Session = Depends(get_current_session),
        files: List[UploadFile] = File(..., description="One or more files"),

):
    """
    Загружает один или несколько файлов (.docx, .pdf, изображения) на сервер.

    Возвращает список с метаданными загруженных файлов.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    session_id = current_session.id
    user_id=current_session.user_id

    results = []
    for f in files:
        file_id = uuid.uuid4().hex
        name = f.filename or up["stored_name"]
        # 1) Заливаем в S3
        up = await s3_service.upload_file(
            file=f,
            session_id=session_id,
        )
        await f.seek(0)
        embedding = embedding_pipeline.index_file(file_id=file_id, filename=name, content_type=up["content_type"],
                                                  file_bytes= await f.read())

        obj = await database_service.create_file_object(
            id=file_id,
            file_name=name,
            description="",
            vector = embedding,
            created_by=str(user_id),
            session_id=session_id,
            file_type=up["content_type"],
            s3_key=up["key"],
            s3_url=up["url"],
        )

        results.append({
            "id": obj.id,
            "file_name": obj.file_name,
            "file_type": obj.file_type,
            "url": obj.s3_url,
            "s3_key": obj.s3_key,
        })

    logger.info("files_uploaded_and_recorded", count=len(results), session_id=session_id, user_id=user_id)
    return {"files": results}
