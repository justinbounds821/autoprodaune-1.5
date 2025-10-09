# Admin Dashboard - Development Plan & Status Report
**Project:** AutoPro Daune  
**Date:** 2025-10-09  
**Status:** 40% Complete  

---

## 1. ADMIN_DASHBOARD_STATUS – Executive Summary

### Overview
Total componente admin identificate: **10 principale**

- ✅ **Complete: 4 (40%)** — Video generation, job status tracking, health check, navigație de bază
- ⚠️ **Parțial complete: 4 (40%)** — Video list (fără paginare), Financial dashboard (nu merge în FAKE_MODE), Cost tracking (lazy init), Automation & Social integration (lipsește OAuth)
- ❌ **Lipsă / Stub: 2 (20%)** — User management, Settings/Notifications

### Component Details

#### VideoManagement.tsx
- **Lines:** 456
- **API Integration:** Uses `fetch` and `axios` for 5 endpoints
- **State Management:** `useState`, `useEffect`, tables, modals
- **Missing:** Pagination implementation

#### FinancialDashboard.tsx
- **Lines:** 189
- **API Calls:** `/api/financial/dashboard` and other `autoproApi` methods
- **Issue:** Returns 503 in FAKE_MODE; lacks fallback

#### AutomationControl.tsx
- **Lines:** 244
- **API Calls:** `getAutomationStatus`, `startAutomation`
- **Missing:** Complete log management

#### User Management
- **Status:** ❌ No component or endpoint exists

---

## 2. ADMIN_ENDPOINTS_COMPLETE_LIST – Endpoint Mapping

### Video Management Endpoints

| Endpoint | Backend File | Line | Status | Notes |
|----------|-------------|------|--------|-------|
| `POST /api/advanced-video/generate` | `video_advanced_alias.py` | 67 | ✅ | Creates job, returns job_id; works in FAKE_MODE |
| `GET /api/advanced-video/jobs` | `video_advanced_alias.py` | 203 | ⚠️ | Returns list without pagination |
| `GET /api/advanced-video/jobs/{id}` | `video_advanced_alias.py` | 159 | ✅ | OK in FAKE_MODE; needs progress extension |
| `DELETE /api/advanced-video/jobs/{id}` | — | — | ❌ | Missing; needs implementation |
| `POST /api/advanced-video/regenerate/{id}` | `video_internal_alias.py` | 121 | ✅ | Reuses existing job; no frontend interface |

### Financial Endpoints

| Endpoint | Line | Status | Notes |
|----------|------|--------|-------|
| `GET /api/financial/dashboard` | 715 | ⚠️ | Returns 503 in FAKE_MODE; needs fallback |
| `POST /api/financial/track-cost` | 78 | ⚠️ | Lazy init; uses Supabase |
| `GET /api/financial/costs` | 120 | ✅ | Returns costs; no filtering/pagination |
| `GET /api/financial/credit-balance/{provider}` | 210 | ❌ | Completely missing; frontend calls for TikTok credit |

### Automation & Social Endpoints

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /api/automation/status` | ⚠️ | Partial; doesn't return all fields |
| `POST /api/automation/trigger` | ✅ | Exists but not connected in UI |
| `POST /api/social/post` | ⚠️ | Stub; requires OAuth and real keys |

---

## 3. ADMIN_FRONTEND_COMPONENTS_ANALYSIS

### VideoManagement.tsx

**API Calls:**
- `/api/advanced-video/list-generated`
- `/api/advanced-video/generate`
- `/api/video/{id}/thumbnail`

**Props:** `{ user, permissions, onUpdate }`

**State Management:** `useState`, `useEffect`; uses loading flags

**UI Components:** Table with jobs, script form, modals

**Issues:**
- ❌ Missing pagination
- ❌ Job progress not updated
- ⚠️ Limited FAKE_MODE fallback

### FinancialDashboard.tsx

**Dependencies:** `autoproApi` for costs and revenues

**Issues:**
- ❌ Returns 503 in FAKE_MODE
- ❌ Missing fallback
- ❌ Incomplete charts

### AutomationControl.tsx

**API:** `getAutomationStatus`, `getAutomationLogs`, `startAutomation`

**Missing:**
- ❌ `getAutomationLogs` doesn't exist in backend
- ❌ Logs are non-existent

### SocialMedia.tsx

**API:** `/api/social/followers`, `/api/social/post`

**State:** Uses `useState` for accounts

**Issues:**
- ❌ No complete OAuth verification

### AIInsightsDashboard.tsx

**Problem:** AI endpoints (pgvector) unavailable in FAKE_MODE; component blocks

---

## 4. ADMIN_DATABASE_REQUIREMENTS

### Existing Tables (Need Extension)

```sql
-- video_jobs: exists; missing columns
ALTER TABLE video_jobs 
ADD COLUMN progress INTEGER DEFAULT 0,
ADD COLUMN error_message TEXT,
ADD COLUMN metadata JSONB;

-- video_templates: exists; OK
-- video_insights: exists; complete for AI
```

### Missing Tables (Need Creation)

```sql
-- Financial tracking
CREATE TABLE video_costs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES video_jobs(id),
  provider VARCHAR(50),
  cost_amount DECIMAL(10,4),
  currency VARCHAR(3) DEFAULT 'USD',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE api_costs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  api_name VARCHAR(100),
  endpoint VARCHAR(255),
  cost_amount DECIMAL(10,4),
  requests_count INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE revenues (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source VARCHAR(100),
  amount DECIMAL(10,2),
  currency VARCHAR(3) DEFAULT 'RON',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE financial_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_name VARCHAR(100),
  metric_value DECIMAL(12,2),
  period_start DATE,
  period_end DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE budget_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_type VARCHAR(50),
  threshold_amount DECIMAL(10,2),
  current_amount DECIMAL(10,2),
  triggered_at TIMESTAMP,
  resolved_at TIMESTAMP
);

CREATE TABLE credit_balances (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider VARCHAR(50),
  balance DECIMAL(10,2),
  last_updated TIMESTAMP DEFAULT NOW()
);

-- Automation
CREATE TABLE automation_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_type VARCHAR(100),
  status VARCHAR(50),
  message TEXT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Analytics
CREATE TABLE analytics_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type VARCHAR(100),
  event_data JSONB,
  user_id UUID,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Social Media
CREATE TABLE social_posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  platform VARCHAR(50),
  post_id VARCHAR(255),
  content TEXT,
  video_url TEXT,
  status VARCHAR(50),
  posted_at TIMESTAMP
);

CREATE TABLE oauth_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  platform VARCHAR(50),
  access_token TEXT,
  refresh_token TEXT,
  expires_at TIMESTAMP,
  user_id UUID
);

CREATE TABLE user_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,
  setting_key VARCHAR(100),
  setting_value JSONB,
  updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 5. ADMIN_FEATURE_IMPLEMENTATION_PLAN

### P0 – CRITIC (Next 24h)

#### 1. Financial Dashboard FAKE_MODE Support
**File:** `routes/financial.py` (line 715)

```python
# Add fallback when FAKE_MODE=true
if os.getenv('FAKE_MODE', 'false').lower() == 'true':
    return JSONResponse({
        "success": True,
        "data": {
            "total_costs": 1250.50,
            "total_revenue": 3500.00,
            "roi": 180.0,
            "videos_generated": 42,
            "avg_cost_per_video": 29.77
        }
    })
```

**Estimate:** 2h

#### 2. Endpoint Delete Job
**File:** `video_advanced_alias.py` (after line 201)

```python
@router.delete("/api/advanced-video/jobs/{job_id}")
async def delete_video_job(job_id: str):
    """Delete a video generation job"""
    # Implementation needed
    pass
```

**Estimate:** 0.5h

#### 3. Job Progress Tracking
**Database Migration:**
```sql
ALTER TABLE video_jobs ADD COLUMN progress INTEGER DEFAULT 0;
```

**Update VideoEngine:** Add progress updates at 10%, 50%, 100%

**Expose in API:** `/api/advanced-video/jobs/{id}` returns `progress` field

**Estimate:** 4h

---

### P1 – HIGH (This Week)

#### 4. Pagination & Filters
**Extend:** `GET /api/advanced-video/jobs` with `page`, `limit`, `status` params

**Frontend:** Update `VideoManagement.tsx` to consume pagination

**Estimate:** 3h

#### 5. Cost Tracking Finalization
**Complete:** `POST /api/financial/track-cost` lazy init

**Add:** Supabase verification or fallback

**Estimate:** 2h

#### 6. Social Posting
**Implement:** Upload via TikTok API + fallback

**UI:** Display errors in `SocialMedia.tsx`

**Estimate:** 5h

#### 7. Automation Logs
**Create:** `automation_logs` table

**Endpoint:** `GET /api/automation/logs`

**Connect:** In `AutomationControl.tsx`

**Estimate:** 3h

---

### P2 – MEDIUM (Future Sprint)

#### 8. User Management
**Create:** `UserManagement.tsx` component

**Features:** User list, permissions management

**Routes:** `/api/users` CRUD endpoints

**Estimate:** 6h

#### 9. Settings & Notifications
**Components:** `Settings.tsx`, `Notifications.tsx`

**Endpoints:** `/api/settings`, `/api/notifications`

**Estimate:** 8h

#### 10. Growth/Analytics
**Tables:** `analytics_events`

**Endpoints:** `/api/analytics/metrics`

**Estimate:** 10h

---

### P3 – LOW (Nice-to-have)

- UI/UX improvements: advanced pagination, friendly modals
- Export/Import CSV from dashboard
- Upload custom backgrounds/avatars

---

## 6. ADMIN_MOCK_DATA_REMOVAL_PLAN

### VideoManagement.tsx
```typescript
// REMOVE:
const mockJobs = [
  { id: 1, status: 'completed', ... },
  // ...
];

// REPLACE WITH:
useEffect(() => {
  axios.get('/api/advanced-video/jobs')
    .then(res => setJobs(res.data))
    .catch(err => console.error(err));
}, []);
```

### FinancialDashboard.tsx
```typescript
// REMOVE hardcoded data
// USE: autoproApi.getFinancialDashboard()
```

### AutomationControl.tsx
```typescript
// REMOVE:
const demoLogs = [...];

// USE:
const logs = await getAutomationLogs();
```

### GrowthDashboard.tsx
```typescript
// REMOVE:
const stats = { visitors: 321, signups: 5 };

// USE:
const metrics = await fetch('/api/analytics/metrics');
```

### AIInsightsDashboard.tsx
```typescript
// REMOVE:
const placeholderInsights = [...];

// USE:
const insights = await getAiInsights();
```

---

## 7. ADMIN_INTEGRATION_TEST_PLAN (FAKE_MODE)

### Prerequisites
- Backend running on `localhost:8001`
- Frontend running on `localhost:3006`
- `FAKE_MODE=true` in environment

### Test Scenarios

#### 1. Video Generation
```bash
# Request
curl -X POST http://localhost:8001/api/advanced-video/generate \
  -H "Content-Type: application/json" \
  -d '{"script": "Test video", "voice_id": "voice_1"}'

# Expected Response
{
  "success": true,
  "job_id": "fake_job_abc123",
  "status": "queued"
}

# Verify
curl http://localhost:8001/api/advanced-video/jobs
# Should contain the created job
```

#### 2. List Jobs
```bash
curl http://localhost:8001/api/advanced-video/jobs

# Expected: Array with at least the created job
# Each job should have: id, status, progress
```

#### 3. Delete Job
```bash
curl -X DELETE http://localhost:8001/api/advanced-video/jobs/{job_id}

# Expected
{"success": true}

# Verify: Job should disappear from list
```

#### 4. Financial Dashboard
```bash
curl http://localhost:8001/api/financial/dashboard

# Expected (FAKE_MODE)
{
  "total_costs": 1250.50,
  "total_revenue": 3500.00,
  "roi": 180.0,
  "videos_generated": 42
}
```

#### 5. Social Posting
```bash
curl -X POST http://localhost:8001/api/social/post \
  -H "Content-Type: application/json" \
  -d '{"content": "Test post", "video_url": "https://..."}'

# Expected (FAKE_MODE): Success without calling real API
{
  "success": true,
  "post_id": "fake_post_123"
}
```

#### 6. Automation Status
```bash
curl http://localhost:8001/api/automation/status

# Expected
{
  "enabled": true,
  "tasks": [...],
  "last_run": "2025-10-09T10:00:00Z"
}
```

#### 7. Automation Logs
```bash
curl http://localhost:8001/api/automation/logs?limit=50

# Expected
{
  "logs": [
    {"timestamp": "...", "level": "info", "message": "..."}
  ]
}
```

---

## 8. ADMIN_API_DOCUMENTATION

### Video Management

#### POST /api/advanced-video/generate
**Description:** Creates a video generation job

**Request Body:**
```json
{
  "script": "string (required)",
  "voice_id": "string (optional)",
  "avatar_image_url": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "uuid",
  "status": "queued"
}
```

**Errors:**
- `400 Bad Request` - Missing script
- `401 Unauthorized` - User not authenticated
- `500 Internal Error` - Processing failure

---

#### GET /api/advanced-video/jobs
**Description:** List all video generation jobs

**Query Parameters:**
- `page` (integer, optional) - Page number (default: 1)
- `limit` (integer, optional) - Items per page (default: 20)
- `status` (string, optional) - Filter by status

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "uuid",
      "status": "completed",
      "progress": 100,
      "created_at": "2025-10-09T10:00:00Z",
      "completed_at": "2025-10-09T10:05:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "pages": 3
}
```

---

#### GET /api/advanced-video/jobs/{id}
**Description:** Get details for a specific job

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": 65,
  "script": "Video script content",
  "video_url": "https://...",
  "thumbnail_url": "https://...",
  "error_message": null,
  "created_at": "2025-10-09T10:00:00Z"
}
```

---

#### DELETE /api/advanced-video/jobs/{id}
**Description:** Delete a video generation job

**Response:**
```json
{
  "success": true,
  "message": "Job deleted successfully"
}
```

**Errors:**
- `404 Not Found` - Job doesn't exist
- `403 Forbidden` - No permission to delete

---

### Financial

#### GET /api/financial/dashboard
**Description:** Get financial overview

**Response:**
```json
{
  "total_costs": 1250.50,
  "total_revenue": 3500.00,
  "roi": 180.0,
  "videos_generated": 42,
  "avg_cost_per_video": 29.77,
  "period": {
    "start": "2025-10-01",
    "end": "2025-10-09"
  }
}
```

---

#### POST /api/financial/track-cost
**Description:** Record a cost entry

**Request Body:**
```json
{
  "job_id": "uuid (optional)",
  "provider": "openai|elevenlabs|heygen",
  "amount": 15.50,
  "currency": "USD"
}
```

**Response:**
```json
{
  "success": true,
  "cost_id": "uuid"
}
```

---

#### GET /api/financial/costs
**Description:** List all recorded costs

**Query Parameters:**
- `start_date` (string, optional) - ISO date
- `end_date` (string, optional) - ISO date
- `provider` (string, optional) - Filter by provider

**Response:**
```json
{
  "costs": [
    {
      "id": "uuid",
      "provider": "openai",
      "amount": 15.50,
      "currency": "USD",
      "created_at": "2025-10-09T10:00:00Z"
    }
  ],
  "total": 1250.50
}
```

---

#### GET /api/financial/credit-balance/{provider}
**Description:** Get credit balance for a provider

**Parameters:**
- `provider` - One of: `tiktok`, `youtube`, `openai`

**Response:**
```json
{
  "provider": "tiktok",
  "balance": 500.00,
  "currency": "USD",
  "last_updated": "2025-10-09T09:00:00Z"
}
```

---

### Automation

#### GET /api/automation/status
**Description:** Get current automation status

**Response:**
```json
{
  "enabled": true,
  "tasks": [
    {
      "name": "video_generation",
      "status": "active",
      "last_run": "2025-10-09T10:00:00Z",
      "next_run": "2025-10-09T11:00:00Z"
    }
  ],
  "total_runs_today": 15
}
```

---

#### POST /api/automation/trigger
**Description:** Manually trigger automation task

**Request Body:**
```json
{
  "task_type": "video_generation|social_posting",
  "parameters": {}
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "uuid"
}
```

---

#### GET /api/automation/logs
**Description:** Get automation execution logs

**Query Parameters:**
- `limit` (integer, optional) - Max number of logs (default: 100)
- `task_type` (string, optional) - Filter by task type

**Response:**
```json
{
  "logs": [
    {
      "id": "uuid",
      "timestamp": "2025-10-09T10:00:00Z",
      "task_type": "video_generation",
      "status": "success",
      "message": "Generated 3 videos",
      "metadata": {}
    }
  ]
}
```

---

### Social Media

#### POST /api/social/post
**Description:** Post content to social media

**Request Body:**
```json
{
  "platform": "tiktok|youtube",
  "content": "Post caption",
  "video_url": "https://...",
  "schedule_time": "2025-10-09T15:00:00Z (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "post_id": "platform_post_id",
  "url": "https://tiktok.com/..."
}
```

**Errors:**
- `401 Unauthorized` - OAuth token missing or expired
- `400 Bad Request` - Invalid video URL or content

---

#### GET /api/social/followers
**Description:** Get follower counts

**Response:**
```json
{
  "platforms": {
    "tiktok": {
      "followers": 15420,
      "following": 234,
      "likes": 89234
    },
    "youtube": {
      "subscribers": 8932,
      "views": 234521
    }
  }
}
```

---

## 9. ADMIN_COMPONENT_DEPENDENCIES

### VideoManagement.tsx

**Component Dependencies:**
- `Button` from `@/components/ui/button`
- `Table` from `@/components/ui/table`
- `Modal` from `@/components/ui/modal`
- `LoadingIndicator` from `@/components/ui/loading`

**Service Dependencies:**
- `autoproApi.getAdvancedVideoJobs()`
- `autoproApi.generateAdvancedVideo()`
- `autoproApi.getVideoThumbnail()`
- `autoproApi.deleteVideoJob()` *(missing)*

**Environment Variables:**
- `VITE_API_BASE`
- `VITE_FAKE_MODE`

**External Libraries:**
- `axios`
- `react` (useState, useEffect)

**Used By:**
- `AdminApp.tsx` - Route `/admin/videos`
- `AdminSidebar.tsx` - Navigation link

---

### FinancialDashboard.tsx

**Component Dependencies:**
- `Card` from `@/components/ui/card`
- `Chart` from `@/components/ui/chart`
- `MetricCard` from `@/components/ui/metric-card`

**Service Dependencies:**
- `autoproApi.getFinancialDashboard()`
- `autoproApi.getFinancialCosts()`
- `autoproApi.getCreditBalance()` *(missing)*

**Environment Variables:**
- `VITE_API_BASE`
- `VITE_FAKE_MODE`

**External Libraries:**
- `recharts` (for charts)
- `date-fns` (for date formatting)

**Used By:**
- `AdminApp.tsx` - Route `/admin/financial`
- `AdminSidebar.tsx` - Navigation link

---

### AutomationControl.tsx

**Component Dependencies:**
- `Button` from `@/components/ui/button`
- `Switch` from `@/components/ui/switch`
- `LogViewer` from `@/components/ui/log-viewer`

**Service Dependencies:**
- `autoproApi.getAutomationStatus()`
- `autoproApi.startAutomation()`
- `autoproApi.stopAutomation()`
- `autoproApi.getAutomationLogs()` *(missing)*

**Environment Variables:**
- `VITE_API_BASE`

**External Libraries:**
- `react` (useState, useEffect, useInterval)

**Used By:**
- `AdminApp.tsx` - Route `/admin/automation`
- `AdminSidebar.tsx` - Navigation link

---

### SocialMedia.tsx

**Component Dependencies:**
- `Button` from `@/components/ui/button`
- `Card` from `@/components/ui/card`
- `PlatformIcon` from `@/components/ui/platform-icon`

**Service Dependencies:**
- `autoproApi.getSocialFollowers()`
- `autoproApi.postToSocial()`
- `autoproApi.getOAuthStatus()` *(missing)*

**Environment Variables:**
- `VITE_API_BASE`
- `VITE_TIKTOK_CLIENT_ID`
- `VITE_YOUTUBE_CLIENT_ID`

**External Libraries:**
- `react` (useState, useEffect)

**Used By:**
- `AdminApp.tsx` - Route `/admin/social`
- `AdminSidebar.tsx` - Navigation link

---

### AIInsightsDashboard.tsx

**Component Dependencies:**
- `Card` from `@/components/ui/card`
- `Badge` from `@/components/ui/badge`
- `InsightCard` from `@/components/ui/insight-card`

**Service Dependencies:**
- `autoproApi.getAiInsights()`
- `autoproApi.getPerformancePredictions()`

**Environment Variables:**
- `VITE_API_BASE`
- `VITE_FAKE_MODE`

**Issues:**
- pgvector endpoints unavailable in FAKE_MODE
- Component blocks when AI features disabled

**Used By:**
- `AdminApp.tsx` - Route `/admin/ai-insights`
- `AdminSidebar.tsx` - Navigation link

---

### GrowthDashboard.tsx

**Component Dependencies:**
- `MetricCard` from `@/components/ui/metric-card`
- `Chart` from `@/components/ui/chart`

**Service Dependencies:**
- `autoproApi.getAnalyticsMetrics()` *(missing)*

**Current State:**
- Uses hardcoded mock data
- Needs real API integration

**Used By:**
- `AdminApp.tsx` - Route `/admin/growth`
- `AdminSidebar.tsx` - Navigation link

---

## 10. ADMIN_IMPLEMENTATION_PRIORITY_MATRIX

| Task | Status | Priority | ETA | Dependencies |
|------|--------|----------|-----|--------------|
| Add FAKE_MODE support to financial.py | ❌ Missing | **P0** | 2h | Supabase optional |
| Implement DELETE job route | ❌ Missing | **P0** | 0.5h | job_store adaptor |
| Add progress column to video_jobs | ❌ Missing | **P0** | 4h | DB migration + service update |
| Add pagination to video jobs | ⚠️ Partial | **P1** | 3h | DB migration (offset/limit) |
| Finalize cost tracking | ⚠️ Partial | **P1** | 2h | Supabase setup |
| Implement automation logs endpoint | ❌ Missing | **P1** | 3h | Table automation_logs |
| Complete social posting with OAuth | ⚠️ Partial | **P1** | 5h | OAuth setup |
| Create UserManagement component | ❌ Missing | **P2** | 6h | /api/users route |
| Add Settings & Notifications modules | ❌ Missing | **P2** | 8h | Backend routes |
| Remove mock data from GrowthDashboard | ❌ Missing | **P2** | 2h | /api/analytics/metrics |
| Implement AI insights in FAKE_MODE | ❌ Missing | **P2** | 4h | Mock data service |
| Add export CSV functionality | ❌ Missing | **P3** | 3h | Data serialization |
| Upload custom avatars/backgrounds | ❌ Missing | **P3** | 6h | File upload service |

### Summary by Priority

**P0 (Critical - 24h):** 3 tasks, 6.5h total
- Financial FAKE_MODE fallback
- Delete job endpoint
- Job progress tracking

**P1 (High - This Week):** 4 tasks, 13h total
- Pagination & filters
- Cost tracking finalization
- Automation logs
- Social posting OAuth

**P2 (Medium - Future Sprint):** 5 tasks, 24h total
- User management
- Settings & Notifications
- Growth analytics
- AI insights FAKE_MODE
- Mock data removal

**P3 (Low - Nice-to-have):** 2 tasks, 9h total
- Export CSV
- Custom uploads

**Total Estimated Time:** ~52.5 hours

---

## 11. ADMIN_DASHBOARD_MASTER_PLAN

### Executive Summary

The Admin Dashboard is approximately **40% complete**, with 4 functionalities fully implemented in FAKE_MODE and the remainder either partial or missing.

**Biggest Blockers:**
1. ❌ Financial dashboard lacks FAKE_MODE support
2. ❌ Missing DELETE endpoint for video jobs
3. ❌ No user management module
4. ❌ No settings/notifications routes
5. ⚠️ No pagination in lists

### Implementation Phases

#### Phase 1: P0 - Critical Foundation (24h)
**Goal:** Make existing features work reliably in FAKE_MODE

1. **Financial Dashboard FAKE_MODE** (2h)
   - Add fallback data in `routes/financial.py:715`
   - Return mock metrics when Supabase unavailable

2. **Job Progress Tracking** (4h)
   - Database migration: Add `progress` column
   - Update VideoEngine to set progress at stages
   - Expose in API response

3. **Delete Job Endpoint** (0.5h)
   - Implement `DELETE /api/advanced-video/jobs/{id}`
   - Update frontend to use it

**Deliverable:** Core video + financial features fully functional in FAKE_MODE

---

#### Phase 2: P1 - Essential Features (1 week)
**Goal:** Complete critical missing functionality

4. **Pagination & Filtering** (3h)
   - Extend jobs endpoint with `page`, `limit`, `status`
   - Update VideoManagement.tsx UI
   - Add pagination controls

5. **Cost Tracking** (2h)
   - Complete Supabase integration
   - Add fallback for FAKE_MODE
   - Test tracking flow

6. **Automation Logs** (3h)
   - Create `automation_logs` table
   - Implement `GET /api/automation/logs`
   - Connect to AutomationControl.tsx

7. **Social Posting OAuth** (5h)
   - Complete TikTok OAuth flow
   - Add YouTube OAuth
   - Implement error handling in UI

**Deliverable:** All existing admin components have complete backend support

---

#### Phase 3: P2 - Missing Modules (2 weeks)
**Goal:** Add missing admin functionality

8. **User Management** (6h)
   - Create UserManagement.tsx component
   - Implement `/api/users` CRUD endpoints
   - Add permissions system

9. **Settings & Notifications** (8h)
   - Create Settings.tsx component
   - Create Notifications.tsx component
   - Implement backend routes
   - Add user preferences storage

10. **Growth Analytics** (10h)
    - Create `analytics_events` table
    - Implement `/api/analytics/metrics`
    - Remove mock data from GrowthDashboard
    - Add real-time charts

11. **AI Insights FAKE_MODE** (4h)
    - Add mock data service for AI insights
    - Update AIInsightsDashboard.tsx
    - Handle pgvector unavailability

**Deliverable:** Complete admin dashboard with all planned features

---

#### Phase 4: P3 - Enhancements (Ongoing)
**Goal:** Polish and advanced features

12. **UI/UX Improvements**
    - Advanced filtering
    - Better modals
    - Responsive design fixes

13. **Export/Import**
    - CSV export for all tables
    - Batch import functionality

14. **Custom Assets**
    - Avatar upload system
    - Background upload
    - Asset management

**Deliverable:** Production-ready admin dashboard

---

### Database Migration Script

```sql
-- Phase 1: Add progress tracking
ALTER TABLE video_jobs 
ADD COLUMN progress INTEGER DEFAULT 0,
ADD COLUMN error_message TEXT,
ADD COLUMN metadata JSONB;

-- Phase 2: Financial tracking
CREATE TABLE IF NOT EXISTS video_costs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES video_jobs(id),
  provider VARCHAR(50),
  cost_amount DECIMAL(10,4),
  currency VARCHAR(3) DEFAULT 'USD',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS api_costs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  api_name VARCHAR(100),
  endpoint VARCHAR(255),
  cost_amount DECIMAL(10,4),
  requests_count INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS revenues (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source VARCHAR(100),
  amount DECIMAL(10,2),
  currency VARCHAR(3) DEFAULT 'RON',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS financial_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_name VARCHAR(100),
  metric_value DECIMAL(12,2),
  period_start DATE,
  period_end DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS budget_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_type VARCHAR(50),
  threshold_amount DECIMAL(10,2),
  current_amount DECIMAL(10,2),
  triggered_at TIMESTAMP,
  resolved_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS credit_balances (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider VARCHAR(50),
  balance DECIMAL(10,2),
  last_updated TIMESTAMP DEFAULT NOW()
);

-- Phase 2: Automation
CREATE TABLE IF NOT EXISTS automation_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_type VARCHAR(100),
  status VARCHAR(50),
  message TEXT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Phase 3: Analytics
CREATE TABLE IF NOT EXISTS analytics_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type VARCHAR(100),
  event_data JSONB,
  user_id UUID,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Phase 3: Social Media
CREATE TABLE IF NOT EXISTS social_posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  platform VARCHAR(50),
  post_id VARCHAR(255),
  content TEXT,
  video_url TEXT,
  status VARCHAR(50),
  posted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS oauth_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  platform VARCHAR(50),
  access_token TEXT,
  refresh_token TEXT,
  expires_at TIMESTAMP,
  user_id UUID
);

CREATE TABLE IF NOT EXISTS user_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,
  setting_key VARCHAR(100),
  setting_value JSONB,
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_video_jobs_status ON video_jobs(status);
CREATE INDEX idx_video_costs_job_id ON video_costs(job_id);
CREATE INDEX idx_automation_logs_created ON automation_logs(created_at);
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);
```

---

### Testing Strategy

#### Unit Tests
- Each endpoint with FAKE_MODE enabled
- Component rendering tests
- Service layer tests

#### Integration Tests
- End-to-end user flows
- API contract tests
- Database migration tests

#### Manual Testing Checklist
- [ ] Video generation works in FAKE_MODE
- [ ] Job list displays with pagination
- [ ] Financial dashboard shows mock data
- [ ] Automation can be triggered
- [ ] Social posting handles OAuth errors
- [ ] User management CRUD operations
- [ ] Settings persist correctly
- [ ] Analytics charts render

---

### Success Metrics

#### Phase 1 Success Criteria
- ✅ All P0 tasks complete
- ✅ No 503 errors in FAKE_MODE
- ✅ Job progress updates visible

#### Phase 2 Success Criteria
- ✅ All P1 tasks complete
- ✅ Pagination working on all lists
- ✅ OAuth flow functional

#### Phase 3 Success Criteria
- ✅ All P2 tasks complete
- ✅ User management operational
- ✅ Zero mock data in production components

#### Final Success Criteria
- ✅ 100% feature completion
- ✅ All integration tests passing
- ✅ Production-ready deployment
- ✅ Documentation complete

---

### Resource Requirements

**Development Team:**
- 1 Backend Developer (Python/FastAPI)
- 1 Frontend Developer (React/TypeScript)
- 1 Full-Stack Developer (for integration)

**Infrastructure:**
- Supabase instance (or PostgreSQL)
- FAKE_MODE environment for testing
- CI/CD pipeline

**Timeline:**
- Phase 1: 1 day (6.5h)
- Phase 2: 5-7 days (13h)
- Phase 3: 10-14 days (24h)
- Phase 4: Ongoing

**Total Estimated Effort:** ~52.5 hours over 3-4 weeks

---

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Supabase integration delays | Medium | High | Use FAKE_MODE fallbacks |
| OAuth complexity | High | Medium | Start with TikTok only, expand later |
| Database migration issues | Low | High | Test migrations on staging first |
| UI/UX changes during development | Medium | Low | Finalize designs before Phase 3 |
| API rate limiting | Low | Medium | Implement caching and rate limit handling |

---

### Next Steps

#### Immediate Actions (Today)
1. Review and approve this plan
2. Set up development branch
3. Begin Phase 1: P0 tasks
4. Create database migration script

#### This Week
1. Complete Phase 1
2. Begin Phase 2: P1 tasks
3. Set up integration testing environment
4. Document API endpoints

#### Next Sprint
1. Complete Phase 2
2. Begin Phase 3: Missing modules
3. User acceptance testing
4. Performance optimization

---

## Conclusion

The Admin Dashboard has a solid foundation with 40% completion. By following this phased approach:

- **Phase 1** establishes reliability in FAKE_MODE
- **Phase 2** completes essential features
- **Phase 3** adds missing modules
- **Phase 4** polishes for production

With focused development effort of ~52.5 hours over 3-4 weeks, the admin dashboard can reach 100% completion and production readiness.

**Key Success Factors:**
- Prioritize FAKE_MODE support for all features
- Complete backend before adding complex frontend
- Test integration after each phase
- Maintain backward compatibility

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-09  
**Next Review:** After Phase 1 completion
