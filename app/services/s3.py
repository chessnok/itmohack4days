import asyncio
import mimetypes
import uuid
from pathlib import Path
from typing import Optional

import boto3
from botocore.client import Config
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings
from app.core.logging import logger


class S3Service:
    def __init__(self):
        config = Config(signature_version="s3v4", s3={"addressing_style": "virtual"})
        kwargs = {
            "aws_access_key_id": settings.S3_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.S3_SECRET_ACCESS_KEY,
            "region_name": settings.S3_REGION,
            "config": config,
        }
        if settings.S3_ENDPOINT:
            kwargs["endpoint_url"] = settings.S3_ENDPOINT

        self._client = boto3.client("s3", **kwargs)
        self._bucket = settings.S3_BUCKET
        self._public_base = settings.S3_PUBLIC_BASE_URL

    def _guess_ext(self, filename: Optional[str]) -> str:
        if not filename:
            return ""
        ext = Path(filename).suffix
        return ext.lower() if ext else ""

    def _public_url(self, key: str) -> str:
        base = self._public_base.rstrip("/")
        return f"{base}/{key}"

    async def upload_file(
            self,
            file: UploadFile,
            session_id: str,
            key_prefix: str = "sessions",
            override_filename: Optional[str] = None,
    ) -> dict:
        """
        Загружает файл в S3 под ключом:
          {key_prefix}/{session_id}/{uuid}{ext}

        Возвращает: { key, url, content_type, size, stored_name }
        """
        # читаем по кускам и ограничиваем размер при необходимости (пример: 50 МБ)
        max_size = 50 * 1024 * 1024
        chunks = []
        size = 0
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large (> {max_size} bytes)",
                )
            chunks.append(chunk)
        data = b"".join(chunks)

        # определим content type
        content_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"

        # сгенерим имя
        ext = self._guess_ext(file.filename or override_filename)
        stored_name = f"{uuid.uuid4().hex}{ext}"
        key = f"{key_prefix}/{session_id}/{stored_name}"

        # upload in thread
        def _put_object():
            return self._client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )

        try:
            resp = await asyncio.to_thread(_put_object)
        except Exception as e:
            logger.error("s3_upload_failed", error=str(e), key=key, bucket=self._bucket, exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to upload to object storage") from e

        etag = resp.get("ETag", "").strip('"')
        url = self._public_url(key)

        logger.info(
            "s3_file_uploaded",
            key=key,
            size=size,
            content_type=content_type,
            etag=etag,
            url=url,
        )

        return {
            "key": key,
            "url": url,
            "etag": etag,
            "content_type": content_type,
            "size": size,
            "stored_name": stored_name,
        }

s3_service = S3Service()