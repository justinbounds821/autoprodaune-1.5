-- ===================================================
-- AutoPro Daune - Complete Database Schema for Supabase
-- ===================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable Row Level Security
ALTER DATABASE postgres SET "app.settings.jwt_secret" TO 'your-jwt-secret';

-- ===================================================
-- CORE BUSINESS TABLES
-- ===================================================

-- Leads table - Central lead management
CREATE TABLE IF NOT EXISTS leads (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT,
    phone_number TEXT,
    email TEXT,
    source TEXT NOT NULL, -- 'tiktok', 'facebook', 'instagram', 'whatsapp', 'referral', 'direct'
    source_post_id TEXT, -- Reference to social media post
    lead_type TEXT DEFAULT 'crash_claim', -- 'crash_claim', 'insurance_dispute', 'consultation'
    status TEXT DEFAULT 'new', -- 'new', 'contacted', 'qualified', 'converted', 'closed'
    priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high'
    notes TEXT,
    details TEXT, -- Extended information about the lead
    metadata JSONB DEFAULT '{}', -- Flexible data storage
    assigned_to TEXT, -- Who handles this lead (e.g., 'manole')
    estimated_value DECIMAL(10,2) DEFAULT 0, -- Estimated claim value
    probability INTEGER DEFAULT 50, -- Conversion probability %
    follow_up_date TIMESTAMPTZ,
    contacted_at TIMESTAMPTZ,
    converted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Lead activities - Timeline and notes
CREATE TABLE IF NOT EXISTS lead_activities (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL, -- 'note', 'email', 'call', 'sms', 'meeting', 'status_change'
    title TEXT,
    description TEXT,
    metadata JSONB DEFAULT '{}', -- Extra data like email subject, call duration, etc.
    performed_by TEXT, -- User who performed the activity
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lead_activities_lead_id ON lead_activities(lead_id);
CREATE INDEX IF NOT EXISTS idx_lead_activities_created_at ON lead_activities(created_at DESC);

-- Lead attachments - physical files uploaded for a lead
CREATE TABLE IF NOT EXISTS lead_attachments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_url TEXT NOT NULL,
    storage_key TEXT,
    content_type TEXT,
    file_size BIGINT,
    uploaded_by TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lead_attachments_lead_id ON lead_attachments(lead_id);
CREATE INDEX IF NOT EXISTS idx_lead_attachments_created_at ON lead_attachments(created_at DESC);

-- Lead status history - conversion funnel tracking
CREATE TABLE IF NOT EXISTS lead_status_history (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    previous_status TEXT,
    new_status TEXT NOT NULL,
    changed_by TEXT,
    notes TEXT,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lead_status_history_lead_id ON lead_status_history(lead_id);
CREATE INDEX IF NOT EXISTS idx_lead_status_history_changed_at ON lead_status_history(changed_at DESC);

-- Lead assignments - track ownership changes
CREATE TABLE IF NOT EXISTS lead_assignments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    assigned_to TEXT NOT NULL,
    assigned_to_email TEXT,
    assigned_by TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lead_assignments_lead_id ON lead_assignments(lead_id);

-- Referrals table - 200 LEI referral system
CREATE TABLE IF NOT EXISTS referrals (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    referrer_phone TEXT NOT NULL,
    referrer_name TEXT,
    referred_phone TEXT NOT NULL,
    referred_name TEXT,
    referral_code TEXT UNIQUE, -- Unique referral tracking code
    status TEXT DEFAULT 'pending', -- 'pending', 'qualified', 'completed', 'cancelled'
    reward_amount DECIMAL(10,2) DEFAULT 200.00,
    currency TEXT DEFAULT 'LEI',
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    qualified_at TIMESTAMPTZ, -- When referral meets qualification criteria
    converted_at TIMESTAMPTZ, -- When referred lead becomes paying client
    rewarded_at TIMESTAMPTZ, -- When reward was paid out
    payout_method TEXT, -- 'bank_transfer', 'cash', 'credit'
    payout_details JSONB DEFAULT '{}', -- Bank details, etc.
    commission_rate DECIMAL(5,2) DEFAULT 200.00, -- LEI amount or percentage
    tracking_data JSONB DEFAULT '{}', -- UTM parameters, etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Social media posts tracking
CREATE TABLE IF NOT EXISTS social_posts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT,
    content TEXT,
    platforms TEXT[] DEFAULT '{}', -- ['tiktok', 'facebook', 'instagram']
    video_url TEXT,
    thumbnail_url TEXT,
    hashtags TEXT[] DEFAULT '{}',
    status TEXT DEFAULT 'scheduled', -- 'scheduled', 'published', 'failed', 'archived'
    template_type TEXT, -- 'educational', 'testimonial', 'promotional'
    target_audience TEXT, -- 'young_drivers', 'accident_victims', 'general'

    -- Performance metrics
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    engagement INTEGER DEFAULT 0, -- Total engagement count
    clicks INTEGER DEFAULT 0, -- Link clicks
    leads_generated INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2) DEFAULT 0,

    -- Revenue tracking
    revenue_generated DECIMAL(10,2) DEFAULT 0,
    cost_per_lead DECIMAL(10,2) DEFAULT 0,

    -- Scheduling
    scheduled_for TIMESTAMPTZ,
    posted_at TIMESTAMPTZ,

    -- Metadata
    post_metadata JSONB DEFAULT '{}',
    performance_data JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Video generation and processing queue
CREATE TABLE IF NOT EXISTS video_jobs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    client_job_id TEXT UNIQUE NOT NULL,
    filename TEXT,
    template_type TEXT, -- 'educational', 'testimonial', 'promotional', 'manole'
    status TEXT DEFAULT 'queued', -- 'queued', 'processing', 'completed', 'failed', 'cancelled'
    priority INTEGER DEFAULT 5, -- 1 (highest) to 10 (lowest)
    progress INTEGER DEFAULT 0, -- 0-100%

    -- Video specifications
    duration_seconds INTEGER DEFAULT 60,
    resolution TEXT DEFAULT '1080x1920', -- 9:16 for mobile
    format TEXT DEFAULT 'mp4',
    quality TEXT DEFAULT 'high',

    -- Content data
    script_data JSONB DEFAULT '{}',
    visual_elements JSONB DEFAULT '{}',
    audio_elements JSONB DEFAULT '{}',

    -- Processing info
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    file_size_mb DECIMAL(10,2),
    output_url TEXT,
    thumbnail_url TEXT,

    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- WhatsApp conversations and message tracking
CREATE TABLE IF NOT EXISTS whatsapp_conversations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    phone_number TEXT NOT NULL,
    contact_name TEXT,
    conversation_type TEXT DEFAULT 'support', -- 'support', 'lead', 'testimonial', 'document'
    status TEXT DEFAULT 'active', -- 'active', 'resolved', 'escalated', 'archived'
    priority TEXT DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'

    -- Routing and assignment
    assigned_to TEXT, -- 'bot', 'manole', 'support_team'
    escalated_to TEXT,
    escalation_reason TEXT,

    -- Lead connection
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,

    -- Conversation metadata
    intent TEXT, -- 'claim_inquiry', 'document_upload', 'testimonial', 'support'
    sentiment TEXT DEFAULT 'neutral', -- 'positive', 'neutral', 'negative'
    language TEXT DEFAULT 'ro',

    -- Metrics
    message_count INTEGER DEFAULT 0,
    response_time_avg INTEGER, -- Average response time in seconds
    resolution_time INTEGER, -- Time to resolution in seconds
    satisfaction_score INTEGER, -- 1-5 rating

    -- Important timestamps
    last_message_at TIMESTAMPTZ,
    first_response_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Individual WhatsApp messages
CREATE TABLE IF NOT EXISTS whatsapp_messages (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    conversation_id UUID REFERENCES whatsapp_conversations(id) ON DELETE CASCADE,
    message_id TEXT, -- WhatsApp message ID
    direction TEXT NOT NULL, -- 'inbound', 'outbound'
    sender_phone TEXT,
    recipient_phone TEXT,

    -- Message content
    message_type TEXT DEFAULT 'text', -- 'text', 'image', 'document', 'audio', 'video'
    content TEXT,
    media_url TEXT,
    media_type TEXT,

    -- Processing status
    status TEXT DEFAULT 'received', -- 'received', 'processed', 'replied', 'escalated'
    processed_by TEXT, -- 'bot', 'manole', 'human'

    -- Bot processing
    intent_detected TEXT,
    confidence_score DECIMAL(3,2), -- 0-1 confidence in intent detection
    automated_response BOOLEAN DEFAULT FALSE,

    -- Response tracking
    response_time INTEGER, -- Time to respond in seconds
    responded_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Document uploads and processing
CREATE TABLE IF NOT EXISTS document_uploads (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    conversation_id UUID REFERENCES whatsapp_conversations(id) ON DELETE SET NULL,

    -- File information
    filename TEXT NOT NULL,
    original_filename TEXT,
    file_path TEXT,
    file_url TEXT,
    file_size INTEGER,
    file_type TEXT,
    mime_type TEXT,

    -- Document classification
    document_type TEXT, -- 'police_report', 'insurance_policy', 'damage_photos', 'id_document', 'other'
    confidence_score DECIMAL(3,2),

    -- Processing status
    status TEXT DEFAULT 'uploaded', -- 'uploaded', 'processing', 'processed', 'failed'
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,

    -- Extracted data
    extracted_data JSONB DEFAULT '{}',
    ocr_text TEXT,

    -- Validation
    is_valid BOOLEAN,
    validation_errors TEXT[],

    -- Security
    encrypted BOOLEAN DEFAULT FALSE,
    access_level TEXT DEFAULT 'private', -- 'private', 'internal', 'public'

    -- Metadata
    metadata JSONB DEFAULT '{}',
    upload_source TEXT DEFAULT 'whatsapp', -- 'whatsapp', 'web', 'email'

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===================================================
-- AUTOMATION AND CONFIGURATION TABLES
-- ===================================================

-- Automation configuration and scheduling
CREATE TABLE IF NOT EXISTS automation_config (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    config_key TEXT UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    environment TEXT DEFAULT 'production', -- 'development', 'production'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Content templates for video generation
CREATE TABLE IF NOT EXISTS content_templates (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    template_type TEXT NOT NULL, -- 'educational', 'testimonial', 'promotional'
    category TEXT, -- 'crash_claims', 'insurance_tips', 'success_stories'

    -- Template content
    title_template TEXT,
    script_template TEXT,
    visual_elements JSONB DEFAULT '{}',
    audio_elements JSONB DEFAULT '{}',

    -- Configuration
    duration_range INTEGER[] DEFAULT '{30,90}', -- Min/max seconds
    target_platforms TEXT[] DEFAULT '{}',
    hashtag_templates TEXT[] DEFAULT '{}',

    -- Performance tracking
    usage_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0,
    avg_engagement DECIMAL(10,2) DEFAULT 0,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance metrics and KPIs
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    metric_date DATE NOT NULL,
    metric_type TEXT NOT NULL, -- 'daily', 'weekly', 'monthly'

    -- Lead metrics
    leads_generated INTEGER DEFAULT 0,
    leads_converted INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2) DEFAULT 0,

    -- Social media metrics
    posts_published INTEGER DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    total_engagement INTEGER DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,

    -- Revenue metrics
    revenue_generated DECIMAL(10,2) DEFAULT 0,
    referral_rewards_paid DECIMAL(10,2) DEFAULT 0,
    cost_per_lead DECIMAL(10,2) DEFAULT 0,
    return_on_investment DECIMAL(5,2) DEFAULT 0,

    -- WhatsApp metrics
    whatsapp_conversations INTEGER DEFAULT 0,
    avg_response_time INTEGER DEFAULT 0,
    satisfaction_score DECIMAL(3,2) DEFAULT 0,

    -- Video metrics
    videos_generated INTEGER DEFAULT 0,
    video_completion_rate DECIMAL(5,2) DEFAULT 0,

    -- Detailed breakdown
    metrics_data JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- System logs and audit trail
CREATE TABLE IF NOT EXISTS system_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    level TEXT NOT NULL, -- 'debug', 'info', 'warning', 'error', 'critical'
    category TEXT, -- 'automation', 'whatsapp', 'video', 'leads', 'referrals'
    message TEXT NOT NULL,
    details JSONB DEFAULT '{}',

    -- Context
    user_id TEXT,
    session_id TEXT,
    request_id TEXT,

    -- Source
    source_service TEXT, -- 'api', 'automation', 'whatsapp_bot'
    source_function TEXT,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===================================================
-- INDEXES FOR PERFORMANCE
-- ===================================================

-- Leads indexes
CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(phone_number);
CREATE INDEX IF NOT EXISTS idx_leads_follow_up_date ON leads(follow_up_date);

-- Referrals indexes
CREATE INDEX IF NOT EXISTS idx_referrals_code ON referrals(referral_code);
CREATE INDEX IF NOT EXISTS idx_referrals_referrer_phone ON referrals(referrer_phone);
CREATE INDEX IF NOT EXISTS idx_referrals_referred_phone ON referrals(referred_phone);
CREATE INDEX IF NOT EXISTS idx_referrals_status ON referrals(status);
CREATE INDEX IF NOT EXISTS idx_referrals_created_at ON referrals(created_at);

-- Social posts indexes
CREATE INDEX IF NOT EXISTS idx_social_posts_platforms ON social_posts USING GIN(platforms);
CREATE INDEX IF NOT EXISTS idx_social_posts_status ON social_posts(status);
CREATE INDEX IF NOT EXISTS idx_social_posts_template_type ON social_posts(template_type);
CREATE INDEX IF NOT EXISTS idx_social_posts_posted_at ON social_posts(posted_at);
CREATE INDEX IF NOT EXISTS idx_social_posts_created_at ON social_posts(created_at);

-- Video jobs indexes
CREATE INDEX IF NOT EXISTS idx_video_jobs_status ON video_jobs(status);
CREATE INDEX IF NOT EXISTS idx_video_jobs_client_job_id ON video_jobs(client_job_id);
CREATE INDEX IF NOT EXISTS idx_video_jobs_created_at ON video_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_video_jobs_priority ON video_jobs(priority);

-- WhatsApp indexes
CREATE INDEX IF NOT EXISTS idx_whatsapp_conversations_phone ON whatsapp_conversations(phone_number);
CREATE INDEX IF NOT EXISTS idx_whatsapp_conversations_status ON whatsapp_conversations(status);
CREATE INDEX IF NOT EXISTS idx_whatsapp_conversations_created_at ON whatsapp_conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_conversation_id ON whatsapp_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_created_at ON whatsapp_messages(created_at);

-- Document uploads indexes
CREATE INDEX IF NOT EXISTS idx_document_uploads_lead_id ON document_uploads(lead_id);
CREATE INDEX IF NOT EXISTS idx_document_uploads_conversation_id ON document_uploads(conversation_id);
CREATE INDEX IF NOT EXISTS idx_document_uploads_document_type ON document_uploads(document_type);
CREATE INDEX IF NOT EXISTS idx_document_uploads_status ON document_uploads(status);

-- Performance metrics indexes
CREATE INDEX IF NOT EXISTS idx_performance_metrics_date ON performance_metrics(metric_date);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_type ON performance_metrics(metric_type);

-- System logs indexes
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_category ON system_logs(category);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);

-- ===================================================
-- VIEWS FOR COMMON QUERIES
-- ===================================================

-- Lead conversion funnel view
CREATE OR REPLACE VIEW lead_funnel_view AS
SELECT
    source,
    COUNT(*) as total_leads,
    COUNT(CASE WHEN status = 'contacted' THEN 1 END) as contacted_leads,
    COUNT(CASE WHEN status = 'qualified' THEN 1 END) as qualified_leads,
    COUNT(CASE WHEN status = 'converted' THEN 1 END) as converted_leads,
    ROUND(
        COUNT(CASE WHEN status = 'converted' THEN 1 END)::decimal /
        NULLIF(COUNT(*), 0) * 100, 2
    ) as conversion_rate
FROM leads
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY source;

-- Daily performance dashboard view
CREATE OR REPLACE VIEW daily_performance_view AS
SELECT
    DATE(created_at) as date,
    COUNT(CASE WHEN source = 'tiktok' THEN 1 END) as tiktok_leads,
    COUNT(CASE WHEN source = 'facebook' THEN 1 END) as facebook_leads,
    COUNT(CASE WHEN source = 'instagram' THEN 1 END) as instagram_leads,
    COUNT(CASE WHEN source = 'whatsapp' THEN 1 END) as whatsapp_leads,
    COUNT(CASE WHEN source = 'referral' THEN 1 END) as referral_leads,
    COUNT(*) as total_leads,
    COUNT(CASE WHEN status = 'converted' THEN 1 END) as converted_leads
FROM leads
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY DATE(created_at) DESC;

-- Referral leaderboard view
CREATE OR REPLACE VIEW referral_leaderboard_view AS
SELECT
    referrer_phone,
    referrer_name,
    COUNT(*) as total_referrals,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_referrals,
    SUM(CASE WHEN status = 'completed' THEN reward_amount ELSE 0 END) as total_earnings,
    ROUND(
        COUNT(CASE WHEN status = 'completed' THEN 1 END)::decimal /
        NULLIF(COUNT(*), 0) * 100, 2
    ) as success_rate
FROM referrals
WHERE created_at >= NOW() - INTERVAL '90 days'
GROUP BY referrer_phone, referrer_name
HAVING COUNT(*) >= 1
ORDER BY total_earnings DESC, completed_referrals DESC;

-- ===================================================
-- FUNCTIONS AND TRIGGERS
-- ===================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_referrals_updated_at BEFORE UPDATE ON referrals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_social_posts_updated_at BEFORE UPDATE ON social_posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_video_jobs_updated_at BEFORE UPDATE ON video_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_whatsapp_conversations_updated_at BEFORE UPDATE ON whatsapp_conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically create referral code
CREATE OR REPLACE FUNCTION generate_referral_code()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.referral_code IS NULL THEN
        NEW.referral_code := 'REF' || UPPER(SUBSTRING(MD5(NEW.referrer_phone || NOW()::text), 1, 8));
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER generate_referral_code_trigger BEFORE INSERT ON referrals
    FOR EACH ROW EXECUTE FUNCTION generate_referral_code();

-- ===================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ===================================================

-- Enable RLS on sensitive tables
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE referrals ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_uploads ENABLE ROW LEVEL SECURITY;

-- Basic policies (can be customized based on authentication system)
CREATE POLICY "Allow service access to leads" ON leads
    FOR ALL USING (true); -- Replace with proper JWT claims

CREATE POLICY "Allow service access to referrals" ON referrals
    FOR ALL USING (true); -- Replace with proper JWT claims

-- ===================================================
-- INITIAL DATA SEEDING
-- ===================================================

-- Insert default automation configuration
INSERT INTO automation_config (config_key, config_value, description) VALUES
('daily_posting_schedule', '{"enabled": true, "times": ["09:00", "15:00", "21:00"], "timezone": "Europe/Bucharest"}', 'Daily video posting schedule'),
('content_templates', '{"educational": {"enabled": true, "weight": 40}, "testimonial": {"enabled": true, "weight": 30}, "promotional": {"enabled": true, "weight": 30}}', 'Content template distribution'),
('referral_system', '{"enabled": true, "reward_amount": 200, "currency": "LEI", "minimum_payout": 200}', 'Referral system configuration'),
('whatsapp_bot', '{"enabled": true, "auto_response": true, "escalation_keywords": ["urgent", "complaint", "manager"], "manole_phone": "+40723456789"}', 'WhatsApp bot configuration'),
('social_platforms', '{"tiktok": {"enabled": true, "priority": 1}, "facebook": {"enabled": true, "priority": 2}, "instagram": {"enabled": true, "priority": 3}}', 'Social media platform settings')
ON CONFLICT (config_key) DO NOTHING;

-- Insert default content templates
INSERT INTO content_templates (name, template_type, category, title_template, script_template, target_platforms, hashtag_templates) VALUES
('Educational - Crash Claims', 'educational', 'crash_claims',
 'Cum obții despăgubiri în {timeframe}',
 'Ai avut un accident? Iată pașii pentru a obține despăgubirile: 1. Documentează totul 2. Contactează AutoPro Daune 3. Primești banii în 24-48h',
 ARRAY['tiktok', 'facebook', 'instagram'],
 ARRAY['#AutoProDaune', '#Despagubiri', '#Accident', '#Asigurari', '#Romania']),

('Testimonial - Success Story', 'testimonial', 'success_stories',
 'Client mulțumit: {client_result}',
 'Mărturie reală: "{testimonial_text}" - Am rezolvat cazul în doar {timeframe}. Tu când îți rezolvi problema?',
 ARRAY['tiktok', 'facebook', 'instagram'],
 ARRAY['#TestimonialReal', '#ClientMultumit', '#AutoProDaune', '#Succes']),

('Promotional - Referral', 'promotional', 'referral_program',
 'Câștigă {reward_amount} LEI ușor!',
 'Pentru fiecare prieten recomandat care devine client, tu câștigi {reward_amount} LEI! Link în bio pentru înscriere.',
 ARRAY['tiktok', 'facebook', 'instagram'],
 ARRAY['#CastigaBani', '#Recomanda', '#200Lei', '#AutoProDaune', '#ProgramRecomandari'])
ON CONFLICT DO NOTHING;

-- Insert sample performance metrics for the current month
INSERT INTO performance_metrics (metric_date, metric_type, leads_generated, posts_published, total_views, total_engagement)
SELECT
    CURRENT_DATE - INTERVAL '1 day' * generate_series(0, 29),
    'daily',
    (RANDOM() * 20 + 5)::INTEGER, -- 5-25 leads per day
    3, -- 3 posts per day as planned
    (RANDOM() * 5000 + 1000)::INTEGER, -- 1000-6000 views
    (RANDOM() * 500 + 50)::INTEGER -- 50-550 engagement
ON CONFLICT DO NOTHING;

-- ===================================================
-- MAINTENANCE AND CLEANUP JOBS
-- ===================================================

-- Function to clean old logs (keep last 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_logs()
RETURNS void AS $$
BEGIN
    DELETE FROM system_logs
    WHERE created_at < NOW() - INTERVAL '30 days';

    RAISE NOTICE 'Cleaned up old system logs';
END;
$$ LANGUAGE plpgsql;

-- Function to update performance metrics daily
CREATE OR REPLACE FUNCTION update_daily_metrics()
RETURNS void AS $$
DECLARE
    yesterday DATE := CURRENT_DATE - INTERVAL '1 day';
    leads_count INTEGER;
    posts_count INTEGER;
    total_views_sum INTEGER;
    total_engagement_sum INTEGER;
BEGIN
    -- Calculate metrics for yesterday
    SELECT COUNT(*) INTO leads_count FROM leads WHERE DATE(created_at) = yesterday;
    SELECT COUNT(*) INTO posts_count FROM social_posts WHERE DATE(posted_at) = yesterday;
    SELECT COALESCE(SUM(views), 0) INTO total_views_sum FROM social_posts WHERE DATE(posted_at) = yesterday;
    SELECT COALESCE(SUM(engagement), 0) INTO total_engagement_sum FROM social_posts WHERE DATE(posted_at) = yesterday;

    -- Insert or update metrics
    INSERT INTO performance_metrics (metric_date, metric_type, leads_generated, posts_published, total_views, total_engagement)
    VALUES (yesterday, 'daily', leads_count, posts_count, total_views_sum, total_engagement_sum)
    ON CONFLICT (metric_date, metric_type) DO UPDATE SET
        leads_generated = EXCLUDED.leads_generated,
        posts_published = EXCLUDED.posts_published,
        total_views = EXCLUDED.total_views,
        total_engagement = EXCLUDED.total_engagement;

    RAISE NOTICE 'Updated daily metrics for %', yesterday;
END;
$$ LANGUAGE plpgsql;

-- ===================================================
-- COMPLETION MESSAGE
-- ===================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '✅ AutoPro Daune Database Schema Created Successfully!';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Tables Created:';
    RAISE NOTICE '   • leads (lead management)';
    RAISE NOTICE '   • referrals (200 LEI referral system)';
    RAISE NOTICE '   • social_posts (content tracking)';
    RAISE NOTICE '   • video_jobs (video automation)';
    RAISE NOTICE '   • whatsapp_conversations (WhatsApp bot)';
    RAISE NOTICE '   • whatsapp_messages (message tracking)';
    RAISE NOTICE '   • document_uploads (document processing)';
    RAISE NOTICE '   • automation_config (system configuration)';
    RAISE NOTICE '   • content_templates (video templates)';
    RAISE NOTICE '   • performance_metrics (analytics)';
    RAISE NOTICE '   • system_logs (audit trail)';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Ready for AutoPro Daune deployment!';
    RAISE NOTICE '';
END $$;