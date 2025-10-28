"""
Lead database models using SQLAlchemy
"""
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

import sys
sys.path.insert(0, "/workspace/microservices/autopro-common")
from autopro_common.database import Base


class LeadStatus(str, Enum):
    """Lead status enumeration"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"
    NURTURE = "nurture"


class LeadPriority(str, Enum):
    """Lead priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class LeadSource(str, Enum):
    """Lead source enumeration"""
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    WHATSAPP = "whatsapp"
    YOUTUBE = "youtube"
    REFERRAL = "referral"
    DIRECT = "direct"
    LANDING_PAGE = "landing_page"


class Lead(Base):
    """Lead model"""
    
    __tablename__ = "leads"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Basic info
    name = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    
    # Lead details
    source = Column(String(50), nullable=False, index=True, default="direct")
    lead_type = Column(String(50), default="crash_claim")
    status = Column(String(50), nullable=False, index=True, default="new")
    priority = Column(String(20), index=True, default="medium")
    
    # Metadata
    details = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    estimated_value = Column(Float, default=0.0)
    score = Column(Integer, default=0, index=True)
    
    # Assignment
    assigned_to = Column(String(255), nullable=True, index=True)
    
    # Files and attachments
    files = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_contacted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    activities = relationship("LeadActivity", back_populates="lead", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_lead_status_priority', 'status', 'priority'),
        Index('idx_lead_source_created', 'source', 'created_at'),
        Index('idx_lead_score_desc', score.desc()),
    )
    
    def __repr__(self):
        return f"<Lead {self.id}: {self.name} ({self.status})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "phone_number": self.phone_number,
            "email": self.email,
            "source": self.source,
            "lead_type": self.lead_type,
            "status": self.status,
            "priority": self.priority,
            "details": self.details,
            "notes": self.notes,
            "estimated_value": self.estimated_value,
            "score": self.score,
            "assigned_to": self.assigned_to,
            "files": self.files,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_contacted_at": self.last_contacted_at.isoformat() if self.last_contacted_at else None,
        }


class LeadActivity(Base):
    """Lead activity/timeline model"""
    
    __tablename__ = "lead_activities"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to lead
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Activity details
    activity_type = Column(String(50), nullable=False, index=True)  # note, email, call, sms, meeting, status_change
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    metadata = Column(JSON, default=dict)
    performed_by = Column(String(255), default="system")
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationship
    lead = relationship("Lead", back_populates="activities")
    
    # Index for timeline queries
    __table_args__ = (
        Index('idx_activity_lead_created', 'lead_id', created_at.desc()),
    )
    
    def __repr__(self):
        return f"<LeadActivity {self.id}: {self.activity_type} for Lead {self.lead_id}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "activity_type": self.activity_type,
            "title": self.title,
            "description": self.description,
            "metadata": self.metadata,
            "performed_by": self.performed_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
