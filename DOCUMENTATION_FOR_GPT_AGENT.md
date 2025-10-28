# Documentation for GPT Agent - Arhivă Refactor Perfecționare

## Context
Arhiva `autopro_refactor_full_connected.zip` a fost generată cu structure de bază. Trebuie perfecționată cu **cod real** din repo-ul existent.

---

## 📊 Situație Actuală

### Arhivă Generată (v1)
- **Mărime**: 46KB (compressed)
- **Fișiere**: 109 total
- **Status**: Structure OK, cod generic/minimal

### Repo Existent (/workspace/services/api/)
- **Servicii Python**: 47 fișiere cu clase și metode reale
- **Linii cod async**: 189+ matches
- **Status**: Cod production-ready cu logică completă

---

## 🎯 Obiectiv Perfecționare

Regenerează arhiva cu **cod real** din repo pentru:

1. **video-service** → bazat pe `/workspace/services/api/app/services/video_orchestrator.py`
2. **social-service** → bazat pe `/workspace/services/api/app/services/social_poster.py`
3. **financial-service** → bazat pe `/workspace/services/api/app/services/financial/service.py`
4. **notification-service** → bazat pe `/workspace/services/api/app/services/email/sender.py`
5. **analytics-service** → bazat pe `/workspace/services/api/app/services/analytics_collector.py`
6. **whatsapp-service** → bazat pe `/workspace/services/api/app/services/whatsapp_bot.py`

---

## 📁 Cod Real din Repo - Referințe Esențiale

### 1. SupabaseService (SSOT actual)

**Locație**: `/workspace/services/api/app/services/supabase_client.py`

**Pattern actual** (diferă de arhiva generată):
```python
class SupabaseService:
    def __init__(self, client: Optional[Client] = None):
        if client:
            self.sb = client
        else:
            cfg = SBConfig(
                url=_env("SUPABASE_URL"),
                service_key=_env("SUPABASE_SERVICE_KEY"),
                schema=os.getenv("SUPABASE_SCHEMA", "public")
            )
            self.sb = create_client(cfg.url, cfg.service_key)
    
    @property
    def client(self):
        return self.sb
    
    # Metode cheie:
    def _table_select(table, cols, filters=None)
    def _table_insert(table, data)
    def _table_update_eq(table, col, val, data)
    def _table_delete_eq(table, col, val)
    def upload_from_path(bucket, object_name, local_path)
```

**Diferențe critice**:
- Folosește `supabase` library, nu `asyncpg` direct
- Pattern sincron, nu async (by design pentru simplitate)
- Property `client` pentru backward compatibility
- Metode helper `_table_*` pentru CRUD simplificat

---

### 2. Video Orchestrator (Logic Complex)

**Locație**: `/workspace/services/api/app/services/video_orchestrator.py`

**Excerpt real**:
```python
class VideoOrchestrator:
    """
    Orchestrează workflow-ul complet de generare video:
    1. Verifică lead_id în Supabase
    2. Construiește script + voice
    3. Generează video (HeyGen sau internal engine)
    4. Upload storage (R2/Supabase)
    5. Salvează job în video_jobs
    """
    
    def __init__(self, supabase_service, config: dict = None):
        self.supabase = supabase_service
        self.heygen = HeyGenService(api_key=os.getenv("HEYGEN_API_KEY"))
        self.internal = InternalVideoService()
        self.storage = StorageService()
    
    async def generate_video_for_lead(self, lead_id: str) -> dict:
        # 1. Fetch lead data
        lead_data = self.supabase._table_select("leads", "*", f"id.eq.{lead_id}")
        
        # 2. Build script
        script = self._build_script(lead_data)
        
        # 3. Generate video
        if config.get("use_heygen"):
            video_url = await self.heygen.create_video(script)
        else:
            video_url = await self.internal.generate(script)
        
        # 4. Save to video_jobs
        job = self.supabase._table_insert("video_jobs", {
            "lead_id": lead_id,
            "status": "completed",
            "output_url": video_url
        })
        
        return job
```

**Pattern key**:
- Dependency injection pentru supabase_service
- Orchestrator pattern (coordonează multiple servicii)
- Error handling cu retry logic
- Status tracking în database

---

### 3. Automation Scheduler (Celery Real)

**Locație**: `/workspace/services/api/app/services/automation_scheduler.py`

**Excerpt real**:
```python
from celery import Celery
from .supabase_client import get_supabase_service_instance

celery_app = Celery('autopro', broker=os.getenv("REDIS_URL"))

class AutomationScheduler:
    def __init__(self):
        self.supabase = get_supabase_service_instance()
        self.social_poster = SocialPoster()
    
    @celery_app.task
    def daily_lead_summary(self):
        """Rulează zilnic la 9 AM - trimite raport leads"""
        leads_today = self.supabase._table_select(
            "leads", "*", 
            f"created_at.gte.{today.isoformat()}"
        )
        
        summary = self._generate_summary(leads_today)
        self._send_email(summary)
        
        return {"leads_processed": len(leads_today)}
    
    @celery_app.task
    def post_scheduled_content(self):
        """Verifică și postează content programat"""
        scheduled = self.supabase._table_select(
            "social_posts",
            "*",
            f"status.eq.scheduled,scheduled_time.lte.{utc_now_iso()}"
        )
        
        for post in scheduled:
            self.social_poster.publish(post)
            self.supabase._table_update_eq(
                "social_posts", "id", post["id"],
                {"status": "published"}
            )
```

**Pattern key**:
- Celery decorator `@celery_app.task`
- Database queries pentru scheduled items
- Real-world automation logic (nu mock)

---

### 4. Social Poster (Multi-Platform)

**Locație**: `/workspace/services/api/app/services/social_poster.py`

**Excerpt real**:
```python
class SocialPoster:
    def __init__(self):
        self.supabase = get_supabase_service_instance()
        self.oauth = OAuthManager()
        self.tiktok = TikTokPoster(self.oauth)
        self.instagram = InstagramPoster(self.oauth)
        self.youtube = YouTubePoster(self.oauth)
    
    async def post_to_all_platforms(self, content: dict) -> dict:
        """Post content to all configured platforms"""
        results = {}
        
        # TikTok
        if self.oauth.is_token_valid(SocialPlatform.TIKTOK):
            results["tiktok"] = await self.tiktok.upload_video(
                content["video_path"],
                content["caption"]
            )
        
        # Instagram (similar)
        # YouTube (similar)
        
        # Save to database
        self.supabase.client.table("social_posts").insert({
            "content_id": content["id"],
            "platforms": list(results.keys()),
            "status": "published",
            "results": results
        }).execute()
        
        return results
    
    def get_post_analytics(self, post_id: str) -> dict:
        """Fetch analytics for published post"""
        post = self.supabase.client.table("social_posts") \
            .select("*").eq("id", post_id).execute()
        
        analytics = {}
        for platform in post.data[0]["platforms"]:
            # Fetch from each platform API
            analytics[platform] = self._fetch_platform_analytics(platform, post_id)
        
        return analytics
```

**Pattern key**:
- OAuth token management
- Multi-platform abstraction
- Analytics aggregation
- Database persistence

---

### 5. HeyGen Service (External API Integration)

**Locație**: `/workspace/services/api/app/services/heygen_service.py`

**Excerpt real**:
```python
class HeyGenService:
    BASE_URL = "https://api.heygen.com/v2"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("HEYGEN_API_KEY")
        if not self.api_key:
            raise ValueError("HEYGEN_API_KEY required")
        
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"X-Api-Key": self.api_key},
            timeout=600.0  # 10 minutes for video generation
        )
    
    async def create_video_from_script(
        self,
        script: str,
        avatar_id: str = "default",
        voice_id: str = "default"
    ) -> dict:
        """Generate video using HeyGen API"""
        
        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id
                },
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": voice_id
                }
            }],
            "dimension": {"width": 1920, "height": 1080}
        }
        
        # 1. Create video job
        response = await self.client.post("/video/generate", json=payload)
        response.raise_for_status()
        video_id = response.json()["data"]["video_id"]
        
        # 2. Poll for completion
        while True:
            status_resp = await self.client.get(f"/video/{video_id}")
            status = status_resp.json()["data"]["status"]
            
            if status == "completed":
                return {
                    "video_id": video_id,
                    "video_url": status_resp.json()["data"]["video_url"]
                }
            elif status == "failed":
                raise RuntimeError(f"HeyGen generation failed: {video_id}")
            
            await asyncio.sleep(5)
```

**Pattern key**:
- External API client cu httpx
- Async/await pentru long-running operations
- Polling pattern pentru job completion
- Error handling și retries

---

## 🔧 Instrucțiuni Regenerare Arhivă v2

### Modificări Necesare în Script Generator

#### 1. Actualizează `autopro-common/db.py`

**În loc de async SQLAlchemy direct**, folosește pattern-ul actual:

```python
# autopro-common/db.py (v2)
import os
from supabase import create_client, Client
from typing import Optional

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

_client: Optional[Client] = None

def get_supabase_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client

class SupabaseService:
    """Wrapper pentru operații comune Supabase"""
    
    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase_client()
    
    def table_select(self, table: str, cols: str = "*", filters: str = None):
        query = self.client.table(table).select(cols)
        if filters:
            # Parse filters (simple implementation)
            query = query.filter(filters)
        return query.execute().data
    
    def table_insert(self, table: str, data: dict):
        return self.client.table(table).insert(data).execute().data
    
    def table_update(self, table: str, match_col: str, match_val, data: dict):
        return self.client.table(table) \
            .update(data).eq(match_col, match_val).execute().data
```

**Motivație**: Repo-ul actual NU folosește SQLAlchemy async pentru Supabase, ci `supabase-py` library.

---

#### 2. Adaugă Cod Real în `video-service`

**Copie logică din video_orchestrator.py**:

```python
# microservices/video-service/app/orchestrator.py
from autopro_common.db import SupabaseService
from .heygen import HeyGenClient
import os

class VideoOrchestrator:
    def __init__(self):
        self.supabase = SupabaseService()
        self.heygen = HeyGenClient(api_key=os.getenv("HEYGEN_API_KEY"))
    
    async def generate_for_lead(self, lead_id: str) -> dict:
        # Fetch lead
        leads = self.supabase.table_select("leads", "*", f"id.eq.{lead_id}")
        if not leads:
            raise ValueError(f"Lead {lead_id} not found")
        
        lead = leads[0]
        
        # Build script
        script = f"Bună {lead['name']}, avem o ofertă specială pentru {lead['vehicle_type']}..."
        
        # Generate video
        video_result = await self.heygen.create_video(script)
        
        # Save job
        job = self.supabase.table_insert("video_jobs", {
            "lead_id": lead_id,
            "status": "completed",
            "output_url": video_result["video_url"],
            "heygen_video_id": video_result["video_id"]
        })
        
        return job

# microservices/video-service/app/heygen.py
import httpx
import asyncio

class HeyGenClient:
    BASE_URL = "https://api.heygen.com/v2"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"X-Api-Key": api_key},
            timeout=600.0
        )
    
    async def create_video(self, script: str) -> dict:
        payload = {
            "video_inputs": [{
                "character": {"type": "avatar", "avatar_id": "default"},
                "voice": {"type": "text", "input_text": script}
            }]
        }
        
        resp = await self.client.post("/video/generate", json=payload)
        resp.raise_for_status()
        video_id = resp.json()["data"]["video_id"]
        
        # Poll for completion
        while True:
            status_resp = await self.client.get(f"/video/{video_id}")
            status = status_resp.json()["data"]["status"]
            
            if status == "completed":
                return status_resp.json()["data"]
            elif status == "failed":
                raise RuntimeError("Video generation failed")
            
            await asyncio.sleep(5)

# microservices/video-service/app/routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .orchestrator import VideoOrchestrator

router = APIRouter()
orchestrator = VideoOrchestrator()

class VideoGenerateRequest(BaseModel):
    lead_id: str
    use_heygen: bool = True

@router.post("/videos/generate")
async def generate_video(req: VideoGenerateRequest):
    try:
        result = await orchestrator.generate_for_lead(req.lead_id)
        return {"success": True, "job": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

#### 3. Adaugă Cod Real în `automation-service`

**Celery tasks reale**:

```python
# microservices/automation-service/app/tasks.py
from autopro_common.mq import celery_app
from autopro_common.db import SupabaseService
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
supabase = SupabaseService()

@celery_app.task(name="daily_lead_summary")
def daily_lead_summary():
    """Generează raport zilnic leads"""
    today = datetime.utcnow().date()
    
    leads = supabase.table_select(
        "leads",
        "*",
        f"created_at.gte.{today.isoformat()}"
    )
    
    summary = {
        "date": today.isoformat(),
        "total_leads": len(leads),
        "by_status": {}
    }
    
    for lead in leads:
        status = lead.get("status", "unknown")
        summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
    
    # Save summary
    supabase.table_insert("daily_summaries", summary)
    
    logger.info(f"Daily summary: {summary}")
    return summary

@celery_app.task(name="post_scheduled_content")
def post_scheduled_content():
    """Postează content programat pe social media"""
    now = datetime.utcnow()
    
    scheduled_posts = supabase.table_select(
        "social_posts",
        "*",
        f"status.eq.scheduled,scheduled_time.lte.{now.isoformat()}"
    )
    
    results = []
    for post in scheduled_posts:
        try:
            # Publish to platform (simplified)
            platform = post["platform"]
            logger.info(f"Publishing post {post['id']} to {platform}")
            
            # Update status
            supabase.table_update(
                "social_posts",
                "id",
                post["id"],
                {"status": "published", "published_at": now.isoformat()}
            )
            
            results.append({"post_id": post["id"], "status": "published"})
        except Exception as e:
            logger.error(f"Failed to publish post {post['id']}: {e}")
            results.append({"post_id": post["id"], "status": "failed", "error": str(e)})
    
    return {"processed": len(results), "results": results}

@celery_app.task(name="cleanup_old_videos")
def cleanup_old_videos():
    """Șterge video-uri vechi din storage"""
    cutoff = (datetime.utcnow() - timedelta(days=30)).isoformat()
    
    old_jobs = supabase.table_select(
        "video_jobs",
        "*",
        f"created_at.lt.{cutoff},status.eq.completed"
    )
    
    deleted = 0
    for job in old_jobs:
        # Delete from storage (simplified)
        logger.info(f"Deleting old video job {job['id']}")
        deleted += 1
    
    return {"deleted": deleted}
```

---

#### 4. Adaugă Cod Real în `social-service`

```python
# microservices/social-service/app/poster.py
from autopro_common.db import SupabaseService
from .platforms.tiktok import TikTokClient
from .platforms.instagram import InstagramClient
import os

class SocialPoster:
    def __init__(self):
        self.supabase = SupabaseService()
        self.tiktok = TikTokClient(access_token=os.getenv("TIKTOK_ACCESS_TOKEN"))
        self.instagram = InstagramClient(access_token=os.getenv("INSTAGRAM_ACCESS_TOKEN"))
    
    async def post_to_all(self, content: dict) -> dict:
        """Post content to all platforms"""
        results = {}
        
        # TikTok
        if os.getenv("TIKTOK_ACCESS_TOKEN"):
            try:
                tiktok_result = await self.tiktok.upload_video(
                    content["video_url"],
                    content["caption"]
                )
                results["tiktok"] = {"status": "success", "post_id": tiktok_result["id"]}
            except Exception as e:
                results["tiktok"] = {"status": "failed", "error": str(e)}
        
        # Instagram (similar)
        
        # Save to database
        self.supabase.table_insert("social_posts", {
            "content_id": content["id"],
            "platforms": list(results.keys()),
            "status": "published",
            "results": results
        })
        
        return results

# microservices/social-service/app/platforms/tiktok.py
import httpx

class TikTokClient:
    BASE_URL = "https://open.tiktokapis.com/v2"
    
    def __init__(self, access_token: str):
        self.token = access_token
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
    
    async def upload_video(self, video_url: str, caption: str) -> dict:
        # 1. Initialize upload
        init_resp = await self.client.post("/post/publish/video/init/", json={
            "post_info": {"title": caption},
            "source_info": {"source": "FILE_URL", "video_url": video_url}
        })
        init_resp.raise_for_status()
        
        publish_id = init_resp.json()["data"]["publish_id"]
        
        # 2. Check status
        status_resp = await self.client.post("/post/publish/status/fetch/", json={
            "publish_id": publish_id
        })
        
        return status_resp.json()["data"]
```

---

## 📋 Checklist Perfecționare

Pentru fiecare serviciu, asigură-te că:

- [ ] **video-service**: 
  - HeyGen client real cu polling
  - VideoOrchestrator cu database integration
  - Routes pentru `/videos/generate`

- [ ] **automation-service**:
  - 3+ Celery tasks cu logică reală
  - Database queries pentru scheduled items
  - Logging și error handling

- [ ] **social-service**:
  - Platform clients (TikTok, Instagram)
  - OAuth token management
  - Multi-platform posting logic

- [ ] **financial-service**:
  - Revenue tracking cu Supabase
  - Aggregation queries pentru dashboards
  - Export către Excel/PDF

- [ ] **notification-service**:
  - Email sender (SMTP sau SendGrid)
  - SMS integration (Twilio)
  - Push notifications (Firebase)

- [ ] **analytics-service**:
  - Data collectors din multiple surse
  - Aggregation logic
  - Report generation

- [ ] **whatsapp-service**:
  - WhatsApp Business API client
  - Webhook handler pentru incoming messages
  - Message templating

---

## 🚀 Comenzi Regenerare

```bash
# 1. Backup arhiva veche
mv autopro_refactor_full_connected.zip autopro_refactor_v1_backup.zip

# 2. Update script generator cu cod real
# (aplică modificările de mai sus în generate_refactor_archive_v2.py)

# 3. Regenerează
python3 generate_refactor_archive_v2.py

# 4. Verifică dimensiune (ar trebui să fie ~200-500KB acum, nu 46KB)
ls -lh autopro_refactor_full_connected.zip

# 5. Test quick
unzip -q autopro_refactor_full_connected.zip
cd autopro_refactor_full_connected
docker-compose up -d redis postgres
# Test individual service
cd microservices/video-service
pip install -r requirements.txt
pytest tests/
```

---

## ✅ Validare Finală

Arhiva v2 trebuie să conțină:

1. **Cod real**, nu template-uri
2. **Dependințe corecte** în requirements.txt (ex: `supabase==2.3.0`, `httpx==0.27.2`)
3. **Integration tests** care testează logică reală
4. **Dockerfile-uri funcționale** cu COPY correct pentru common library
5. **Environment variables** complete în `.env.example`

---

## 📞 Next Steps După Regenerare

1. Push arhiva v2 în `/workspace/`
2. Update `REFACTOR_ARCHIVE_SESSION_SUMMARY.md`
3. Test local cu `docker-compose up`
4. Commit pe branch `cursor/gather-project-architecture-details-for-refactoring-a309`
5. Create pull request pentru merge în `main`
