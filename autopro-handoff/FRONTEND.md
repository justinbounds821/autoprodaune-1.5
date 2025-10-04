# FRONTEND

## ENV
```env
VITE_API_BASE_URL=http://localhost:8001
VITE_API_URL=http://localhost:8001
VITE_API_TIMEOUT=20000
VITE_ENV=development
VITE_ENABLE_METRICS=true
```

**Issue identificat:** FE folosește `VITE_API_BASE_URL` sau `VITE_API_URL` ca bază, dar în cod se concatenează cu `/api`:
```ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || "/api";
```

Dacă `VITE_API_URL=http://localhost:8001` și apoi apelează `api.get("/api/leads")`, rezultă `http://localhost:8001/api/leads` ✅ OK.

Dar vite.config.ts are proxy:
```ts
proxy: {
  "/api": {
    target: "http://127.0.0.1:8001",
    changeOrigin: true,
    secure: false,
    rewrite: (p) => p.replace(/^\/api/, ""), // strip /api prefix
  },
}
```

**Atenție:** dacă FE rulează pe dev server (cu proxy), apelurile merg prin proxy care **strip-uiește `/api`** → backend primește ruta fără `/api` → **404 dacă BE așteaptă `/api/...`**.

**Soluție:** fie disable proxy, fie configurează `VITE_API_URL=/` (doar prefix `/api`) și lasă proxy-ul să facă forward.

## Client API
- **Locație:** `02_FRONTEND_UI_CLEAN/src/services/autoproApi.ts`
- **Folosește interceptors:** DA
  - Request: adaugă `Authorization: Bearer <token>` din `localStorage.getItem("authToken")`
  - Response: dacă 401 → logout + redirect `/admin`
- **Structură:** clasă `AutoProApiService` cu metode:
  - `getLeads()`, `createLead()`, `getPayments()`, `createPayment()`, etc.
  - `getAutomationStatus()`, `toggleAutomation()`, etc.

## Fluxuri Admin de legat

### /admin/automation
- **UI:** status banner + toggle switch + schedule form
- **API calls:**
  - GET `/api/automation/status` → afișează enabled/disabled
  - POST `/api/automation/toggle` → {enabled: true/false} → refresh UI

### /admin/payments
- **UI:** tabel cu payments, butoane add/edit/delete
- **API calls:**
  - GET `/api/financial/payments` → listă
  - POST `/api/financial/payments` → create
  - PUT `/api/financial/payments/{id}` → update (lipsește adaptor în autoproApi.ts)
  - DELETE `/api/financial/payments/{id}` → delete (lipsește adaptor în autoproApi.ts)

**Gap:** `updatePayment(id, updates)` și `deletePayment(id)` există în cod dar **nu sunt conectate la UI**.

### /admin/video (HeyGen)
- **UI:** avatars selector + generate form + status polling
- **API calls:**
  - GET `/api/video/video/heygen/avatars` → listă avatare disponibile
  - POST `/api/video/video/heygen/generate` → {script, quality, style} → returnează {id}
  - GET `/api/video/video/heygen/status/{id}` → polling pentru status

**Gap UX:** când `HEYGEN_API_KEY` lipsește, BE returnează 400 → **FE trebuie să detecteze acest caz și să afișeze banner + disable CTA** în loc de error toast generic.

### /admin/social
- **UI:** posts list + create/edit modal
- **API calls:**
  - GET `/api/social/posts` → listă
  - POST `/api/social/posts` → create
  - PUT `/api/social/posts/{id}` → update (verifică dacă există rută în BE)

### /admin/analytics
- **UI:** growth charts + metrics cards
- **API calls:**
  - GET `/api/dashboard/overview` → stats generale
  - GET `/api/growth-analytics/dashboard` → metrics detaliate

## Log FE (console/network – scurt)

**Eroare tipică (CORS preflight):**
```
Access to fetch at 'http://127.0.0.1:8001/api/automation/status' from origin 'http://localhost:3006' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

**Cauză:** BE CORS nu include `:3006`

**Eroare tipică (HeyGen generate fără key):**
```
POST /api/video/video/heygen/generate → 400
Response: { detail: "HEYGEN_API_KEY nu este configurat sau este invalid" }
FE toast: "Error: Request failed with status code 400"
```

**UX dorit:** în loc de toast generic, detectează mesajul specific și afișează:
```tsx
{error.response?.data?.detail?.includes("HEYGEN_API_KEY") && (
  <Alert variant="warning">
    HeyGen API key lipsește. Configurează în settings sau contactează admin.
  </Alert>
)}
```
