-- Automation and notification related tables

CREATE TABLE IF NOT EXISTS automation_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    cron_expression VARCHAR(120) NOT NULL,
    timezone VARCHAR(60) DEFAULT 'Europe/Bucharest',
    is_active BOOLEAN DEFAULT TRUE,
    trigger_type VARCHAR(50) DEFAULT 'time',
    condition_logic JSONB DEFAULT '[]'::jsonb,
    action_config JSONB DEFAULT '[]'::jsonb,
    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS automation_run_history (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER NOT NULL REFERENCES automation_rules(id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL,
    trigger_payload JSONB,
    result_payload JSONB,
    error_message TEXT,
    attempt INTEGER DEFAULT 1,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finished_at TIMESTAMP WITH TIME ZONE,
    triggered_by VARCHAR(60) DEFAULT 'system'
);

CREATE TABLE IF NOT EXISTS automation_conditions (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER NOT NULL REFERENCES automation_rules(id) ON DELETE CASCADE,
    field VARCHAR(120) NOT NULL,
    operator VARCHAR(30) NOT NULL,
    target_value TEXT,
    value_type VARCHAR(30) DEFAULT 'string',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS automation_actions (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER NOT NULL REFERENCES automation_rules(id) ON DELETE CASCADE,
    action_type VARCHAR(60) NOT NULL,
    action_payload JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    destination VARCHAR(255),
    enabled BOOLEAN DEFAULT TRUE,
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    preferences JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (user_id, channel)
);

