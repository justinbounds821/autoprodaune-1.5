-- Phase 9 AI Enhancements Tables
-- Run this migration to add AI features support

-- Video Templates
CREATE TABLE IF NOT EXISTS video_templates (
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

-- Video Insights (AI analysis results)
CREATE TABLE IF NOT EXISTS video_insights (
    job_id TEXT PRIMARY KEY REFERENCES video_jobs(id) ON DELETE CASCADE,
    tags TEXT[] DEFAULT '{}',
    sentiment TEXT,
    sentiment_score FLOAT DEFAULT 0,
    entities JSONB DEFAULT '[]',
    scene_cuts JSONB DEFAULT '[]',
    vector_embedding FLOAT[],
    captions_srt_path TEXT,
    captions_ass_path TEXT,
    audio_quality_score FLOAT,
    processed_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_video_job FOREIGN KEY (job_id) REFERENCES video_jobs(id)
);

-- Video Costs
CREATE TABLE IF NOT EXISTS video_costs (
    job_id TEXT PRIMARY KEY REFERENCES video_jobs(id) ON DELETE CASCADE,
    amount_cents INTEGER NOT NULL DEFAULT 0,
    breakdown JSONB NOT NULL DEFAULT '{}',
    calculated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_video_job_cost FOREIGN KEY (job_id) REFERENCES video_jobs(id)
);

-- Webhook Logs
CREATE TABLE IF NOT EXISTS webhook_logs (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    job_id TEXT REFERENCES video_jobs(id) ON DELETE CASCADE,
    event TEXT NOT NULL,
    url TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}',
    response_status INTEGER,
    response_body TEXT,
    attempts INTEGER DEFAULT 1,
    sent_at TIMESTAMP DEFAULT NOW(),
    delivered BOOLEAN DEFAULT false,
    error TEXT,
    CONSTRAINT fk_webhook_job FOREIGN KEY (job_id) REFERENCES video_jobs(id)
);

-- CDN Cache Purge History
CREATE TABLE IF NOT EXISTS cdn_purge_history (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    job_id TEXT REFERENCES video_jobs(id) ON DELETE CASCADE,
    purged_urls TEXT[] DEFAULT '{}',
    purged_at TIMESTAMP DEFAULT NOW(),
    purged_by TEXT,
    CONSTRAINT fk_cdn_job FOREIGN KEY (job_id) REFERENCES video_jobs(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_video_insights_job_id ON video_insights(job_id);
CREATE INDEX IF NOT EXISTS idx_video_insights_tags ON video_insights USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_video_costs_job_id ON video_costs(job_id);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_job_id ON webhook_logs(job_id);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_delivered ON webhook_logs(delivered);
CREATE INDEX IF NOT EXISTS idx_cdn_purge_job_id ON cdn_purge_history(job_id);
CREATE INDEX IF NOT EXISTS idx_templates_category ON video_templates(category);
CREATE INDEX IF NOT EXISTS idx_templates_active ON video_templates(is_active);

-- Insert default templates
INSERT INTO video_templates (id, name, description, category, config, preview_url) VALUES
('tpl_insurance_claim', 'Insurance Claim Video', 'Professional video for insurance claim presentation', 'insurance', 
 '{"resolution": "1920x1080", "fps": 30, "format": "mp4", "avatar": "professional_male_ro", "background": "office", "voice": "romanian_male_formal"}'::jsonb,
 '/assets/templates/insurance_claim_preview.jpg'),
 
('tpl_social_short', 'Social Media Short', 'Short-form video optimized for social media', 'social',
 '{"resolution": "1080x1920", "fps": 30, "format": "mp4", "avatar": "casual_female_ro", "background": "modern", "voice": "romanian_female_friendly", "duration_max": 60}'::jsonb,
 '/assets/templates/social_short_preview.jpg'),
 
('tpl_explainer', 'Explainer Video', 'Educational explainer video with animations', 'education',
 '{"resolution": "1920x1080", "fps": 25, "format": "mp4", "avatar": "teacher_ro", "background": "whiteboard", "voice": "romanian_neutral", "include_subtitles": true}'::jsonb,
 '/assets/templates/explainer_preview.jpg')
ON CONFLICT (id) DO NOTHING;

-- Enable pgvector extension for vector search (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- Add vector column to video_insights if using pgvector
-- ALTER TABLE video_insights ADD COLUMN IF NOT EXISTS embedding vector(384);

COMMENT ON TABLE video_templates IS 'Video generation templates and presets';
COMMENT ON TABLE video_insights IS 'AI-generated insights for videos (tags, sentiment, scenes)';
COMMENT ON TABLE video_costs IS 'Per-job cost tracking and billing';
COMMENT ON TABLE webhook_logs IS 'Webhook delivery history and retry logs';
COMMENT ON TABLE cdn_purge_history IS 'CDN cache purge history';
