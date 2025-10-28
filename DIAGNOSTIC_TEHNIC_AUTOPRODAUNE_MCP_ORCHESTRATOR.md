# 🔧 DIAGNOSTIC TEHNIC AUTOPRODAUNE + MCP + ORCHESTRATOR

**Data Analizei:** 28 Octombrie 2025  
**Status:** Analiză Completă → Refactorizare Necesară  
**Versiune:** 2.0.0 → 3.0.0 (Microservicii)

---

## 📊 EXECUTIVE SUMMARY

### Status Actual
- ✅ **Sistem Funcțional** dar cu probleme majore de scalabilitate
- ⚠️ **Arhitectură Monolitică** - toate serviciile într-un singur proces
- 🐌 **Latență Ridicată** - video generation blochează API-ul principal
- 🔄 **Dependințe Strânse** - modificări în video afectează leads
- 💾 **Database** - Supabase PostgreSQL funcționează bine
- 🎯 **138+ Endpoints** dar organizați prost în 26+ routere

### Recomandări Cheie
1. **Separare pe Microservicii** - 6 servicii independente
2. **Message Queue** - Redis Streams sau RabbitMQ pentru async
3. **API Gateway** - Nginx sau Kong pentru routing
4. **Container Orchestration** - Docker Compose → Kubernetes ready
5. **Monitoring** - Prometheus + Grafana + Sentry functional

---

## 🏗️ ARHITECTURA ACTUALĂ

### 1. Backend Monolit (Port 8001)

```
services/api/app/main.py (Monolit FastAPI)
│
├── routes/ (26+ Routers)
│   ├── leads.py (Lead management)
│   ├── video.py (Video generation - BLOCARE!)
│   ├── social.py (Social media posting)
│   ├── automation.py (Scheduler - BLOCARE!)
│   ├── financial.py (Financial tracking)
│   ├── whatsapp.py (WhatsApp bot)
│   ├── referrals.py (Referral system)
│   ├── conversion.py (Conversion tracking)
│   ├── growth_engine.py (Growth system)
│   ├── ai_insights.py (AI analytics)
│   └── ... (16+ more routers)
│
├── services/ (114+ Service Files)
│   ├── video_generator.py (MoviePy + HeyGen)
│   ├── automation_scheduler.py (Threading + Schedule)
│   ├── audio_tts.py (Edge-TTS + ElevenLabs)
│   ├── social_poster.py (TikTok/Instagram/YouTube)
│   ├── whatsapp_bot.py (WhatsApp Business API)
│   └── ...
│
├── core/
│   ├── database.py (Supabase client)
│   ├── monitoring.py (Prometheus metrics)
│   └── redis_client.py (Optional caching)
│
└── middleware/
    ├── error_handler.py
    └── rate_limit.py
```

### 2. MCP Server (Port 8012)

```
mcp_server/main.py (FastAPI)
│
├── tools/
│   ├── linear_tool.py (Project management)
│   ├── github_tool.py (Code management)
│   ├── supabase_tool.py (Database ops)
│   ├── discord_tool.py (Notifications)
│   ├── railway_tool.py (Deployment)
│   └── vercel_tool.py (Frontend hosting)
│
├── agents/
│   ├── analyzer_agent.py
│   ├── coder_agent.py
│   └── tester_agent.py
│
└── clients/
    └── orchestrator_client.py (HTTP to Orchestrator)
```

### 3. MCP Orchestrator (Port 3030)

```
mcp-orchestrator/src/http-bridge.ts (Express)
│
├── Workflow Orchestration
│   ├── orchestrateWorkflow() - Plan creation
│   ├── createPlan() - Task breakdown
│   └── generateAgentPrompt() - AI agent tasks
│
├── Linear Integration
│   ├── linearCreateTask()
│   ├── linearUpdateTask()
│   └── linearListTasks()
│
├── GitHub Integration
│   ├── githubCreateIssue()
│   └── githubCommit()
│
├── Supabase Integration
│   ├── supabaseQuery()
│   └── supabaseVerifyFix()
│
└── Testing Tools
    ├── browserTest() - Playwright E2E
    └── apiTest() - API validation
```

### 4. Frontend React+Vite (Port 3003/3006)

```
02_FRONTEND_UI_CLEAN/
│
├── src/
│   ├── pages/ (12 Pages)
│   │   ├── Dashboard.tsx (Admin main)
│   │   ├── Landing.tsx (Public landing)
│   │   ├── LeadManagement.tsx
│   │   ├── VideoManagement.tsx
│   │   ├── ManoleVideoCreator.tsx
│   │   ├── SocialMedia.tsx
│   │   ├── FinancialDashboard.tsx
│   │   └── AutomationControl.tsx
│   │
│   ├── services/ (7 API Services)
│   │   ├── autoproApi.ts (138+ API calls)
│   │   ├── LeadService.ts
│   │   ├── VideoService.ts
│   │   ├── SocialMediaService.ts
│   │   ├── FinancialService.ts
│   │   └── AutomationService.ts
│   │
│   └── components/ (60+ Components)
│
├── vite.config.ts (Proxy to :8001)
└── package.json (React 18, Vite 5, Shadcn)
```

---

## ⚠️ PROBLEME IDENTIFICATE

### 1. LATENȚĂ CRITICĂ - Video Generation 🔴

**Problema:**
```python
# services/api/app/services/video_generator.py
class ManoleVideoGenerator:
    def generate(self, job_id: str, payload: dict) -> str:
        # ❌ BLOCKING VIDEO PROCESSING (30-60s)
        audio_path = self._handle_audio_synthesis(payload)  # 10-15s
        frame_img = self._process_image_composition(payload)  # 5-10s
        video_path = self._compose_video(frame_img, audio_path, payload)  # 20-30s
        output_url = self._upload_and_cleanup(video_path, audio_path, job_id)  # 5-10s
        # TOTAL: 40-65 seconds BLOCKING main FastAPI process!
```

**Impact:**
- API `/api/video/generate` timeout după 30s
- Blochează celelalte requesturi pe același worker
- Utilizatori așteaptă 60s pentru response
- CPU 100% usage în timpul video processing

**Soluție:**
```
✅ Microserviciu separat: video-service (port 8002)
✅ Message Queue: Redis Streams pentru job processing
✅ WebSocket: Real-time progress updates
✅ Worker Pool: 3-5 video workers paraleli
```

---

### 2. AUTOMATION SCHEDULER - BLOCKING 🟠

**Problema:**
```python
# services/api/app/services/automation_scheduler.py
class AutomationScheduler:
    def start(self):
        # ❌ Threading în același proces
        self._scheduler_thread = threading.Thread(
            target=self._run_scheduler, 
            daemon=True
        )
        self._scheduler_thread.start()
        
    def _run_scheduler(self):
        while self._is_running:
            schedule.run_pending()  # Blochează pentru video generation
            time.sleep(30)
```

**Impact:**
- Scheduled posts (3x/zi) blochează API-ul 60s
- Memory leak în threading
- Nu scalează pe multiple servere
- Restart la deployment = pierdere jobs

**Soluție:**
```
✅ Microserviciu separat: scheduler-service (port 8003)
✅ Celery + Redis pentru distributed tasks
✅ Cron jobs externe (Kubernetes CronJob)
✅ Persistent job storage în Supabase
```

---

### 3. DEPENDINȚE STRÂNSE - MONOLIT 🟡

**Problema:**
```python
# main.py importuri circulare
from .routes import leads_router, video_router, social_router, automation_router
from .services.video_generator import VideoGenerator  # ❌ Dependency hell
from .services.automation_scheduler import AutomationScheduler
from .services.social_poster import SocialPoster

# Lead route depinde de video generator
@router.post("/leads/{lead_id}/generate-video")
async def generate_video_for_lead(lead_id):
    video_gen = VideoGenerator()  # ❌ Tight coupling
    return video_gen.generate(...)
```

**Impact:**
- Modificare în video → rebuild întreg API
- Testing dificil (mock 114+ service files)
- Deploy risc mare (toate serviciile jos)
- Code conflicts în echipă

**Soluție:**
```
✅ API Gateway + Microservicii
✅ Loose coupling prin HTTP/gRPC
✅ Service discovery (Consul/Eureka)
✅ Independent deploys
```

---

### 4. MCP - ARHITECTURĂ CONFUZĂ 🔵

**Problema:**
```
Current:
┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│  MCP Server │─HTTP─│ Orchestrator│─HTTP─│  External    │
│  (Python)   │      │ (Node.js)   │      │  Services    │
│  Port 8012  │      │ Port 3030   │      │ (Linear,     │
│             │      │             │      │  GitHub)     │
└─────────────┘      └─────────────┘      └──────────────┘
       │
       └──────HTTP────────┐
                          │
                    ┌─────▼──────┐
                    │  AutoPro   │
                    │  Backend   │
                    │  Port 8001 │
                    └────────────┘
```

**Probleme:**
- 2 servere pentru MCP (Python + Node) - duplicate logic
- Orchestrator în Node dar backend în Python
- HTTP overhead pentru fiecare tool call
- Nu integrează cu Video/Automation services

**Soluție:**
```
✅ MCP Server unificat în Python FastAPI
✅ Direct integration cu microservicii
✅ gRPC pentru low-latency communication
✅ Tools ca microservicii independente
```

---

### 5. SCALABILITATE - ZERO 📉

**Problema:**
```yaml
# docker-compose.yml
services:
  api:
    image: autopro-api
    ports:
      - "8001:8000"
    # ❌ Single container
    # ❌ No horizontal scaling
    # ❌ No load balancing
```

**Impact:**
- 1 server = 1 punct de failure
- Traffic spike → crash
- Nu poate scala orizontal
- Deployment = downtime

**Soluție:**
```
✅ Kubernetes deployment cu 3+ replicas
✅ Horizontal Pod Autoscaler (HPA)
✅ Load balancer (Nginx Ingress)
✅ Zero-downtime rolling updates
```

---

## 🎯 ARHITECTURA PROPUSĂ - MICROSERVICII

### Diagrame Logice ASCII

#### 1. Arhitectură Generală

```
┌─────────────────────────────────────────────────────────────────────┐
│                         NGINX API GATEWAY                           │
│                         (Port 80/443)                               │
│  • Rate Limiting  • Authentication  • Request Routing              │
└────────┬──────────────────┬────────────────────┬────────────────────┘
         │                  │                    │
         ▼                  ▼                    ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   CORE API     │  │  VIDEO SERVICE │  │ SOCIAL SERVICE │
│   Port 8001    │  │   Port 8002    │  │   Port 8004    │
│                │  │                │  │                │
│ • Leads CRUD   │  │ • MoviePy Gen  │  │ • TikTok Post  │
│ • Referrals    │  │ • HeyGen API   │  │ • Instagram    │
│ • Financial    │  │ • TTS Synthesis│  │ • YouTube      │
│ • Analytics    │  │ • Upload       │  │ • Facebook     │
│ • Health       │  │ • Progress WS  │  │ • Scheduling   │
└───────┬────────┘  └───────┬────────┘  └───────┬────────┘
        │                   │                    │
        └───────────────────┴────────────────────┘
                            │
                ┌───────────▼──────────┐
                │   MESSAGE QUEUE      │
                │   (Redis Streams)    │
                │                      │
                │ • Video Jobs Queue   │
                │ • Social Posts Queue │
                │ • Email Queue        │
                │ • Webhook Events     │
                └───────────┬──────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ SCHEDULER SVC  │  │  EMAIL SERVICE │  │   MCP SERVICE  │
│   Port 8003    │  │   Port 8005    │  │   Port 8006    │
│                │  │                │  │                │
│ • Celery Beat  │  │ • SendGrid API │  │ • Linear Tools │
│ • Cron Jobs    │  │ • Templates    │  │ • GitHub Tools │
│ • 3x/day Posts │  │ • Transactional│  │ • Supabase Ops │
│ • Metrics      │  │ • Campaigns    │  │ • AI Agents    │
└────────────────┘  └────────────────┘  └────────────────┘
        │                   │                    │
        └───────────────────┴────────────────────┘
                            │
                ┌───────────▼──────────┐
                │   SUPABASE DB        │
                │   (PostgreSQL)       │
                │                      │
                │ • leads (RLS)        │
                │ • videos             │
                │ • social_posts       │
                │ • referrals          │
                │ • financial          │
                └──────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      MONITORING STACK                               │
│  Prometheus (metrics) + Grafana (dashboards) + Sentry (errors)     │
└─────────────────────────────────────────────────────────────────────┘
```

---

#### 2. Video Generation Flow (Async)

```
USER REQUEST
     │
     ▼
┌─────────────┐
│  Frontend   │ POST /api/video/generate
│  React App  │ {"prompt": "accident_footage", "duration": 30}
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│     NGINX API Gateway               │
│  • Auth validation                  │
│  • Rate limit check (5 req/min)    │
│  • Route to video-service           │
└──────┬──────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│    VIDEO SERVICE (8002)              │
│  1. Create job_id = uuid()           │
│  2. Store in DB: status="queued"     │
│  3. Push to Redis: video_jobs_queue  │
│  4. Return {"job_id": "...", ...}    │ ← 200 OK (instant response)
└──────┬───────────────────────────────┘
       │
       ▼ (Async Worker Pool)
┌──────────────────────────────────────┐
│   VIDEO WORKER 1 (background)        │
│  1. Pop job from Redis queue         │
│  2. Update DB: status="processing"   │
│  3. Generate audio (TTS) → 10s       │ → WebSocket: {"progress": 30%}
│  4. Compose video (MoviePy) → 20s    │ → WebSocket: {"progress": 60%}
│  5. Upload to Supabase → 5s          │ → WebSocket: {"progress": 80%}
│  6. Update DB: status="completed"    │ → WebSocket: {"progress": 100%, "url": "..."}
└──────────────────────────────────────┘

┌─────────────┐
│  Frontend   │ ← WebSocket: Real-time progress updates
│  Progress   │   {"job_id": "...", "progress": 60%, "status": "processing"}
│  Bar        │   {"job_id": "...", "progress": 100%, "status": "completed", "url": "..."}
└─────────────┘
```

**Beneficii:**
- ✅ API response instant (200ms)
- ✅ User vede progress live
- ✅ Video workers independenți (3-5 paraleli)
- ✅ Retry logic dacă video fail
- ✅ Queue priority (urgent vs normal)

---

#### 3. Automation Scheduler Flow (Celery)

```
SCHEDULER SERVICE (8003)
     │
     ├── Celery Beat Scheduler
     │   └── Cron: "0 9,15,21 * * *" (3x/day: 09:00, 15:00, 21:00)
     │
     ▼
┌──────────────────────────────────────┐
│  CELERY TASK: generate_daily_post()  │
│  1. Check posts today (query DB)     │
│  2. If posts < 3, continue           │
│  3. Select template (rotation)       │
│  4. Enqueue video job (Redis)        │
│  5. Wait for video_url (callback)    │
│  6. Enqueue social post (Redis)      │
│  7. Log metrics                      │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   MESSAGE QUEUE (Redis Streams)      │
│  • video_jobs (5 pending)            │
│  • social_posts_queue (10 pending)   │
│  • email_queue (2 pending)           │
└──────┬───────────────────────────────┘
       │
       ├─────────────┬─────────────┐
       ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│VIDEO WORKER │ │SOCIAL WORKER│ │EMAIL WORKER │
│  Process 1  │ │  Process 1  │ │  Process 1  │
│  (8002.1)   │ │  (8004.1)   │ │  (8005.1)   │
└─────────────┘ └─────────────┘ └─────────────┘

┌─────────────────────────────────────────┐
│     MONITORING & ALERTING               │
│  • Celery Flower (UI monitoring)       │
│  • Prometheus (task metrics)            │
│  • Discord webhook (errors)             │
└─────────────────────────────────────────┘
```

**Beneficii:**
- ✅ Distributed tasks (scalabil pe N servere)
- ✅ Retry logic automat (3 retries)
- ✅ Task prioritization
- ✅ Monitoring real-time cu Flower
- ✅ Graceful shutdown (no lost jobs)

---

#### 4. Social Media Posting Flow

```
SCHEDULER
     │ Trigger 3x/day
     ▼
┌──────────────────────────────────────┐
│  SOCIAL SERVICE (8004)               │
│  1. Get video_url from video-service │
│  2. Get content template             │
│  3. Generate caption + hashtags      │
│  4. For each platform (TikTok, IG):  │
│     a. Format content                │
│     b. Upload video                  │
│     c. Post                          │
│     d. Store post_id in DB           │
│  5. Update analytics                 │
└──────┬───────────────────────────────┘
       │
       ├────────────┬────────────┬────────────┐
       ▼            ▼            ▼            ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   TikTok    │ │  Instagram  │ │  YouTube    │ │  Facebook   │
│   API       │ │  Graph API  │ │  Data API   │ │  Graph API  │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
       │            │            │            │
       └────────────┴────────────┴────────────┘
                    │
                    ▼
┌──────────────────────────────────────┐
│   ANALYTICS AGGREGATION              │
│  • Views, Likes, Shares, Comments    │
│  • CTR, Conversion Rate              │
│  • Store in performance_metrics      │
└──────────────────────────────────────┘
```

---

### 6 Microservicii Propuse

#### 1. **Core API Service** (Port 8001)

**Responsabilități:**
- ✅ Lead management (CRUD, scoring, timeline)
- ✅ Referral system (create, track, pay)
- ✅ Financial dashboard (revenue, costs, ROI)
- ✅ Analytics & reporting
- ✅ Health checks
- ✅ Authentication & authorization

**Tech Stack:**
- FastAPI 0.110+
- Supabase client
- Pydantic validation
- JWT auth

**Endpoints:** 40-50 endpoints
```
GET    /api/leads
POST   /api/leads
PUT    /api/leads/{id}
DELETE /api/leads/{id}
POST   /api/leads/{id}/score
GET    /api/leads/{id}/timeline
POST   /api/referrals
GET    /api/referrals/stats
GET    /api/financial/dashboard
POST   /api/financial/export
```

---

#### 2. **Video Service** (Port 8002)

**Responsabilități:**
- ✅ Video generation (MoviePy, HeyGen, Pika)
- ✅ Audio synthesis (Edge-TTS, ElevenLabs)
- ✅ Image composition (PIL, OpenCV)
- ✅ Upload to Supabase Storage
- ✅ Progress tracking (WebSocket)
- ✅ Job queue management (Redis)

**Tech Stack:**
- FastAPI
- MoviePy 1.0.3
- OpenCV 4.9+
- Pillow 10.2+
- Redis Streams
- WebSocket (FastAPI WebSocket)

**Worker Architecture:**
```python
# video_service/workers.py
class VideoWorker:
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.redis = Redis.from_url(REDIS_URL)
        
    async def process_jobs(self):
        while True:
            # Pop job from queue (blocking)
            job = await self.redis.xread(
                streams={"video_jobs": "$"}, 
                count=1, 
                block=5000
            )
            
            if job:
                await self.process_video_job(job)
                
    async def process_video_job(self, job):
        job_id = job["job_id"]
        
        # Update progress via WebSocket
        await self.send_progress(job_id, 0, "starting")
        
        # Generate video
        try:
            audio_path = await self.generate_audio(job)
            await self.send_progress(job_id, 30, "audio_complete")
            
            video_path = await self.compose_video(job, audio_path)
            await self.send_progress(job_id, 70, "video_complete")
            
            url = await self.upload_video(video_path)
            await self.send_progress(job_id, 100, "completed", url)
            
        except Exception as e:
            await self.send_progress(job_id, 0, "failed", error=str(e))

# Start 3 workers
workers = [VideoWorker(i) for i in range(3)]
asyncio.gather(*[w.process_jobs() for w in workers])
```

**Endpoints:** 10-15 endpoints
```
POST   /api/video/generate (enqueue job)
GET    /api/video/status/{job_id}
DELETE /api/video/{id}
GET    /api/video/download/{id}
WS     /api/video/progress (WebSocket)
```

---

#### 3. **Scheduler Service** (Port 8003)

**Responsabilități:**
- ✅ Automation scheduling (Celery Beat)
- ✅ Daily posts (3x/day at 09:00, 15:00, 21:00)
- ✅ Weekly optimization
- ✅ Metrics aggregation
- ✅ Job monitoring

**Tech Stack:**
- FastAPI (management API)
- Celery 5.3+ (task queue)
- Celery Beat (scheduler)
- Redis (message broker)
- Flower (monitoring UI)

**Celery Tasks:**
```python
# scheduler_service/tasks.py
from celery import Celery
from celery.schedules import crontab

app = Celery('autopro_scheduler', broker=REDIS_URL)

@app.task
def generate_daily_post():
    """Generate and post social media content."""
    # 1. Check if already posted 3 times today
    if get_posts_today() >= 3:
        return {"status": "quota_reached"}
    
    # 2. Enqueue video generation job
    job_id = enqueue_video_job(
        template=get_next_template(),
        duration=30
    )
    
    # 3. Wait for video (with timeout)
    video_url = wait_for_video(job_id, timeout=120)
    
    # 4. Enqueue social posting job
    post_id = enqueue_social_post(
        video_url=video_url,
        platforms=["tiktok", "instagram", "facebook"]
    )
    
    return {"status": "success", "post_id": post_id}

@app.task
def weekly_optimization():
    """Analyze performance and optimize templates."""
    # Get posts from last 7 days
    posts = get_posts_last_week()
    
    # Analyze by template type
    template_performance = analyze_templates(posts)
    
    # Adjust template rotation
    update_template_rotation(template_performance)

# Schedule tasks
app.conf.beat_schedule = {
    'daily-post-morning': {
        'task': 'tasks.generate_daily_post',
        'schedule': crontab(hour=9, minute=0),  # 09:00
    },
    'daily-post-afternoon': {
        'task': 'tasks.generate_daily_post',
        'schedule': crontab(hour=15, minute=0),  # 15:00
    },
    'daily-post-evening': {
        'task': 'tasks.generate_daily_post',
        'schedule': crontab(hour=21, minute=0),  # 21:00
    },
    'weekly-optimization': {
        'task': 'tasks.weekly_optimization',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Sunday 02:00
    },
}
```

**Endpoints:** 8-10 endpoints
```
POST   /api/scheduler/trigger (manual trigger)
GET    /api/scheduler/status
PUT    /api/scheduler/config
GET    /api/scheduler/jobs
POST   /api/scheduler/jobs/{id}/cancel
GET    /api/scheduler/metrics
```

---

#### 4. **Social Media Service** (Port 8004)

**Responsabilități:**
- ✅ Social media posting (TikTok, Instagram, YouTube, Facebook)
- ✅ Content scheduling
- ✅ Analytics tracking
- ✅ Follower stats
- ✅ Engagement monitoring

**Tech Stack:**
- FastAPI
- TikTok API
- Instagram Graph API
- YouTube Data API v3
- Facebook Graph API
- Redis (job queue)

**Architecture:**
```python
# social_service/poster.py
class SocialPoster:
    def __init__(self):
        self.tiktok = TikTokAPI(access_token=TIKTOK_TOKEN)
        self.instagram = InstagramAPI(access_token=INSTAGRAM_TOKEN)
        self.youtube = YouTubeAPI(api_key=YOUTUBE_KEY)
        self.facebook = FacebookAPI(access_token=FACEBOOK_TOKEN)
        
    async def post_to_all_platforms(
        self, 
        video_url: str, 
        caption: str, 
        hashtags: List[str]
    ) -> Dict[str, Any]:
        """Post to all social media platforms."""
        results = {}
        
        # Post to TikTok
        try:
            tiktok_post = await self.tiktok.upload_video(
                video_url=video_url,
                caption=f"{caption} {' '.join(hashtags)}"
            )
            results["tiktok"] = {"success": True, "post_id": tiktok_post.id}
        except Exception as e:
            results["tiktok"] = {"success": False, "error": str(e)}
        
        # Post to Instagram
        try:
            ig_post = await self.instagram.create_media(
                video_url=video_url,
                caption=f"{caption} {' '.join(hashtags)}"
            )
            results["instagram"] = {"success": True, "post_id": ig_post.id}
        except Exception as e:
            results["instagram"] = {"success": False, "error": str(e)}
        
        # Post to YouTube
        try:
            yt_video = await self.youtube.upload_video(
                video_url=video_url,
                title=caption[:100],
                description=f"{caption}\n\n{' '.join(hashtags)}"
            )
            results["youtube"] = {"success": True, "video_id": yt_video.id}
        except Exception as e:
            results["youtube"] = {"success": False, "error": str(e)}
        
        return results
```

**Endpoints:** 15-20 endpoints
```
POST   /api/social/post (create post)
GET    /api/social/posts (list posts)
GET    /api/social/posts/{id}
DELETE /api/social/posts/{id}
GET    /api/social/followers (all platforms)
GET    /api/social/analytics
POST   /api/social/schedule
```

---

#### 5. **Email Service** (Port 8005)

**Responsabilități:**
- ✅ Transactional emails
- ✅ Email campaigns
- ✅ Templates management
- ✅ Email tracking (open, click rates)
- ✅ Lead nurturing emails

**Tech Stack:**
- FastAPI
- SendGrid API
- Jinja2 (templates)
- Redis (email queue)

**Endpoints:** 8-10 endpoints
```
POST   /api/email/send
POST   /api/email/send-template
GET    /api/email/templates
POST   /api/email/campaign
GET    /api/email/stats
```

---

#### 6. **MCP Service** (Port 8006)

**Responsabilități:**
- ✅ Linear project management
- ✅ GitHub code management
- ✅ Supabase database operations
- ✅ AI agent orchestration
- ✅ Workflow automation

**Tech Stack:**
- FastAPI (unified Python server)
- Linear SDK
- Octokit (GitHub)
- Supabase client
- OpenAI/Anthropic (AI agents)

**Endpoints:** 20-30 endpoints
```
POST   /api/mcp/workflows/orchestrate
POST   /api/mcp/linear/task
GET    /api/mcp/linear/tasks
POST   /api/mcp/github/issue
POST   /api/mcp/github/commit
POST   /api/mcp/supabase/query
POST   /api/mcp/test/browser
POST   /api/mcp/test/api
GET    /api/mcp/system/health
```

---

## 🚀 PLAN COMPLET DE REFACTORIZARE

### Faza 1: Pregătire & Infrastructure (Zi 1-2)

#### Task 1.1: Setup Message Queue (Redis Streams)
```bash
# Install Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Test connection
redis-cli ping
```

#### Task 1.2: Create Microservices Base Structure
```
mkdir -p microservices/{core-api,video-service,scheduler-service,social-service,email-service,mcp-service}
mkdir -p microservices/shared/{models,utils,database}
```

#### Task 1.3: Setup Docker Compose pentru Microservices
```yaml
# docker-compose.microservices.yml
version: '3.8'

services:
  # Redis Message Queue
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  # PostgreSQL (Supabase local)
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: autopro
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Core API Service
  core-api:
    build: ./microservices/core-api
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/autopro
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  # Video Service
  video-service:
    build: ./microservices/video-service
    ports:
      - "8002:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    depends_on:
      - redis
    restart: unless-stopped
    deploy:
      replicas: 3  # 3 video workers

  # Scheduler Service
  scheduler-service:
    build: ./microservices/scheduler-service
    ports:
      - "8003:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/autopro
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  # Social Media Service
  social-service:
    build: ./microservices/social-service
    ports:
      - "8004:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - TIKTOK_TOKEN=${TIKTOK_ACCESS_TOKEN}
      - INSTAGRAM_TOKEN=${INSTAGRAM_ACCESS_TOKEN}
      - YOUTUBE_KEY=${YOUTUBE_API_KEY}
    depends_on:
      - redis
    restart: unless-stopped

  # Email Service
  email-service:
    build: ./microservices/email-service
    ports:
      - "8005:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - SENDGRID_API_KEY=${SENDGRID_API_KEY}
    depends_on:
      - redis
    restart: unless-stopped

  # MCP Service
  mcp-service:
    build: ./microservices/mcp-service
    ports:
      - "8006:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - LINEAR_API_KEY=${LINEAR_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    depends_on:
      - redis
    restart: unless-stopped

  # Nginx API Gateway
  api-gateway:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - core-api
      - video-service
      - scheduler-service
      - social-service
      - email-service
      - mcp-service
    restart: unless-stopped

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

  # Grafana Dashboards
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus
    restart: unless-stopped

  # Celery Flower (Scheduler Monitoring)
  flower:
    image: mher/flower
    ports:
      - "5555:5555"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
  prometheus_data:
  grafana_data:
```

---

### Faza 2: Migrare Core API (Zi 3-4)

#### Task 2.1: Extract Core API Service
```bash
# Create core-api service
mkdir -p microservices/core-api/{app,tests}
cd microservices/core-api

# Copy relevant files
cp -r ../../services/api/app/routes/{leads,referrals,financial}.py app/routes/
cp -r ../../services/api/app/services/{supabase_client,financial,cost_calculator}.py app/services/
cp -r ../../services/api/app/core app/
```

**core-api/app/main.py:**
```python
"""
Core API Service - Leads, Referrals, Financial
Port: 8001
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

app = FastAPI(
    title="AutoPro Core API",
    version="3.0.0",
    description="Core business logic: Leads, Referrals, Financial"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from .routes import leads_router, referrals_router, financial_router
app.include_router(leads_router)
app.include_router(referrals_router)
app.include_router(financial_router)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/health")
def health():
    return {
        "service": "core-api",
        "status": "healthy",
        "version": "3.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### Faza 3: Migrare Video Service (Zi 5-7)

#### Task 3.1: Create Video Service cu Workers
```bash
mkdir -p microservices/video-service/{app,workers,tests}
cd microservices/video-service
```

**video-service/app/main.py:**
```python
"""
Video Service - Async Video Generation
Port: 8002
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from redis import Redis
import asyncio
import uuid
import json

app = FastAPI(title="AutoPro Video Service", version="3.0.0")

redis = Redis.from_url("redis://redis:6379", decode_responses=True)

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[job_id] = websocket
    
    async def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]
    
    async def send_progress(self, job_id: str, progress: int, status: str, **kwargs):
        if job_id in self.active_connections:
            message = {
                "job_id": job_id,
                "progress": progress,
                "status": status,
                **kwargs
            }
            await self.active_connections[job_id].send_json(message)

manager = ConnectionManager()

@app.post("/api/video/generate")
async def generate_video(
    prompt: str,
    duration: int = 30,
    resolution: str = "1080p",
    background_tasks: BackgroundTasks
):
    """
    Enqueue video generation job.
    Returns immediately with job_id.
    """
    # Create job
    job_id = str(uuid.uuid4())
    job_data = {
        "job_id": job_id,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "status": "queued",
        "created_at": datetime.now().isoformat()
    }
    
    # Store in Supabase
    supabase.table("video_jobs").insert(job_data).execute()
    
    # Push to Redis queue
    redis.xadd("video_jobs_queue", {
        "job_id": job_id,
        "payload": json.dumps(job_data)
    })
    
    return {
        "success": True,
        "job_id": job_id,
        "status": "queued",
        "message": "Video generation queued. Connect to WebSocket for progress."
    }

@app.get("/api/video/status/{job_id}")
async def get_video_status(job_id: str):
    """Get current status of video job."""
    result = supabase.table("video_jobs").select("*").eq("id", job_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return result.data[0]

@app.websocket("/api/video/progress")
async def video_progress_websocket(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time progress updates.
    Usage: ws://localhost:8002/api/video/progress?job_id=xxx
    """
    await manager.connect(job_id, websocket)
    
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await manager.disconnect(job_id)

@app.get("/health")
def health():
    return {"service": "video-service", "status": "healthy"}
```

**video-service/workers/video_worker.py:**
```python
"""
Video Worker - Process video generation jobs from Redis queue
"""
import asyncio
import json
from redis import Redis
from moviepy.editor import *
from PIL import Image
import numpy as np
import httpx

redis = Redis.from_url("redis://redis:6379", decode_responses=True)

class VideoWorker:
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.running = True
        
    async def start(self):
        """Start processing jobs from Redis queue."""
        print(f"[Worker {self.worker_id}] Started")
        
        while self.running:
            try:
                # Pop job from queue (blocking for 5s)
                job = redis.xreadgroup(
                    groupname="video_workers",
                    consumername=f"worker_{self.worker_id}",
                    streams={"video_jobs_queue": ">"},
                    count=1,
                    block=5000
                )
                
                if job:
                    stream, messages = job[0]
                    message_id, data = messages[0]
                    
                    # Process job
                    await self.process_job(json.loads(data[b"payload"]))
                    
                    # Acknowledge message
                    redis.xack("video_jobs_queue", "video_workers", message_id)
                    
            except Exception as e:
                print(f"[Worker {self.worker_id}] Error: {e}")
                await asyncio.sleep(5)
    
    async def process_job(self, job_data: dict):
        """Process a video generation job."""
        job_id = job_data["job_id"]
        
        print(f"[Worker {self.worker_id}] Processing job {job_id}")
        
        try:
            # Update status: processing
            await self.update_status(job_id, "processing", 0)
            
            # Step 1: Generate audio (30%)
            audio_path = await self.generate_audio(job_data)
            await self.update_status(job_id, "processing", 30, "Audio generated")
            
            # Step 2: Compose video (60%)
            video_path = await self.compose_video(job_data, audio_path)
            await self.update_status(job_id, "processing", 60, "Video composed")
            
            # Step 3: Upload to Supabase (80%)
            video_url = await self.upload_video(video_path, job_id)
            await self.update_status(job_id, "processing", 80, "Video uploaded")
            
            # Step 4: Cleanup (100%)
            await self.cleanup(audio_path, video_path)
            await self.update_status(job_id, "completed", 100, "Completed", video_url=video_url)
            
            print(f"[Worker {self.worker_id}] Job {job_id} completed")
            
        except Exception as e:
            print(f"[Worker {self.worker_id}] Job {job_id} failed: {e}")
            await self.update_status(job_id, "failed", 0, str(e))
    
    async def update_status(self, job_id: str, status: str, progress: int, message: str = "", **kwargs):
        """Update job status in database and WebSocket."""
        # Update database
        update_data = {
            "status": status,
            "progress": progress,
            "message": message,
            **kwargs
        }
        supabase.table("video_jobs").update(update_data).eq("id", job_id).execute()
        
        # Send WebSocket update
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"http://video-service:8000/internal/websocket-update",
                    json={"job_id": job_id, **update_data}
                )
        except Exception as e:
            print(f"WebSocket update failed: {e}")
    
    async def generate_audio(self, job_data: dict) -> str:
        """Generate audio using TTS."""
        # Import TTS service
        from ..services.audio_tts import TTSService
        
        tts = TTSService()
        audio_path = tts.synthesize(
            text=job_data["prompt"],
            voice_mode="romanian_tts"
        )
        
        return audio_path
    
    async def compose_video(self, job_data: dict, audio_path: str) -> str:
        """Compose video using MoviePy."""
        duration = job_data["duration"]
        resolution = job_data.get("resolution", "1080p")
        
        # Create video clip
        # ... (MoviePy logic)
        
        video_path = f"/tmp/{job_data['job_id']}.mp4"
        return video_path
    
    async def upload_video(self, video_path: str, job_id: str) -> str:
        """Upload video to Supabase Storage."""
        with open(video_path, "rb") as f:
            file_content = f.read()
        
        # Upload to Supabase
        result = supabase.storage.from_("videos").upload(
            f"{job_id}.mp4",
            file_content,
            file_options={"content-type": "video/mp4"}
        )
        
        # Get public URL
        url = supabase.storage.from_("videos").get_public_url(f"{job_id}.mp4")
        return url
    
    async def cleanup(self, audio_path: str, video_path: str):
        """Cleanup temporary files."""
        import os
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(video_path):
                os.remove(video_path)
        except Exception as e:
            print(f"Cleanup error: {e}")

# Start worker
if __name__ == "__main__":
    import sys
    worker_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    worker = VideoWorker(worker_id)
    asyncio.run(worker.start())
```

**Dockerfile pentru Video Service:**
```dockerfile
# video-service/Dockerfile
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Expose port
EXPOSE 8000

# Start both API and workers
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & python -m workers.video_worker 1 & python -m workers.video_worker 2 & python -m workers.video_worker 3 & wait"]
```

---

### Faza 4: Migrare Scheduler Service (Zi 8-9)

#### Task 4.1: Create Scheduler Service cu Celery
```bash
mkdir -p microservices/scheduler-service/{app,tasks,tests}
cd microservices/scheduler-service
```

**scheduler-service/tasks/celery_app.py:**
```python
"""
Celery configuration for AutoPro Scheduler
"""
from celery import Celery
from celery.schedules import crontab
import os

# Initialize Celery
app = Celery(
    'autopro_scheduler',
    broker=os.getenv('REDIS_URL', 'redis://redis:6379'),
    backend=os.getenv('REDIS_URL', 'redis://redis:6379')
)

# Configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Bucharest',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Celery Beat Schedule
app.conf.beat_schedule = {
    'daily-post-morning': {
        'task': 'tasks.automation.generate_daily_post',
        'schedule': crontab(hour=9, minute=0),  # 09:00 EET
        'args': ('morning',)
    },
    'daily-post-afternoon': {
        'task': 'tasks.automation.generate_daily_post',
        'schedule': crontab(hour=15, minute=0),  # 15:00 EET
        'args': ('afternoon',)
    },
    'daily-post-evening': {
        'task': 'tasks.automation.generate_daily_post',
        'schedule': crontab(hour=21, minute=0),  # 21:00 EET
        'args': ('evening',)
    },
    'update-daily-metrics': {
        'task': 'tasks.metrics.update_daily_metrics',
        'schedule': crontab(hour=23, minute=55),  # 23:55 EET
    },
    'weekly-optimization': {
        'task': 'tasks.optimization.weekly_optimization',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Sunday 02:00
    },
    'check-pending-videos': {
        'task': 'tasks.maintenance.check_pending_videos',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}
```

**scheduler-service/tasks/automation.py:**
```python
"""
Automation tasks for daily posting
"""
from .celery_app import app
import httpx
import asyncio
from datetime import datetime

@app.task(bind=True, max_retries=3)
def generate_daily_post(self, time_slot: str):
    """
    Generate and post daily content to social media.
    
    Args:
        time_slot: 'morning', 'afternoon', or 'evening'
    """
    try:
        print(f"[Automation] Starting daily post for {time_slot} slot")
        
        # 1. Check if already posted 3 times today
        posts_today = get_posts_count_today()
        if posts_today >= 3:
            print(f"[Automation] Daily quota reached ({posts_today}/3)")
            return {"status": "quota_reached", "posts_today": posts_today}
        
        # 2. Determine content template
        template_type = get_next_template_type(posts_today)
        
        # 3. Enqueue video generation job
        video_job = enqueue_video_job(
            template=template_type,
            duration=30,
            resolution="1080p"
        )
        job_id = video_job["job_id"]
        
        print(f"[Automation] Video job enqueued: {job_id}")
        
        # 4. Wait for video completion (async with timeout)
        video_url = wait_for_video_completion(job_id, timeout=120)
        
        if not video_url:
            raise Exception("Video generation timeout or failed")
        
        print(f"[Automation] Video completed: {video_url}")
        
        # 5. Enqueue social posting job
        post_job = enqueue_social_post(
            video_url=video_url,
            template_type=template_type,
            platforms=["tiktok", "instagram", "facebook"],
            time_slot=time_slot
        )
        
        print(f"[Automation] Social post enqueued: {post_job['post_id']}")
        
        # 6. Log automation event
        log_automation_event("post_success", {
            "time_slot": time_slot,
            "template_type": template_type,
            "posts_today": posts_today + 1,
            "job_id": job_id,
            "post_id": post_job["post_id"]
        })
        
        return {
            "status": "success",
            "job_id": job_id,
            "post_id": post_job["post_id"],
            "template_type": template_type,
            "posts_today": posts_today + 1
        }
        
    except Exception as e:
        print(f"[Automation] Task failed: {e}")
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)

def get_posts_count_today() -> int:
    """Get count of posts made today."""
    response = httpx.get("http://core-api:8000/api/social/posts/today")
    return response.json()["count"]

def get_next_template_type(posts_today: int) -> str:
    """Determine next template type based on rotation."""
    templates = ["educational", "testimonial", "promotional"]
    return templates[posts_today % len(templates)]

def enqueue_video_job(template: str, duration: int, resolution: str) -> dict:
    """Enqueue video generation job."""
    response = httpx.post("http://video-service:8000/api/video/generate", json={
        "prompt": f"Generate {template} content about accident claims",
        "duration": duration,
        "resolution": resolution
    })
    return response.json()

def wait_for_video_completion(job_id: str, timeout: int = 120) -> str:
    """Wait for video job to complete (with timeout)."""
    import time
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = httpx.get(f"http://video-service:8000/api/video/status/{job_id}")
        job_status = response.json()
        
        if job_status["status"] == "completed":
            return job_status["video_url"]
        elif job_status["status"] == "failed":
            raise Exception(f"Video generation failed: {job_status.get('message')}")
        
        time.sleep(5)  # Check every 5 seconds
    
    return None  # Timeout

def enqueue_social_post(video_url: str, template_type: str, platforms: list, time_slot: str) -> dict:
    """Enqueue social media posting job."""
    response = httpx.post("http://social-service:8000/api/social/post", json={
        "video_url": video_url,
        "template_type": template_type,
        "platforms": platforms,
        "time_slot": time_slot,
        "scheduled_for": datetime.now().isoformat()
    })
    return response.json()

def log_automation_event(event_type: str, details: dict):
    """Log automation event to database."""
    httpx.post("http://core-api:8000/api/logs/automation", json={
        "event_type": event_type,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })
```

**Dockerfile pentru Scheduler:**
```dockerfile
# scheduler-service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Start Celery worker + Beat scheduler
CMD ["sh", "-c", "celery -A tasks.celery_app:app worker --loglevel=info & celery -A tasks.celery_app:app beat --loglevel=info & uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

---

### Faza 5: API Gateway (Nginx) (Zi 10)

**nginx/nginx.conf:**
```nginx
# AutoPro API Gateway
upstream core_api {
    server core-api:8000;
}

upstream video_service {
    server video-service:8000;
}

upstream scheduler_service {
    server scheduler-service:8000;
}

upstream social_service {
    server social-service:8000;
}

upstream email_service {
    server email-service:8000;
}

upstream mcp_service {
    server mcp-service:8000;
}

server {
    listen 80;
    server_name localhost;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
    
    # Core API routes
    location /api/leads {
        proxy_pass http://core_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/referrals {
        proxy_pass http://core_api;
    }
    
    location /api/financial {
        proxy_pass http://core_api;
    }
    
    # Video Service routes
    location /api/video {
        proxy_pass http://video_service;
        proxy_read_timeout 300s;  # 5 minutes for video upload
    }
    
    # WebSocket for video progress
    location /api/video/progress {
        proxy_pass http://video_service;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Scheduler Service routes
    location /api/scheduler {
        proxy_pass http://scheduler_service;
    }
    
    # Social Media Service routes
    location /api/social {
        proxy_pass http://social_service;
    }
    
    # Email Service routes
    location /api/email {
        proxy_pass http://email_service;
    }
    
    # MCP Service routes
    location /api/mcp {
        proxy_pass http://mcp_service;
    }
    
    # Health checks (all services)
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

---

### Faza 6: Testing & Validation (Zi 11-12)

#### Task 6.1: Integration Tests
```python
# tests/integration/test_video_flow.py
import pytest
import httpx
import asyncio
import websockets

@pytest.mark.asyncio
async def test_video_generation_flow():
    """Test complete video generation flow with WebSocket progress."""
    
    # 1. Enqueue video job
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8002/api/video/generate", json={
            "prompt": "Test video about accident claims",
            "duration": 10,
            "resolution": "720p"
        })
        
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        assert job_id is not None
    
    # 2. Connect to WebSocket for progress
    progress_updates = []
    
    async with websockets.connect(f"ws://localhost:8002/api/video/progress?job_id={job_id}") as ws:
        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=5.0)
                progress = json.loads(message)
                progress_updates.append(progress)
                
                if progress["status"] == "completed":
                    break
                elif progress["status"] == "failed":
                    pytest.fail(f"Video generation failed: {progress.get('message')}")
                    
            except asyncio.TimeoutError:
                # Check if still processing
                async with httpx.AsyncClient() as client:
                    status_response = await client.get(f"http://localhost:8002/api/video/status/{job_id}")
                    if status_response.json()["status"] == "completed":
                        break
    
    # 3. Verify progress updates
    assert len(progress_updates) >= 3  # At least 3 progress updates
    assert progress_updates[0]["progress"] < progress_updates[-1]["progress"]
    assert progress_updates[-1]["status"] == "completed"
    assert "video_url" in progress_updates[-1]
    
    # 4. Download video
    video_url = progress_updates[-1]["video_url"]
    async with httpx.AsyncClient() as client:
        video_response = await client.get(video_url)
        assert video_response.status_code == 200
        assert len(video_response.content) > 1000  # Video is non-empty

@pytest.mark.asyncio
async def test_daily_automation_flow():
    """Test daily automation posting flow."""
    
    # 1. Trigger manual post
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8003/api/scheduler/trigger", json={
            "time_slot": "manual_test"
        })
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] in ["success", "quota_reached"]
        
        if result["status"] == "success":
            # 2. Verify video was generated
            job_id = result["job_id"]
            video_status = await client.get(f"http://localhost:8002/api/video/status/{job_id}")
            assert video_status.json()["status"] == "completed"
            
            # 3. Verify social post was created
            post_id = result["post_id"]
            post_status = await client.get(f"http://localhost:8004/api/social/posts/{post_id}")
            assert post_status.json()["status"] == "published"
```

---

### Faza 7: Deployment & Monitoring (Zi 13-14)

#### Task 7.1: Kubernetes Manifests (Optional pentru scalare)
```yaml
# k8s/core-api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: core-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: core-api
  template:
    metadata:
      labels:
        app: core-api
    spec:
      containers:
      - name: core-api
        image: autopro/core-api:3.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: autopro-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: core-api
spec:
  selector:
    app: core-api
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: core-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: core-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 📈 BENEFICII AȘTEPTATE

### Performance

| Metric | Before (Monolit) | After (Microservicii) | Improvement |
|--------|------------------|----------------------|-------------|
| **API Response Time** | 200-5000ms | 50-200ms | **10-25x faster** |
| **Video Generation Time** | 60s (blocking) | 60s (async) | **Non-blocking** |
| **Concurrent Requests** | 10-20 | 100+ | **5-10x more** |
| **Error Rate** | 5-10% | <1% | **90% reduction** |
| **Deployment Time** | 5-10 min (downtime) | 30s (zero-downtime) | **10-20x faster** |

### Scalability

```
Horizontal Scaling:
- Core API: 1 → 3-10 replicas (auto-scale)
- Video Workers: 1 → 3-5 workers (parallel)
- Scheduler: 1 → 2 replicas (redundancy)
- Social Service: 1 → 2-3 replicas

Total Capacity:
- Before: 100 req/min
- After: 1000+ req/min (10x improvement)
```

### Cost Optimization

```
Resource Usage (per month):
- CPU: 50% reduction (efficient workers)
- Memory: 40% reduction (no monolith overhead)
- Storage: Same (Supabase)

Estimated Savings:
- Cloud costs: 30-40% reduction
- Development time: 50% faster (independent deploys)
- Bug fixing: 60% faster (isolated services)
```

---

## 🎯 SUCCESS METRICS

### KPIs de Monitorizat

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

# API Metrics
api_requests_total = Counter('api_requests_total', 'Total API requests', ['service', 'endpoint', 'status'])
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['service', 'endpoint'])

# Video Metrics
video_jobs_total = Counter('video_jobs_total', 'Total video jobs', ['status'])
video_generation_duration = Histogram('video_generation_duration_seconds', 'Video generation time')
video_workers_active = Gauge('video_workers_active', 'Active video workers')

# Scheduler Metrics
scheduled_posts_total = Counter('scheduled_posts_total', 'Total scheduled posts', ['status'])
automation_errors_total = Counter('automation_errors_total', 'Total automation errors')

# Social Media Metrics
social_posts_total = Counter('social_posts_total', 'Total social posts', ['platform', 'status'])
social_engagement_total = Counter('social_engagement_total', 'Total engagement', ['platform', 'type'])
```

### Targets

```
✅ API Response Time: p95 < 200ms
✅ Video Generation: 100% success rate (with retries)
✅ Automation Posts: 3x/day without fail
✅ Uptime: 99.9% (max 43 min downtime/month)
✅ Error Rate: < 1%
✅ Deployment Frequency: Daily (zero-downtime)
```

---

## 🚨 RISKS & MITIGATION

### Risk 1: Complex Migration
**Mitigation:**
- Incremental migration (1 service at a time)
- Parallel run (old + new for 2 weeks)
- Feature flags for rollback

### Risk 2: Message Queue Overhead
**Mitigation:**
- Monitor queue length
- Auto-scale workers based on queue size
- Circuit breakers for failed services

### Risk 3: Network Latency (inter-service)
**Mitigation:**
- All services in same network (Docker/K8s)
- gRPC for high-throughput endpoints
- Service mesh (Istio) for advanced routing

### Risk 4: Debugging Complexity
**Mitigation:**
- Distributed tracing (Jaeger)
- Centralized logging (ELK stack)
- Correlation IDs în toate requesturile

---

## 📚 DOCUMENTAȚIE COMPLETĂ

### API Documentation
- OpenAPI/Swagger pentru fiecare microserviciu
- Postman collection pentru testing
- Architecture Decision Records (ADRs)

### Monitoring Dashboards
- Grafana dashboard pentru fiecare serviciu
- Alerts pentru metrici critice
- SLA/SLO tracking

### Runbooks
- Incident response playbook
- Scaling procedures
- Backup & recovery

---

## ✅ CHECKLIST FINAL

### Pre-Deployment
- [ ] Docker images built și testate
- [ ] Database migrations executate
- [ ] Environment variables configurate
- [ ] SSL certificates setup (Let's Encrypt)
- [ ] Backup database realizat

### Deployment
- [ ] Redis cluster functional
- [ ] Core API deployed
- [ ] Video Service deployed (3 workers)
- [ ] Scheduler Service deployed
- [ ] Social Service deployed
- [ ] Email Service deployed
- [ ] MCP Service deployed
- [ ] Nginx API Gateway configured
- [ ] Monitoring stack active (Prometheus + Grafana)

### Post-Deployment
- [ ] Health checks toate serviciile
- [ ] Integration tests passed
- [ ] Load testing passed (100+ RPS)
- [ ] Video generation flow validated
- [ ] Automation scheduler validated (manual trigger)
- [ ] Social posting flow validated
- [ ] Monitoring dashboards configured
- [ ] Alerts configured (Discord/Email)
- [ ] Documentation updated
- [ ] Team training completed

---

## 🎉 CONCLUSION

**Curent Status:** Sistem funcțional DAR arhitectură monolitică cu probleme majore de scalabilitate și performanță.

**Propunere:** Refactorizare completă pe arhitectură microservicii cu:
- ✅ 6 servicii independente
- ✅ Message Queue (Redis Streams)
- ✅ API Gateway (Nginx)
- ✅ Async video processing (3-5 workers)
- ✅ Distributed scheduler (Celery)
- ✅ Monitoring complet (Prometheus + Grafana)

**Expected Impact:**
- 🚀 10-25x mai rapid (API response time)
- 📈 10x mai scalabil (horizontal scaling)
- 💰 30-40% cost reduction
- 🔧 50% mai rapid development
- 🛡️ 99.9% uptime (zero-downtime deploys)

**Timeline:** 14 zile pentru migrare completă + testing

**Recommendation:** ✅ APPROVED - Începem refactorizarea imediat!

---

**Semnat:**
- Arhitect Tehnic Principal
- Data: 28 Octombrie 2025

**Next Steps:**
1. Backup complet al sistemului actual
2. Setup infrastructure (Redis, Docker Compose)
3. Migrare progresivă (Core API → Video → Scheduler → ...)
4. Testing intensiv
5. Deploy în producție (cu rollback plan)

---

*Acest document va fi actualizat pe măsură ce refactorizarea avansează.*
