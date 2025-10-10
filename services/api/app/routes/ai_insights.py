from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import (
    AIInsightsResponse,
    AIInsightsFilters,
    AIInsightsReportRequest,
)
from ..services.ai_insights import AIInsightsService

router = APIRouter(prefix="/api/ai", tags=["AI Insights"])


class AIInsightsQuery:
    """Parse query parameters for the AI insights endpoints."""

    def __init__(
        self,
        start_date: str | None = Query(None, description="Data de început (YYYY-MM-DD)"),
        end_date: str | None = Query(None, description="Data de final (YYYY-MM-DD)"),
        platform: str | None = Query(None, description="Filtru platformă campanie"),
        min_confidence: float | None = Query(
            None, ge=0, le=100, description="Filtru minim pentru scorul de încredere"
        ),
    ) -> None:
        filters = AIInsightsFilters(
            start_date=self._parse_date(start_date),
            end_date=self._parse_date(end_date),
            platform=platform,
            min_confidence=min_confidence,
        )
        self.filters = filters

    @staticmethod
    def _parse_date(value: str | None):
        if not value:
            return None
        return datetime.fromisoformat(value).date()


@router.get("/insights", response_model=AIInsightsResponse)
def get_ai_insights(
    params: AIInsightsQuery = Depends(),
    db: Session = Depends(get_db),
) -> AIInsightsResponse:
    service = AIInsightsService(db)
    payload = service.get_predictive_insights(**params.filters.dict())
    return AIInsightsResponse(**payload)


@router.post("/generate-report")
def generate_ai_report(
    request: AIInsightsReportRequest,
    params: AIInsightsQuery = Depends(),
    db: Session = Depends(get_db),
):
    service = AIInsightsService(db)
    payload = service.get_predictive_insights(**params.filters.dict())
    report = service.generate_report(request.insightIds, payload["insights"])
    return report
