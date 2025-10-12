# 🚗 AutoPro Daune - Automated Claims Management System

> **Versiune:** 1.5.0  
> **Data:** 10 Octombrie 2025  
> **Status:** Production Ready ✅

## 📋 Cuprins

- [Despre Proiect](#despre-proiect)
- [Arhitectura Sistemului](#arhitectura-sistemului)
- [Instalare Rapidă](#instalare-rapid%C4%83)
- [Utilizare](#utilizare)
- [Structura Proiectului](#structura-proiectului)
- [Documentație API](#documenta%C8%9Bie-api)
- [Depanare](#depanare)

---

## 🎯 Despre Proiect

**AutoPro Daune** este un sistem complet automatizat pentru gestionarea despăgubirilor auto, care include:

### ✨ Funcționalități Principale

- **🎬 Generare Automată de Video** - Creează conținut video educațional și promoțional folosind AI
- **📱 Social Media Automation** - Postare automată pe TikTok, Instagram, YouTube, Facebook
- **💰 Management Financiar** - Tracking complet al veniturilor, costurilor și profitabilității
- **👥 Gestionare Lead-uri** - Sistem avansat de urmărire și conversie a clienților
- **🤖 Automatizare Completă** - Task-uri programate pentru toate procesele
- **📊 Dashboard Admin** - Interfață intuitivă pentru monitorizare și control
- **🧠 AI Insights** - Analiză inteligentă și recomandări automate

### 🛠️ Tehnologii Utilizate

**Backend:**
- Python 3.10+
- FastAPI (REST API)
- Supabase (PostgreSQL)
- Redis (Rate Limiting)
- OpenAI API (AI Generation)
- ElevenLabs (Voice Synthesis)
- HeyGen (Video AI)

**Frontend:**
- React 18 + TypeScript
- Vite (Build Tool)
- Tailwind CSS + shadcn/ui
- React Router
- Axios
- React Query

**Infrastructure:**
- Cloudflare R2 (CDN Storage)
- GitHub Actions (CI/CD)
- Docker (Containerization)

---

## 🏗️ Arhitectura Sistemului

### Structura Logică

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND (React)                   │
│              http://localhost:3007                   │
└───────────────────────┬─────────────────────────────┘
                        │ API Calls
                        ↓
┌─────────────────────────────────────────────────────┐
│              BACKEND API (FastAPI)                   │
│              http://localhost:8001                   │
│                                                       │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   Routes    │  │   Services   │  │  Database  │ │
│  │             │→ │              │→ │            │ │
│  │ /api/leads  │  │ Lead Mgmt    │  │  Supabase  │ │
│  │ /api/video  │  │ Video Gen    │  │            │ │
│  │ /api/social │  │ Social Media │  │            │ │
│  │ /api/...    │  │ ...          │  │            │ │
│  └─────────────┘  └──────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────┐
│              EXTERNAL SERVICES                       │
│                                                       │
│  • OpenAI (GPT-4)        • ElevenLabs (Voice)       │
│  • HeyGen (Video AI)     • Cloudflare R2 (CDN)      │
│  • TikTok API            • Instagram API             │
│  • YouTube API           • Facebook API              │
└─────────────────────────────────────────────────────┘
```

### Flow de Date

```
1. LEADS:     Landing Page → POST /api/leads → Database → Notification

2. VIDEOS:    Automation → Video Service → HeyGen/Internal → CDN → Database

3. SOCIAL:    Video Ready → Social Service → Platform APIs → Analytics → Database

4. FINANCIAL: Revenue/Costs → Database → Dashboard → Reports
```

---

## 🚀 Instalare Rapidă

### Prerequisite

1. **Python 3.10+**
   ```bash
   python --version
   ```

2. **Node.js 18+**
   ```bash
   node --version
   ```

3. **Git**
   ```bash
   git --version
   ```

### Pași de Instalare

#### 1. Clone Repository
```bash
git clone <repository-url>
cd autoprodaune-1.5
```

#### 2. Configurare Environment Variables

**Backend** (`services/api/.env`):
```env
# Supabase
SUPABASE_URL=https://yfbhmbjtauhxgalvdfns.supabase.co
SUPABASE_KEY=your_supabase_key

# OpenAI
OPENAI_API_KEY=your_openai_key

# ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_key

# HeyGen
HEYGEN_API_KEY=your_heygen_key

# Cloudflare R2
R2_ACCOUNT_ID=your_r2_account_id
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=your_bucket_name

# Social Media APIs (optional)
TIKTOK_CLIENT_KEY=your_tiktok_key
TIKTOK_CLIENT_SECRET=your_tiktok_secret
```

**Frontend** (`02_FRONTEND_UI_CLEAN/.env`):
```env
VITE_API_BASE_URL=http://localhost:8001
VITE_SUPABASE_URL=https://yfbhmbjtauhxgalvdfns.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

#### 3. Rulare Automată (Recomandat)

```powershell
.\START_SYSTEM.ps1
```

Acest script va:
- ✅ Verifica prerequisites
- ✅ Instala dependințele
- ✅ Porni backend-ul (port 8001)
- ✅ Porni frontend-ul (port 3007)
- ✅ Deschide browser-ul

#### 4. Oprire Sistem

```powershell
.\STOP_SYSTEM.ps1
```

---

## 📖 Utilizare

### Accesare Aplicație

După pornire, accesează:

- **Frontend:** http://localhost:3007
- **Admin Panel:** http://localhost:3007/admin
- **API Docs:** http://localhost:8001/docs
- **API Health:** http://localhost:8001/health

### Pagini Principale

#### 1. **Landing Page** (`/`)
- Lead generation form
- Company presentation
- Statistics showcase

#### 2. **Admin Dashboard** (`/admin/dashboard`)
- **Overview general** al sistemului
- KPIs principale
- Notificări
- Link-uri rapide către module

#### 3. **Leads Management** (`/admin/leads`)
- Lista completă de lead-uri
- Filtrare și search
- Editare status
- Statistici conversie

#### 4. **Video Management** (`/admin/videos`)
- Job-uri video (pending, processing, completed)
- Upload custom backgrounds/avatars
- Video templates
- Cost tracking

#### 5. **Social Media** (`/admin/social`)
- Summary pe platforme (TikTok, Instagram, YouTube, Facebook)
- Lista postări
- Analytics și engagement
- Schedule posting

#### 6. **Financial Dashboard** (`/admin/financial`)
- Revenue tracking
- Cost management
- Profit margins
- Invoice & payments
- Tax calculations

#### 7. **Automation Control** (`/admin/automation`)
- Enable/disable automation
- Task scheduling
- Logs și monitoring
- Configuration settings

#### 8. **Assets Manager** (`/admin/assets`)
- Upload backgrounds pentru video
- Upload avatare AI
- Manage existing assets
- CDN integration

---

## 📁 Structura Proiectului

```
autoprodaune-1.5/
│
├── 📂 services/api/              # Backend (FastAPI)
│   ├── app/
│   │   ├── main.py               # Entry point
│   │   ├── routes/               # API endpoints
│   │   │   ├── leads.py
│   │   │   ├── video.py
│   │   │   ├── social.py
│   │   │   ├── financial.py
│   │   │   └── ...
│   │   ├── services/             # Business logic
│   │   │   ├── supabase_client.py
│   │   │   ├── openai_service.py
│   │   │   ├── video_service.py
│   │   │   └── ...
│   │   └── models/               # Data models
│   ├── requirements.txt
│   └── .env
│
├── 📂 02_FRONTEND_UI_CLEAN/      # Frontend (React)
│   ├── src/
│   │   ├── pages/                # React pages
│   │   │   ├── Dashboard.tsx
│   │   │   ├── AdminApp.tsx
│   │   │   ├── VideoManagement.tsx
│   │   │   ├── SocialMedia.tsx
│   │   │   └── ...
│   │   ├── components/           # React components
│   │   ├── services/             # API clients
│   │   │   └── autoproApi.ts
│   │   └── lib/                  # Utils
│   ├── package.json
│   └── .env
│
├── 📂 .github/workflows/         # CI/CD
│   ├── ci-cd.yml
│   └── docker.yml
│
├── 📄 database_schema_complete.sql    # Database schema
├── 📄 API_ENDPOINTS_DOCUMENTATION.md  # API documentation
├── 📄 START_SYSTEM.ps1                # Startup script
├── 📄 STOP_SYSTEM.ps1                 # Stop script
└── 📄 README.md                       # This file
```

---

## 📚 Documentație API

Documentația completă a endpoint-urilor se găsește în:
- **`API_ENDPOINTS_DOCUMENTATION.md`** - Documentație detaliată
- **http://localhost:8001/docs** - Swagger UI (interactiv)
- **http://localhost:8001/redoc** - ReDoc (documentație elegantă)

### Endpoints Principale

| Modul | Endpoint | Metodă | Descriere |
|-------|----------|--------|-----------|
| **Health** | `/health` | GET | Health check |
| **Leads** | `/api/leads/` | GET/POST | Manage leads |
| **Financial** | `/api/financial/dashboard` | GET | Financial overview |
| **Social** | `/api/social/summary` | GET | Social media summary |
| **Video** | `/api/video/stats` | GET | Video statistics |
| **Automation** | `/api/automation/status` | GET | Automation status |

---

## 🔧 Depanare

### Probleme Comune

#### 1. Backend nu pornește
```bash
# Verifică dacă portul 8001 este ocupat
netstat -an | Select-String "8001"

# Oprește procesul existent
Get-NetTCPConnection -LocalPort 8001 | Select-Object -ExpandProperty OwningProcess | Stop-Process -Force
```

#### 2. Frontend nu pornește
```bash
# Șterge node_modules și reinstalează
cd 02_FRONTEND_UI_CLEAN
Remove-Item -Recurse -Force node_modules
npm install
```

#### 3. Erori de conexiune la API
```bash
# Verifică dacă backend rulează
Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing

# Verifică .env frontend
cat 02_FRONTEND_UI_CLEAN\.env
```

#### 4. Database connection failed
- Verifică `SUPABASE_URL` și `SUPABASE_KEY` în `.env`
- Asigură-te că Supabase project este activ
- Rulează `database_schema_complete.sql` pentru a crea tabelele

### Logs

- **Backend Logs:** Afișate în consola PowerShell unde rulează backend-ul
- **Frontend Logs:** Browser Console (F12) + PowerShell console
- **Database Logs:** Supabase Dashboard → Logs

---

## 🧪 Testing

### Manual Testing

1. **Health Check:**
   ```bash
   curl http://localhost:8001/health
   ```

2. **Create Lead:**
   ```bash
   curl -X POST http://localhost:8001/api/leads/ \
     -H "Content-Type: application/json" \
     -d '{"name":"Test User","phone":"0721234567","email":"test@example.com"}'
   ```

3. **Get Social Summary:**
   ```bash
   curl http://localhost:8001/api/social/summary
   ```

### Automated Tests (CI/CD)

```bash
# Backend tests
cd services/api
pytest

# Frontend tests
cd 02_FRONTEND_UI_CLEAN
npm test
```

---

## 🚀 Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Production Checklist

- [ ] Update `.env` with production values
- [ ] Configure CORS for production domain
- [ ] Set up SSL certificates
- [ ] Configure CDN for static assets
- [ ] Enable production logging
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

---

## 📞 Support

Pentru întrebări sau probleme:

1. **Check Documentation:** `API_ENDPOINTS_DOCUMENTATION.md`
2. **Check Logs:** Backend/Frontend console output
3. **Database Schema:** `database_schema_complete.sql`
4. **GitHub Issues:** Creează un issue în repository

---

## 📝 License

Proprietary - AutoPro Daune © 2025

---

## 🎉 Contributors

- **Development Team** - Initial work and ongoing maintenance
- **AI Integration** - OpenAI, ElevenLabs, HeyGen integration
- **Infrastructure** - Supabase, Cloudflare setup

---

**Last Updated:** 10 Octombrie 2025  
**Version:** 1.5.0  
**Status:** ✅ Production Ready
