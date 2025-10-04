# services/api/app/services/lipsync_backend.py
"""
Lip-sync backend wrapper for SadTalker and Wav2Lip.
SRP: Lip-sync processing only, no business logic.
"""
import os
import tempfile
import subprocess
import logging
import glob
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class LipSyncBackend:
    """Lip-sync backend for generating talking head videos."""

    def __init__(self):
        """Initialize lip-sync backend."""
        self.backend = os.getenv("LIPSYNC_BACKEND", "sadtalker").lower()
        self.enabled = os.getenv("USE_INTERNAL_VIDEO_ENGINE", "false").lower() in ("1", "true", "yes")

        if not self.enabled:
            logger.info("Lip-sync backend disabled")
            return

        # Check backend availability
        self.sadtalker_available = os.path.exists("third_party/SadTalker")
        self.wav2lip_available = os.path.exists("third_party/Wav2Lip")

        if self.backend == "sadtalker" and not self.sadtalker_available:
            logger.warning("SadTalker backend selected but not available")
        elif self.backend == "wav2lip" and not self.wav2lip_available:
            logger.warning("Wav2Lip backend selected but not available")

        logger.info(f"✅ Lip-sync backend initialized: {self.backend}")

    def run_lipsync(self, image_path: Optional[str], video_path: Optional[str],
                   audio_path: str, output_path: str) -> bool:
        """
        Run lip-sync generation.

        Args:
            image_path: Path to source image (optional)
            video_path: Path to source video (optional)
            audio_path: Path to audio file
            output_path: Output video path

        Returns:
            True if lip-sync successful, False otherwise
        """
        if not self.enabled:
            logger.info("Lip-sync disabled, skipping")
            return False

        if self.backend == "sadtalker" and self.sadtalker_available:
            return self._run_sadtalker(image_path, video_path, audio_path, output_path)
        elif self.backend == "wav2lip" and self.wav2lip_available:
            return self._run_wav2lip(image_path, video_path, audio_path, output_path)
        else:
            logger.error(f"Lip-sync backend {self.backend} not available")
            return False

    def _run_sadtalker(self, image_path: Optional[str], video_path: Optional[str],
                      audio_path: str, output_path: str) -> bool:
        """
        Run SadTalker lip-sync generation.

        Args:
            image_path: Path to source image (optional)
            video_path: Path to source video (optional)
            audio_path: Path to WAV audio file
            output_path: Output video path

        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting SadTalker lip-sync generation")

        try:
            import sys
            sadtalker_path = "third_party/SadTalker"

            # Build SadTalker command
            cmd = [
                sys.executable, os.path.join(sadtalker_path, "inference.py"),
                "--driven_audio", audio_path,
                "--enhancer", "gfpgan",
                "--preprocess", "full",
                "--size", "512",
                "--fps", os.getenv("VIDEO_ENGINE_FPS", "25"),
                "--save_dir", os.path.dirname(output_path)
            ]

            # Add source (image or video)
            if image_path and os.path.exists(image_path):
                cmd.extend(["--source_image", image_path])
            elif video_path and os.path.exists(video_path):
                cmd.extend(["--source_image", video_path])
            else:
                logger.error("No valid source image/video for SadTalker")
                return False

            logger.info(f"Running SadTalker: {' '.join(cmd)}")

            # Run SadTalker
            result = subprocess.run(
                cmd,
                cwd=sadtalker_path,
                capture_output=True,
                text=True,
                check=True
            )

            # Find the generated video file
            output_dir = os.path.dirname(output_path)
            video_files = sorted(
                glob.glob(os.path.join(output_dir, "*.mp4")),
                key=os.path.getmtime
            )

            if not video_files:
                logger.error("SadTalker produced no output video")
                return False

            # Use the most recent output
            input_video = video_files[-1]

            # Post-process the video (scale, normalize)
            self._post_process_video(input_video, output_path)

            logger.info(f"✅ SadTalker lip-sync completed: {output_path}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"SadTalker failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"SadTalker error: {e}")
            return False

    def _run_wav2lip(self, image_path: Optional[str], video_path: Optional[str],
                    audio_path: str, output_path: str) -> bool:
        """
        Run Wav2Lip lip-sync generation.

        Args:
            image_path: Path to source image (optional)
            video_path: Path to source video (optional)
            audio_path: Path to WAV audio file
            output_path: Output video path

        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting Wav2Lip lip-sync generation")

        try:
            import sys
            wav2lip_path = "third_party/Wav2Lip"
            checkpoint_path = os.path.join(wav2lip_path, "checkpoints", "Wav2Lip.pth")

            if not os.path.exists(checkpoint_path):
                logger.error(f"Wav2Lip checkpoint not found: {checkpoint_path}")
                return False

            # Prepare source video/input
            source_input = self._prepare_wav2lip_input(image_path, video_path, output_path)

            if not source_input:
                logger.error("Failed to prepare Wav2Lip input")
                return False

            # Build Wav2Lip command
            cmd = [
                sys.executable, os.path.join(wav2lip_path, "inference.py"),
                "--checkpoint_path", checkpoint_path,
                "--face", source_input,
                "--audio", audio_path,
                "--outfile", output_path,
                "--nosmooth"  # Disable face smoothing for better performance
            ]

            logger.info(f"Running Wav2Lip: {' '.join(cmd)}")

            # Run Wav2Lip
            result = subprocess.run(
                cmd,
                cwd=wav2lip_path,
                capture_output=True,
                text=True,
                check=True
            )

            # Post-process the video if needed
            if os.path.exists(output_path):
                self._post_process_video(output_path, output_path)
                logger.info(f"✅ Wav2Lip lip-sync completed: {output_path}")
                return True
            else:
                logger.error("Wav2Lip produced no output video")
                return False

        except subprocess.CalledProcessError as e:
            logger.error(f"Wav2Lip failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Wav2Lip error: {e}")
            return False
        finally:
            # Clean up temporary source video
            if source_input and source_input != (video_path or image_path):
                try:
                    os.remove(source_input)
                except:
                    pass

    def _prepare_wav2lip_input(self, image_path: Optional[str], video_path: Optional[str],
                              output_path: str) -> Optional[str]:
        """Prepare input for Wav2Lip (convert image to video if needed)."""
        # If we have a video, use it directly
        if video_path and os.path.exists(video_path):
            return video_path

        # If we have an image, convert it to a short video
        if image_path and os.path.exists(image_path):
            temp_video = output_path.replace(".mp4", "_temp.mp4")

            try:
                # Create a 30-second video from the image with subtle movement
                cmd = [
                    "ffmpeg", "-y", "-loop", "1", "-i", image_path,
                    "-t", "30",  # 30 seconds
                    "-vf", "scale=512:512,fps=25,zoompan=z='min(1.05,max(1,zoom-0.001))':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-t", "30", temp_video
                ]

                subprocess.run(cmd, check=True, capture_output=True)
                return temp_video

            except Exception as e:
                logger.error(f"Failed to convert image to video for Wav2Lip: {e}")
                return None

        return None

    def _post_process_video(self, input_path: str, output_path: str) -> None:
        """Post-process video (normalize, scale)."""
        try:
            canvas = os.getenv("VIDEO_ENGINE_CANVAS", "1280x720")
            fps = os.getenv("VIDEO_ENGINE_FPS", "25")

            cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", f"scale={canvas},fps={fps}",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k",
                output_path
            ]

            subprocess.run(cmd, check=True, capture_output=True)

        except Exception as e:
            logger.warning(f"Video post-processing failed: {e}")
            # If post-processing fails, just copy the original
            try:
                import shutil
                shutil.copy2(input_path, output_path)
            except:
                pass

    def is_available(self) -> bool:
        """Check if lip-sync backend is available."""
        if not self.enabled:
            return False

        if self.backend == "sadtalker":
            return self.sadtalker_available
        elif self.backend == "wav2lip":
            return self.wav2lip_available
        else:
            return False

    def get_backend_info(self) -> Dict[str, Any]:
        """Get backend information."""
        return {
            "backend": self.backend,
            "enabled": self.enabled,
            "sadtalker_available": self.sadtalker_available,
            "wav2lip_available": self.wav2lip_available,
            "available": self.is_available()
        }

# Global instance
_lipsync_backend = None

def get_lipsync_backend() -> LipSyncBackend:
    """Get or create global lip-sync backend instance."""
    global _lipsync_backend
    if _lipsync_backend is None:
        _lipsync_backend = LipSyncBackend()
    return _lipsync_backend