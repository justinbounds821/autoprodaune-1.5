from decimal import Decimal as D
from typing import Dict, Any, Optional
from datetime import datetime
from .types import CostCategory
from .errors import CostCalcError
from .rates import DEFAULT_RATES

class CostCalculator:
    def __init__(self, rates: Optional[Dict[str, Any]] = None):
        self.rates = rates or DEFAULT_RATES

    # --------- Pika
    def calculate_pika_cost(self, duration_seconds: int, resolution: str = "720p", quality: str = "high") -> Dict[str, Any]:
        if duration_seconds <= 0:
            raise CostCalcError("Durata trebuie să fie pozitivă")
        if duration_seconds > 60:
            raise CostCalcError("Pika suportă maxim 60 secunde")
        pika_rates = self.rates.get("Pika", {})
        if not isinstance(pika_rates, dict):
            raise CostCalcError("Invalid Pika rates configuration")

        resolution_multipliers = pika_rates.get("resolution_multipliers", {})
        quality_multipliers = pika_rates.get("quality_multipliers", {})

        if resolution not in resolution_multipliers:
            raise CostCalcError("Rezoluție invalidă")
        if quality not in quality_multipliers:
            raise CostCalcError("Calitate invalidă")

        base_rate = pika_rates.get("base_rate_per_second", 0)
        min_cost = pika_rates.get("min_cost", 0)

        total = (D(str(base_rate)) * D(duration_seconds) *
                 D(str(resolution_multipliers[resolution])) *
                 D(str(quality_multipliers[quality])))
        if total < D(str(min_cost)):
            total = D(str(min_cost))

        return {
            "provider": "Pika", "operation": "generate_video",
            "cost": total, "credits_used": duration_seconds, "currency": "USD",
            "breakdown": {"duration_seconds": duration_seconds, "resolution": resolution, "quality": quality},
            "metadata": {"video_duration": duration_seconds, "calculation_timestamp": datetime.now().isoformat()},
            "category": CostCategory.VIDEO_GENERATION.value,
        }

    # --------- HeyGen
    def calculate_heygen_cost(self, duration_seconds: int, avatar_type: str = "default", voice_type: str = "standard") -> Dict[str, Any]:
        if duration_seconds <= 0:
            raise CostCalcError("Durata trebuie să fie pozitivă")
        if duration_seconds > 300:
            raise CostCalcError("HeyGen suportă maxim 300 secunde")

        heygen_rates = self.rates.get("HeyGen", {})
        if not isinstance(heygen_rates, dict):
            raise CostCalcError("Invalid HeyGen rates configuration")

        base_rate = heygen_rates.get("base_rate_per_second", 0)
        min_cost = heygen_rates.get("min_cost", 0)
        avatar_multipliers = heygen_rates.get("avatar_multipliers", {})
        voice_multipliers = heygen_rates.get("voice_multipliers", {})

        total = (D(str(base_rate)) * D(duration_seconds) *
                 D(str(avatar_multipliers.get(avatar_type, 1.0))) *
                 D(str(voice_multipliers.get(voice_type, 1.0))))
        if total < D(str(min_cost)):
            total = D(str(min_cost))

        return {
            "provider": "HeyGen", "operation": "generate_video",
            "cost": total, "credits_used": duration_seconds, "currency": "USD",
            "breakdown": {"duration_seconds": duration_seconds, "avatar_type": avatar_type, "voice_type": voice_type},
            "metadata": {"video_duration": duration_seconds, "calculation_timestamp": datetime.now().isoformat()},
            "category": CostCategory.VIDEO_GENERATION.value,
        }

    # --------- Social posting
    def calculate_social_media_posting_cost(self, platform: str, content_type: str = "video", file_size_mb: Optional[float] = None) -> Dict[str, Any]:
        if platform not in self.rates:
            raise CostCalcError("Platformă invalidă")
        if content_type not in ["video", "image", "text"]:
            raise CostCalcError("Tip conținut invalid")

        platform_rates = self.rates.get(platform, {})
        if not isinstance(platform_rates, dict):
            raise CostCalcError(f"Invalid {platform} rates configuration")

        posting_cost = platform_rates.get("posting_cost", 0)
        content_multipliers = platform_rates.get("content_multipliers", {})

        base = D(str(posting_cost))
        mult = D(str(content_multipliers.get(content_type, 1)))
        total = base * mult
        if file_size_mb and file_size_mb > 100:
            total += D(file_size_mb - 100) * D("0.001")

        return {
            "provider": platform, "operation": "post_content",
            "cost": total, "credits_used": 1, "currency": "USD",
            "breakdown": {"base_cost": base, "content_multiplier": mult, "file_size_mb": file_size_mb},
            "metadata": {"platform": platform, "content_type": content_type, "calculation_timestamp": datetime.now().isoformat()},
            "category": CostCategory.SOCIAL_MEDIA_POSTING.value,
        }

    # --------- API calls
    def calculate_api_calls_cost(self, provider: str, num_calls: int, call_type: str = "standard") -> Dict[str, Any]:
        if num_calls <= 0:
            raise CostCalcError("Numărul de apeluri trebuie să fie pozitiv")
        pr = self.rates.get(provider, {})
        base = D(pr.get("api_call_cost", 0))
        mult = D(pr.get("call_type_multipliers", {}).get(call_type, 1))
        total = base * D(num_calls) * mult
        return {
            "provider": provider, "operation": "api_calls",
            "cost": total, "credits_used": num_calls, "currency": "USD",
            "breakdown": {"base_rate_per_call": base, "num_calls": num_calls, "type_multiplier": mult, "call_type": call_type},
            "metadata": {"provider": provider, "calculation_timestamp": datetime.now().isoformat()},
            "category": CostCategory.API_CALLS.value,
        }
