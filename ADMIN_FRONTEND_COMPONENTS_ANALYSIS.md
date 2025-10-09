# Admin Frontend Components - Detailed Analysis

## VideoManagement.tsx

### API Calls
- `/api/advanced-video/list-generated`
- `/api/advanced-video/generate`
- `/api/video/{id}/thumbnail`

### Props
```typescript
{
  user: User,
  permissions: Permission[],
  onUpdate: () => void
}
```

### State Management
- Uses `useState`, `useEffect`
- Loading flags for async operations

### UI Components
- Table with job listings
- Form for script input
- Modals for actions

### Issues
- ❌ Missing pagination
- ❌ Job progress not updated in real-time
- ⚠️ Limited FAKE_MODE fallback

---

## FinancialDashboard.tsx

### Dependencies
- `autoproApi` for costs and revenues

### API Integration
- Uses `autoproApi.getFinancialDashboard()`
- Calls cost tracking endpoints

### Issues
- ❌ In FAKE_MODE responds with 503
- ❌ Missing fallback data
- ❌ Incomplete charts/graphs

---

## AutomationControl.tsx

### API Calls
- `getAutomationStatus()`
- `getAutomationLogs()`
- `startAutomation()`

### Issues
- ❌ `getAutomationLogs()` doesn't exist in backend
- ❌ No log display functionality
- ⚠️ Limited automation controls

---

## SocialMedia.tsx

### API Calls
- `/api/social/followers`
- `/api/social/post`

### State Management
- Uses `useState` for account management

### Issues
- ❌ No complete OAuth verification
- ❌ Missing account connection flow
- ⚠️ Limited platform support

---

## AIInsightsDashboard.tsx

### Dependencies
- pgvector for AI insights
- autoproApi methods

### Issues
- ❌ pgvector endpoints not available in FAKE_MODE
- ❌ Component blocks when endpoints fail
- ❌ No fallback mechanism

---

## GrowthDashboard.tsx

### Current Implementation
- Uses hardcoded mock data
- No real API integration

### Mock Data Example
```typescript
{
  visitors: 321,
  signups: 5,
  conversions: 12
}
```

### Issues
- ❌ Completely using mock data
- ❌ No real analytics endpoint
- ❌ Missing `/api/analytics/metrics` implementation

---

## UserManagement Component

### Status
**❌ MISSING - Does not exist**

### Required Features
- User list with pagination
- User creation/editing
- Permission management
- Role assignment

---

## Settings Component

### Status
**❌ MISSING - Does not exist**

### Required Features
- Application settings
- API key management
- Feature toggles
- Environment configuration

---

## Notifications Component

### Status
**❌ MISSING - Does not exist**

### Required Features
- Notification list
- Mark as read functionality
- Notification preferences
- Real-time updates

---

## Component Dependencies Summary

### Common Dependencies
```typescript
// UI Components
import { Button, Table, Modal, LoadingIndicator } from '@/components/ui'

// Services
import { autoproApi } from '@/services/autoproApi'
import axios from 'axios'

// Environment
VITE_API_BASE
VITE_FAKE_MODE
```

### Import Chain
```
AdminApp.tsx
  ├── AdminSidebar.tsx
  ├── VideoManagement.tsx
  ├── FinancialDashboard.tsx
  ├── AutomationControl.tsx
  ├── SocialMedia.tsx
  ├── AIInsightsDashboard.tsx
  └── GrowthDashboard.tsx
```
