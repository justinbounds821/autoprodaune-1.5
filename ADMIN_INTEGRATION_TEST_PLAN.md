# Admin Integration Test Plan (FAKE_MODE)

## Test Environment Setup

### Prerequisites
```bash
# Backend on port 8001
cd backend
FAKE_MODE=true uvicorn main:app --port 8001

# Frontend on port 3006
cd frontend
VITE_API_BASE=http://localhost:8001 npm run dev -- --port 3006
```

### Environment Variables
```env
FAKE_MODE=true
VITE_API_BASE=http://localhost:8001
VITE_FAKE_MODE=true
```

---

## Test Scenarios

### 1. Video Generation Flow

#### 1.1 Create Video Job
**Endpoint:** `POST /api/advanced-video/generate`

**Request:**
```bash
curl -X POST http://localhost:8001/api/advanced-video/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer FAKE_TOKEN" \
  -d '{
    "script": "Test video generation",
    "voice_id": "voice_1",
    "avatar_image_url": "https://example.com/avatar.jpg"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "job_id": "fake_job_abc123",
  "status": "queued"
}
```

**UI Test:**
1. Navigate to Video Management
2. Fill in script field with "Test video"
3. Select voice from dropdown
4. Click "Generate Video"
5. Verify success message appears
6. Verify job appears in jobs list

**Success Criteria:**
- ✅ Returns 200 status code
- ✅ Response contains job_id
- ✅ Job appears in list immediately
- ✅ UI shows success notification

---

#### 1.2 List Video Jobs
**Endpoint:** `GET /api/advanced-video/jobs`

**Request:**
```bash
curl http://localhost:8001/api/advanced-video/jobs \
  -H "Authorization: Bearer FAKE_TOKEN"
```

**Expected Response:**
```json
{
  "jobs": [
    {
      "id": "fake_job_abc123",
      "status": "completed",
      "script": "Test video generation",
      "progress": 100,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

**UI Test:**
1. Navigate to Video Management
2. Verify jobs table loads
3. Check job from previous test appears
4. Verify all columns display correctly

**Success Criteria:**
- ✅ Returns array of jobs
- ✅ Each job has required fields
- ✅ Jobs display in table with correct formatting
- ✅ No errors in console

---

#### 1.3 Get Job Details
**Endpoint:** `GET /api/advanced-video/jobs/{job_id}`

**Request:**
```bash
curl http://localhost:8001/api/advanced-video/jobs/fake_job_abc123 \
  -H "Authorization: Bearer FAKE_TOKEN"
```

**Expected Response:**
```json
{
  "id": "fake_job_abc123",
  "status": "completed",
  "progress": 100,
  "script": "Test video generation",
  "voice_id": "voice_1",
  "video_url": "https://fake-storage.com/video.mp4",
  "created_at": "2024-01-01T10:00:00Z",
  "completed_at": "2024-01-01T10:05:00Z"
}
```

**UI Test:**
1. Click on a job row in the table
2. Verify modal/detail view opens
3. Check all job details are displayed
4. Verify video player loads (if completed)

**Success Criteria:**
- ✅ Returns complete job object
- ✅ Includes progress field (0-100)
- ✅ Shows video_url when completed
- ✅ UI displays all information correctly

---

#### 1.4 Delete Video Job
**Endpoint:** `DELETE /api/advanced-video/jobs/{job_id}`

**Request:**
```bash
curl -X DELETE http://localhost:8001/api/advanced-video/jobs/fake_job_abc123 \
  -H "Authorization: Bearer FAKE_TOKEN"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Job deleted successfully"
}
```

**UI Test:**
1. Click delete button on a job
2. Confirm deletion in modal
3. Verify job disappears from list
4. Verify success notification

**Success Criteria:**
- ✅ Returns 200 status
- ✅ Job removed from database
- ✅ Job disappears from UI immediately
- ✅ Confirmation modal appears before deletion

---

### 2. Financial Dashboard

#### 2.1 Get Financial Dashboard
**Endpoint:** `GET /api/financial/dashboard`

**Request:**
```bash
curl http://localhost:8001/api/financial/dashboard \
  -H "Authorization: Bearer FAKE_TOKEN"
```

**Expected Response (FAKE_MODE):**
```json
{
  "total_costs": 125.50,
  "total_revenue": 450.00,
  "roi": 2.58,
  "videos_generated": 23,
  "api_calls": 145,
  "cost_breakdown": {
    "heygen": 85.00,
    "elevenlabs": 25.50,
    "tiktok": 15.00
  },
  "revenue_breakdown": {
    "subscriptions": 300.00,
    "one_time": 150.00
  }
}
```

**UI Test:**
1. Navigate to Financial Dashboard
2. Verify all metrics load
3. Check charts render correctly
4. Verify cost breakdown pie chart

**Success Criteria:**
- ✅ No 503 error in FAKE_MODE
- ✅ Returns mock financial data
- ✅ All metrics display in UI
- ✅ Charts render without errors

---

#### 2.2 Track Cost
**Endpoint:** `POST /api/financial/track-cost`

**Request:**
```bash
curl -X POST http://localhost:8001/api/financial/track-cost \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer FAKE_TOKEN" \
  -d '{
    "job_id": "fake_job_abc123",
    "provider": "heygen",
    "amount": 5.50,
    "type": "video_generation"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "cost_id": "fake_cost_xyz789"
}
```

**Success Criteria:**
- ✅ Returns success response
- ✅ Cost is tracked (visible in dashboard)
- ✅ No lazy init errors
- ✅ Works without Supabase in FAKE_MODE

---

#### 2.3 Get Credit Balance
**Endpoint:** `GET /api/financial/credit-balance/{provider}`

**Request:**
```bash
curl http://localhost:8001/api/financial/credit-balance/tiktok \
  -H "Authorization: Bearer FAKE_TOKEN"
```

**Expected Response:**
```json
{
  "provider": "tiktok",
  "balance": 150.00,
  "currency": "USD",
  "last_updated": "2024-01-01T10:00:00Z"
}
```

**UI Test:**
1. Navigate to Financial Dashboard
2. Check credit balance section
3. Verify TikTok balance displays

**Success Criteria:**
- ✅ Endpoint exists and returns data
- ✅ Balance displays in UI
- ✅ No 404 errors

---

### 3. Automation & Control

#### 3.1 Get Automation Status
**Endpoint:** `GET /api/automation/status`

**Request:**
```bash
curl http://localhost:8001/api/automation/status \
  -H "Authorization: Bearer FAKE_TOKEN"
```

**Expected Response:**
```json
{
  "enabled": true,
  "active_automations": 3,
  "last_run": "2024-01-01T09:00:00Z",
  "next_run": "2024-01-01T10:00:00Z",
  "tasks": [
    {
      "id": "auto_1",
      "name": "Daily video generation",
      "status": "active",
      "schedule": "0 9 * * *"
    }
  ]
}
```

**UI Test:**
1. Navigate to Automation Control
2. Verify status badge shows correct state
3. Check task list loads
4. Verify schedule displays

**Success Criteria:**
- ✅ Returns complete status object
- ✅ All fields present
- ✅ UI reflects automation state correctly

---

#### 3.2 Get Automation Logs
**Endpoint:** `GET /api/automation/logs`

**Request:**
```bash
curl http://localhost:8001/api/automation/logs?limit=50 \
  -H "Authorization: Bearer FAKE_TOKEN"
```

**Expected Response:**
```json
{
  "logs": [
    {
      "id": "log_1",
      "automation_id": "auto_1",
      "action": "video_generation",
      "status": "success",
      "details": {
        "videos_created": 1,
        "duration": "45s"
      },
      "created_at": "2024-01-01T09:00:00Z"
    }
  ],
  "total": 150
}
```

**UI Test:**
1. Navigate to Automation Control
2. Click "View Logs" button
3. Verify logs table loads
4. Check pagination works

**Success Criteria:**
- ✅ Endpoint exists (not 404)
- ✅ Returns array of logs
- ✅ Logs display in UI table
- ✅ Pagination controls work

---

#### 3.3 Trigger Automation
**Endpoint:** `POST /api/automation/trigger`

**Request:**
```bash
curl -X POST http://localhost:8001/api/automation/trigger \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer FAKE_TOKEN" \
  -d '{
    "automation_id": "auto_1"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "execution_id": "exec_abc123",
  "status": "running"
}
```

**UI Test:**
1. Click "Run Now" button on automation
2. Verify confirmation modal
3. Check success notification
4. Verify status updates

**Success Criteria:**
- ✅ Automation triggers successfully
- ✅ Execution ID returned
- ✅ UI shows running state
- ✅ Log entry created

---

### 4. Social Media Integration

#### 4.1 Post to Social Media
**Endpoint:** `POST /api/social/post`

**Request:**
```bash
curl -X POST http://localhost:8001/api/social/post \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer FAKE_TOKEN" \
  -d '{
    "platform": "tiktok",
    "video_url": "https://storage.com/video.mp4",
    "content": "Check out this amazing video! #AI #AutoPro",
    "schedule_time": null
  }'
```

**Expected Response (FAKE_MODE):**
```json
{
  "success": true,
  "post_id": "fake_post_xyz123",
  "platform": "tiktok",
  "url": "https://tiktok.com/@fake/video_xyz123",
  "status": "published"
}
```

**UI Test:**
1. Navigate to Social Media tab
2. Select a video to post
3. Choose platform (TikTok)
4. Add caption
5. Click "Post Now"
6. Verify success message

**Success Criteria:**
- ✅ Post created successfully in FAKE_MODE
- ✅ No OAuth errors in FAKE_MODE
- ✅ Returns post URL
- ✅ UI shows success notification

---

#### 4.2 Get Social Accounts
**Endpoint:** `GET /api/social/accounts`

**Request:**
```bash
curl http://localhost:8001/api/social/accounts \
  -H "Authorization: Bearer FAKE_TOKEN"
```

**Expected Response:**
```json
{
  "accounts": [
    {
      "platform": "tiktok",
      "username": "@autopro_demo",
      "connected": true,
      "followers": 1234
    },
    {
      "platform": "instagram",
      "username": "@autopro_demo",
      "connected": false,
      "followers": 0
    }
  ]
}
```

**UI Test:**
1. Check connected accounts section
2. Verify connection status badges
3. Test "Connect Account" button

**Success Criteria:**
- ✅ Lists all available platforms
- ✅ Shows connection status correctly
- ✅ Follower counts display

---

### 5. AI Insights

#### 5.1 Get AI Insights
**Endpoint:** `GET /api/ai/insights`

**Request:**
```bash
curl http://localhost:8001/api/ai/insights \
  -H "Authorization: Bearer FAKE_TOKEN"
```

**Expected Response (FAKE_MODE):**
```json
{
  "top_performers": [
    {
      "video_id": "vid_1",
      "title": "AI Tutorial",
      "views": 15000,
      "engagement": 0.12
    }
  ],
  "recommendations": [
    "Post between 9-11 AM for better engagement",
    "Use trending sounds in your videos",
    "Add more call-to-actions in captions"
  ],
  "sentiment_score": 0.85,
  "trending_topics": ["AI", "Automation", "TikTok"]
}
```

**UI Test:**
1. Navigate to AI Insights
2. Verify insights load without pgvector
3. Check recommendations display
4. Verify charts render

**Success Criteria:**
- ✅ Works in FAKE_MODE without pgvector
- ✅ Returns insights data
- ✅ UI displays recommendations
- ✅ No blocking errors

---

### 6. User Management

#### 6.1 List Users (When Implemented)
**Endpoint:** `GET /api/users`

**Request:**
```bash
curl http://localhost:8001/api/users?page=1&limit=20 \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Expected Response:**
```json
{
  "users": [
    {
      "id": "user_1",
      "email": "admin@autopro.com",
      "role": "admin",
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "pages": 1
}
```

**Success Criteria:**
- ✅ Returns paginated user list
- ✅ Admin can see all users
- ✅ Regular users see limited info

---

## Error Scenarios

### 7.1 Invalid Authentication
```bash
curl http://localhost:8001/api/advanced-video/jobs
# No Authorization header
```

**Expected:** 401 Unauthorized

---

### 7.2 Missing Required Fields
```bash
curl -X POST http://localhost:8001/api/advanced-video/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer FAKE_TOKEN" \
  -d '{"voice_id": "voice_1"}'
# Missing script field
```

**Expected:** 400 Bad Request with error message

---

### 7.3 Resource Not Found
```bash
curl http://localhost:8001/api/advanced-video/jobs/invalid_id \
  -H "Authorization: Bearer FAKE_TOKEN"
```

**Expected:** 404 Not Found

---

### 7.4 Server Error Handling
```bash
# Simulate server error by stopping Supabase
curl http://localhost:8001/api/financial/dashboard \
  -H "Authorization: Bearer FAKE_TOKEN"
```

**Expected in FAKE_MODE:** Should return mock data, not 500 error

---

## Performance Tests

### 8.1 Load Test - List Jobs
```bash
# Send 100 concurrent requests
for i in {1..100}; do
  curl http://localhost:8001/api/advanced-video/jobs \
    -H "Authorization: Bearer FAKE_TOKEN" &
done
wait
```

**Success Criteria:**
- ✅ All requests complete successfully
- ✅ Response time < 500ms
- ✅ No timeout errors

---

### 8.2 Pagination Performance
```bash
curl "http://localhost:8001/api/advanced-video/jobs?page=1&limit=100" \
  -H "Authorization: Bearer FAKE_TOKEN"
```

**Success Criteria:**
- ✅ Returns within 1 second
- ✅ Correct number of results
- ✅ Pagination metadata accurate

---

## Test Execution Checklist

### Pre-Test
- [ ] Backend running on port 8001
- [ ] Frontend running on port 3006
- [ ] FAKE_MODE=true set
- [ ] Test user authenticated

### Video Management
- [ ] Create video job
- [ ] List video jobs
- [ ] Get job details
- [ ] Delete video job
- [ ] Check progress updates

### Financial
- [ ] Get dashboard (no 503 error)
- [ ] Track cost
- [ ] Get credit balance
- [ ] View cost breakdown

### Automation
- [ ] Get automation status
- [ ] Get automation logs
- [ ] Trigger automation
- [ ] View task list

### Social Media
- [ ] Post to platform
- [ ] Get accounts
- [ ] Check connection status

### AI Insights
- [ ] Get insights (FAKE_MODE)
- [ ] View recommendations
- [ ] Check trending topics

### Error Handling
- [ ] Test 401 errors
- [ ] Test 400 errors
- [ ] Test 404 errors
- [ ] Test 500 fallbacks

---

## Test Report Template

```markdown
## Test Execution Report

**Date:** YYYY-MM-DD
**Tester:** [Name]
**Environment:** FAKE_MODE

### Summary
- Total Tests: X
- Passed: X
- Failed: X
- Skipped: X

### Failed Tests
1. [Test Name]
   - Expected: [...]
   - Actual: [...]
   - Error: [...]

### Notes
[Any additional observations]
```

---

## Automated Test Script

```bash
#!/bin/bash
# run_integration_tests.sh

API_BASE="http://localhost:8001"
TOKEN="FAKE_TOKEN"

echo "Starting integration tests..."

# Test 1: Video Generation
echo "Test 1: Video Generation"
response=$(curl -s -X POST $API_BASE/api/advanced-video/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"script":"Test"}')

if echo "$response" | grep -q "job_id"; then
  echo "✅ PASS"
else
  echo "❌ FAIL"
fi

# Test 2: List Jobs
echo "Test 2: List Jobs"
response=$(curl -s $API_BASE/api/advanced-video/jobs \
  -H "Authorization: Bearer $TOKEN")

if echo "$response" | grep -q "jobs"; then
  echo "✅ PASS"
else
  echo "❌ FAIL"
fi

# Test 3: Financial Dashboard
echo "Test 3: Financial Dashboard"
response=$(curl -s $API_BASE/api/financial/dashboard \
  -H "Authorization: Bearer $TOKEN")

if echo "$response" | grep -q "total_costs"; then
  echo "✅ PASS"
else
  echo "❌ FAIL"
fi

# Add more tests...

echo "Integration tests complete"
```
