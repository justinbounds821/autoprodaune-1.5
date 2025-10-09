# Admin Database Requirements

## Existing Tables (Need Updates)

### video_jobs
**Status:** ✅ Exists, ⚠️ Needs columns

**Missing Columns:**
- `progress` (INTEGER, 0-100)
- `error_message` (TEXT)
- `metadata` (JSONB)

### video_templates
**Status:** ✅ Complete

### video_insights
**Status:** ✅ Complete (for AI features)

---

## Required New Tables

### Financial Tables

#### video_costs
```sql
CREATE TABLE video_costs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES video_jobs(id),
  provider VARCHAR(50),
  cost_amount DECIMAL(10, 4),
  currency VARCHAR(3) DEFAULT 'USD',
  cost_type VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### api_costs
```sql
CREATE TABLE api_costs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider VARCHAR(50),
  endpoint VARCHAR(255),
  cost_amount DECIMAL(10, 4),
  request_count INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### revenues
```sql
CREATE TABLE revenues (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source VARCHAR(100),
  amount DECIMAL(10, 2),
  currency VARCHAR(3) DEFAULT 'USD',
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### financial_metrics
```sql
CREATE TABLE financial_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_type VARCHAR(50),
  value DECIMAL(12, 2),
  period_start DATE,
  period_end DATE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### budget_alerts
```sql
CREATE TABLE budget_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_type VARCHAR(50),
  threshold_amount DECIMAL(10, 2),
  current_amount DECIMAL(10, 2),
  triggered_at TIMESTAMP,
  resolved_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### credit_balances
```sql
CREATE TABLE credit_balances (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider VARCHAR(50) UNIQUE,
  balance DECIMAL(10, 2),
  currency VARCHAR(3) DEFAULT 'USD',
  last_updated TIMESTAMP DEFAULT NOW()
);
```

---

### Automation Tables

#### automation_config
**Status:** ⚠️ Exists but not populated

**Required Data:**
- Schedule configuration
- Enabled/disabled state
- Trigger conditions
- Action definitions

#### automation_logs
```sql
CREATE TABLE automation_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  automation_id UUID,
  action VARCHAR(100),
  status VARCHAR(50),
  details JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

### Analytics Tables

#### analytics_events
```sql
CREATE TABLE analytics_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type VARCHAR(100),
  user_id UUID,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### analytics_metrics
```sql
CREATE TABLE analytics_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_name VARCHAR(100),
  metric_value DECIMAL(12, 2),
  dimensions JSONB,
  recorded_at TIMESTAMP DEFAULT NOW()
);
```

---

### Social Media Tables

#### social_posts
```sql
CREATE TABLE social_posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  platform VARCHAR(50),
  post_id VARCHAR(255),
  content TEXT,
  video_url TEXT,
  status VARCHAR(50),
  posted_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### oauth_tokens
```sql
CREATE TABLE oauth_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,
  provider VARCHAR(50),
  access_token TEXT,
  refresh_token TEXT,
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, provider)
);
```

---

### User Management Tables

#### users
**Status:** ⚠️ Partial - needs extension

**Required Additional Columns:**
- `role` VARCHAR(50)
- `permissions` JSONB
- `last_login` TIMESTAMP
- `is_active` BOOLEAN

#### user_settings
```sql
CREATE TABLE user_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  settings_key VARCHAR(100),
  settings_value JSONB,
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, settings_key)
);
```

---

## Migration Priority

### P0 - Critical
1. Add columns to `video_jobs` (progress, error_message, metadata)
2. Create `credit_balances` table
3. Create `automation_logs` table

### P1 - High
1. Create financial tables (video_costs, api_costs, revenues, financial_metrics)
2. Create `analytics_events` table
3. Populate `automation_config` table

### P2 - Medium
1. Create social media tables (social_posts, oauth_tokens)
2. Extend users table
3. Create user_settings table
4. Create budget_alerts table

### P3 - Low
1. Create analytics_metrics table
2. Add indexes for performance
3. Add foreign key constraints
4. Create views for common queries

---

## Required Indexes

```sql
-- Performance indexes
CREATE INDEX idx_video_jobs_status ON video_jobs(status);
CREATE INDEX idx_video_jobs_user_id ON video_jobs(user_id);
CREATE INDEX idx_video_costs_job_id ON video_costs(job_id);
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_events_user ON analytics_events(user_id);
CREATE INDEX idx_social_posts_platform ON social_posts(platform);
CREATE INDEX idx_automation_logs_automation_id ON automation_logs(automation_id);
```

---

## Estimated Storage Requirements

| Table | Est. Rows/Month | Storage/Month |
|-------|----------------|---------------|
| video_jobs | 1,000 | 2 MB |
| video_costs | 1,000 | 100 KB |
| automation_logs | 10,000 | 5 MB |
| analytics_events | 50,000 | 20 MB |
| social_posts | 500 | 500 KB |

**Total estimated:** ~30 MB/month
