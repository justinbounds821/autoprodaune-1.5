# services/api/app/services/video_engine.py
"""
Main video engine orchestrator for AutoPro Video Engine.
SRP: Video generation orchestration only, coordinates services.
"""
import os
import uuid
import asyncio
import logging
import tempfile
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class VideoEngine:
    """Main orchestrator for video generation pipeline."""

    def __init__(self):
        """Initialize video engine."""
        # Import services (avoid circular imports)
        self.job_store = None
        self.job_repo = None
        self.voice_service = None
        self.template_engine = None
        self.lipsync_backend = None
        self.compositor = None
        self.storage_service = None
        self.cost_tracker = None
        self.webhook_notifier = None

        logger.info("✅ Video engine initialized")

    async def generate_video(self, request: Dict[str, Any]) -> str:
        """
        Generate video from request.

        Args:
            request: Video generation request

        Returns:
            Job ID for tracking

        Raises:
            Exception: If validation fails or generation fails
        """
        # Validate request
        self._validate_request(request)

        # Generate job ID
        job_id = str(uuid.uuid4())

        try:
            # Initialize services
            await self._init_services()

            # Create job entry
            await self._create_job(job_id, request)

            # Start background processing
            asyncio.create_task(self._process_job(job_id, request))

            logger.info(f"✅ Video generation queued: {job_id}")
            return job_id

        except Exception as e:
            logger.error(f"Failed to queue video generation: {e}")
            # Update job status to failed
            if self.job_store:
                self.job_store.set_status(job_id, "failed", error=str(e))
            if self.job_repo:
                await self.job_repo.update_job_status(job_id, "failed", error=str(e))
            raise

    async def _init_services(self) -> None:
        """Initialize all required services."""
        if not self.job_store:
            from .job_store import get_job_store
            self.job_store = get_job_store()

        if not self.job_repo:
            from .job_repo_supabase import get_job_repo
            self.job_repo = get_job_repo()

        if not self.voice_service:
            from .voice_elevenlabs import tts_elevenlabs
            self.voice_service = tts_elevenlabs

        if not self.template_engine:
            from .template_engine import get_template_engine
            self.template_engine = get_template_engine()

        if not self.lipsync_backend:
            from .lipsync_backend import get_lipsync_backend
            self.lipsync_backend = get_lipsync_backend()

        if not self.compositor:
            from .compositor_ffmpeg import get_compositor
            self.compositor = get_compositor()

        if not self.storage_service:
            from .storage_service import get_storage_service
            self.storage_service = get_storage_service()

        if not self.cost_tracker:
            from .cost_tracker import get_cost_tracker
            self.cost_tracker = get_cost_tracker()

        if not self.webhook_notifier:
            from .webhook_notifier import get_webhook_notifier
            self.webhook_notifier = get_webhook_notifier()

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate video generation request."""
        # Script validation
        script = request.get("script", "").strip()
        if not script:
            raise ValueError("Script is required")
        if len(script) < 10:
            raise ValueError("Script must be at least 10 characters")
        if len(script) > 1000:
            raise ValueError("Script cannot exceed 1000 characters")

        # Avatar validation (at least one required for lip-sync)
        avatar_image_url = request.get("avatar_image_url")
        avatar_video_url = request.get("avatar_video_url")

        lipsync_backend = os.getenv("LIPSYNC_BACKEND", "sadtalker").lower()
        if lipsync_backend != "none":
            if not avatar_image_url and not avatar_video_url:
                raise ValueError("At least one avatar source (image_url or video_url) is required for lip-sync")

    async def _create_job(self, job_id: str, request: Dict[str, Any]) -> None:
        """Create job entry in both stores."""
        # In-memory job store
        if self.job_store:
            self.job_store.create_job(job_id, {
                "script": request.get("script"),
                "voice_id": request.get("voice_id"),
                "avatar_image_url": request.get("avatar_image_url"),
                "avatar_video_url": request.get("avatar_video_url"),
                "status": "queued"
            })

        # Supabase job store
        if self.job_repo:
            job_data = {
                "status": "queued",
                "script": request.get("script"),
                "voice_id": request.get("voice_id"),
                "avatar_image_url": request.get("avatar_image_url"),
                "avatar_video_url": request.get("avatar_video_url"),
                "provider": "internal"
            }
            await self.job_repo.save_job(job_id, job_data)

    async def _process_job(self, job_id: str, request: Dict[str, Any]) -> None:
        """Process video generation job."""
        start_time = asyncio.get_event_loop().time()

        try:
            # Update status to processing
            await self._update_job_status(job_id, "processing")

            # Step 1: Generate TTS audio
            logger.info(f"🎵 Generating TTS for job {job_id}")
            audio_data, audio_duration = await self._generate_tts_audio(request)

            # Step 2: Build timeline
            logger.info(f"📋 Building timeline for job {job_id}")
            timeline = await self._build_timeline(request, audio_duration)

            # Step 3: Generate lip-sync video (if enabled)
            lipsync_backend = os.getenv("LIPSYNC_BACKEND", "sadtalker").lower()
            avatar_video_path = None

            if lipsync_backend != "none" and self.lipsync_backend.is_available():
                logger.info(f"🎭 Generating lip-sync for job {job_id}")
                avatar_video_path = await self._generate_lipsync_video(job_id, request, audio_data)
            else:
                logger.info(f"⏭️ Skipping lip-sync for job {job_id}")

            # Step 4: Compose final video
            logger.info(f"🎬 Composing final video for job {job_id}")
            final_video_path = await self._compose_video(job_id, timeline, audio_data, avatar_video_path)

            # Step 5: Upload to storage
            logger.info(f"📦 Uploading video for job {job_id}")
            video_url = await self._upload_video(job_id, final_video_path)

            # Step 6: Calculate and save costs
            processing_duration = asyncio.get_event_loop().time() - start_time
            await self._calculate_and_save_costs(job_id, request, audio_duration, processing_duration)

            # Step 7: Update job as completed
            await self._update_job_status(job_id, "completed", video_url=video_url)

            # Step 8: Send webhook notification
            await self._send_webhook_notification(job_id, "completed", video_url)

            logger.info(f"✅ Video generation completed: {job_id}")

        except Exception as e:
            logger.error(f"❌ Video generation failed for job {job_id}: {e}")
            await self._update_job_status(job_id, "failed", error=str(e))
            await self._send_webhook_notification(job_id, "failed", error=str(e))
        finally:
            # Clean up temporary files
            await self._cleanup_temp_files(job_id)

    async def _generate_tts_audio(self, request: Dict[str, Any]) -> tuple[bytes, float]:
        """Generate TTS audio and return duration."""
        script = request.get("script")
        voice_id = request.get("voice_id")

        # Generate audio
        audio_data = await self.voice_service(script, voice_id)

        # For now, estimate duration (in real implementation, parse from audio metadata)
        # Assume ~150 words per minute = 2.5 words per second
        word_count = len(script.split())
        estimated_duration = word_count / 2.5

        return audio_data, estimated_duration

    async def _build_timeline(self, request: Dict[str, Any], audio_duration: float) -> Dict[str, Any]:
        """Build video timeline."""
        return self.template_engine.build_timeline(request, audio_duration)

    async def _generate_lipsync_video(self, job_id: str, request: Dict[str, Any], audio_data: bytes) -> Optional[str]:
        """Generate lip-sync video."""
        # Save audio temporarily for lip-sync processing
        audio_fd, audio_path = tempfile.mkstemp(suffix=".wav")
        os.close(audio_fd)

        try:
            # Convert MP3 to WAV for lip-sync (if needed)
            from .voice_elevenlabs import _mp3_to_wav
            wav_path = _mp3_to_wav(audio_data)

            # Run lip-sync
            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)

            success = self.lipsync_backend.run_lipsync(
                image_path=request.get("avatar_image_url"),
                video_path=request.get("avatar_video_url"),
                audio_path=wav_path,
                output_path=output_path
            )

            if success and os.path.exists(output_path):
                return output_path
            else:
                logger.warning(f"Lip-sync generation failed for job {job_id}")
                return None

        except Exception as e:
            logger.error(f"Lip-sync generation error for job {job_id}: {e}")
            return None
        finally:
            # Clean up temp audio file
            for path in [audio_path, wav_path if 'wav_path' in locals() else None]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass

    async def _compose_video(self, job_id: str, timeline: Dict[str, Any],
                           audio_data: bytes, avatar_video_path: Optional[str]) -> str:
        """Compose final video."""
        # Save audio temporarily
        audio_fd, audio_path = tempfile.mkstemp(suffix=".mp3")
        os.close(audio_fd)

        try:
            with open(audio_path, 'wb') as f:
                f.write(audio_data)

            # Update timeline with actual file paths
            composition_timeline = timeline.copy()
            if avatar_video_path:
                composition_timeline["layers"] = [
                    layer if layer.get("type") != "video" else {
                        **layer,
                        "params": {**layer.get("params", {}), "video_path": avatar_video_path}
                    }
                    for layer in composition_timeline.get("layers", [])
                ]

            # Generate output path
            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)

            # Compose video
            success = self.compositor.compose_video(composition_timeline, audio_path, output_path)

            if not success or not os.path.exists(output_path):
                raise Exception("Video composition failed")

            return output_path

        finally:
            # Clean up temp audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)

    async def _upload_video(self, job_id: str, video_path: str) -> str:
        """Upload video to storage and return URL."""
        with open(video_path, 'rb') as f:
            video_data = f.read()

        return self.storage_service.save_video(video_data, f"video_{job_id}.mp4")

    async def _calculate_and_save_costs(self, job_id: str, request: Dict[str, Any],
                                      audio_duration: float, processing_duration: float) -> None:
        """Calculate and save job costs."""
        # Estimate file size (rough calculation)
        estimated_mb = 5  # Default estimate

        job_data = {
            "tts_duration": audio_duration,
            "processing_duration": processing_duration,
            "estimated_storage_mb": estimated_mb
        }

        costs = self.cost_tracker.calculate_costs(job_data)
        await self.cost_tracker.save_costs(job_id, costs)

    async def _update_job_status(self, job_id: str, status: str, **kwargs) -> None:
        """Update job status in both stores."""
        # Update in-memory store
        if self.job_store:
            self.job_store.set_status(job_id, status, **kwargs)

        # Update in Supabase
        if self.job_repo:
            await self.job_repo.update_job_status(job_id, status, **kwargs)

    async def _send_webhook_notification(self, job_id: str, status: str, video_url: str = None, error: str = None) -> None:
        """Send webhook notification."""
        if self.webhook_notifier:
            await self.webhook_notifier.send_webhook(job_id, status, video_url, error)

    async def _cleanup_temp_files(self, job_id: str) -> None:
        """Clean up temporary files."""
        # Implementation would clean up temp files created during processing
        pass

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status."""
        if self.job_store:
            return self.job_store.get_job(job_id)
        return None

# Global instance
_video_engine = None

def get_video_engine() -> VideoEngine:
    """Get or create global video engine instance."""
    global _video_engine
    if _video_engine is None:
        _video_engine = VideoEngine()
    return _video_engine