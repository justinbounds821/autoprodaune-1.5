# Supabase Database Setup - Quick Guide

## Step 1: Open Supabase Dashboard

1. Go to: https://supabase.com/dashboard
2. Login with your account
3. Select your AutoPro Daune project

## Step 2: Run Database Schema

1. Click "SQL Editor" in the left sidebar
2. Click "New query"
3. Copy the ENTIRE content from: `services/api/database/supabase_schema.sql`
4. Paste it into the SQL Editor
5. Click "Run" button

## Step 3: Verify Tables Created

Run this query to verify:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

You should see 11 tables:
- automation_config
- content_templates
- document_uploads
- leads
- performance_metrics
- referrals
- social_posts
- system_logs
- video_jobs
- whatsapp_conversations
- whatsapp_messages

## Step 4: Restart Backend

After running SQL:
```powershell
cd services/api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Warnings about missing tables should disappear!

## Current Status

- Schema file: `services/api/database/supabase_schema.sql` ✅
- Contains ALL 11 required tables ✅
- Just needs to be executed in Supabase Dashboard ✅
