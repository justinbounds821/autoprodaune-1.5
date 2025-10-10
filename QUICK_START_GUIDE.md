# 🚀 AUTOPRO DAUNE - QUICK START GUIDE

## ⚡ INSTALARE ȘI PORNIRE RAPIDĂ

### 🎯 OBIECTIV
Pornirea completă a sistemului AutoPro Daune cu funcționalitate REALĂ de generare video.

---

## 📋 CERINȚE PRE-INSTALARE

### Sistem:
- ✅ Linux/Mac/WSL (pentru Bash scripts)
- ✅ Python 3.11+ instalat
- ✅ Node.js 18+ și npm instalate
- ✅ Git instalat

### API Keys (DEJA CONFIGURATE în .env):
- ✅ SUPABASE_URL și SUPABASE_ANON_KEY
- ✅ HEYGEN_API_KEY
- ✅ OPENAI_API_KEY
- ✅ ELEVENLABS_API_KEY
- ✅ CLOUDFLARE R2 credentials
- ✅ TIKTOK API credentials

---

## 🚀 METODA 1: PORNIRE AUTOMATĂ (RECOMANDAT)

### Backend:
```bash
./START_BACKEND_REAL.sh
```

Acest script:
1. ✅ Verifică dacă există `.env`
2. ✅ Creează virtual environment (dacă nu există)
3. ✅ Instalează toate dependințele din `requirements.txt`
4. ✅ Pornește FastAPI pe port 8001

### Frontend:
```bash
# În alt terminal
./START_FRONTEND_REAL.sh
```

Acest script:
1. ✅ Instalează npm dependencies (dacă nu sunt instalate)
2. ✅ Pornește Vite dev server
3. ✅ Deschide pe port 3006 sau 3007

---

## 🔧 METODA 2: PORNIRE MANUALĂ

### Backend:
```bash
cd /workspace/services/api

# Creează virtual environment
python3 -m venv venv
source venv/bin/activate

# Instalează dependințe
pip install --upgrade pip
pip install -r requirements.txt

# Setează PYTHONPATH
export PYTHONPATH=/workspace/services/api

# Pornește server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend:
```bash
cd /workspace/02_FRONTEND_UI_CLEAN

# Instalează dependințe
npm install

# Pornește dev server
npm run dev
```

---

## 🧪 TESTARE FUNCȚIONALITATE

### 1. Verificare Backend Running:
```bash
# Health check
curl http://localhost:8001/health

# Expected response:
# {"status":"ok","service":"autopro-daune","port":8001}
```

### 2. Testare Financial Endpoints:
```bash
# Revenue data
curl http://localhost:8001/api/financial/revenue?period=7d

# Costs data
curl http://localhost:8001/api/financial/costs?period=7d
```

### 3. Testare Automation Logs:
```bash
curl http://localhost:8001/api/automation/logs?limit=10
```

### 4. Testare Video Generation (HeyGen):
```bash
curl -X POST http://localhost:8001/api/advanced-video/generate \
  -H "Content-Type: application/json" \
  -d '{
    "script": "Test AutoPro Daune - Generare video real cu HeyGen",
    "avatar_type": "professional",
    "background_type": "office",
    "aspect_ratio": "portrait",
    "resolution": "1080p"
  }'

# Expected response:
# {
#   "success": true,
#   "data": {
#     "job_id": "advanced_20251010_XXXXXX",
#     "status": "queued"
#   }
# }
```

### 5. Verificare Job Status:
```bash
curl http://localhost:8001/api/advanced-video/jobs
```

---

## 🌐 ACCESARE APLICAȚIE

### Backend:
- **API:** http://localhost:8001
- **Documentație:** http://localhost:8001/docs
- **Redoc:** http://localhost:8001/redoc
- **Health:** http://localhost:8001/health
- **Metrics:** http://localhost:8001/metrics

### Frontend:
- **Admin Panel:** http://localhost:3006/admin sau http://localhost:3007/admin
- **Dashboard:** http://localhost:3006/
- **Login:** http://localhost:3006/login

---

## 🎯 FEATURES DISPONIBILE

### ✅ Video Generation (REAL):
- **HeyGen AI Avatars** - Avatar video profesionale
- **Pika Labs** - Video generation din text
- **ManoleVideoGenerator** - Video custom cu TTS

### ✅ Financial Tracking:
- Revenue tracking în timp real
- Cost monitoring (API + Infrastructure + Marketing)
- ROI calculation și analytics

### ✅ Automation:
- 3x daily video posting
- Social media automation (TikTok, Instagram, Facebook)
- WhatsApp bot automation
- Automation logs tracking

### ✅ Lead Management:
- Lead capture și tracking
- Referral system (200 LEI per referral)
- Customer nurturing journeys

### ✅ Social Media:
- Multi-platform posting
- Performance analytics
- Engagement tracking

---

## 📊 MONITORING ȘI LOGS

### Backend Logs:
```bash
# Vezi logs în terminal unde rulează backend
# Logs include:
# - ✅ Request/Response logs
# - ✅ Video generation progress
# - ✅ API call tracking
# - ✅ Error tracking
```

### Frontend Logs:
```bash
# Vezi logs în browser console (F12)
# Sau în terminal unde rulează npm dev
```

### Database Logs:
```bash
# Accesează Supabase Dashboard pentru query logs
# URL: https://yfbhmbjtauhxgalvdfns.supabase.co
```

---

## 🐛 TROUBLESHOOTING

### Backend nu pornește:

#### 1. Check .env file:
```bash
ls -la /workspace/services/api/.env
# Ar trebui să existe și să aibă ~5KB
```

#### 2. Check Python version:
```bash
python3 --version
# Trebuie să fie >= 3.11
```

#### 3. Install missing dependencies:
```bash
cd /workspace/services/api
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend nu pornește:

#### 1. Check Node version:
```bash
node --version
npm --version
# Node >= 18, npm >= 9
```

#### 2. Clear cache și reinstall:
```bash
cd /workspace/02_FRONTEND_UI_CLEAN
rm -rf node_modules package-lock.json
npm install
```

### Video generation failed:

#### 1. Check API keys:
```bash
cd /workspace/services/api
grep HEYGEN_API_KEY .env
grep OPENAI_API_KEY .env
# Ar trebui să returneze key-urile reale
```

#### 2. Check logs pentru erori:
```bash
# În terminal backend, caută:
# "HeyGen API error"
# "Pika API error"
```

#### 3. Verify API quotas:
- HeyGen: Check dashboard pentru remaining credits
- Pika: Check API usage
- ElevenLabs: Check character limit (10k/month free)

### Database connection failed:

#### 1. Test Supabase connection:
```bash
curl -X GET "https://yfbhmbjtauhxgalvdfns.supabase.co/rest/v1/" \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### 2. Check RLS policies în Supabase Dashboard

#### 3. Verify service role key este corect în .env

---

## 🔐 SECURITATE

### API Keys:
- ❌ **NU COMMITA .env în Git!**
- ✅ .env este în .gitignore
- ✅ Folosește environment variables în production

### Database:
- ✅ Row Level Security (RLS) activat
- ✅ Service role key doar pentru backend
- ✅ Anon key pentru frontend (cu limitări RLS)

---

## 📈 NEXT STEPS

### După pornire cu succes:

1. **Test Video Generation:**
   - Accesează Admin Panel → Video Management
   - Click "Generate Video"
   - Urmărește progress în real-time

2. **Check Financial Dashboard:**
   - Accesează Admin Panel → Financial
   - Vezi revenue și costs în timp real

3. **Configurare Automation:**
   - Accesează Admin Panel → Automation Control
   - Enable daily 3x video posting

4. **Add Sample Data:**
   - Creează test leads
   - Generează test videos
   - Postează pe social media

---

## 📞 SUPPORT

### Documentație completă:
- `/workspace/IMPLEMENTATION_COMPLETE_REAL.md` - Detalii implementare
- `/workspace/FULL_SYSTEM_LOGS_AND_ERRORS.md` - Erori și soluții
- `http://localhost:8001/docs` - OpenAPI documentation

### Common Issues:
1. Port already in use → Change port în startup command
2. Database connection failed → Check Supabase credentials
3. Video generation timeout → Check API quotas

---

## ✅ CHECKLIST PORNIRE

- [ ] Backend pornit pe port 8001
- [ ] Frontend pornit pe port 3006/3007
- [ ] Health check returnează "ok"
- [ ] Financial endpoints returnează date
- [ ] Automation logs sunt accesibile
- [ ] Admin panel se încarcă fără erori
- [ ] Video generation job poate fi creat
- [ ] Database connection funcționează

---

## 🎉 GATA DE UTILIZARE!

**Sistem complet funcțional cu:**
- ✅ Real video generation (HeyGen + Pika)
- ✅ Financial tracking complet
- ✅ Automation system activ
- ✅ Lead management
- ✅ Social media integration

**🚀 HAPPY CODING!**
