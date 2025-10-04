# services/api/app/services/storage_service.py
"""
File storage service supporting local filesystem and Cloudflare R2.
SRP: File storage operations only, no business logic.
"""
import os
import uuid
import logging
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class StorageService:
    """File storage service for video assets."""

    def __init__(self):
        """Initialize storage service."""
        self.storage_type = os.getenv("VIDEO_ENGINE_STORAGE", "local").lower()
        self.local_base_path = os.getcwd()
        self.videos_dir = os.path.join(self.local_base_path, "generated_videos")

        # R2 configuration
        self.r2_endpoint = os.getenv("R2_ENDPOINT_URL")
        self.r2_access_key = os.getenv("R2_ACCESS_KEY_ID")
        self.r2_secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
        self.r2_bucket = os.getenv("R2_BUCKET_NAME", "autopro-videos")
        self.r2_public_base = os.getenv("R2_PUBLIC_BASE")
        self.sign_urls = os.getenv("R2_SIGN_URLS", "true").lower() in ("1", "true", "yes")
        self.sign_ttl = int(os.getenv("R2_SIGN_TTL_SECONDS", "86400"))  # 24 hours
        self.cache_control = os.getenv("CDN_CACHE_CONTROL", "public, max-age=31536000, immutable")

        # Ensure local videos directory exists
        if self.storage_type == "local":
            os.makedirs(self.videos_dir, exist_ok=True)

        # Initialize R2 client if needed
        self.r2_client = None
        if self.storage_type == "r2":
            self._init_r2_client()

        logger.info(f"✅ Storage service initialized: {self.storage_type}")

    def _init_r2_client(self) -> None:
        """Initialize R2/S3 compatible client."""
        try:
            import boto3
            from botocore.config import Config

            if not all([self.r2_endpoint, self.r2_access_key, self.r2_secret_key]):
                logger.warning("R2 credentials incomplete, falling back to local storage")
                self.storage_type = "local"
                return

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
            logger.warning("boto3 not available, falling back to local storage")
            self.storage_type = "local"
        except Exception as e:
            logger.error(f"R2 initialization failed: {e}")
            self.storage_type = "local"

    def save_video(self, video_data: bytes, filename: Optional[str] = None) -> str:
        """
        Save video file and return URL.

        Args:
            video_data: Video file bytes
            filename: Optional filename (generated if not provided)

        Returns:
            URL to access the video
        """
        if filename is None:
            filename = f"video_{uuid.uuid4()}.mp4"

        if self.storage_type == "r2":
            return self._save_to_r2(video_data, filename)
        else:
            return self._save_to_local(video_data, filename)

    def _save_to_local(self, video_data: bytes, filename: str) -> str:
        """Save video to local filesystem."""
        filepath = os.path.join(self.videos_dir, filename)

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Write file
            with open(filepath, 'wb') as f:
                f.write(video_data)

            # Generate relative URL
            relative_path = os.path.relpath(filepath, self.local_base_path)
            url = f"/api/video/video/heygen/download/{Path(filename).stem}"

            logger.info(f"✅ Video saved locally: {filepath}")
            return url

        except Exception as e:
            logger.error(f"Failed to save video locally: {e}")
            raise

    def _save_to_r2(self, video_data: bytes, filename: str) -> str:
        """Save video to Cloudflare R2."""
        try:
            # Generate key with date-based folder structure
            now = datetime.utcnow()
            key = f"videos/{now.year}/{now.month"02d"}/{filename}"

            # Upload to R2 with cache headers
            self.r2_client.put_object(
                Bucket=self.r2_bucket,
                Key=key,
                Body=video_data,
                ContentType='video/mp4',
                CacheControl=self.cache_control,
                Metadata={
                    'uploaded-at': datetime.utcnow().isoformat(),
                    'content-type': 'video/mp4'
                }
            )

            # Generate presigned URL (24 hours)
            presigned_url = self.r2_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.r2_bucket, 'Key': key},
                ExpiresIn=24 * 3600  # 24 hours
            )

            logger.info(f"✅ Video saved to R2: {key}")
            return presigned_url

        except Exception as e:
            logger.error(f"Failed to save video to R2: {e}")
            raise

    def get_video_url(self, job_id: str) -> Optional[str]:
        """
        Get video URL for a job.

        Args:
            job_id: Job identifier

        Returns:
            Video URL or None if not found
        """
        if self.storage_type == "r2":
            return self._get_r2_url(job_id)
        else:
            return self._get_local_url(job_id)

    def _get_local_url(self, job_id: str) -> Optional[str]:
        """Get local video URL."""
        video_path = os.path.join(self.videos_dir, f"video_{job_id}.mp4")

        if os.path.exists(video_path):
            relative_path = os.path.relpath(video_path, self.local_base_path)
            return f"/api/video/video/heygen/download/{job_id}"
        else:
            logger.warning(f"Video not found locally: {video_path}")
            return None

    def _get_r2_url(self, job_id: str) -> Optional[str]:
        """Get R2 presigned URL."""
        try:
            # Try current month first, then fallback to search
            now = datetime.utcnow()
            possible_keys = [
                f"videos/{now.year}/{now.month"02d"}/video_{job_id}.mp4",
                f"videos/{now.year}/{now.month-1"02d"}/video_{job_id}.mp4"  # Previous month
            ]

            for key in possible_keys:
                try:
                    # Check if object exists
                    self.r2_client.head_object(Bucket=self.r2_bucket, Key=key)

                    if self.sign_urls:
                        # Generate presigned URL with configurable TTL
                        presigned_url = self.r2_client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': self.r2_bucket, 'Key': key},
                            ExpiresIn=self.sign_ttl
                        )
                        logger.info(f"✅ Generated signed URL for video: {key}")
                        return presigned_url
                    else:
                        # Use public URL if available
                        if self.r2_public_base:
                            public_url = f"{self.r2_public_base}/{key}"
                            logger.info(f"✅ Using public URL for video: {key}")
                            return public_url
                        else:
                            # Fallback to presigned URL
                            presigned_url = self.r2_client.generate_presigned_url(
                                'get_object',
                                Params={'Bucket': self.r2_bucket, 'Key': key},
                                ExpiresIn=self.sign_ttl
                            )
                            return presigned_url

                except self.r2_client.exceptions.NoSuchKey:
                    continue
                except Exception as e:
                    logger.warning(f"Error checking R2 object {key}: {e}")
                    continue

            logger.warning(f"Video not found in R2 for job {job_id}")
            return None

        except Exception as e:
            logger.error(f"Error getting R2 video URL for job {job_id}: {e}")
            return None

    def delete_video(self, job_id: str) -> bool:
        """
        Delete video file.

        Args:
            job_id: Job identifier

        Returns:
            True if deleted successfully, False otherwise
        """
        if self.storage_type == "r2":
            return self._delete_from_r2(job_id)
        else:
            return self._delete_from_local(job_id)

    def _delete_from_local(self, job_id: str) -> bool:
        """Delete video from local filesystem."""
        video_path = os.path.join(self.videos_dir, f"video_{job_id}.mp4")

        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.info(f"✅ Deleted local video: {video_path}")
                return True
            else:
                logger.warning(f"Local video not found for deletion: {video_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete local video: {e}")
            return False

    def _delete_from_r2(self, job_id: str) -> bool:
        """Delete video from R2."""
        try:
            # Find the object key (similar to _get_r2_url logic)
            now = datetime.utcnow()
            possible_keys = [
                f"videos/{now.year}/{now.month"02d"}/video_{job_id}.mp4",
                f"videos/{now.year}/{now.month-1"02d"}/video_{job_id}.mp4"
            ]

            for key in possible_keys:
                try:
                    self.r2_client.delete_object(Bucket=self.r2_bucket, Key=key)
                    logger.info(f"✅ Deleted R2 video: {key}")
                    return True
                except self.r2_client.exceptions.NoSuchKey:
                    continue
                except Exception as e:
                    logger.warning(f"Error deleting R2 object {key}: {e}")
                    continue

            logger.warning(f"R2 video not found for deletion: {job_id}")
            return False

        except Exception as e:
            logger.error(f"Error deleting R2 video for job {job_id}: {e}")
            return False

    def purge_cdn_object(self, key: str) -> bool:
        """
        Purge object from R2/CDN cache.

        Args:
            key: Object key to purge

        Returns:
            True if purged successfully, False otherwise
        """
        if not self.r2_client:
            logger.debug("R2 client not available for purge")
            return False

        try:
            # Delete the object (soft delete - just removes from CDN cache)
            self.r2_client.delete_object(Bucket=self.r2_bucket, Key=key)
            logger.info(f"✅ Purged CDN object: {key}")
            return True

        except Exception as e:
            logger.error(f"Failed to purge CDN object {key}: {e}")
            return False

    def check_object_exists(self, key: str) -> bool:
        """
        Check if object exists in R2.

        Args:
            key: Object key to check

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

    def save_file_with_metadata(self, file_path: str, key: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Save file to R2 with additional metadata.

        Args:
            file_path: Local file path
            key: R2 object key
            metadata: Additional metadata to store

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.r2_client:
            logger.debug("R2 client not available for save")
            return False

        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Prepare metadata
            r2_metadata = {
                'uploaded-at': datetime.utcnow().isoformat(),
                'file-size': str(len(file_data))
            }

            if metadata:
                for k, v in metadata.items():
                    r2_metadata[k] = str(v)

            # Upload with metadata
            self.r2_client.put_object(
                Bucket=self.r2_bucket,
                Key=key,
                Body=file_data,
                CacheControl=self.cache_control,
                Metadata=r2_metadata
            )

            logger.info(f"✅ Saved file to R2 with metadata: {key}")
            return True

        except Exception as e:
            logger.error(f"Failed to save file {file_path} to R2: {e}")
            return False

    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage configuration information."""
        return {
            "storage_type": self.storage_type,
            "local_path": self.videos_dir if self.storage_type == "local" else None,
            "r2_bucket": self.r2_bucket if self.storage_type == "r2" else None,
            "r2_endpoint": self.r2_endpoint if self.storage_type == "r2" else None,
            "r2_public_base": self.r2_public_base if self.storage_type == "r2" else None,
            "sign_urls": self.sign_urls,
            "sign_ttl_seconds": self.sign_ttl,
            "cache_control": self.cache_control
        }

# Global instance
_storage_service = None

def get_storage_service() -> StorageService:
    """Get or create global storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service