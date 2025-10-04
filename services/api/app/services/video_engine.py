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
        self.metrics_service = None
        self.captions_generator = None

        logger.info("✅ Video engine initialized")

    async def generate_video(self, request: Dict[str, Any]) -> str:
        """
        Generate video from request with idempotency and retry support.

        Args:
            request: Video generation request

        Returns:
            Job ID for tracking

        Raises:
            Exception: If validation fails or generation fails
        """
        start_time = time.time()

        # Check idempotency first
        idempotency_key = request.get("extra", {}).get("idempotency_key")
        if idempotency_key and self.job_repo:
            existing_job = await self.job_repo.get_job_by_idempotency_key(idempotency_key)
            if existing_job:
                logger.info(f"Returning existing job for idempotency key: {idempotency_key}")
                return existing_job["job_id"]

        # Validate request
        self._validate_request(request)

        # Generate job ID
        job_id = str(uuid.uuid4())

        try:
            # Initialize services
            await self._init_services()

            # Record metrics
            if self.metrics_service:
                self.metrics_service.record_job_status("queued")

            # Create job entry with metadata
            job_data = request.copy()
            job_data.update({
                "idempotency_key": idempotency_key,
                "retry_count": 0,
                "meta": {
                    "preset": os.getenv("VIDEO_ENGINE_PRESET", "medium"),
                    "fps": os.getenv("VIDEO_ENGINE_FPS", "25"),
                    "backend": os.getenv("LIPSYNC_BACKEND", "sadtalker"),
                    "storage": os.getenv("VIDEO_ENGINE_STORAGE", "local"),
                    "created_at": time.time()
                }
            })

            await self._create_job(job_id, job_data)

            # Start background processing with retry capability
            asyncio.create_task(self._process_job_with_retry(job_id, request))

            logger.info(f"✅ Video generation queued: {job_id} (idempotency: {idempotency_key})")

            # Record queue metrics
            if self.metrics_service and self.job_store:
                stats = self.job_store.get_queue_stats()
                self.metrics_service.update_queue_metrics(stats["queue_length"], stats["processing_count"])

            return job_id

        except Exception as e:
            logger.error(f"Failed to queue video generation: {e}")
            # Update job status to failed
            if self.job_store:
                self.job_store.set_status(job_id, "failed", error=str(e))
            if self.job_repo:
                await self.job_repo.update_job_status(job_id, "failed", error=str(e))

            # Record failure metric
            if self.metrics_service:
                self.metrics_service.record_job_failure("queue_error")

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

        if not self.metrics_service:
            from .metrics import get_metrics_service
            self.metrics_service = get_metrics_service()

        if not self.captions_generator:
            from .captions_generator import get_captions_generator
            self.captions_generator = get_captions_generator()

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
        """Process video generation job with metrics and structured logging."""
        start_time = time.time()
        phase_start = start_time

        try:
            # Update status to processing
            await self._update_job_status(job_id, "processing")
            self._log_job_event(job_id, "processing_start", "Started processing")

            # Record backend availability
            if self.metrics_service and self.lipsync_backend:
                backend_info = self.lipsync_backend.get_backend_info()
                self.metrics_service.set_backend_availability(
                    backend_info["backend"],
                    backend_info["available"]
                )

            # Step 1: Generate TTS audio
            self._log_job_event(job_id, "tts_start", "Starting TTS generation")
            tts_start = time.time()
            audio_data, audio_duration = await self._generate_tts_audio(request)
            tts_duration = time.time() - tts_start

            self._log_job_event(job_id, "tts_complete", f"TTS generated in {tts_duration:.2f}s")
            if self.metrics_service:
                self.metrics_service.record_tts_duration(audio_duration)

            # Step 2: Build timeline
            self._log_job_event(job_id, "timeline_start", "Building video timeline")
            timeline_start = time.time()
            timeline = await self._build_timeline(request, audio_duration)
            timeline_duration = time.time() - timeline_start

            self._log_job_event(job_id, "timeline_complete", f"Timeline built in {timeline_duration:.2f}s")

            # Step 3: Generate lip-sync video (if enabled)
            lipsync_backend = os.getenv("LIPSYNC_BACKEND", "sadtalker").lower()
            avatar_video_path = None

            if lipsync_backend != "none" and self.lipsync_backend.is_available():
                self._log_job_event(job_id, "lipsync_start", f"Starting lip-sync with {lipsync_backend}")
                lipsync_start = time.time()
                avatar_video_path = await self._generate_lipsync_video(job_id, request, audio_data)
                lipsync_duration = time.time() - lipsync_start

                self._log_job_event(job_id, "lipsync_complete", f"Lip-sync completed in {lipsync_duration:.2f}s")
            else:
                self._log_job_event(job_id, "lipsync_skip", f"Skipping lip-sync (backend: {lipsync_backend})")

            # Step 4: Compose final video
            self._log_job_event(job_id, "composition_start", "Starting video composition")
            composition_start = time.time()
            final_video_path = await self._compose_video(job_id, timeline, audio_data, avatar_video_path)
            composition_duration = time.time() - composition_start

            self._log_job_event(job_id, "composition_complete", f"Video composed in {composition_duration:.2f}s")

            # Get video file size for metrics
            video_size_bytes = 0
            if os.path.exists(final_video_path):
                video_size_bytes = os.path.getsize(final_video_path)
                if self.metrics_service:
                    self.metrics_service.record_video_size(video_size_bytes)

            # Step 5: Upload to storage
            self._log_job_event(job_id, "upload_start", "Uploading video to storage")
            upload_start = time.time()
            video_url = await self._upload_video(job_id, final_video_path)
            upload_duration = time.time() - upload_start

            self._log_job_event(job_id, "upload_complete", f"Video uploaded in {upload_duration:.2f}s")

            # Step 6: Calculate and save costs
            processing_duration = time.time() - start_time
            self._log_job_event(job_id, "cost_calculation", f"Calculating costs for {processing_duration:.2f}s processing")
            await self._calculate_and_save_costs(job_id, request, audio_duration, processing_duration)

            # Step 7: Generate thumbnail and metadata
            self._log_job_event(job_id, "thumbnail_start", "Generating video thumbnail and metadata")
            thumbnail_url = await self._generate_thumbnail(job_id, final_video_path)
            metadata = await self._extract_metadata(job_id, final_video_path)
            self._log_job_event(job_id, "thumbnail_complete", "Thumbnail and metadata generated")

            # Step 8: Update job as completed with enhanced metadata
            completion_meta = {
                "video_url": video_url,
                "thumbnail_url": thumbnail_url,
                "metadata": metadata,
                "processing_duration": processing_duration,
                "file_size_bytes": video_size_bytes
            }
            await self._update_job_status(job_id, "completed", **completion_meta)
            self._log_job_event(job_id, "job_complete", f"Job completed successfully in {processing_duration:.2f}s")

            # Step 9: Send webhook notification
            await self._send_webhook_notification(job_id, "completed", video_url)

            # Record final metrics
            if self.metrics_service:
                self.metrics_service.record_processing_duration(processing_duration, "completed")
                total_cost = request.get("meta", {}).get("total_cost_cents", 0)
                if total_cost > 0:
                    self.metrics_service.record_total_cost(total_cost)

            logger.info(f"✅ Video generation completed: {job_id}")

        except Exception as e:
            error_msg = str(e)
            processing_duration = time.time() - start_time

            self._log_job_event(job_id, "job_failed", f"Job failed after {processing_duration:.2f}s: {error_msg}")

            # Record failure metrics
            if self.metrics_service:
                self.metrics_service.record_processing_duration(processing_duration, "failed")
                self.metrics_service.record_job_failure("processing_error")

            await self._update_job_status(job_id, "failed", error=error_msg)
            await self._send_webhook_notification(job_id, "failed", error=error_msg)
            raise
        finally:
            # Clean up temporary files
            await self._cleanup_temp_files(job_id)

            # Update queue metrics
            if self.metrics_service and self.job_store:
                stats = self.job_store.get_queue_stats()
                self.metrics_service.update_queue_metrics(stats["queue_length"], stats["processing_count"])

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

    async def _generate_thumbnail(self, job_id: str, video_path: str) -> Optional[str]:
        """Generate thumbnail for the video."""
        try:
            if not self.thumbnailer:
                return None

            # Generate thumbnail locally
            thumb_path = self.thumbnailer.generate_thumbnail(video_path)

            if not thumb_path:
                return None

            # Upload to storage if R2 is configured
            if self.storage_service and self.storage_service.storage_type == "r2":
                thumb_key = f"thumbnails/video_{job_id}.jpg"
                thumb_url = self.storage_service.save_file_with_metadata(
                    thumb_path,
                    thumb_key,
                    {"type": "thumbnail", "job_id": job_id}
                )

                # Clean up local thumbnail file
                try:
                    os.remove(thumb_path)
                except:
                    pass

                return thumb_url

            # For local storage, return relative path
            return f"/api/video/thumbnails/video_{job_id}.jpg"

        except Exception as e:
            logger.error(f"Failed to generate thumbnail for job {job_id}: {e}")
            return None

    async def _extract_metadata(self, job_id: str, video_path: str) -> Dict[str, Any]:
        """Extract video metadata."""
        try:
            if not self.metadata_probe:
                return {}

            metadata = self.metadata_probe.get_video_metadata(video_path)

            if not metadata:
                return {}

            # Extract key information
            video_info = {
                "duration": metadata.get("duration", 0),
                "width": metadata.get("video", {}).get("width", 0),
                "height": metadata.get("video", {}).get("height", 0),
                "fps": metadata.get("video", {}).get("fps", 25.0),
                "bitrate": metadata.get("bitrate", 0),
                "size_bytes": metadata.get("size", 0),
                "codec": metadata.get("video", {}).get("codec", ""),
                "storage_type": os.getenv("VIDEO_ENGINE_STORAGE", "local"),
                "preset": os.getenv("VIDEO_ENGINE_PRESET", "medium"),
                "generated_at": time.time()
            }

            return video_info

        except Exception as e:
            logger.error(f"Failed to extract metadata for job {job_id}: {e}")
            return {}

    async def _cleanup_temp_files(self, job_id: str) -> None:
        """Clean up temporary files."""
        # Implementation would clean up temp files created during processing
        pass

    async def _process_job_with_retry(self, job_id: str, request: Dict[str, Any]) -> None:
        """Process job with retry logic and structured logging."""
        max_retries = int(os.getenv("VIDEO_ENGINE_RETRY_LIMIT", "2"))
        retry_backoff = int(os.getenv("VIDEO_ENGINE_RETRY_BACKOFF", "6"))

        for attempt in range(max_retries + 1):
            try:
                self._log_job_event(job_id, "start_attempt", f"Attempt {attempt + 1}/{max_retries + 1}")

                # Update retry count
                if attempt > 0 and self.job_repo:
                    await self.job_repo.increment_retry_count(job_id)

                # Process the job
                await self._process_job(job_id, request)

                # Success - exit retry loop
                self._log_job_event(job_id, "completed", f"Success after {attempt + 1} attempts")
                break

            except Exception as e:
                logger.warning(f"❌ Job {job_id} failed on attempt {attempt + 1}: {e}")

                if attempt < max_retries:
                    # Wait before retry with exponential backoff
                    wait_time = retry_backoff * (2 ** attempt)
                    self._log_job_event(job_id, "retry_wait", f"Waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                else:
                    # Final failure
                    self._log_job_event(job_id, "final_failure", f"Failed after {max_retries + 1} attempts: {e}")
                    await self._update_job_status(job_id, "failed", error=str(e))

                    # Record failure metrics
                    if self.metrics_service:
                        self.metrics_service.record_job_failure("max_retries_exceeded")

                    # Send webhook for final failure
                    await self._send_webhook_notification(job_id, "failed", error=str(e))

    def _log_job_event(self, job_id: str, phase: str, message: str, duration_ms: float = None) -> None:
        """Structured logging for job events."""
        log_data = {
            "job_id": job_id,
            "phase": phase,
            "message": message,
            "timestamp": time.time()
        }

        if duration_ms:
            log_data["duration_ms"] = duration_ms

        logger.info(f"🎬 Job {job_id}: {phase} - {message}", extra=log_data)

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