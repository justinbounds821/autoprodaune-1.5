-- ============================================
-- AutoPro Video Engine - Phase 7 Database Schema
-- CDN, Thumbnails, Metadata, Billing Exports
-- ============================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- ENHANCED VIDEO JOBS TABLE
-- ============================================

-- Add thumbnail and metadata columns if they don't exist
ALTER TABLE video_jobs ADD COLUMN IF NOT EXISTS thumb_url text;
ALTER TABLE video_jobs ADD COLUMN IF NOT EXISTS meta jsonb DEFAULT '{}'::jsonb;

-- Add comment for clarity
COMMENT ON COLUMN video_jobs.thumb_url IS 'URL to video thumbnail image';
COMMENT ON COLUMN video_jobs.meta IS 'Extended metadata (duration, dimensions, codec, etc.)';

-- ============================================
-- BILLING EXPORTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS billing_exports (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    month text NOT NULL,                          -- '2025-10'
    rows_count integer NOT NULL,
    amount_cents integer NOT NULL,
    file_url text NOT NULL,
    created_at timestamptz DEFAULT now(),
    UNIQUE(month)
);

-- Add comment for clarity
COMMENT ON TABLE billing_exports IS 'Audit trail for monthly billing exports';

-- ============================================
-- ENHANCED INDEXES
-- ============================================

-- Existing indexes (ensure they exist)
CREATE INDEX IF NOT EXISTS ix_video_jobs_status ON video_jobs(status);
CREATE INDEX IF NOT EXISTS ix_video_jobs_created_at ON video_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS ix_video_jobs_updated_at ON video_jobs(updated_at DESC);

-- New indexes for phase 7 features
CREATE INDEX IF NOT EXISTS ix_video_jobs_thumb_url ON video_jobs(thumb_url) WHERE thumb_url IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_video_jobs_meta ON video_jobs USING gin(meta) WHERE meta IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_billing_exports_month ON billing_exports(month);
CREATE INDEX IF NOT EXISTS ix_billing_exports_created_at ON billing_exports(created_at DESC);

-- ============================================
-- ENHANCED TRIGGERS
-- ============================================

-- Function to update updated_at timestamp (ensure it exists)
CREATE OR REPLACE FUNCTION touch_updated_at() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers to video_jobs if not already applied
DROP TRIGGER IF EXISTS tg_touch_video_jobs ON video_jobs;
CREATE TRIGGER tg_touch_video_jobs
    BEFORE UPDATE ON video_jobs
    FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

-- ============================================
-- ROW LEVEL SECURITY (RLS) FOR BILLING EXPORTS
-- ============================================

-- Enable RLS on billing_exports table
ALTER TABLE billing_exports ENABLE ROW LEVEL SECURITY;

-- Service role policies (full access for backend)
CREATE POLICY billing_exports_service_all ON billing_exports
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Anonymous/Authenticated policies (read-only for monitoring)
CREATE POLICY billing_exports_read_anon ON billing_exports
    FOR SELECT TO anon USING (true);

CREATE POLICY billing_exports_read_auth ON billing_exports
    FOR SELECT TO authenticated USING (true);

-- ============================================
-- VIEWS FOR BILLING AND MONITORING
-- ============================================

-- Enhanced video jobs view with metadata
CREATE OR REPLACE VIEW video_jobs_enhanced AS
SELECT
    vj.*,
    -- Extract metadata fields for easier querying
    (vj.meta->>'duration')::float as duration_seconds,
    (vj.meta->>'width')::integer as video_width,
    (vj.meta->>'height')::integer as video_height,
    (vj.meta->>'fps')::float as video_fps,
    (vj.meta->>'bitrate')::integer as video_bitrate,
    (vj.meta->>'size_bytes')::bigint as file_size_bytes,
    vj.meta->>'codec' as video_codec,
    vj.meta->>'storage_type' as storage_type,
    vj.meta->>'preset' as quality_preset,
    (vj.meta->>'generated_at')::float as generated_at_timestamp,
    -- Cost information if available
    vc.tts_seconds,
    vc.processing_seconds,
    vc.storage_mb,
    vc.amount_cents
FROM video_jobs vj
LEFT JOIN video_costs vc ON vj.job_id = vc.job_id;

-- Monthly billing summary view
CREATE OR REPLACE VIEW monthly_billing_summary AS
SELECT
    to_char(vc.created_at, 'YYYY-MM') as month,
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN vj.status = 'completed' THEN 1 END) as completed_jobs,
    SUM(vc.amount_cents) as total_cost_cents,
    AVG(vc.amount_cents) as avg_cost_per_job_cents,
    SUM(vc.tts_seconds) as total_tts_seconds,
    SUM(vc.processing_seconds) as total_processing_seconds,
    SUM(vc.storage_mb) as total_storage_mb
FROM video_costs vc
JOIN video_jobs vj ON vc.job_id = vj.job_id
WHERE vc.created_at >= NOW() - INTERVAL '12 months'
GROUP BY to_char(vc.created_at, 'YYYY-MM')
ORDER BY month DESC;

-- Recent jobs with thumbnails view (for admin panel)
CREATE OR REPLACE VIEW recent_jobs_with_media AS
SELECT
    vj.job_id,
    vj.status,
    vj.script,
    vj.thumb_url,
    vj.created_at,
    vj.updated_at,
    vj.meta->>'duration' as duration_seconds,
    vj.meta->>'storage_type' as storage_type,
    vc.amount_cents,
    vc.created_at as cost_calculated_at
FROM video_jobs vj
LEFT JOIN video_costs vc ON vj.job_id = vc.job_id
WHERE vj.created_at >= NOW() - INTERVAL '7 days'
AND vj.status IN ('completed', 'failed')
ORDER BY vj.created_at DESC
LIMIT 100;

-- ============================================
-- USEFUL QUERIES FOR ADMIN PANEL
-- ============================================

-- Get jobs with thumbnails for admin panel
CREATE OR REPLACE VIEW admin_panel_jobs AS
SELECT
    job_id,
    status,
    script,
    thumb_url,
    created_at,
    updated_at,
    meta->>'duration' as duration,
    meta->>'preset' as preset,
    (SELECT amount_cents FROM video_costs WHERE job_id = vj.job_id LIMIT 1) as cost_cents
FROM video_jobs vj
WHERE created_at >= NOW() - INTERVAL '30 days'
ORDER BY created_at DESC;

-- Get storage usage statistics
CREATE OR REPLACE VIEW storage_usage_stats AS
SELECT
    meta->>'storage_type' as storage_type,
    COUNT(*) as job_count,
    SUM((meta->>'size_bytes')::bigint) as total_bytes,
    AVG((meta->>'size_bytes')::bigint) as avg_file_size_bytes,
    SUM((meta->>'duration')::float) as total_duration_seconds
FROM video_jobs
WHERE meta IS NOT NULL
AND meta->>'size_bytes' IS NOT NULL
GROUP BY meta->>'storage_type';

-- ============================================
-- BILLING EXPORT FUNCTIONS
-- ============================================

-- Function to generate billing CSV data for a month
CREATE OR REPLACE FUNCTION generate_monthly_billing_csv(target_month text)
RETURNS TABLE (
    job_id text,
    created_at timestamptz,
    tts_seconds numeric,
    processing_seconds numeric,
    storage_mb numeric,
    amount_cents integer,
    preset text,
    duration_seconds numeric
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        vj.job_id::text,
        vj.created_at,
        vc.tts_seconds,
        vc.processing_seconds,
        vc.storage_mb,
        vc.amount_cents,
        COALESCE(vj.meta->>'preset', 'unknown') as preset,
        (vj.meta->>'duration')::numeric as duration_seconds
    FROM video_jobs vj
    JOIN video_costs vc ON vj.job_id = vc.job_id
    WHERE to_char(vj.created_at, 'YYYY-MM') = target_month
    ORDER BY vj.created_at;
END;
$$ LANGUAGE plpgsql;

-- Function to get billing summary for a month
CREATE OR REPLACE FUNCTION get_monthly_billing_summary(target_month text)
RETURNS TABLE (
    total_jobs bigint,
    completed_jobs bigint,
    total_cost_cents bigint,
    avg_cost_per_job_cents numeric,
    total_tts_seconds numeric,
    total_processing_seconds numeric,
    total_storage_mb numeric
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) as total_jobs,
        COUNT(CASE WHEN vj.status = 'completed' THEN 1 END) as completed_jobs,
        SUM(vc.amount_cents) as total_cost_cents,
        AVG(vc.amount_cents) as avg_cost_per_job_cents,
        SUM(vc.tts_seconds) as total_tts_seconds,
        SUM(vc.processing_seconds) as total_processing_seconds,
        SUM(vc.storage_mb) as total_storage_mb
    FROM video_jobs vj
    JOIN video_costs vc ON vj.job_id = vc.job_id
    WHERE to_char(vj.created_at, 'YYYY-MM') = target_month;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- HOUSEKEEPING FUNCTIONS
-- ============================================

-- Function to mark old jobs as expired
CREATE OR REPLACE FUNCTION mark_old_jobs_expired()
RETURNS INTEGER AS $$
DECLARE
    expired_count INTEGER := 0;
    completed_cutoff TIMESTAMPTZ;
    failed_cutoff TIMESTAMPTZ;
BEGIN
    -- Calculate cutoff dates
    completed_cutoff := NOW() - INTERVAL '30 days';
    failed_cutoff := NOW() - INTERVAL '7 days';

    -- Mark old completed jobs as expired
    UPDATE video_jobs
    SET status = 'expired'
    WHERE status = 'completed'
    AND created_at < completed_cutoff;

    GET DIAGNOSTICS expired_count = ROW_COUNT;

    -- Mark old failed jobs as expired
    UPDATE video_jobs
    SET status = 'expired'
    WHERE status = 'failed'
    AND created_at < failed_cutoff;

    expired_count := expired_count + ROW_COUNT;

    RETURN expired_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired job records (hard delete)
CREATE OR REPLACE FUNCTION cleanup_expired_jobs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- Delete expired jobs and related records
    DELETE FROM video_jobs WHERE status = 'expired';

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    -- Clean up orphaned records
    DELETE FROM video_assets WHERE job_id NOT IN (SELECT job_id FROM video_jobs);
    DELETE FROM video_costs WHERE job_id NOT IN (SELECT job_id FROM video_jobs);
    DELETE FROM video_webhooks WHERE job_id NOT IN (SELECT job_id FROM video_jobs);

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- GRANTS AND PERMISSIONS
-- ============================================

-- Grant necessary permissions for service role
GRANT ALL ON billing_exports TO service_role;
GRANT SELECT ON video_jobs TO service_role;
GRANT SELECT ON video_assets TO service_role;
GRANT SELECT ON video_costs TO service_role;
GRANT SELECT ON video_webhooks TO service_role;

-- Grant read permissions for authenticated users
GRANT SELECT ON billing_exports TO authenticated;
GRANT SELECT ON video_jobs TO authenticated;
GRANT SELECT ON video_assets TO authenticated;
GRANT SELECT ON video_costs TO authenticated;
GRANT SELECT ON video_webhooks TO authenticated;

-- ============================================
-- SAMPLE DATA FOR TESTING
-- ============================================

-- Insert sample billing export record for testing
INSERT INTO billing_exports (month, rows_count, amount_cents, file_url)
VALUES ('2025-01', 0, 0, 'https://example.com/billing_2025-01.csv')
ON CONFLICT (month) DO NOTHING;

-- ============================================
-- COMPLETION MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '✅ AutoPro Video Engine Phase 7 Database Schema Applied!';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 CDN and billing enhancements completed:';
    RAISE NOTICE '   • Enhanced video_jobs with thumb_url and meta columns';
    RAISE NOTICE '   • billing_exports table for audit trail';
    RAISE NOTICE '   • Performance indexes for metadata queries';
    RAISE NOTICE '   • RLS policies for billing data';
    RAISE NOTICE '   • Views for monitoring and admin panel';
    RAISE NOTICE '   • Functions for billing export and housekeeping';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Database ready for CDN and billing features!';
    RAISE NOTICE '';
END $$;