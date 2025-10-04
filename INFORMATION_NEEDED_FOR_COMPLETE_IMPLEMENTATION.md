# Informatii Necesare Pentru Implementare Completa

**Data:** 2025-09-30  
**Scop:** Refactorizare si implementare completa fara backup, fara placeholders, cod real functional

---

## 1. BACKEND API - VERIFICARE ENDPOINTS

### Ce trebuie sa stiu:

**A. Endpoints care functioneaza deja:**
- [ ] `GET /health` - returneaza status OK?
- [ ] `GET /api/leads/` - returneaza 3 leads reale?
- [ ] `GET /api/financial/dashboard` - returneaza date financiare reale?
- [ ] `PUT /api/leads/{id}` - poate actualiza status lead?
- [ ] `POST /api/leads/` - poate crea lead nou?

**B. Endpoints pentru Video:**
- [ ] `GET /api/video/list` - exista?
- [ ] `POST /api/video/generate` - exista si functioneaza?
- [ ] `DELETE /api/video/{id}` - exista?
- [ ] Unde se salveaza video-urile generate? (`generated_videos/`?)

**C. Endpoints pentru Automation:**
- [ ] `GET /api/automation/status` - exista?
- [ ] `POST /api/automation/toggle` - exista?
- [ ] `POST /api/automation/trigger-post` - exista?
- [ ] `GET /api/automation/schedule` - exista?

**D. Endpoints pentru Social Media:**
- [ ] `GET /api/social/stats` - exista?
- [ ] `POST /api/social/post` - exista?
- [ ] `GET /api/social/posts` - exista?

**INTREBARI:**
1. Care dintre aceste endpoints sunt implementate COMPLET cu date reale?
2. Care endpoints lipsesc si trebuie create?
3. Care endpoints returneaza mock data deocamdata?

---

## 2. DATABASE SUPABASE - SCHEMA COMPLETA

### Ce trebuie sa stiu:

**A. Tabele existente - CONFIRMA:**
- [ ] `leads` - exista? Are 3 randuri cu Ion Popescu, Maria Ionescu, Petru Dumitrescu?
- [ ] `referrals` - exista?
- [ ] `social_posts` - exista?
- [ ] `video_jobs` - exista?
- [ ] `automation_config` - exista sau lipseste?
- [ ] `performance_metrics` - exista sau lipseste?

**B. Structura tabel `leads`:**
```sql
- id (UUID)
- name (TEXT)
- phone (TEXT)
- email (TEXT)
- location (TEXT)
- damage_type (TEXT)
- priority (TEXT) - 'low', 'medium', 'high', 'urgent'
- status (TEXT) - 'new', 'contacted', 'in-progress', 'completed', 'rejected'
- details (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

**CONFIRMA:** Structura de mai sus e corecta?

**C. Tabele lipsesc - trebuie create?**
- [ ] `automation_config` - DA/NU?
- [ ] `performance_metrics` - DA/NU?
- [ ] Alte tabele necesare?

**INTREBARI:**
1. Poti sa rulezi SQL in Supabase Dashboard pentru tabele lipsesc?
2. Ai acces la Supabase Dashboard acum?
3. Vrei sa-ti dau SQL-ul exact pentru tabele lipsesc?

---

## 3. VIDEO GENERATION - VERIFICARE SISTEM

### Ce trebuie sa stiu:

**A. ManoleVideoGenerator:**
- [ ] E implementat in `services/api/app/services/video_generator.py`?
- [ ] Foloseste MoviePy versiunea 1.0.3 sau 2.x?
- [ ] Are toate dependentele instalate?

**B. FFmpeg:**
- [ ] E instalat pe sistem?
- [ ] Path-ul e configurat corect?
- [ ] Comanda: `ffmpeg -version` functioneaza?

**C. Edge-TTS (Text-to-Speech):**
- [ ] E instalat? (`pip install edge-tts`)
- [ ] Voice romana configurata? (`ro-RO-AlinaNeural`)

**D. Output Video:**
- [ ] Folder: `generated_videos/` exista?
- [ ] Video-uri generate se salveaza corect?
- [ ] Format: MP4?

**INTREBARI:**
1. Ai testat generarea unui video simplu?
2. Functioneaza fara erori?
3. Unde ar trebui sa apara video-urile generate in UI?

---

## 4. SOCIAL MEDIA - API KEYS & INTEGRATION

### Ce trebuie sa stiu:

**A. TikTok:**
- [ ] Ai TikTok Developer Account?
- [ ] Ai Access Token real?
- [ ] Ai Client Key si Client Secret?
- [ ] SAU folosim mock data deocamdata?

**B. Instagram:**
- [ ] Ai Instagram Business Account?
- [ ] Ai Access Token real?
- [ ] E conectat la Facebook API?
- [ ] SAU folosim mock data deocamdata?

**C. Facebook:**
- [ ] Ai Facebook App ID?
- [ ] Ai App Secret?
- [ ] Ai Access Token?
- [ ] SAU folosim mock data deocamdata?

**D. YouTube:**
- [ ] Ai YouTube Data API enabled?
- [ ] Ai OAuth credentials?
- [ ] Poti uploada video-uri?
- [ ] SAU folosim mock data deocamdata?

**DECIZIE CRITICA:**
- Implementez cu API keys reale (necesita configurare complexa)?
- SAU implementez cu mock data dar sistem functional (mai rapid)?
- SAU implementez hybrid (TikTok real, restul mock)?

---

## 5. WHATSAPP BUSINESS API

### Ce trebuie sa stiu:

**A. WhatsApp Business API:**
- [ ] Ai WhatsApp Business Account?
- [ ] Ai Access Token?
- [ ] Ai Phone Number ID?
- [ ] Webhook e configurat?

**B. Integrare Lead Notification:**
- [ ] Cand vine lead nou, trimite mesaj WhatsApp?
- [ ] La cine? Numarul tau de telefon?
- [ ] Template mesaj specific?

**INTREBARI:**
1. WhatsApp e prioritate sau poate ramane mock data?
2. Ai deja configurare WhatsApp Business?

---

## 6. AUTOMATION SYSTEM - FLOW EXACT

### Ce trebuie sa stiu:

**A. Flow Automation (clarifica exact ce vrei):**

**Varianta 1: Automation Completa**
1. La 09:00, 15:00, 21:00 → genereaza video automat
2. Dupa generare → posteaza pe TikTok/Instagram/Facebook
3. Monitorizeaza engagement
4. Actualizeaza metrici

**Varianta 2: Automation Semi-Manuala**
1. Genereaza video manual din UI
2. Aproba video
3. Programeaza postare
4. Posteaza automat la ora setata

**Varianta 3: Mock Automation (pentru testare)**
1. Simuleaza generare video
2. Simuleaza postare
3. Afiseaza date fake dar realiste in UI

**INTREBARI:**
1. Care varianta vrei implementata?
2. Automation trebuie sa ruleze non-stop sau doar cand pornesti manual?
3. Celery worker e configurat si ruleaza?

---

## 7. FINANCIAL TRACKING - DATE REALE SAU MOCK?

### Ce trebuie sa stiu:

**A. Revenue Tracking:**
- [ ] Date reale din Supabase (`revenue` tabel)?
- [ ] Calculat din leads convertite?
- [ ] Mock data pentru demonstratie?

**B. Cost Tracking:**
- [ ] Costuri API (TikTok, Instagram)?
- [ ] Costuri video generation?
- [ ] Costuri server?
- [ ] Mock data?

**C. ROI Calculation:**
- [ ] Formula: `(Revenue - Cost) / Cost * 100`?
- [ ] Date reale sau estimate?

**INTREBARI:**
1. Financial data trebuie sa fie reala sau poate fi mock deocamdata?
2. Unde se stocheaza revenue si cost in database?

---

## 8. STRUCTURA FISIERE - LIMITE SI ORGANIZARE

### Ce trebuie sa stiu:

**A. Reguli refactorizare (confirma):**
- [ ] Max 500 linii per fisier?
- [ ] Max 400 linii per fisier?
- [ ] Split imediat daca aproape de limita?

**B. Organizare services:**
```
services/
├── api/
│   ├── LeadService.ts (max X linii)
│   ├── VideoService.ts (max X linii)
│   ├── SocialMediaService.ts (max X linii)
│   ├── AutomationService.ts (max X linii)
│   └── FinancialService.ts (max X linii)
```

**C. Organizare components:**
```
components/
├── leads/
│   ├── LeadList.tsx (max X linii)
│   ├── LeadCard.tsx (max X linii)
│   └── LeadForm.tsx (max X linii)
├── videos/
│   ├── VideoList.tsx
│   ├── VideoPlayer.tsx
│   └── VideoGenerator.tsx
└── ...
```

**INTREBARI:**
1. Limita exacta de linii per fisier?
2. Cum vrei organizate componentele - pe feature sau pe tip?
3. Hook-uri custom separate sau in componente?

---

## 9. ENVIRONMENT VARIABLES - CONFIGURARE COMPLETA

### Ce trebuie sa stiu:

**A. Backend `.env` - CE AI DEJA:**
```env
SUPABASE_URL=https://orctxxpyiqzbordibqxi.supabase.co
SUPABASE_ANON_KEY=sb_publishable_7Qh8xZcxTp5tLb87ezr5tg_s2_cw0uj
SUPABASE_SERVICE_KEY=sb_secret_I0Kvv13Pn05qPDsTQvJWmw_DtVHPQPz
```

**B. CE LIPSESTE (completeaza):**
```env
# Social Media
TIKTOK_ACCESS_TOKEN=?
INSTAGRAM_ACCESS_TOKEN=?
FACEBOOK_APP_ID=?
FACEBOOK_APP_SECRET=?
YOUTUBE_CLIENT_ID=?

# WhatsApp
WHATSAPP_ACCESS_TOKEN=?
WHATSAPP_PHONE_NUMBER_ID=?

# Video
FFMPEG_PATH=? (default sau custom?)

# Redis (optional)
REDIS_URL=? (ai Redis instalat?)
```

**INTREBARI:**
1. Ai aceste keys sau le sar deocamdata?
2. Redis e instalat si configured?
3. Celery e configurat?

---

## 10. TESTING & QUALITY - CE NIVEL VREI?

### Ce trebuie sa stiu:

**A. Testing:**
- [ ] Unit tests (Jest/Pytest)?
- [ ] Integration tests?
- [ ] E2E tests (Playwright)?
- [ ] SAU skip testing deocamdata?

**B. Error Handling:**
- [ ] Try-catch peste tot?
- [ ] Error boundaries in React?
- [ ] Logging structured?

**C. Code Quality:**
- [ ] TypeScript strict mode?
- [ ] ESLint + Prettier?
- [ ] Pre-commit hooks?

**INTREBARI:**
1. Cat de important e testing acum?
2. Error handling minimal sau complet?

---

## 11. DEPLOYMENT & PRODUCTION

### Ce trebuie sa stiu:

**A. Unde va rula in productie?**
- [ ] Local (laptop/desktop)?
- [ ] VPS/Server?
- [ ] Vercel + Railway?
- [ ] Docker?

**B. Domain & HTTPS:**
- [ ] Ai domeniu?
- [ ] HTTPS necesar?
- [ ] Nginx config?

**INTREBARI:**
1. Deployment e prioritate sau deocamdata local?
2. Docker e preferat sau direct?

---

## 12. UI/UX - DESIGN REQUIREMENTS

### Ce trebuie sa stiu:

**A. Design System:**
- [ ] Shadcn UI (actual) - OK?
- [ ] Culori custom sau default?
- [ ] Logo AutoPro Daune - ai fisier?

**B. Responsive:**
- [ ] Desktop + Mobile?
- [ ] SAU doar Desktop deocamdata?

**C. Accessibility:**
- [ ] ARIA labels?
- [ ] Keyboard navigation?
- [ ] SAU skip deocamdata?

---

## PRIORITIZARE - ALEGE 1-3 FOCUS AREAS

Din toate functiile, care sunt TOP 3 prioritati?

**Opțiuni:**
1. Lead Management (CRUD complet, real functional)
2. Video Generation (genereaza si afiseaza video-uri reale)
3. Automation System (genereaza + posteaza automat)
4. Financial Dashboard (tracking real revenue/cost)
5. Social Media Integration (posting real pe platforme)
6. Analytics & Reports (metrici si grafice)

**ALEGE 1-3 SI SPUNE-MI:**
- Care functioneaza deja partial?
- Care e cea mai importanta pentru tine?
- Care poate ramane mock data deocamdata?

---

## RASPUNDE LA ACESTE INTREBARI:

### BACKEND:
1. Ce endpoints functioneaza 100% cu date reale acum?
2. MoviePy e versiunea 1.0.3 sau 2.x?
3. FFmpeg e instalat si functional?

### DATABASE:
4. Tabela `automation_config` exista in Supabase?
5. Tabela `performance_metrics` exista in Supabase?
6. Poti rula SQL in Supabase Dashboard?

### SOCIAL MEDIA:
7. Ai API keys reale pentru TikTok/Instagram/Facebook?
8. SAU implementez cu mock data functional?

### VIDEO:
9. ManoleVideoGenerator functioneaza si genereaza video-uri?
10. Unde vrei sa apara video-urile in admin panel?

### AUTOMATION:
11. Automation trebuie sa ruleze non-stop sau manual?
12. Celery worker e configurat?

### REFACTORIZARE:
13. Limita linii per fisier: 400 sau 500?
14. Organizare componente: pe feature sau pe tip?

### PRIORITATE:
15. TOP 3 functionalitati pe care le vrei COMPLET functionale?

---

## DUPA CE RASPUNZI:

Voi crea:
1. Plan detaliat 40-50 TODO-uri organizate
2. Structura noua de foldere si fisiere
3. Refactorizare completa fara backup
4. Implementari reale, fara placeholders
5. Cod curat, bine organizat, sub limite

**RASPUNDE LA TOATE INTREBARILE SI INCEP IMPLEMENTAREA!**
