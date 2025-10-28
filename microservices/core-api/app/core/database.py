"""
Enhanced database operations for AutoPro Daune.

This module provides centralized database operations that integrate with
and extend the existing SupabaseService functionality.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

from supabase import create_client, Client
from postgrest.exceptions import APIError

# Import existing SupabaseService for integration
from ..services.supabase_client import SupabaseService, get_supabase_service_instance

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Enhanced database manager that extends SupabaseService functionality.

    This class provides high-level database operations while leveraging
    the existing SupabaseService for core functionality.
    """

    def __init__(self):
        """Initialize the database manager."""
        # Use existing SupabaseService as the foundation
        self.supabase_service = get_supabase_service_instance()
        self.client = self.supabase_service.client  # Now using the property

        # Keep direct access for compatibility
        self.service_client = self.client

        logger.info("✅ Enhanced Database Manager initialized with SupabaseService integration")

    # ==================== LEAD OPERATIONS ====================

    def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lead using the existing SupabaseService."""
        try:
            # Use existing SupabaseService method
            result = self.supabase_service.lead_create(lead_data)

            if result and result.get("id"):
                logger.info(f"✅ Lead created via SupabaseService: {result.get('id')}")
                return {
                    "success": True,
                    "message": "Lead creat cu succes",
                    "data": [result]
                }
            else:
                logger.error("❌ No data returned from SupabaseService lead creation")
                return {
                    "success": False,
                    "message": "Eroare la crearea lead-ului",
                    "data": []
                }

        except Exception as e:
            logger.error(f"❌ Error creating lead via SupabaseService: {e}")
            return {
                "success": False,
                "message": f"Eroare: {e}",
                "data": []
            }

    async def get_leads(
        self,
        page: int = 1,
        limit: int = 20,
        source: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get leads with advanced filtering and pagination."""
        try:
            # Get leads using existing service
            leads = self.supabase_service.leads_list(limit=500)  # Get all first for filtering

            # Apply filters
            filtered_leads = leads

            if source and source != "all":
                filtered_leads = [lead for lead in filtered_leads if lead.get("source") == source]

            if status and status != "all":
                filtered_leads = [lead for lead in filtered_leads if lead.get("status") == status]

            if search:
                search_lower = search.lower()
                filtered_leads = [
                    lead for lead in filtered_leads
                    if (lead.get("name", "").lower().find(search_lower) != -1 or
                        lead.get("email", "").lower().find(search_lower) != -1 or
                        lead.get("phone", "").find(search) != -1)
                ]

            # Apply pagination
            total = len(filtered_leads)
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paginated_leads = filtered_leads[start_idx:end_idx]

            return {
                "success": True,
                "items": paginated_leads,
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit if total > 0 else 0
            }

        except Exception as e:
            logger.error(f"❌ Error getting leads: {e}")
            return {
                "success": False,
                "items": [],
                "total": 0,
                "error": str(e)
            }

    async def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific lead by ID."""
        try:
            result = self.client.table("leads").select("*").eq("id", lead_id).execute()

            if result.data:
                return result.data[0]
            else:
                return None

        except Exception as e:
            logger.error(f"❌ Error getting lead {lead_id}: {e}")
            return None

    async def update_lead(self, lead_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a lead."""
        try:
            update_data["updated_at"] = datetime.now().isoformat()

            result = self.client.table("leads").update(update_data).eq("id", lead_id).execute()

            if result.data:
                return {
                    "success": True,
                    "message": "Lead actualizat cu succes",
                    "data": result.data[0]
                }
            else:
                return {
                    "success": False,
                    "message": "Lead-ul nu a fost găsit",
                    "data": None
                }

        except Exception as e:
            logger.error(f"❌ Error updating lead {lead_id}: {e}")
            return {
                "success": False,
                "message": f"Eroare la actualizare: {e}",
                "data": None
            }

    # ==================== REFERRAL OPERATIONS ====================

    async def create_referral(self, referral_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new referral using SupabaseService."""
        try:
            # Use existing SupabaseService method
            result = self.supabase_service.referral_create(referral_data)

            if result and result.get("id"):
                logger.info(f"✅ Referral created via SupabaseService: {result.get('id')}")
                return {
                    "success": True,
                    "message": "Referral creat cu succes",
                    "data": [result]
                }
            else:
                return {
                    "success": False,
                    "message": "Eroare la crearea referral-ului",
                    "data": []
                }

        except Exception as e:
            logger.error(f"❌ Error creating referral: {e}")
            return {
                "success": False,
                "message": f"Eroare: {e}",
                "data": []
            }

    async def get_referrals(self, phone: Optional[str] = None) -> Dict[str, Any]:
        """Get referrals using SupabaseService."""
        try:
            referrals = self.supabase_service.referrals_list()

            if phone:
                referrals = [r for r in referrals if r.get("referrer_phone") == phone]

            return {
                "success": True,
                "items": referrals,
                "total": len(referrals)
            }

        except Exception as e:
            logger.error(f"❌ Error getting referrals: {e}")
            return {
                "success": False,
                "items": [],
                "error": str(e)
            }

    async def get_referral_stats(self) -> Dict[str, Any]:
        """Get referral statistics using SupabaseService."""
        try:
            # Use existing method from SupabaseService
            stats = self.supabase_service.referral_stats()
            return stats

        except Exception as e:
            logger.error(f"❌ Error getting referral stats: {e}")
            return {
                "total_referrals": 0,
                "completed_referrals": 0,
                "pending_referrals": 0,
                "total_rewards_paid": 0,
                "error": str(e)
            }

    # ==================== SOCIAL MEDIA OPERATIONS ====================

    async def create_social_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a social media post record."""
        try:
            post_data["created_at"] = datetime.now().isoformat()
            post_data["updated_at"] = datetime.now().isoformat()

            result = self.client.table("social_posts").insert(post_data).execute()

            if result.data:
                return {
                    "success": True,
                    "data": result.data[0]
                }
            else:
                return {
                    "success": False,
                    "error": "No data returned"
                }

        except Exception as e:
            logger.error(f"❌ Error creating social post: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_social_posts(self, limit: int = 20) -> Dict[str, Any]:
        """Get recent social media posts."""
        try:
            result = self.client.table("social_posts").select("*").order("created_at", desc=True).limit(limit).execute()

            return {
                "success": True,
                "items": result.data or [],
                "total": len(result.data) if result.data else 0
            }

        except Exception as e:
            logger.error(f"❌ Error getting social posts: {e}")
            return {
                "success": False,
                "items": [],
                "error": str(e)
            }

    async def get_social_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get social media analytics."""
        try:
            # Get posts from specified period
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            result = self.client.table("social_posts").select("*").gte("created_at", start_date).execute()

            posts = result.data or []

            # Calculate analytics
            total_posts = len(posts)
            total_views = sum(p.get("views", 0) for p in posts)
            total_likes = sum(p.get("likes", 0) for p in posts)
            total_shares = sum(p.get("shares", 0) for p in posts)
            total_comments = sum(p.get("comments", 0) for p in posts)
            total_clicks = sum(p.get("clicks", 0) for p in posts)
            total_leads = sum(p.get("leads_generated", 0) for p in posts)

            # Platform breakdown
            platform_stats = {}
            for post in posts:
                platforms = post.get("platforms", [])
                for platform in platforms:
                    if platform not in platform_stats:
                        platform_stats[platform] = {
                            "posts": 0,
                            "views": 0,
                            "engagement": 0
                        }
                    platform_stats[platform]["posts"] += 1
                    platform_stats[platform]["views"] += post.get("views", 0) // len(platforms)
                    platform_stats[platform]["engagement"] += post.get("engagement", 0) // len(platforms)

            return {
                "period_days": days,
                "total_posts": total_posts,
                "total_views": total_views,
                "total_likes": total_likes,
                "total_shares": total_shares,
                "total_comments": total_comments,
                "total_clicks": total_clicks,
                "total_leads_generated": total_leads,
                "engagement_rate": (total_likes + total_shares + total_comments) / total_views * 100 if total_views > 0 else 0,
                "click_through_rate": total_clicks / total_views * 100 if total_views > 0 else 0,
                "lead_conversion_rate": total_leads / total_clicks * 100 if total_clicks > 0 else 0,
                "platform_breakdown": platform_stats
            }

        except Exception as e:
            logger.error(f"❌ Error getting social analytics: {e}")
            return {
                "period_days": days,
                "total_posts": 0,
                "error": str(e)
            }

    # ==================== AUTOMATION OPERATIONS ====================

    async def get_automation_config(self, config_key: str) -> Optional[Dict[str, Any]]:
        """Get automation configuration by key."""
        try:
            result = self.client.table("automation_config").select("*").eq("config_key", config_key).execute()

            if result.data:
                return result.data[0]
            else:
                return None

        except Exception as e:
            logger.error(f"❌ Error getting automation config {config_key}: {e}")
            return None

    async def update_automation_config(self, config_key: str, config_value: Dict[str, Any]) -> Dict[str, Any]:
        """Update automation configuration."""
        try:
            config_data = {
                "config_key": config_key,
                "config_value": config_value,
                "updated_at": datetime.now().isoformat()
            }

            result = self.client.table("automation_config").upsert(config_data).execute()

            return {
                "success": True,
                "data": result.data[0] if result.data else None
            }

        except Exception as e:
            logger.error(f"❌ Error updating automation config: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # ==================== WHATSAPP OPERATIONS ====================

    async def create_whatsapp_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a WhatsApp conversation."""
        try:
            phone_number = conversation_data.get("phone_number")

            if not phone_number:
                return {
                    "success": False,
                    "error": "Phone number is required"
                }

            # Check if conversation already exists
            existing = self.client.table("whatsapp_conversations").select("*").eq("phone_number", phone_number).execute()

            if existing.data:
                # Update existing conversation
                conversation_id = existing.data[0]["id"]
                update_data = {
                    "last_message_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }

                if "status" in conversation_data:
                    update_data["status"] = conversation_data["status"]

                result = self.client.table("whatsapp_conversations").update(update_data).eq("id", conversation_id).execute()

                return {
                    "success": True,
                    "data": result.data[0] if result.data else existing.data[0],
                    "is_new": False
                }
            else:
                # Create new conversation
                conversation_data["created_at"] = datetime.now().isoformat()
                conversation_data["updated_at"] = datetime.now().isoformat()
                conversation_data["last_message_at"] = datetime.now().isoformat()

                result = self.client.table("whatsapp_conversations").insert(conversation_data).execute()

                return {
                    "success": True,
                    "data": result.data[0] if result.data else None,
                    "is_new": True
                }

        except Exception as e:
            logger.error(f"❌ Error creating WhatsApp conversation: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def create_whatsapp_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a WhatsApp message record."""
        try:
            message_data["created_at"] = datetime.now().isoformat()

            result = self.client.table("whatsapp_messages").insert(message_data).execute()

            if result.data:
                return {
                    "success": True,
                    "data": result.data[0]
                }
            else:
                return {
                    "success": False,
                    "error": "No data returned"
                }

        except Exception as e:
            logger.error(f"❌ Error creating WhatsApp message: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # ==================== ANALYTICS & REPORTING ====================

    async def get_daily_summary(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get daily summary statistics."""
        try:
            if date is None:
                date = datetime.now().date()

            date_start = datetime.combine(date, datetime.min.time()).isoformat()
            date_end = datetime.combine(date, datetime.max.time()).isoformat()

            # Get leads
            leads_result = self.client.table("leads").select("*").gte("created_at", date_start).lte("created_at", date_end).execute()
            leads = leads_result.data or []

            # Get social posts
            posts_result = self.client.table("social_posts").select("*").gte("created_at", date_start).lte("created_at", date_end).execute()
            posts = posts_result.data or []

            # Get referrals
            referrals_result = self.client.table("referrals").select("*").gte("created_at", date_start).lte("created_at", date_end).execute()
            referrals = referrals_result.data or []

            # Calculate metrics
            total_leads = len(leads)
            total_posts = len(posts)
            total_views = sum(p.get("views", 0) for p in posts)
            total_engagement = sum(p.get("engagement", 0) for p in posts)
            total_referrals = len(referrals)

            # Lead sources breakdown
            lead_sources = {}
            for lead in leads:
                source = lead.get("source", "unknown")
                lead_sources[source] = lead_sources.get(source, 0) + 1

            return {
                "date": date.isoformat(),
                "total_leads": total_leads,
                "total_posts": total_posts,
                "total_views": total_views,
                "total_engagement": total_engagement,
                "total_referrals": total_referrals,
                "lead_sources": lead_sources,
                "engagement_rate": (total_engagement / total_views * 100) if total_views > 0 else 0
            }

        except Exception as e:
            logger.error(f"❌ Error getting daily summary: {e}")
            return {
                "date": date.isoformat() if date else None,
                "total_leads": 0,
                "error": str(e)
            }

    # ==================== UTILITY METHODS ====================

    def test_connection(self) -> bool:
        """Test the database connection."""
        try:
            # Simple query to test connection - use a table that should exist
            result = self.client.table("leads").select("*").limit(1).execute()
            logger.info("✅ Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False

# Global database instance
_db_manager = None

def get_database() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

# Dependency for FastAPI
def get_db():
    """FastAPI dependency to get database instance."""
    return get_database()

# Legacy compatibility
get_supabase = get_database