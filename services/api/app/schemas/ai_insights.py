from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AIInsightData(BaseModel):
    id: str
    type: str
    impact: str
    title: str
    description: str
    confidence: float
    category: str
    data: Dict[str, float]
    created_at: str


class AIInsightMetrics(BaseModel):
    total_insights: int = Field(..., ge=0)
    high_confidence_insights: int = Field(..., ge=0)
    critical_alerts: int = Field(..., ge=0)
    categories: Dict[str, int]


class AIInsightsContext(BaseModel):
    window: Dict[str, str]
    source_counts: Dict[str, int]


class AIInsightsResponse(BaseModel):
    insights: List[AIInsightData]
    metrics: AIInsightMetrics
    context: AIInsightsContext


class AIInsightsFilters(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    platform: Optional[str] = None
    min_confidence: Optional[float] = Field(default=None, ge=0, le=100)


class AIInsightsReportRequest(BaseModel):
    insightIds: List[str] = Field(default_factory=list, min_items=0)
