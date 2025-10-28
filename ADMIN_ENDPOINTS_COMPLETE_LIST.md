# Admin Endpoints - Complete Mapping

## Video Management

| Endpoint | File Backend | Line | Status | Observații |
|----------|--------------|------|--------|------------|
| POST /api/advanced-video/generate | video_advanced_alias.py | 67 | ✅ | Crează job și returnează job_id; funcționează în FAKE_MODE |
| GET /api/advanced-video/jobs | video_advanced_alias.py | 203 | ⚠️ | Returnează lista fără paginare |
| GET /api/advanced-video/jobs/{id} | video_advanced_alias.py | 159 | ✅ | OK în FAKE_MODE; trebuie extins cu progres |
| DELETE /api/advanced-video/jobs/{id} | — | — | ❌ | Lipsește; trebuie implementat |
| POST /api/advanced-video/regenerate/{id} | video_internal_alias.py | 121 | ✅ | Refolosește job existent; nu există interfață frontend |

## Financial

| Endpoint | Line | Status | Observații |
|----------|------|--------|------------|
| GET /api/financial/dashboard | 715 | ⚠️ | În FAKE_MODE returnează 503; trebuie implementat fallback |
| POST /api/financial/track-cost | 78 | ⚠️ | Lazy init; folosește Supabase |
| GET /api/financial/costs | 120 | ✅ | Returnează costurile; fără filtrare/paginare |
| GET /api/financial/credit-balance/{provider} | 210 | ❌ | Lipsește complet; front-end îl apelează pentru credit TikTok |

## Automation & Social

| Endpoint | Status | Observații |
|----------|--------|------------|
| GET /api/automation/status | ⚠️ | Parțial; nu returnează toate câmpurile |
| POST /api/automation/trigger | ⚠️ | Există, dar nu este conectat în UI |
| POST /api/social/post | ⚠️ | Are stub, necesită OAuth și chei reale |
| GET /api/automation/logs | ❌ | Lipsește complet |

## User Management

| Endpoint | Status | Observații |
|----------|--------|------------|
| GET /api/users | ❌ | Nu există |
| POST /api/users | ❌ | Nu există |
| PUT /api/users/{id} | ❌ | Nu există |
| DELETE /api/users/{id} | ❌ | Nu există |

## Settings & Notifications

| Endpoint | Status | Observații |
|----------|--------|------------|
| GET /api/settings | ❌ | Nu există |
| PUT /api/settings | ❌ | Nu există |
| GET /api/notifications | ❌ | Nu există |
| POST /api/notifications/mark-read | ❌ | Nu există |

## Analytics & Growth

| Endpoint | Status | Observații |
|----------|--------|------------|
| GET /api/analytics/metrics | ❌ | Nu există; componenta folosește mock data |
| GET /api/analytics/events | ❌ | Nu există |
| POST /api/analytics/track | ❌ | Nu există |
