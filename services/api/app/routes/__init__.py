# Routes package for AutoPro Daune API
from .leads import router as leads_router
from .referrals import router as referrals_router
from .financial import router as financial_router

# Social router may depend on SQLAlchemy; guard to avoid startup crashes on Python 3.13
try:
    from .social import router as social_router
except Exception:
    social_router = None
try:
    from .logs import router as logs_router
except Exception:
    logs_router = None
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
    # Include social_router only if import succeeded
    # logs_router optional
    "health_router",
]

if whatsapp_router:
    __all__.append("whatsapp_router")
if social_router:
    __all__.append("social_router")
