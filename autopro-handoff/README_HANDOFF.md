# AutoPro Daune – Hand-off

## Runtime & versiuni
**OS:** Windows 11
**Node:** 18.x / 20.x (verificat cu npm)
**npm:** 9.x / 10.x
**Python:** 3.10+ (FastAPI)
**FastAPI:** 0.115+
**Vite:** 5.x

## Porturi
**Frontend:** http://localhost:3006 (configurabil via vite.config.ts, poate deveni 3007)
**Admin:**    http://localhost:3006/admin
**Backend:**  http://127.0.0.1:8001 (prefix API: `/api`)

## Comenzi locale
### Backend
```powershell
cd services\api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### Frontend
```powershell
cd 02_FRONTEND_UI_CLEAN
npm run dev
```
*(Vite va porni pe :3006, strictPort=false)*

## Ce trebuie legat prioritar (TOP 5)
1. **Payments** – overview/list/update/delete (rute `/api/financial/payments`)
2. **Automation** – status/toggle/schedule (rute `/api/automation/*` și `/api/working-automation/*`)
3. **HeyGen** – generate/status/avatars (rute `/api/video/video/heygen/*`)
4. **Social** – posts list/create/update (rute `/api/social/*`)
5. **Growth Analytics** – dashboards (rute `/api/growth-analytics/*`)

## Auth
**Mode:** `bearer` (token în header `Authorization: Bearer <token>`)
**Token storage:** FE folosește `localStorage.getItem("authToken")`
**Fallback:** dacă 401 → redirect la `/admin`

## Known issues
1. **CORS:** BE permite 3000/3005 dar FE rulează pe 3006 → **trebuie adăugat `http://localhost:3006` și `:3007` în `BACKEND_CORS_ORIGINS`**
2. **HEYGEN_API_KEY:** absent complet în `.env` → **UX banner dorit când key lipsă, fără 500 error**
3. **Redis:** off în dev (nu există REDIS_URL) → **fallback in-memory fără warning** (deja implementat parțial în main.py)
4. **Supabase tabel `automation_config`:** lipsește → **script SQL inclus** (vezi `sql/automation_config.sql`)
5. **API client FE:** folosește `/api` ca prefix dar BE returnează `/api/...` deja în rute → **verifică double-prefix issue**

## Acces demo (dacă există)
**user:** admin
**pass:** admin123 (din `.env` ADMIN_PASSWORD)
**token dev:** (generat după autentificare, dummy OK pentru dev)

## Observații structurale
- **FE:** Vite proxy către BE (target: `http://127.0.0.1:8001`, rewrite `/api → /`)
- **BE:** include 25+ routere, unele încarcă condiționat (ex: video, whatsapp)
- **Supabase:** configurare parțială, unele rute nu au adaptor pentru automation_config
- **Rate limiting:** Redis-based dacă disponibil, altfel in-memory (vezi middleware în main.py)
