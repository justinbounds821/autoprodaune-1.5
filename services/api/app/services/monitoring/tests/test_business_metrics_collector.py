import pytest

from ..collectors import BusinessMetricsCollector
from ...analytics.processor import AnalyticsProcessor


class FakeSupabaseService:
    def __init__(self):
        self.financial_calls = 0
        self.social_calls = 0

    def financial_dashboard(self):
        self.financial_calls += 1
        return {
            "total_revenue": 1250.0,
            "total_costs": 450.0,
            "net_profit": 800.0,
            "roi_percentage": 177.78,
            "recent_revenues": [
                {"amount": 750.0, "timestamp": "2024-01-02T10:00:00Z", "currency": "EUR"},
                {"amount": 500.0, "timestamp": "2024-01-01T10:00:00Z", "currency": "EUR"},
            ],
            "recent_costs": [
                {"cost": 250.0, "timestamp": "2024-01-02T09:30:00Z", "currency": "EUR"},
            ],
        }

    def social_summary(self):
        self.social_calls += 1
        return {
            "tiktok": {
                "posts_today": 3,
                "followers": 1520,
                "engagement_rate": 4.5,
                "revenue": 95.0,
            },
            "instagram": {
                "posts_today": 2,
                "followers": 980,
                "engagement_rate": 3.1,
                "revenue": 45.5,
            },
        }


@pytest.fixture
def collector():
    supabase = FakeSupabaseService()
    analytics_processor = AnalyticsProcessor()
    return supabase, BusinessMetricsCollector(supabase, analytics_processor)


def test_collect_financial_metrics_queries_supabase(collector):
    supabase, business_collector = collector

    metrics = business_collector.collect_financial_metrics()

    assert supabase.financial_calls == 1, "financial_dashboard should be queried"

    metric_map = {metric.name: metric for metric in metrics}

    assert metric_map["business_total_revenue"].value == pytest.approx(1250.0)
    assert metric_map["business_total_costs"].value == pytest.approx(450.0)
    assert metric_map["business_net_profit"].value == pytest.approx(800.0)

    recent_metrics = [m for m in metrics if m.name == "business_financial_recent_activity_count"]
    assert recent_metrics, "expected analytics aggregation metric for financial data"
    assert recent_metrics[0].value >= 1


def test_collect_social_media_metrics_queries_supabase(collector):
    supabase, business_collector = collector

    metrics = business_collector.collect_social_media_metrics()

    assert supabase.social_calls == 1, "social_summary should be queried"

    followers_metrics = [
        m
        for m in metrics
        if m.name == "social_media_followers_total" and m.labels.get("platform") == "tiktok"
    ]
    assert followers_metrics, "expected follower metric for TikTok platform"
    assert followers_metrics[0].value == pytest.approx(1520)

    count_metrics = [m for m in metrics if m.name == "social_media_metrics_count"]
    assert count_metrics, "expected analytics aggregation metric for social data"
    assert count_metrics[0].value >= 1
