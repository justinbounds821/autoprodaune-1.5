# TROUBLESHOOTING

Ghid rapid pentru depanarea celor mai frecvente probleme în AutoPro Daune.

---

## 🔴 Problemă: CORS blocat (FE 3006/3007)

**Semne:**
- Console browser: `Access to fetch at 'http://127.0.0.1:8001/...' blocked by CORS policy`
- Network tab: preflight `OPTIONS` request → `403 Forbidden`
- Backend logs: `CORS policy blocked: origin http://localhost:3006 not in allowed origins`

**Cauze:**
- `BACKEND_CORS_ORIGINS` nu include portul pe care rulează FE (3006 sau 3007)
- FE schimbă portul (vite.config.ts: `port: 3006`, dar ENV spune altceva)

**Soluție:**
1. Editează `services/api/.env`:
   ```env
   BACKEND_CORS_ORIGINS=http://localhost:3006,http://127.0.0.1:3006,http://localhost:3007,http://127.0.0.1:3007
   ```
2. Restart BE: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload`
3. Verificare: din FE browser console:
   ```js
   fetch("http://127.0.0.1:8001/health").then(r => r.json()).then(console.log)
   ```
   Ar trebui să returneze `{status: "ok", ...}` fără erori CORS.

---

## 🔴 Problemă: HeyGen fără API key

**Semne:**
- POST `/api/video/video/heygen/generate` → `400 Bad Request`
- Response body: `{ "detail": "HEYGEN_API_KEY nu este configurat sau este invalid" }`
- FE afișează toast error generic: "Request failed with status code 400"

**Cauze:**
- `HEYGEN_API_KEY` lipsește din `.env` sau este gol
- User încearcă să genereze video fără configurare prealabilă

**Soluție (backend):**
- Adaugă `HEYGEN_API_KEY=your_key_here` în `services/api/.env`
- Restart BE

**Soluție (frontend UX):**
- Detectează eroarea specifică și afișează banner:
  ```tsx
  if (error?.response?.data?.detail?.includes("HEYGEN_API_KEY")) {
    return (
      <Alert variant="warning">
        🔑 HeyGen API key lipsește. Configurează în settings sau contactează admin.
      </Alert>
    );
  }
  ```
- Disable butoanele "Generate Video" și "Load Avatars" când key lipsește
- Verificare: GET `/api/video/video/heygen/avatars` → dacă 400 cu mesaj key, afișează banner

---

## 🟡 Problemă: Redis warning spam în dev

**Semne:**
- Backend logs: `WARNING: Redis connection failed... falling back to in-memory`
- Repetă warning-ul la fiecare request
- Funcționalitatea merge, dar logurile sunt poluate

**Cauze:**
- `REDIS_URL` nu este setat sau Redis nu rulează local
- Codul încearcă să conecteze Redis la fiecare request și loghează warning

**Soluție:**
1. Setează explicit fallback în `.env`:
   ```env
   REDIS_URL=disabled
   RATE_LIMIT_MODE=memory
   ```
2. În cod (deja implementat în `main.py:204`):
   ```python
   if r:  # Redis available
       # use Redis
   else:
       # fallback to in-memory (fără warning dacă REDIS_URL="disabled")
   ```
3. Verificare: restart BE → ar trebui să vezi `✅ Using in-memory rate limiting` fără warning-uri repetitive

---

## 🟡 Problemă: Supabase tabel `automation_config` lipsește

**Semne:**
- BE logs: `ERROR: relation "automation_config" does not exist`
- Apeluri către automation settings → 500 Internal Server Error
- Sau: adaptor returnează date mock/hardcoded

**Cauze:**
- Tabelul nu a fost creat în Supabase
- Migrare SQL nu a fost rulată

**Soluție:**
1. Rulează script SQL din `autopro-handoff/sql/automation_config.sql` în Supabase SQL Editor:
   ```sql
   create extension if not exists pgcrypto;
   create table if not exists public.automation_config (...);
   ```
2. Verifică în Supabase Table Editor că tabelul `automation_config` apare
3. Test: GET `/api/automation/status` → ar trebui să returneze date reale, nu mock

**Alternativă (fallback în cod):**
- Dacă nu poți crea tabelul imediat, implementează adaptor fallback cu valori default hardcoded
- Documentează în LEDGER.md că folosești fallback temporar

---

## 🟡 Problemă: Vite proxy strip-uiește `/api` → 404

**Semne:**
- FE apelează `/api/leads` → Network tab: `http://127.0.0.1:8001/leads` (fără `/api`)
- BE returnează 404 Not Found
- vite.config.ts are `rewrite: (p) => p.replace(/^\/api/, "")`

**Cauze:**
- Proxy Vite strip-uiește prefix `/api` înainte de forward la BE
- BE așteaptă rute cu prefix `/api/...`

**Soluție:**
1. **Opțiunea 1 (recomandată):** dezactivează proxy, apelează direct BE:
   ```ts
   // 02_FRONTEND_UI_CLEAN/.env
   VITE_API_URL=http://127.0.0.1:8001  // URL complet
   ```
   În cod:
   ```ts
   api.get("/api/leads")  // va apela http://127.0.0.1:8001/api/leads
   ```

2. **Opțiunea 2:** păstrează proxy, dar folosește `/` ca bază:
   ```ts
   // 02_FRONTEND_UI_CLEAN/.env
   VITE_API_URL=/  // relativă la proxy
   ```
   În cod:
   ```ts
   api.get("/api/leads")  // va apela /api/leads → proxy strip /api → BE primește /leads ❌
   ```
   **Atenție:** BE trebuie să aibă rute fără prefix `/api` (nu e cazul actual).

**Verificare:**
- Network tab browser: vezi exact ce URL se apelează
- BE logs: vezi ce path primește uvicorn
- Dacă apare `/leads` în loc de `/api/leads`, proxy strip-uiește greșit

---

## 🟢 Verificări generale (quando tutto va male)

### 1. Backend pornit și accesibil?
```powershell
curl.exe http://127.0.0.1:8001/health
# Ar trebui: {"status":"ok","service":"autopro-daune","port":8001}
```

### 2. Frontend pornit pe portul așteptat?
```powershell
# În consolă Vite:
# VITE v5.x ready in 500 ms
# ➜ Local:   http://localhost:3006/
```

### 3. ENV-uri corect încărcate?
Backend:
```python
import os
print(os.getenv("BACKEND_CORS_ORIGINS"))  # trebuie să includă :3006/:3007
```

Frontend (în browser console):
```js
console.log(import.meta.env.VITE_API_URL)  // http://127.0.0.1:8001
```

### 4. Smoke test trece?
```powershell
pwsh -File scripts/smoke-test.ps1
# Ar trebui: ✅ All smoke tests passed!
```

---

## 📞 Când ceri ajutor

Includează următoarele:
1. **Logs BE:** ultimele 20 linii din consolă uvicorn
2. **Logs FE:** browser console + Network tab (screenshot)
3. **ENV-uri:** `BACKEND_CORS_ORIGINS`, `VITE_API_URL`, `HEYGEN_API_KEY` (valori sanitizate)
4. **Request/Response exact:** copy-paste din Network tab (Headers + Response)
5. **Acțiune care declanșează eroarea:** "click pe Generate Video" → POST /api/... → 400

Cu aceste info, debugging devine 10x mai rapid! 🚀
