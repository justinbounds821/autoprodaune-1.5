-- AutoPro Database Initialization Script
-- This script creates all necessary tables for the microservices

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== LEADS ====================
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    phone_number VARCHAR(20),
    email VARCHAR(255),
    source VARCHAR(50) NOT NULL DEFAULT 'direct',
    lead_type VARCHAR(50) DEFAULT 'crash_claim',
    status VARCHAR(50) NOT NULL DEFAULT 'new',
    priority VARCHAR(20) DEFAULT 'medium',
    details TEXT,
    notes TEXT,
    estimated_value FLOAT DEFAULT 0.0,
    score INTEGER DEFAULT 0,
    assigned_to VARCHAR(255),
    files JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_contacted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_leads_status_priority ON leads(status, priority);
CREATE INDEX idx_leads_source_created ON leads(source, created_at);
CREATE INDEX idx_leads_score_desc ON leads(score DESC);
CREATE INDEX idx_leads_phone ON leads(phone_number);
CREATE INDEX idx_leads_email ON leads(email);

-- ==================== LEAD ACTIVITIES ====================
CREATE TABLE IF NOT EXISTS lead_activities (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    performed_by VARCHAR(255) DEFAULT 'system',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lead_activities_lead_created ON lead_activities(lead_id, created_at DESC);
CREATE INDEX idx_lead_activities_type ON lead_activities(activity_type);

-- ==================== REFERRALS ====================
CREATE TABLE IF NOT EXISTS referrals (
    id SERIAL PRIMARY KEY,
    referrer_id INTEGER REFERENCES leads(id),
    referred_id INTEGER REFERENCES leads(id),
    referral_code VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    commission_amount FLOAT DEFAULT 0.0,
    commission_paid BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    converted_at TIMESTAMP WITH TIME ZONE,
    paid_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_referrals_code ON referrals(referral_code);
CREATE INDEX idx_referrals_referrer ON referrals(referrer_id);
CREATE INDEX idx_referrals_status ON referrals(status);

-- ==================== FINANCIAL ====================
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    type VARCHAR(50) NOT NULL,
    amount FLOAT NOT NULL,
    currency VARCHAR(10) DEFAULT 'RON',
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_transactions_lead ON transactions(lead_id);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_created ON transactions(created_at DESC);

-- ==================== VIDEO ====================
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    video_url TEXT,
    thumbnail_url TEXT,
    duration_seconds INTEGER,
    status VARCHAR(50) DEFAULT 'pending',
    template_id VARCHAR(100),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_videos_lead ON videos(lead_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_created ON videos(created_at DESC);

-- ==================== SOCIAL MEDIA ====================
CREATE TABLE IF NOT EXISTS social_posts (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    video_id INTEGER REFERENCES videos(id),
    platform VARCHAR(50) NOT NULL,
    post_url TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    engagement JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    posted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_social_posts_lead ON social_posts(lead_id);
CREATE INDEX idx_social_posts_platform ON social_posts(platform);
CREATE INDEX idx_social_posts_status ON social_posts(status);

-- ==================== NOTIFICATIONS ====================
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    type VARCHAR(50) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    message TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_notifications_lead ON notifications(lead_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created ON notifications(created_at DESC);

-- ==================== ANALYTICS ====================
CREATE TABLE IF NOT EXISTS analytics_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}'::jsonb,
    lead_id INTEGER REFERENCES leads(id),
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_events_lead ON analytics_events(lead_id);
CREATE INDEX idx_analytics_events_created ON analytics_events(created_at DESC);

-- ==================== AUTOMATION ====================
CREATE TABLE IF NOT EXISTS workflows (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    trigger_type VARCHAR(50) NOT NULL,
    trigger_config JSONB DEFAULT '{}'::jsonb,
    actions JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow_executions (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES workflows(id) ON DELETE CASCADE,
    lead_id INTEGER REFERENCES leads(id),
    status VARCHAR(50) DEFAULT 'running',
    execution_log JSONB DEFAULT '[]'::jsonb,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_workflow_executions_workflow ON workflow_executions(workflow_id);
CREATE INDEX idx_workflow_executions_lead ON workflow_executions(lead_id);
CREATE INDEX idx_workflow_executions_status ON workflow_executions(status);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Insert sample data for testing
INSERT INTO leads (name, phone_number, email, source, status, priority, estimated_value, score) VALUES
('Test Lead 1', '0712345678', 'test1@example.com', 'referral', 'new', 'high', 5000.0, 75),
('Test Lead 2', '0712345679', 'test2@example.com', 'instagram', 'contacted', 'medium', 3000.0, 55),
('Test Lead 3', '0712345680', 'test3@example.com', 'direct', 'qualified', 'low', 1000.0, 25)
ON CONFLICT DO NOTHING;

-- Success message
DO $$
BEGIN
  RAISE NOTICE '✅ AutoPro database initialized successfully!';
END $$;
