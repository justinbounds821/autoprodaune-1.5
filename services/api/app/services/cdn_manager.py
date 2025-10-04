# services/api/app/services/cdn_manager.py
"""
CDN manager for R2/S3 compatible operations.
SRP: CDN operations only, no business logic.
"""
import os
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class CDNManager:
    """Service for managing CDN operations on R2."""

    def __init__(self):
        """Initialize CDN manager."""
        self.r2_endpoint = os.getenv("R2_ENDPOINT_URL")
        self.r2_access_key = os.getenv("R2_ACCESS_KEY_ID")
        self.r2_secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
        self.r2_bucket = os.getenv("R2_BUCKET_NAME", "autopro-videos")
        self.r2_public_base = os.getenv("R2_PUBLIC_BASE")
        self.sign_urls = os.getenv("R2_SIGN_URLS", "true").lower() in ("1", "true", "yes")
        self.sign_ttl = int(os.getenv("R2_SIGN_TTL_SECONDS", "86400"))

        self.r2_client = None
        if self.r2_endpoint and self.r2_access_key and self.r2_secret_key:
            self._init_r2_client()

        logger.info(f"✅ CDN manager initialized: {'R2' if self.r2_client else 'disabled'}")

    def _init_r2_client(self) -> None:
        """Initialize R2/S3 compatible client."""
        try:
            import boto3
            from botocore.config import Config

            self.r2_client = boto3.client(
                's3',
                endpoint_url=self.r2_endpoint,
                aws_access_key_id=self.r2_access_key,
                aws_secret_access_key=self.r2_secret_key,
                config=Config(signature_version='s3v4'),
                region_name='auto'
            )

            # Test connection
            self.r2_client.head_bucket(Bucket=self.r2_bucket)
            logger.info("✅ R2 client initialized successfully")

        except ImportError:
            logger.warning("boto3 not available, CDN operations disabled")
            self.r2_client = None
        except Exception as e:
            logger.error(f"R2 initialization failed: {e}")
            self.r2_client = None

    def generate_signed_url(self, key: str, expires_in: int = None) -> Optional[str]:
        """
        Generate presigned URL for R2 object.

        Args:
            key: Object key
            expires_in: Expiration time in seconds (optional, uses default)

        Returns:
            Presigned URL or None if failed
        """
        if not self.r2_client:
            logger.debug("R2 client not available for signed URL")
            return None

        try:
            ttl = expires_in or self.sign_ttl

            presigned_url = self.r2_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.r2_bucket,
                    'Key': key
                },
                ExpiresIn=ttl
            )

            logger.info(f"✅ Generated signed URL for {key} (expires: {ttl}s)")
            return presigned_url

        except Exception as e:
            logger.error(f"Failed to generate signed URL for {key}: {e}")
            return None

    def get_public_url(self, key: str) -> Optional[str]:
        """
        Get public URL for R2 object.

        Args:
            key: Object key

        Returns:
            Public URL or None if not configured
        """
        if not self.r2_public_base:
            logger.debug("Public base URL not configured")
            return None

        public_url = f"{self.r2_public_base}/{key}"
        logger.debug(f"Generated public URL for {key}")
        return public_url

    def check_object_exists(self, key: str) -> bool:
        """
        Check if object exists in R2.

        Args:
            key: Object key

        Returns:
            True if exists, False otherwise
        """
        if not self.r2_client:
            return False

        try:
            self.r2_client.head_object(Bucket=self.r2_bucket, Key=key)
            return True
        except self.r2_client.exceptions.NoSuchKey:
            return False
        except Exception as e:
            logger.error(f"Error checking object {key}: {e}")
            return False

    def delete_object(self, key: str) -> bool:
        """
        Delete object from R2.

        Args:
            key: Object key

        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.r2_client:
            logger.debug("R2 client not available for delete")
            return False

        try:
            self.r2_client.delete_object(Bucket=self.r2_bucket, Key=key)
            logger.info(f"✅ Deleted object from R2: {key}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete object {key}: {e}")
            return False

    def purge_related_objects(self, job_id: str) -> int:
        """
        Purge all objects related to a job (video, thumbnail, HLS segments).

        Args:
            job_id: Job identifier

        Returns:
            Number of objects purged
        """
        if not self.r2_client:
            logger.debug("R2 client not available for purge")
            return 0

        purged_count = 0

        # List of possible related keys
        now = __import__('datetime').datetime.utcnow()
        possible_keys = [
            f"videos/{now.year}/{now.month"02d"}/video_{job_id}.mp4",
            f"videos/{now.year}/{now.month-1"02d"}/video_{job_id}.mp4",  # Previous month
            f"thumbnails/{now.year}/{now.month"02d"}/thumb_{job_id}.jpg",
            f"thumbnails/{now.year}/{now.month-1"02d"}/thumb_{job_id}.jpg",
            f"hls/{now.year}/{now.month"02d"}/{job_id}/index.m3u8",
            f"hls/{now.year}/{now.month-1"02d"}/{job_id}/index.m3u8",
        ]

        # Also try to find by pattern (more comprehensive)
        try:
            # List objects with job_id pattern
            paginator = self.r2_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.r2_bucket)

            for page in pages:
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    if job_id in key:
                        try:
                            self.r2_client.delete_object(Bucket=self.r2_bucket, Key=key)
                            purged_count += 1
                            logger.debug(f"Purged related object: {key}")
                        except Exception as e:
                            logger.warning(f"Failed to purge {key}: {e}")

        except Exception as e:
            logger.error(f"Error during comprehensive purge for {job_id}: {e}")

        # Also try the specific keys
        for key in possible_keys:
            if self.delete_object(key):
                purged_count += 1

        logger.info(f"✅ Purged {purged_count} objects related to job {job_id}")
        return purged_count

    def list_job_objects(self, job_id: str) -> List[Dict[str, Any]]:
        """
        List all objects related to a job.

        Args:
            job_id: Job identifier

        Returns:
            List of object information dictionaries
        """
        if not self.r2_client:
            return []

        objects = []

        try:
            # List objects with job_id pattern
            paginator = self.r2_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.r2_bucket)

            for page in pages:
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    if job_id in key:
                        objects.append({
                            'key': key,
                            'size': obj.get('Size', 0),
                            'last_modified': obj.get('LastModified'),
                            'exists': True
                        })

        except Exception as e:
            logger.error(f"Error listing objects for job {job_id}: {e}")

        return objects

    def get_cdn_info(self) -> Dict[str, Any]:
        """Get CDN configuration information."""
        return {
            "r2_enabled": self.r2_client is not None,
            "r2_bucket": self.r2_bucket,
            "r2_endpoint": self.r2_endpoint,
            "r2_public_base": self.r2_public_base,
            "sign_urls": self.sign_urls,
            "sign_ttl_seconds": self.sign_ttl,
            "object_count": len(self.list_job_objects("dummy")) if self.r2_client else 0
        }

# Global instance
_cdn_manager = None

def get_cdn_manager() -> CDNManager:
    """Get or create global CDN manager instance."""
    global _cdn_manager
    if _cdn_manager is None:
        _cdn_manager = CDNManager()
    return _cdn_manager