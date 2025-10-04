# services/api/app/services/captions_generator.py
"""
Captions generator for ASS/SSA subtitle files.
SRP: Subtitle generation only, no business logic.
"""
import os
import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class CaptionsGenerator:
    """Service for generating ASS/SSA subtitle files from scripts."""

    def __init__(self):
        """Initialize captions generator."""
        self.words_per_minute = 150  # Average speaking rate
        self.min_caption_duration = 1.0  # Minimum seconds per caption
        self.max_caption_duration = 4.0  # Maximum seconds per caption

        logger.info("✅ Captions generator initialized")

    def generate_captions(self, script: str, audio_duration: float) -> str:
        """
        Generate ASS subtitle content from script and audio duration.

        Args:
            script: Text script to convert to captions
            audio_duration: Total audio duration in seconds

        Returns:
            ASS subtitle content as string
        """
        if not script or not script.strip():
            logger.warning("Empty script provided for captions")
            return self._generate_empty_ass()

        # Split script into sentences/phrases
        phrases = self._split_into_phrases(script)

        if not phrases:
            logger.warning("No phrases found in script")
            return self._generate_empty_ass()

        # Calculate timing for each phrase
        captions = self._calculate_phrase_timing(phrases, audio_duration)

        # Generate ASS content
        ass_content = self._generate_ass_content(captions)

        logger.info(f"Generated {len(captions)} caption entries for {audio_duration:.1f}s audio")
        return ass_content

    def _split_into_phrases(self, script: str) -> List[str]:
        """Split script into meaningful phrases for captions."""
        # Clean the script
        script = script.strip()

        # Split by common delimiters
        delimiters = [r'[.!?]+', r'[;:]', r'[,]', r' - ', r' – ']
        phrases = [script]

        for delimiter in delimiters:
            new_phrases = []
            for phrase in phrases:
                parts = re.split(f'({delimiter})', phrase)
                # Rejoin delimiters with their following text
                for i in range(0, len(parts) - 1, 2):
                    if i + 1 < len(parts):
                        new_phrases.append(parts[i] + parts[i + 1])
                    else:
                        new_phrases.append(parts[i])
                if len(parts) % 2 == 1:  # Odd number of parts
                    new_phrases.append(parts[-1])
            phrases = new_phrases

        # Filter out very short phrases and clean up
        phrases = [
            phrase.strip()
            for phrase in phrases
            if len(phrase.strip()) > 3  # At least 4 characters
        ]

        return phrases

    def _calculate_phrase_timing(self, phrases: List[str], audio_duration: float) -> List[Dict[str, Any]]:
        """Calculate start and end times for each phrase."""
        if not phrases:
            return []

        # Estimate total words
        total_words = sum(len(phrase.split()) for phrase in phrases)

        # Calculate average duration per word
        if total_words == 0:
            return []

        avg_duration_per_word = audio_duration / total_words

        captions = []
        current_time = 0.0

        for phrase in phrases:
            words_in_phrase = len(phrase.split())

            # Calculate duration for this phrase
            phrase_duration = max(
                self.min_caption_duration,
                min(self.max_caption_duration, words_in_phrase * avg_duration_per_word)
            )

            # Ensure we don't exceed total duration
            if current_time + phrase_duration > audio_duration:
                phrase_duration = audio_duration - current_time
                if phrase_duration < self.min_caption_duration:
                    break  # Can't fit this phrase

            captions.append({
                "text": phrase,
                "start_time": current_time,
                "end_time": current_time + phrase_duration
            })

            current_time += phrase_duration

            # Stop if we've reached the end
            if current_time >= audio_duration:
                break

        return captions

    def _generate_ass_content(self, captions: List[Dict[str, Any]]) -> str:
        """Generate ASS subtitle file content."""
        ass_content = """[Script Info]
Title: AutoPro Video Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,48,&Hffffff,&Hffffff,&H0,&H0,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        for i, caption in enumerate(captions):
            start_time_str = self._format_ass_time(caption["start_time"])
            end_time_str = self._format_ass_time(caption["end_time"])

            # Escape commas in text for ASS format
            safe_text = caption["text"].replace(',', '\\,')

            ass_content += f"Dialogue: 0,{start_time_str},{end_time_str},Default,,0,0,0,,{safe_text}\n"

        return ass_content

    def _format_ass_time(self, seconds: float) -> str:
        """Format seconds as ASS time format (H:MM:SS.CC)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60

        return f"{hours}:{minutes:02d}:{secs:02.1f}"

    def _generate_empty_ass(self) -> str:
        """Generate empty ASS file for when no captions are available."""
        return """[Script Info]
Title: AutoPro Video Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,48,&Hffffff,&Hffffff,&H0,&H0,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def attach_captions_to_timeline(self, timeline: Dict[str, Any], script: str, audio_duration: float) -> Dict[str, Any]:
        """
        Attach captions to timeline configuration.

        Args:
            timeline: Existing timeline configuration
            script: Script text for captions
            audio_duration: Audio duration in seconds

        Returns:
            Updated timeline with captions layer
        """
        # Generate captions content
        captions_content = self.generate_captions(script, audio_duration)

        # Find existing captions layer or add new one
        captions_layer = None
        for layer in timeline.get("layers", []):
            if layer.get("type") == "captions":
                captions_layer = layer
                break

        if not captions_layer:
            # Add new captions layer
            captions_layer = {
                "type": "captions",
                "in": 0,
                "out": audio_duration,
                "params": {
                    "script": script,
                    "style": "white_text"
                }
            }
            timeline.setdefault("layers", []).append(captions_layer)

        # Update captions parameters
        captions_layer["params"]["ass_content"] = captions_content

        return timeline

    def save_captions_file(self, captions_content: str, output_path: str) -> bool:
        """
        Save captions content to file.

        Args:
            captions_content: ASS content to save
            output_path: Path to save the file

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Write ASS file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(captions_content)

            logger.info(f"✅ Captions saved to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save captions file {output_path}: {e}")
            return False

# Global instance
_captions_generator = None

def get_captions_generator() -> CaptionsGenerator:
    """Get or create global captions generator instance."""
    global _captions_generator
    if _captions_generator is None:
        _captions_generator = CaptionsGenerator()
    return _captions_generator