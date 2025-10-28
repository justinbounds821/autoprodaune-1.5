"""
Lead scoring business logic service
"""
from typing import Dict, Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/workspace/microservices/autopro-common")
from autopro_common import get_logger

from app.models.lead import Lead

logger = get_logger(__name__)


class LeadScoringService:
    """Lead scoring logic"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def calculate_score(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate lead score based on multiple factors
        
        Args:
            lead_data: Lead data dictionary
            
        Returns:
            Scoring results with score, priority, and factors
        """
        score = 0
        factors = []
        
        # Factor 1: Source Quality (0-30 points)
        source = lead_data.get("source", "direct").lower()
        source_scores = {
            "referral": 30,
            "whatsapp": 25,
            "instagram": 20,
            "tiktok": 20,
            "youtube": 15,
            "facebook": 15,
            "landing_page": 10,
            "direct": 5,
        }
        source_score = source_scores.get(source, 5)
        score += source_score
        factors.append(f"Source ({source}): +{source_score}")
        
        # Factor 2: Contact Completeness (0-25 points)
        has_phone = bool(lead_data.get("phone_number"))
        has_email = bool(lead_data.get("email"))
        if has_phone and has_email:
            score += 25
            factors.append("Contact (phone + email): +25")
        elif has_phone or has_email:
            score += 12
            factors.append("Contact (one method): +12")
        
        # Factor 3: Details Provided (0-20 points)
        details = lead_data.get("details", "")
        if len(details) > 100:
            score += 20
            factors.append("Details (comprehensive): +20")
        elif len(details) > 50:
            score += 10
            factors.append("Details (adequate): +10")
        elif len(details) > 0:
            score += 5
            factors.append("Details (minimal): +5")
        
        # Factor 4: Estimated Value (0-15 points)
        estimated_value = lead_data.get("estimated_value", 0)
        if estimated_value >= 10000:
            score += 15
            factors.append("Value (high): +15")
        elif estimated_value >= 5000:
            score += 10
            factors.append("Value (medium): +10")
        elif estimated_value > 0:
            score += 5
            factors.append("Value (low): +5")
        
        # Factor 5: Name Provided (0-10 points)
        if lead_data.get("name"):
            score += 10
            factors.append("Name provided: +10")
        
        # Determine Priority
        if score >= 70:
            priority = "urgent"
            priority_label = "🔴 URGENT"
        elif score >= 50:
            priority = "high"
            priority_label = "🟠 High"
        elif score >= 30:
            priority = "medium"
            priority_label = "🟡 Medium"
        else:
            priority = "low"
            priority_label = "🟢 Low"
        
        return {
            "score": score,
            "priority": priority,
            "priority_label": priority_label,
            "max_score": 100,
            "factors": factors,
            "recommendation": self._get_recommendation(score),
        }
    
    def _get_recommendation(self, score: int) -> str:
        """Get action recommendation based on score"""
        if score >= 70:
            return "Contact immediately! High-value lead with strong intent."
        elif score >= 50:
            return "Priority contact within 2 hours. Strong potential."
        elif score >= 30:
            return "Follow up within 24 hours. Standard lead process."
        else:
            return "Add to nurture campaign. Monitor engagement."
    
    async def score_lead(self, lead_id: int) -> Optional[Dict[str, Any]]:
        """
        Score a single lead and update priority
        
        Args:
            lead_id: Lead ID
            
        Returns:
            Scoring results or None if lead not found
        """
        # Get lead
        result = await self.session.execute(
            select(Lead).where(Lead.id == lead_id)
        )
        lead = result.scalar_one_or_none()
        
        if not lead:
            return None
        
        # Calculate score
        lead_dict = lead.to_dict()
        scoring_result = self.calculate_score(lead_dict)
        
        # Update lead with new score and priority
        lead.score = scoring_result["score"]
        lead.priority = scoring_result["priority"]
        
        await self.session.commit()
        
        logger.info(f"Lead {lead_id} scored: {scoring_result['score']}/100")
        
        return scoring_result
    
    async def batch_score_leads(
        self,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Batch score multiple leads
        
        Args:
            status: Optional filter by status
            limit: Max leads to score
            
        Returns:
            List of scoring results
        """
        # Build query
        query = select(Lead)
        if status:
            query = query.where(Lead.status == status)
        query = query.limit(limit)
        
        # Get leads
        result = await self.session.execute(query)
        leads = result.scalars().all()
        
        # Score each lead
        scored_leads = []
        for lead in leads:
            try:
                lead_dict = lead.to_dict()
                scoring_result = self.calculate_score(lead_dict)
                
                # Update lead
                lead.score = scoring_result["score"]
                lead.priority = scoring_result["priority"]
                
                scored_leads.append({
                    "lead_id": lead.id,
                    "score": scoring_result["score"],
                    "priority": scoring_result["priority"],
                })
                
            except Exception as e:
                logger.warning(f"Failed to score lead {lead.id}: {e}")
                continue
        
        await self.session.commit()
        
        logger.info(f"Batch scored {len(scored_leads)} leads")
        
        return scored_leads
