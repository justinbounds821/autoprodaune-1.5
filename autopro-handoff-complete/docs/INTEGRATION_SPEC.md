# Frontend ↔ API Integration Specification

## Component to API Mapping

### Dashboard Components

| Component | API Method | Endpoint | Payload | Status |
|-----------|------------|----------|---------|--------|
| `Dashboard.tsx` | `getOverviewStats()` | `/api/dashboard/overview` | None | ✅ Implemented |
| `FinancialDashboard.tsx` | `getRevenueData()` | `/api/financial/revenue` | None | ⚠️ Stub |
| `FinancialDashboard.tsx` | `getCostData()` | `/api/financial/costs` | None | ⚠️ Stub |

### Lead Management

| Component | API Method | Endpoint | Payload | Status |
|-----------|------------|----------|---------|--------|
| `LeadManagement.tsx` | `getLeads()` | `/api/leads/` | `{page, limit}` | ✅ Implemented |
| `LeadTracker.tsx` | `createLead()` | `/api/leads/` | `{name, phone, email, source}` | ✅ Implemented |

### Video Management

| Component | API Method | Endpoint | Payload | Status |
|-----------|------------|----------|---------|--------|
| `VideoManagement.tsx` | `getVideos()` | `/api/video/list` | None | ⚠️ Stub |
| `VideoManagement.tsx` | `generateHeyGenVideo()` | `/api/video/video/heygen/generate` | `{script, quality, style}` | ✅ Implemented* |
| `ManoleVideoCreator.tsx` | `generateManoleVideo()` | `/api/video/manole-generate` | `{script, style}` | ✅ Implemented |

### Automation Control

| Component | API Method | Endpoint | Payload | Status |
|-----------|------------|----------|---------|--------|
| `AutomationControl.tsx` | `getAutomationStatus()` | `/api/automation/status` | None | ✅ Implemented |
| `AutomationControl.tsx` | `getAutomationLogs()` | `/api/automation/logs` | None | ⚠️ Stub |
| `AutomationControl.tsx` | `startAutomation()` | `/api/automation/start` | None | ⚠️ Stub |
| `AutomationControl.tsx` | `stopAutomation()` | `/api/automation/stop` | None | ⚠️ Stub |

### Social Media

| Component | API Method | Endpoint | Payload | Status |
|-----------|------------|----------|---------|--------|
| `SocialMedia.tsx` | `getSocialPosts()` | `/api/social/posts` | None | ⚠️ Stub |
| `SocialMedia.tsx` | `createPost()` | `/api/social/posts` | `{content, platform, schedule}` | ⚠️ Stub |
| `SocialMedia.tsx` | `getPostAnalytics()` | `/api/social/analytics` | None | ⚠️ Stub |

### Payment & Financial

| Component | API Method | Endpoint | Payload | Status |
|-----------|------------|----------|---------|--------|
| `PaymentTracker.tsx` | `getPayments()` | `/api/financial/payments` | `{filters}` | ✅ Implemented |
| `PaymentTracker.tsx` | `createPayment()` | `/api/financial/payments` | `{amount, description, date}` | ✅ Implemented |
| `PaymentTracker.tsx` | `updatePayment()` | `/api/financial/payments/{id}` | `{updates}` | ✅ Implemented |
| `PaymentTracker.tsx` | `deletePayment()` | `/api/financial/payments/{id}` | None | ✅ Implemented |

### Growth & Intelligence (Missing Components)

| Feature | API Method | Endpoint | Payload | Status |
|---------|------------|----------|---------|--------|
| Growth Engine | `getGrowthStatus()` | `/api/growth-engine/growth-status` | None | ❌ No Frontend |
| Growth Engine | `generateMassContent()` | `/api/growth-engine/generate-mass-content` | `{type, count}` | ❌ No Frontend |
| Intelligent Conversion | `analyzeLead()` | `/api/intelligent-conversion/analyze-lead` | `{leadId}` | ❌ No Frontend |
| Customer Nurturing | `startNurturingJourney()` | `/api/customer-nurturing/start-nurturing-journey` | `{customerId}` | ❌ No Frontend |
| Master Growth | `activateExplosiveGrowth()` | `/api/master-growth/activate-explosive-growth` | None | ❌ No Frontend |

## API Client Implementation Status

### `autoproApi.ts` - Current Methods (20/182 endpoints)

```typescript
// ✅ Implemented Methods
getLeads, createLead, getFinancialDashboard, getInvoices, createInvoice,
getPayments, createPayment, getNotifications, markNotificationRead,
getAIInsights, generateAIReport, getTaxRates, calculateTax,
getAutomationStatus, getAutomationLogs, updateAutomationSettings, toggleAutomation,
getVideos, getPaymentOverview, updatePayment, deletePayment,
getOverviewStats, startAutomation, stopAutomation, triggerAutomation,
getRevenueData, getCostData, getSocialPosts, getPostAnalytics,
createPost, schedulePost, checkApiHealth

// ❌ Missing Methods (162 endpoints)
// Growth Engine (4)
getGrowthEngineStatus, generateMassContent, viralBoost, getGrowthAnalytics

// Intelligent Conversion (5)  
analyzeLead, executeConversionActions, getConversionAnalytics,
massLeadProcessing, getSystemStatus

// Customer Nurturing (6)
startNurturingJourney, massNurturingActivation, getNurturingAnalytics,
optimizeNurturing, getCustomerJourneyMap, getNurturingSystemStatus

// Affiliate Multiplication (6)
createAffiliate, processReferral, getAffiliateLeaderboard,
viralBoostCampaign, getViralAnalytics, getAffiliateSystemStatus

// Growth Analytics (8)
getGrowthDashboard, getRealTimeMetrics, getGrowthProjections,
getCompetitiveIntelligence, getOptimizationRecommendations,
getROIAnalysis, getGrowthHealthScore, getSystemStatus

// Master Growth (6)
activateExplosiveGrowth, getSystemOverview, getActivationStatus,
emergencyScaleUp, getGrowthEcosystemSummary, getMasterStatus

// Advanced Video (4)
generateAdvancedVideo, getCapabilities, getListGenerated, getPreview

// Professional Video (4)
generateProfessionalVideo, getAvatars, getBackgrounds, testCapabilities

// And 125+ more endpoints...
```

## Missing Frontend Components

### Required Components for Complete Integration

1. **Growth Engine Dashboard** (`components/GrowthEngine/GrowthEngineDashboard.tsx`)
2. **Intelligent Conversion Panel** (`components/IntelligentConversion/LeadAnalyzer.tsx`)
3. **Customer Nurturing Manager** (`components/CustomerNurturing/JourneyManager.tsx`)
4. **Master Growth Control** (`components/MasterGrowth/GrowthOrchestrator.tsx`)
5. **Advanced Video Editor** (`components/AdvancedVideo/VideoEditor.tsx`)
6. **Professional Video Tools** (`components/ProfessionalVideo/Generator.tsx`)

## Integration Gaps Summary

- **Total API Endpoints**: 182
- **Frontend Integrated**: ~20 (11%)
- **Missing API Methods**: 162 (89%)
- **Missing Components**: 6 major components
- **Stub Implementations**: ~160 endpoints return empty data

## Priority for Implementation

### High Priority (Core Business)
1. Complete social media posting functionality
2. Fix automation scheduler integration
3. Implement notification system
4. Complete financial tracking

### Medium Priority (Growth Features)
1. Growth engine dashboard
2. Intelligent conversion tools
3. Customer nurturing system

### Low Priority (Advanced Features)
1. Master growth orchestration
2. Advanced video tools
3. Professional video generation
