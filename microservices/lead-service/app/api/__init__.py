"""API routes for lead service"""

from .leads import router as leads_router
from .scoring import router as scoring_router

__all__ = ["leads_router", "scoring_router"]
