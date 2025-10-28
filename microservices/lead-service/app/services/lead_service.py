"""
Lead business logic service
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/workspace/microservices/autopro-common")
from autopro_common import get_logger

from app.models.lead import Lead, LeadActivity

logger = get_logger(__name__)


class LeadService:
    """Lead business logic"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_lead(self, lead_data: Dict[str, Any]) -> Lead:
        """
        Create a new lead
        
        Args:
            lead_data: Lead data dictionary
            
        Returns:
            Created Lead instance
        """
        lead = Lead(**lead_data)
        self.session.add(lead)
        await self.session.commit()
        await self.session.refresh(lead)
        
        # Create initial activity
        activity = LeadActivity(
            lead_id=lead.id,
            activity_type="note",
            title="Lead created",
            description=f"Lead created from source: {lead.source}",
            performed_by="system",
        )
        self.session.add(activity)
        await self.session.commit()
        
        logger.info(f"Lead created: {lead.id}")
        return lead
    
    async def get_lead(self, lead_id: int) -> Optional[Lead]:
        """
        Get lead by ID
        
        Args:
            lead_id: Lead ID
            
        Returns:
            Lead instance or None
        """
        result = await self.session.execute(
            select(Lead).where(Lead.id == lead_id)
        )
        return result.scalar_one_or_none()
    
    async def update_lead(self, lead_id: int, update_data: Dict[str, Any]) -> Optional[Lead]:
        """
        Update a lead
        
        Args:
            lead_id: Lead ID
            update_data: Update data dictionary
            
        Returns:
            Updated Lead instance or None
        """
        lead = await self.get_lead(lead_id)
        if not lead:
            return None
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        
        lead.updated_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(lead)
        
        # Log status change
        if "status" in update_data:
            activity = LeadActivity(
                lead_id=lead.id,
                activity_type="status_change",
                title="Status updated",
                description=f"Status changed to {update_data['status']}",
                performed_by="system",
            )
            self.session.add(activity)
            await self.session.commit()
        
        logger.info(f"Lead updated: {lead_id}")
        return lead
    
    async def delete_lead(self, lead_id: int) -> bool:
        """
        Delete a lead
        
        Args:
            lead_id: Lead ID
            
        Returns:
            True if deleted, False if not found
        """
        lead = await self.get_lead(lead_id)
        if not lead:
            return False
        
        await self.session.delete(lead)
        await self.session.commit()
        
        logger.info(f"Lead deleted: {lead_id}")
        return True
    
    async def create_activity(self, lead_id: int, activity_data: Dict[str, Any]) -> Optional[LeadActivity]:
        """
        Create activity for a lead
        
        Args:
            lead_id: Lead ID
            activity_data: Activity data dictionary
            
        Returns:
            Created LeadActivity instance or None
        """
        # Verify lead exists
        lead = await self.get_lead(lead_id)
        if not lead:
            return None
        
        # Set default title if not provided
        if "title" not in activity_data or not activity_data["title"]:
            activity_data["title"] = f"{activity_data['activity_type'].capitalize()} added"
        
        activity = LeadActivity(lead_id=lead_id, **activity_data)
        self.session.add(activity)
        
        # Update lead's updated_at timestamp
        lead.updated_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(activity)
        
        logger.info(f"Activity created for lead {lead_id}: {activity.activity_type}")
        return activity
    
    async def bulk_update(self, lead_ids: List[int], updates: Dict[str, Any]) -> int:
        """
        Bulk update multiple leads
        
        Args:
            lead_ids: List of lead IDs
            updates: Fields to update
            
        Returns:
            Number of leads updated
        """
        updates["updated_at"] = datetime.utcnow()
        
        result = await self.session.execute(
            update(Lead)
            .where(Lead.id.in_(lead_ids))
            .values(**updates)
        )
        
        await self.session.commit()
        
        updated_count = result.rowcount
        logger.info(f"Bulk updated {updated_count} leads")
        
        return updated_count
