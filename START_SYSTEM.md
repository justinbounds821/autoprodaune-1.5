# 🚀 AutoPro Daune 1.5 - Complete System Startup Guide

## 📋 System Overview

AutoPro Daune 1.5 is a complete lead generation and automation system featuring:
- **Backend**: FastAPI with 86+ routes and comprehensive services
- **Frontend**: React 18 with TypeScript and modern UI components
- **Database**: Supabase PostgreSQL with 11 optimized tables
- **Video Generation**: MoviePy, HeyGen, Pika Labs, ElevenLabs integration
- **Social Media**: TikTok, YouTube, Instagram, Facebook automation
- **Automation**: 3x daily posting scheduler with content templates
- **Monitoring**: Prometheus metrics and comprehensive logging

## 🔧 Prerequisites

### System Requirements
- **Python**: 3.9+ (recommended: 3.11)
- **Node.js**: 18+ (recommended: 20 LTS)
- **RAM**: Minimum 4GB (recommended: 8GB+)
- **Storage**: 2GB free space for dependencies and cache
- **OS**: Windows 10+, macOS 10.15+, or Linux

### Required Accounts & API Keys
- ✅ **Supabase**: Database and authentication
- ✅ **Cloudflare R2**: File storage
- ✅ **ElevenLabs**: Voice synthesis
- ✅ **YouTube API**: Social media integration
- ⚠️ **HeyGen**: AI avatar videos (optional)
- ⚠️ **TikTok Business**: Social posting (OAuth required)
- ⚠️ **Instagram/Facebook**: Social posting (OAuth required)

## 📁 Project Structure

```
/workspace/
├── services/api/           # FastAPI Backend
│   ├── app/
│   │   ├── main.py        # Main application
│   │   ├── core/          # Database & monitoring
│   │   ├── routes/        # 30+ API route modules
│   │   ├── services/      # Business logic services
│   │   └── middleware/    # Rate limiting, auth
│   └── requirements.txt   # Python dependencies
├── 02_FRONTEND_UI_CLEAN/  # React Frontend
│   ├── src/
│   │   ├── pages/         # 12 main pages
│   │   ├── components/    # Reusable UI components
│   │   └── services/      # API integration
│   └── package.json       # Node.js dependencies
├── .env                   # Backend environment
├── database_schema.sql    # Complete DB schema
└── start-*.sh            # Startup scripts
```

## 🚀 Quick Start (5 Minutes)

### Step 1: Environment Setup
```bash
# Clone or navigate to project directory
cd /workspace

# Verify environment files exist
ls -la .env 02_FRONTEND_UI_CLEAN/.env
```

### Step 2: Start Backend
```bash
# Make scripts executable (Linux/macOS)
chmod +x start-backend.sh start-frontend.sh

# Start backend
./start-backend.sh

# Expected output:
# ✅ .env file found
# 📦 Installing Python dependencies...
# 🚀 Starting FastAPI server on port 8001...
# INFO: Uvicorn running on http://0.0.0.0:8001
```

### Step 3: Start Frontend (New Terminal)
```bash
# Start frontend
./start-frontend.sh

# Expected output:
# ✅ .env file found
# 📦 Installing Node.js dependencies...
# 🚀 Starting Vite development server on port 3006...
# ➜ Local: http://localhost:3006/
```

### Step 4: Verify System
```bash
# Test backend health
curl http://localhost:8001/health

# Expected: {"status":"ok","service":"autopro-daune","port":8001}

# Open frontend
open http://localhost:3006
```

## 🔧 Manual Setup (Detailed)

### Backend Setup

1. **Navigate to API directory**:
   ```bash
   cd services/api
   ```

2. **Create Python virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # OR
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd 02_FRONTEND_UI_CLEAN
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev -- --port 3006 --host 0.0.0.0
   ```

### Database Setup

1. **Apply database schema**:
   ```bash
   # Connect to your Supabase project and run:
   psql -h your-supabase-host -U postgres -d postgres -f database_schema.sql
   ```

2. **Verify tables created**:
   - leads (sample data included)
   - referrals (sample data included)
   - social_posts
   - whatsapp_conversations
   - whatsapp_messages
   - video_jobs
   - automation_config (default config included)
   - system_logs
   - performance_metrics (sample data included)
   - financial_records
   - user_sessions

## 🌐 System Access Points

### Main Applications
- **Frontend**: http://localhost:3006
- **Admin Panel**: http://localhost:3006/admin
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Metrics**: http://localhost:8001/metrics

### Key Features Access
- **Dashboard**: http://localhost:3006/admin/dashboard
- **Video Management**: http://localhost:3006/admin/videos
- **Lead Management**: http://localhost:3006/admin/leads
- **Social Media**: http://localhost:3006/admin/social
- **Financial Dashboard**: http://localhost:3006/admin/financial
- **Automation Control**: http://localhost:3006/admin/automation

## 🧪 System Verification

Run the comprehensive verification test:

```bash
# Install test dependencies
pip install aiohttp

# Run verification
python test_system_verification.py

# Expected output:
# 🚀 AutoPro Daune 1.5 - System Verification Starting...
# ✅ test_authentication_flow completed
# ✅ test_dashboard_loading completed
# ✅ test_video_generation completed
# ... (all tests)
# 🎉 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION!
```

## 📊 Performance Verification Checklist

### ✅ Phase 1: Core Functionality (CRITICAL)

**Priority 1 - Authentication Flow:**
- [ ] 1.1 Open app - redirect to login if not authenticated
- [ ] 1.2 Register new user - receive confirmation
- [ ] 1.3 Login with credentials - JWT stored
- [ ] 1.4 Access protected route - verify authorization
- [ ] 1.5 Logout - token cleared, redirect to login
- [ ] 1.6 Try access without token - verify 401 error

**Priority 2 - Dashboard Loading:**
- [ ] 2.1 Dashboard loads in <3 seconds
- [ ] 2.2 All metrics display correctly
- [ ] 2.3 No console errors (F12 check)
- [ ] 2.4 Responsive on mobile (320px width)
- [ ] 2.5 Data refreshes on manual reload

**Priority 3 - Video Generation:**
- [ ] 3.1 Generate internal video (MoviePy)
- [ ] 3.2 Verify video completion (30-60s)
- [ ] 3.3 Preview video in browser
- [ ] 3.4 Download video successfully
- [ ] 3.5 Video includes WhatsApp CTA

### ✅ Phase 2: Advanced Features (HIGH)

**Priority 4 - Lead Management:**
- [ ] 4.1 Create, edit, delete lead
- [ ] 4.2 Lead scoring calculates correctly
- [ ] 4.3 Timeline shows all activities
- [ ] 4.4 Bulk operations work (5+ leads)
- [ ] 4.5 CSV export downloads

**Priority 5 - Financial Tracking:**
- [ ] 5.1 Revenue data displays
- [ ] 5.2 Cost breakdown accurate
- [ ] 5.3 Date range filters work
- [ ] 5.4 Export CSV with custom dates
- [ ] 5.5 Charts render (if implemented)

**Priority 6 - Social Media:**
- [ ] 6.1 YouTube followers load
- [ ] 6.2 TikTok OAuth flow (if ready)
- [ ] 6.3 Post video to one platform
- [ ] 6.4 Verify post appears (manual)
- [ ] 6.5 Analytics update

## 🔧 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.9+

# Check if port is in use
lsof -i :8001  # Linux/macOS
netstat -ano | findstr :8001  # Windows

# Check environment variables
cat .env | grep -E "(SUPABASE|API_KEY)"
```

**Frontend won't start:**
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if port is in use
lsof -i :3006  # Linux/macOS
netstat -ano | findstr :3006  # Windows
```

**Database connection issues:**
```bash
# Test Supabase connection
curl -H "apikey: YOUR_SUPABASE_ANON_KEY" \
     "https://YOUR_PROJECT.supabase.co/rest/v1/leads?select=*&limit=1"
```

**Video generation fails:**
```bash
# Check FFmpeg installation
ffmpeg -version

# Install FFmpeg if missing:
# Ubuntu: sudo apt install ffmpeg
# macOS: brew install ffmpeg
# Windows: Download from https://ffmpeg.org/
```

### Performance Issues

**Slow API responses:**
- Check database connection
- Verify Supabase project status
- Monitor system resources (RAM, CPU)
- Check network connectivity

**Frontend loading slowly:**
- Clear browser cache
- Check browser console for errors
- Verify API endpoints are responding
- Test with different browser

## 🔐 Security Configuration

### Production Deployment

1. **Update environment variables**:
   ```env
   ENVIRONMENT=production
   DEBUG=false
   JWT_SECRET_KEY=your-secure-secret-key
   ```

2. **Configure CORS properly**:
   ```env
   BACKEND_CORS_ORIGINS=https://your-domain.com
   ```

3. **Enable HTTPS**:
   - Use reverse proxy (nginx, Apache)
   - Configure SSL certificates
   - Update all URLs to HTTPS

4. **Database security**:
   - Use RLS (Row Level Security) in Supabase
   - Configure proper user permissions
   - Enable audit logging

## 📈 Monitoring & Maintenance

### Health Checks
- **API Health**: http://localhost:8001/health
- **Metrics**: http://localhost:8001/metrics
- **Database**: Check Supabase dashboard
- **Storage**: Check Cloudflare R2 usage

### Log Files
- **Backend logs**: `./logs/autoprodaune.log`
- **System logs**: Database `system_logs` table
- **Performance metrics**: Database `performance_metrics` table

### Backup Strategy
1. **Database**: Supabase automatic backups
2. **Files**: Cloudflare R2 versioning
3. **Configuration**: Git repository
4. **Logs**: Rotate and archive weekly

## 🎯 Success Metrics

### Performance Targets
- **Page Load**: <3 seconds
- **API Response**: <500ms (95th percentile)
- **Video Generation**: 30-60s (internal), 2-3min (HeyGen)
- **Dashboard Refresh**: <1 second
- **Uptime**: 99.5%

### Quality Gates
- ✅ Zero console errors on load
- ✅ All API endpoints return 200/201/400 (not 500)
- ✅ Mobile responsive (320px min width)
- ✅ Accessibility score >90 (Lighthouse)
- ✅ Security headers configured

## 🆘 Support & Documentation

### Additional Resources
- **API Documentation**: http://localhost:8001/docs (Swagger UI)
- **Project Status**: `/workspace/MASTER_PROJECT_STATUS.md`
- **Architecture Overview**: `/workspace/SYSTEM_STARTUP_COMPLETE.md`
- **Verification Report**: Run `python test_system_verification.py`

### Getting Help
1. Check this startup guide
2. Review error logs in console/files
3. Run system verification tests
4. Check API documentation
5. Review environment configuration

---

**AutoPro Daune 1.5 - Complete Lead Generation & Automation System**  
*Ready for explosive growth and maximum efficiency* 🚀