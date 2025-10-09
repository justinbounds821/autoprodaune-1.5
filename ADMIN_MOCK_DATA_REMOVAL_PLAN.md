# Admin Mock Data Removal Plan

## Overview
This document outlines the strategy for removing hardcoded mock data from admin components and replacing them with real API calls.

---

## 1. VideoManagement.tsx

### Current Mock Data
```typescript
const mockJobs = [
  {
    id: "job_1",
    status: "completed",
    script: "Test video",
    created_at: "2024-01-01"
  },
  // ... more mock jobs
];
```

### Replacement Strategy
```typescript
// Remove mock array
// Add API call in useEffect
useEffect(() => {
  const fetchJobs = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/advanced-video/jobs');
      setJobs(response.data.jobs || []);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };
  
  fetchJobs();
}, []);
```

**Files to modify:**
- `frontend/src/components/admin/VideoManagement.tsx`

**Lines to remove:** Mock job array declarations

**Estimate:** 30 minutes

---

## 2. FinancialDashboard.tsx

### Current Mock Data
```typescript
const mockFinancialData = {
  totalCosts: 1250.00,
  totalRevenue: 4500.00,
  roi: 2.6,
  videosGenerated: 45
};
```

### Replacement Strategy
```typescript
// Remove hardcoded values
// Use API call
useEffect(() => {
  const fetchFinancialData = async () => {
    setLoading(true);
    try {
      const data = await autoproApi.getFinancialDashboard();
      setFinancialData(data);
    } catch (error) {
      console.error('Failed to fetch financial data:', error);
      // Use empty state instead of mock
      setFinancialData(null);
    } finally {
      setLoading(false);
    }
  };
  
  fetchFinancialData();
}, []);
```

**Files to modify:**
- `frontend/src/components/admin/FinancialDashboard.tsx`

**Lines to remove:** Mock financial data objects

**Estimate:** 1 hour

---

## 3. AutomationControl.tsx

### Current Mock Data
```typescript
const demoLogs = [
  { id: 1, action: "video_gen", status: "success", timestamp: "2024-01-01" },
  { id: 2, action: "social_post", status: "failed", timestamp: "2024-01-02" },
  // ... more demo logs
];
```

### Replacement Strategy
```typescript
// Remove demo logs array
// Add API integration
const [logs, setLogs] = useState<AutomationLog[]>([]);

useEffect(() => {
  const fetchLogs = async () => {
    setLoadingLogs(true);
    try {
      const response = await autoproApi.getAutomationLogs();
      setLogs(response.data || []);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
      setLogs([]);
    } finally {
      setLoadingLogs(false);
    }
  };
  
  fetchLogs();
}, []);
```

**Files to modify:**
- `frontend/src/components/admin/AutomationControl.tsx`

**Backend required:**
- Implement `GET /api/automation/logs` endpoint

**Estimate:** 2 hours

---

## 4. GrowthDashboard.tsx

### Current Mock Data
```typescript
const mockMetrics = {
  visitors: 321,
  signups: 5,
  conversions: 12,
  revenue: 450.00
};

const mockChartData = [
  { date: "2024-01-01", value: 100 },
  { date: "2024-01-02", value: 150 },
  // ... more data points
];
```

### Replacement Strategy
```typescript
// Remove all mock data
// Implement real analytics
const [metrics, setMetrics] = useState<GrowthMetrics | null>(null);
const [chartData, setChartData] = useState<ChartDataPoint[]>([]);

useEffect(() => {
  const fetchGrowthData = async () => {
    setLoading(true);
    try {
      const [metricsRes, chartRes] = await Promise.all([
        axios.get('/api/analytics/metrics'),
        axios.get('/api/analytics/chart-data')
      ]);
      
      setMetrics(metricsRes.data);
      setChartData(chartRes.data);
    } catch (error) {
      console.error('Failed to fetch growth data:', error);
      setMetrics(null);
      setChartData([]);
    } finally {
      setLoading(false);
    }
  };
  
  fetchGrowthData();
}, []);
```

**Files to modify:**
- `frontend/src/components/admin/GrowthDashboard.tsx`

**Backend required:**
- Implement `GET /api/analytics/metrics`
- Implement `GET /api/analytics/chart-data`

**Estimate:** 3 hours

---

## 5. AIInsightsDashboard.tsx

### Current Mock Data
```typescript
const placeholderInsights = {
  topPerformers: ["Video 1", "Video 2"],
  recommendations: ["Use more emojis", "Post at 9 AM"],
  sentimentScore: 0.85
};
```

### Replacement Strategy
```typescript
// Remove placeholder data
// Use real AI insights
const [insights, setInsights] = useState<AIInsights | null>(null);

useEffect(() => {
  const fetchInsights = async () => {
    setLoading(true);
    try {
      const data = await autoproApi.getAiInsights();
      setInsights(data);
    } catch (error) {
      console.error('Failed to fetch AI insights:', error);
      // Show error state instead of placeholder
      setInsights(null);
      setError('AI insights are currently unavailable');
    } finally {
      setLoading(false);
    }
  };
  
  fetchInsights();
}, []);

// Add error state UI
{error && (
  <div className="alert alert-warning">
    <AlertTriangle className="h-4 w-4" />
    <span>{error}</span>
  </div>
)}
```

**Files to modify:**
- `frontend/src/components/admin/AIInsightsDashboard.tsx`

**Backend required:**
- Ensure `/api/ai/insights` works in FAKE_MODE

**Estimate:** 2 hours

---

## 6. SocialMedia.tsx

### Current Mock Data
```typescript
const mockAccounts = [
  { platform: "tiktok", username: "@demo", connected: false },
  { platform: "instagram", username: "@demo", connected: false }
];

const mockStats = {
  followers: 1234,
  posts: 45,
  engagement: 0.056
};
```

### Replacement Strategy
```typescript
// Remove mock data
// Use real social media APIs
const [accounts, setAccounts] = useState<SocialAccount[]>([]);
const [stats, setStats] = useState<SocialStats | null>(null);

useEffect(() => {
  const fetchSocialData = async () => {
    setLoading(true);
    try {
      const [accountsRes, statsRes] = await Promise.all([
        axios.get('/api/social/accounts'),
        axios.get('/api/social/stats')
      ]);
      
      setAccounts(accountsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Failed to fetch social data:', error);
      setAccounts([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };
  
  fetchSocialData();
}, []);
```

**Files to modify:**
- `frontend/src/components/admin/SocialMedia.tsx`

**Backend required:**
- Implement `GET /api/social/accounts`
- Implement `GET /api/social/stats`

**Estimate:** 2 hours

---

## Implementation Checklist

### Phase 1: Backend Preparation (Day 1)
- [ ] Implement missing endpoints:
  - [ ] `GET /api/automation/logs`
  - [ ] `GET /api/analytics/metrics`
  - [ ] `GET /api/analytics/chart-data`
  - [ ] `GET /api/social/accounts`
  - [ ] `GET /api/social/stats`

### Phase 2: Frontend Updates (Day 2)
- [ ] Update VideoManagement.tsx
- [ ] Update FinancialDashboard.tsx
- [ ] Update AutomationControl.tsx

### Phase 3: Advanced Components (Day 3)
- [ ] Update GrowthDashboard.tsx
- [ ] Update AIInsightsDashboard.tsx
- [ ] Update SocialMedia.tsx

### Phase 4: Testing (Day 4)
- [ ] Test all components with real APIs
- [ ] Test error states
- [ ] Test loading states
- [ ] Test empty states

### Phase 5: Cleanup (Day 4)
- [ ] Remove all commented mock data
- [ ] Update PropTypes/TypeScript types
- [ ] Update documentation

---

## Testing Strategy

### For Each Component:

1. **With Real Data**
```bash
# Start backend with real DB
FAKE_MODE=false npm run backend
# Test component functionality
```

2. **With FAKE_MODE**
```bash
# Start backend in FAKE_MODE
FAKE_MODE=true npm run backend
# Verify fallback data works
```

3. **Error Scenarios**
```bash
# Stop backend
# Verify error states display correctly
```

4. **Loading States**
```bash
# Add network delay
# Verify loading indicators work
```

---

## Rollback Plan

If issues arise during removal:

1. **Keep mock data commented** (don't delete immediately)
2. **Add feature flag** for mock vs real data
3. **Monitor error rates** in production
4. **Gradual rollout** - one component at a time

```typescript
// Feature flag example
const USE_REAL_DATA = import.meta.env.VITE_USE_REAL_DATA === 'true';

const fetchData = async () => {
  if (USE_REAL_DATA) {
    return await api.getRealData();
  } else {
    return MOCK_DATA;
  }
};
```

---

## Success Criteria

- [ ] All components fetch data from real APIs
- [ ] No hardcoded mock data in production code
- [ ] Error states handled gracefully
- [ ] Loading states implemented
- [ ] Empty states implemented
- [ ] FAKE_MODE still works for development
- [ ] All tests pass
- [ ] No console errors

---

## Total Estimate

| Component | Time |
|-----------|------|
| VideoManagement | 0.5h |
| FinancialDashboard | 1h |
| AutomationControl | 2h |
| GrowthDashboard | 3h |
| AIInsightsDashboard | 2h |
| SocialMedia | 2h |
| Testing & Cleanup | 4h |
| **TOTAL** | **14.5h** |
