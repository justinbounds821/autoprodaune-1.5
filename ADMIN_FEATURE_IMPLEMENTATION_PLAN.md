# Admin Dashboard - Feature Implementation Plan

## P0 - CRITICAL (Next 24 hours)

### 1. Financial Dashboard FAKE_MODE Support
**File:** `backend/routes/financial.py`  
**Line:** ~715  
**Task:** Add fallback when FAKE_MODE=true

```python
if FAKE_MODE:
    return {
        "total_costs": 125.50,
        "total_revenue": 450.00,
        "roi": 2.58,
        "videos_generated": 23,
        "api_calls": 145,
        "cost_breakdown": {
            "heygen": 85.00,
            "elevenlabs": 25.50,
            "tiktok": 15.00
        }
    }
```

**Estimate:** 2 hours

---

### 2. Implement DELETE Job Endpoint
**File:** `backend/routes/video_advanced_alias.py`  
**Location:** After line 201  
**Task:** Create DELETE route

```python
@router.delete("/api/advanced-video/jobs/{job_id}")
async def delete_job(job_id: str, user: User = Depends(get_current_user)):
    """Delete a video generation job"""
    job = await job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    
    if job.user_id != user.id and not user.is_admin:
        raise HTTPException(403, "Not authorized")
    
    await job_store.delete_job(job_id)
    return {"success": True}
```

**Estimate:** 30 minutes

---

### 3. Add Progress Tracking to Video Jobs
**Files:** 
- `backend/models/video_job.py`
- `backend/services/video_engine.py`
- Database migration

**Tasks:**
1. Add migration for `progress` column
2. Update VideoJob model
3. Update VideoEngine to report progress
4. Update API response to include progress

**Migration:**
```sql
ALTER TABLE video_jobs 
ADD COLUMN progress INTEGER DEFAULT 0,
ADD COLUMN error_message TEXT,
ADD COLUMN metadata JSONB DEFAULT '{}'::jsonb;
```

**VideoEngine Update:**
```python
async def generate_video(self, job_id: str):
    await self.update_progress(job_id, 10)  # Started
    # ... voice generation
    await self.update_progress(job_id, 30)  # Voice done
    # ... video generation
    await self.update_progress(job_id, 70)  # Video done
    # ... finalization
    await self.update_progress(job_id, 100)  # Complete
```

**Estimate:** 4 hours

---

## P1 - HIGH (This Week)

### 4. Pagination & Filters for Video Jobs
**File:** `backend/routes/video_advanced_alias.py`  
**Endpoint:** GET `/api/advanced-video/jobs`

**Update:**
```python
@router.get("/api/advanced-video/jobs")
async def list_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    offset = (page - 1) * limit
    jobs = await job_store.list_jobs(
        user_id=user.id,
        status=status,
        limit=limit,
        offset=offset
    )
    total = await job_store.count_jobs(user_id=user.id, status=status)
    
    return {
        "jobs": jobs,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }
```

**Frontend Update:** `VideoManagement.tsx`
```typescript
const [page, setPage] = useState(1);
const [totalPages, setTotalPages] = useState(1);

const fetchJobs = async () => {
  const response = await axios.get(`/api/advanced-video/jobs?page=${page}&limit=20`);
  setJobs(response.data.jobs);
  setTotalPages(response.data.pages);
};
```

**Estimate:** 3 hours

---

### 5. Complete Cost Tracking Implementation
**File:** `backend/routes/financial.py`  
**Endpoint:** POST `/api/financial/track-cost`

**Tasks:**
1. Remove lazy init, add proper validation
2. Add Supabase fallback for FAKE_MODE
3. Create `video_costs` table if needed

**Update:**
```python
@router.post("/api/financial/track-cost")
async def track_cost(cost_data: CostData, user: User = Depends(get_current_user)):
    if FAKE_MODE:
        # Store in memory or local DB
        return {"success": True, "cost_id": "fake_cost_" + uuid4().hex[:8]}
    
    # Real Supabase logic
    result = await supabase_client.table("video_costs").insert({
        "job_id": cost_data.job_id,
        "provider": cost_data.provider,
        "cost_amount": cost_data.amount,
        "cost_type": cost_data.type
    }).execute()
    
    return {"success": True, "cost_id": result.data[0]["id"]}
```

**Estimate:** 2 hours

---

### 6. Social Posting with Error Handling
**File:** `backend/routes/social.py`  
**Endpoint:** POST `/api/social/post`

**Tasks:**
1. Implement TikTok upload with OAuth
2. Add fallback for FAKE_MODE
3. Display errors in UI

**Implementation:**
```python
@router.post("/api/social/post")
async def post_to_social(
    post_data: SocialPostData,
    user: User = Depends(get_current_user)
):
    if FAKE_MODE:
        return {
            "success": True,
            "post_id": "fake_post_" + uuid4().hex[:8],
            "platform": post_data.platform,
            "url": f"https://tiktok.com/@fake/{uuid4().hex[:8]}"
        }
    
    # Check OAuth token
    token = await get_oauth_token(user.id, post_data.platform)
    if not token:
        raise HTTPException(401, "Please connect your account first")
    
    # Upload to platform
    result = await upload_to_platform(
        platform=post_data.platform,
        video_url=post_data.video_url,
        caption=post_data.content,
        token=token
    )
    
    # Save to database
    await db.social_posts.insert({
        "user_id": user.id,
        "platform": post_data.platform,
        "post_id": result.post_id,
        "content": post_data.content,
        "video_url": post_data.video_url,
        "status": "published"
    })
    
    return {"success": True, "post_id": result.post_id, "url": result.url}
```

**Estimate:** 4 hours

---

### 7. Automation Logs Implementation
**Files:**
- `backend/routes/automation.py`
- Database migration

**Tasks:**
1. Create `automation_logs` table
2. Add logging to automation service
3. Create GET endpoint for logs
4. Connect to AutomationControl.tsx

**Migration:**
```sql
CREATE TABLE automation_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  automation_id UUID,
  action VARCHAR(100),
  status VARCHAR(50),
  details JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Endpoint:**
```python
@router.get("/api/automation/logs")
async def get_logs(
    limit: int = Query(100, le=500),
    automation_id: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    if FAKE_MODE:
        return [{
            "id": f"log_{i}",
            "action": "video_generation",
            "status": "success",
            "details": {"videos": 1},
            "created_at": datetime.now().isoformat()
        } for i in range(10)]
    
    logs = await db.automation_logs.select(
        automation_id=automation_id,
        limit=limit,
        order_by="created_at DESC"
    )
    return logs
```

**Estimate:** 3 hours

---

## P2 - MEDIUM (Future Sprint)

### 8. User Management Module
**Component:** `frontend/src/components/admin/UserManagement.tsx`  
**Backend:** `backend/routes/users.py`

**Features:**
- User list with pagination
- Create/Edit/Delete users
- Permission management
- Role assignment

**Estimate:** 6 hours

---

### 9. Settings & Notifications
**Components:**
- `frontend/src/components/admin/Settings.tsx`
- `frontend/src/components/admin/Notifications.tsx`

**Backend Routes:**
- GET/PUT `/api/settings`
- GET/POST `/api/notifications`

**Estimate:** 8 hours

---

### 10. Growth/Analytics Implementation
**Tasks:**
1. Create `analytics_events` table
2. Implement `/api/analytics/metrics` endpoint
3. Remove mock data from GrowthDashboard.tsx

**Estimate:** 5 hours

---

## P3 - LOW (Nice-to-have)

### 11. UI/UX Improvements
- Advanced filters
- Better modals
- Loading states
- Error boundaries

**Estimate:** 6 hours

---

### 12. Export/Import Features
- CSV export from dashboard
- Data import utilities

**Estimate:** 4 hours

---

### 13. Custom Media Upload
- Background images
- Avatar uploads
- Media library

**Estimate:** 5 hours

---

## Total Time Estimates

| Priority | Tasks | Hours |
|----------|-------|-------|
| P0 | 3 | 6.5h |
| P1 | 4 | 12h |
| P2 | 3 | 19h |
| P3 | 3 | 15h |
| **TOTAL** | **13** | **52.5h** |

---

## Implementation Order

### Week 1 (P0)
1. Day 1: Financial FAKE_MODE + DELETE endpoint
2. Day 2: Progress tracking implementation

### Week 2 (P1)
1. Day 3-4: Pagination, filters, cost tracking
2. Day 5: Social posting + automation logs

### Week 3 (P2)
1. Day 6-7: User management
2. Day 8-9: Settings & notifications
3. Day 10: Analytics implementation

### Week 4 (P3)
1. Day 11-12: UI/UX improvements
2. Day 13: Export/import features
3. Day 14: Custom media upload
