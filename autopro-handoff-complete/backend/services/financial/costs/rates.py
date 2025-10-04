from decimal import Decimal as D

DEFAULT_RATES = {
    "Pika": {
        "base_rate_per_second": D("0.05"),
        "min_cost": D("0.10"),
        "resolution_multipliers": {"720p": D("1.0"), "1080p": D("1.5"), "4K": D("2.0")},
        "quality_multipliers": {"low": D("0.7"), "medium": D("1.0"), "high": D("1.3")},
    },
    "HeyGen": {
        "base_rate_per_second": D("0.03"),
        "min_cost": D("0.05"),
        "avatar_multipliers": {"default": D("1.0"), "premium": D("1.4"), "custom": D("2.0")},
        "voice_multipliers": {"standard": D("1.0"), "premium": D("1.2"), "custom": D("1.8")},
    },
    "TikTok": {
        "posting_cost": D("0.01"),
        "content_multipliers": {"text": D("1.0"), "image": D("1.2"), "video": D("1.5")},
        "api_call_cost": D("0.001"),
    },
    "Instagram": {
        "posting_cost": D("0.015"),
        "content_multipliers": {"text": D("1.0"), "image": D("1.3"), "video": D("1.8")},
        "api_call_cost": D("0.002"),
    },
    "YouTube": {
        "posting_cost": D("0.02"),
        "content_multipliers": {"text": D("1.0"), "image": D("1.1"), "video": D("1.4")},
        "api_call_cost": D("0.0015"),
    },
}

CREDIT_LIMITS = {
    "Pika": {"free_tier": 60, "basic_tier": 3600, "pro_tier": 18000, "enterprise_tier": 86400},
    "HeyGen": {"free_tier": 30, "basic_tier": 1800, "pro_tier": 7200, "enterprise_tier": 36000},
    "TikTok": {"free_tier": 1000, "basic_tier": 10000, "pro_tier": 100000, "enterprise_tier": 1000000},
    "Instagram": {"free_tier": 500, "basic_tier": 5000, "pro_tier": 50000, "enterprise_tier": 500000},
    "YouTube": {"free_tier": 10000, "basic_tier": 100000, "pro_tier": 1000000, "enterprise_tier": 10000000},
}

CONFIG = {
    "currency": "USD",
    "tax_rate": D("0.05"),
    "overhead_rate": D("0.10"),
}
