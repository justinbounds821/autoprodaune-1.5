# ✅ Integration Checklist – Director de integrare

Folosește acest checklist pentru a te asigura că toate pașii sunt îndepliniți în ordine. Marchează cu `[x]` când completezi un pas.

---

## 📖 Faza 1: AUDIT & Context (15 min)

- [ ] Citit **README_HANDOFF.md** → înțeles runtime, porturi, known issues
- [ ] Citit **BACKEND.md** → înțeles rute critice, ENV, erori
- [ ] Citit **FRONTEND.md** → înțeles API client, structură, UX gaps
- [ ] Citit **ADMIN_GAPS.md** → înțeles priorități (1/2/3)
- [ ] Citit **.vibe/CONTRACT.json** → înțeles reguli (commits ≤200 LOC, non-destructive)
- [ ] Citit **.vibe/INTEGRATION_SPEC.md** → înțeles feature map (ok/broken/todo)
- [ ] Citit **.vibe/STANDARDS.md** → înțeles limite (max linii, SRP, naming)
- [ ] Explorat **openapi.json** → verificat rute disponibile în BE

**Output:** Hai o viziune clară a ce trebuie legat și ce lipsește.

---

## 🔧 Faza 2: CORS Fix (5 min)

- [ ] Verificat `services/api/.env` → `BACKEND_CORS_ORIGINS` include `:3006` și `:3007`
- [ ] Dacă NU: editat `.env`:
  ```env
  BACKEND_CORS_ORIGINS=http://localhost:3006,http://127.0.0.1:3006,http://localhost:3007,http://127.0.0.1:3007
  ```
- [ ] Restartat uvicorn: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload`
- [ ] Testat din FE browser console:
  ```js
  fetch("http://127.0.0.1:8001/health").then(r => r.json()).then(console.log)
  ```
  → Ar trebui `{status: "ok", ...}` fără eroare CORS
- [ ] Verificat Network tab: preflight OPTIONS → `200 OK` (nu 403)

**Output:** CORS deblocat, FE poate comunica cu BE.

**Commit:** `fix(cors): add :3006 and :3007 to allowed origins`

---

## 🎨 Faza 3: HeyGen UX (15 min)

### 3.1 Verificare status actual
- [ ] Testat POST `/api/video/video/heygen/generate` fără `HEYGEN_API_KEY`:
  ```bash
  curl.exe -X POST http://127.0.0.1:8001/api/video/video/heygen/generate -H "Content-Type: application/json" -d '{"script":"test"}'
  ```
  → Ar trebui `400 {"detail":"HEYGEN_API_KEY nu este configurat..."}`

### 3.2 Implementare banner FE
- [ ] Creat componentă `HeyGenKeyMissingBanner.tsx` (sau echivalent):
  ```tsx
  export function HeyGenKeyMissingBanner() {
    return (
      <Alert variant="warning" className="mb-4">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>HeyGen API Key lipsește</AlertTitle>
        <AlertDescription>
          Configurează HEYGEN_API_KEY în settings pentru a genera videoclipuri AI.
          Contactează administratorul pentru detalii.
        </AlertDescription>
      </Alert>
    );
  }
  ```

### 3.3 Integrare în HeyGen UI
- [ ] În componenta `/admin/video` (sau echivalent), adăugat logică:
  ```tsx
  const { data: avatars, error } = useQuery("heygen-avatars", fetchAvatars, { retry: false });

  if (error?.response?.data?.detail?.includes("HEYGEN_API_KEY")) {
    return <HeyGenKeyMissingBanner />;
  }
  ```
- [ ] Disable butoane "Generate Video" și "Load Avatars" când `heygenAvailable === false`
- [ ] Testat: fără key → banner apare, butoane disabled → UX friendly ✅

**Output:** User vede mesaj clar, nu error 400 brutal.

**Commit:** `feat(heygen): add friendly UX banner when API key missing`

---

## 💳 Faza 4: Payments CRUD (30 min)

### 4.1 Verificare adaptoare existente
- [ ] Verificat `autoproApi.ts`:
  - `updatePayment(id, updates)` → ✅ există
  - `deletePayment(id)` → ✅ există

### 4.2 Conectare la UI
- [ ] În `/admin/payments` (sau componenta echivalentă):
  - [ ] Adăugat buton **Edit** în fiecare row din tabel → open modal cu form
  - [ ] Form edit → apelează `autoproApi.updatePayment(id, formData)` → toast success → refresh listă
  - [ ] Adăugat buton **Delete** → confirmă → apelează `autoproApi.deletePayment(id)` → toast success → refresh listă

### 4.3 Test e2e
- [ ] Creat payment nou → verificat apare în listă
- [ ] Edit payment (schimbat amount/status) → verificat update reușit
- [ ] Delete payment → verificat dispare din listă
- [ ] Verificat în BE logs: PUT `/api/financial/payments/{id}` → `200 OK`

**Output:** Payments CRUD complet funcțional.

**Commit:** `feat(payments): connect update and delete to UI`

---

## 🤖 Faza 5: Automation Toggle (10 min)

- [ ] Verificat rută BE: POST `/api/automation/toggle` sau `/api/working-automation/toggle`
- [ ] În `/admin/automation`, conectat switch toggle la:
  ```tsx
  const handleToggle = async (enabled: boolean) => {
    await autoproApi.toggleAutomation(enabled);
    toast.success(`Automation ${enabled ? "enabled" : "disabled"}`);
    refetch();  // refresh status
  };
  ```
- [ ] Testat: toggle ON → status devine `enabled: true` → backend loghează schimbarea
- [ ] Testat: toggle OFF → status devine `enabled: false`

**Output:** Automation toggle funcțional.

**Commit:** `feat(automation): wire toggle switch to backend`

---

## 📱 Faza 6: Social Posts (20 min)

### 6.1 Standardizare pagination
- [ ] Verificat rută BE: GET `/api/social/posts` → parametri actuali (`q`, `offset` sau `search`, `page`?)
- [ ] Dacă inconsistent: aliniază cu pattern din `/api/leads`:
  - Query param: `search` (nu `q`)
  - Pagination: `page`, `limit` (nu `offset`)
- [ ] Update adaptor FE: `getSocialPosts({ search, page, limit })`

### 6.2 CRUD UI
- [ ] Lista posts → ✅ funcțional
- [ ] Create post → ✅ funcțional
- [ ] Update post → verificat dacă există rută BE `PUT /api/social/posts/{id}` → conectat la UI
- [ ] Delete post → verificat dacă există rută BE `DELETE /api/social/posts/{id}` → conectat la UI

**Output:** Social posts CRUD consistent cu restul API-ului.

**Commit:** `refactor(social): standardize pagination and complete CRUD`

---

## 📊 Faza 7: Analytics Filters (30 min)

- [ ] În `/admin/analytics`, adăugat date picker (ex: react-datepicker sau shadcn calendar):
  - Preset buttons: "7d", "30d", "90d", "ytd"
  - Custom: date_from, date_to
- [ ] Conectat la apeluri API:
  ```tsx
  const { data } = useQuery(["analytics", period, dateFrom, dateTo], () =>
    autoproApi.getGrowthAnalytics({ period, date_from: dateFrom, date_to: dateTo })
  );
  ```
- [ ] Testat: schimbat perioada → grafice refresh cu date corecte

**Output:** Analytics flexibil cu filtre custom.

**Commit:** `feat(analytics): add date range picker for custom periods`

---

## 🗄️ Faza 8: Supabase Tabel (5 min)

- [ ] Verificat dacă `automation_config` există în Supabase Table Editor
- [ ] Dacă NU:
  - [ ] Deschis Supabase SQL Editor
  - [ ] Copiat conținutul din `sql/automation_config.sql`
  - [ ] Rulat → verificat `Query executed successfully`
  - [ ] Refresh Table Editor → tabel `automation_config` apare
- [ ] Testat GET `/api/automation/status` → ar trebui să returneze date reale (nu mock)

**Output:** Backend poate citi/scrie automation config în DB.

**Commit:** (SQL migration, nu cod) → documentat în LEDGER.md

---

## 🔕 Faza 9: Redis Fallback Silent (5 min)

- [ ] Verificat `services/api/.env`:
  ```env
  REDIS_URL=disabled
  RATE_LIMIT_MODE=memory
  ```
- [ ] Restartat uvicorn
- [ ] Verificat logs: NU ar trebui să apară `WARNING: Redis connection failed` repetat
- [ ] Dacă apare încă: verificat cod în `main.py:199-206` → skip warning când `REDIS_URL == "disabled"`

**Output:** Logs clean în dev, fără warning spam.

**Commit:** (dacă modifici cod) `fix(redis): silent fallback when REDIS_URL=disabled`

---

## 🧪 Faza 10: Smoke Test (10 min)

- [ ] Rulat `pwsh -File scripts\smoke-test.ps1` (sau `.sh` pe Linux/Mac)
- [ ] Verificat output:
  - [ ] ✅ Health Check → `200 {status: "ok", ...}`
  - [ ] ✅ Mock Data → `200 {success: true, ...}`
  - [ ] ✅ Automation Status → `200 {enabled: bool, ...}`
  - [ ] ✅ Payments List → `200 {items: [...], total: int}`
  - [ ] ✅ HeyGen Avatars → `200 {...}` sau `400 {detail: "HEYGEN_API_KEY..."}` (UX OK)
  - [ ] ✅ HeyGen Generate → `400` cu mesaj clar (fără key) → UX banner funcționează

**Output:** Toate testele trec SAU erori așteptate (ex: HeyGen fără key) sunt tratate UX-friendly.

---

## 📚 Faza 11: Docs Update (10 min)

- [ ] Actualizat `.vibe/INTEGRATION_SPEC.md`:
  - Schimbat status din `broken` → `ok` pentru features completate
  - Schimbat status din `blocked` → `ok` pentru UX improvements
  - Adăugat note despre decizii luate
- [ ] Actualizat `.vibe/LEDGER.md`:
  - Adăugat intrări noi pentru fiecare fix/decizie:
    ```markdown
    ## [2025-01-XX HH:mm] frontend – HeyGen UX banner implementat
    **Symptom:** 400 error brutal când key lipsește
    **Fix aplicat:** HeyGenKeyMissingBanner component + disable CTA
    **Commit(s):** <hash>
    ```

**Output:** Documentație up-to-date pentru următoarea persoană care preia proiectul.

---

## 🎯 Faza 12: Definition of Done (STATUS=green) (5 min)

Verificat checklist final:

- [ ] **CORS OK:** FE pe :3006/:3007 poate face fetch fără preflight 403
- [ ] **TOP 5 features funcționale:**
  - [ ] Payments: list + create + update + delete ✅
  - [ ] Automation: status + toggle ✅
  - [ ] HeyGen: avatars + generate + status (UX banner când key lipsă) ✅
  - [ ] Social: posts list + create + update ✅
  - [ ] Analytics: dashboard + filters ✅
- [ ] **HeyGen UX corect:** banner friendly, butoane disabled când key lipsă
- [ ] **Redis fallback:** in-memory fără warning spam (REDIS_URL=disabled)
- [ ] **Supabase:** automation_config tabel creat ✅
- [ ] **Smoke test trece:** `pwsh -File scripts\smoke-test.ps1` → ✅ all passed
- [ ] **Docs actualizate:** INTEGRATION_SPEC.md + LEDGER.md up-to-date
- [ ] **Zero erori critice:** BE logs clean, FE console clean

**Dacă toate ✅ → STATUS=green! 🎉**

---

## 🚀 Next Steps (după STATUS=green)

- [ ] Creat PR cu toate commits (conventional messages)
- [ ] Merge în branch `feat/integration-green`
- [ ] Deploy în staging pentru QA
- [ ] Demo cu stakeholders
- [ ] Plan pentru următoarele features (analytics avansate, export data, etc.)

---

**Timp estimat total:** ~2-3h pentru toate fazele.

**Principiu:** Un pas la un timp, test după fiecare, commit ≤200 LOC. Slow is smooth, smooth is fast! 🐢💨
