"""
RabbitMQ consumers for lead service
"""
from typing import Dict, Any
import asyncio

import sys
sys.path.insert(0, "/workspace/microservices/autopro-common")
from autopro_common import get_mq_connection, get_logger, RabbitMQConsumer

logger = get_logger(__name__)


async def handle_lead_scoring(data: Dict[str, Any]) -> None:
    """
    Handle lead scoring message
    
    Args:
        data: Message payload with lead_id
    """
    try:
        lead_id = data.get("lead_id")
        logger.info(f"Processing lead scoring for lead {lead_id}")
        
        # Import here to avoid circular imports
        from autopro_common import get_database
        from app.services.scoring_service import LeadScoringService
        
        db = get_database()
        async with db.session() as session:
            scoring_service = LeadScoringService(session)
            result = await scoring_service.score_lead(lead_id)
            
            if result:
                logger.info(f"Lead {lead_id} scored successfully: {result['score']}/100")
            else:
                logger.warning(f"Lead {lead_id} not found for scoring")
                
    except Exception as e:
        logger.error(f"Error handling lead scoring: {e}")


async def handle_lead_enrichment(data: Dict[str, Any]) -> None:
    """
    Handle lead enrichment message
    
    Args:
        data: Message payload with lead_id
    """
    try:
        lead_id = data.get("lead_id")
        logger.info(f"Processing lead enrichment for lead {lead_id}")
        
        # Placeholder for lead enrichment logic
        # Could integrate with external services to enrich lead data
        # Examples: Company lookup, social media profiles, location data, etc.
        
        logger.info(f"Lead {lead_id} enrichment completed")
        
    except Exception as e:
        logger.error(f"Error handling lead enrichment: {e}")


async def start_lead_consumers() -> None:
    """Start all lead service consumers"""
    try:
        connection = get_mq_connection()
        consumer = RabbitMQConsumer(connection)
        
        # Declare queues
        await connection.declare_queue("lead.scoring")
        await connection.declare_queue("lead.enrichment")
        
        # Start consumers in background tasks
        asyncio.create_task(consumer.consume("lead.scoring", handle_lead_scoring))
        asyncio.create_task(consumer.consume("lead.enrichment", handle_lead_enrichment))
        
        logger.info("✅ Lead consumers started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start lead consumers: {e}")
        raise
