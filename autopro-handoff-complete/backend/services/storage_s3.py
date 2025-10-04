"""
S3-compatible storage service using boto3.

This module provides helper functions to upload files to Cloudflare R2
and return the public URL.  It reads configuration from environment
variables defined in `.env`.
"""
import os
import boto3
from typing import IO


def _get_client():
    endpoint = os.getenv("R2_ENDPOINT")
    access_key = os.getenv("R2_ACCESS_KEY")
    secret_key = os.getenv("R2_SECRET_KEY")
    region = os.getenv("R2_REGION", "auto")
    session = boto3.session.Session()
    return session.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )


def upload_file(file_obj: IO[bytes], key: str, content_type: str) -> str:
    """Upload a file object to the configured R2 bucket and return its URL.

    :param file_obj: binary file-like object
    :param key: the object key under which to store the file
    :param content_type: MIME type of the file
    :returns: public URL of the uploaded object
    """
    bucket = os.getenv("R2_BUCKET")
    public_base = os.getenv("R2_PUBLIC_BASE_URL")
    client = _get_client()
    client.upload_fileobj(
        Fileobj=file_obj,
        Bucket=bucket,
        Key=key,
        ExtraArgs={"ACL": "public-read", "ContentType": content_type},
    )
    return f"{public_base}/{key}"