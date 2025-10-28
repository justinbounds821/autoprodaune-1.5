# 🚀 AutoPro Daune - Lead Generation & Automation System

**Status:** ✅ PRODUCTION READY - Refactorizare Corectă În Curs  
**Version:** 3.0.0 (Refactoring)  
**Last Update:** 28 Octombrie 2025  
**Architecture:** Microservicii din cod existent (backwards compatible)

---

## 📖 DOCUMENTATION

### 🎯 Start Here
**👉 [MASTER_PROJECT_STATUS.md](MASTER_PROJECT_STATUS.md)** - Complete project overview, all TODOs, and implementation status

### 🔧 Technical Guides
- **[CURSOR_AGENT_FULL_INSTRUCTIONS.md](CURSOR_AGENT_FULL_INSTRUCTIONS.md)** - Complete setup & testing instructions
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment
- **[DEBUGGING_REPORT.md](DEBUGGING_REPORT.md)** - Troubleshooting guide
- **[MANUAL_UTILIZARE_COMPLET.md](MANUAL_UTILIZARE_COMPLET.md)** - User manual (Romanian)

### 🔑 Setup Guides
- **[SUPABASE_SETUP_INSTRUCTIONS.md](SUPABASE_SETUP_INSTRUCTIONS.md)** - Database setup
- **[HEYGEN_SETUP_GUIDE.md](HEYGEN_SETUP_GUIDE.md)** - Video generation API
- **[OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md)** - Social media OAuth
- **[YOUTUBE_SETUP.md](YOUTUBE_SETUP.md)** - YouTube API configuration
- **[CLOUDFLARE_R2_SETUP.md](CLOUDFLARE_R2_SETUP.md)** - Cloud storage

---

## 🚀 QUICK START

### ⚡ REFACTORIZARE CORECTĂ (Folosind cod existent)

**Arhitectură microservicii DIN codul existent - backwards compatible!**

```bash
# Start toate serviciile (hybrid)
docker-compose up -d

# SAU doar API original (backwards compatible)
docker-compose up -d api frontend redis

# SAU doar microservicii
docker-compose up -d core-api video-service frontend redis
```

**Read the guide:** [START_REFACTORIZARE_CORECTĂ.md](START_REFACTORIZARE_CORECTĂ.md)

**Architecture docs:** [REFACTORIZARE_CORECTĂ_3.0.md](REFACTORIZARE_CORECTĂ_3.0.md)

### Access Points
- 🌐 **Frontend:** http://localhost:3003
- 🔌 **API Original (toate routerele):** http://localhost:8001
- 💼 **Core API Microservice:** http://localhost:8002
- 🎬 **Video Service Microservice:** http://localhost:8003

---

### 🏛️ MONOLITH (Legacy)

**Old architecture (still works but not recommended for production):**

```powershell
# Start legacy monolith
.\scripts\start-all.ps1

# Or manually:
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
```

### Access Points (Legacy)
- 🌐 **Frontend:** http://localhost:3003
- 🔌 **Backend API:** http://localhost:8001/docs
- 🏥 **Health Check:** http://localhost:8001/health

---

## 📊 PROJECT STRUCTURE

```
autoprodaune-1/
├── services/api/              # Backend FastAPI (Python)
│   ├── app/                   # 138 API endpoints
│   ├── database/              # Supabase schema (11 tables)
│   └── requirements.txt
│
├── 02_FRONTEND_UI_CLEAN/      # Frontend React + Vite
│   ├── src/                   # 12 pages, 60+ components
│   ├── package.json
│   └── vite.config.ts         # Port 3003, proxy to 8001
│
├── monitoring/                # Prometheus + Grafana
├── scripts/                   # Helper scripts
├── _BACKUP_OLD_PROJECT/       # Old code backup
└── _OLD_DOCS/                 # Archived documentation
```

---

## ✅ FEATURES

### Core Features (100% Complete)
- ✅ **Lead Management** - CRM with scoring, timeline, bulk operations
- ✅ **Video Generation** - MoviePy + Edge-TTS + HeyGen integration
- ✅ **Social Media** - TikTok, Instagram, YouTube automation
- ✅ **WhatsApp Bot** - Business API integration
- ✅ **Financial Dashboard** - Revenue/Cost tracking with CSV export
- ✅ **Automation** - Daily scheduling (3x/day)
- ✅ **Referral System** - 200 LEI rewards

### In Progress (18.6% Complete - 13/70 TODOs)
- 🚧 Real-time dashboard updates
- 🚧 Advanced charts (Recharts)
- 🚧 Email/SMS notifications
- 🚧 File attachments
- 🚧 Conversion funnel
- 🚧 AI insights

**See [MASTER_PROJECT_STATUS.md](MASTER_PROJECT_STATUS.md) for complete TODO list**

---

## 🛠️ TECH STACK

### Backend
- FastAPI 0.111.0
- Python 3.13
- Supabase (PostgreSQL)
- Redis (optional)
- MoviePy, OpenCV, PIL
- Edge-TTS / ElevenLabs

### Frontend
- React 18.3.1
- Vite 5.4.19
- TypeScript 5
- Tailwind CSS + Shadcn UI
- TanStack Query
- React Router 6

---

## 🔧 CONFIGURATION

### Backend (.env in `services/api/`)
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
PORT=8001
BACKEND_CORS_ORIGINS=http://localhost:3003
```

### Frontend (.env in `02_FRONTEND_UI_CLEAN/`)
```env
VITE_API_URL=http://localhost:8001
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

---

## 🧪 TESTING

### Health Check
```powershell
curl http://localhost:8001/health
# Expected: {"status":"ok","service":"autopro-daune","port":8001}
```

### API Documentation
Visit: http://localhost:8001/docs (Swagger UI)

---

## 📈 PROGRESS

| Metric | Status |
|--------|--------|
| **Overall Completion** | 93% Production Ready |
| **TODOs Complete** | 13/70 (18.6%) |
| **Backend Endpoints** | 138 active |
| **Database Tables** | 11 configured |
| **Frontend Pages** | 12 functional |
| **Linter Errors** | 0 ✅ |

---

## 🐛 KNOWN ISSUES

1. ⚠️ **Redis Warning**: Falls back to in-memory (OK for dev)
2. 💡 **Social API Keys**: Need production keys for TikTok/Instagram
3. 📊 **Charts**: Need Recharts integration for advanced visualizations

See [DEBUGGING_REPORT.md](DEBUGGING_REPORT.md) for solutions.

---

## 📞 SUPPORT

For detailed information, see:
- **Complete Status:** [MASTER_PROJECT_STATUS.md](MASTER_PROJECT_STATUS.md)
- **Setup Guide:** [CURSOR_AGENT_FULL_INSTRUCTIONS.md](CURSOR_AGENT_FULL_INSTRUCTIONS.md)
- **Troubleshooting:** [DEBUGGING_REPORT.md](DEBUGGING_REPORT.md)

---

**AutoPro Daune** - Automated Lead Generation & Social Media System  
**License:** Proprietary  
**Maintained by:** AutoPro Daune Development Team
