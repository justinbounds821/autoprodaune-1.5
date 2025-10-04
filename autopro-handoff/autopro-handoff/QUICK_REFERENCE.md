# ⚡ Quick Reference Card – AutoPro Daune Integration

**One-page cheat sheet pentru debugging rapid și comenzi esențiale.**

---

## 🎯 Obiectiv Principal
FE(:3006/3007) ↔ BE(:8001) complet legate; TOP 5 features funcționale; STATUS=green în ~2h.

---

## 🚀 Comenzi Esențiale

### Start Backend
```powershell
cd services\api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### Start Frontend
```powershell
cd 02_FRONTEND_UI_CLEAN
npm run dev
```
→ Vite pe http://localhost:3006

### Smoke Test
```powershell
pwsh -File scripts\smoke-test.ps1
```
→ Testează 6 rute critice

### Health Check (manual)
```bash
curl http://127.0.0.1:8001/health
# Ar trebui: {"status":"ok","service":"autopro-daune","port":8001}
```

---

## 🔴 Top 5 Erori & Fix-uri

### 1. CORS blocat (preflight 403)
**Semn:** FE console: `Access to fetch blocked by CORS policy`

**Fix rapid:**
```bash
# services/api/.env
BACKEND_CORS_ORIGINS=http://localhost:3006,http://127.0.0.1:3006,http://localhost:3007,http://127.0.0.1:3007
```
→ Restart uvicorn

**Test:**
```js
fetch("http://127.0.0.1:8001/health").then(r => r.json()).then(console.log)
```

---

### 2. HeyGen 400 error (UX brutal)
**Semn:** POST `/api/video/video/heygen/generate` → 400, toast error generic

**Fix rapid (FE):**
```tsx
if (error?.response?.data?.detail?.includes("HEYGEN_API_KEY")) {
  return <Alert>🔑 HeyGen API key lipsește. Configurează în settings.</Alert>;
}
```
→ Disable butoane când key lipsește

---

### 3. Redis warning spam
**Semn:** Logs: `WARNING: Redis connection failed...` repetat

**Fix rapid:**
```bash
# services/api/.env
REDIS_URL=disabled
RATE_LIMIT_MODE=memory
```
→ Restart uvicorn → logs clean

---

### 4. Supabase tabel lipsește
**Semn:** Logs: `relation "automation_config" does not exist`

**Fix rapid:**
```sql
-- Rulează în Supabase SQL Editor (copy din sql/automation_config.sql)
create extension if not exists pgcrypto;
create table if not exists public.automation_config (...);
```

---

### 5. Vite proxy double prefix (404)
**Semn:** Network tab: request la `/leads` în loc de `/api/leads` → 404

**Fix rapid:**
```bash
# 02_FRONTEND_UI_CLEAN/.env
VITE_API_URL=http://127.0.0.1:8001  # bypass proxy, apel direct
```
→ Restart vite

---

## 📋 Feature Status (Quick Reference)

| Feature            | Status      | Fix Needed                        | Priority |
|--------------------|-------------|-----------------------------------|----------|
| Automation toggle  | **BROKEN**  | CORS fix                          | **1**    |
| Payments list      | **OK**      | —                                 | —        |
| Payments update    | **BLOCKED** | Conectează UI la `updatePayment()`| **1**    |
| Payments delete    | **BLOCKED** | Conectează UI la `deletePayment()`| **1**    |
| HeyGen avatars     | **BLOCKED** | UX banner când key lipsește       | **2**    |
| HeyGen generate    | **BLOCKED** | UX banner când key lipsește       | **2**    |
| Social posts list  | **MIXED**   | Standardizare pagination          | **2**    |
| Social posts CRUD  | **TODO**    | Verifică rute BE, conectează UI   | **2**    |
| Analytics dashboard| **OK**      | —                                 | —        |
| Analytics filters  | **TODO**    | Date picker custom (nice-to-have) | **3**    |

**Legendă:**
- **OK** = funcționează e2e
- **BROKEN** = eroare critică (ex: CORS)
- **BLOCKED** = ruta există dar UX/adaptor lipsește
- **MIXED** = funcționează parțial
- **TODO** = de implementat

---

## 🔧 ENV Variables (Critical)

### Backend (`services/api/.env`)
```env
BACKEND_CORS_ORIGINS=http://localhost:3006,http://127.0.0.1:3006,http://localhost:3007,http://127.0.0.1:3007
REDIS_URL=disabled
RATE_LIMIT_MODE=memory
HEYGEN_API_KEY=        # gol = UX banner în FE
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
```

### Frontend (`02_FRONTEND_UI_CLEAN/.env`)
```env
VITE_API_URL=http://127.0.0.1:8001
VITE_API_TIMEOUT=20000
VITE_ENV=development
```

---

## 🧪 Test Checklist (Quick)

- [ ] Health check: `curl http://127.0.0.1:8001/health` → 200 OK
- [ ] CORS: fetch din FE console → fără error
- [ ] Automation toggle: switch ON/OFF → status update
- [ ] Payments CRUD: list → create → edit → delete → toate OK
- [ ] HeyGen UX: fără key → banner apare, butoane disabled
- [ ] Social posts: list cu pagination → create post → OK
- [ ] Analytics: dashboard loads → metrici afișate
- [ ] Smoke test: `pwsh -File scripts\smoke-test.ps1` → toate ✅

**Dacă toate ✅ → STATUS=green! 🎉**

---

## 📖 Docs Hierarchy (unde să cauți info)

1. **Quick fix?** → `QUICK_REFERENCE.md` (acest fișier)
2. **Context general?** → `README_HANDOFF.md`
3. **Eroare specifică?** → `.vibe/TROUBLESHOOTING.md` + `logs/last_errors.txt`
4. **Feature status?** → `.vibe/INTEGRATION_SPEC.md`
5. **Decizie de design?** → `.vibe/LEDGER.md`
6. **Limite cod?** → `.vibe/STANDARDS.md`
7. **Reguli execuție?** → `.vibe/CONTRACT.json`
8. **Rute API?** → `openapi.json` sau http://127.0.0.1:8001/docs

---

## 🎯 Priorități (2h roadmap)

### Faza 1: CORS Fix (5 min) → deblochează tot
- Editează `.env` → restart uvicorn → test fetch

### Faza 2: Payments CRUD (30 min) → feature complet
- Conectează edit/delete buttons → test CRUD

### Faza 3: HeyGen UX (15 min) → user-friendly
- Creat banner component → integrat în UI → test fără key

### Faza 4: Automation Toggle (10 min) → feature complet
- Conectează switch la API → test ON/OFF

### Faza 5: Social Standardization (20 min) → consistență
- Aliniază pagination → test search + pagination

### Faza 6: Smoke Test (10 min) → validare
- Rulează `smoke-test.ps1` → toate ✅

### Faza 7: Docs Update (10 min) → done
- Update INTEGRATION_SPEC.md + LEDGER.md → commit

**Total:** ~2h → **STATUS=green** 🚀

---

## 💡 Pro Tips

1. **CORS issues:** Întotdeauna primul lucru de verificat când fetch-uri eșuează
2. **Network tab:** Best friend pentru debugging API calls (vezi exact ce se trimite/primește)
3. **BE logs:** Uvicorn loghează fiecare request → caută 403/404/500
4. **FE console:** Erori JavaScript + network failures → primele indicii
5. **Smoke test:** Rulează după fiecare fix major → early detection de regressions
6. **Commits mici:** ≤200 LOC → mai ușor de reviewuit și rollback dacă ceva crapă
7. **Test manual:** Click prin UI după fiecare schimbare → automated tests ≠ UX real

---

## 🆘 Când te blochezi

1. **Caută în docs:** `TROUBLESHOOTING.md` → `last_errors.txt` → `LEDGER.md`
2. **Verifică ENV:** sunt setate corect? (print în consolă pentru debug)
3. **Restart servere:** uneori un simplu restart rezolvă cache issues
4. **Check git diff:** ce s-a schimbat recent? (poate introducere de bug)
5. **Smoke test:** izolează problema (care rută exact eșuează?)
6. **Binary search:** dezactivează features până găsești cuplrit-ul
7. **Ask for help:** dacă >30 min blocat, escalate (nu sta blocat!)

---

## ✅ Definition of Done (Quick)

- [ ] CORS fix → FE comunică cu BE
- [ ] TOP 5 features funcționale (payments, automation, heygen, social, analytics)
- [ ] HeyGen UX friendly (banner când key lipsă)
- [ ] Redis silent fallback (fără warning spam)
- [ ] Supabase tabel creat (automation_config)
- [ ] Smoke test trece (toate ✅)
- [ ] Docs actualizate (INTEGRATION_SPEC + LEDGER)
- [ ] Zero erori critice (BE + FE logs clean)

**All ✅ = STATUS=green = 🎉 Done!**

---

**Keep this card open in a tab while integrating – you'll thank yourself later! 📌**
