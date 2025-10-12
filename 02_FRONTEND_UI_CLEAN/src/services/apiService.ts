/**
 * Centralized API Service for AutoPro Daune
 * Handles all backend API calls with proper error handling and type safety
 */

import { api } from '@/lib/api';
import type {
  FinancialBreakdown,
  SocialFollowers,
  VideoPerformance,
  AutomationStatus,
  AutomationAction,
  CaptionGenerateRequest,
  CaptionResponse,
  BusinessInsight,
  AIInsightsResponse,
  PredictiveAnalytics,
  CostEntry,
  CostCategory,
  ApiResponse,
  SocialPost,
  Lead,
} from '@/types/api';

// ==================== FINANCIAL ENDPOINTS ====================

export async function getFinancialBreakdown(period: string = '30d'): Promise<FinancialBreakdown> {
  const response = await api.get<ApiResponse<FinancialBreakdown>>(`/api/financial/breakdown?period=${period}`);
  return response.data.data || {
    total_revenue: 0,
    total_costs: 0,
    net_profit: 0,
    roi_percentage: 0,
    start_date: '',
    end_date: '',
    timeline: [],
    costs: { top: [], by_provider: {}, by_category: {}, total: 0 }
  };
}

export async function getCostCategories(): Promise<CostCategory[]> {
  const response = await api.get<ApiResponse<CostCategory[]>>('/api/financial/cost-categories');
  return response.data.data || [];
}

export async function assignCostCategory(costId: string, categoryId: string): Promise<void> {
  await api.post(`/api/financial/costs/${costId}/assign-category`, { category_id: categoryId });
}

export async function getFinancialDashboard() {
  const response = await api.get('/api/financial/dashboard');
  return response.data;
}

export async function getFinancialForecast(months: number = 3) {
  const response = await api.get(`/api/financial/forecast?months=${months}`);
  return response.data;
}

export async function exportFinancialData(format: 'csv' | 'excel' = 'csv', period: string = '30d') {
  const response = await api.get(`/api/financial/export?format=${format}&period=${period}`, {
    responseType: 'blob'
  });
  return response.data;
}

// ==================== SOCIAL MEDIA ENDPOINTS ====================

export async function getSocialFollowers(): Promise<SocialFollowers> {
  const response = await api.get<ApiResponse<SocialFollowers>>('/api/social/followers');
  return response.data.data || { total: 0, by_platform: {} };
}

export async function getSocialSummary() {
  const response = await api.get('/api/social/summary');
  return response.data;
}

export async function getSocialPosts(platform?: string, limit: number = 20): Promise<SocialPost[]> {
  const params = new URLSearchParams();
  if (platform) params.append('platform', platform);
  params.append('limit', limit.toString());
  
  const response = await api.get<ApiResponse<SocialPost[]>>(`/api/social/posts?${params.toString()}`);
  return response.data.data || [];
}

export async function generateCaption(request: CaptionGenerateRequest): Promise<CaptionResponse> {
  const response = await api.post<ApiResponse<CaptionResponse>>('/api/social/caption', {
    topic: request.topic,
    tone: request.tone,
    platform: request.platform,
    include_hashtags: request.include_hashtags,
    max_length: request.max_length
  });
  
  return response.data.data || {
    caption: '',
    hashtags: [],
    engagement_prediction: { estimated: 0, factors: [] }
  };
}

export async function postToSocial(platform: string, content: string, videoId?: string) {
  const response = await api.post('/api/social/post-now', {
    platform,
    content,
    video_id: videoId
  });
  return response.data;
}

// ==================== VIDEO ENDPOINTS ====================

export async function getVideoAnalytics(): Promise<VideoPerformance> {
  const response = await api.get<ApiResponse<VideoPerformance>>('/api/video/analytics/performance');
  return response.data.data || {
    total_videos: 0,
    total_views: 0,
    avg_completion_rate: 0,
    top_performing: []
  };
}

export async function getVideoStats() {
  const response = await api.get('/api/video/stats');
  return response.data;
}

export async function getVideoQueue() {
  const response = await api.get('/api/video/queue');
  return response.data;
}

export async function generateVideo(data: any) {
  const response = await api.post('/api/video/generate', data);
  return response.data;
}

// ==================== LEAD ENDPOINTS ====================

export async function getLeads(): Promise<Lead[]> {
  const response = await api.get<ApiResponse<Lead[]>>('/api/leads/');
  return response.data.data || response.data || [];
}

export async function createLead(leadData: Partial<Lead>): Promise<Lead> {
  const response = await api.post<ApiResponse<Lead>>('/api/leads/', leadData);
  return response.data.data || response.data;
}

export async function updateLead(leadId: string, updates: Partial<Lead>): Promise<Lead> {
  const response = await api.put<ApiResponse<Lead>>(`/api/leads/${leadId}`, updates);
  return response.data.data || response.data;
}

export async function getLeadTimeline(period: string = '30d') {
  const response = await api.get(`/api/leads/timeline?period=${period}`);
  return response.data;
}

// ==================== AUTOMATION ENDPOINTS ====================

export async function getAutomationStatus(): Promise<AutomationStatus> {
  const response = await api.get<ApiResponse<AutomationStatus>>('/api/working-automation/status');
  return response.data.data || {
    automation_active: false,
    daily_target: 3,
    posts_today: 0,
    next_scheduled_post: '',
    schedule: []
  };
}

export async function toggleAutomation(active: boolean): Promise<void> {
  await api.post('/api/working-automation/toggle', { active });
}

export async function updateAutomationSchedule(schedule: string[], dailyTarget?: number): Promise<void> {
  await api.post('/api/working-automation/update-schedule', {
    schedule,
    daily_target: dailyTarget
  });
}

export async function getRecentAutomationActions(limit: number = 10): Promise<AutomationAction[]> {
  const response = await api.get<ApiResponse<AutomationAction[]>>(
    `/api/working-automation/recent-actions?limit=${limit}`
  );
  return response.data.data || [];
}

// ==================== AI INSIGHTS ENDPOINTS ====================

export async function getBusinessInsights(filters?: Record<string, unknown>): Promise<AIInsightsResponse> {
  const response = await api.get<ApiResponse<AIInsightsResponse>>(
    '/api/advanced-business-intelligence/business-insights',
    { params: filters }
  );
  return response.data.data || {
    insights: [],
    metrics: {
      total_insights: 0,
      high_confidence_insights: 0,
      critical_alerts: 0,
      categories: {}
    },
    context: {
      window: { start: '', end: '' },
      source_counts: {}
    }
  };
}

export async function getPredictiveAnalytics(): Promise<PredictiveAnalytics> {
  const response = await api.get<ApiResponse<PredictiveAnalytics>>(
    '/api/advanced-business-intelligence/predictive-analytics'
  );
  return response.data.data || {
    forecasts: [],
    trends: [],
    recommendations: []
  };
}

export async function getComprehensiveAnalytics() {
  const response = await api.get('/api/advanced-business-intelligence/comprehensive-analytics');
  return response.data;
}

// ==================== HEALTH & MONITORING ====================

export async function getHealthCheck() {
  const response = await api.get('/health');
  return response.data;
}

export async function getMetrics() {
  const response = await api.get('/metrics');
  return response.data;
}

// ==================== ERROR HANDLING UTILITY ====================

export function handleApiError(error: any): string {
  if (error?.response?.data?.error) {
    return error.response.data.error;
  }
  if (error?.response?.data?.message) {
    return error.response.data.message;
  }
  if (error?.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
}
