import axios from "axios";

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
  getLeads = async () => (await api.get("/api/leads/")).data;
  createLead = async (lead: any) => (await api.post("/api/leads", lead)).data;
  getFinancialDashboard = async (params?: any) =>
    (await api.get("/api/financial/dashboard", { params })).data;
  getInvoices = async () => (await api.get("/api/financial/invoices")).data;
  createInvoice = async (invoice: any) =>
    (await api.post("/api/financial/invoices", invoice)).data;
  getPayments = async () => (await api.get("/api/financial/payments")).data;
  createPayment = async (payment: any) =>
    (await api.post("/api/financial/payments", payment)).data;
  getNotifications = async (params?: any) =>
    (await api.get("/api/notify/list", { params })).data;
  markNotificationRead = async (id: string) =>
    (await api.post(`/api/notify/mark-read/${id}`)).data;
  getAIInsights = async (filters?: any) =>
    (await api.get("/api/ai/insights", { params: filters })).data;
  generateAIReport = async (ids: string[]) =>
    (await api.post("/api/ai/generate-report", { insightIds: ids })).data;
  getTaxRates = async () => (await api.get("/api/financial/tax-rates")).data;
  calculateTax = async (req: any) =>
    (await api.post("/api/financial/calculate-tax", req)).data;
  // Automation methods
  getAutomationStatus = async () => (await api.get("/api/automation/status")).data;
  getAutomationLogs = async () => (await api.get("/api/automation/logs")).data;
  updateAutomationSettings = async (settings: any) =>
    (await api.post("/api/automation/settings", settings)).data;
  toggleAutomation = async (enabled: boolean) =>
    (await api.post("/api/automation/toggle", { enabled })).data;
  // Additional missing methods
  getVideos = async () => (await api.get("/api/video/stats")).data;
  getPaymentOverview = async (period?: string) =>
    (await api.get("/api/financial/payments/overview", { params: { period } })).data;
  updatePayment = async (id: string, updates: any) =>
    (await api.put(`/api/financial/payments/${id}`, updates)).data;
  deletePayment = async (id: string) =>
    (await api.delete(`/api/financial/payments/${id}`)).data;
  getOverviewStats = async () => (await api.get("/api/dashboard/overview")).data;
  startAutomation = async () => (await api.post("/api/automation/start")).data;
  stopAutomation = async () => (await api.post("/api/automation/stop")).data;
  triggerAutomation = async () => (await api.post("/api/automation/trigger")).data;
  getRevenueData = async () => (await api.get("/api/financial/revenue")).data;
  getCostData = async () => (await api.get("/api/financial/costs")).data;
  getSocialPosts = async () => (await api.get("/api/social/posts")).data;
  getPostAnalytics = async () => (await api.get("/api/social/analytics")).data;
  createPost = async (post: any) => (await api.post("/api/social/posts", post)).data;
  schedulePost = async (post: any) => (await api.post("/api/social/post-now", post)).data;
  checkApiHealth = async () => (await api.get("/health")).data;
  
  // FAZA 2.5: Automation (mapat la alias)
  getAutomationStatus = async () => api.get("/api/automation/status").then(r=>r.data);
  toggleAutomation = async (enabled:boolean) => api.post("/api/automation/toggle",{enabled}).then(r=>r.data);
  triggerAutomation = async () => api.post("/api/automation/trigger").then(r=>r.data);
  updateAutomationSettings = async (settings:any) => api.post("/api/automation/settings", settings).then(r=>r.data);
  getAutomationLogs = async () => api.get("/api/automation/logs").then(r=>r.data);
}

const svc = new AutoProApiService();
export default svc;                // default
export { api };                    // low-level axios (dacă ai nevoie)
export type { AutoProApiService }; // tipuri opționale
