import axios from "axios";
import type * as API from "../types/api";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: Number(import.meta.env.VITE_API_TIMEOUT ?? 10000),
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("authToken");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem("authToken");
      localStorage.removeItem("adminAuth");
      window.location.href = "/admin";
    }
    return Promise.reject(error);
  }
);

export async function healthCheck(): Promise<{ status: string }> {
  const r = await api.get("/health");
  return r.data;
}

export async function ping(): Promise<{ status: string; timestamp: string }> {
  const r = await api.get("/ping");
  return r.data;
}

class AutoProApiService {
  healthCheck = healthCheck;
  ping = ping;
  
  // Leads
  getLeads = async (): Promise<API.ApiResponse<API.Lead[]>> => 
    (await api.get("/api/leads/")).data;
  createLead = async (lead: Partial<API.Lead>): Promise<API.ApiResponse<API.Lead>> => 
    (await api.post("/api/leads", lead)).data;
  
  // Financial
  getFinancialDashboard = async (params?: API.DashboardParams): Promise<API.ApiResponse<API.FinancialDashboard>> =>
    (await api.get("/api/financial/dashboard", { params })).data;
  getInvoices = async (): Promise<API.ApiResponse<{ invoices: API.Invoice[] }>> => 
    (await api.get("/api/financial/invoices")).data;
  createInvoice = async (invoice: Partial<API.Invoice>): Promise<API.ApiResponse<API.Invoice>> =>
    (await api.post("/api/financial/invoices", invoice)).data;
  getPayments = async (): Promise<API.ApiResponse<{ payments: API.Payment[] }>> => 
    (await api.get("/api/financial/payments")).data;
  createPayment = async (payment: Partial<API.Payment>): Promise<API.ApiResponse<API.Payment>> =>
    (await api.post("/api/financial/payments", payment)).data;
  getPaymentOverview = async (period?: string): Promise<API.ApiResponse<API.PaymentOverview>> =>
    (await api.get("/api/financial/payments/overview", { params: { period } })).data;
  updatePayment = async (id: string, updates: Partial<API.Payment>): Promise<API.ApiResponse<API.Payment>> =>
    (await api.put(`/api/financial/payments/${id}`, updates)).data;
  deletePayment = async (id: string): Promise<API.ApiResponse<void>> =>
    (await api.delete(`/api/financial/payments/${id}`)).data;
  getCreditBalance = async (provider: string): Promise<API.ApiResponse<API.CreditBalance>> =>
    (await api.get(`/api/financial/credit-balance/${provider}`)).data;
  
  // Notifications
  getNotifications = async (params?: API.NotificationParams): Promise<API.ApiResponse<API.Notification[]>> =>
    (await api.get("/api/notify/list", { params })).data;
  markNotificationRead = async (id: string): Promise<API.ApiResponse<void>> =>
    (await api.post(`/api/notify/mark-read/${id}`)).data;
  
  // AI Insights
  getAIInsights = async (filters?: Record<string, string | number>): Promise<API.ApiResponse<API.AIInsight[]>> =>
    (await api.get("/api/ai/insights", { params: filters })).data;
  generateAIReport = async (ids: string[]): Promise<API.ApiResponse<unknown>> =>
    (await api.post("/api/ai/generate-report", { insightIds: ids })).data;
  
  // Tax
  getTaxRates = async (): Promise<API.ApiResponse<API.TaxRate[]>> => 
    (await api.get("/api/financial/tax-rates")).data;
  calculateTax = async (req: Record<string, number | string>): Promise<API.ApiResponse<API.TaxCalculation>> =>
    (await api.post("/api/financial/calculate-tax", req)).data;
  
  // Automation
  getAutomationStatus = async (): Promise<API.ApiResponse<API.AutomationStatus>> => 
    (await api.get("/api/automation/status")).data;
  getAutomationLogs = async (params?: { limit?: number; task_type?: string }): Promise<API.ApiResponse<API.AutomationLog[]>> => 
    (await api.get("/api/automation/logs", { params })).data;
  updateAutomationSettings = async (settings: API.AutomationSettings): Promise<API.ApiResponse<unknown>> =>
    (await api.post("/api/automation/settings", settings)).data;
  toggleAutomation = async (enabled: boolean): Promise<API.ApiResponse<unknown>> =>
    (await api.post("/api/automation/toggle", { enabled })).data;
  startAutomation = async (): Promise<API.ApiResponse<unknown>> => 
    (await api.post("/api/automation/start")).data;
  stopAutomation = async (): Promise<API.ApiResponse<unknown>> => 
    (await api.post("/api/automation/stop")).data;
  triggerAutomation = async (): Promise<API.ApiResponse<unknown>> => 
    (await api.post("/api/automation/trigger")).data;
  
  // Videos
  getVideos = async (): Promise<API.ApiResponse<API.VideoStats>> => 
    (await api.get("/api/video/stats")).data;
  getVideoJobs = async (params?: { page?: number; limit?: number; status?: string }): Promise<API.PaginatedResponse<API.VideoJob>> =>
    (await api.get("/api/advanced-video/jobs", { params })).data;
  deleteVideo = async (filename: string): Promise<API.ApiResponse<void>> =>
    (await api.delete(`/api/advanced-video/delete/${filename}`)).data;
  
  // Social Media
  getSocialPosts = async (): Promise<API.ApiResponse<API.SocialPost[]>> => 
    (await api.get("/api/social/posts")).data;
  getPostAnalytics = async (): Promise<API.ApiResponse<API.PostAnalytics>> => 
    (await api.get("/api/social/analytics")).data;
  createPost = async (post: Partial<API.SocialPost>): Promise<API.ApiResponse<API.SocialPost>> => 
    (await api.post("/api/social/posts", post)).data;
  schedulePost = async (post: Partial<API.SocialPost>): Promise<API.ApiResponse<API.SocialPost>> => 
    (await api.post("/api/social/post-now", post)).data;
  
  // Health & Overview
  checkApiHealth = async (): Promise<{ status: string }> => 
    (await api.get("/health")).data;
  getOverviewStats = async (): Promise<API.ApiResponse<Record<string, unknown>>> => 
    (await api.get("/api/dashboard/overview")).data;
  getRevenueData = async (): Promise<API.ApiResponse<unknown>> => 
    (await api.get("/api/financial/revenue")).data;
  getCostData = async (): Promise<API.ApiResponse<unknown>> => 
    (await api.get("/api/financial/costs")).data;
}

const svc = new AutoProApiService();
export default svc;                // default
export { api };                    // low-level axios (dacă ai nevoie)
export type { AutoProApiService }; // tipuri opționale
