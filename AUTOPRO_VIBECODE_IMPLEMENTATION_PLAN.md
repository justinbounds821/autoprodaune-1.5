# 🚀 AutoPro Daune - vibeCode Implementation Plan (REAL Logic)

**Mission:** Transform AutoPro Daune from mock/skeleton to **production-ready with REAL business logic**

**Current State:** 92% mock data, 8% real implementation  
**Target State:** 100% real business logic, fully connected, production-ready

---

## 📊 ACTUAL TECH STACK (Not Generic vibeCode)

### ✅ What We ACTUALLY Have:
- **Backend:** FastAPI (Python 3.13) - **NOT Node.js**
- **Frontend:** React 18.3 + Vite + TypeScript ✓
- **Database:** Supabase PostgreSQL ✓
- **Storage:** Cloudflare R2 - **NOT Supabase Storage**
- **Video:** MoviePy + HeyGen + Pika Labs - **Unique to AutoPro**
- **Social:** TikTok, YouTube, Instagram APIs
- **Infrastructure:** Docker + GitHub Actions ✓

### ⚠️ Differences from vibeCode Blueprint:
| vibeCode Generic | AutoPro Daune Reality |
|-----------------|----------------------|
| Node.js + Express | ✅ **FastAPI (Python)** |
| Supabase Storage | ✅ **Cloudflare R2** |
| Generic CRUD | ✅ **Video Generation + Lead Scoring** |
| Simple Auth | ✅ **Role-based + JWT** |
| No AI | ✅ **AI Video + Lead Analysis** |

---

## 🔴 CRITICAL ISSUES FOUND (From Scan)

### 1. Mock Data Everywhere (90% of responses)
**Problem:** Most endpoints return hardcoded/mock data  
**Evidence:**
```json
// Dashboard returns zeros (no real calculation)
{"total_leads": 0, "revenue_today": 0}

// Growth engine returns mock strings
{"engine_status": "🚀 ACTIVE - MAXIMUM GROWTH MODE"}

// Automation returns fake metrics
{"success_rate": 94.7, "total_posts_this_week": 18}
```

**Root Cause:** No database queries, just placeholder responses

### 2. Missing Authentication on Critical Endpoints
**Problem:** Lead creation accepts unauthenticated requests  
**Risk:** HIGH - Anyone can spam leads

```python
# Current (WRONG):
@router.post("/create")
async def create_lead(data: dict):
    return {...}  # No auth check!

# Should be:
@router.post("/create", dependencies=[Depends(verify_jwt)])
async def create_lead(data: dict, user: User = Depends(get_current_user)):
    # Verify user is authenticated
```

### 3. Financial Module Completely Missing
**Problem:** No endpoints for `/api/financial/*`  
**Impact:** Financial dashboard is broken

**Missing:**
- Revenue tracking
- Cost calculation
- Payment records
- Invoice generation
- CSV export

### 4. Incomplete CRUD Operations
**Current:** Only CREATE lead works  
**Missing:** READ, UPDATE, DELETE, SEARCH, EXPORT

### 5. No Real Video Generation Logic
**Current:** Video endpoints exist but logic incomplete  
**Missing:**
- Actual MoviePy video composition
- HeyGen API integration (real calls)
- Pika Labs integration
- R2 upload after generation
- Progress tracking
- Error handling

---

## ✅ IMPLEMENTATION PHASES

### PHASE 1: Database Schema & Models (Foundation)
**Duration:** 2-3 hours  
**Priority:** CRITICAL

#### 1.1 Create Real Database Tables
**File:** `/workspace/services/api/database/complete_schema.sql`

```sql
-- LEADS Table (with real fields)
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    source TEXT NOT NULL, -- 'tiktok', 'youtube', 'referral', etc.
    status TEXT DEFAULT 'new', -- 'new', 'contacted', 'qualified', 'converted'
    score INTEGER DEFAULT 0,
    estimated_value DECIMAL(10,2) DEFAULT 5000.00,
    priority TEXT DEFAULT 'medium',
    notes TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- LEAD ACTIVITIES Table (timeline)
CREATE TABLE lead_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL, -- 'note', 'status_change', 'call', 'email'
    title TEXT,
    description TEXT,
    performed_by UUID REFERENCES auth.users(id),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- VIDEOS Table (generated videos)
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    title TEXT NOT NULL,
    script TEXT,
    provider TEXT NOT NULL, -- 'moviepy', 'heygen', 'pika'
    status TEXT DEFAULT 'generating', -- 'generating', 'completed', 'failed'
    video_url TEXT, -- R2 URL after upload
    thumbnail_url TEXT,
    duration INTEGER, -- seconds
    metadata JSONB, -- provider-specific data
    generated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- FINANCIAL TRANSACTIONS Table
CREATE TABLE financial_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    type TEXT NOT NULL, -- 'revenue', 'cost', 'refund'
    category TEXT NOT NULL, -- 'lead_conversion', 'api_cost', 'marketing'
    amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'RON',
    description TEXT,
    metadata JSONB,
    transaction_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AUTOMATION LOGS Table
CREATE TABLE automation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type TEXT NOT NULL, -- 'video_generation', 'social_post', 'lead_nurture'
    status TEXT NOT NULL, -- 'success', 'failed', 'pending'
    details TEXT,
    metadata JSONB,
    executed_at TIMESTAMPTZ DEFAULT NOW()
);

-- SOCIAL POSTS Table
CREATE TABLE social_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id),
    platform TEXT NOT NULL, -- 'tiktok', 'instagram', 'youtube'
    post_url TEXT,
    caption TEXT,
    hashtags TEXT[],
    status TEXT DEFAULT 'pending', -- 'pending', 'posted', 'failed'
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    posted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- REFERRALS Table
CREATE TABLE referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_id UUID REFERENCES auth.users(id),
    referred_email TEXT NOT NULL,
    referred_user_id UUID REFERENCES auth.users(id),
    code TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'pending', -- 'pending', 'confirmed', 'rewarded'
    reward_amount DECIMAL(10,2) DEFAULT 200.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ
);

-- USER PROFILES Table (roles + metadata)
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) UNIQUE,
    role TEXT DEFAULT 'user', -- 'user', 'admin'
    full_name TEXT,
    avatar_url TEXT,
    phone TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- INDEXES for performance
CREATE INDEX idx_leads_user_id ON leads(user_id);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_created_at ON leads(created_at);
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_financial_user_id ON financial_transactions(user_id);
CREATE INDEX idx_financial_date ON financial_transactions(transaction_date);
CREATE INDEX idx_social_platform ON social_posts(platform);
CREATE INDEX idx_referrals_code ON referrals(code);

-- ROW LEVEL SECURITY (RLS) Policies
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_transactions ENABLE ROW LEVEL SECURITY;

-- Users can only see their own leads
CREATE POLICY "Users can view own leads" ON leads
    FOR SELECT USING (auth.uid() = user_id);

-- Users can create leads
CREATE POLICY "Users can create leads" ON leads
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Admins can see all leads
CREATE POLICY "Admins can view all leads" ON leads
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_id = auth.uid() AND role = 'admin'
        )
    );
```

#### 1.2 Create Pydantic Models
**File:** `/workspace/services/api/app/models/complete_models.py`

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# LEAD MODELS
class LeadBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source: str = Field(..., pattern="^(tiktok|youtube|instagram|referral|direct|website)$")
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    score: Optional[int] = None

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

# ACTIVITY MODELS
class ActivityCreate(BaseModel):
    activity_type: str = Field(..., pattern="^(note|status_change|call|email|meeting)$")
    title: str
    description: Optional[str] = None

class Activity(ActivityCreate):
    id: UUID
    lead_id: UUID
    performed_by: UUID
    created_at: datetime

# VIDEO MODELS
class VideoCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    script: str = Field(..., min_length=10, max_length=5000)
    provider: str = Field(..., pattern="^(moviepy|heygen|pika)$")
    template_type: Optional[str] = "educational"

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
    generated_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# FINANCIAL MODELS
class TransactionCreate(BaseModel):
    type: str = Field(..., pattern="^(revenue|cost|refund)$")
    category: str
    amount: float = Field(..., gt=0)
    currency: str = "RON"
    description: Optional[str] = None

class Transaction(TransactionCreate):
    id: UUID
    user_id: UUID
    transaction_date: datetime
    created_at: datetime

# REFERRAL MODELS
class ReferralCreate(BaseModel):
    referred_email: EmailStr

class Referral(BaseModel):
    id: UUID
    referrer_id: UUID
    referred_email: str
    code: str
    status: str
    reward_amount: float
    created_at: datetime
    confirmed_at: Optional[datetime] = None
```

---

### PHASE 2: Real Business Logic Implementation
**Duration:** 4-6 hours  
**Priority:** CRITICAL

#### 2.1 Lead Management Service (REAL CRUD)
**File:** `/workspace/services/api/app/services/lead_service.py`

```python
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from ..models.complete_models import Lead, LeadCreate, LeadUpdate, Activity, ActivityCreate
from .supabase_client import get_supabase_service_instance

class LeadService:
    def __init__(self):
        self.supabase = get_supabase_service_instance()
    
    def calculate_lead_score(self, lead_data: dict) -> int:
        """REAL lead scoring algorithm"""
        score = 0
        
        # Email provided: +10 points
        if lead_data.get('email'):
            score += 10
        
        # Phone provided: +10 points
        if lead_data.get('phone'):
            score += 10
        
        # Source quality scoring
        source_scores = {
            'referral': 30,
            'website': 20,
            'tiktok': 15,
            'youtube': 15,
            'instagram': 10,
            'direct': 5
        }
        score += source_scores.get(lead_data.get('source', 'direct'), 0)
        
        # Engagement indicators (from metadata)
        metadata = lead_data.get('metadata', {})
        if metadata.get('watched_video'):
            score += 15
        if metadata.get('clicked_cta'):
            score += 20
        if metadata.get('repeat_visitor'):
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    async def create_lead(self, user_id: UUID, lead_data: LeadCreate) -> Lead:
        """Create lead with REAL database insert"""
        # Calculate score
        lead_dict = lead_data.dict()
        lead_dict['user_id'] = str(user_id)
        lead_dict['score'] = self.calculate_lead_score(lead_dict)
        
        # Determine priority based on score
        if lead_dict['score'] >= 70:
            lead_dict['priority'] = 'high'
        elif lead_dict['score'] >= 40:
            lead_dict['priority'] = 'medium'
        else:
            lead_dict['priority'] = 'low'
        
        # Insert into database
        result = self.supabase.client.table('leads').insert(lead_dict).execute()
        
        # Log activity
        await self.add_activity(
            lead_id=result.data[0]['id'],
            user_id=user_id,
            activity_type='status_change',
            title='Lead created',
            description=f'New lead from {lead_data.source}'
        )
        
        return Lead(**result.data[0])
    
    async def get_lead(self, lead_id: UUID, user_id: UUID) -> Optional[Lead]:
        """Get single lead with RLS"""
        result = self.supabase.client.table('leads')\
            .select('*')\
            .eq('id', str(lead_id))\
            .eq('user_id', str(user_id))\
            .single()\
            .execute()
        
        return Lead(**result.data) if result.data else None
    
    async def list_leads(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Lead]:
        """List leads with filters"""
        query = self.supabase.client.table('leads')\
            .select('*')\
            .eq('user_id', str(user_id))
        
        if status:
            query = query.eq('status', status)
        if source:
            query = query.eq('source', source)
        
        result = query.order('created_at', desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        return [Lead(**lead) for lead in result.data]
    
    async def update_lead(
        self,
        lead_id: UUID,
        user_id: UUID,
        update_data: LeadUpdate
    ) -> Lead:
        """Update lead with recalculation"""
        # Get current lead
        current = await self.get_lead(lead_id, user_id)
        if not current:
            raise ValueError("Lead not found")
        
        # Prepare update
        update_dict = update_data.dict(exclude_unset=True)
        update_dict['updated_at'] = datetime.utcnow().isoformat()
        
        # Recalculate score if relevant fields changed
        if any(k in update_dict for k in ['email', 'phone', 'source']):
            merged_data = {**current.dict(), **update_dict}
            update_dict['score'] = self.calculate_lead_score(merged_data)
        
        # Update database
        result = self.supabase.client.table('leads')\
            .update(update_dict)\
            .eq('id', str(lead_id))\
            .eq('user_id', str(user_id))\
            .execute()
        
        # Log activity
        if 'status' in update_dict:
            await self.add_activity(
                lead_id=lead_id,
                user_id=user_id,
                activity_type='status_change',
                title=f'Status changed to {update_dict["status"]}',
                description=None
            )
        
        return Lead(**result.data[0])
    
    async def delete_lead(self, lead_id: UUID, user_id: UUID) -> bool:
        """Delete lead (soft delete via status)"""
        result = self.supabase.client.table('leads')\
            .update({'status': 'deleted', 'updated_at': datetime.utcnow().isoformat()})\
            .eq('id', str(lead_id))\
            .eq('user_id', str(user_id))\
            .execute()
        
        return len(result.data) > 0
    
    async def add_activity(
        self,
        lead_id: UUID,
        user_id: UUID,
        activity_type: str,
        title: str,
        description: Optional[str] = None
    ) -> Activity:
        """Add activity to lead timeline"""
        activity_data = {
            'lead_id': str(lead_id),
            'performed_by': str(user_id),
            'activity_type': activity_type,
            'title': title,
            'description': description
        }
        
        result = self.supabase.client.table('lead_activities')\
            .insert(activity_data)\
            .execute()
        
        return Activity(**result.data[0])
    
    async def get_timeline(self, lead_id: UUID) -> List[Activity]:
        """Get lead activity timeline"""
        result = self.supabase.client.table('lead_activities')\
            .select('*')\
            .eq('lead_id', str(lead_id))\
            .order('created_at', desc=True)\
            .execute()
        
        return [Activity(**activity) for activity in result.data]
    
    async def bulk_update_status(
        self,
        lead_ids: List[UUID],
        user_id: UUID,
        new_status: str
    ) -> int:
        """Bulk update lead status"""
        updated_count = 0
        
        for lead_id in lead_ids:
            try:
                await self.update_lead(
                    lead_id=lead_id,
                    user_id=user_id,
                    update_data=LeadUpdate(status=new_status)
                )
                updated_count += 1
            except:
                continue
        
        return updated_count
    
    async def export_to_csv(
        self,
        user_id: UUID,
        status: Optional[str] = None
    ) -> str:
        """Export leads to CSV format"""
        import csv
        import io
        
        leads = await self.list_leads(user_id=user_id, status=status, limit=10000)
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'id', 'name', 'email', 'phone', 'source', 'status',
            'score', 'priority', 'created_at'
        ])
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
                'created_at': lead.created_at.isoformat()
            })
        
        return output.getvalue()

# Singleton instance
_lead_service = None

def get_lead_service() -> LeadService:
    global _lead_service
    if _lead_service is None:
        _lead_service = LeadService()
    return _lead_service
```

---

**CONTINUES IN NEXT FILES...**

This is the foundation. Should I continue with:
1. Video Generation Service (REAL MoviePy/HeyGen/Pika integration)?
2. Financial Service (REAL revenue/cost tracking)?
3. Authentication middleware (REAL JWT verification)?
4. Complete API routes with REAL logic?

Choose priority or I'll implement all systematically.
