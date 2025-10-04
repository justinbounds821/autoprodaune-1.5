"""
Routes for file uploads.

This module defines an endpoint for uploading one or more files to
Cloudflare R2.  It returns publicly accessible URLs for each uploaded
file.  The actual upload logic is delegated to the `storage_s3`
service module.
"""
import uuid
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException

from ..services.storage_s3 import upload_file

router = APIRouter()


@router.post("/uploads")
async def upload_files(files: List[UploadFile] = File(...)) -> dict[str, List[str]]:
    """Upload multiple files to Cloudflare R2 and return their URLs.

    Each file is stored under a unique key.  Only files with allowed
    extensions (configured via environment variables) will be uploaded.

    :param files: list of UploadFile objects
    :returns: dictionary with list of URLs
    """
    urls: List[str] = []
    for file in files:
        filename = file.filename or "upload"
        ext = filename.split(".")[-1].lower()
        key = f"uploads/{uuid.uuid4().hex}.{ext}"
        try:
            url = upload_file(file.file, key, content_type=file.content_type or f"application/octet-stream")
            urls.append(url)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))
    return {"urls": urls}