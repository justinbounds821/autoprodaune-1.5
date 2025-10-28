# services/api/app/services/job_repo_supabase.py
"""
Supabase job repository.
SRP: Persist video job data to Supabase.
"""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Singleton instance
_instance: Optional["SupabaseService"] = None


def get_supabase_service_instance():
    """
    Get or create Supabase service singleton.
    
    Returns:
        SupabaseService instance
    """
    global _instance
    
    if _instance is None:
        from .supabase_client import SupabaseService
        _instance = SupabaseService()
        logger.info("Created Supabase service instance")
    
    return _instance
