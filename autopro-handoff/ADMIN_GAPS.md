# ADMIN – Gaps

## 1. Automation schedule UI
**Problemă:** UI nu trimite payload corect pentru schedule automation
**Structură actuală:** `{ enabled: bool }` (toggle simplu)
**Structură dorită:** `{ enabled: bool, schedule?: { days: string[], time: string } }`
**Prioritate:** **1** (critical)

## 2. Payments – adaptor lipsă pentru update/delete
**Problemă:** `updatePayment(id, updates)` și `deletePayment(id)` definite în `autoproApi.ts` dar **nu sunt conectate la UI**
**Rute BE:**
- PUT `/api/financial/payments/{id}` ✅ există
- DELETE `/api/financial/payments/{id}` ✅ există
**Fix:** conectează butoane edit/delete din tabel la aceste metode
**Prioritate:** **1** (critical)

## 3. HeyGen – lipsă UX când API key unset
**Problemă:** când `HEYGEN_API_KEY` lipsește, BE returnează 400 cu `{ detail: "HEYGEN_API_KEY..." }` → FE afișează toast error generic
**UX dorit:**
- Banner persistent: "HeyGen API key lipsește. Configurează în settings."
- Disable butoane "Generate Video" / "Load Avatars"
- Mesaj friendly în loc de error brutal
**Cod fix sugestie:**
```tsx
const { data: avatars, error } = useQuery("heygen-avatars", fetchAvatars, { retry: false });

if (error?.response?.data?.detail?.includes("HEYGEN_API_KEY")) {
  return <HeyGenKeyMissingBanner />;
}
```
**Prioritate:** **2** (important)

## 4. Social posts – inconsistent search/pagination
**Problemă:** unele rute folosesc `q` (query), altele `search`; pagination `page` vs `offset`
**Exemple:**
- `/api/leads?search=john&page=1&limit=20` ✅
- `/api/social/posts?q=viral&offset=0` ❌ inconsistent
**Fix:** standardizează pe `search`, `page`, `limit` (aliniază cu leads router)
**Prioritate:** **2** (important)

## 5. Analytics – lipsă filtre date
**Problemă:** dashboard afișează metrici dar nu are date picker pentru interval custom
**UX dorit:**
- Preset: "7d", "30d", "90d", "ytd"
- Custom: date_from, date_to
**API:** BE acceptă deja `?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD` în `/api/financial/roi/{period}`
**Prioritate:** **3** (nice-to-have)

## 6. Automation – logs UI
**Problemă:** există rută `/api/automation/logs` dar nu e afișată în Admin
**UX dorit:** tabel cu ultimele 50 logs (timestamp, action, status, message)
**Prioritate:** **3** (nice-to-have)

---

## Priorități rezumat
1. **Automation schedule** + **Payments update/delete** → critical, fără acestea UX este blocat
2. **HeyGen UX** + **Social search standardization** → important pentru consistență
3. **Analytics filters** + **Automation logs UI** → nice-to-have, îmbunătățesc UX dar nu blochează workflow
