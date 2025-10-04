# 🤖 CURSOR AGENT - INSTRUCȚIUNI COMPLETE DE ANALIZĂ ȘI RULARE

## 📋 CONTEXT PROIECT

**Nume:** AutoPro Daune - Lead Generation & Automation System
**Status:** ✅ FUNCTIONAL - Ready for production
**Data:** 2025-09-30

---

## 🎯 MISIUNEA TA (CURSOR AGENT)

1. **Analizează COMPLET** tot proiectul
2. **Identifică** toate componentele funcționale
3. **Testează** fiecare sistem
4. **Documentează** ce funcționează și ce nu
5. **Sugerează** îmbunătățiri și optimizări

---

## 📁 STRUCTURA PROIECTULUI

```
autoprodaune-1/
│
├── services/api/                    # 🔴 BACKEND - FastAPI Python
│   ├── app/
│   │   ├── main.py                 # Entry point - 138 routes
│   │   ├── routes/                 # API endpoints (20+ routers)
│   │   ├── services/               # Business logic
│   │   ├── core/                   # Database, monitoring, config
│   │   └── schemas/                # Pydantic models
│   ├── database/
│   │   └── supabase_schema.sql    # 🔴 IMPORTANT: Rulează asta în Supabase
│   ├── requirements.txt            # Python dependencies
│   └── .env                        # Environment variables
│
├── 02_FRONTEND_UI_CLEAN/            # 🔵 FRONTEND - React + Vite
│   ├── src/
│   │   ├── pages/                  # Dashboard pages (10+)
│   │   ├── components/             # React components
│   │   ├── services/               # API client (autoproApi.ts)
│   │   └── types/                  # TypeScript types
│   ├── package.json                # Node dependencies
│   ├── vite.config.ts             # Vite config (port 3003, proxy to 8001)
│   └── .env                        # Frontend env vars
│
├── monitoring/                      # 🟡 OPTIONAL - Prometheus/Grafana
│   ├── prometheus.yml
│   ├── grafana-dashboard.json
│   └── alert_rules.yml
│
├── scripts/                         # 🟢 HELPER SCRIPTS
│   ├── start-backend.ps1
│   ├── start-frontend.ps1
│   └── start-all.ps1
│
├── start.ps1                       # 🚀 MAIN STARTUP SCRIPT
├── README.md                        # Documentation
├── SYSTEM_READY.md                 # Status report
└── _BACKUP_OLD_PROJECT/            # Backup old code (ignore)
```

---

## 🔴 BACKEND - FastAPI (services/api/)

### Tech Stack:
- **Framework:** FastAPI 0.111.0
- **Python:** 3.13
- **Database:** Supabase (PostgreSQL)
- **Video:** MoviePy 2.2.1, PIL/Pillow, FFmpeg
- **Cache/Rate Limit:** Redis (optional)
- **Monitoring:** Prometheus

### Key Files:
- `app/main.py` - Main application (138 routes)
- `app/core/database.py` - Supabase integration
- `app/core/monitoring.py` - Prometheus metrics
- `app/services/video_generator.py` - Video generation
- `app/services/social_poster.py` - Social media automation

### Environment Variables (.env):
```env
# Supabase (CRITICAL)
SUPABASE_URL=https://orctxxpyiqzbordibqxi.supabase.co
SUPABASE_ANON_KEY=sb_publishable_7Qh8xZcxTp5tLb87ezr5tg_s2_cw0uj
SUPABASE_SERVICE_KEY=sb_secret_I0Kvv13Pn05qPDsTQvJWmw_DtVHPQPz

# Server
PORT=8001
BACKEND_CORS_ORIGINS=http://localhost:3003,http://127.0.0.1:3003

# Redis (optional)
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379

# Automation
AUTOMATION_ENABLED=true
```

### API Endpoints (138 total):

#### Core Routes:
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - Swagger UI
- `GET /metrics` - Prometheus metrics

#### Lead Management:
- `GET /api/leads/` - List leads
- `POST /api/leads/` - Create lead
- `GET /api/leads/{lead_id}` - Get lead details
- `PUT /api/leads/{lead_id}` - Update lead
- `DELETE /api/leads/{lead_id}` - Delete lead

#### Video Generation:
- `POST /api/video/generate` - Generate video
- `POST /api/simple-video/generate` - Simple video
- `POST /api/professional-video/generate` - Professional video
- `POST /api/advanced-video/generate` - Advanced video with avatars
- `GET /api/video/stats` - Video statistics

#### Social Media:
- `GET /api/social/summary` - Social media overview
- `POST /api/social/post-now` - Post immediately
- `GET /api/social/posts` - List posts
- `POST /api/social/posts` - Create post
- `GET /api/social/analytics` - Social analytics

#### Automation:
- `GET /api/automation/status` - Automation status
- `POST /api/automation/schedule/configure` - Configure schedule
- `POST /api/automation/video/generate-and-post` - Generate + post
- `POST /api/automation/daily-cycle/trigger` - Trigger daily cycle
- `GET /api/automation/performance` - Performance metrics

#### Financial:
- `POST /api/financial/track-cost` - Track cost
- `POST /api/financial/track-revenue` - Track revenue
- `GET /api/financial/roi/{period}` - ROI analysis
- `GET /api/financial/dashboard` - Financial dashboard

#### Referrals:
- `GET /api/referrals/` - List referrals
- `POST /api/referrals/` - Create referral
- `GET /api/referrals/stats` - Referral statistics
- `PUT /api/referrals/{referral_id}/complete` - Complete referral

#### WhatsApp:
- `POST /api/whatsapp/webhook` - WhatsApp webhook
- `POST /api/whatsapp/send` - Send WhatsApp message

#### Growth Engine (NEW):
- `POST /api/growth-engine/generate-mass-content` - Mass content
- `GET /api/growth-engine/growth-analytics` - Growth analytics
- `POST /api/growth-engine/viral-boost` - Viral boost

#### Intelligent Conversion (NEW):
- `POST /api/intelligent-conversion/analyze-lead` - AI lead scoring
- `POST /api/intelligent-conversion/execute-conversion-actions` - Auto actions
- `GET /api/intelligent-conversion/conversion-analytics` - Analytics

#### Customer Nurturing (NEW):
- `POST /api/customer-nurturing/start-nurturing-journey` - Start journey
- `POST /api/customer-nurturing/mass-nurturing-activation` - Mass activation
- `GET /api/customer-nurturing/nurturing-analytics` - Analytics

#### Affiliate System (NEW):
- `POST /api/affiliate-multiplication/create-affiliate` - Create affiliate
- `GET /api/affiliate-multiplication/affiliate-leaderboard` - Leaderboard
- `POST /api/affiliate-multiplication/viral-boost-campaign` - Viral campaign

### Database Schema (Supabase):

**IMPORTANT:** Rulează acest SQL în Supabase Dashboard → SQL Editor:
```
services/api/database/supabase_schema.sql
```

**Tabele create:**
1. `leads` - Lead management
2. `referrals` - Referral system (200 LEI)
3. `social_posts` - Social media tracking
4. `video_jobs` - Video generation queue
5. `whatsapp_conversations` - WhatsApp bot
6. `whatsapp_messages` - Message tracking
7. `document_uploads` - File uploads
8. `automation_config` - Automation settings
9. `content_templates` - Video templates
10. `performance_metrics` - Analytics
11. `system_logs` - Audit trail

---

## 🔵 FRONTEND - React (02_FRONTEND_UI_CLEAN/)

### Tech Stack:
- **Framework:** React 18.3.1
- **Build Tool:** Vite 5.4.19
- **UI Library:** Shadcn UI (Radix UI + TailwindCSS)
- **Router:** React Router 6.30.1
- **State:** React Query (TanStack Query)
- **HTTP Client:** Axios
- **Supabase:** @supabase/supabase-js

### Pages:
1. `Landing.tsx` - Landing page
2. `Dashboard.tsx` - Main dashboard
3. `LeadManagement.tsx` - Lead management
4. `VideoManagement.tsx` - Video generation
5. `SocialMedia.tsx` - Social media control
6. `FinancialDashboard.tsx` - Financial tracking
7. `GrowthDashboard.tsx` - Growth analytics
8. `AutomationControl.tsx` - Automation settings
9. `Referral.tsx` - Referral program
10. `Community.tsx` - Community features
11. `AdminLogin.tsx` - Admin authentication
12. `AdminApp.tsx` - Admin panel

### Key Components:
- `components/admin/` - Admin UI components
- `components/__tests__/` - Component tests
- `services/autoproApi.ts` - API client (main interface)
- `hooks/useAdminAuth.ts` - Admin authentication
- `hooks/useApiHealth.ts` - API health check

### Environment Variables (.env):
```env
# API Configuration
VITE_API_URL=http://localhost:8001
VITE_API_BASE_URL=http://localhost:8001

# Supabase (Frontend)
VITE_SUPABASE_URL=https://orctxxpyiqzbordibqxi.supabase.co
VITE_SUPABASE_ANON_KEY=sb_publishable_7Qh8xZcxTp5tLb87ezr5tg_s2_cw0uj

# Development
VITE_ENV=development
VITE_DEBUG=true
```

### Vite Config:
```typescript
// Port 3003
// Proxy /api → http://127.0.0.1:8001
```

---

## 🚀 INSTRUCȚIUNI DE RULARE - CAP-COADĂ

### PASUL 1: Verifică Prerequisites

```powershell
# Check Python
python --version  # Should be 3.13+

# Check Node
node --version    # Should be 18+
npm --version

# Check Git
git --version
```

### PASUL 2: Setup Database (Supabase)

1. **Mergi la:** https://supabase.com/dashboard
2. **Login** cu contul tau
3. **Selectează proiectul:** orctxxpyiqzbordibqxi
4. **Click:** SQL Editor (left sidebar)
5. **Click:** New Query
6. **Copiază tot conținutul din:**
   ```
   C:\Users\JJ\Desktop\autopro_daune\autoprodaune-1\services\api\database\supabase_schema.sql
   ```
7. **Paste** în SQL Editor
8. **Click:** RUN (bottom right)
9. **Verifică:** Table Editor → Ar trebui să vezi 11 tabele noi

**Confirmare:**
```sql
-- Rulează asta pentru verificare:
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

Ar trebui să vezi:
- automation_config ✅
- content_templates ✅
- document_uploads ✅
- leads ✅
- performance_metrics ✅
- referrals ✅
- social_posts ✅
- system_logs ✅
- video_jobs ✅
- whatsapp_conversations ✅
- whatsapp_messages ✅

### PASUL 3: Setup Backend

```powershell
# Navighează la backend
cd C:\Users\JJ\Desktop\autopro_daune\autoprodaune-1\services\api

# Verifică .env există
ls .env

# Install dependencies (dacă nu sunt deja instalate)
pip install -r requirements.txt

# Test import
python -c "from app.main import app; print('Backend OK')"

# Pornește serverul
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

**Expected Output:**
```
INFO:     ✅ Prometheus metrics configured
WARNING:  ⚠️ Redis connection failed (OK - folosim in-memory)
INFO:     ✅ All main routers loaded successfully
INFO:     ✅ Video router loaded
INFO:     ✅ Database connection verified
INFO:     ✅ Automation scheduler started
INFO:     ✅ AutoPro Daune API started with 138 routes
INFO:     Application startup complete
INFO:     Uvicorn running on http://127.0.0.1:8001
```

**Test endpoints:**
```powershell
# Într-un nou terminal:
curl http://localhost:8001/health
# Should return: {"status":"ok","service":"autopro-daune","port":8001}

curl http://localhost:8001/api/leads/
# Should return: {"items":[],"total":0,...}
```

### PASUL 4: Setup Frontend

```powershell
# ÎNTR-UN NOU TERMINAL (lasă backend-ul să ruleze)
cd C:\Users\JJ\Desktop\autopro_daune\autoprodaune-1\02_FRONTEND_UI_CLEAN

# Verifică .env
ls .env

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Expected Output:**
```
VITE v5.4.19  ready in 2341 ms

➜  Local:   http://localhost:3003/
➜  Network: use --host to expose
➜  press h + enter to show help
```

**Test în browser:**
1. Deschide: http://localhost:3003
2. Ar trebui să vezi Landing Page
3. Click: "Admin" sau mergi la http://localhost:3003/admin
4. Verifică: Dashboard loads, API calls funcționează

### PASUL 5: Test Complete System

```powershell
# Test 1: Health Check
curl http://localhost:8001/health

# Test 2: Create Lead
curl -X POST http://localhost:8001/api/leads/ `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"Test Lead\",\"phone\":\"0712345678\",\"source\":\"direct\"}'

# Test 3: Get Leads
curl http://localhost:8001/api/leads/

# Test 4: Automation Status
curl http://localhost:8001/api/automation/status

# Test 5: Social Summary
curl http://localhost:8001/api/social/summary
```

### PASUL 6: Test Video Generation

```powershell
# Simple Video Test
curl -X POST http://localhost:8001/api/simple-video/generate `
  -H "Content-Type: application/json" `
  -d '{\"text\":\"Test AutoPro Daune\",\"duration\":5}'

# Check generated videos
dir services\api\generated_videos\simple\
```

### PASUL 7: Verifică Logs

**Backend logs:** Vezi în terminalul unde rulează backend-ul
**Frontend logs:** Vezi în browser console (F12)

**Expected în backend logs:**
- ✅ Database connection verified
- ✅ All routers loaded
- ✅ Automation scheduler started
- ⚠️ Redis connection failed (OK)
- ℹ️ API requests logging

---

## 🎯 METODA AUTOMATĂ (UN SINGUR SCRIPT)

```powershell
# Pornește tot dintr-o comandă
cd C:\Users\JJ\Desktop\autopro_daune\autoprodaune-1
.\start.ps1
```

Asta deschide 2 terminale:
1. **Terminal 1:** Backend pe 8001
2. **Terminal 2:** Frontend pe 3003

**Așteaptă 10-15 secunde** până pornesc ambele, apoi:
- Frontend: http://localhost:3003
- Backend: http://localhost:8001/docs

---

## 📊 CHECKLIST VALIDARE SISTEM

### Backend Validation:
- [ ] Server pornește fără erori critice
- [ ] 138 routes loaded successfully
- [ ] Database connection OK
- [ ] Swagger UI accessible: http://localhost:8001/docs
- [ ] Health endpoint: http://localhost:8001/health
- [ ] Metrics endpoint: http://localhost:8001/metrics
- [ ] Lead creation works
- [ ] Video generation works
- [ ] Social media endpoints respond

### Frontend Validation:
- [ ] Dev server pornește pe port 3003
- [ ] Landing page loads
- [ ] Admin dashboard accessible
- [ ] API calls succeed (check Network tab)
- [ ] Lead management UI works
- [ ] Video management UI works
- [ ] No console errors (except warnings OK)

### Database Validation:
- [ ] 11 tabele create în Supabase
- [ ] Leads table accessible
- [ ] automation_config exists (fix pentru warning)
- [ ] performance_metrics exists (fix pentru error)
- [ ] RLS policies active
- [ ] Indexes created

### Integration Validation:
- [ ] Frontend → Backend communication OK
- [ ] Backend → Supabase communication OK
- [ ] Video generation produces files
- [ ] Automation scheduler running
- [ ] Logs being written to system_logs table

---

## 🤖 CURSOR AGENT - TASKURI DE ANALIZĂ

### Task 1: Code Quality Analysis
```
Analizează:
- services/api/app/main.py
- services/api/app/routes/* (toate router-ele)
- 02_FRONTEND_UI_CLEAN/src/pages/* (toate page-urile)
- 02_FRONTEND_UI_CLEAN/src/services/autoproApi.ts

Raportează:
- Code quality issues
- Security vulnerabilities
- Performance bottlenecks
- Best practices violations
- Technical debt
```

### Task 2: Dependencies Audit
```
Verifică:
- services/api/requirements.txt - outdated packages?
- 02_FRONTEND_UI_CLEAN/package.json - vulnerabilities?
- Conflicting versions?
- Missing dependencies?

Sugerează:
- Update strategy
- Alternative packages
- Optimization opportunities
```

### Task 3: API Coverage Analysis
```
Verifică:
- Toate cele 138 endpoints
- Request/Response validation
- Error handling
- Rate limiting
- Authentication/Authorization
- Documentation completeness

Raportează:
- Endpoints fără tests
- Missing error handlers
- Incomplete documentation
```

### Task 4: Database Schema Review
```
Analizează:
- services/api/database/supabase_schema.sql
- Table relationships
- Index efficiency
- Query optimization opportunities
- Missing constraints
- Data integrity

Sugerează:
- Schema improvements
- Performance optimizations
- Migration strategy
```

### Task 5: Frontend Architecture
```
Analizează:
- Component structure
- State management
- API integration patterns
- Error handling
- Loading states
- User experience

Sugerează:
- Refactoring opportunities
- Performance improvements
- UX enhancements
```

### Task 6: Video Generation Pipeline
```
Verifică:
- services/api/app/services/video_generator.py
- services/api/app/routes/video.py
- services/api/app/routes/simple_video.py
- services/api/app/routes/professional_video.py
- services/api/app/routes/advanced_video.py

Testează:
- All video generation endpoints
- Output quality
- Processing time
- Error handling
- Queue management

Raportează:
- Issues
- Optimization opportunities
- Feature gaps
```

### Task 7: Social Media Integration
```
Analizează:
- services/api/app/services/social_poster.py
- services/api/app/services/instagram/
- services/api/app/services/tiktok_poster.py
- services/api/app/routes/social.py

Verifică:
- API integrations active?
- Credentials configured?
- Posting works?
- Analytics tracking?

Raportează:
- Integration status
- Missing features
- Error handling
```

### Task 8: Automation System
```
Verifică:
- services/api/app/services/automation_scheduler.py
- services/api/app/routes/automation.py
- Scheduler running?
- Tasks executing?
- Performance monitoring?

Testează:
- Daily cycle trigger
- Video generation + post
- WhatsApp optimization
- Performance tracking

Raportează:
- System health
- Reliability issues
- Improvements needed
```

### Task 9: Security Audit
```
Scanează pentru:
- SQL injection vulnerabilities
- XSS vulnerabilities
- CSRF protection
- Authentication weaknesses
- API key exposure
- Sensitive data logging
- Input validation gaps

Raportează:
- Security issues (priority order)
- Remediation steps
```

### Task 10: Performance Analysis
```
Măsoară:
- API response times
- Database query performance
- Video generation speed
- Frontend load time
- Bundle size

Identifică:
- Slow endpoints
- N+1 queries
- Memory leaks
- Unnecessary re-renders

Sugerează:
- Caching strategies
- Query optimization
- Code splitting
- Lazy loading
```

---

## 📝 FORMAT RAPORT FINAL (pentru Cursor Agent)

```markdown
# AutoPro Daune - Raport Complet de Analiză

## Executive Summary
- Overall health score: X/100
- Critical issues: X
- Warnings: X
- Recommendations: X

## 1. Backend Analysis (services/api/)
### Code Quality: X/100
- Issues found: [list]
- Recommendations: [list]

### API Endpoints: X/138 functional
- Working: [list top 10]
- Broken: [list]
- Needs testing: [list]

### Dependencies: X outdated
- Critical updates: [list]
- Optional updates: [list]

## 2. Frontend Analysis (02_FRONTEND_UI_CLEAN/)
### Code Quality: X/100
- Issues found: [list]
- Recommendations: [list]

### UI/UX: X/100
- Working pages: [list]
- Broken pages: [list]
- Performance issues: [list]

## 3. Database Schema
### Health: X/100
- Tables status: [list]
- Index optimization: [suggestions]
- Query performance: [analysis]

## 4. Integration Tests
### Backend ↔ Database: [PASS/FAIL]
### Frontend ↔ Backend: [PASS/FAIL]
### External APIs: [status]

## 5. Security Audit
### Critical: [issues]
### High: [issues]
### Medium: [issues]
### Low: [issues]

## 6. Performance Metrics
- API avg response time: Xms
- Video generation avg time: Xs
- Frontend load time: Xs
- Database query avg time: Xms

## 7. Priority Action Items
1. [Critical] [description]
2. [High] [description]
3. [Medium] [description]
...

## 8. Long-term Recommendations
- Architecture improvements
- Scalability strategy
- Monitoring enhancements
- Feature additions

## 9. Deployment Readiness
- Production ready: [YES/NO]
- Blockers: [list]
- Pre-production checklist: [items]

## 10. Next Steps
1. [Immediate action]
2. [Short term - 1 week]
3. [Medium term - 1 month]
4. [Long term - 3 months]
```

---

## 🔧 TROUBLESHOOTING COMMON ISSUES

### Issue 1: Backend nu pornește
```powershell
# Check Python path
where python

# Check dependencies
pip list | findstr "fastapi uvicorn"

# Try reinstall
pip install -r requirements.txt --force-reinstall

# Check .env
cat services/api/.env | findstr SUPABASE
```

### Issue 2: Database connection failed
```powershell
# Test connection
python -c "from supabase import create_client; client=create_client('https://orctxxpyiqzbordibqxi.supabase.co', 'sb_publishable_7Qh8xZcxTp5tLb87ezr5tg_s2_cw0uj'); print(client.table('leads').select('*').limit(1).execute())"

# Check Supabase dashboard
# https://supabase.com/dashboard/project/orctxxpyiqzbordibqxi

# Verify tables exist
# SQL Editor: SELECT * FROM information_schema.tables WHERE table_schema='public';
```

### Issue 3: Frontend nu pornește
```powershell
# Clear cache
rm -r node_modules
rm package-lock.json

# Reinstall
npm install

# Check port
netstat -ano | findstr :3003

# Try different port
# Edit vite.config.ts → port: 3004
```

### Issue 4: Video generation fails
```powershell
# Check FFmpeg
python -c "from moviepy import ImageClip; print('MoviePy OK')"

# Check output directory
mkdir services\api\generated_videos\simple

# Check permissions
icacls services\api\generated_videos
```

### Issue 5: Redis warnings
```
⚠️ Redis connection failed
```
**Solution:** Ignoră sau pornește Redis:
```powershell
docker run -d -p 6379:6379 redis:alpine
```

---

## ✅ SUCCESS CRITERIA

Proiectul e considerat **FUNCTIONAL** dacă:

1. ✅ Backend pornește fără erori critice
2. ✅ Frontend pornește și loads dashboard
3. ✅ Database connection OK
4. ✅ Cel puțin 1 lead poate fi creat via API
5. ✅ Cel puțin 1 video poate fi generat
6. ✅ API docs accessible
7. ✅ Frontend poate comunica cu backend

Proiectul e considerat **PRODUCTION READY** dacă:

1. ✅ Toate criteriile de FUNCTIONAL
2. ✅ Toate tabelele create în Supabase
3. ✅ Error handling complet
4. ✅ Logging functional
5. ✅ Authentication implementat
6. ✅ Rate limiting activ
7. ✅ Monitoring setup (Prometheus)
8. ✅ Tests pass (unit + integration)
9. ✅ Security audit pass
10. ✅ Performance benchmarks meet targets

---

## 📞 CONTACT & SUPPORT

**Proiect:** AutoPro Daune
**Location:** `C:\Users\JJ\Desktop\autopro_daune\autoprodaune-1`
**Documentation:**
- `README.md` - Overview
- `SYSTEM_READY.md` - Status report
- `CURSOR_AGENT_FULL_INSTRUCTIONS.md` - This file

**Useful Links:**
- Supabase Dashboard: https://supabase.com/dashboard/project/orctxxpyiqzbordibqxi
- Backend API Docs: http://localhost:8001/docs
- Frontend: http://localhost:3003

---

## 🎯 FINAL NOTE FOR CURSOR AGENT

**Scopul tău:**
1. Analizează COMPLET fiecare componentă
2. Testează TOTUL sistematic
3. Documentează ce funcționează și ce nu
4. Sugerează îmbunătățiri CONCRETE
5. Prioritizează action items

**Nu face:**
- Nu schimba code fără aprobare
- Nu șterge nimic
- Nu face refactoring major fără discuție

**Întotdeauna:**
- Documentează findings
- Dă exemple concrete
- Prioritizează issues
- Sugerează quick wins
- Identifică long-term improvements

**Good luck! 🚀**