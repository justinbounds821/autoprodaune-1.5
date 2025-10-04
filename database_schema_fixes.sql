-- ============================================
-- FAZA 1.3: Database Schema Fixes
-- Execută în Supabase SQL Editor
-- ============================================

-- 0. Verifică dacă tabela leads există (CRITICAL pentru foreign keys)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'leads') THEN
        CREATE TABLE leads (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            name TEXT,
            phone_number TEXT,
            email TEXT,
            source TEXT NOT NULL,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        RAISE NOTICE '✅ Created leads table';
    ELSE
        RAISE NOTICE '✅ leads table already exists';
    END IF;
END $$;

-- 1. Verifică dacă tabela automation_config există
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'automation_config') THEN
        CREATE TABLE automation_config (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
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
        
        RAISE NOTICE '✅ Created automation_config table';
    ELSE
        RAISE NOTICE '✅ automation_config table already exists';
    END IF;
END $$;

-- 2. Verifică dacă tabela system_logs există
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'system_logs') THEN
        CREATE TABLE system_logs (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
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
        
        RAISE NOTICE '✅ Created system_logs table';
    ELSE
        RAISE NOTICE '✅ system_logs table already exists';
    END IF;
END $$;

-- 3. Verifică dacă tabela social_posts există și adaugă coloana clicks
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'social_posts') THEN
        -- Verifică dacă coloana clicks există
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'social_posts' AND column_name = 'clicks') THEN
            ALTER TABLE social_posts ADD COLUMN clicks INTEGER DEFAULT 0;
            RAISE NOTICE '✅ Added clicks column to social_posts table';
        ELSE
            RAISE NOTICE '✅ clicks column already exists in social_posts table';
        END IF;
    ELSE
        -- Creează tabela social_posts dacă nu există
        CREATE TABLE social_posts (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            title TEXT,
            content TEXT,
            platforms TEXT[] DEFAULT '{}',
            video_url TEXT,
            thumbnail_url TEXT,
            hashtags TEXT[] DEFAULT '{}',
            status TEXT DEFAULT 'scheduled',
            template_type TEXT,
            target_audience TEXT,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            engagement INTEGER DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            leads_generated INTEGER DEFAULT 0,
            conversion_rate DECIMAL(5,2) DEFAULT 0,
            revenue_generated DECIMAL(10,2) DEFAULT 0,
            cost_per_lead DECIMAL(10,2) DEFAULT 0,
            scheduled_for TIMESTAMPTZ,
            posted_at TIMESTAMPTZ,
            post_metadata JSONB DEFAULT '{}',
            performance_data JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        RAISE NOTICE '✅ Created social_posts table with clicks column';
    END IF;
END $$;

-- 4. Verifică dacă tabela performance_metrics există
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'performance_metrics') THEN
        CREATE TABLE performance_metrics (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            metric_date DATE NOT NULL,
            metric_type TEXT NOT NULL,
            leads_generated INTEGER DEFAULT 0,
            leads_converted INTEGER DEFAULT 0,
            conversion_rate DECIMAL(5,2) DEFAULT 0,
            posts_published INTEGER DEFAULT 0,
            total_views INTEGER DEFAULT 0,
            total_engagement INTEGER DEFAULT 0,
            total_clicks INTEGER DEFAULT 0,
            revenue_generated DECIMAL(10,2) DEFAULT 0,
            referral_rewards_paid DECIMAL(10,2) DEFAULT 0,
            cost_per_lead DECIMAL(10,2) DEFAULT 0,
            return_on_investment DECIMAL(5,2) DEFAULT 0,
            whatsapp_conversations INTEGER DEFAULT 0,
            avg_response_time INTEGER DEFAULT 0,
            satisfaction_score DECIMAL(3,2) DEFAULT 0,
            videos_generated INTEGER DEFAULT 0,
            video_completion_rate DECIMAL(5,2) DEFAULT 0,
            metrics_data JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(metric_date, metric_type)
        );
        
        CREATE INDEX IF NOT EXISTS idx_performance_metrics_date ON performance_metrics(metric_date);
        CREATE INDEX IF NOT EXISTS idx_performance_metrics_type ON performance_metrics(metric_type);
        
        RAISE NOTICE '✅ Created performance_metrics table';
    ELSE
        RAISE NOTICE '✅ performance_metrics table already exists';
    END IF;
END $$;

-- 5. Verifică dacă tabela content_templates există
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'content_templates') THEN
        CREATE TABLE content_templates (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
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
        
        RAISE NOTICE '✅ Created content_templates table';
    ELSE
        RAISE NOTICE '✅ content_templates table already exists';
    END IF;
END $$;

-- 6. Verifică dacă tabela whatsapp_conversations există
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'whatsapp_conversations') THEN
        CREATE TABLE whatsapp_conversations (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
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
        
        RAISE NOTICE '✅ Created whatsapp_conversations table';
    ELSE
        RAISE NOTICE '✅ whatsapp_conversations table already exists';
    END IF;
END $$;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🎉 FAZA 1.3: Database Schema Fixes COMPLETED!';
    RAISE NOTICE '';
    RAISE NOTICE '✅ All required tables created/verified:';
    RAISE NOTICE '   • automation_config (fixes scheduler error)';
    RAISE NOTICE '   • system_logs (fixes automation logging error)';
    RAISE NOTICE '   • social_posts with clicks column (fixes social poster error)';
    RAISE NOTICE '   • performance_metrics (fixes daily metrics error)';
    RAISE NOTICE '   • content_templates (video automation)';
    RAISE NOTICE '   • whatsapp_conversations (WhatsApp bot)';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Backend should now start without database errors!';
    RAISE NOTICE '';
END $$;
