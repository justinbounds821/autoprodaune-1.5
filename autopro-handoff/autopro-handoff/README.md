# 🎯 AutoPro Daune – Integration Handoff Package

> **Obiectiv:** FE(:3006/3007) ↔ BE(:8001) complet legate; TOP 5 features funcționale; UX HeyGen fără key; Redis fallback fără warning; Supabase adaptor/tabel; **STATUS=green**. Non-destructive, commits ≤200 LOC.

Acest pachet conține **tot ce este necesar** pentru a continua integrarea completă FE↔BE fără context suplimentar.

---

## 📂 Structura Package-ului

```
autopro-handoff/
├─ README.md                    # acest fișier (start here!)
├─ README_HANDOFF.md            # context 1-pager cu runtime, porturi, issues
├─ FRONTEND.md                  # detalii FE: ENV, API client, logs
├─ BACKEND.md                   # detalii BE: ENV, rute critice, logs
├─ ADMIN_GAPS.md                # ce lipsește în Admin UI (priorități)
├─ .env.example                 # toate variabilele ENV (valori dummy OK)
├─ openapi.json                 # export complet din http://127.0.0.1:8001/openapi.json
├─ logs/
│  ├─ backend_startup.txt       # output uvicorn din pornire
│  ├─ frontend_startup.txt      # output vite dev
│  └─ last_errors.txt           # erori frecvente + quick fixes
├─ sql/
│  └─ automation_config.sql     # schema pentru tabel lipsă Supabase
├─ scripts/
│  ├─ start-backend.ps1         # start BE (PowerShell)
│  ├─ start-frontend.ps1        # start FE (PowerShell)
│  ├─ smoke-test.ps1            # testează health + rute cheie (PowerShell)
│  └─ smoke-test.sh             # variantă bash
└─ .vibe/
   ├─ CONTRACT.json             # reguli de execuție (max LOC, commit policy)
   ├─ INTEGRATION_SPEC.md       # feature map UI ⇄ API (tabel cu status)
   ├─ TROUBLESHOOTING.md        # probleme & fixuri detaliate
   ├─ LEDGER.md                 # jurnal erori/decizii (timeline)
   └─ STANDARDS.md              # reguli: max linii, SRP, naming, etc.
```

---

## 🚀 Quick Start (pentru GPT/Director de integrare)

### 1. Citește contextul complet
În ordine:
1. **README_HANDOFF.md** → context general, porturi, known issues
2. **BACKEND.md** → rute API critice, ENV, erori frecvente
3. **FRONTEND.md** → client API, structură, UX gaps
4. **ADMIN_GAPS.md** → ce lipsește în UI (priorități 1/2/3)
5. **.vibe/CONTRACT.json** → reguli de execuție (commits ≤200 LOC, non-destructive)
6. **.vibe/INTEGRATION_SPEC.md** → feature map UI↔API (tabel cu status ok/broken/todo)

### 2. Setup local (dacă rulezi manual)
```powershell
# Backend
cd services\api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

# Frontend (alt terminal)
cd 02_FRONTEND_UI_CLEAN
npm run dev
```

### 3. Rulează smoke test
```powershell
pwsh -File scripts\smoke-test.ps1
```
Ar trebui să vadă:
- ✅ Health Check
- ✅ Mock Data
- ✅ Automation Status (sau CORS blocat → fix în .env)
- ✅ Payments List
- ⚠️ HeyGen Avatars (400 dacă key lipsește → UX banner necesar)

### 4. Fix-uri prioritare (în ordine)

#### 4.1 CORS Fix (critical)
**Problemă:** FE pe :3006 nu poate face fetch la BE :8001 → preflight 403

**Fix:**
```bash
# services/api/.env
BACKEND_CORS_ORIGINS=http://localhost:3006,http://127.0.0.1:3006,http://localhost:3007,http://127.0.0.1:3007
```
Restart uvicorn → smoke test → ar trebui să treacă.

#### 4.2 HeyGen UX (important)
**Problemă:** când `HEYGEN_API_KEY` lipsește, FE afișează toast error generic → user confuz

**Fix FE:**
```tsx
// Detectează error specific
if (error?.response?.data?.detail?.includes("HEYGEN_API_KEY")) {
  return (
    <Alert variant="warning">
      🔑 HeyGen API key lipsește. Configurează în settings sau contactează admin.
    </Alert>
  );
}

// Disable CTA când key lipsește
<Button disabled={!heygenAvailable} onClick={generateVideo}>
  Generate Video
</Button>
```

#### 4.3 Redis Fallback (low priority, dar poluează logs)
**Problemă:** WARNING spam în logs când Redis nu e disponibil

**Fix:**
```bash
# services/api/.env
REDIS_URL=disabled
RATE_LIMIT_MODE=memory
```
→ codul va skip warning dacă `REDIS_URL == "disabled"`

#### 4.4 Supabase Tabel (dacă lipsește)
**Problemă:** `automation_config` table missing → 500 errors

**Fix:**
Rulează `sql/automation_config.sql` în Supabase SQL Editor.

#### 4.5 Payments CRUD complet (important)
**Problemă:** adaptoare `updatePayment(id, data)` și `deletePayment(id)` există în `autoproApi.ts` dar nu sunt conectate la UI

**Fix:**
- Adaugă butoane edit/delete în tabel payments
- Conectează la `autoproApi.updatePayment()` / `autoproApi.deletePayment()`
- Test: edit payment → update successful, tabel refresh

---

## 📋 Definition of Done (STATUS=green)

Checklist pentru a marca integrarea ca **completă**:

- [ ] **CORS OK:** FE pe :3006/:3007 poate face fetch la BE fără preflight 403
- [ ] **TOP 5 features funcționale:**
  - [ ] Payments: list + create + update + delete ✅
  - [ ] Automation: status + toggle + schedule ✅
  - [ ] HeyGen: avatars + generate + status (cu UX banner când key lipsă) ✅
  - [ ] Social: posts list + create + update ✅
  - [ ] Analytics: dashboard + growth metrics ✅
- [ ] **HeyGen UX corect:** banner friendly când key lipsește, fără 500 error
- [ ] **Redis fallback:** in-memory fără warning spam (REDIS_URL=disabled)
- [ ] **Supabase:** automation_config tabel creat SAU adaptor fallback funcțional
- [ ] **Smoke test trece:** `pwsh -File scripts\smoke-test.ps1` → ✅ all passed
- [ ] **Docs actualizate:** INTEGRATION_SPEC.md, LEDGER.md cu ultimele decizii
- [ ] **Zero erori critice:** BE logs fără 500, FE console fără CORS/network errors

---

## 🛠️ Tools & Resources

### OpenAPI Explorer
```bash
# Rulează BE și deschide în browser:
http://127.0.0.1:8001/docs
```
→ Swagger UI interactiv cu toate rutele disponibile

### Log Debugging
- **BE logs:** rulează uvicorn cu `--reload`, vezi output în consolă
- **FE logs:** browser DevTools → Console + Network tab
- **Quick grep:** `grep "ERROR" logs/backend_startup.txt`

### Postman Collection (opțional)
Dacă ai nevoie de teste rapide API fără FE, importează `openapi.json` în Postman:
1. Postman → Import → OpenAPI 3.0 → selectează `openapi.json`
2. Generează collection automată cu toate rutele
3. Setează `base_url = http://127.0.0.1:8001`

---

## 📖 Reguli de Execuție (din .vibe/CONTRACT.json)

**IMPORTANT:** Citește `.vibe/CONTRACT.json` înainte de a face schimbări!

**Rezumat:**
- ✅ **Non-destructive:** nu șterge fără să întrebi
- ✅ **Commits ≤200 LOC:** split în micro-commits cu mesaje conventional (`feat|fix|refactor|docs(scope): message`)
- ✅ **Max 500 linii/fișier:** split când ajungi la 400 linii
- ✅ **Max 40 linii/funcție:** refactor dacă depășești
- ✅ **Single Responsibility:** o funcție = un singur lucru
- ✅ **No god classes:** split în module specializate
- ✅ **Clear naming:** fără `data`, `info`, `temp`, `x`

Vezi `.vibe/STANDARDS.md` pentru detalii complete.

---

## 🆘 Troubleshooting

**Problema cea mai frecventă:** CORS blocat
→ Vezi `.vibe/TROUBLESHOOTING.md` → secțiunea "CORS blocat (FE 3006/3007)"

**HeyGen nu merge:** API key lipsește
→ Vezi `.vibe/TROUBLESHOOTING.md` → secțiunea "HeyGen fără API key"

**Redis warnings spam:** dev fără Redis
→ Vezi `.vibe/TROUBLESHOOTING.md` → secțiunea "Redis warning spam"

**Altceva:** caută în `logs/last_errors.txt` → quick fixes pentru cele mai comune probleme

---

## 📊 Feature Map (quick reference)

Vezi `.vibe/INTEGRATION_SPEC.md` pentru tabel complet, dar rezumat:

| Feature            | FE Route           | BE Route                      | Status    |
|--------------------|--------------------|-------------------------------|-----------|
| Automation toggle  | /admin/automation  | POST /api/automation/toggle   | **broken** (CORS) |
| Payments list      | /admin/payments    | GET /api/financial/payments   | **ok**     |
| Payments update    | /admin/payments    | PUT /api/financial/payments/{id} | **blocked** (adaptor există, UI lipsește) |
| HeyGen avatars     | /admin/video       | GET /api/video/video/heygen/avatars | **blocked** (UX banner când key lipsă) |
| HeyGen generate    | /admin/video       | POST /api/video/video/heygen/generate | **blocked** (idem) |
| Social posts       | /admin/social      | GET /api/social/posts         | **mixed** (inconsistent pagination) |
| Analytics dashboard| /admin/analytics   | GET /api/dashboard/overview   | **ok**     |

**Legendă:**
- **ok** = funcționează e2e
- **broken** = eroare critică (ex: CORS)
- **blocked** = ruta există dar UX/adaptor lipsește
- **mixed** = funcționează parțial, inconsistențe

---

## 🎯 Priorități pentru Director de integrare

În ordine de impact:

1. **CORS fix** (5 min) → deblochează automation + HeyGen + toate fetch-urile
2. **HeyGen UX** (15 min) → user experience friendly când key lipsește
3. **Payments CRUD** (30 min) → completează update/delete în UI
4. **Social standardization** (20 min) → aliniază pagination (`q` → `search`, `offset` → `page`)
5. **Analytics filters** (30 min) → date picker pentru interval custom
6. **Supabase tabel** (5 min) → rulează SQL sau implementează fallback
7. **Redis silent fallback** (5 min) → stop warning spam

**Total estimate:** ~2h pentru STATUS=green! 🚀

---

## 🤝 Next Steps

1. **Read:** README_HANDOFF.md + .vibe/INTEGRATION_SPEC.md
2. **Fix:** CORS + HeyGen UX (primele 2 priorități)
3. **Test:** smoke test → ar trebui să treacă toate
4. **Iterate:** payments CRUD → social → analytics → done
5. **Document:** actualizează LEDGER.md cu deciziile luate
6. **Commit:** micro-commits ≤200 LOC cu mesaje conventional

**Regula de aur:** dacă ceva nu e clar, caută în `.vibe/` sau `logs/` înainte de a improviza! 📚

---

**Package creat de:** Claude (Sonnet 4.5) la data 2025-01-16
**Status:** ✅ Complete & Ready for handoff
**Contact:** vezi TROUBLESHOOTING.md pentru debugging tips

🚀 **Happy integrating!**
