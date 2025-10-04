-- ================================================================
-- MIGRAȚIE 001: TABELE FINANCIARE PENTRU AUTOPRO DAUNE
-- ================================================================
-- 
-- Această migrație creează tabelele necesare pentru tracking financiar:
-- - api_costs: înregistrează costurile API externe
-- - revenue: înregistrează veniturile obținute  
-- - financial_metrics: metricile financiare agregate pe zile
-- - campaign_metrics: metricile specifice campaniilor
-- - credit_balances: tracking credite disponibile
-- - budget_alerts: alertele de buget și praguri
--
-- Data: 2024-01-XX
-- Versiune: 1.0
-- ================================================================

-- Activează extensiile necesare
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ================================================================
-- 1. TABELA API_COSTS - Costuri API externe
-- ================================================================

CREATE TABLE IF NOT EXISTS api_costs (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    operation VARCHAR(100) NOT NULL,
    cost DECIMAL(10,2) NOT NULL CHECK (cost > 0),
    credits_used INTEGER CHECK (credits_used >= 0),
    currency VARCHAR(3) DEFAULT 'USD' CHECK (currency IN ('USD', 'EUR', 'RON')),
    metadata TEXT, -- JSON cu detalii suplimentare
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Index-uri pentru performanță
    CONSTRAINT api_costs_provider_check CHECK (provider IN (
        'Pika', 'HeyGen', 'TikTok', 'Instagram', 'YouTube', 
        'Publer', 'GoogleSheets', 'Telegram', 'Other'
    ))
);

-- Index-uri pentru api_costs
CREATE INDEX IF NOT EXISTS idx_api_costs_provider ON api_costs(provider);
CREATE INDEX IF NOT EXISTS idx_api_costs_timestamp ON api_costs(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_costs_provider_timestamp ON api_costs(provider, timestamp);
CREATE INDEX IF NOT EXISTS idx_api_costs_operation ON api_costs(operation);

-- ================================================================
-- 2. TABELA REVENUE - Venituri obținute
-- ================================================================

CREATE TABLE IF NOT EXISTS revenue (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    lead_id INTEGER, -- FK către tabela leads (dacă există)
    conversion_type VARCHAR(50),
    currency VARCHAR(3) DEFAULT 'USD' CHECK (currency IN ('USD', 'EUR', 'RON')),
    metadata TEXT, -- JSON cu detalii suplimentare
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Index-uri pentru performanță
    CONSTRAINT revenue_source_check CHECK (source IN (
        'LeadConversion', 'Referral', 'Consultation', 
        'InsuranceSale', 'TikTokAds', 'Other'
    ))
);

-- Index-uri pentru revenue
CREATE INDEX IF NOT EXISTS idx_revenue_source ON revenue(source);
CREATE INDEX IF NOT EXISTS idx_revenue_timestamp ON revenue(timestamp);
CREATE INDEX IF NOT EXISTS idx_revenue_lead_id ON revenue(lead_id);
CREATE INDEX IF NOT EXISTS idx_revenue_source_timestamp ON revenue(source, timestamp);

-- ================================================================
-- 3. TABELA FINANCIAL_METRICS - Metrici financiare agregate
-- ================================================================

CREATE TABLE IF NOT EXISTS financial_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    
    -- Costuri
    total_costs DECIMAL(10,2) DEFAULT 0.00 NOT NULL CHECK (total_costs >= 0),
    api_costs DECIMAL(10,2) DEFAULT 0.00 NOT NULL CHECK (api_costs >= 0),
    advertising_costs DECIMAL(10,2) DEFAULT 0.00 NOT NULL CHECK (advertising_costs >= 0),
    other_costs DECIMAL(10,2) DEFAULT 0.00 NOT NULL CHECK (other_costs >= 0),
    
    -- Venituri
    total_revenue DECIMAL(10,2) DEFAULT 0.00 NOT NULL CHECK (total_revenue >= 0),
    lead_conversion_revenue DECIMAL(10,2) DEFAULT 0.00 NOT NULL CHECK (lead_conversion_revenue >= 0),
    referral_revenue DECIMAL(10,2) DEFAULT 0.00 NOT NULL CHECK (referral_revenue >= 0),
    other_revenue DECIMAL(10,2) DEFAULT 0.00 NOT NULL CHECK (other_revenue >= 0),
    
    -- Metrici calculate
    net_profit DECIMAL(10,2) DEFAULT 0.00 NOT NULL,
    roi_percentage DECIMAL(5,2) DEFAULT 0.00 NOT NULL CHECK (roi_percentage >= -100),
    
    -- Contoare
    total_leads INTEGER DEFAULT 0 NOT NULL CHECK (total_leads >= 0),
    converted_leads INTEGER DEFAULT 0 NOT NULL CHECK (converted_leads >= 0),
    total_referrals INTEGER DEFAULT 0 NOT NULL CHECK (total_referrals >= 0),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Constraint pentru validarea datelor
    CONSTRAINT financial_metrics_conversion_check CHECK (converted_leads <= total_leads),
    CONSTRAINT financial_metrics_cost_sum_check CHECK (
        total_costs = api_costs + advertising_costs + other_costs
    ),
    CONSTRAINT financial_metrics_revenue_sum_check CHECK (
        total_revenue = lead_conversion_revenue + referral_revenue + other_revenue
    )
);

-- Index-uri pentru financial_metrics
CREATE INDEX IF NOT EXISTS idx_financial_metrics_date ON financial_metrics(date);
CREATE INDEX IF NOT EXISTS idx_financial_metrics_roi ON financial_metrics(roi_percentage);
CREATE INDEX IF NOT EXISTS idx_financial_metrics_profit ON financial_metrics(net_profit);

-- ================================================================
-- 4. TABELA CAMPAIGN_METRICS - Metrici specifice campaniilor
-- ================================================================

CREATE TABLE IF NOT EXISTS campaign_metrics (
    id SERIAL PRIMARY KEY,
    campaign_name VARCHAR(100) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Metrici de cost
    total_spent DECIMAL(10,2) DEFAULT 0.00 NOT NULL CHECK (total_spent >= 0),
    cost_per_lead DECIMAL(10,2) DEFAULT 0.00 NOT NULL CHECK (cost_per_lead >= 0),
    cost_per_conversion DECIMAL(10,2) DEFAULT 0.00 NOT NULL CHECK (cost_per_conversion >= 0),
    
    -- Metrici de performanță
    total_leads INTEGER DEFAULT 0 NOT NULL CHECK (total_leads >= 0),
    total_conversions INTEGER DEFAULT 0 NOT NULL CHECK (total_conversions >= 0),
    conversion_rate DECIMAL(5,2) DEFAULT 0.00 NOT NULL CHECK (conversion_rate >= 0 AND conversion_rate <= 100),
    
    -- Metrici de engagement
    total_views INTEGER DEFAULT 0 NOT NULL CHECK (total_views >= 0),
    total_likes INTEGER DEFAULT 0 NOT NULL CHECK (total_likes >= 0),
    total_shares INTEGER DEFAULT 0 NOT NULL CHECK (total_shares >= 0),
    engagement_rate DECIMAL(5,2) DEFAULT 0.00 NOT NULL CHECK (engagement_rate >= 0 AND engagement_rate <= 100),
    
    -- ROI și profit
    total_revenue DECIMAL(10,2) DEFAULT 0.00 NOT NULL CHECK (total_revenue >= 0),
    net_profit DECIMAL(10,2) DEFAULT 0.00 NOT NULL,
    roi_percentage DECIMAL(5,2) DEFAULT 0.00 NOT NULL CHECK (roi_percentage >= -100),
    
    -- Metadata
    metadata TEXT, -- JSON cu detalii suplimentare
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Constraint pentru validarea datelor
    CONSTRAINT campaign_metrics_period_check CHECK (period_start <= period_end),
    CONSTRAINT campaign_metrics_conversion_check CHECK (total_conversions <= total_leads),
    CONSTRAINT campaign_metrics_platform_check CHECK (platform IN (
        'TikTok', 'Instagram', 'YouTube', 'Facebook', 'Twitter', 'LinkedIn', 'Other'
    ))
);

-- Index-uri pentru campaign_metrics
CREATE INDEX IF NOT EXISTS idx_campaign_metrics_campaign ON campaign_metrics(campaign_name);
CREATE INDEX IF NOT EXISTS idx_campaign_metrics_platform ON campaign_metrics(platform);
CREATE INDEX IF NOT EXISTS idx_campaign_metrics_period ON campaign_metrics(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_campaign_metrics_roi ON campaign_metrics(roi_percentage);

-- ================================================================
-- 5. TABELA CREDIT_BALANCES - Solduri credite disponibile
-- ================================================================

CREATE TABLE IF NOT EXISTS credit_balances (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL UNIQUE,
    credit_type VARCHAR(50) NOT NULL,
    current_balance DECIMAL(10,2) NOT NULL CHECK (current_balance >= 0),
    total_allocated DECIMAL(10,2) NOT NULL CHECK (total_allocated >= 0),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Constraint pentru validarea datelor
    CONSTRAINT credit_balances_balance_check CHECK (current_balance <= total_allocated),
    CONSTRAINT credit_balances_provider_check CHECK (provider IN (
        'Pika', 'HeyGen', 'TikTok', 'Instagram', 'YouTube', 
        'Publer', 'GoogleSheets', 'Telegram', 'Other'
    ))
);

-- Index-uri pentru credit_balances
CREATE INDEX IF NOT EXISTS idx_credit_balances_provider ON credit_balances(provider);
CREATE INDEX IF NOT EXISTS idx_credit_balances_last_updated ON credit_balances(last_updated);

-- ================================================================
-- 6. TABELA BUDGET_ALERTS - Alerte de buget și praguri
-- ================================================================

CREATE TABLE IF NOT EXISTS budget_alerts (
    id SERIAL PRIMARY KEY,
    alert_name VARCHAR(100) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    threshold_value DECIMAL(10,2) NOT NULL,
    current_value DECIMAL(10,2) NOT NULL,
    is_triggered INTEGER DEFAULT 0 NOT NULL CHECK (is_triggered IN (0, 1)),
    is_active INTEGER DEFAULT 1 NOT NULL CHECK (is_active IN (0, 1)),
    
    -- Detalii alerte
    message TEXT,
    notification_sent TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Constraint pentru validarea datelor
    CONSTRAINT budget_alerts_type_check CHECK (alert_type IN (
        'budget_exceeded', 'negative_roi', 'low_credits',
        'high_cost_per_lead', 'low_conversion_rate'
    ))
);

-- Index-uri pentru budget_alerts
CREATE INDEX IF NOT EXISTS idx_budget_alerts_type ON budget_alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_budget_alerts_triggered ON budget_alerts(is_triggered);
CREATE INDEX IF NOT EXISTS idx_budget_alerts_active ON budget_alerts(is_active);
CREATE INDEX IF NOT EXISTS idx_budget_alerts_name ON budget_alerts(alert_name);

-- ================================================================
-- 7. TRIGGERE PENTRU AUTOMATIZARE
-- ================================================================

-- Funcție pentru actualizarea automată a updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger pentru financial_metrics
DROP TRIGGER IF EXISTS update_financial_metrics_updated_at ON financial_metrics;
CREATE TRIGGER update_financial_metrics_updated_at
    BEFORE UPDATE ON financial_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger pentru campaign_metrics
DROP TRIGGER IF EXISTS update_campaign_metrics_updated_at ON campaign_metrics;
CREATE TRIGGER update_campaign_metrics_updated_at
    BEFORE UPDATE ON campaign_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger pentru budget_alerts
DROP TRIGGER IF EXISTS update_budget_alerts_updated_at ON budget_alerts;
CREATE TRIGGER update_budget_alerts_updated_at
    BEFORE UPDATE ON budget_alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ================================================================
-- 8. FUNCȚII UTILE PENTRU CALCULE FINANCIARE
-- ================================================================

-- Funcție pentru calcularea ROI-ului
CREATE OR REPLACE FUNCTION calculate_roi(revenue DECIMAL, costs DECIMAL)
RETURNS DECIMAL AS $$
BEGIN
    IF costs = 0 THEN
        RETURN CASE WHEN revenue > 0 THEN 999.99 ELSE 0.00 END;
    END IF;
    
    RETURN ROUND(((revenue - costs) / costs) * 100, 2);
END;
$$ LANGUAGE plpgsql;

-- Funcție pentru calcularea profitului net
CREATE OR REPLACE FUNCTION calculate_net_profit(revenue DECIMAL, costs DECIMAL)
RETURNS DECIMAL AS $$
BEGIN
    RETURN ROUND(revenue - costs, 2);
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- 9. DATE INIȚIALE (SEED DATA)
-- ================================================================

-- Inserează date inițiale pentru credit balances
INSERT INTO credit_balances (provider, credit_type, current_balance, total_allocated)
VALUES 
    ('Pika', 'video_seconds', 3600.00, 3600.00),
    ('HeyGen', 'credits', 1000.00, 1000.00),
    ('TikTok', 'api_calls', 10000.00, 10000.00),
    ('Instagram', 'api_calls', 10000.00, 10000.00),
    ('YouTube', 'api_calls', 10000.00, 10000.00)
ON CONFLICT (provider) DO NOTHING;

-- Inserează alerte inițiale
INSERT INTO budget_alerts (alert_name, alert_type, threshold_value, current_value, message)
VALUES 
    ('ROI Negativ Zilnic', 'negative_roi', 0.00, 0.00, 'ROI-ul zilnic este negativ'),
    ('Credite Pika Scăzute', 'low_credits', 100.00, 3600.00, 'Creditele Pika sunt sub 100 secunde'),
    ('Cost per Lead Ridicat', 'high_cost_per_lead', 50.00, 0.00, 'Costul per lead depășește $50'),
    ('Rata Conversie Scăzută', 'low_conversion_rate', 5.00, 0.00, 'Rata de conversie este sub 5%')
ON CONFLICT DO NOTHING;

-- ================================================================
-- 10. COMENTARII ȘI DOCUMENTAȚIE
-- ================================================================

COMMENT ON TABLE api_costs IS 'Înregistrează costurile API externe pentru tracking financiar';
COMMENT ON TABLE revenue IS 'Înregistrează veniturile obținute din conversii și alte surse';
COMMENT ON TABLE financial_metrics IS 'Metricile financiare agregate zilnic pentru analiza ROI';
COMMENT ON TABLE campaign_metrics IS 'Metricile specifice campaniilor de marketing';
COMMENT ON TABLE credit_balances IS 'Soldurile creditelor disponibile la providerii externi';
COMMENT ON TABLE budget_alerts IS 'Alertele configurate pentru praguri financiare';

-- Comentarii pentru coloane importante
COMMENT ON COLUMN api_costs.cost IS 'Costul în dolari (USD)';
COMMENT ON COLUMN revenue.amount IS 'Suma în dolari (USD)';
COMMENT ON COLUMN financial_metrics.roi_percentage IS 'ROI calculat ca procent: ((revenue - costs) / costs) * 100';
COMMENT ON COLUMN campaign_metrics.conversion_rate IS 'Rata de conversie în procente: (conversions / leads) * 100';

-- ================================================================
-- FINALIZARE MIGRAȚIE
-- ================================================================

-- Verifică că toate tabelele au fost create
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN ('api_costs', 'revenue', 'financial_metrics', 'campaign_metrics', 'credit_balances', 'budget_alerts');
    
    IF table_count = 6 THEN
        RAISE NOTICE 'SUCCESS: Toate cele 6 tabele financiare au fost create cu succes!';
    ELSE
        RAISE EXCEPTION 'ERROR: Doar % din 6 tabele au fost create!', table_count;
    END IF;
END $$;

-- Afișează un mesaj de finalizare
SELECT 'Migrația 001_financial_tables.sql a fost executată cu succes!' AS status;
