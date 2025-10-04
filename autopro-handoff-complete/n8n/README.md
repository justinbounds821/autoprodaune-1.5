# n8n Workflows

## Status: NOT IMPLEMENTED

This project does not currently have n8n workflows implemented.

## Expected Structure (for future implementation)

```
n8n/
└── workflows/
    ├── lead-intake.json           # Lead intake workflow
    ├── referral-processing.json   # Referral processing
    ├── sla-30m.json              # 30-minute SLA workflow
    ├── sla-90m.json              # 90-minute SLA workflow
    ├── autoposter.json           # Auto-posting workflow
    └── fallback-publer.json      # Fallback to Publer
```

## Required Workflows (based on blueprint)

### 1. Lead Intake Workflow
- Trigger: New lead from website/form
- Actions: Create lead in database, send notification, start SLA timer

### 2. Referral Processing Workflow  
- Trigger: Referral form submission
- Actions: Validate referral, create lead, notify referrer

### 3. SLA 30/90 Minute Workflows
- Trigger: Timer-based
- Actions: Check lead status, send reminders, escalate if needed

### 4. Auto-poster Workflow
- Trigger: Scheduled or manual
- Actions: Generate content, post to social platforms, track analytics

### 5. Fallback Publer Workflow
- Trigger: Auto-poster failure
- Actions: Use Publer API as backup posting method

## Integration Points

Workflows should integrate with:
- `/api/leads/` - Lead management
- `/api/automation/trigger` - Automation triggers
- `/api/social/posts` - Social media posting
- `/api/notify/whatsapp` - WhatsApp notifications
- `/api/video/video/heygen/generate` - Video generation

## Required n8n Environment Variables

```env
N8N_WEBHOOK_URL=https://your-n8n-instance.com
N8N_API_KEY=your_n8n_api_key
PUBLER_API_KEY=your_publer_api_key
PUBLER_PROFILE_IDS=your_profile_ids
```
