# BACKEND

## ENV (valori dummy OK pentru handoff)
```env
# Supabase
SUPABASE_URL=https://orctxxpyiqzbordibqxi.supabase.co
SUPABASE_ANON_KEY=__dummy__
SUPABASE_SERVICE_KEY=__dummy__
SUPABASE_SERVICE_ROLE_KEY=__dummy__

# Server
PORT=8001
HOST=127.0.0.1
BACKEND_CORS_ORIGINS=http://localhost:3006,http://127.0.0.1:3006,http://localhost:3007,http://127.0.0.1:3007

# Logging
LOG_LEVEL=DEBUG
ENVIRONMENT=development

# Security
SECRET_KEY=dev-secret-key-32-chars-minimum-123
JWT_SECRET_KEY=dev-jwt-secret-key-here
ADMIN_PASSWORD=admin123

# AI/Video (opțional, dezactivat dacă lipsă)
HEYGEN_API_KEY=__unset__

# Redis (fallback in-memory dacă lipsă)
REDIS_URL=disabled
RATE_LIMIT_MODE=memory
```

## Prefix API
Toate rutele backend sunt sub `/api` (ex: `/api/leads`, `/api/financial/payments`)

## Rute folosite de FE (critice)

### Automation
- **GET** `/api/automation/status` → `200 { enabled: bool, ... }`
- **POST** `/api/automation/toggle` → `200 { ok: true, enabled: bool }`
- **POST** `/api/working-automation/toggle` → `200 { success: true, enabled: bool }`

### Financial / Payments
- **GET** `/api/financial/payments` → `200 { items: [...], total: int }`
  - Query params: `?status=paid&date_from=2025-01-01&limit=50`
- **POST** `/api/financial/payments` → `200 { ok: true, payment: {...} }`
  - Body: `{ client_id, amount, status, date, description }`
- **PUT** `/api/financial/payments/{id}` → `200 { ok: true }`
- **DELETE** `/api/financial/payments/{id}` → `200 { ok: true }`
- **GET** `/api/financial/payments/overview` → `200 { total_paid, total_pending, ... }`

### Video / HeyGen
- **GET** `/api/video/video/heygen/avatars` → `200 { items: [...] }` sau `400 { detail: "HEYGEN_API_KEY..." }` dacă lipsă
- **POST** `/api/video/video/heygen/generate` → `400 { detail: "HEYGEN_API_KEY nu este configurat" }` dacă lipsă key
  - Body: `{ script: str, quality?: str, style?: str }`
  - Response (cu key): `{ id: str, status: "pending" }`
- **GET** `/api/video/video/heygen/status/{id}` → `200 { status: "completed" | "processing", url?: str }`

### Social Media
- **GET** `/api/social/posts` → `200 { items: [...] }`
- **POST** `/api/social/posts` → `200 { ok: true, post: {...} }`
- **PUT** `/api/social/posts/{id}` → `200 { ok: true }`

### Analytics / Growth
- **GET** `/api/growth-analytics/dashboard` → `200 { metrics: {...}, charts: [...] }`
- **GET** `/api/dashboard/overview` → `200 { leads_count, revenue, ... }`

### Health
- **GET** `/health` → `200 { status: "ok", service: "autopro-daune", port: 8001 }`
- **GET** `/api/test/mock-data` → `200 { success: true, mock_data: {...} }` (fără DB dependency)

## Loguri ultime erori (scurt)

**Eroare tipică (CORS):**
```
INFO:     127.0.0.1:xxxxx - "OPTIONS /api/automation/status HTTP/1.1" 403 Forbidden
CORS policy blocked: origin http://localhost:3006 not in allowed origins
```

**Cauză:** `BACKEND_CORS_ORIGINS` nu include `:3006` sau `:3007`

**Fix:** adaugă în `.env`:
```env
BACKEND_CORS_ORIGINS=http://localhost:3006,http://127.0.0.1:3006,http://localhost:3007,http://127.0.0.1:3007
```

**Eroare tipică (HeyGen fără key):**
```
POST /api/video/video/heygen/generate → 400
{ "detail": "HEYGEN_API_KEY nu este configurat sau este invalid" }
```

**UX dorit:** în loc de 500/400 error brutal, FE să afișeze banner: "HeyGen API key lipsește. Configurează în settings sau contactează admin." + disable CTA "Generate Video".
