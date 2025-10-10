-- AutoPro Daune 1.5 - Complete Database Schema
-- ===============================================
-- This schema supports all 11 tables mentioned in the blueprint

-- 1. LEADS TABLE - Core lead management
CREATE TABLE IF NOT EXISTS leads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    source VARCHAR(100) DEFAULT 'direct',
    status VARCHAR(50) DEFAULT 'new',
    notes TEXT,
    estimated_value DECIMAL(10,2) DEFAULT 5000.00,
    priority VARCHAR(20) DEFAULT 'medium',
    lead_score INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. REFERRALS TABLE - Referral system (200 LEI per referral)
CREATE TABLE IF NOT EXISTS referrals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    referrer_phone VARCHAR(50) NOT NULL,
    referrer_name VARCHAR(255),
    referred_phone VARCHAR(50) NOT NULL,
    referred_name VARCHAR(255),
    referral_code VARCHAR(50) UNIQUE,
    status VARCHAR(50) DEFAULT 'pending', -- pending, confirmed, paid
    reward_amount DECIMAL(10,2) DEFAULT 200.00,
    reward_currency VARCHAR(10) DEFAULT 'RON',
    conversion_date TIMESTAMP WITH TIME ZONE,
    payout_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. SOCIAL_POSTS TABLE - Social media content tracking
CREATE TABLE IF NOT EXISTS social_posts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    caption TEXT,
    hashtags TEXT[],
    template_type VARCHAR(50), -- educational, testimonial, promotional
    platforms TEXT[], -- tiktok, instagram, facebook, youtube
    video_url TEXT,
    image_url TEXT,
    status VARCHAR(50) DEFAULT 'draft', -- draft, scheduled, published, failed
    scheduled_for TIMESTAMP WITH TIME ZONE,
    published_at TIMESTAMP WITH TIME ZONE,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    engagement INTEGER DEFAULT 0,
    leads_generated INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. WHATSAPP_CONVERSATIONS TABLE - WhatsApp bot interactions
CREATE TABLE IF NOT EXISTS whatsapp_conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    phone_number VARCHAR(50) NOT NULL,
    contact_name VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active', -- active, completed, blocked
    last_message_at TIMESTAMP WITH TIME ZONE,
    message_count INTEGER DEFAULT 0,
    lead_id UUID REFERENCES leads(id),
    conversation_type VARCHAR(50) DEFAULT 'support', -- support, sales, referral
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. WHATSAPP_MESSAGES TABLE - Individual WhatsApp messages
CREATE TABLE IF NOT EXISTS whatsapp_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conversation_id UUID REFERENCES whatsapp_conversations(id),
    phone_number VARCHAR(50) NOT NULL,
    message_text TEXT,
    message_type VARCHAR(50) DEFAULT 'text', -- text, image, document, audio
    direction VARCHAR(20) NOT NULL, -- inbound, outbound
    status VARCHAR(50) DEFAULT 'sent', -- sent, delivered, read, failed
    media_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. VIDEO_JOBS TABLE - Video generation tracking
CREATE TABLE IF NOT EXISTS video_jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    job_type VARCHAR(50) NOT NULL, -- internal, heygen, pika
    script TEXT,
    template_type VARCHAR(50),
    provider VARCHAR(50), -- moviepy, heygen, pika, elevenlabs
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    video_url TEXT,
    thumbnail_url TEXT,
    duration_seconds INTEGER,
    file_size_bytes BIGINT,
    error_message TEXT,
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. AUTOMATION_CONFIG TABLE - Automation settings
CREATE TABLE IF NOT EXISTS automation_config (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. SYSTEM_LOGS TABLE - Application logging
CREATE TABLE IF NOT EXISTS system_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    level VARCHAR(20) NOT NULL, -- info, warning, error, debug
    category VARCHAR(50), -- automation, api, video, social, etc.
    message TEXT NOT NULL,
    details JSONB,
    source_service VARCHAR(50),
    source_function VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. PERFORMANCE_METRICS TABLE - Daily/weekly performance tracking
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    metric_date DATE NOT NULL,
    metric_type VARCHAR(50) DEFAULT 'daily', -- daily, weekly, monthly
    leads_generated INTEGER DEFAULT 0,
    posts_published INTEGER DEFAULT 0,
    videos_generated INTEGER DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    total_engagement INTEGER DEFAULT 0,
    whatsapp_conversations INTEGER DEFAULT 0,
    referral_rewards_paid DECIMAL(10,2) DEFAULT 0,
    revenue_generated DECIMAL(10,2) DEFAULT 0,
    costs_incurred DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(metric_date, metric_type)
);

-- 10. FINANCIAL_RECORDS TABLE - Revenue and cost tracking
CREATE TABLE IF NOT EXISTS financial_records (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    record_type VARCHAR(50) NOT NULL, -- revenue, cost, payout
    category VARCHAR(100), -- api_costs, marketing, referral_payout, lead_revenue
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'RON',
    description TEXT,
    reference_id UUID, -- Can reference leads, referrals, etc.
    reference_type VARCHAR(50), -- lead, referral, automation, etc.
    transaction_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 11. USER_SESSIONS TABLE - Authentication and user management
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID,
    email VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user', -- admin, user
    session_token VARCHAR(500),
    expires_at TIMESTAMP WITH TIME ZONE,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- INDEXES for performance
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(phone);

CREATE INDEX IF NOT EXISTS idx_referrals_referrer_phone ON referrals(referrer_phone);
CREATE INDEX IF NOT EXISTS idx_referrals_status ON referrals(status);
CREATE INDEX IF NOT EXISTS idx_referrals_created_at ON referrals(created_at);

CREATE INDEX IF NOT EXISTS idx_social_posts_created_at ON social_posts(created_at);
CREATE INDEX IF NOT EXISTS idx_social_posts_status ON social_posts(status);
CREATE INDEX IF NOT EXISTS idx_social_posts_template_type ON social_posts(template_type);

CREATE INDEX IF NOT EXISTS idx_whatsapp_conversations_phone ON whatsapp_conversations(phone_number);
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_conversation_id ON whatsapp_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_created_at ON whatsapp_messages(created_at);

CREATE INDEX IF NOT EXISTS idx_video_jobs_status ON video_jobs(status);
CREATE INDEX IF NOT EXISTS idx_video_jobs_created_at ON video_jobs(created_at);

CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_category ON system_logs(category);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_date ON performance_metrics(metric_date);
CREATE INDEX IF NOT EXISTS idx_financial_records_date ON financial_records(transaction_date);
CREATE INDEX IF NOT EXISTS idx_financial_records_type ON financial_records(record_type);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);

-- Insert default automation configuration
INSERT INTO automation_config (config_key, config_value, description) VALUES
('daily_posting_schedule', 
 '{"enabled": true, "times": ["09:00", "15:00", "21:00"], "timezone": "Europe/Bucharest", "platforms": ["tiktok", "facebook", "instagram"]}',
 'Daily posting schedule configuration'),
('content_templates',
 '{"educational": 40, "testimonial": 30, "promotional": 30}',
 'Content template distribution percentages'),
('referral_settings',
 '{"reward_amount": 200, "currency": "RON", "auto_approve": false}',
 'Referral system configuration'),
('whatsapp_settings',
 '{"group_link": "https://chat.whatsapp.com/Kz8GEkh4MJV4qg8JmiQmZL", "auto_respond": true}',
 'WhatsApp bot configuration')
ON CONFLICT (config_key) DO NOTHING;

-- Insert sample data for testing
INSERT INTO leads (name, phone, email, source, status, lead_score) VALUES
('Ion Popescu', '0712345678', 'ion.popescu@email.com', 'tiktok', 'new', 30),
('Maria Ionescu', '0723456789', 'maria.ionescu@email.com', 'facebook', 'contacted', 45),
('Gheorghe Vasilescu', '0734567890', 'gheorghe.v@email.com', 'referral', 'qualified', 60),
('Ana Georgescu', '0745678901', 'ana.georgescu@email.com', 'instagram', 'new', 25),
('Mihai Constantinescu', '0756789012', 'mihai.c@email.com', 'direct', 'converted', 80)
ON CONFLICT DO NOTHING;

-- Insert sample referrals
INSERT INTO referrals (referrer_phone, referrer_name, referred_phone, referred_name, referral_code, status) VALUES
('0712345678', 'Ion Popescu', '0798765432', 'Vasile Marin', 'REF-ION123', 'confirmed'),
('0723456789', 'Maria Ionescu', '0787654321', 'Elena Stoica', 'REF-MAR456', 'pending')
ON CONFLICT DO NOTHING;

-- Insert sample performance metrics
INSERT INTO performance_metrics (metric_date, leads_generated, posts_published, videos_generated, total_views, total_engagement) VALUES
(CURRENT_DATE - INTERVAL '1 day', 5, 3, 3, 1250, 89),
(CURRENT_DATE - INTERVAL '2 days', 3, 3, 3, 980, 67),
(CURRENT_DATE - INTERVAL '3 days', 7, 3, 3, 1580, 112)
ON CONFLICT DO NOTHING;