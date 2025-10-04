-- ============================================
-- AutoPro Video Engine - Database Schema
-- Run this in Supabase SQL Editor
-- ============================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- VIDEO JOBS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS video_jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    job_id UUID UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    script TEXT NOT NULL,
    voice_id TEXT,
    avatar_image_url TEXT,
    avatar_video_url TEXT,
    timeline JSONB,
    result_url TEXT,
    provider TEXT DEFAULT 'internal',
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- VIDEO ASSETS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS video_assets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    job_id UUID REFERENCES video_jobs(job_id) ON DELETE CASCADE,
    kind TEXT NOT NULL, -- 'audio', 'video', 'image', 'caption'
    url TEXT NOT NULL,
    meta JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- VIDEO COSTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS video_costs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    job_id UUID REFERENCES video_jobs(job_id) ON DELETE CASCADE,
    tts_seconds NUMERIC DEFAULT 0,
    processing_seconds NUMERIC DEFAULT 0,
    storage_mb NUMERIC DEFAULT 0,
    amount_cents INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- VIDEO WEBHOOKS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS video_webhooks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    job_id UUID REFERENCES video_jobs(job_id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    delivered BOOLEAN DEFAULT FALSE,
    last_error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Video jobs indexes
CREATE INDEX IF NOT EXISTS idx_video_jobs_job_id ON video_jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_video_jobs_status ON video_jobs(status);
CREATE INDEX IF NOT EXISTS idx_video_jobs_created_at ON video_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_video_jobs_provider ON video_jobs(provider);

-- Video assets indexes
CREATE INDEX IF NOT EXISTS idx_video_assets_job_id ON video_assets(job_id);
CREATE INDEX IF NOT EXISTS idx_video_assets_kind ON video_assets(kind);
CREATE INDEX IF NOT EXISTS idx_video_assets_created_at ON video_assets(created_at);

-- Video costs indexes
CREATE INDEX IF NOT EXISTS idx_video_costs_job_id ON video_costs(job_id);
CREATE INDEX IF NOT EXISTS idx_video_costs_created_at ON video_costs(created_at);

-- Video webhooks indexes
CREATE INDEX IF NOT EXISTS idx_video_webhooks_job_id ON video_webhooks(job_id);
CREATE INDEX IF NOT EXISTS idx_video_webhooks_delivered ON video_webhooks(delivered);
CREATE INDEX IF NOT EXISTS idx_video_webhooks_created_at ON video_webhooks(created_at);

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_video_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
DROP TRIGGER IF EXISTS update_video_jobs_updated_at ON video_jobs;
CREATE TRIGGER update_video_jobs_updated_at
    BEFORE UPDATE ON video_jobs
    FOR EACH ROW EXECUTE FUNCTION update_video_updated_at_column();

DROP TRIGGER IF EXISTS update_video_webhooks_updated_at ON video_webhooks;
CREATE TRIGGER update_video_webhooks_updated_at
    BEFORE UPDATE ON video_webhooks
    FOR EACH ROW EXECUTE FUNCTION update_video_updated_at_column();

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS on video tables
ALTER TABLE video_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_costs ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_webhooks ENABLE ROW LEVEL SECURITY;

-- Basic policies (can be customized based on authentication system)
CREATE POLICY "Allow service access to video_jobs" ON video_jobs
    FOR ALL USING (true); -- Replace with proper JWT claims

CREATE POLICY "Allow service access to video_assets" ON video_assets
    FOR ALL USING (true); -- Replace with proper JWT claims

CREATE POLICY "Allow service access to video_costs" ON video_costs
    FOR ALL USING (true); -- Replace with proper JWT claims

CREATE POLICY "Allow service access to video_webhooks" ON video_webhooks
    FOR ALL USING (true); -- Replace with proper JWT claims

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- Video jobs with costs view
CREATE OR REPLACE VIEW video_jobs_with_costs AS
SELECT
    vj.*,
    vc.tts_seconds,
    vc.processing_seconds,
    vc.storage_mb,
    vc.amount_cents,
    vc.created_at as cost_calculated_at
FROM video_jobs vj
LEFT JOIN video_costs vc ON vj.job_id = vc.job_id;

-- Recent video jobs view
CREATE OR REPLACE VIEW recent_video_jobs AS
SELECT
    job_id,
    status,
    script,
    provider,
    created_at,
    updated_at,
    result_url,
    error
FROM video_jobs
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;

-- Video analytics view
CREATE OR REPLACE VIEW video_analytics AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
    AVG(CASE WHEN status = 'completed' THEN EXTRACT(EPOCH FROM (updated_at - created_at)) END) as avg_processing_time_seconds,
    SUM(CASE WHEN status = 'completed' THEN vc.amount_cents ELSE 0 END) as total_cost_cents
FROM video_jobs vj
LEFT JOIN video_costs vc ON vj.job_id = vc.job_id
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function to clean up old video jobs (keep last 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_video_jobs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM video_jobs
    WHERE created_at < NOW() - INTERVAL '30 days'
    AND status IN ('completed', 'failed');

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get video job statistics
CREATE OR REPLACE FUNCTION get_video_job_stats()
RETURNS TABLE (
    total_jobs BIGINT,
    queued_jobs BIGINT,
    processing_jobs BIGINT,
    completed_jobs BIGINT,
    failed_jobs BIGINT,
    avg_processing_time_seconds NUMERIC,
    total_cost_cents BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) as total_jobs,
        COUNT(CASE WHEN status = 'queued' THEN 1 END) as queued_jobs,
        COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_jobs,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
        AVG(CASE WHEN status = 'completed' THEN EXTRACT(EPOCH FROM (updated_at - created_at)) END) as avg_processing_time_seconds,
        COALESCE(SUM(vc.amount_cents), 0) as total_cost_cents
    FROM video_jobs vj
    LEFT JOIN video_costs vc ON vj.job_id = vc.job_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- INITIAL DATA SEEDING
-- ============================================

-- Insert default webhook configuration if webhook URL is set
DO $$
DECLARE
    webhook_url TEXT := CURRENT_SETTING('app.settings.webhook_url', true);
BEGIN
    IF webhook_url IS NOT NULL AND webhook_url != '' THEN
        -- Note: This would typically be handled by the application
        -- rather than seeded in the database
        RAISE NOTICE 'Webhook URL configured: %', webhook_url;
    END IF;
END $$;

-- ============================================
-- COMPLETION MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '✅ AutoPro Video Engine Database Schema Created Successfully!';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Tables Created:';
    RAISE NOTICE '   • video_jobs (job tracking)';
    RAISE NOTICE '   • video_assets (asset metadata)';
    RAISE NOTICE '   • video_costs (cost tracking)';
    RAISE NOTICE '   • video_webhooks (webhook delivery)';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 AutoPro Video Engine is ready for deployment!';
    RAISE NOTICE '';
END $$;