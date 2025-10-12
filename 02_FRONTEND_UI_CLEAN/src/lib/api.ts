// bridge: BEGIN axios client
import axios from "axios";

const baseURL = import.meta.env.DEV ? "/api" : (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || "http://localhost:8001");

export const api = axios.create({
  baseURL,
  timeout: Number(import.meta.env.VITE_API_TIMEOUT || 20000),
  headers: { "Content-Type": "application/json" },
});

// Optional: inject Supabase/JWT if you have it in localStorage
api.interceptors.request.use((cfg) => {
  const token = localStorage.getItem("supabase_access_token"); // adapt if needed
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  console.log(`🚀 API Request: ${cfg.method?.toUpperCase()} ${cfg.url}`);
  return cfg;
});

// Basic error normalization
api.interceptors.response.use(
  (r) => {
    console.log(`✅ API Response: ${r.status} ${r.config.url}`);
    return r;
  },
  async (err) => {
    const status = err?.response?.status;
    // naive retry once for 502/503/504
    if ([502, 503, 504].includes(status) && !err.config.__retried) {
      err.config.__retried = true;
      await new Promise((res) => setTimeout(res, 600));
      return api.request(err.config);
    }
    console.error('❌ API Response Error:', err);
    return Promise.reject({
      status,
      message: err?.response?.data?.error || err?.message || "request_failed",
    });
  }
);

export const ping = async () => (await api.get("/health")).data;
// bridge: END axios client

// Get metrics
export async function getMetrics() {
  try {
    const response = await api.get("/metrics");
    return response.data;
  } catch (error) {
    console.error('Metrics fetch failed:', error);
    throw error;
  }
}

// Get leads
export async function getLeads() {
  try {
    const response = await api.get("/api/leads/");
    return response.data;
  } catch (error) {
    console.error('Get leads failed:', error);
    throw error;
  }
}

// Create lead
export async function createLead(leadData: {
  name: string;
  phone: string;
  email?: string;
  location?: string;
  damageType?: string;
  details: string;
}) {
  try {
    const response = await api.post("/api/leads/", leadData);
    return response.data;
  } catch (error) {
    console.error('Create lead failed:', error);
    throw error;
  }
}

// Update lead status
export async function updateLeadStatus(leadId: string, status: string) {
  try {
    const response = await api.put(`/api/leads/${leadId}`, { status });
    return response.data;
  } catch (error) {
    console.error('Update lead status failed:', error);
    throw error;
  }
}

// Get financial dashboard
export async function getFinancialDashboard() {
  try {
    const response = await api.get("/api/financial/dashboard");
    return response.data;
  } catch (error) {
    console.error('Get financial dashboard failed:', error);
    throw error;
  }
}

// Get social media summary
export async function getSocialSummary() {
  try {
    const response = await api.get("/api/social/summary");
    return response.data;
  } catch (error) {
    console.error('Get social summary failed:', error);
    throw error;
  }
}

// Get video stats
export async function getVideoStats() {
  try {
    const response = await api.get("/api/video/stats");
    return response.data;
  } catch (error) {
    console.error('Get video stats failed:', error);
    throw error;
  }
}

// Get financial breakdown
export async function getFinancialBreakdown(period: string = '30d') {
  try {
    const response = await api.get(`/api/financial/breakdown?period=${period}`);
    return response.data;
  } catch (error) {
    console.error('Get financial breakdown failed:', error);
    throw error;
  }
}

// Get financial cost categories
export async function getFinancialCostCategories() {
  try {
    const response = await api.get('/api/financial/cost-categories');
    return response.data;
  } catch (error) {
    console.error('Get cost categories failed:', error);
    throw error;
  }
}

// Get social followers
export async function getSocialFollowers() {
  try {
    const response = await api.get('/api/social/followers');
    return response.data;
  } catch (error) {
    console.error('Get social followers failed:', error);
    throw error;
  }
}

// Get video analytics performance
export async function getVideoAnalyticsPerformance() {
  try {
    const response = await api.get('/api/video/analytics/performance');
    return response.data;
  } catch (error) {
    console.error('Get video analytics performance failed:', error);
    throw error;
  }
}

// Get automation status
export async function getAutomationStatus() {
  try {
    const response = await api.get('/api/working-automation/status');
    return response.data;
  } catch (error) {
    console.error('Get automation status failed:', error);
    throw error;
  }
}

// Toggle automation
export async function toggleAutomation(enabled: boolean) {
  try {
    const response = await api.post('/api/working-automation/toggle', { enabled });
    return response.data;
  } catch (error) {
    console.error('Toggle automation failed:', error);
    throw error;
  }
}

// Update automation schedule
export async function updateAutomationSchedule(schedule: Record<string, unknown>) {
  try {
    const response = await api.post('/api/working-automation/update-schedule', schedule);
    return response.data;
  } catch (error) {
    console.error('Update automation schedule failed:', error);
    throw error;
  }
}

// Get automation recent actions
export async function getAutomationRecentActions() {
  try {
    const response = await api.get('/api/working-automation/recent-actions');
    return response.data;
  } catch (error) {
    console.error('Get automation recent actions failed:', error);
    throw error;
  }
}

// Generate AI caption
export async function generateCaption(options: {
  topic: string;
  tone: string;
  platform: string;
  include_hashtags: boolean;
  max_length: number;
}) {
  try {
    const response = await api.post('/api/social/caption', options);
    return response.data;
  } catch (error) {
    console.error('Generate caption failed:', error);
    throw error;
  }
}

// Get business insights
export async function getBusinessInsights() {
  try {
    const response = await api.get('/api/advanced-business-intelligence/business-insights');
    return response.data;
  } catch (error) {
    console.error('Get business insights failed:', error);
    throw error;
  }
}

// Get predictive analytics
export async function getPredictiveAnalytics() {
  try {
    const response = await api.get('/api/advanced-business-intelligence/predictive-analytics');
    return response.data;
  } catch (error) {
    console.error('Get predictive analytics failed:', error);
    throw error;
  }
}

// Get comprehensive analytics
export async function getComprehensiveAnalytics() {
  try {
    const response = await api.get('/api/advanced-business-intelligence/comprehensive-analytics');
    return response.data;
  } catch (error) {
    console.error('Get comprehensive analytics failed:', error);
    throw error;
  }
}

export default api;
