# FAZA 5.11: Ordine de rulare (exact)

## 🚀 **INSTRUCȚIUNI EXACTE PENTRU RULARE**

### **1. MIGRARE DATABASE (Supabase SQL Editor)**

**Obligatoriu înainte de orice altceva!**

```sql
-- Rulează în Supabase SQL Editor:
-- Fișier: database_schema_fixes.sql

-- Acest script creează toate tabelele lipsă:
-- ✅ automation_config (fixează scheduler error)
-- ✅ system_logs (fixează automation logging error)  
-- ✅ social_posts cu clicks column (fixează social poster error)
-- ✅ performance_metrics (fixează daily metrics error)
-- ✅ content_templates (video automation)
-- ✅ whatsapp_conversations (WhatsApp bot)
```

### **2. BACKEND START**

```powershell
# Rulează din directorul proiectului:
powershell -ExecutionPolicy Bypass -File .\scripts\start-backend.ps1
```

**Ce face:**
- Navighează la `services\api`
- Setează `BACKEND_CORS_ORIGINS` pentru 3006/3007
- Setează `RATE_LIMIT_MODE="memory"` (Redis fallback)
- Pornește FastAPI pe `127.0.0.1:8001` cu reload

### **3. FRONTEND START**

```powershell
# În alt terminal, din directorul proiectului:
powershell -ExecutionPolicy Bypass -File .\scripts\start-frontend.ps1
```

**Ce face:**
- Navighează la `02_FRONTEND_UI_CLEAN`
- Rulează `npm install` (dacă e necesar)
- Pornește Vite dev server (port 3006 sau 3007)

### **4. SMOKE TEST**

```powershell
# În al treilea terminal, din directorul proiectului:
powershell -ExecutionPolicy Bypass -File .\scripts\smoke-test-simple.ps1
```

**Ce testează:**
- `GET /health` → status ok
- `GET /api/automation/status` → JSON valid
- `GET /api/financial/payments` → JSON valid
- `GET /api/video/video/heygen/avatars` → JSON valid
- `POST /api/video/video/heygen/generate` → 400 HEYGEN_API_KEY not configured
- `GET /api/growth-engine/growth-status` → 200 JSON safe defaults

## 🎯 **REZULTATE AȘTEPTATE**

### **Backend (port 8001):**
```
✅ FastAPI started on http://127.0.0.1:8001
✅ CORS origins: http://localhost:3006, http://127.0.0.1:3006, http://localhost:3007, http://127.0.0.1:3007
✅ All routers loaded successfully
✅ Health endpoint: http://127.0.0.1:8001/health
✅ API docs: http://127.0.0.1:8001/docs
```

### **Frontend (port 3006/3007):**
```
✅ Vite dev server started
✅ Hot reload enabled
✅ Proxy configured for /api → http://127.0.0.1:8001
✅ Frontend accessible: http://localhost:3006 (sau 3007)
```

### **Smoke Test Results:**
```
✅ /health → {"status":"healthy","timestamp":"..."}
✅ /api/automation/status → {"automation_active":true,"daily_target":3,...}
✅ /api/financial/payments → []
✅ /api/video/video/heygen/avatars → {"success":true,"avatars":[...]}
✅ /api/video/video/heygen/generate → 400 "HEYGEN_API_KEY not configured"
✅ /api/growth-engine/growth-status → {"status":"ok","queue":0,...}
```

## 🔧 **CONFIGURARE OPCȚIONALĂ**

### **Pentru HeyGen (opțional):**
```bash
# Adaugă în .env din services/api:
HEYGEN_API_KEY=your_heygen_api_key_here
```

### **Pentru Redis (opțional):**
```bash
# Dacă vrei Redis real în loc de memory fallback:
REDIS_URL=redis://localhost:6379
```

## 🚨 **TROUBLESHOOTING**

### **Eroare: "Table automation_config doesn't exist"**
```sql
-- Rulează din nou în Supabase SQL Editor:
-- Fișier: database_schema_fixes.sql
```

### **Eroare: "Port 8001 already in use"**
```powershell
# Găsește și oprește procesul:
netstat -ano | findstr :8001
taskkill /PID <PID_NUMBER> /F
```

### **Eroare: "CORS policy"**
```powershell
# Verifică că BACKEND_CORS_ORIGINS conține portul corect:
echo $env:BACKEND_CORS_ORIGINS
```

### **Eroare: "npm install failed"**
```powershell
# Curăță cache și reinstalează:
cd 02_FRONTEND_UI_CLEAN
rm -rf node_modules
npm cache clean --force
npm install
```

## 📱 **ACCES URLS**

### **Development:**
- **Frontend**: http://localhost:3006 (sau 3007)
- **Backend**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Ping Test**: http://localhost:8001/ping

### **Admin UI:**
- **Dashboard**: http://localhost:3006/admin
- **Automation**: http://localhost:3006/admin/automation
- **Leads**: http://localhost:3006/admin/leads
- **Financial**: http://localhost:3006/admin/financial

## ✅ **VERIFICARE FINALĂ**

### **Checklist complet:**
- [ ] Database migrated (automation_config, system_logs, etc.)
- [ ] Backend running on port 8001
- [ ] Frontend running on port 3006/3007
- [ ] CORS configured correctly
- [ ] All smoke tests passing
- [ ] Admin UI accessible without crashes
- [ ] HeyGen shows proper error (400) when no API key
- [ ] Growth endpoints return safe defaults
- [ ] Automation endpoints work via alias

### **Success Metrics:**
- ✅ **UI nu mai crapă** pe ecranele care loveau rute inexistente
- ✅ **Toate endpointurile** returnează JSON valid
- ✅ **Error handling clar** pentru toate API-urile
- ✅ **Contracte stabile** pentru dezvoltare ulterioară
- ✅ **Respectă SRP** - fișiere mici, modular, fără duplicare

## 🎉 **GATA!**

**AutoPro Daune este acum complet funcțional cu:**
- ✅ Foundation fixes (FAZA 1)
- ✅ Core business alignment (FAZA 2)  
- ✅ Growth endpoints (FAZA 3)
- ✅ Advanced video placeholders (FAZA 4)
- ✅ Integration & testing (FAZA 5)

**Gata pentru dezvoltare ulterioară! 🚀**
