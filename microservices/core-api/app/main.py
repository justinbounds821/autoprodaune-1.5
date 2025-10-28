"""
Core API Service - Leads, Referrals, Financial
Port: 8001 (microservicii: 8000 intern, 8001 extern via gateway)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AutoPro Core API",
    version="3.0.0",
    description="Core business logic: Leads, Referrals, Financial, Analytics"
)

# CORS - permisiv pentru development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
def health():
    return {
        "service": "core-api",
        "status": "healthy",
        "version": "3.0.0",
        "port": int(os.getenv("PORT", "8000"))
    }

# Root endpoint
@app.get("/")
def root():
    return {
        "service": "AutoPro Core API",
        "version": "3.0.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }

# Import routes - lazy loading pentru a evita erori dacă lipsesc dependințe
try:
    from .routes.leads import router as leads_router
    app.include_router(leads_router, prefix="/api", tags=["leads"])
    logger.info("✅ Leads router loaded")
except Exception as e:
    logger.warning(f"⚠️ Leads router not loaded: {e}")

try:
    from .routes.referrals import router as referrals_router
    app.include_router(referrals_router, prefix="/api", tags=["referrals"])
    logger.info("✅ Referrals router loaded")
except Exception as e:
    logger.warning(f"⚠️ Referrals router not loaded: {e}")

try:
    from .routes.financial import router as financial_router
    app.include_router(financial_router, prefix="/api", tags=["financial"])
    logger.info("✅ Financial router loaded")
except Exception as e:
    logger.warning(f"⚠️ Financial router not loaded: {e}")

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

logger.info("🚀 Core API Service started")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
