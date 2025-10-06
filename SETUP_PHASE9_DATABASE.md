# 🗄️ PHASE 9 DATABASE SETUP GUIDE

**Status**: Required for Phase 9 AI features to work  
**Location**: `services/api/database/migrations/002_phase9_ai_tables.sql`

---

## ✅ WHAT YOU NEED TO DO

### 1. Run the Migration SQL

Connect to your Supabase database and run the migration file:

```bash
# Option 1: Via Supabase Dashboard
# 1. Go to https://supabase.com/dashboard/project/YOUR_PROJECT/sql
# 2. Paste contents of services/api/database/migrations/002_phase9_ai_tables.sql
# 3. Click "Run"

# Option 2: Via psql
psql YOUR_DATABASE_URL < services/api/database/migrations/002_phase9_ai_tables.sql
```

### 2. Verify Tables Created

The migration creates 5 new tables:

| Table | Purpose |
|-------|---------|
| `video_templates` | Video generation templates and presets |
| `video_insights` | AI-generated insights (tags, sentiment, scenes, embeddings) |
| `video_costs` | Per-job cost tracking and billing |
| `webhook_logs` | Webhook delivery history and retry logs |
| `cdn_purge_history` | CDN cache purge history |

### 3. Enable pgvector (Optional - for Vector Search)

If you want real semantic vector search:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Add vector column to video_insights
ALTER TABLE video_insights ADD COLUMN IF NOT EXISTS embedding vector(384);
```

---

## 🔍 VERIFY INSTALLATION

After running the migration, verify with:

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'video_%' OR table_name LIKE '%_logs%';

-- Check default templates inserted
SELECT id, name, category FROM video_templates;

-- Should return 3 templates:
-- tpl_insurance_claim | Insurance Claim Video | insurance
-- tpl_social_short    | Social Media Short    | social
-- tpl_explainer       | Explainer Video       | education
```

---

## 🎯 WHAT THIS ENABLES

Once migration is complete, these endpoints will work with **REAL DATABASE** queries:

### Templates
```bash
GET /api/video/templates          # List all templates
GET /api/video/templates/{id}     # Get template by ID
POST /api/video/templates/{id}/preview  # Generate preview
```

### AI Insights
```bash
GET /api/video/ai/insights/{job_id}  # Get insights for job
POST /api/video/ai/process/{job_id}  # Generate AI insights
POST /api/video/ai/search/similar    # Semantic search
GET /api/video/ai/captions/{job_id}  # Download captions
```

### Costs
```bash
GET /api/video/templates/costs/{job_id}  # Get cost breakdown
```

### Webhooks
```bash
# Webhooks automatically logged when sent
# View logs via:
GET /api/video/webhooks?job_id={id}
```

### CDN
```bash
POST /api/video/cdn/purge/{job_id}  # Purges logged to database
GET /api/video/cdn/stats            # Shows purge history
```

---

## 📊 DATABASE SCHEMA

### video_templates
```sql
CREATE TABLE video_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    config JSONB NOT NULL DEFAULT '{}',
    preview_url TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### video_insights
```sql
CREATE TABLE video_insights (
    job_id TEXT PRIMARY KEY REFERENCES video_jobs(id),
    tags TEXT[] DEFAULT '{}',
    sentiment TEXT,
    sentiment_score FLOAT DEFAULT 0,
    entities JSONB DEFAULT '[]',
    scene_cuts JSONB DEFAULT '[]',
    vector_embedding FLOAT[],
    captions_srt_path TEXT,
    captions_ass_path TEXT,
    audio_quality_score FLOAT,
    processed_at TIMESTAMP DEFAULT NOW()
);
```

### video_costs
```sql
CREATE TABLE video_costs (
    job_id TEXT PRIMARY KEY REFERENCES video_jobs(id),
    amount_cents INTEGER NOT NULL DEFAULT 0,
    breakdown JSONB NOT NULL DEFAULT '{}',
    calculated_at TIMESTAMP DEFAULT NOW()
);
```

### webhook_logs
```sql
CREATE TABLE webhook_logs (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    job_id TEXT REFERENCES video_jobs(id),
    event TEXT NOT NULL,
    url TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}',
    response_status INTEGER,
    response_body TEXT,
    attempts INTEGER DEFAULT 1,
    sent_at TIMESTAMP DEFAULT NOW(),
    delivered BOOLEAN DEFAULT false,
    error TEXT
);
```

### cdn_purge_history
```sql
CREATE TABLE cdn_purge_history (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    job_id TEXT REFERENCES video_jobs(id),
    purged_urls TEXT[] DEFAULT '{}',
    purged_at TIMESTAMP DEFAULT NOW(),
    purged_by TEXT
);
```

---

## 🔧 TROUBLESHOOTING

### Error: relation "video_jobs" does not exist

You need to have the `video_jobs` table first. Check your main database migrations.

### Error: extension "vector" does not exist

This is optional. Vector search will fall back to keyword search without pgvector.

To enable:
```sql
CREATE EXTENSION vector;
```

### Templates not showing up

Re-run the INSERT statements from the migration:

```sql
INSERT INTO video_templates (id, name, description, category, config, preview_url) VALUES
('tpl_insurance_claim', 'Insurance Claim Video', 'Professional video for insurance claim presentation', 'insurance', 
 '{"resolution": "1920x1080", "fps": 30, "format": "mp4"}'::jsonb,
 '/assets/templates/insurance_claim_preview.jpg')
ON CONFLICT (id) DO NOTHING;
```

---

## ✅ COMPLETION CHECKLIST

- [ ] Run migration SQL in Supabase
- [ ] Verify 5 tables created
- [ ] Verify 3 default templates inserted
- [ ] (Optional) Enable pgvector extension
- [ ] Test template endpoint: `GET /api/video/templates`
- [ ] Enable AI features in .env: `ENABLE_AI_INSIGHTS=true`

---

## 🎉 READY TO USE

Once migration is complete:
1. All Phase 9 endpoints will use **REAL DATABASE** queries
2. No more mock/sample data
3. Full AI insights, templates, costs, webhooks tracking
4. Production-ready data persistence

**Next step**: Enable AI features in your `.env` file!
