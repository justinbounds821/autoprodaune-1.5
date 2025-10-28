# 🚀 AutoPro Daune - System Startup Guide

**Date:** 2025-10-10  
**Status:** ✅ Ready to Start

---

## 📋 PREREQUISITES

Toate dependențele au fost instalate:
- ✅ Python 3.13.3
- ✅ Node.js v22.20.0
- ✅ npm 10.9.3
- ✅ Backend dependencies installed
- ✅ Frontend dependencies installed
- ✅ .env files configured

---

## 🎯 QUICK START (2 Terminals Required)

### Terminal 1 - Backend
```bash
cd /workspace
./start-backend.sh
```

**Expected Output:**
```
🚀 Starting AutoPro Daune Backend...
✅ .env file found
🔧 Starting Uvicorn server...
INFO: Started server process
INFO: Application startup complete
INFO: Uvicorn running on http://127.0.0.1:8001
```

**Access Points:**
- 📊 API Docs: http://127.0.0.1:8001/docs
- 🏥 Health: http://127.0.0.1:8001/health

---

### Terminal 2 - Frontend  
```bash
cd /workspace
./start-frontend.sh
```

**Expected Output:**
```
🎨 Starting AutoPro Daune Frontend...
✅ Dependencies ready
🔧 Starting Vite dev server...
VITE v5.4.19 ready in XXX ms
➜  Local: http://localhost:3006/
```

**Access Points:**
- 🌐 Frontend: http://localhost:3006
- 👤 Admin: http://localhost:3006/admin

---

## 🔍 HEALTH CHECK

După pornirea ambelor servicii, testează:

```bash
# Test backend
curl http://127.0.0.1:8001/health

# Expected: {"status":"ok","service":"autopro-daune","port":8001}
```

```bash
# Test frontend (in browser)
# Open: http://localhost:3006
# Should load the main page
```

---

## 📊 AVAILABLE ROUTES

Backend has **86 active routes**:

### Core
- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger)
- `GET /metrics` - Prometheus metrics

### Lead Management
- `POST /api/working-leads/create` - Create lead
- `GET /api/dashboard/overview` - Dashboard data

### Video Generation
- `POST /api/autoposter/generate` - Generate video
- `POST /api/autoposter/publish` - Publish to social media
- `GET /api/autoposter/status` - Check generation status

### Notifications
- `POST /api/notify/whatsapp` - Send WhatsApp message
- `POST /api/notify/email` - Send email
- `GET /api/notify/list` - List notifications

### Social Media
- Multiple endpoints for TikTok, Instagram, YouTube
- Follower count tracking
- Post scheduling

**Full list:** http://127.0.0.1:8001/docs

---

## ⚠️ KNOWN ISSUES & WORKAROUNDS

### 1. Redis Warning
```
WARNING: ⚠️ Redis connection failed, using in-memory rate limiting
```
**Impact:** Low - System uses in-memory fallback  
**Fix (optional):** Install and start Redis locally

### 2. Automation Config Table Missing
```
WARNING: Failed to load config from DB, using defaults
```
**Impact:** Low - Uses default configuration  
**Fix:** Run database migration in Supabase:
```sql
-- In Supabase SQL Editor, run:
-- /workspace/services/api/database/supabase_schema.sql
```

### 3. Syntax Error in growth_skeletons.py
```
SyntaxError: unterminated triple-quoted string literal
```
**Impact:** Medium - Growth Skeletons router disabled  
**Status:** Marked as TODO, other 85 routes work fine  
**Fix:** Will be fixed in next update

---

## 🎯 TESTING THE SYSTEM

### 1. Test Backend Health
```bash
curl http://127.0.0.1:8001/health
```

### 2. Test Dashboard
```bash
curl http://127.0.0.1:8001/api/dashboard/overview
```

### 3. Test Frontend
Open browser: http://localhost:3006/admin

### 4. Generate Test Video
```bash
curl -X POST http://127.0.0.1:8001/api/autoposter/generate \
  -H "Content-Type: application/json" \
  -d '{
    "script": "Test video pentru AutoPro Daune",
    "template_type": "educational"
  }'
```

---

## 📁 PROJECT STRUCTURE

```
/workspace/
├── services/api/              # Backend (FastAPI)
│   ├── app/
│   │   ├── main.py           # Entry point (86 routes)
│   │   ├── routes/           # API endpoints
│   │   └── services/         # Business logic
│   └── .env                  # ✅ Configured
│
├── 02_FRONTEND_UI_CLEAN/     # Frontend (React+Vite)
│   ├── src/
│   │   ├── pages/            # 12 pages
│   │   └── components/       # 60+ components
│   └── .env                  # ✅ Configured
│
├── start-backend.sh          # ✅ Backend startup script
├── start-frontend.sh         # ✅ Frontend startup script
└── START_SYSTEM.md           # This file
```

---

## 🔧 CONFIGURATION FILES

### Backend (.env)
Location: `/workspace/services/api/.env`

Key variables:
- `SUPABASE_URL` - ✅ Configured
- `SUPABASE_ANON_KEY` - ✅ Configured
- `ELEVENLABS_API_KEY` - ✅ Configured
- `YOUTUBE_API_KEY` - ✅ Configured

### Frontend (.env)
Location: `/workspace/02_FRONTEND_UI_CLEAN/.env`

Key variables:
- `VITE_API_URL=http://localhost:8001` - ✅ Configured
- `VITE_SUPABASE_URL` - ✅ Configured

---

## 🆘 TROUBLESHOOTING

### Backend won't start
```bash
# Check if port 8001 is already in use
lsof -i :8001

# If blocked, kill the process
kill -9 <PID>
```

### Frontend won't start
```bash
# Clear npm cache and reinstall
cd /workspace/02_FRONTEND_UI_CLEAN
rm -rf node_modules package-lock.json
npm install
```

### CORS errors in browser
- Make sure backend is running on 127.0.0.1:8001
- Frontend proxy is configured in vite.config.ts
- Backend CORS includes localhost:3006

---

## 🎉 SUCCESS CRITERIA

✅ Backend running on port 8001  
✅ Frontend running on port 3006  
✅ Health check returns 200 OK  
✅ Admin panel loads without errors  
✅ Dashboard shows data  
✅ No critical errors in console  

---

## 📚 DOCUMENTATION

- **API Documentation:** http://127.0.0.1:8001/docs (when backend running)
- **Master Status:** /workspace/MASTER_PROJECT_STATUS.md
- **Implementation Details:** /workspace/_OLD_DOCS/FINAL_IMPLEMENTATION_SUMMARY.md
- **User Manual:** /workspace/MANUAL_UTILIZARE_COMPLET.md

---

**System Ready! 🚀**

Start backend and frontend in separate terminals, then access:
- Admin Panel: http://localhost:3006/admin
- API Docs: http://127.0.0.1:8001/docs
