-- ============================================
-- QUICK FIX: Create Missing Tables
-- Run this in Supabase SQL Editor NOW
-- ============================================

-- 1. automation_config (CRITICAL - fixes scheduler error)
CREATE TABLE IF NOT EXISTS automation_config (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    config_key TEXT UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    environment TEXT DEFAULT 'production',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default config
INSERT INTO automation_config (config_key, config_value, description) VALUES
('daily_posting_schedule', '{"enabled": true, "times": ["09:00", "15:00", "21:00"], "timezone": "Europe/Bucharest"}', 'Daily video posting schedule'),
('content_templates', '{"educational": {"enabled": true, "weight": 40}, "testimonial": {"enabled": true, "weight": 30}, "promotional": {"enabled": true, "weight": 30}}', 'Content template distribution'),
('referral_system', '{"enabled": true, "reward_amount": 200, "currency": "LEI", "minimum_payout": 200}', 'Referral system configuration')
ON CONFLICT (config_key) DO NOTHING;

-- 2. performance_metrics (CRITICAL - fixes daily metrics error)
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    metric_date DATE NOT NULL,
    metric_type TEXT NOT NULL,

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

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(metric_date, metric_type)
);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_date ON performance_metrics(metric_date);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_type ON performance_metrics(metric_type);

-- 3. whatsapp_conversations
CREATE TABLE IF NOT EXISTS whatsapp_conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    phone_number TEXT NOT NULL,
    contact_name TEXT,
    conversation_type TEXT DEFAULT 'support',
    status TEXT DEFAULT 'active',
    priority TEXT DEFAULT 'normal',

    assigned_to TEXT,
    escalated_to TEXT,
    escalation_reason TEXT,

    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,

    intent TEXT,
    sentiment TEXT DEFAULT 'neutral',
    language TEXT DEFAULT 'ro',

    message_count INTEGER DEFAULT 0,
    response_time_avg INTEGER,
    resolution_time INTEGER,
    satisfaction_score INTEGER,

    last_message_at TIMESTAMPTZ,
    first_response_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,

    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_whatsapp_conversations_phone ON whatsapp_conversations(phone_number);
CREATE INDEX IF NOT EXISTS idx_whatsapp_conversations_status ON whatsapp_conversations(status);

-- 4. content_templates
CREATE TABLE IF NOT EXISTS content_templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    template_type TEXT NOT NULL,
    category TEXT,

    title_template TEXT,
    script_template TEXT,
    visual_elements JSONB DEFAULT '{}',
    audio_elements JSONB DEFAULT '{}',

    duration_range INTEGER[] DEFAULT '{30,90}',
    target_platforms TEXT[] DEFAULT '{}',
    hashtag_templates TEXT[] DEFAULT '{}',

    usage_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0,
    avg_engagement DECIMAL(10,2) DEFAULT 0,

    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default templates
INSERT INTO content_templates (name, template_type, category, title_template, script_template, target_platforms, hashtag_templates) VALUES
('Educational - Crash Claims', 'educational', 'crash_claims',
 'Cum obții despăgubiri în {timeframe}',
 'Ai avut un accident? Iată pașii pentru a obține despăgubirile: 1. Documentează totul 2. Contactează AutoPro Daune 3. Primești banii în 24-48h',
 ARRAY['tiktok', 'facebook', 'instagram'],
 ARRAY['#AutoProDaune', '#Despagubiri', '#Accident', '#Asigurari', '#Romania']),

('Testimonial - Success Story', 'testimonial', 'success_stories',
 'Client mulțumit: {client_result}',
 'Mărturie reală: Am rezolvat cazul în doar {timeframe}. Tu când îți rezolvi problema?',
 ARRAY['tiktok', 'facebook', 'instagram'],
 ARRAY['#TestimonialReal', '#ClientMultumit', '#AutoProDaune', '#Succes']),

('Promotional - Referral', 'promotional', 'referral_program',
 'Câștigă {reward_amount} LEI ușor!',
 'Pentru fiecare prieten recomandat care devine client, tu câștigi 200 LEI! Link în bio.',
 ARRAY['tiktok', 'facebook', 'instagram'],
 ARRAY['#CastigaBani', '#Recomanda', '#200Lei', '#AutoProDaune'])
ON CONFLICT DO NOTHING;

-- 5. system_logs
CREATE TABLE IF NOT EXISTS system_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    level TEXT NOT NULL,
    category TEXT,
    message TEXT NOT NULL,
    details JSONB DEFAULT '{}',

    user_id TEXT,
    session_id TEXT,
    request_id TEXT,

    source_service TEXT,
    source_function TEXT,

    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_category ON system_logs(category);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);

-- Update triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_automation_config_updated_at BEFORE UPDATE ON automation_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_whatsapp_conversations_updated_at BEFORE UPDATE ON whatsapp_conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_templates_updated_at BEFORE UPDATE ON content_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 6. lead_attachments + lead history tables
CREATE TABLE IF NOT EXISTS lead_attachments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
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

CREATE TABLE IF NOT EXISTS lead_status_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    previous_status TEXT,
    new_status TEXT NOT NULL,
    changed_by TEXT,
    notes TEXT,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lead_status_history_lead_id ON lead_status_history(lead_id);
CREATE INDEX IF NOT EXISTS idx_lead_status_history_changed_at ON lead_status_history(changed_at DESC);

CREATE TABLE IF NOT EXISTS lead_assignments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    assigned_to TEXT NOT NULL,
    assigned_to_email TEXT,
    assigned_by TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lead_assignments_lead_id ON lead_assignments(lead_id);

-- Success message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '✅ Missing tables created successfully!';
    RAISE NOTICE '';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '   • automation_config (fixes scheduler error)';
    RAISE NOTICE '   • performance_metrics (fixes daily metrics error)';
    RAISE NOTICE '   • whatsapp_conversations';
    RAISE NOTICE '   • content_templates';
    RAISE NOTICE '   • system_logs';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Backend should now start without errors!';
    RAISE NOTICE '';
END $$;