-- ============================================
-- AutoPro Daune - Complete Database Schema
-- REAL Production Schema (Not Mocks)
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- LEADS MODULE
-- ============================================

CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    source TEXT NOT NULL CHECK (source IN ('tiktok', 'youtube', 'instagram', 'facebook', 'referral', 'direct', 'website')),
    status TEXT DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'qualified', 'converted', 'lost', 'deleted')),
    score INTEGER DEFAULT 0 CHECK (score >= 0 AND score <= 100),
    estimated_value DECIMAL(10,2) DEFAULT 5000.00,
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lead_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL CHECK (activity_type IN ('note', 'status_change', 'call', 'email', 'meeting', 'sms', 'whatsapp')),
    title TEXT NOT NULL,
    description TEXT,
    performed_by UUID REFERENCES auth.users(id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- VIDEO GENERATION MODULE
-- ============================================

CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    script TEXT NOT NULL,
    provider TEXT NOT NULL CHECK (provider IN ('moviepy', 'heygen', 'pika', 'manole')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'generating', 'completed', 'failed')),
    video_url TEXT, -- R2 Cloudflare URL
    thumbnail_url TEXT,
    duration INTEGER, -- seconds
    file_size BIGINT, -- bytes
    format TEXT DEFAULT 'mp4',
    resolution TEXT DEFAULT '1280x720',
    fps INTEGER DEFAULT 25,
    provider_job_id TEXT, -- HeyGen/Pika job ID for tracking
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    generated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS video_generation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    job_id TEXT NOT NULL, -- Provider's job ID
    status TEXT DEFAULT 'pending',
    progress INTEGER DEFAULT 0, -- 0-100
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_details JSONB
);

-- ============================================
-- FINANCIAL TRACKING MODULE
-- ============================================

CREATE TABLE IF NOT EXISTS financial_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    type TEXT NOT NULL CHECK (type IN ('revenue', 'cost', 'refund', 'commission')),
    category TEXT NOT NULL,
    subcategory TEXT,
    amount DECIMAL(12,2) NOT NULL,
    currency TEXT DEFAULT 'RON',
    description TEXT,
    source TEXT, -- Which lead/video generated this
    metadata JSONB DEFAULT '{}',
    transaction_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS api_costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider TEXT NOT NULL CHECK (provider IN ('heygen', 'pika', 'elevenlabs', 'openai', 'anthropic')),
    operation_type TEXT NOT NULL,
    units_consumed DECIMAL(10,4), -- API units (tokens, minutes, etc.)
    cost_per_unit DECIMAL(10,6),
    total_cost DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS revenues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency TEXT DEFAULT 'RON',
    source TEXT NOT NULL, -- 'lead_conversion', 'referral_reward', etc.
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- SOCIAL MEDIA & AUTOMATION
-- ============================================

CREATE TABLE IF NOT EXISTS social_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id) ON DELETE SET NULL,
    platform TEXT NOT NULL CHECK (platform IN ('tiktok', 'instagram', 'facebook', 'youtube')),
    post_url TEXT,
    caption TEXT,
    hashtags TEXT[],
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'scheduled', 'posted', 'failed')),
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0.00, -- Percentage
    posted_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS automation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type TEXT NOT NULL CHECK (task_type IN ('video_generation', 'social_post', 'lead_nurture', 'email_send', 'data_sync')),
    status TEXT NOT NULL CHECK (status IN ('success', 'failed', 'pending', 'in_progress')),
    details TEXT,
    error_message TEXT,
    execution_time_ms INTEGER,
    metadata JSONB DEFAULT '{}',
    executed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS automation_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- REFERRAL SYSTEM
-- ============================================

CREATE TABLE IF NOT EXISTS referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    referred_email TEXT NOT NULL,
    referred_user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    code TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'registered', 'confirmed', 'rewarded', 'expired')),
    reward_amount DECIMAL(10,2) DEFAULT 200.00,
    currency TEXT DEFAULT 'RON',
    qualifying_action TEXT, -- What action confirms the referral
    created_at TIMESTAMPTZ DEFAULT NOW(),
    registered_at TIMESTAMPTZ,
    confirmed_at TIMESTAMPTZ,
    rewarded_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '90 days')
);

-- ============================================
-- USER PROFILES & SETTINGS
-- ============================================

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin', 'manager')),
    full_name TEXT,
    avatar_url TEXT,
    phone TEXT,
    company TEXT,
    position TEXT,
    preferences JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    notifications_enabled BOOLEAN DEFAULT true,
    email_notifications BOOLEAN DEFAULT true,
    sms_notifications BOOLEAN DEFAULT false,
    automation_enabled BOOLEAN DEFAULT true,
    daily_video_target INTEGER DEFAULT 3,
    preferred_posting_times TIME[] DEFAULT '{09:00,15:00,21:00}',
    timezone TEXT DEFAULT 'Europe/Bucharest',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- NOTIFICATIONS
-- ============================================

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('lead', 'video', 'financial', 'social', 'system')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    action_url TEXT,
    read BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    read_at TIMESTAMPTZ
);

-- ============================================
-- CONTENT TEMPLATES
-- ============================================

CREATE TABLE IF NOT EXISTS content_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('educational', 'testimonial', 'promotional', 'news', 'tutorial')),
    script_template TEXT NOT NULL,
    variables JSONB DEFAULT '[]', -- Array of variable names to replace
    active BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- PERFORMANCE INDEXES
-- ============================================

-- Leads indexes
CREATE INDEX IF NOT EXISTS idx_leads_user_id ON leads(user_id);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email) WHERE email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(phone) WHERE phone IS NOT NULL;

-- Videos indexes
CREATE INDEX IF NOT EXISTS idx_videos_user_id ON videos(user_id);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_provider ON videos(provider);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at DESC);

-- Financial indexes
CREATE INDEX IF NOT EXISTS idx_financial_user_id ON financial_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_financial_type ON financial_transactions(type);
CREATE INDEX IF NOT EXISTS idx_financial_date ON financial_transactions(transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_financial_category ON financial_transactions(category);

-- Social posts indexes
CREATE INDEX IF NOT EXISTS idx_social_platform ON social_posts(platform);
CREATE INDEX IF NOT EXISTS idx_social_status ON social_posts(status);
CREATE INDEX IF NOT EXISTS idx_social_posted_at ON social_posts(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_social_video_id ON social_posts(video_id);

-- Referrals indexes
CREATE INDEX IF NOT EXISTS idx_referrals_code ON referrals(code);
CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_referrals_status ON referrals(status);

-- Notifications indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS on all user-specific tables
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE referrals ENABLE ROW LEVEL SECURITY;

-- LEADS Policies
CREATE POLICY "Users can view own leads" ON leads
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own leads" ON leads
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own leads" ON leads
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own leads" ON leads
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all leads" ON leads
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_id = auth.uid() AND role = 'admin'
        )
    );

-- VIDEOS Policies
CREATE POLICY "Users can view own videos" ON videos
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own videos" ON videos
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Admins can view all videos" ON videos
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_id = auth.uid() AND role = 'admin'
        )
    );

-- FINANCIAL Policies
CREATE POLICY "Users can view own transactions" ON financial_transactions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all transactions" ON financial_transactions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_id = auth.uid() AND role = 'admin'
        )
    );

-- NOTIFICATIONS Policies
CREATE POLICY "Users can view own notifications" ON notifications
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own notifications" ON notifications
    FOR UPDATE USING (auth.uid() = user_id);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to relevant tables
CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate lead score automatically
CREATE OR REPLACE FUNCTION calculate_lead_score(lead_row leads)
RETURNS INTEGER AS $$
DECLARE
    score INTEGER := 0;
BEGIN
    -- Email: +10
    IF lead_row.email IS NOT NULL THEN
        score := score + 10;
    END IF;
    
    -- Phone: +10
    IF lead_row.phone IS NOT NULL THEN
        score := score + 10;
    END IF;
    
    -- Source quality
    score := score + CASE lead_row.source
        WHEN 'referral' THEN 30
        WHEN 'website' THEN 20
        WHEN 'tiktok' THEN 15
        WHEN 'youtube' THEN 15
        WHEN 'instagram' THEN 10
        WHEN 'facebook' THEN 10
        ELSE 5
    END;
    
    -- Engagement from metadata
    IF lead_row.metadata ? 'watched_video' AND (lead_row.metadata->>'watched_video')::boolean THEN
        score := score + 15;
    END IF;
    
    IF lead_row.metadata ? 'clicked_cta' AND (lead_row.metadata->>'clicked_cta')::boolean THEN
        score := score + 20;
    END IF;
    
    RETURN LEAST(score, 100); -- Cap at 100
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- INITIAL DATA / SEED DATA
-- ============================================

-- Insert default automation config
INSERT INTO automation_config (key, value, description) VALUES
('daily_video_target', '3', 'Number of videos to generate per day'),
('posting_schedule', '["09:00", "15:00", "21:00"]', 'Times to post content'),
('automation_enabled', 'true', 'Master switch for automation'),
('content_template_rotation', '{"educational": 40, "testimonial": 30, "promotional": 30}', 'Template usage percentages')
ON CONFLICT (key) DO NOTHING;

-- Insert default content templates
INSERT INTO content_templates (name, type, script_template, variables) VALUES
('Educational - RCA Basics', 'educational', 'Știați că {{percentage}}% dintre șoferi nu cunosc drepturile lor la despăgubiri RCA? AutoPro Daune vă ajută să obțineți {{amount}} lei în doar {{days}} zile! Contactați-ne pe WhatsApp!', '["percentage", "amount", "days"]'),
('Testimonial - Success Story', 'testimonial', 'Client mulțumit: "Am primit {{amount}} lei despăgubire în doar {{days}} zile! Mulțumesc AutoPro Daune!" - {{client_name}}', '["amount", "days", "client_name"]'),
('Promotional - Limited Offer', 'promotional', 'OFERTĂ SPECIALĂ! Evaluare GRATUITĂ a dosarului RCA! Contactați AutoPro Daune astăzi și aflați cât puteți primi! WhatsApp: {{phone}}', '["phone"]')
ON CONFLICT DO NOTHING;

-- ============================================
-- VIEWS FOR ANALYTICS
-- ============================================

-- Revenue summary view
CREATE OR REPLACE VIEW revenue_summary AS
SELECT
    DATE_TRUNC('day', created_at) as date,
    SUM(amount) as total_revenue,
    COUNT(*) as transaction_count,
    AVG(amount) as avg_transaction
FROM revenues
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date DESC;

-- Cost summary view
CREATE OR REPLACE VIEW cost_summary AS
SELECT
    provider,
    DATE_TRUNC('day', created_at) as date,
    SUM(total_cost) as daily_cost,
    SUM(units_consumed) as units_used
FROM api_costs
GROUP BY provider, DATE_TRUNC('day', created_at)
ORDER BY date DESC, provider;

-- Lead conversion funnel
CREATE OR REPLACE VIEW lead_funnel AS
SELECT
    source,
    COUNT(*) FILTER (WHERE status = 'new') as new_leads,
    COUNT(*) FILTER (WHERE status = 'contacted') as contacted,
    COUNT(*) FILTER (WHERE status = 'qualified') as qualified,
    COUNT(*) FILTER (WHERE status = 'converted') as converted,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'converted') / NULLIF(COUNT(*), 0), 2) as conversion_rate
FROM leads
WHERE status != 'deleted'
GROUP BY source;

-- ============================================
-- SCHEMA VERSION TRACKING
-- ============================================

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO schema_version (version, description) VALUES
(1, 'Initial complete schema with all modules')
ON CONFLICT (version) DO NOTHING;

-- Schema created successfully
SELECT 'AutoPro Daune database schema created successfully!' as status;
