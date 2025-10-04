# Feature Map UI ⇄ API

Această matrice mapează fiecare ecran/componentă din Admin UI la rutele backend corespunzătoare. Scopul: a avea o hartă clară pentru debugging și implementare.

| UI Route / Component         | Intent                            | API Route                              | Method | IN → OUT (ex.)                                  | Status    | Notes                                    |
|-----------------------------|-----------------------------------|----------------------------------------|--------|-------------------------------------------------|-----------|------------------------------------------|
| `/admin/automation`         | Vizualizare status automation     | `GET /api/automation/status`           | GET    | – → `{ enabled: bool, last_run: str, ... }`     | **broken**| CORS issue (port 3006 nu e în allowed)   |
|                             | Toggle automation on/off          | `POST /api/automation/toggle`          | POST   | `{enabled: bool}` → `{ok: true, enabled: bool}` | **todo**  | Alternativă: `/api/working-automation/toggle` |
|                             | Configurare schedule              | `POST /api/automation/settings`        | POST   | `{schedule: {...}}` → `{ok: true}`              | **todo**  | Payload structure TBD                    |
| `/admin/payments`           | Lista plăți                       | `GET /api/financial/payments`          | GET    | `?status=paid&limit=50` → `{items: [...], total: int}` | **ok** | Funcțional dar lipsește UI pentru filter |
|                             | Creare plată nouă                 | `POST /api/financial/payments`         | POST   | `{client_id, amount, status, ...}` → `{ok: true, payment: {...}}` | **ok** | |
|                             | Actualizare plată                 | `PUT /api/financial/payments/{id}`     | PUT    | `{amount, status, ...}` → `{ok: true}`          | **blocked**| Adaptor există în autoproApi.ts dar nu e conectat la UI |
|                             | Ștergere plată                    | `DELETE /api/financial/payments/{id}`  | DELETE | – → `{ok: true}`                                 | **blocked**| Idem, adaptor există dar nu e în UI      |
|                             | Overview (stats)                  | `GET /api/financial/payments/overview` | GET    | `?period=30d` → `{total_paid, total_pending, ...}` | **ok** | |
| `/admin/video` (HeyGen)     | Lista avatare disponibile         | `GET /api/video/video/heygen/avatars`  | GET    | – → `{items: [...]}` sau `400 {detail: "HEYGEN_API_KEY..."}` | **blocked**| Fără key → UX banner dorit în loc de error |
|                             | Generare video nou                | `POST /api/video/video/heygen/generate`| POST   | `{script: str, quality?: str, style?: str}` → `{id: str, status: "pending"}` | **blocked**| Fără key → 400, trebuie UX banner + disable CTA |
|                             | Status job video                  | `GET /api/video/video/heygen/status/{id}` | GET | – → `{status: "completed" | "processing", url?: str}` | **ok** | Polling la 5s interval                   |
| `/admin/social`             | Lista posts                       | `GET /api/social/posts`                | GET    | `?page=1&limit=20` → `{items: [...], total: int}` | **mixed** | Inconsistent pagination (`q` vs `search`) |
|                             | Creare post nou                   | `POST /api/social/posts`               | POST   | `{platform, content, media_url, ...}` → `{ok: true, post: {...}}` | **ok** | |
|                             | Actualizare post                  | `PUT /api/social/posts/{id}`           | PUT    | `{content, status, ...}` → `{ok: true}`          | **todo**  | Verifică dacă ruta există în BE          |
|                             | Ștergere post                     | `DELETE /api/social/posts/{id}`        | DELETE | – → `{ok: true}`                                 | **todo**  | Verifică dacă ruta există în BE          |
| `/admin/analytics`          | Dashboard overview                | `GET /api/dashboard/overview`          | GET    | – → `{leads_count, revenue, costs, roi, ...}`    | **ok** | |
|                             | Growth metrics                    | `GET /api/growth-analytics/dashboard`  | GET    | `?period=7d` → `{metrics: {...}, charts: [...]}` | **ok** | Lipsesc filtre custom date în UI         |
|                             | ROI analysis                      | `GET /api/financial/roi/{period}`      | GET    | `period=30d&date_from=...&date_to=...` → `{roi: float, ...}` | **ok** | |
| `/admin/leads`              | Lista leads                       | `GET /api/leads/`                      | GET    | `?page=1&limit=20&search=john` → `{items: [...], total: int}` | **ok** | |
|                             | Creare lead                       | `POST /api/leads/`                     | POST   | `{name, phone, email, source, ...}` → `{ok: true, lead: {...}}` | **ok** | |
|                             | Update lead                       | `PUT /api/leads/{lead_id}`             | PUT    | `{status, priority, ...}` → `{ok: true}`         | **ok** | |
|                             | Scoring lead                      | `POST /api/leads/{lead_id}/score`      | POST   | – → `{score: int, priority: str, ...}`           | **ok** | AI lead scoring                          |
| Global                      | Health check (status BE)          | `GET /health`                          | GET    | – → `{status: "ok", service: "autopro-daune", port: 8001}` | **ok** | |
|                             | Mock data (test fără DB)          | `GET /api/test/mock-data`              | GET    | – → `{success: true, mock_data: {...}}`          | **ok** | Util pentru debugging                    |

## Legendă Status
- **ok** – funcționează end-to-end
- **broken** – eroare critică (ex: CORS, 500)
- **blocked** – ruta există dar UX/adaptor lipsește
- **todo** – de implementat
- **mixed** – funcționează parțial, inconsistențe

## Priorități pentru Director de integrare
1. **CORS fix:** adaugă `:3006` și `:3007` în `BACKEND_CORS_ORIGINS` → deblochează automation + HeyGen
2. **HeyGen UX:** banner când key lipsește + disable CTA → user experience friendly
3. **Payments update/delete:** conectează adaptoarele la UI → completează CRUD
4. **Social posts standardization:** aliniază `q`→`search`, `offset`→`page` → consistență API
5. **Analytics date filters:** adaugă date picker în UI → flexibilitate raportare
