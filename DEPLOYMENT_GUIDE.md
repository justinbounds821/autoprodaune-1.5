# 🚀 AutoPro Daune - Complete Deployment Guide

**Last Updated:** September 30, 2025  
**System Status:** ✅ Production Ready

---

## 📋 Pre-Deployment Checklist

### **Required**
- [ ] Supabase account created
- [ ] Redis installed (or Docker available)
- [ ] FFmpeg installed (for video processing)
- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Git repository cloned

### **Optional** 
- [ ] ElevenLabs API key (for voice cloning)
- [ ] Social media API keys (TikTok, Instagram, Facebook, YouTube)
- [ ] Domain name and SSL certificate (for production)

---

## 🗄️ Step 1: Database Setup (5 minutes)

### **1.1 Create Supabase Project**
```bash
1. Go to https://supabase.com
2. Create new project
3. Wait for provisioning (~2 minutes)
4. Copy your project URL and anon key
```

### **1.2 Execute SQL Schema**
```bash
1. Open Supabase Dashboard → SQL Editor
2. Copy contents of services/api/database/supabase_schema.sql
3. Paste and click "Run"
4. Verify tables created (should see 11 tables)
```

**Tables Created:**
- `leads` - Lead management
- `referrals` - Referral system
- `financial_transactions` - Financial tracking
- `video_jobs` - Video generation
- `social_posts` - Social media posts
- `automation_config` - Automation settings
- `performance_metrics` - Analytics
- `conversion_events` - Conversion tracking
- `lead_scores` - Lead scoring
- `subscriber_stats` - Social media followers
- `whatsapp_cta_clicks` - WhatsApp tracking

---

## ⚙️ Step 2: Environment Configuration (10 minutes)

### **2.1 Create .env File**
```bash
# Copy example file
cp env.example .env

# Edit with your values
nano .env  # or use your editor
```

### **2.2 Minimum Required Configuration**
```bash
# Supabase (REQUIRED)
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Redis (REQUIRED)
REDIS_URL=redis://localhost:6379

# Backend (REQUIRED)
PORT=8001
BACKEND_CORS_ORIGINS=http://localhost:3003,http://127.0.0.1:3003
```

### **2.3 Optional API Keys**
```bash
# ElevenLabs (Optional - fallback to Edge-TTS)
ELEVENLABS_API_KEY=your_key_here

# Social Media (Optional - fallback to mock data)
TIKTOK_ACCESS_TOKEN=your_token_here
INSTAGRAM_ACCESS_TOKEN=your_token_here
FACEBOOK_ACCESS_TOKEN=your_token_here
YOUTUBE_API_KEY=your_key_here

# WhatsApp
WHATSAPP_GROUP_LINK=https://chat.whatsapp.com/Kz8GEkh4MJV4qg8JmiQmZL
```

---

## 📦 Step 3: Installation (5 minutes)

### **3.1 Backend Installation**
```bash
cd services/api
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 supabase-1.0.0 ...
```

### **3.2 Frontend Installation**
```bash
cd 02_FRONTEND_UI_CLEAN
npm install
```

**Expected Output:**
```
added 1234 packages in 45s
```

### **3.3 FFmpeg Installation**

**Windows:**
```powershell
# Using Chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
# Add to PATH manually
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Mac
brew install ffmpeg
```

**Verify:**
```bash
ffmpeg -version
# Should show: ffmpeg version 4.x.x or higher
```

---

## 🐳 Step 4: Docker Deployment (Recommended)

### **4.1 Using Docker Compose**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Services Started:**
- `autopro-api` - Backend (port 8001)
- `autopro-frontend` - Frontend (port 3003)
- `autopro-redis` - Redis cache (port 6379)

### **4.2 Health Checks**
```bash
# Backend
curl http://localhost:8001/health
# Expected: {"status":"ok","service":"autopro-daune","port":8001}

# Frontend
curl http://localhost:3003
# Expected: HTML content

# Redis
docker exec autopro-redis redis-cli ping
# Expected: PONG
```

---

## 🔧 Step 5: Manual Deployment (Alternative)

### **5.1 Start Redis**
```bash
# Linux/Mac
redis-server

# Windows
redis-server.exe

# Or use Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### **5.2 Start Backend**
```bash
cd services/api
uvicorn app.main:app --reload --port 8001
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete.
✅ All main routers loaded successfully
✅ Video router loaded
✅ Conversion tracking router loaded
```

### **5.3 Start Frontend**
```bash
cd 02_FRONTEND_UI_CLEAN
npm run dev
```

**Expected Output:**
```
  VITE v5.0.0  ready in 1234 ms

  ➜  Local:   http://localhost:3003/
  ➜  Network: use --host to expose
```

### **5.4 All-in-One Script (Windows)**
```powershell
.\scripts\start-all.ps1
```

---

## ✅ Step 6: Verification (3 minutes)

### **6.1 Access Application**
```
1. Open browser: http://localhost:3003
2. Check Landing page loads
3. Click "Admin" button → Dashboard
4. Verify all 8 tabs load:
   ✓ Overview
   ✓ Videos
   ✓ Manole Creator
   ✓ Automation
   ✓ Social
   ✓ Subscribers
   ✓ Financial
   ✓ Leads
```

### **6.2 Test Core Features**

**Test 1: Lead Creation**
```
1. Go to Landing page (http://localhost:3003)
2. Fill form:
   - Name: Test User
   - Phone: 0712345678
   - Email: test@example.com
3. Submit
4. Check Dashboard → Leads tab
5. Verify lead appears
```

**Test 2: Manole Video Creator**
```
1. Dashboard → Manole Creator tab
2. Enter prompt: "Bună! Sunt Manole de la AutoPro Daune."
3. Upload a photo
4. Click "Generează Video"
5. Wait for processing (~30 seconds)
6. Verify video appears in list
7. Click download button
```

**Test 3: WhatsApp CTA Tracking**
```
1. Landing page
2. Scroll to WhatsApp button
3. Click "Contactează pe WhatsApp"
4. Verify opens WhatsApp link
5. Check backend logs for tracking event
```

---

## 📊 Step 7: Monitoring Setup (Optional)

### **7.1 Prometheus + Grafana**
```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access dashboards
Prometheus: http://localhost:9090
Grafana: http://localhost:3000
  Username: admin
  Password: admin
```

### **7.2 Import Grafana Dashboard**
```
1. Login to Grafana
2. Go to Dashboards → Import
3. Upload: monitoring/grafana-dashboard.json
4. Select Prometheus as data source
5. Click Import
```

---

## 🌐 Step 8: Production Deployment

### **8.1 Environment Variables**
```bash
# Update .env for production
VITE_ENV=production
DEBUG=false
LOG_LEVEL=WARNING

# Add production URLs
BACKEND_CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
VITE_API_URL=https://api.your-domain.com
```

### **8.2 Build for Production**

**Backend:**
```bash
# Already using uvicorn in production mode
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

**Frontend:**
```bash
cd 02_FRONTEND_UI_CLEAN
npm run build

# Output in dist/ folder
# Deploy to:
# - Vercel
# - Netlify
# - Nginx
# - Docker (already configured)
```

### **8.3 Recommended Hosting**

**Option 1: VPS (DigitalOcean, Linode, etc.)**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone repo
git clone https://your-repo.git
cd your-repo

# Configure .env
nano .env

# Start services
docker-compose up -d
```

**Option 2: Cloud Platform**
- **Backend:** Railway.app, Render.com, Fly.io
- **Frontend:** Vercel, Netlify, Cloudflare Pages
- **Database:** Supabase (already cloud)
- **Redis:** Upstash, Redis Cloud

---

## 🔒 Step 9: Security Checklist

### **Before Going Live:**
- [ ] Change default passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Set up CORS properly
- [ ] Enable Supabase RLS (Row Level Security)
- [ ] Secure API keys (use environment variables)
- [ ] Enable logging and monitoring
- [ ] Set up automated backups
- [ ] Configure error alerting

---

## 🐛 Troubleshooting

### **Issue: Backend won't start**
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep fastapi

# Check port availability
netstat -an | grep 8001

# Check logs
tail -f logs/autopro.log
```

### **Issue: Frontend build fails**
```bash
# Clear cache
npm clean-install

# Check Node version
node --version  # Should be 18+

# Rebuild
npm run build
```

### **Issue: Database connection failed**
```bash
# Verify Supabase credentials
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Test connection
curl -H "apikey: $SUPABASE_KEY" "$SUPABASE_URL/rest/v1/"
```

### **Issue: Redis connection failed**
```bash
# Check Redis is running
redis-cli ping

# If using Docker
docker ps | grep redis

# Restart Redis
docker restart autopro-redis
```

### **Issue: Videos not generating**
```bash
# Check FFmpeg
ffmpeg -version

# Check disk space
df -h

# Check video_cache directory permissions
ls -la video_cache/

# Check logs
docker logs autopro-api | grep video
```

---

## 📈 Performance Optimization

### **Backend Optimization**
```bash
# Use multiple workers
uvicorn app.main:app --workers 4

# Enable Redis caching
REDIS_URL=redis://localhost:6379

# Optimize database queries
# (Already optimized in code)
```

### **Frontend Optimization**
```bash
# Enable production build
npm run build

# Use CDN for static assets
# (Configure in nginx.conf)

# Enable gzip compression
# (Already enabled in nginx.conf)
```

---

## 🎯 Success Metrics

**System is working correctly when:**
- ✅ Landing page loads in < 2 seconds
- ✅ Dashboard shows real data from API
- ✅ Videos generate in < 60 seconds
- ✅ Lead forms submit successfully
- ✅ WhatsApp CTA tracking works
- ✅ All 8 dashboard tabs load without errors
- ✅ Backend health check returns 200
- ✅ Redis connection is stable
- ✅ Prometheus metrics are being collected

---

## 📞 Support

**Issues?**
1. Check logs: `docker logs autopro-api`
2. Check system status: `docker-compose ps`
3. Review this guide
4. Check COMPLETE_SYSTEM_ANALYSIS.md

**System Status:** ✅ PRODUCTION READY

**All Phase 1-4 features are complete and tested!** 🎉
