# Ghid de Testare End-to-End - AutoPro Daune

## Configurare Mediu de Dezvoltare

### Backend
1. Setează variabilele de mediu în `services/api/.env`:
```bash
FAKE_MODE=true
DEV_ALLOW_ANON=true
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SECRET_KEY=your_secret_key
REDIS_URL=redis://localhost:6379/0
```

2. Rulează verificatorul de configurare:
```bash
cd services/api
python scripts/config_doctor.py
```

3. Pornește backend-ul:
```bash
cd services/api
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Frontend
1. Verifică configurația în `02_FRONTEND_UI_CLEAN/.env`:
```bash
VITE_API_BASE_URL=/api
VITE_API_TIMEOUT=20000
```

2. Pornește frontend-ul:
```bash
cd 02_FRONTEND_UI_CLEAN
npm install
npm run dev
```

## Scenarii de Testare

### 1. Leads Management
- [ ] **List Leads**: GET /api/leads/ - Verifică că se încarcă lista de lead-uri
- [ ] **Create Lead**: POST /api/leads/ - Creează un lead nou cu date valide
- [ ] **Lead Timeline**: Verifică că timeline-ul se actualizează
- [ ] **Upload Files**: Testează încărcarea de fișiere pentru leads

### 2. Video Generation
- [ ] **Internal Generate**: POST /api/video/internal-generate
  - Topic: "Accidente auto"
  - Verifică că video-ul se generează fără erori
- [ ] **Avatar Humanize**: POST /api/video/avatar-humanize
  - Verifică că video-ul cu avatar se generează
- [ ] **Thumbnail Generation**: Verifică generarea thumbnail-urilor
- [ ] **Video List**: GET /api/video/stats - Verifică lista video-urilor

### 3. Social Media
- [ ] **Followers**: GET /api/social/followers
  - Verifică date pentru TikTok, Instagram, Facebook
- [ ] **Posts**: GET /api/social/posts - Verifică lista postărilor
- [ ] **Caption Generator**: POST /api/social/caption
  - Topic: "Daune auto"
  - Tone: "professional"
  - Platform: "TikTok"
  - Verifică că caption-ul se generează corect

### 4. Financial
- [ ] **Dashboard**: GET /api/financial/dashboard
  - Verifică metrici: revenue, costs, profit, ROI
- [ ] **Breakdown**: GET /api/financial/breakdown?period=30d
  - Verifică timeline, costuri pe categorie
- [ ] **Cost Categories**: GET /api/financial/cost-categories
  - Verifică categoriile de costuri
- [ ] **Export**: GET /api/financial/export?format=csv
  - Verifică export CSV

### 5. Automation
- [ ] **Status**: GET /api/working-automation/status
  - Verifică dacă automatizarea este activă
- [ ] **Toggle**: POST /api/working-automation/toggle
  - Activează/dezactivează automatizarea
- [ ] **Update Schedule**: POST /api/working-automation/update-schedule
  - Actualizează programarea job-urilor
- [ ] **Recent Actions**: GET /api/working-automation/recent-actions
  - Verifică acțiunile recente

### 6. Business Intelligence
- [ ] **Business Insights**: GET /api/advanced-business-intelligence/business-insights
  - Verifică insight-urile generate de AI
- [ ] **Predictive Analytics**: GET /api/advanced-business-intelligence/predictive-analytics
  - Verifică predicțiile AI
- [ ] **Comprehensive Analytics**: GET /api/advanced-business-intelligence/comprehensive-analytics
  - Verifică analizele comprehensive

## Verificări UI

### Console Browser
- [ ] **Fără erori în console**: Nu ar trebui să existe erori JavaScript
- [ ] **API Calls**: Toate cererile HTTP returnează 200 OK sau erori controlate
- [ ] **Network Tab**: Verifică că toate endpoint-urile sunt apelate corect

### Componente UI
- [ ] **AdvancedAnalytics**: Afișează date reale, fără mock-uri
- [ ] **CronScheduleEditor**: Încarcă job-uri de la backend
- [ ] **CostTracking**: Afișează costuri reale din breakdown
- [ ] **BudgetPlanner**: Afișează categorii din backend (read-only)
- [ ] **AICaptionGenerator**: Generează caption-uri via API
- [ ] **AIInsights**: Încarcă insights de la business intelligence API

### Funcționalități
- [ ] **Loading States**: Spinner-ele apar când se încarcă date
- [ ] **Error Handling**: Mesajele de eroare sunt clare și utile
- [ ] **Empty States**: UI-ul afișează mesaje prietenoase când nu există date
- [ ] **Toasts**: Notificările apar pentru success/error

## Teste de Integrare

### Mock vs Real Data
Verifică că următoarele NU mai conțin mock-uri:
- [ ] `AdvancedAnalytics.tsx` - folosește getFinancialBreakdown, getSocialFollowers, etc.
- [ ] `CronScheduleEditor.tsx` - folosește getAutomationStatus
- [ ] `CostTracking.tsx` - folosește getFinancialBreakdown
- [ ] `BudgetPlanner.tsx` - folosește getFinancialCostCategories
- [ ] `AICaptionGenerator.tsx` - folosește generateCaption
- [ ] `AIInsightsManager.ts` - folosește getAIInsights

### TypeScript
- [ ] **Fără "any"**: Toate tipurile sunt definite corect
- [ ] **Importuri corecte**: Toate importurile sunt rezolvate
- [ ] **Props tipizate**: Toate componentele au props tipizate

## Rulare Teste Automate

### Backend
```bash
cd services/api
python -m pytest tests/ -v --cov=app --cov-report=term-missing
```

### Frontend (dacă există)
```bash
cd 02_FRONTEND_UI_CLEAN
npm run test:run
npm run lint
```

## Troubleshooting

### Erori Comune

1. **CORS Errors**
   - Verifică că backend-ul rulează pe port 8001
   - Frontend proxy este configurat corect în vite.config.ts

2. **API Timeout**
   - Crește VITE_API_TIMEOUT în .env
   - Verifică că backend-ul răspunde la /health

3. **Authentication Errors**
   - DEV_ALLOW_ANON=true pentru development
   - Verifică token-ul în localStorage

4. **Missing Data**
   - FAKE_MODE=true pentru date simulate
   - Verifică logs backend pentru erori

## Checklist Final

- [ ] Backend rulează fără erori
- [ ] Frontend se compilează fără warnings
- [ ] Toate API calls returnează date valide
- [ ] UI este responsive și funcțional
- [ ] Fără console errors în browser
- [ ] Toate feature-urile principale funcționează
- [ ] Documentația este actualizată

## Next Steps

După testare:
1. Creează un backup în folderul `duplicates/`
2. Commitează modificările
3. Push către remote (dacă este cazul)
4. Documentează orice bug găsit în GitHub Issues
