# Admin API Documentation

## Authentication

All admin endpoints require authentication via Bearer token.

```http
Authorization: Bearer <token>
```

---

## Video Management API

### POST /api/advanced-video/generate

Create a new video generation job.

**Request Body:**
```json
{
  "script": "string (required)",
  "voice_id": "string (optional)",
  "avatar_image_url": "string (optional)",
  "background_url": "string (optional)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "job_id": "uuid",
  "status": "queued"
}
```

**Errors:**
- `400 Bad Request` - Missing or invalid script
- `401 Unauthorized` - User not authenticated
- `500 Internal Server Error` - Processing failed

**Example:**
```bash
curl -X POST http://localhost:8001/api/advanced-video/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "script": "Welcome to AutoPro Daune!",
    "voice_id": "voice_1"
  }'
```

---

### GET /api/advanced-video/jobs

List all video generation jobs for the current user.

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `limit` (integer, default: 20, max: 100) - Items per page
- `status` (string, optional) - Filter by status: queued, processing, completed, failed

**Response (200 OK):**
```json
{
  "jobs": [
    {
      "id": "uuid",
      "status": "completed",
      "progress": 100,
      "script": "string",
      "voice_id": "string",
      "video_url": "string",
      "created_at": "ISO8601",
      "completed_at": "ISO8601"
    }
  ],
  "total": 45,
  "page": 1,
  "pages": 3
}
```

**Errors:**
- `401 Unauthorized` - User not authenticated
- `500 Internal Server Error` - Database error

**Example:**
```bash
curl http://localhost:8001/api/advanced-video/jobs?page=1&limit=20&status=completed \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### GET /api/advanced-video/jobs/{job_id}

Get details of a specific video generation job.

**Path Parameters:**
- `job_id` (uuid, required) - Job identifier

**Response (200 OK):**
```json
{
  "id": "uuid",
  "status": "completed",
  "progress": 100,
  "script": "Welcome to AutoPro",
  "voice_id": "voice_1",
  "avatar_image_url": "https://...",
  "video_url": "https://...",
  "thumbnail_url": "https://...",
  "duration": 30,
  "created_at": "2024-01-01T10:00:00Z",
  "started_at": "2024-01-01T10:00:30Z",
  "completed_at": "2024-01-01T10:05:00Z",
  "error_message": null,
  "metadata": {}
}
```

**Errors:**
- `401 Unauthorized` - User not authenticated
- `404 Not Found` - Job not found
- `403 Forbidden` - User doesn't own this job

**Example:**
```bash
curl http://localhost:8001/api/advanced-video/jobs/abc-123-def \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### DELETE /api/advanced-video/jobs/{job_id}

Delete a video generation job.

**Path Parameters:**
- `job_id` (uuid, required) - Job identifier

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Job deleted successfully"
}
```

**Errors:**
- `401 Unauthorized` - User not authenticated
- `404 Not Found` - Job not found
- `403 Forbidden` - User doesn't own this job or job is processing

**Example:**
```bash
curl -X DELETE http://localhost:8001/api/advanced-video/jobs/abc-123-def \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### POST /api/advanced-video/regenerate/{job_id}

Regenerate a video using an existing job's configuration.

**Path Parameters:**
- `job_id` (uuid, required) - Original job identifier

**Response (200 OK):**
```json
{
  "success": true,
  "job_id": "uuid",
  "original_job_id": "uuid",
  "status": "queued"
}
```

**Errors:**
- `401 Unauthorized` - User not authenticated
- `404 Not Found` - Original job not found
- `403 Forbidden` - User doesn't own this job

---

## Financial API

### GET /api/financial/dashboard

Get financial overview and metrics.

**Response (200 OK):**
```json
{
  "total_costs": 125.50,
  "total_revenue": 450.00,
  "roi": 2.58,
  "videos_generated": 23,
  "api_calls": 145,
  "period_start": "2024-01-01",
  "period_end": "2024-01-31",
  "cost_breakdown": {
    "heygen": 85.00,
    "elevenlabs": 25.50,
    "tiktok": 15.00
  },
  "revenue_breakdown": {
    "subscriptions": 300.00,
    "one_time_purchases": 150.00
  }
}
```

**FAKE_MODE Response:**
Returns mock data when `FAKE_MODE=true`

**Errors:**
- `401 Unauthorized` - User not authenticated
- `403 Forbidden` - User is not admin
- `500 Internal Server Error` - Database error (returns mock data in FAKE_MODE)

**Example:**
```bash
curl http://localhost:8001/api/financial/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### POST /api/financial/track-cost

Track a cost for a video generation or API call.

**Request Body:**
```json
{
  "job_id": "uuid (optional)",
  "provider": "string (required)",
  "amount": 5.50,
  "currency": "USD",
  "type": "video_generation|api_call|storage"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "cost_id": "uuid"
}
```

**Errors:**
- `400 Bad Request` - Missing required fields
- `401 Unauthorized` - User not authenticated

**Example:**
```bash
curl -X POST http://localhost:8001/api/financial/track-cost \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "job_id": "abc-123",
    "provider": "heygen",
    "amount": 5.50,
    "type": "video_generation"
  }'
```

---

### GET /api/financial/costs

Get list of all tracked costs.

**Query Parameters:**
- `page` (integer, default: 1)
- `limit` (integer, default: 50, max: 200)
- `provider` (string, optional) - Filter by provider
- `start_date` (ISO8601, optional)
- `end_date` (ISO8601, optional)

**Response (200 OK):**
```json
{
  "costs": [
    {
      "id": "uuid",
      "job_id": "uuid",
      "provider": "heygen",
      "amount": 5.50,
      "currency": "USD",
      "type": "video_generation",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 3
}
```

---

### GET /api/financial/credit-balance/{provider}

Get credit balance for a specific provider (e.g., TikTok).

**Path Parameters:**
- `provider` (string, required) - Provider name: tiktok, heygen, elevenlabs

**Response (200 OK):**
```json
{
  "provider": "tiktok",
  "balance": 150.00,
  "currency": "USD",
  "last_updated": "2024-01-01T10:00:00Z"
}
```

**Errors:**
- `404 Not Found` - Provider not found or not configured

---

## Automation API

### GET /api/automation/status

Get current automation status and configuration.

**Response (200 OK):**
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
      "description": "Generate videos daily at 9 AM",
      "status": "active",
      "schedule": "0 9 * * *",
      "last_run": "2024-01-01T09:00:00Z",
      "next_run": "2024-01-02T09:00:00Z"
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8001/api/automation/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### GET /api/automation/logs

Get automation execution logs.

**Query Parameters:**
- `limit` (integer, default: 100, max: 500)
- `automation_id` (uuid, optional) - Filter by automation
- `status` (string, optional) - Filter by status: success, failed, running

**Response (200 OK):**
```json
{
  "logs": [
    {
      "id": "uuid",
      "automation_id": "auto_1",
      "action": "video_generation",
      "status": "success",
      "details": {
        "videos_created": 1,
        "duration": "45s",
        "cost": 5.50
      },
      "created_at": "2024-01-01T09:00:00Z"
    }
  ],
  "total": 250
}
```

---

### POST /api/automation/trigger

Manually trigger an automation.

**Request Body:**
```json
{
  "automation_id": "uuid (required)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "execution_id": "uuid",
  "status": "running",
  "started_at": "2024-01-01T10:00:00Z"
}
```

**Errors:**
- `404 Not Found` - Automation not found
- `409 Conflict` - Automation is already running

---

## Social Media API

### POST /api/social/post

Post a video to social media platform.

**Request Body:**
```json
{
  "platform": "tiktok|instagram|youtube",
  "video_url": "string (required)",
  "content": "string (required)",
  "hashtags": ["string"],
  "schedule_time": "ISO8601 (optional)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "post_id": "platform_specific_id",
  "platform": "tiktok",
  "url": "https://tiktok.com/@user/video/12345",
  "status": "published|scheduled"
}
```

**FAKE_MODE Response:**
Returns mock post data without actually posting

**Errors:**
- `400 Bad Request` - Missing required fields
- `401 Unauthorized` - Platform not connected (OAuth required)
- `500 Internal Server Error` - Platform API error

---

### GET /api/social/accounts

Get list of connected social media accounts.

**Response (200 OK):**
```json
{
  "accounts": [
    {
      "platform": "tiktok",
      "username": "@autopro_demo",
      "display_name": "AutoPro Daune",
      "connected": true,
      "followers": 1234,
      "verified": false,
      "connected_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

---

### GET /api/social/followers

Get follower statistics across platforms.

**Response (200 OK):**
```json
{
  "total_followers": 5432,
  "by_platform": {
    "tiktok": 1234,
    "instagram": 2345,
    "youtube": 1853
  },
  "growth_rate": 0.15,
  "period": "last_30_days"
}
```

---

## AI Insights API

### GET /api/ai/insights

Get AI-generated insights and recommendations.

**Query Parameters:**
- `period` (string, default: "30d") - Analysis period: 7d, 30d, 90d
- `type` (string, optional) - Insight type: performance, content, audience

**Response (200 OK):**
```json
{
  "top_performers": [
    {
      "video_id": "uuid",
      "title": "AI Tutorial",
      "views": 15000,
      "engagement_rate": 0.12,
      "revenue": 50.00
    }
  ],
  "recommendations": [
    "Post between 9-11 AM for better engagement",
    "Use trending sounds in your videos",
    "Add more call-to-actions in captions"
  ],
  "sentiment_score": 0.85,
  "trending_topics": ["AI", "Automation", "TikTok Marketing"],
  "audience_insights": {
    "avg_age": 28,
    "top_locations": ["US", "UK", "CA"],
    "gender_split": {"male": 0.6, "female": 0.4}
  }
}
```

**FAKE_MODE:** Returns mock insights without requiring pgvector

---

## Analytics API

### GET /api/analytics/metrics

Get analytics metrics and KPIs.

**Query Parameters:**
- `period` (string, default: "30d") - 7d, 30d, 90d, 1y
- `metrics` (string[], optional) - Specific metrics to fetch

**Response (200 OK):**
```json
{
  "visitors": 321,
  "signups": 45,
  "conversions": 12,
  "conversion_rate": 0.037,
  "revenue": 450.00,
  "avg_revenue_per_user": 37.50,
  "churn_rate": 0.05,
  "active_users": 230,
  "period": "last_30_days"
}
```

---

### GET /api/analytics/chart-data

Get time-series data for charts.

**Query Parameters:**
- `metric` (string, required) - Metric name: visitors, revenue, signups
- `period` (string, default: "30d")
- `granularity` (string, default: "day") - day, week, month

**Response (200 OK):**
```json
{
  "metric": "visitors",
  "data": [
    {"date": "2024-01-01", "value": 45},
    {"date": "2024-01-02", "value": 52},
    {"date": "2024-01-03", "value": 48}
  ],
  "total": 145,
  "average": 48.33
}
```

---

## User Management API

### GET /api/users

List all users (admin only).

**Query Parameters:**
- `page` (integer, default: 1)
- `limit` (integer, default: 20)
- `role` (string, optional) - Filter by role: admin, user
- `status` (string, optional) - Filter by status: active, inactive

**Response (200 OK):**
```json
{
  "users": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "role": "admin",
      "is_active": true,
      "last_login": "2024-01-01T10:00:00Z",
      "created_at": "2024-01-01T10:00:00Z",
      "permissions": ["video:create", "admin:read"]
    }
  ],
  "total": 45,
  "page": 1,
  "pages": 3
}
```

**Errors:**
- `403 Forbidden` - User is not admin

---

### POST /api/users

Create a new user (admin only).

**Request Body:**
```json
{
  "email": "string (required)",
  "password": "string (required)",
  "role": "admin|user",
  "permissions": ["string"]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "user_id": "uuid",
  "email": "user@example.com"
}
```

---

### PUT /api/users/{user_id}

Update user details (admin only).

**Request Body:**
```json
{
  "role": "admin|user",
  "is_active": true,
  "permissions": ["string"]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "user_id": "uuid"
}
```

---

### DELETE /api/users/{user_id}

Delete a user (admin only).

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

## Settings API

### GET /api/settings

Get application settings.

**Response (200 OK):**
```json
{
  "general": {
    "app_name": "AutoPro Daune",
    "timezone": "Europe/Bucharest",
    "language": "ro"
  },
  "api_keys": {
    "heygen": "configured",
    "elevenlabs": "configured",
    "tiktok": "missing"
  },
  "features": {
    "automation": true,
    "ai_insights": true,
    "social_posting": false
  }
}
```

---

### PUT /api/settings

Update application settings (admin only).

**Request Body:**
```json
{
  "general": {
    "timezone": "Europe/Bucharest"
  },
  "features": {
    "automation": true
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Settings updated successfully"
}
```

---

## Rate Limiting

All endpoints are rate-limited:
- **Standard users:** 100 requests/minute
- **Admin users:** 500 requests/minute

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

**Error Response (429 Too Many Requests):**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

---

## Common Error Responses

### 400 Bad Request
```json
{
  "error": "Validation error",
  "details": {
    "script": ["This field is required"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "error": "Not found",
  "message": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```
