# 📖 AUTOPRO DAUNE - MANUAL DE UTILIZARE COMPLET

**Versiune:** 1.0
**Data:** 2025-09-30
**Status:** Production Ready

---

## 📑 CUPRINS

1. [Pornire Sistem](#1-pornire-sistem)
2. [Lead Management](#2-lead-management)
3. [Generare Video](#3-generare-video)
4. [Social Media Automation](#4-social-media-automation)
5. [Sistem Referral (200 LEI)](#5-sistem-referral-200-lei)
6. [Financial Tracking](#6-financial-tracking)
7. [WhatsApp Bot](#7-whatsapp-bot)
8. [Automation & Scheduling](#8-automation--scheduling)
9. [Analytics & Reports](#9-analytics--reports)
10. [Growth Engine](#10-growth-engine)
11. [Admin Dashboard](#11-admin-dashboard)
12. [API Usage](#12-api-usage)

---

## 1. PORNIRE SISTEM

### 1.1 Pornire Rapidă (Recomandat)

```powershell
# Navighează în folderul proiectului
cd C:\Users\JJ\Desktop\autopro_daune\autoprodaune-1

# Pornește tot
.\start.ps1
```

**Ce face:**
- Deschide 2 terminale separate
- Terminal 1: Backend FastAPI (port 8001)
- Terminal 2: Frontend React (port 3003)
- Așteaptă 10-15 secunde până pornesc

**URLs:**
- 🌐 Frontend: http://localhost:3003
- 🔧 Backend API: http://localhost:8001
- 📚 API Docs: http://localhost:8001/docs

---

### 1.2 Pornire Manuală (Control Complet)

#### Backend (Terminal 1):
```powershell
cd C:\Users\JJ\Desktop\autopro_daune\autoprodaune-1\services\api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

**Output așteptat:**
```
INFO:     ✅ Prometheus metrics configured
INFO:     ✅ All main routers loaded successfully
INFO:     ✅ Database connection verified
INFO:     ✅ Automation scheduler started
INFO:     ✅ AutoPro Daune API started with 138 routes
INFO:     Uvicorn running on http://127.0.0.1:8001
```

#### Frontend (Terminal 2):
```powershell
cd C:\Users\JJ\Desktop\autopro_daune\autoprodaune-1\02_FRONTEND_UI_CLEAN
npm run dev
```

**Output așteptat:**
```
VITE v5.4.19  ready in 2341 ms
➜  Local:   http://localhost:3003/
```

---

### 1.3 Verificare Sistem

```powershell
# Test backend
curl http://localhost:8001/health

# Expected: {"status":"ok","service":"autopro-daune","port":8001}

# Test database
curl http://localhost:8001/api/leads/

# Expected: {"items":[],"total":0,"page":1}
```

---

## 2. LEAD MANAGEMENT

### 2.1 Creare Lead Manual (API)

```powershell
# Lead simplu
curl -X POST http://localhost:8001/api/leads/ `
  -H "Content-Type: application/json" `
  -d '{
    "name": "Ion Popescu",
    "phone_number": "0712345678",
    "email": "ion.popescu@email.com",
    "source": "direct",
    "lead_type": "crash_claim",
    "priority": "high",
    "notes": "Accident din 15 martie"
  }'
```

**Parametri disponibili:**
- `name` - Nume client (optional)
- `phone_number` - Telefon (required)
- `email` - Email (optional)
- `source` - Sursă: `tiktok`, `facebook`, `instagram`, `whatsapp`, `referral`, `direct`
- `lead_type` - Tip: `crash_claim`, `insurance_dispute`, `consultation`
- `status` - Status: `new`, `contacted`, `qualified`, `converted`, `closed`
- `priority` - Prioritate: `low`, `medium`, `high`
- `estimated_value` - Valoare estimată (număr)
- `notes` - Notițe

**Response:**
```json
{
  "id": "uuid-here",
  "name": "Ion Popescu",
  "phone_number": "0712345678",
  "source": "direct",
  "status": "new",
  "priority": "high",
  "created_at": "2025-09-30T10:00:00Z"
}
```

---

### 2.2 Vizualizare Leads (Dashboard)

**URL:** http://localhost:3003/admin → Leads Tab

**Funcționalități:**
- 📋 Lista completă leads
- 🔍 Filtrare după status, prioritate, sursă
- ✏️ Edit lead (click pe lead)
- 🗑️ Delete lead
- 📊 Statistici (conversie, valoare totală)

---

### 2.3 Update Lead Status

```powershell
# Marchează lead ca "contacted"
curl -X PUT http://localhost:8001/api/leads/{lead_id} `
  -H "Content-Type: application/json" `
  -d '{
    "status": "contacted",
    "notes": "Apelat la 10:30, răspunde mâine"
  }'
```

---

### 2.4 Get Lead Details

```powershell
curl http://localhost:8001/api/leads/{lead_id}
```

---

### 2.5 List Leads cu Filtre

```powershell
# Toate leads cu prioritate HIGH
curl "http://localhost:8001/api/leads/?priority=high"

# Leads din TikTok
curl "http://localhost:8001/api/leads/?source=tiktok"

# Leads convertite
curl "http://localhost:8001/api/leads/?status=converted"

# Combinat
curl "http://localhost:8001/api/leads/?source=tiktok&priority=high&status=new"
```

---

### 2.6 Delete Lead

```powershell
curl -X DELETE http://localhost:8001/api/leads/{lead_id}
```

---

## 3. GENERARE VIDEO

### 3.1 Video Simplu (Rapid, Text pe Background)

```powershell
curl -X POST http://localhost:8001/api/simple-video/generate `
  -H "Content-Type: application/json" `
  -d '{
    "text": "AutoPro Daune - Rezolvă daunele rapid și simplu!",
    "duration": 10,
    "width": 1080,
    "height": 1920,
    "background_color": "#1a73e8",
    "text_color": "#ffffff"
  }'
```

**Parametri:**
- `text` - Textul afișat (required)
- `duration` - Durată în secunde (default: 10)
- `width` / `height` - Rezoluție (default: 720x480)
- `background_color` - Culoare fundal (hex code)
- `text_color` - Culoare text (hex code)

**Response:**
```json
{
  "success": true,
  "message": "Video generated successfully",
  "video_path": "services/api/generated_videos/simple/video_20250930_123456.mp4",
  "file_size": 1024000,
  "duration": 10
}
```

**Output:** Fișier salvat în `services/api/generated_videos/simple/`

---

### 3.2 Video Professional (Cu Avatar și Background)

```powershell
curl -X POST http://localhost:8001/api/professional-video/generate `
  -H "Content-Type: application/json" `
  -d '{
    "text": "Ai avut un accident? AutoPro Daune te ajută!",
    "duration": 15,
    "resolution": "1080p",
    "aspect_ratio": "portrait",
    "avatar_style": "professional",
    "background": "office",
    "voice_language": "romanian",
    "enable_subtitles": true
  }'
```

**Parametri:**
- `text` - Script video (required)
- `duration` - Durată (10-60 secunde)
- `resolution` - `720p`, `1080p`, `4k`
- `aspect_ratio` - `portrait` (9:16), `landscape` (16:9), `square` (1:1)
- `avatar_style` - `professional`, `casual`, `friendly`
- `background` - `office`, `modern`, `gradient`, `custom`
- `voice_language` - `romanian`, `english`
- `enable_subtitles` - true/false

**Output:** Video de calitate înaltă cu avatar animat

---

### 3.3 Video Advanced (Cu Toate Feature-urile)

```powershell
curl -X POST http://localhost:8001/api/advanced-video/generate `
  -H "Content-Type: application/json" `
  -d '{
    "text": "Câștigă 200 LEI pentru fiecare recomandare!",
    "duration": 20,
    "resolution": "1080p",
    "aspect_ratio": "portrait",
    "avatar_id": "professional",
    "background_id": "office",
    "voice_language": "romanian",
    "voice_gender": "female",
    "enable_subtitles": true,
    "enable_lip_sync": true,
    "custom_background_color": "#1a73e8",
    "text_position": "bottom"
  }'
```

**Feature-uri extra:**
- Lip sync (sincronizare buze cu voce)
- Subtitles automate
- Multiple avatars
- Custom backgrounds
- Text positioning

---

### 3.4 List Generated Videos

```powershell
# Simple videos
curl http://localhost:8001/api/simple-video/list

# Advanced videos
curl http://localhost:8001/api/advanced-video/list-generated
```

---

### 3.5 Video Stats

```powershell
curl http://localhost:8001/api/video/stats
```

**Response:**
```json
{
  "total_videos": 45,
  "completed": 40,
  "processing": 3,
  "failed": 2,
  "total_duration_seconds": 1200,
  "avg_processing_time": 15.5
}
```

---

### 3.6 Video Generation în Dashboard

**URL:** http://localhost:3003/admin → Video Management

**Funcționalități:**
- 🎬 Generate new video (form interactiv)
- 📋 Lista video-uri generate
- ▶️ Preview video
- 📥 Download video
- 🗑️ Delete video
- 📊 Video statistics

---

## 4. SOCIAL MEDIA AUTOMATION

### 4.1 Post Imediat (Manual)

```powershell
curl -X POST http://localhost:8001/api/social/post-now `
  -H "Content-Type: application/json" `
  -d '{
    "content": "Ai avut un accident? Află cum îți poți recupera banii! 💰",
    "platforms": ["tiktok", "facebook", "instagram"],
    "media_url": "https://example.com/video.mp4",
    "hashtags": ["#AutoProDaune", "#Despagubiri", "#Accident"]
  }'
```

**Parametri:**
- `content` - Text post (required)
- `platforms` - Array: `tiktok`, `facebook`, `instagram`
- `media_url` - URL video/imagine (optional)
- `hashtags` - Array hashtag-uri
- `scheduled_for` - Data/ora (optional, pentru scheduling)

---

### 4.2 Schedule Post (Programare)

```powershell
curl -X POST http://localhost:8001/api/social/posts `
  -H "Content-Type: application/json" `
  -d '{
    "title": "Post despre despăgubiri",
    "content": "Câștigă bani din accidente! Contactează-ne acum!",
    "platforms": ["tiktok", "instagram"],
    "scheduled_for": "2025-09-30T15:00:00Z",
    "hashtags": ["#AutoPro", "#Daune"],
    "template_type": "promotional"
  }'
```

---

### 4.3 Get Social Posts

```powershell
# Toate posts
curl http://localhost:8001/api/social/posts

# Doar published
curl "http://localhost:8001/api/social/posts?status=published"

# Doar scheduled
curl "http://localhost:8001/api/social/posts?status=scheduled"
```

---

### 4.4 Social Media Analytics

```powershell
curl http://localhost:8001/api/social/analytics
```

**Response:**
```json
{
  "total_posts": 150,
  "total_views": 45000,
  "total_likes": 3200,
  "total_shares": 450,
  "total_comments": 280,
  "engagement_rate": 8.4,
  "leads_generated": 45,
  "conversion_rate": 3.2,
  "by_platform": {
    "tiktok": {"posts": 50, "views": 25000, "engagement": 10.2},
    "facebook": {"posts": 50, "views": 12000, "engagement": 6.5},
    "instagram": {"posts": 50, "views": 8000, "engagement": 8.1}
  }
}
```

---

### 4.5 Social Media Dashboard

**URL:** http://localhost:3003/admin → Social Media

**Funcționalități:**
- 📊 Overview statistics
- 📅 Calendar cu posts programate
- ➕ Create new post
- ✏️ Edit scheduled posts
- 📈 Analytics per platform
- 🎯 Performance tracking

---

## 5. SISTEM REFERRAL (200 LEI)

### 5.1 Create Referral

```powershell
curl -X POST http://localhost:8001/api/referrals/ `
  -H "Content-Type: application/json" `
  -d '{
    "referrer_phone": "0712345678",
    "referrer_name": "Maria Ionescu",
    "referred_phone": "0723456789",
    "referred_name": "Ion Popescu",
    "reward_amount": 200.00
  }'
```

**Response:**
```json
{
  "id": "uuid",
  "referral_code": "REF12345ABC",
  "referrer_phone": "0712345678",
  "referred_phone": "0723456789",
  "status": "pending",
  "reward_amount": 200.00,
  "created_at": "2025-09-30T10:00:00Z"
}
```

---

### 5.2 Complete Referral (Plată Recompensă)

```powershell
curl -X PUT http://localhost:8001/api/referrals/{referral_id}/complete `
  -H "Content-Type: application/json" `
  -d '{
    "payout_method": "bank_transfer",
    "payout_details": {
      "iban": "RO49AAAA1B31007593840000",
      "bank_name": "BRD"
    }
  }'
```

**Status flow:**
1. `pending` - Referral creat, în așteptare
2. `qualified` - Persoana recomandată a devenit client
3. `completed` - Recompensă plătită
4. `cancelled` - Anulat

---

### 5.3 Referral Stats

```powershell
curl http://localhost:8001/api/referrals/stats
```

**Response:**
```json
{
  "total_referrals": 120,
  "pending": 30,
  "qualified": 40,
  "completed": 45,
  "cancelled": 5,
  "total_rewards_paid": 9000.00,
  "avg_conversion_rate": 37.5,
  "top_referrers": [
    {"phone": "0712345678", "name": "Maria", "referrals": 15, "earned": 3000.00}
  ]
}
```

---

### 5.4 Leaderboard (Top Referrers)

```powershell
curl http://localhost:8001/api/affiliate-multiplication/affiliate-leaderboard
```

---

### 5.5 Referral Dashboard

**URL:** http://localhost:3003/admin → Referral Program

**Funcționalități:**
- 📋 Lista toate referrals
- 💰 Track payments
- 🏆 Leaderboard
- 📊 Conversion statistics
- ✅ Approve/Complete referrals
- 📧 Send rewards

---

## 6. FINANCIAL TRACKING

### 6.1 Track Cost (Cheltuieli)

```powershell
curl -X POST http://localhost:8001/api/financial/track-cost `
  -H "Content-Type: application/json" `
  -d '{
    "category": "marketing",
    "amount": 500.00,
    "currency": "LEI",
    "description": "Facebook Ads - Campanie Septembrie",
    "date": "2025-09-30",
    "provider": "facebook_ads"
  }'
```

**Categorii cost:**
- `marketing` - Marketing și publicitate
- `video_generation` - Generare video (Pika, HeyGen)
- `social_media` - Social media tools
- `software` - Licențe software
- `infrastructure` - Servere, hosting
- `personnel` - Salarii, contractori

---

### 6.2 Track Revenue (Venituri)

```powershell
curl -X POST http://localhost:8001/api/financial/track-revenue `
  -H "Content-Type: application/json" `
  -d '{
    "amount": 5000.00,
    "currency": "LEI",
    "source": "crash_claim",
    "description": "Dosar daune Ion Popescu",
    "date": "2025-09-30",
    "lead_id": "uuid-lead"
  }'
```

**Surse revenue:**
- `crash_claim` - Dosare daune
- `insurance_dispute` - Dispute asigurări
- `consultation` - Consultanță
- `referral_bonus` - Bonusuri referral

---

### 6.3 ROI Analysis

```powershell
# ROI lunar
curl http://localhost:8001/api/financial/roi/monthly

# ROI zilnic
curl http://localhost:8001/api/financial/roi/daily

# ROI anual
curl http://localhost:8001/api/financial/roi/yearly
```

**Response:**
```json
{
  "period": "monthly",
  "total_revenue": 45000.00,
  "total_costs": 15000.00,
  "profit": 30000.00,
  "roi_percentage": 200.0,
  "cost_breakdown": {
    "marketing": 8000.00,
    "video_generation": 2000.00,
    "social_media": 1000.00,
    "infrastructure": 2000.00,
    "personnel": 2000.00
  },
  "revenue_breakdown": {
    "crash_claim": 35000.00,
    "insurance_dispute": 8000.00,
    "consultation": 2000.00
  }
}
```

---

### 6.4 Financial Dashboard

```powershell
curl http://localhost:8001/api/financial/dashboard
```

**Response:** Overview complet financiar

---

### 6.5 Cost per Lead

```powershell
curl -X POST http://localhost:8001/api/financial/calculate-cost/social-media `
  -H "Content-Type: application/json" `
  -d '{
    "posts_count": 30,
    "total_leads": 15,
    "ad_spend": 1000.00
  }'
```

---

### 6.6 Financial Dashboard UI

**URL:** http://localhost:3003/admin → Financial Dashboard

**Funcționalități:**
- 💰 Revenue vs Costs chart
- 📊 ROI tracking
- 📈 Profit/Loss statement
- 💳 Track expenses
- 🎯 Budget management
- 📉 Cost per lead analysis

---

## 7. WHATSAPP BOT

### 7.1 Send WhatsApp Message

```powershell
curl -X POST http://localhost:8001/api/whatsapp/send `
  -H "Content-Type: application/json" `
  -d '{
    "phone": "40712345678",
    "message": "Bună! Mulțumim pentru interes. Cum te putem ajuta?"
  }'
```

---

### 7.2 WhatsApp Webhook (Receive Messages)

**Endpoint:** `POST /api/whatsapp/webhook`

**Configurare în WhatsApp Business API:**
```
Webhook URL: https://your-domain.com/api/whatsapp/webhook
Verify Token: set in .env as WHATSAPP_VERIFY_TOKEN
```

**Procesare automată:**
- Detectează intent (claim inquiry, document upload, testimonial)
- Răspunde automat bazat pe intent
- Escalează la Manole dacă e nevoie
- Creează lead automat în sistem

---

### 7.3 WhatsApp Optimization

```powershell
curl -X POST http://localhost:8001/api/automation/whatsapp/optimize
```

**Ce face:**
- Analizează conversații
- Optimizează response time
- Identifică conversații de escalat
- Sugerează îmbunătățiri

---

## 8. AUTOMATION & SCHEDULING

### 8.1 Get Automation Status

```powershell
curl http://localhost:8001/api/automation/status
```

**Response:**
```json
{
  "enabled": true,
  "scheduler_running": true,
  "last_daily_cycle": "2025-09-30T09:00:00Z",
  "next_scheduled_post": "2025-09-30T15:00:00Z",
  "active_jobs": 3,
  "completed_today": 12,
  "failed_today": 1
}
```

---

### 8.2 Configure Schedule

```powershell
curl -X POST http://localhost:8001/api/automation/schedule/configure `
  -H "Content-Type: application/json" `
  -d '{
    "daily_posting_times": ["09:00", "15:00", "21:00"],
    "timezone": "Europe/Bucharest",
    "content_types": {
      "educational": 40,
      "testimonial": 30,
      "promotional": 30
    },
    "platforms": ["tiktok", "facebook", "instagram"],
    "auto_approve": false
  }'
```

---

### 8.3 Trigger Daily Cycle (Manual)

```powershell
curl -X POST http://localhost:8001/api/automation/daily-cycle/trigger
```

**Ce face:**
- Generează 3 video-uri noi (educational, testimonial, promotional)
- Schedule posts pentru zilele următoare
- Actualizează metrics
- Trimite raport email (dacă configurat)

---

### 8.4 Generate Video + Post Automat

```powershell
curl -X POST http://localhost:8001/api/automation/video/generate-and-post `
  -H "Content-Type: application/json" `
  -d '{
    "template_type": "educational",
    "platforms": ["tiktok", "instagram"],
    "schedule_for": "2025-09-30T18:00:00Z"
  }'
```

---

### 8.5 Automation Performance

```powershell
curl http://localhost:8001/api/automation/performance
```

**Metrics:**
- Total automated posts
- Success rate
- Avg engagement per post
- Cost per automated lead
- Time saved

---

### 8.6 Automation Dashboard UI

**URL:** http://localhost:3003/admin → Automation Control

**Funcționalități:**
- ⏯️ Start/Stop automation
- ⚙️ Configure schedule
- 📅 View scheduled tasks
- 🎬 Generate + post on-demand
- 📊 Performance metrics
- 🔔 Notifications settings

---

## 9. ANALYTICS & REPORTS

### 9.1 Overview Stats

```powershell
curl http://localhost:8001/api/test/mock-data
```

**Response:**
```json
{
  "leads": {"total": 150, "new": 45, "contacted": 60, "converted": 40},
  "financial": {"revenue": 50000, "costs": 15000, "roi": 233.3},
  "social": {"posts": 120, "views": 45000, "engagement": 3850},
  "videos": {"generated": 85, "avg_duration": 15},
  "referrals": {"total": 40, "completed": 25, "rewards_paid": 5000}
}
```

---

### 9.2 Growth Analytics

```powershell
curl http://localhost:8001/api/growth-analytics/dashboard
```

**Comprehensive metrics:**
- Lead growth rate
- Revenue growth
- Social media growth
- Engagement trends
- Conversion funnel
- Retention metrics

---

### 9.3 Growth Projections

```powershell
curl http://localhost:8001/api/growth-analytics/growth-projections
```

**AI-powered predictions:**
- Next 30 days leads forecast
- Revenue projection
- Optimal posting times
- Content type recommendations

---

### 9.4 Real-time Metrics

```powershell
curl http://localhost:8001/api/growth-analytics/real-time-metrics
```

**Live data:**
- Active users
- Current conversions
- Posts performance today
- Revenue today

---

### 9.5 Analytics Dashboard UI

**URL:** http://localhost:3003/admin → Growth Dashboard

**Vizualizări:**
- 📈 Lead funnel chart
- 💰 Revenue timeline
- 📊 Social media performance
- 🎯 Conversion rates
- 🔥 Viral content tracker
- 📉 Cost analysis

---

## 10. GROWTH ENGINE

### 10.1 Generate Mass Content

```powershell
curl -X POST http://localhost:8001/api/growth-engine/generate-mass-content `
  -H "Content-Type: application/json" `
  -d '{
    "video_count": 10,
    "content_types": ["educational", "testimonial", "promotional"],
    "target_platforms": ["tiktok", "instagram", "facebook"],
    "schedule_distribution": "optimal"
  }'
```

**Ce face:**
- Generează 10 video-uri diferite
- Optimizează pentru fiecare platformă
- Schedule automat la orele optime
- Track performance

---

### 10.2 Viral Boost Campaign

```powershell
curl -X POST http://localhost:8001/api/growth-engine/viral-boost `
  -H "Content-Type: application/json" `
  -d '{
    "budget": 1000.00,
    "duration_days": 7,
    "target_audience": "young_drivers",
    "platforms": ["tiktok", "instagram"]
  }'
```

**Strategie automată:**
- Identifică best performing content
- Boost cu buget dedicat
- A/B testing automat
- Real-time optimization

---

### 10.3 Growth Status

```powershell
curl http://localhost:8001/api/growth-engine/growth-status
```

---

## 11. ADMIN DASHBOARD

### 11.1 Login Admin

**URL:** http://localhost:3003/admin/login

**Credentials:** (configurează în Supabase Auth)

---

### 11.2 Main Dashboard

**URL:** http://localhost:3003/admin

**Secțiuni:**

#### 📊 Overview
- Total leads
- Revenue today/month
- Active automation tasks
- Recent activity

#### 👥 Lead Management
- Create, view, edit, delete leads
- Filter și search
- Export CSV
- Bulk actions

#### 🎬 Video Management
- Generate videos (toate tipurile)
- Preview videos
- Download/Delete
- Queue status

#### 📱 Social Media
- Schedule posts
- View analytics
- Manage platforms
- Content calendar

#### 💰 Financial
- Track revenue/costs
- ROI analysis
- Budget alerts
- Reports

#### 🔄 Automation
- Start/Stop automation
- Configure schedule
- View tasks
- Performance metrics

#### 🎯 Growth Analytics
- Funnel analysis
- Projections
- Recommendations
- A/B testing results

#### 👤 Referral Program
- Track referrals
- Leaderboard
- Approve payments
- Generate referral codes

---

## 12. API USAGE

### 12.1 Authentication (dacă activat)

```powershell
# Login
curl -X POST http://localhost:8001/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email": "admin@autopro.ro", "password": "your-password"}'

# Response: {"access_token": "jwt-token"}

# Folosește token în requests
curl http://localhost:8001/api/leads/ `
  -H "Authorization: Bearer jwt-token"
```

---

### 12.2 Rate Limiting

**Limits:**
- 5 requests / 60 secunde pentru video generation
- 120 requests / minut pentru alte endpoints

**Response când limită depășită:**
```json
{
  "ok": false,
  "error": "rate_limited",
  "retry_after": 60
}
```

**Headers:**
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
Retry-After: 60
```

---

### 12.3 Error Handling

**Standard error response:**
```json
{
  "ok": false,
  "error": "error_code",
  "message": "Human readable message",
  "details": {}
}
```

**Error codes:**
- `validation_error` - Invalid input
- `not_found` - Resource not found
- `database_error` - Database issue
- `rate_limited` - Too many requests
- `internal_error` - Server error

---

### 12.4 Pagination

```powershell
# Default: page 1, 20 items
curl http://localhost:8001/api/leads/

# Custom pagination
curl "http://localhost:8001/api/leads/?page=2&limit=50"
```

**Response format:**
```json
{
  "items": [...],
  "total": 150,
  "page": 2,
  "limit": 50,
  "pages": 3
}
```

---

### 12.5 API Documentation

**Swagger UI:** http://localhost:8001/docs
- Interactive API explorer
- Try endpoints în browser
- See request/response schemas

**ReDoc:** http://localhost:8001/redoc
- Clean documentation layout
- Downloadable OpenAPI spec

---

## 📞 COMENZI RAPIDE (CHEAT SHEET)

```powershell
# ===== SYSTEM =====
.\start.ps1                                    # Pornește tot
curl http://localhost:8001/health              # Health check
curl http://localhost:8001/docs                # API docs

# ===== LEADS =====
curl http://localhost:8001/api/leads/                                           # List leads
curl -X POST http://localhost:8001/api/leads/ -H "Content-Type: application/json" -d '{"name":"Test","phone":"0712345678","source":"direct"}'  # Create lead
curl http://localhost:8001/api/leads/{id}                                       # Get lead
curl -X PUT http://localhost:8001/api/leads/{id} -d '{"status":"contacted"}'    # Update lead

# ===== VIDEO =====
curl -X POST http://localhost:8001/api/simple-video/generate -d '{"text":"Test"}' # Generate video
curl http://localhost:8001/api/video/stats                                      # Video stats

# ===== SOCIAL =====
curl -X POST http://localhost:8001/api/social/post-now -d '{"content":"Test"}' # Post now
curl http://localhost:8001/api/social/analytics                                # Analytics

# ===== AUTOMATION =====
curl http://localhost:8001/api/automation/status                               # Status
curl -X POST http://localhost:8001/api/automation/daily-cycle/trigger         # Trigger cycle

# ===== FINANCIAL =====
curl http://localhost:8001/api/financial/dashboard                            # Dashboard
curl http://localhost:8001/api/financial/roi/monthly                          # ROI monthly

# ===== REFERRALS =====
curl http://localhost:8001/api/referrals/stats                                # Referral stats
curl -X POST http://localhost:8001/api/referrals/ -d '{"referrer_phone":"0712345678","referred_phone":"0723456789"}'  # Create referral
```

---

## 🆘 SUPPORT & TROUBLESHOOTING

### Common Issues:

**1. Backend nu pornește**
```powershell
cd services/api
pip install -r requirements.txt --force-reinstall
python -c "from app.main import app"
```

**2. Database connection failed**
- Check Supabase keys în `.env`
- Verify SQL schema rulat în Supabase
- Test connection: https://supabase.com/dashboard

**3. Frontend blank page**
```powershell
cd 02_FRONTEND_UI_CLEAN
rm -r node_modules
npm install
npm run dev
```

**4. Video generation fails**
- Check FFmpeg installed
- Verify output directory exists: `services/api/generated_videos/`
- Check logs pentru MoviePy errors

**5. Rate limit errors**
- Reducde request frequency
- Sau pornește Redis: `docker run -d -p 6379:6379 redis:alpine`

---

## 📚 RESURSE ADIȚIONALE

- **API Docs:** http://localhost:8001/docs
- **Frontend:** http://localhost:3003
- **Supabase Dashboard:** https://supabase.com/dashboard/project/orctxxpyiqzbordibqxi
- **System Status:** `SYSTEM_READY.md`
- **Technical Docs:** `CURSOR_AGENT_FULL_INSTRUCTIONS.md`

---

**Manual creat pentru AutoPro Daune v1.0**
**Pentru support: vezi logs în terminale sau check API docs**