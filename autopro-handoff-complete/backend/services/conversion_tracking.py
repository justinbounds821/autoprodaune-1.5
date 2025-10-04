"""
Conversion Tracking Service for AutoPro Daune.

Tracks user actions, lead sources, and conversion events across all platforms.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class ConversionSource(str, Enum):
    """Lead/conversion sources"""
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    LANDING_PAGE = "landing_page"
    WHATSAPP = "whatsapp"
    REFERRAL = "referral"
    DIRECT = "direct"
    ORGANIC = "organic"
    PAID = "paid"


class ConversionEvent(str, Enum):
    """Conversion event types"""
    PAGE_VIEW = "page_view"
    FORM_SUBMIT = "form_submit"
    LEAD_CREATED = "lead_created"
    WHATSAPP_CLICK = "whatsapp_click"
    PHONE_CLICK = "phone_click"
    REFERRAL_CLICK = "referral_click"
    VIDEO_VIEW = "video_view"
    SOCIAL_CLICK = "social_click"
    DOCUMENT_UPLOAD = "document_upload"
    FORM_STARTED = "form_started"


class ConversionTracker:
    """Track and analyze conversion events"""
    
    def __init__(self, supabase_client=None):
        """
        Initialize conversion tracker.
        
        Args:
            supabase_client: Optional Supabase client for database operations
        """
        self.supabase = supabase_client
    
    def track_event(
        self,
        event_type: ConversionEvent,
        source: ConversionSource,
        user_id: Optional[str] = None,
        lead_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track a conversion event.
        
        Args:
            event_type: Type of event (form_submit, whatsapp_click, etc.)
            source: Traffic source (tiktok, landing_page, etc.)
            user_id: Optional user/session ID
            lead_id: Optional lead ID if lead was created
            metadata: Additional event data (UTM params, page URL, etc.)
            
        Returns:
            Dictionary with event tracking result
        """
        try:
            event_data = {
                "event_type": event_type.value,
                "source": source.value,
                "user_id": user_id,
                "lead_id": lead_id,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat()
            }
            
            # Save to database if Supabase client available
            if self.supabase:
                try:
                    result = self.supabase._table_insert("conversion_events", event_data)
                    logger.info(f"[ConversionTracker] Event tracked: {event_type.value} from {source.value}")
                    return {"success": True, "event_id": result.get("id"), **event_data}
                except Exception as db_error:
                    logger.warning(f"[ConversionTracker] Database insert failed: {db_error}")
            
            # Fallback: log event even if DB fails
            logger.info(f"[ConversionTracker] Event: {event_type.value} | Source: {source.value} | User: {user_id}")
            return {"success": True, "event_id": None, **event_data}
            
        except Exception as e:
            logger.error(f"[ConversionTracker] Failed to track event: {e}")
            return {"success": False, "error": str(e)}
    
    def track_lead_created(
        self,
        lead_id: str,
        source: ConversionSource,
        utm_params: Optional[Dict[str, str]] = None,
        referrer: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track lead creation with source attribution.
        
        Args:
            lead_id: Created lead ID
            source: Traffic source
            utm_params: UTM parameters (utm_source, utm_medium, utm_campaign)
            referrer: HTTP referrer
            
        Returns:
            Tracking result
        """
        metadata = {
            "utm_params": utm_params or {},
            "referrer": referrer,
            "attribution": self._determine_attribution(source, utm_params)
        }
        
        return self.track_event(
            event_type=ConversionEvent.LEAD_CREATED,
            source=source,
            lead_id=lead_id,
            metadata=metadata
        )
    
    def track_whatsapp_click(
        self,
        source: ConversionSource,
        user_id: Optional[str] = None,
        cta_location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track WhatsApp CTA clicks.
        
        Args:
            source: Where the click came from
            user_id: Optional user/session ID
            cta_location: Where CTA was clicked (video, landing_page, etc.)
            
        Returns:
            Tracking result
        """
        metadata = {
            "cta_location": cta_location,
            "platform": "whatsapp"
        }
        
        return self.track_event(
            event_type=ConversionEvent.WHATSAPP_CLICK,
            source=source,
            user_id=user_id,
            metadata=metadata
        )
    
    def get_conversion_rate(
        self,
        source: Optional[ConversionSource] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate conversion rate by source.
        
        Args:
            source: Optional specific source to analyze
            days: Number of days to analyze
            
        Returns:
            Conversion rate statistics
        """
        try:
            if not self.supabase:
                return {"error": "Database not available"}
            
            # Get date range
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Query conversion events
            filters = [("gte", "created_at", start_date)]
            if source:
                filters.append(("eq", "source", source.value))
            
            events = self.supabase._table_select(
                "conversion_events",
                "*",
                filters=filters
            )
            
            # Calculate stats
            total_events = len(events)
            leads_created = len([e for e in events if e.get("event_type") == "lead_created"])
            whatsapp_clicks = len([e for e in events if e.get("event_type") == "whatsapp_click"])
            page_views = len([e for e in events if e.get("event_type") == "page_view"])
            
            conversion_rate = (leads_created / page_views * 100) if page_views > 0 else 0
            click_through_rate = (whatsapp_clicks / page_views * 100) if page_views > 0 else 0
            
            return {
                "source": source.value if source else "all",
                "days": days,
                "total_events": total_events,
                "page_views": page_views,
                "leads_created": leads_created,
                "whatsapp_clicks": whatsapp_clicks,
                "conversion_rate": round(conversion_rate, 2),
                "click_through_rate": round(click_through_rate, 2),
                "lead_to_whatsapp_ratio": round(
                    (whatsapp_clicks / leads_created) if leads_created > 0 else 0, 2
                )
            }
            
        except Exception as e:
            logger.error(f"[ConversionTracker] Error calculating conversion rate: {e}")
            return {"error": str(e)}
    
    def get_top_sources(self, days: int = 30, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get top performing traffic sources.
        
        Args:
            days: Number of days to analyze
            limit: Max number of sources to return
            
        Returns:
            List of top sources with stats
        """
        try:
            sources = [source for source in ConversionSource]
            source_stats = []
            
            for source in sources:
                stats = self.get_conversion_rate(source=source, days=days)
                if not stats.get("error") and stats.get("total_events", 0) > 0:
                    source_stats.append(stats)
            
            # Sort by leads created
            source_stats.sort(key=lambda x: x.get("leads_created", 0), reverse=True)
            
            return source_stats[:limit]
            
        except Exception as e:
            logger.error(f"[ConversionTracker] Error getting top sources: {e}")
            return []
    
    def _determine_attribution(
        self,
        source: ConversionSource,
        utm_params: Optional[Dict[str, str]]
    ) -> str:
        """
        Determine attribution model (first-touch, last-touch).
        
        For now, using last-touch attribution (source that directly led to conversion).
        Future: Implement multi-touch attribution.
        """
        attribution = f"last_touch:{source.value}"
        
        if utm_params:
            campaign = utm_params.get("utm_campaign", "")
            medium = utm_params.get("utm_medium", "")
            if campaign:
                attribution += f":campaign_{campaign}"
            if medium:
                attribution += f":medium_{medium}"
        
        return attribution


# Helper functions for easy tracking
def track_page_view(source: str, path: str, user_id: Optional[str] = None):
    """Quick helper to track page view"""
    tracker = ConversionTracker()
    return tracker.track_event(
        event_type=ConversionEvent.PAGE_VIEW,
        source=ConversionSource(source),
        user_id=user_id,
        metadata={"path": path}
    )


def track_form_submit(source: str, form_type: str, lead_id: Optional[str] = None):
    """Quick helper to track form submission"""
    tracker = ConversionTracker()
    return tracker.track_event(
        event_type=ConversionEvent.FORM_SUBMIT,
        source=ConversionSource(source),
        lead_id=lead_id,
        metadata={"form_type": form_type}
    )


def track_whatsapp_click(source: str, location: str):
    """Quick helper to track WhatsApp CTA click"""
    tracker = ConversionTracker()
    return tracker.track_whatsapp_click(
        source=ConversionSource(source),
        cta_location=location
    )
