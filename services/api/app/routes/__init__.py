# Routes package for AutoPro Daune API
from .leads import router as leads_router
from .referrals import router as referrals_router
from .financial import router as financial_router
from .social import router as social_router
from .logs import router as logs_router
from .health import router as health_router

# Optional routers
try:
    from .whatsapp import router as whatsapp_router
except ImportError:
    whatsapp_router = None

__all__ = [
    "leads_router",
    "referrals_router", 
    "financial_router",
    "social_router",
    "logs_router",
    "health_router",
]

if whatsapp_router:
    __all__.append("whatsapp_router")
