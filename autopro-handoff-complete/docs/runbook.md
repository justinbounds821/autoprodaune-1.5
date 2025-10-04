# Production Runbook

## System Startup

### 1. Backend Startup
```powershell
cd .\services\api
$env:BACKEND_CORS_ORIGINS = "http://localhost:3007,http://127.0.0.1:3007"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### 2. Frontend Startup
```powershell
cd .\02_FRONTEND_UI_CLEAN
npm run dev
```

### 3. Quick Start (All Services)
```powershell
.\scripts\start-all.ps1
```

## Health Checks

### Backend Health
```bash
curl http://127.0.0.1:8001/health
```

### Frontend Health
```bash
curl http://127.0.0.1:3007/
```

### API Proxy Test
```bash
curl http://127.0.0.1:3007/api/leads/
```

## Environment Configuration

### Required Environment Variables
```env
# Backend (.env)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
HEYGEN_API_KEY=your_heygen_api_key_here

# Frontend (.env)
VITE_API_BASE_URL=http://127.0.0.1:8001
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check if port 8001 is free
   - Verify Python dependencies: `pip install -r requirements.txt`
   - Check environment variables

2. **Frontend won't start**
   - Check if port 3007 is free (Vite will auto-increment)
   - Verify Node dependencies: `npm install`
   - Check Vite configuration

3. **API calls failing**
   - Verify CORS configuration in backend
   - Check proxy settings in vite.config.ts
   - Ensure backend is running on port 8001

4. **Database errors**
   - Missing tables: `automation_config`, `system_logs`
   - Missing column: `clicks` in `social_posts`
   - Run database migrations if available

### Port Configuration
- Backend: 8001 (fixed)
- Frontend: 3007 (dynamic, Vite auto-increments if busy)
- CORS: Configured for localhost:3007

## Monitoring

### Log Locations
- Backend logs: Console output
- Frontend logs: Browser dev tools + console
- Error logs: `autopro-handoff-complete/logs/last_errors.txt`

### Key Metrics
- API response times
- Frontend loading times
- Database connection status
- Automation scheduler status

## Deployment Notes

- Backend uses FastAPI with Uvicorn
- Frontend uses Vite + React + TypeScript
- Database: Supabase (PostgreSQL)
- Rate limiting: Redis (with in-memory fallback)
- CORS: Configured for development ports
