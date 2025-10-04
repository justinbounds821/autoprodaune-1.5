# Environment Variables Configuration

## Backend (.env)

### Database & Core
- `SUPABASE_URL` - Supabase project URL (required)
- `SUPABASE_ANON_KEY` - Supabase anonymous key (required)  
- `SUPABASE_SERVICE_KEY` - Supabase service key (required)
- `PORT` - Backend port (default: 8001)

### CORS Configuration
- `BACKEND_CORS_ORIGINS` - Allowed origins (default: http://localhost:3007,http://127.0.0.1:3007)

### API Keys (Required for functionality)
- `HEYGEN_API_KEY` - HeyGen video generation API key
- `ELEVENLABS_API_KEY` - ElevenLabs TTS API key
- `TIKTOK_ACCESS_TOKEN` - TikTok API access token
- `INSTAGRAM_ACCESS_TOKEN` - Instagram API access token
- `FACEBOOK_ACCESS_TOKEN` - Facebook API access token
- `YOUTUBE_API_KEY` - YouTube API key

### Redis & Rate Limiting
- `REDIS_URL` - Redis connection URL (optional, defaults to in-memory)
- `RATE_LIMIT_MODE` - Rate limiting mode: redis|memory (default: memory)

### WhatsApp & Communication
- `WHATSAPP_GROUP_LINK` - WhatsApp group link for notifications

### Cloud Storage
- `R2_ACCESS_KEY_ID` - Cloudflare R2 access key
- `R2_SECRET_ACCESS_KEY` - Cloudflare R2 secret key
- `R2_BUCKET_NAME` - Cloudflare R2 bucket name
- `R2_ENDPOINT_URL` - Cloudflare R2 endpoint URL

## Frontend (.env)

### API Configuration
- `VITE_API_BASE_URL` - Backend API URL (default: http://127.0.0.1:8001)
- `VITE_API_TIMEOUT` - API timeout in ms (default: 10000)

### Supabase Client
- `VITE_SUPABASE_URL` - Supabase project URL (same as backend)
- `VITE_SUPABASE_ANON_KEY` - Supabase anonymous key (same as backend)

## Development Values (Safe to use)
```env
# Backend
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
HEYGEN_API_KEY=your_heygen_api_key_here
REDIS_URL=redis://localhost:6379

# Frontend  
VITE_API_BASE_URL=http://127.0.0.1:8001
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Required vs Optional

### Required for Core Functionality
- SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY
- HEYGEN_API_KEY (for video generation)

### Optional (Fallback to defaults)
- REDIS_URL (falls back to in-memory)
- PORT (defaults to 8001)
- BACKEND_CORS_ORIGINS (defaults to localhost:3007)
