# Admin Component Dependencies

## Component Dependency Graph

```
AdminApp.tsx (Root)
  │
  ├── AdminSidebar.tsx
  │
  ├── VideoManagement.tsx
  │   ├── Button (UI)
  │   ├── Table (UI)
  │   ├── Modal (UI)
  │   ├── LoadingIndicator (UI)
  │   ├── axios
  │   └── autoproApi
  │
  ├── FinancialDashboard.tsx
  │   ├── Card (UI)
  │   ├── Chart (UI)
  │   ├── Badge (UI)
  │   └── autoproApi
  │
  ├── AutomationControl.tsx
  │   ├── Switch (UI)
  │   ├── Table (UI)
  │   ├── Button (UI)
  │   └── autoproApi
  │
  ├── SocialMedia.tsx
  │   ├── Card (UI)
  │   ├── Button (UI)
  │   ├── Badge (UI)
  │   └── autoproApi
  │
  ├── AIInsightsDashboard.tsx
  │   ├── Card (UI)
  │   ├── Chart (UI)
  │   ├── List (UI)
  │   └── autoproApi
  │
  └── GrowthDashboard.tsx
      ├── Card (UI)
      ├── Chart (UI)
      ├── Table (UI)
      └── autoproApi
```

---

## VideoManagement.tsx

### File Location
`frontend/src/components/admin/VideoManagement.tsx`

### Component Dependencies
```typescript
import { Button } from '@/components/ui/button'
import { Table } from '@/components/ui/table'
import { Modal } from '@/components/ui/modal'
import { LoadingIndicator } from '@/components/ui/loading'
import { Badge } from '@/components/ui/badge'
```

### Service Dependencies
```typescript
import axios from 'axios'
import { autoproApi } from '@/services/autoproApi'
```

### API Methods Used
- `autoproApi.getAdvancedVideoJobs()`
- `autoproApi.generateAdvancedVideo(data)`
- `autoproApi.getVideoThumbnail(videoId)`
- `autoproApi.deleteVideoJob(jobId)`
- `autoproApi.regenerateVideo(jobId)`

### Environment Variables
```typescript
const API_BASE = import.meta.env.VITE_API_BASE
const FAKE_MODE = import.meta.env.VITE_FAKE_MODE === 'true'
```

### Props Interface
```typescript
interface VideoManagementProps {
  user: User;
  permissions: Permission[];
  onUpdate?: () => void;
}
```

### State Management
```typescript
const [jobs, setJobs] = useState<VideoJob[]>([])
const [loading, setLoading] = useState(true)
const [selectedJob, setSelectedJob] = useState<VideoJob | null>(null)
const [isGenerating, setIsGenerating] = useState(false)
```

### Used By
- `AdminApp.tsx` - Main admin route `/admin/videos`
- `AdminSidebar.tsx` - Navigation link

---

## FinancialDashboard.tsx

### File Location
`frontend/src/components/admin/FinancialDashboard.tsx`

### Component Dependencies
```typescript
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Chart } from '@/components/ui/chart'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
```

### Service Dependencies
```typescript
import { autoproApi } from '@/services/autoproApi'
```

### API Methods Used
- `autoproApi.getFinancialDashboard()`
- `autoproApi.getCosts()`
- `autoproApi.getCreditBalance(provider)`
- `autoproApi.trackCost(costData)`

### Environment Variables
```typescript
const FAKE_MODE = import.meta.env.VITE_FAKE_MODE === 'true'
```

### Props Interface
```typescript
interface FinancialDashboardProps {
  user: User;
}
```

### State Management
```typescript
const [financialData, setFinancialData] = useState<FinancialData | null>(null)
const [costs, setCosts] = useState<Cost[]>([])
const [loading, setLoading] = useState(true)
const [creditBalances, setCreditBalances] = useState<Record<string, number>>({})
```

### External Libraries
- `recharts` - For chart visualization
- `date-fns` - For date formatting

### Used By
- `AdminApp.tsx` - Route `/admin/financial`
- `AdminSidebar.tsx` - Navigation link

---

## AutomationControl.tsx

### File Location
`frontend/src/components/admin/AutomationControl.tsx`

### Component Dependencies
```typescript
import { Switch } from '@/components/ui/switch'
import { Table } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
```

### Service Dependencies
```typescript
import { autoproApi } from '@/services/autoproApi'
```

### API Methods Used
- `autoproApi.getAutomationStatus()`
- `autoproApi.startAutomation(automationId)`
- `autoproApi.stopAutomation(automationId)`
- `autoproApi.getAutomationLogs()` ⚠️ Not implemented

### Props Interface
```typescript
interface AutomationControlProps {
  user: User;
}
```

### State Management
```typescript
const [automationStatus, setAutomationStatus] = useState<AutomationStatus | null>(null)
const [logs, setLogs] = useState<AutomationLog[]>([])
const [loading, setLoading] = useState(true)
```

### Used By
- `AdminApp.tsx` - Route `/admin/automation`
- `AdminSidebar.tsx` - Navigation link

---

## SocialMedia.tsx

### File Location
`frontend/src/components/admin/SocialMedia.tsx`

### Component Dependencies
```typescript
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
```

### Service Dependencies
```typescript
import { autoproApi } from '@/services/autoproApi'
```

### API Methods Used
- `autoproApi.getSocialAccounts()`
- `autoproApi.getSocialFollowers()`
- `autoproApi.postToSocial(postData)`
- `autoproApi.connectSocialAccount(platform)` ⚠️ OAuth not complete

### Props Interface
```typescript
interface SocialMediaProps {
  user: User;
}
```

### State Management
```typescript
const [accounts, setAccounts] = useState<SocialAccount[]>([])
const [followers, setFollowers] = useState<FollowerStats | null>(null)
const [selectedPlatform, setSelectedPlatform] = useState<string>('')
const [postContent, setPostContent] = useState('')
const [posting, setPosting] = useState(false)
```

### Used By
- `AdminApp.tsx` - Route `/admin/social`
- `AdminSidebar.tsx` - Navigation link

---

## AIInsightsDashboard.tsx

### File Location
`frontend/src/components/admin/AIInsightsDashboard.tsx`

### Component Dependencies
```typescript
import { Card } from '@/components/ui/card'
import { Chart } from '@/components/ui/chart'
import { List } from '@/components/ui/list'
import { Badge } from '@/components/ui/badge'
import { Alert } from '@/components/ui/alert'
```

### Service Dependencies
```typescript
import { autoproApi } from '@/services/autoproApi'
```

### API Methods Used
- `autoproApi.getAiInsights()`
- `autoproApi.getTopPerformers()`
- `autoproApi.getTrendingTopics()`

### Environment Variables
```typescript
const FAKE_MODE = import.meta.env.VITE_FAKE_MODE === 'true'
```

### Props Interface
```typescript
interface AIInsightsDashboardProps {
  user: User;
}
```

### State Management
```typescript
const [insights, setInsights] = useState<AIInsights | null>(null)
const [loading, setLoading] = useState(true)
const [error, setError] = useState<string | null>(null)
```

### Used By
- `AdminApp.tsx` - Route `/admin/ai-insights`
- `AdminSidebar.tsx` - Navigation link

---

## GrowthDashboard.tsx

### File Location
`frontend/src/components/admin/GrowthDashboard.tsx`

### Component Dependencies
```typescript
import { Card } from '@/components/ui/card'
import { Chart } from '@/components/ui/chart'
import { Table } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
```

### Service Dependencies
```typescript
import { autoproApi } from '@/services/autoproApi'
```

### API Methods Used
- `autoproApi.getAnalyticsMetrics()` ⚠️ Not implemented
- `autoproApi.getChartData()` ⚠️ Not implemented

### Current Status
⚠️ **Using mock data** - No real API integration

### Props Interface
```typescript
interface GrowthDashboardProps {
  user: User;
}
```

### State Management
```typescript
const [metrics, setMetrics] = useState<GrowthMetrics | null>(null)
const [chartData, setChartData] = useState<ChartDataPoint[]>([])
const [loading, setLoading] = useState(true)
```

### Used By
- `AdminApp.tsx` - Route `/admin/growth`
- `AdminSidebar.tsx` - Navigation link

---

## AdminSidebar.tsx

### File Location
`frontend/src/components/admin/AdminSidebar.tsx`

### Component Dependencies
```typescript
import { NavLink } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
```

### Icons Used
```typescript
import {
  Video,
  DollarSign,
  Zap,
  Share2,
  Brain,
  TrendingUp,
  Users,
  Settings
} from 'lucide-react'
```

### Props Interface
```typescript
interface AdminSidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}
```

### Navigation Structure
```typescript
const navItems = [
  { path: '/admin/videos', label: 'Videos', icon: Video },
  { path: '/admin/financial', label: 'Financial', icon: DollarSign },
  { path: '/admin/automation', label: 'Automation', icon: Zap },
  { path: '/admin/social', label: 'Social Media', icon: Share2 },
  { path: '/admin/ai-insights', label: 'AI Insights', icon: Brain },
  { path: '/admin/growth', label: 'Growth', icon: TrendingUp },
  { path: '/admin/users', label: 'Users', icon: Users },
  { path: '/admin/settings', label: 'Settings', icon: Settings }
]
```

---

## AdminApp.tsx

### File Location
`frontend/src/components/admin/AdminApp.tsx`

### Component Dependencies
```typescript
import { Routes, Route } from 'react-router-dom'
import AdminSidebar from './AdminSidebar'
import VideoManagement from './VideoManagement'
import FinancialDashboard from './FinancialDashboard'
import AutomationControl from './AutomationControl'
import SocialMedia from './SocialMedia'
import AIInsightsDashboard from './AIInsightsDashboard'
import GrowthDashboard from './GrowthDashboard'
```

### Service Dependencies
```typescript
import { autoproApi } from '@/services/autoproApi'
import { useAuth } from '@/hooks/useAuth'
```

### State Management
```typescript
const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
const { user, permissions } = useAuth()
```

### Route Structure
```typescript
<Routes>
  <Route path="/videos" element={<VideoManagement />} />
  <Route path="/financial" element={<FinancialDashboard />} />
  <Route path="/automation" element={<AutomationControl />} />
  <Route path="/social" element={<SocialMedia />} />
  <Route path="/ai-insights" element={<AIInsightsDashboard />} />
  <Route path="/growth" element={<GrowthDashboard />} />
  <Route path="/users" element={<UserManagement />} /> {/* Not implemented */}
  <Route path="/settings" element={<Settings />} /> {/* Not implemented */}
</Routes>
```

---

## Shared Services

### autoproApi Service

**Location:** `frontend/src/services/autoproApi.ts`

**Methods:**
```typescript
// Video
getAdvancedVideoJobs()
generateAdvancedVideo(data)
getVideoThumbnail(videoId)
deleteVideoJob(jobId)
regenerateVideo(jobId)

// Financial
getFinancialDashboard()
getCosts()
getCreditBalance(provider)
trackCost(costData)

// Automation
getAutomationStatus()
startAutomation(automationId)
stopAutomation(automationId)
getAutomationLogs() // Not implemented

// Social
getSocialAccounts()
getSocialFollowers()
postToSocial(postData)

// AI
getAiInsights()
getTopPerformers()
getTrendingTopics()

// Analytics
getAnalyticsMetrics() // Not implemented
getChartData() // Not implemented
```

---

## UI Components Library

### Component Locations
All UI components are in `frontend/src/components/ui/`

**Available Components:**
- `Button` - `button.tsx`
- `Card`, `CardHeader`, `CardTitle`, `CardContent` - `card.tsx`
- `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableCell` - `table.tsx`
- `Modal`, `ModalHeader`, `ModalBody`, `ModalFooter` - `modal.tsx`
- `Badge` - `badge.tsx`
- `Switch` - `switch.tsx`
- `Input` - `input.tsx`
- `Textarea` - `textarea.tsx`
- `LoadingIndicator` - `loading.tsx`
- `Skeleton` - `skeleton.tsx`
- `Alert` - `alert.tsx`
- `Chart` - `chart.tsx`

---

## External Package Dependencies

### package.json (Frontend)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "recharts": "^2.10.3",
    "date-fns": "^2.30.0",
    "lucide-react": "^0.294.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.1.0"
  }
}
```

---

## Environment Variables Required

### Frontend (.env)
```env
VITE_API_BASE=http://localhost:8001
VITE_FAKE_MODE=true
```

### Backend (.env)
```env
FAKE_MODE=true
SUPABASE_URL=...
SUPABASE_KEY=...
```

---

## Missing Dependencies

### Components Not Implemented
1. **UserManagement.tsx** - User management component
2. **Settings.tsx** - Settings component
3. **Notifications.tsx** - Notifications component

### API Methods Not Implemented
1. `autoproApi.getAutomationLogs()`
2. `autoproApi.getAnalyticsMetrics()`
3. `autoproApi.getChartData()`
4. `autoproApi.getUserList()`
5. `autoproApi.getSettings()`

### Backend Routes Missing
1. `GET /api/automation/logs`
2. `GET /api/analytics/metrics`
3. `GET /api/analytics/chart-data`
4. `GET /api/users`
5. `GET /api/settings`
6. `DELETE /api/advanced-video/jobs/{id}`
7. `GET /api/financial/credit-balance/{provider}`

---

## Dependency Installation Order

### 1. Install UI Components (if missing)
```bash
cd frontend
npm install lucide-react class-variance-authority clsx tailwind-merge
```

### 2. Install Chart Library
```bash
npm install recharts
```

### 3. Install Date Utilities
```bash
npm install date-fns
```

### 4. Install Axios
```bash
npm install axios
```

---

## Import Path Aliases

### tsconfig.json / vite.config.ts
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/services/*": ["./src/services/*"],
      "@/hooks/*": ["./src/hooks/*"]
    }
  }
}
```
