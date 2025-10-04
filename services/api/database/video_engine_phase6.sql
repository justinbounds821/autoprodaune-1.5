-- ============================================
-- AutoPro Video Engine - Phase 6 Database Schema
-- Production hardening with RLS, indexes, triggers
-- ============================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- PERFORMANCE INDEXES
-- ============================================

-- Video jobs indexes for common queries
CREATE INDEX IF NOT EXISTS ix_video_jobs_status ON video_jobs(status);
CREATE INDEX IF NOT EXISTS ix_video_jobs_created_at ON video_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS ix_video_jobs_updated_at ON video_jobs(updated_at DESC);
CREATE INDEX IF NOT EXISTS ix_video_jobs_provider ON video_jobs(provider);
CREATE INDEX IF NOT EXISTS ix_video_jobs_idempotency_key ON video_jobs(idempotency_key);
CREATE INDEX IF NOT EXISTS ix_video_jobs_retry_count ON video_jobs(retry_count);

-- Video assets indexes
CREATE INDEX IF NOT EXISTS ix_video_assets_job_id ON video_assets(job_id);
CREATE INDEX IF NOT EXISTS ix_video_assets_kind ON video_assets(kind);
CREATE INDEX IF NOT EXISTS ix_video_assets_created_at ON video_assets(created_at);

-- Video costs indexes
CREATE INDEX IF NOT EXISTS ix_video_costs_job_id ON video_costs(job_id);
CREATE INDEX IF NOT EXISTS ix_video_costs_created_at ON video_costs(created_at);

-- Video webhooks indexes
CREATE INDEX IF NOT EXISTS ix_video_webhooks_job_id ON video_webhooks(job_id);
CREATE INDEX IF NOT EXISTS ix_video_webhooks_delivered ON video_webhooks(delivered);
CREATE INDEX IF NOT EXISTS ix_video_webhooks_created_at ON video_webhooks(created_at);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS ix_video_jobs_status_created_at ON video_jobs(status, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_video_jobs_provider_status ON video_jobs(provider, status);

-- ============================================
-- UPDATED_AT TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION touch_updated_at() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers to video tables
DROP TRIGGER IF EXISTS tg_touch_video_jobs ON video_jobs;
CREATE TRIGGER tg_touch_video_jobs
    BEFORE UPDATE ON video_jobs
    FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

DROP TRIGGER IF EXISTS tg_touch_video_webhooks ON video_webhooks;
CREATE TRIGGER tg_touch_video_webhooks
    BEFORE UPDATE ON video_webhooks
    FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS on all video tables
ALTER TABLE video_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_costs ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_webhooks ENABLE ROW LEVEL SECURITY;

-- Service role policies (full access for backend)
CREATE POLICY video_jobs_service_all ON video_jobs
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY video_assets_service_all ON video_assets
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY video_costs_service_all ON video_costs
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY video_webhooks_service_all ON video_webhooks
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Anonymous/Authenticated policies (read-only for monitoring)
CREATE POLICY video_jobs_read_anon ON video_jobs
    FOR SELECT TO anon USING (status IN ('completed', 'failed'));

CREATE POLICY video_jobs_read_auth ON video_jobs
    FOR SELECT TO authenticated USING (true);

CREATE POLICY video_assets_read_anon ON video_assets
    FOR SELECT TO anon USING (
        job_id IN (SELECT job_id FROM video_jobs WHERE status IN ('completed', 'failed'))
    );

CREATE POLICY video_assets_read_auth ON video_assets
    FOR SELECT TO authenticated USING (true);

CREATE POLICY video_costs_read_anon ON video_costs
    FOR SELECT TO anon USING (
        job_id IN (SELECT job_id FROM video_jobs WHERE status IN ('completed', 'failed'))
    );

CREATE POLICY video_costs_read_auth ON video_costs
    FOR SELECT TO authenticated USING (true);

CREATE POLICY video_webhooks_read_anon ON video_webhooks
    FOR SELECT TO anon USING (delivered = true);

CREATE POLICY video_webhooks_read_auth ON video_webhooks
    FOR SELECT TO authenticated USING (true);

-- ============================================
-- DATA VALIDATION TRIGGERS
-- ============================================

-- Function to validate job status transitions
CREATE OR REPLACE FUNCTION validate_job_status() RETURNS TRIGGER AS $$
BEGIN
    -- Only allow valid status transitions
    IF NEW.status NOT IN ('queued', 'processing', 'completed', 'failed', 'cancelled') THEN
        RAISE EXCEPTION 'Invalid job status: %', NEW.status;
    END IF;

    -- Prevent invalid transitions
    IF OLD.status = 'completed' AND NEW.status != 'completed' THEN
        RAISE EXCEPTION 'Cannot change status of completed job';
    END IF;

    IF OLD.status = 'failed' AND NEW.status NOT IN ('failed', 'queued') THEN
        RAISE EXCEPTION 'Can only retry failed jobs';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply status validation trigger
DROP TRIGGER IF EXISTS tg_validate_job_status ON video_jobs;
CREATE TRIGGER tg_validate_job_status
    BEFORE UPDATE ON video_jobs
    FOR EACH ROW EXECUTE FUNCTION validate_job_status();

-- ============================================
-- AUTOMATIC CLEANUP FUNCTION
-- ============================================

-- Function to clean up old completed/failed jobs
CREATE OR REPLACE FUNCTION cleanup_old_video_jobs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    cutoff_date TIMESTAMPTZ;
BEGIN
    -- Calculate cutoff date (default 7 days for completed, 30 days for failed)
    cutoff_date := NOW() - INTERVAL '7 days';

    -- Delete old completed jobs
    DELETE FROM video_jobs
    WHERE status = 'completed'
    AND created_at < cutoff_date;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    -- Delete old failed jobs (keep longer for debugging)
    DELETE FROM video_jobs
    WHERE status = 'failed'
    AND created_at < (NOW() - INTERVAL '30 days');

    deleted_count := deleted_count + ROW_COUNT;

    -- Clean up orphaned assets and costs
    DELETE FROM video_assets
    WHERE job_id NOT IN (SELECT job_id FROM video_jobs);

    DELETE FROM video_costs
    WHERE job_id NOT IN (SELECT job_id FROM video_jobs);

    DELETE FROM video_webhooks
    WHERE job_id NOT IN (SELECT job_id FROM video_jobs);

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- VIEWS FOR MONITORING
-- ============================================

-- Enhanced video jobs view with costs
CREATE OR REPLACE VIEW video_jobs_with_costs AS
SELECT
    vj.*,
    vc.tts_seconds,
    vc.processing_seconds,
    vc.storage_mb,
    vc.amount_cents,
    vc.created_at as cost_calculated_at,
    -- Calculate total duration
    EXTRACT(EPOCH FROM (vj.updated_at - vj.created_at)) as total_duration_seconds
FROM video_jobs vj
LEFT JOIN video_costs vc ON vj.job_id = vc.job_id;

-- Recent activity view for monitoring
CREATE OR REPLACE VIEW recent_video_activity AS
SELECT
    job_id,
    status,
    provider,
    created_at,
    updated_at,
    retry_count,
    -- Include cost info if available
    (SELECT amount_cents FROM video_costs WHERE job_id = vj.job_id LIMIT 1) as cost_cents,
    -- Include error info for failed jobs
    CASE WHEN status = 'failed' THEN error ELSE NULL END as last_error
FROM video_jobs vj
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- Performance metrics view
CREATE OR REPLACE VIEW video_performance_metrics AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
    COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_jobs,
    AVG(CASE WHEN status = 'completed' THEN EXTRACT(EPOCH FROM (updated_at - created_at)) END) as avg_completion_time_seconds,
    SUM(CASE WHEN status = 'completed' THEN vc.amount_cents ELSE 0 END) as total_cost_cents,
    AVG(CASE WHEN status = 'completed' THEN vc.amount_cents END) as avg_cost_per_job
FROM video_jobs vj
LEFT JOIN video_costs vc ON vj.job_id = vc.job_id
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- ============================================
-- USEFUL QUERIES FOR MONITORING
-- ============================================

-- Get current queue status
CREATE OR REPLACE VIEW current_queue_status AS
SELECT
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN status = 'queued' THEN 1 END) as queued_jobs,
    COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_jobs,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
    MIN(created_at) as oldest_job_date,
    MAX(created_at) as newest_job_date
FROM video_jobs;

-- Get jobs by status with recent activity
CREATE OR REPLACE VIEW jobs_by_status AS
SELECT
    status,
    COUNT(*) as count,
    AVG(retry_count) as avg_retries,
    MAX(created_at) as latest_job
FROM video_jobs
GROUP BY status
ORDER BY count DESC;

-- ============================================
-- SCHEDULED MAINTENANCE
-- ============================================

-- Function to run periodic cleanup (can be called by cron job)
CREATE OR REPLACE FUNCTION scheduled_video_cleanup()
RETURNS TEXT AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Clean up old jobs
    deleted_count := cleanup_old_video_jobs();

    RETURN format('Cleaned up %s old video jobs', deleted_count);
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- GRANTS AND PERMISSIONS
-- ============================================

-- Grant necessary permissions for service role
GRANT ALL ON video_jobs TO service_role;
GRANT ALL ON video_assets TO service_role;
GRANT ALL ON video_costs TO service_role;
GRANT ALL ON video_webhooks TO service_role;

-- Grant read permissions for authenticated users
GRANT SELECT ON video_jobs TO authenticated;
GRANT SELECT ON video_assets TO authenticated;
GRANT SELECT ON video_costs TO authenticated;
GRANT SELECT ON video_webhooks TO authenticated;

-- Grant read permissions for anonymous users (limited)
GRANT SELECT ON video_jobs TO anon;
GRANT SELECT ON video_assets TO anon;
GRANT SELECT ON video_costs TO anon;

-- ============================================
-- COMPLETION MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '✅ AutoPro Video Engine Phase 6 Database Schema Applied!';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Production hardening completed:';
    RAISE NOTICE '   • Performance indexes added';
    RAISE NOTICE '   • RLS policies configured';
    RAISE NOTICE '   • Data validation triggers';
    RAISE NOTICE '   • Monitoring views created';
    RAISE NOTICE '   • Cleanup functions ready';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Database is production-ready!';
    RAISE NOTICE '';
END $$;