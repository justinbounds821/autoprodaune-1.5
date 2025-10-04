# services/api/app/services/template_engine.py
"""
Template engine for video timeline generation.
SRP: Timeline building only, no business logic.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class TemplateEngine:
    """Template engine for building video timelines."""

    def __init__(self):
        """Initialize template engine."""
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        logger.info(f"✅ Template engine initialized: {self.templates_dir}")

    def build_timeline(self, request: Dict[str, Any], audio_duration: float) -> Dict[str, Any]:
        """
        Build video timeline from request.

        Args:
            request: Video generation request
            audio_duration: Audio duration in seconds

        Returns:
            Timeline configuration dictionary
        """
        # Check if custom timeline provided
        if request.get("extra", {}).get("timeline"):
            return request["extra"]["timeline"]

        # Check if template_id provided
        template_id = request.get("extra", {}).get("template_id")
        if template_id:
            template = self._load_template(template_id)
            if template:
                return self._apply_template(template, request, audio_duration)

        # Build default timeline
        return self._build_default_timeline(request, audio_duration)

    def _load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Load template from file."""
        template_path = self.templates_dir / f"{template_id}.json"

        if not template_path.exists():
            logger.warning(f"Template {template_id} not found, using default")
            return None

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = json.load(f)
            logger.info(f"Loaded template: {template_id}")
            return template
        except Exception as e:
            logger.error(f"Failed to load template {template_id}: {e}")
            return None

    def _apply_template(self, template: Dict[str, Any], request: Dict[str, Any], audio_duration: float) -> Dict[str, Any]:
        """Apply template with request parameters."""
        timeline = template.copy()

        # Update duration based on audio
        timeline["duration"] = audio_duration

        # Apply request parameters to layers
        for layer in timeline.get("layers", []):
            layer_type = layer.get("type")

            if layer_type == "bg":
                self._apply_bg_params(layer, request)
            elif layer_type == "video":
                self._apply_avatar_params(layer, request)
            elif layer_type == "image":
                self._apply_image_params(layer, request)
            elif layer_type == "captions":
                self._apply_captions_params(layer, request)
            elif layer_type == "text":
                self._apply_text_params(layer, request)

        return timeline

    def _apply_bg_params(self, layer: Dict[str, Any], request: Dict[str, Any]) -> None:
        """Apply background parameters."""
        params = layer.get("params", {})
        bg_image = request.get("extra", {}).get("background_image")
        bg_color = request.get("extra", {}).get("background_color", "black")

        if bg_image:
            params["image_path"] = bg_image
            params["type"] = "image"
        else:
            params["color"] = bg_color
            params["type"] = "color"

    def _apply_avatar_params(self, layer: Dict[str, Any], request: Dict[str, Any]) -> None:
        """Apply avatar parameters."""
        params = layer.get("params", {})

        # Avatar positioning
        avatar_position = request.get("extra", {}).get("avatar_position", "center")
        if avatar_position == "left":
            params["x"] = 0.1
            params["y"] = 0.2
        elif avatar_position == "right":
            params["x"] = 0.6
            params["y"] = 0.2
        else:  # center
            params["x"] = 0.2
            params["y"] = 0.2

        # Avatar size
        avatar_size = request.get("extra", {}).get("avatar_size", "medium")
        if avatar_size == "small":
            params["scale"] = 0.6
        elif avatar_size == "large":
            params["scale"] = 0.9
        else:  # medium
            params["scale"] = 0.8

    def _apply_image_params(self, layer: Dict[str, Any], request: Dict[str, Any]) -> None:
        """Apply image overlay parameters."""
        params = layer.get("params", {})

        # Use avatar image as overlay if available
        avatar_image_url = request.get("avatar_image_url")
        if avatar_image_url:
            params["image_path"] = avatar_image_url

    def _apply_captions_params(self, layer: Dict[str, Any], request: Dict[str, Any]) -> None:
        """Apply captions parameters."""
        params = layer.get("params", {})

        # Enable/disable captions
        captions_enabled = request.get("extra", {}).get("captions_enabled", True)
        if not captions_enabled:
            layer["enabled"] = False
            return

        # Caption style
        caption_style = request.get("extra", {}).get("caption_style", "white_text")
        params["style"] = caption_style

        # Script for captions
        params["script"] = request.get("script", "")

    def _apply_text_params(self, layer: Dict[str, Any], request: Dict[str, Any]) -> None:
        """Apply text overlay parameters."""
        params = layer.get("params", {})

        # Custom text overlay
        text_overlay = request.get("extra", {}).get("text_overlay")
        if text_overlay:
            params["text"] = text_overlay["text"]
            params["x"] = text_overlay.get("x", 0.5)
            params["y"] = text_overlay.get("y", 0.9)

    def _build_default_timeline(self, request: Dict[str, Any], audio_duration: float) -> Dict[str, Any]:
        """Build default talking head timeline."""
        timeline = {
            "duration": audio_duration,
            "fps": int(os.getenv("VIDEO_ENGINE_FPS", "25")),
            "canvas": os.getenv("VIDEO_ENGINE_CANVAS", "1280x720"),
            "layers": []
        }

        # Background layer
        timeline["layers"].append({
            "type": "bg",
            "in": 0,
            "out": audio_duration,
            "params": {
                "type": "color",
                "color": "black"
            }
        })

        # Avatar layer (video if available, otherwise static image)
        if request.get("avatar_video_url"):
            timeline["layers"].append({
                "type": "video",
                "in": 0,
                "out": min(audio_duration, 30),  # Limit avatar video to 30s or audio length
                "params": {
                    "video_path": request["avatar_video_url"],
                    "scale": 0.8,
                    "x": 0.2,
                    "y": 0.2
                }
            })
        elif request.get("avatar_image_url"):
            timeline["layers"].append({
                "type": "image",
                "in": 0,
                "out": audio_duration,
                "params": {
                    "image_path": request["avatar_image_url"]
                }
            })

        # Captions layer (if enabled)
        captions_enabled = request.get("extra", {}).get("captions_enabled", True)
        if captions_enabled and request.get("script"):
            timeline["layers"].append({
                "type": "captions",
                "in": 0,
                "out": audio_duration,
                "params": {
                    "script": request["script"],
                    "style": "white_text"
                }
            })

        # Lower third text (optional)
        lower_third = request.get("extra", {}).get("lower_third")
        if lower_third:
            timeline["layers"].append({
                "type": "text",
                "in": 0,
                "out": audio_duration,
                "params": {
                    "text": lower_third,
                    "x": 0.5,
                    "y": 0.85
                }
            })

        return timeline

    def save_template(self, template_id: str, template: Dict[str, Any]) -> bool:
        """
        Save template to file.

        Args:
            template_id: Template identifier
            template: Template configuration

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            template_path = self.templates_dir / f"{template_id}.json"

            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)

            logger.info(f"✅ Saved template: {template_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save template {template_id}: {e}")
            return False

    def list_templates(self) -> Dict[str, Any]:
        """
        List available templates.

        Returns:
            Dictionary with template information
        """
        try:
            templates = []

            for template_file in self.templates_dir.glob("*.json"):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template = json.load(f)

                    templates.append({
                        "id": template_file.stem,
                        "name": template.get("name", template_file.stem),
                        "description": template.get("description", ""),
                        "duration": template.get("duration", 60),
                        "layers": len(template.get("layers", []))
                    })

                except Exception as e:
                    logger.warning(f"Failed to load template {template_file}: {e}")

            return {
                "templates": templates,
                "total": len(templates)
            }

        except Exception as e:
            logger.error(f"Failed to list templates: {e}")
            return {"templates": [], "total": 0}

# Global instance
_template_engine = None

def get_template_engine() -> TemplateEngine:
    """Get or create global template engine instance."""
    global _template_engine
    if _template_engine is None:
        _template_engine = TemplateEngine()
    return _template_engine