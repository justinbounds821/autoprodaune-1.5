# System Blueprint

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React/Vite)  │◄──►│   (FastAPI)     │◄──►│   (Supabase)    │
│   Port: 3007    │    │   Port: 8001    │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vite Proxy    │    │   Redis Cache   │    │   External APIs │
│   /api → :8001  │    │   (Optional)    │    │   (HeyGen, etc) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Component Structure

### Frontend (React/Vite)
```
src/
├── components/          # UI components
├── pages/              # Page components
├── services/           # API client
├── types/              # TypeScript types
└── hooks/              # React hooks
```

### Backend (FastAPI)
```
services/api/app/
├── main.py             # FastAPI app entry point
├── routes/             # API route handlers
├── services/           # Business logic
├── models/             # Database models
└── schemas/            # Pydantic schemas
```

## API Endpoints (182 total)

### Core Business (20 implemented)
- `/api/leads/` - Lead management
- `/api/financial/` - Payment tracking
- `/api/automation/` - Automation control
- `/api/video/` - Video generation
- `/api/notify/` - Notifications

### Growth Features (162 stubs)
- `/api/growth-engine/` - Mass content generation
- `/api/intelligent-conversion/` - AI conversion optimization
- `/api/customer-nurturing/` - Automated journey system
- `/api/affiliate-multiplication/` - Viral growth system
- `/api/growth-analytics/` - Intelligence dashboard
- `/api/master-growth/` - Complete ecosystem orchestration

## Data Flow

### Lead Processing Flow
1. Lead created via `/api/leads/`
2. Stored in Supabase database
3. Automation scheduler processes lead
4. Notifications sent via WhatsApp
5. Video content generated if needed

### Video Generation Flow
1. Script submitted to `/api/video/video/heygen/generate`
2. HeyGen API called with script
3. Video URL returned
4. Video metadata stored in database

### Automation Flow
1. Scheduler checks automation config
2. Generates content based on rules
3. Posts to social media platforms
4. Tracks analytics and performance

## Integration Points

### External APIs
- **HeyGen**: Video generation
- **ElevenLabs**: Text-to-speech
- **TikTok**: Social media posting
- **Instagram**: Social media posting
- **Facebook**: Social media posting
- **YouTube**: Video publishing

### Internal Services
- **Supabase**: Database and auth
- **Redis**: Rate limiting and caching
- **WhatsApp**: Notifications
- **Cloudflare R2**: File storage

## Missing Components

### Not Implemented
- Telegram bot integration
- n8n workflow automation
- Advanced video editing tools
- Professional video generation
- Growth engine dashboard
- Customer nurturing system

### Database Issues
- Missing tables: `automation_config`, `system_logs`
- Missing column: `clicks` in `social_posts`
- Schema validation needed

## Development Status

- **Backend**: 182 routes defined, ~20 functional
- **Frontend**: Core components implemented
- **Database**: Basic schema, missing tables
- **External APIs**: HeyGen integration partial
- **Automation**: Scheduler implemented, needs DB fixes
