"""
Core API Service - Subset of main.py pentru Leads, Referrals, Financial
Acest fișier rulează ca serviciu separat pe port 8002
"""
from __future__ import annotations
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

try:
    from dotenv import load_dotenv
    load_dotenv()
except: pass

log = logging.getLogger(__name__)

# Initialize FastAPI app pentru Core API
app = FastAPI(
    title="AutoPro Core API",
    version="3.0.0",
    description="Core business: Leads, Referrals, Financial"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health
@app.get("/health")
def health():
    return {"status": "ok", "service": "core-api", "port": int(os.getenv("PORT", "8002"))}

# Import DOAR routerele pentru core business
try:
    from .routes import leads_router, referrals_router, financial_router
    app.include_router(leads_router)
    app.include_router(referrals_router)
    app.include_router(financial_router)
    log.info("✅ Core routers loaded")
except Exception as e:
    log.error(f"❌ Failed to load routers: {e}")

# Metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8002")))
