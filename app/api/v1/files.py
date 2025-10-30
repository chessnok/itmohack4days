import asyncio
import io
import json
import mimetypes
import os
import tarfile
import uuid
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import List, Dict, Any, Optional, Iterable, Tuple
import py7zr
import rarfile


from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.api.v1.auth import get_current_session
from app.core.logging import logger
from app.models.session import Session
from app.services import database_service
from app.services.classifier import classifier_service
from app.services.embeddings import embedding_pipeline
from app.services.parser import parser_service
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





MAX_ARCHIVE_MEMBERS = 500           # лимит числа файлов в архиве
MAX_MEMBER_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB на один файл
ALLOWED_EXTS = {".pdf", ".docx", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}

def _is_json(s: str) -> bool:
    try:
        json.loads(s)
        return True
    except Exception:
        return False

def _is_archive(filename: str, content_type: Optional[str]) -> bool:
    name = (filename or "").lower()
    if name.endswith((".zip", ".rar", ".7z", ".tar", ".tgz", ".tar.gz", ".tbz2", ".tar.bz2")):
        return True
    if content_type and content_type.startswith("application/"):
        return content_type in {
            "application/zip",
            "application/x-7z-compressed",
            "application/x-rar-compressed",
            "application/x-tar",
            "application/gzip",
            "application/x-bzip2",
        }
    return False

def _guess_type_by_name(name: str) -> str:
    return mimetypes.guess_type(name)[0] or "application/octet-stream"

def _ext_allowed(name: str) -> bool:
    for ext in ALLOWED_EXTS:
        if name.lower().endswith(ext):
            return True
    return False

def _is_macos_junk(name: str) -> bool:
    lname = name.lstrip("/").replace("\\", "/")
    return lname.startswith("__MACOSX/") or os.path.basename(lname).startswith("._")

def _is_safe_member(name: str) -> bool:
    p = PurePosixPath("/" + name.lstrip("/"))
    # запретим абсолюты и выход за корень
    return not any(part in ("..",) for part in p.parts)

# в _iter_zip / _iter_rar / _iter_7z / _iter_tar перед yield добавьте:


def _iter_zip(file_bytes: bytes) -> Iterable[Tuple[str, bytes]]:
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:

        infos = zf.infolist()
        if len(infos) > MAX_ARCHIVE_MEMBERS:
            raise HTTPException(400, detail=f"Archive too large: more than {MAX_ARCHIVE_MEMBERS} entries")
        for info in infos:
            if _is_macos_junk(info.filename) or not _is_safe_member(info.filename):
                continue
            if info.is_dir():
                continue
            if info.file_size > MAX_MEMBER_SIZE_BYTES:
                logger.warning("archive_entry_skipped_size", name=info.filename, size=info.file_size)
                continue
            yield info.filename, zf.read(info)

def _iter_tar(file_bytes: bytes) -> Iterable[Tuple[str, bytes]]:
    with tarfile.open(fileobj=io.BytesIO(file_bytes), mode="r:*") as tf:
        members = tf.getmembers()
        if len(members) > MAX_ARCHIVE_MEMBERS:
            raise HTTPException(400, detail=f"Archive too large: more than {MAX_ARCHIVE_MEMBERS} entries")
        for m in members:
            if not m.isfile():
                continue
            if m.size and m.size > MAX_MEMBER_SIZE_BYTES:
                logger.warning("archive_entry_skipped_size", name=m.name, size=m.size)
                continue
            fobj = tf.extractfile(m)
            if fobj is None:
                continue
            yield m.name, fobj.read()

def _iter_7z(file_bytes: bytes) -> Iterable[Tuple[str, bytes]]:
    with py7zr.SevenZipFile(io.BytesIO(file_bytes), mode="r") as z:
        files_map = z.readall()  # dict[name] = BytesIO
        if len(files_map) > MAX_ARCHIVE_MEMBERS:
            raise HTTPException(400, detail=f"Archive too large: more than {MAX_ARCHIVE_MEMBERS} entries")
        for name, bio in files_map.items():
            if _is_macos_junk(name) or not _is_safe_member(name):
                continue
            bio.seek(0, io.SEEK_END)
            size = bio.tell()
            if size > MAX_MEMBER_SIZE_BYTES:
                logger.warning("archive_entry_skipped_size", name=name, size=size)
                continue
            bio.seek(0)
            yield name, bio.read()

def _iter_rar(file_bytes: bytes) -> Iterable[Tuple[str, bytes]]:
    with rarfile.RarFile(io.BytesIO(file_bytes)) as rf:
        infos = rf.infolist()
        if len(infos) > MAX_ARCHIVE_MEMBERS:
            raise HTTPException(400, detail=f"Archive too large: more than {MAX_ARCHIVE_MEMBERS} entries")
        for info in infos:
            if _is_macos_junk(info.filename) or not _is_safe_member(info.filename):
                continue
            if info.isdir():
                continue
            if info.file_size and info.file_size > MAX_MEMBER_SIZE_BYTES:
                logger.warning("archive_entry_skipped_size", name=info.filename, size=info.file_size)
                continue
            with rf.open(info) as f:
                yield info.filename, f.read()

def _iter_archive_members(file_bytes: bytes, filename: str, content_type: Optional[str]) -> Iterable[Tuple[str, bytes]]:
    lname = (filename or "").lower()
    if lname.endswith(".zip"):
        return _iter_zip(file_bytes)
    if lname.endswith((".tar", ".tgz", ".tar.gz", ".tbz2", ".tar.bz2")):
        return _iter_tar(file_bytes)
    if lname.endswith(".7z"):
        return _iter_7z(file_bytes)
    if lname.endswith(".rar"):
        return _iter_rar(file_bytes)

    # Fallback по content-type
    if content_type in ("application/zip",):
        return _iter_zip(file_bytes)
    if content_type in ("application/x-7z-compressed",):
        return _iter_7z(file_bytes)
    if content_type in ("application/x-rar-compressed",):
        return _iter_rar(file_bytes)
    if content_type in ("application/x-tar", "application/gzip", "application/x-bzip2"):
        return _iter_tar(file_bytes)

    raise HTTPException(400, detail="Unknown archive format")

async def _process_single_file(
        *,
        outer_package_id: Optional[str],
        outer_package_name: Optional[str],
        original_outer_name: Optional[str],
        session_id: str,
        user_id: str,
        filename: str,
        file_bytes: bytes,
        content_type: Optional[str],
) -> Dict[str, Any]:
    file_id = uuid.uuid4().hex
    ctype = content_type or _guess_type_by_name(filename)

    # 1) Загрузка в S3
    up = await s3_service.upload_file(
        filename=filename,
        content_type=ctype,
        data=file_bytes,
        session_id=session_id,
    )
    stored_name = up.get("stored_name")
    name = filename or stored_name or f"{file_id}"
    meta_obj = classifier_service.classify(up["url"], ctype.startswith("image/"))
    meta2obj = parser_service.parse(up["url"], ctype.startswith("image/"),meta_obj["document_type"])
    obj = await database_service.create_file_object(
        id=file_id,
        file_name=name,
        description=f"uploaded{' from archive' if outer_package_id else ''}",
        created_by=str(user_id),
        session_id=session_id,
        file_type=ctype,
        s3_key=up["key"],
        s3_url=up["url"],
        metadata_json=json.dumps(meta_obj, ensure_ascii=False),
    )

    # 6) Результат
    return {
        "id": obj.id,
        "file_name": obj.file_name,
        "file_type": obj.file_type,
        "url": obj.s3_url,
        "s3_key": obj.s3_key,
        "package_id": outer_package_id,
        "package_name": outer_package_name,
        "metadata1": meta_obj,  # уже объект, удобнее клиенту
        "metadata2": meta2obj
    }

@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload files (docx, pdf, images) or archives (zip, rar, 7z, tar)",
)
async def upload_files(
        current_session: Session = Depends(get_current_session),
        files: List[UploadFile] = File(..., description="One or more files or archives (.zip, .rar, .7z, .tar.*)"),
):
    """
    Загружает файлы (.docx, .pdf, изображения) **и/или архивы** (.zip/.rar/.7z/.tar.*).
    Для архивов:
      • распаковывает,
      • обрабатывает каждый вложенный файл,
      • добавляет в метаданные `package_id` (UUID архива) и `package_name` (имя архива).
    Возвращает список объектов c метаданными, результатами OCR/парсинга.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    session_id = current_session.id
    user_id = current_session.user_id

    results: List[Dict[str, Any]] = []

    for f in files:
        try:
            outer_bytes: bytes = await f.read()
            outer_name = f.filename or ""
            outer_content_type = f.content_type or mimetypes.guess_type(outer_name)[0] or "application/octet-stream"

            # Если это архив — распаковываем и обрабатываем вложенные файлы
            if _is_archive(outer_name, outer_content_type):
                package_id = uuid.uuid4().hex
                package_name = outer_name or f"archive-{package_id}"

                count_total = 0
                count_processed = 0
                for inner_name, inner_bytes in _iter_archive_members(outer_bytes, outer_name, outer_content_type):
                    count_total += 1
                    if not _ext_allowed(inner_name):
                        logger.info("archive_entry_skipped_extension", name=inner_name)
                        continue

                    inner_ctype = _guess_type_by_name(inner_name)
                    try:
                        item = await _process_single_file(
                            outer_package_id=package_id,
                            outer_package_name=package_name,
                            original_outer_name=outer_name,
                            session_id=session_id,
                            user_id=user_id,
                            filename=inner_name,
                            file_bytes=inner_bytes,
                            content_type=inner_ctype,
                        )
                        results.append(item)
                        count_processed += 1
                    except Exception as e:
                        logger.exception("archive_entry_failed", archive=outer_name, inner=inner_name, session_id=session_id)
                        results.append({
                            "id": None,
                            "file_name": inner_name,
                            "package_id": package_id,
                            "package_name": package_name,
                            "error": str(e),
                        })

                logger.info(
                    "archive_processed",
                    archive=outer_name,
                    package_id=package_id,
                    total=count_total,
                    processed=count_processed,
                    session_id=session_id,
                    user_id=user_id
                )
            else:
                # Обычный одиночный файл — как раньше
                item = await _process_single_file(
                    outer_package_id=None,
                    outer_package_name=None,
                    original_outer_name=None,
                    session_id=session_id,
                    user_id=str(user_id),
                    filename=outer_name,
                    file_bytes=outer_bytes,
                    content_type=outer_content_type,
                )
                results.append(item)

        except HTTPException:
            raise
        except Exception as e:
            logger.exception("file_upload_or_ocr_failed", filename=getattr(f, "filename", None), session_id=session_id)
            results.append({
                "id": None,
                "file_name": getattr(f, "filename", None),
                "error": str(e),
            })

    logger.info(
        "files_uploaded_ocr_parsed",
        count=len(results),
        session_id=session_id,
        user_id=user_id
    )
    return {"files": results}

