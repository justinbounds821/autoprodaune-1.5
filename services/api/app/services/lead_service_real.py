"""
REAL Lead Management Service - AutoPro Daune
Complete CRUD + Scoring + Timeline + Export
NO MOCKS - All database operations are real
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from ..models.complete_models import Lead, LeadCreate, LeadUpdate, Activity, ActivityCreate
from .supabase_client import get_supabase_service_instance
from fastapi import HTTPException
import csv
import io
import logging

logger = logging.getLogger(__name__)

class LeadService:
    """Real lead management with database persistence"""
    
    def __init__(self):
        self.supabase = get_supabase_service_instance()
    
    def calculate_lead_score(self, lead_data: dict) -> int:
        """
        REAL lead scoring algorithm based on multiple factors
        Returns score 0-100
        """
        score = 0
        
        # Contact information (20 points max)
        if lead_data.get('email'):
            score += 10
        if lead_data.get('phone'):
            score += 10
        
        # Source quality (30 points max)
        source_scores = {
            'referral': 30,      # Highest quality
            'website': 25,       # Direct interest
            'youtube': 20,       # Engaged viewer
            'tiktok': 15,        # Social engagement
            'instagram': 15,     # Social engagement
            'facebook': 10,      # Lower engagement
            'direct': 5          # Unknown source
        }
        score += source_scores.get(lead_data.get('source', 'direct'), 0)
        
        # Engagement indicators from metadata (35 points max)
        metadata = lead_data.get('metadata', {})
        
        if metadata.get('watched_video'):
            score += 15  # Watched educational content
        
        if metadata.get('clicked_cta'):
            score += 20  # Clicked call-to-action
        
        if metadata.get('repeat_visitor'):
            score += 10  # Returned multiple times
        
        if metadata.get('form_submitted'):
            score += 10  # Submitted contact form
        
        # Additional signals (15 points max)
        if lead_data.get('notes'):
            score += 5  # Has additional context
        
        if metadata.get('estimated_damage'):
            score += 10  # Provided damage estimate
        
        return min(score, 100)  # Cap at 100
    
    def determine_priority(self, score: int) -> str:
        """Determine lead priority based on score"""
        if score >= 80:
            return 'urgent'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'
    
    async def create_lead(
        self,
        user_id: UUID,
        lead_data: LeadCreate
    ) -> Lead:
        """
        Create new lead with REAL database insert
        Returns: Created lead with calculated score
        """
        try:
            # Prepare lead data
            lead_dict = lead_data.dict()
            lead_dict['user_id'] = str(user_id)
            
            # Calculate score
            lead_dict['score'] = self.calculate_lead_score(lead_dict)
            lead_dict['priority'] = self.determine_priority(lead_dict['score'])
            
            # Set timestamps
            now = datetime.utcnow().isoformat()
            lead_dict['created_at'] = now
            lead_dict['updated_at'] = now
            
            # Insert into database
            result = self.supabase.client.table('leads').insert(lead_dict).execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create lead")
            
            created_lead = Lead(**result.data[0])
            
            # Log creation activity
            await self.add_activity(
                lead_id=created_lead.id,
                user_id=user_id,
                activity_type='status_change',
                title='Lead created',
                description=f'New lead from {lead_data.source} (Score: {created_lead.score})'
            )
            
            logger.info(f"Lead created: {created_lead.id} with score {created_lead.score}")
            
            return created_lead
            
        except Exception as e:
            logger.error(f"Error creating lead: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error creating lead: {str(e)}")
    
    async def get_lead(
        self,
        lead_id: UUID,
        user_id: UUID
    ) -> Lead:
        """
        Get single lead by ID
        Enforces user ownership via RLS
        """
        try:
            result = self.supabase.client.table('leads')\
                .select('*')\
                .eq('id', str(lead_id))\
                .eq('user_id', str(user_id))\
                .single()\
                .execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Lead not found")
            
            return Lead(**result.data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching lead: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching lead: {str(e)}")
    
    async def list_leads(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        source: Optional[str] = None,
        priority: Optional[str] = None,
        min_score: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List leads with filters and pagination
        Returns: {leads: [...], total: N}
        """
        try:
            # Build query
            query = self.supabase.client.table('leads')\
                .select('*', count='exact')\
                .eq('user_id', str(user_id))\
                .neq('status', 'deleted')  # Exclude deleted
            
            # Apply filters
            if status:
                query = query.eq('status', status)
            if source:
                query = query.eq('source', source)
            if priority:
                query = query.eq('priority', priority)
            if min_score is not None:
                query = query.gte('score', min_score)
            if search:
                query = query.or_(f'name.ilike.%{search}%,email.ilike.%{search}%,phone.ilike.%{search}%')
            
            # Pagination and ordering
            result = query.order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            leads = [Lead(**lead) for lead in result.data]
            total = result.count if hasattr(result, 'count') else len(leads)
            
            return {
                'leads': leads,
                'total': total,
                'offset': offset,
                'limit': limit
            }
            
        except Exception as e:
            logger.error(f"Error listing leads: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error listing leads: {str(e)}")
    
    async def update_lead(
        self,
        lead_id: UUID,
        user_id: UUID,
        update_data: LeadUpdate
    ) -> Lead:
        """
        Update lead with score recalculation
        """
        try:
            # Get current lead
            current = await self.get_lead(lead_id, user_id)
            
            # Prepare update
            update_dict = update_data.dict(exclude_unset=True)
            update_dict['updated_at'] = datetime.utcnow().isoformat()
            
            # Recalculate score if relevant fields changed
            if any(k in update_dict for k in ['email', 'phone', 'source', 'metadata']):
                merged_data = {**current.dict(), **update_dict}
                update_dict['score'] = self.calculate_lead_score(merged_data)
                update_dict['priority'] = self.determine_priority(update_dict['score'])
            
            # Update database
            result = self.supabase.client.table('leads')\
                .update(update_dict)\
                .eq('id', str(lead_id))\
                .eq('user_id', str(user_id))\
                .execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Lead not found or update failed")
            
            updated_lead = Lead(**result.data[0])
            
            # Log activity for status changes
            if 'status' in update_dict:
                await self.add_activity(
                    lead_id=lead_id,
                    user_id=user_id,
                    activity_type='status_change',
                    title=f'Status changed to {update_dict["status"]}',
                    description=f'Lead status updated from {current.status} to {update_dict["status"]}'
                )
            
            logger.info(f"Lead updated: {lead_id}")
            
            return updated_lead
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating lead: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error updating lead: {str(e)}")
    
    async def delete_lead(
        self,
        lead_id: UUID,
        user_id: UUID,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete lead (soft delete by default, hard delete if specified)
        """
        try:
            if hard_delete:
                # Permanent deletion
                result = self.supabase.client.table('leads')\
                    .delete()\
                    .eq('id', str(lead_id))\
                    .eq('user_id', str(user_id))\
                    .execute()
            else:
                # Soft delete (mark as deleted)
                result = self.supabase.client.table('leads')\
                    .update({
                        'status': 'deleted',
                        'updated_at': datetime.utcnow().isoformat()
                    })\
                    .eq('id', str(lead_id))\
                    .eq('user_id', str(user_id))\
                    .execute()
            
            success = len(result.data) > 0
            
            if success:
                logger.info(f"Lead {'hard' if hard_delete else 'soft'} deleted: {lead_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting lead: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting lead: {str(e)}")
    
    async def add_activity(
        self,
        lead_id: UUID,
        user_id: UUID,
        activity_type: str,
        title: str,
        description: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Activity:
        """
        Add activity to lead timeline
        """
        try:
            activity_data = {
                'lead_id': str(lead_id),
                'performed_by': str(user_id),
                'activity_type': activity_type,
                'title': title,
                'description': description,
                'metadata': metadata or {},
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.client.table('lead_activities')\
                .insert(activity_data)\
                .execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create activity")
            
            return Activity(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error adding activity: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error adding activity: {str(e)}")
    
    async def get_timeline(
        self,
        lead_id: UUID,
        limit: int = 100
    ) -> List[Activity]:
        """
        Get lead activity timeline
        """
        try:
            result = self.supabase.client.table('lead_activities')\
                .select('*')\
                .eq('lead_id', str(lead_id))\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return [Activity(**activity) for activity in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching timeline: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching timeline: {str(e)}")
    
    async def bulk_update_status(
        self,
        lead_ids: List[UUID],
        user_id: UUID,
        new_status: str
    ) -> Dict[str, Any]:
        """
        Bulk update lead status
        Returns: {success_count, failed_count, errors}
        """
        success_count = 0
        failed_count = 0
        errors = []
        
        for lead_id in lead_ids:
            try:
                await self.update_lead(
                    lead_id=lead_id,
                    user_id=user_id,
                    update_data=LeadUpdate(status=new_status)
                )
                success_count += 1
            except Exception as e:
                failed_count += 1
                errors.append({
                    'lead_id': str(lead_id),
                    'error': str(e)
                })
        
        logger.info(f"Bulk update: {success_count} succeeded, {failed_count} failed")
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'errors': errors
        }
    
    async def export_to_csv(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        source: Optional[str] = None
    ) -> str:
        """
        Export leads to CSV format
        Returns: CSV string
        """
        try:
            # Get all leads matching criteria
            leads_data = await self.list_leads(
                user_id=user_id,
                status=status,
                source=source,
                limit=10000  # Max export
            )
            
            leads = leads_data['leads']
            
            # Create CSV
            output = io.StringIO()
            fieldnames = [
                'id', 'name', 'email', 'phone', 'source', 'status',
                'score', 'priority', 'estimated_value', 'notes', 'created_at'
            ]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for lead in leads:
                writer.writerow({
                    'id': str(lead.id),
                    'name': lead.name,
                    'email': lead.email or '',
                    'phone': lead.phone or '',
                    'source': lead.source,
                    'status': lead.status,
                    'score': lead.score,
                    'priority': lead.priority,
                    'estimated_value': float(lead.estimated_value),
                    'notes': lead.notes or '',
                    'created_at': lead.created_at.isoformat()
                })
            
            csv_content = output.getvalue()
            
            logger.info(f"Exported {len(leads)} leads to CSV")
            
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting leads: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error exporting leads: {str(e)}")
    
    async def get_statistics(
        self,
        user_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get lead statistics for dashboard
        REAL calculations from database
        """
        try:
            since = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Total leads
            total_result = self.supabase.client.table('leads')\
                .select('*', count='exact')\
                .eq('user_id', str(user_id))\
                .neq('status', 'deleted')\
                .execute()
            
            total_leads = total_result.count if hasattr(total_result, 'count') else 0
            
            # New leads (recent)
            new_result = self.supabase.client.table('leads')\
                .select('*', count='exact')\
                .eq('user_id', str(user_id))\
                .gte('created_at', since)\
                .execute()
            
            new_leads = new_result.count if hasattr(new_result, 'count') else 0
            
            # Converted leads
            converted_result = self.supabase.client.table('leads')\
                .select('*', count='exact')\
                .eq('user_id', str(user_id))\
                .eq('status', 'converted')\
                .execute()
            
            converted_leads = converted_result.count if hasattr(converted_result, 'count') else 0
            
            # Conversion rate
            conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
            
            # Average score
            all_leads = await self.list_leads(user_id=user_id, limit=10000)
            avg_score = sum(lead.score for lead in all_leads['leads']) / len(all_leads['leads']) if all_leads['leads'] else 0
            
            # By source
            by_source = {}
            for lead in all_leads['leads']:
                by_source[lead.source] = by_source.get(lead.source, 0) + 1
            
            # By status
            by_status = {}
            for lead in all_leads['leads']:
                by_status[lead.status] = by_status.get(lead.status, 0) + 1
            
            return {
                'total_leads': total_leads,
                'new_leads_last_30d': new_leads,
                'converted_leads': converted_leads,
                'conversion_rate': round(conversion_rate, 2),
                'average_score': round(avg_score, 2),
                'by_source': by_source,
                'by_status': by_status,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error calculating statistics: {str(e)}")

# Singleton instance
_lead_service = None

def get_lead_service() -> LeadService:
    global _lead_service
    if _lead_service is None:
        _lead_service = LeadService()
    return _lead_service
