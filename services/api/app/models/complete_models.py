"""
Complete Pydantic Models for AutoPro Daune
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# ============================================
# LEAD MODELS
# ============================================

class LeadBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source: str = Field(..., pattern="^(tiktok|youtube|instagram|facebook|referral|direct|website)$")
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    score: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class Lead(LeadBase):
    id: UUID
    user_id: UUID
    status: str
    score: int
    estimated_value: float
    priority: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============================================
# ACTIVITY MODELS
# ============================================

class ActivityCreate(BaseModel):
    activity_type: str = Field(..., pattern="^(note|status_change|call|email|meeting|sms|whatsapp)$")
    title: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class Activity(BaseModel):
    id: UUID
    lead_id: UUID
    activity_type: str
    title: str
    description: Optional[str] = None
    performed_by: UUID
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================
# VIDEO MODELS
# ============================================

class VideoCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    script: str = Field(..., min_length=10, max_length=5000)
    provider: str = Field(..., pattern="^(moviepy|heygen|pika|manole)$")
    avatar_id: Optional[str] = "professional"
    background_image: Optional[str] = None

class Video(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    script: str
    provider: str
    status: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    file_size: Optional[int] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    provider_job_id: Optional[str] = None
    error_message: Optional[str] = None
    generated_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================
# FINANCIAL MODELS
# ============================================

class TransactionCreate(BaseModel):
    type: str = Field(..., pattern="^(revenue|cost|refund|commission)$")
    category: str
    amount: float = Field(..., gt=0)
    currency: str = "RON"
    description: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class Transaction(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    type: str
    category: str
    amount: float
    currency: str
    description: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    transaction_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================
# SOCIAL POST MODELS
# ============================================

class SocialPostCreate(BaseModel):
    video_id: Optional[UUID] = None
    platform: str = Field(..., pattern="^(tiktok|instagram|facebook|youtube)$")
    caption: str
    hashtags: Optional[List[str]] = []

class SocialPost(BaseModel):
    id: UUID
    video_id: Optional[UUID] = None
    platform: str
    post_url: Optional[str] = None
    caption: str
    hashtags: List[str]
    status: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    engagement_rate: float = 0.0
    posted_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================
# REFERRAL MODELS
# ============================================

class ReferralCreate(BaseModel):
    referred_email: EmailStr

class Referral(BaseModel):
    id: UUID
    referrer_id: UUID
    referred_email: str
    referred_user_id: Optional[UUID] = None
    code: str
    status: str
    reward_amount: float
    currency: str
    created_at: datetime
    registered_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    rewarded_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============================================
# NOTIFICATION MODELS
# ============================================

class NotificationCreate(BaseModel):
    user_id: UUID
    type: str = Field(..., pattern="^(lead|video|financial|social|system)$")
    title: str
    message: str
    action_url: Optional[str] = None

class Notification(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: str
    action_url: Optional[str] = None
    read: bool = False
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
