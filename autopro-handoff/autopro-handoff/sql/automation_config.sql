-- Automation config table for Supabase
-- Run this in Supabase SQL editor to create the missing table

-- Enable pgcrypto extension for UUID generation
create extension if not exists pgcrypto;

-- Create automation_config table
create table if not exists public.automation_config (
  id uuid primary key default gen_random_uuid(),
  key text not null unique,
  value jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);

-- Create index for faster lookups by key
create index if not exists idx_automation_config_key on public.automation_config(key);

-- Create index for timestamp queries
create index if not exists idx_automation_config_updated on public.automation_config(updated_at desc);

-- Enable Row Level Security (RLS)
alter table public.automation_config enable row level security;

-- Policy: allow service role full access (for backend API)
create policy "Service role full access" on public.automation_config
  for all
  using (auth.role() = 'service_role');

-- Insert default config (optional, customize as needed)
insert into public.automation_config (key, value)
values
  ('global_enabled', '{"enabled": false, "last_toggled_at": null}'::jsonb),
  ('schedule', '{"days": ["monday", "wednesday", "friday"], "time": "09:00"}'::jsonb),
  ('retry_policy', '{"max_retries": 3, "backoff_seconds": 60}'::jsonb)
on conflict (key) do nothing;

-- Grant permissions
grant all on public.automation_config to service_role;
grant select on public.automation_config to anon;
