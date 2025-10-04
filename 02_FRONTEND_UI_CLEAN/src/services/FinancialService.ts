import { api } from '@/lib/api';

export interface FinancialDashboard {
  total_revenue: number;
  total_costs: number;
  net_profit: number;
  roi: number;
  revenue_trend: Array<{ date: string; amount: number }>;
  cost_breakdown: Record<string, number>;
}

export interface Revenue {
  id: string;
  amount: number;
  source: string;
  lead_id?: string;
  description: string;
  date: string;
  status: 'pending' | 'received' | 'cancelled';
}

export interface Cost {
  id: string;
  amount: number;
  category: string;
  description: string;
  date: string;
  status: 'pending' | 'paid' | 'cancelled';
}

export interface CreateRevenueDto {
  amount: number;
  source: string;
  lead_id?: string;
  description: string;
  date?: string;
}

export interface CreateCostDto {
  amount: number;
  category: string;
  description: string;
  date?: string;
}

export interface FinancialMetrics {
  total_revenue: number;
  total_costs: number;
  net_profit: number;
  roi: number;
  avg_revenue_per_lead: number;
  cost_per_lead: number;
  conversion_value: number;
  monthly_recurring_revenue: number;
}

export interface CostBreakdown {
  advertising: number;
  software: number;
  operations: number;
  personnel: number;
  other: number;
}

class FinancialService {
  /**
   * Get financial dashboard overview
   */
  async getDashboard(period?: '7d' | '30d' | '90d' | 'all'): Promise<FinancialDashboard> {
    const params = period ? `?period=${period}` : '';
    const response = await api.get(`/financial/dashboard${params}`);
    return response.data;
  }

  /**
   * Get all revenue entries
   */
  async getRevenues(filters?: {
    source?: string;
    status?: string;
    from_date?: string;
    to_date?: string;
  }): Promise<{ items: Revenue[]; total: number; sum: number }> {
    const params = new URLSearchParams();
    if (filters?.source) params.append('source', filters.source);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);

    const response = await api.get(`/financial/revenue?${params.toString()}`);
    return response.data;
  }

  /**
   * Create new revenue entry
   */
  async createRevenue(data: CreateRevenueDto): Promise<Revenue> {
    const response = await api.post('/financial/revenue', data);
    return response.data;
  }

  /**
   * Update revenue entry
   */
  async updateRevenue(id: string, data: Partial<Revenue>): Promise<Revenue> {
    const response = await api.put(`/financial/revenue/${id}`, data);
    return response.data;
  }

  /**
   * Delete revenue entry
   */
  async deleteRevenue(id: string): Promise<void> {
    await api.delete(`/financial/revenue/${id}`);
  }

  /**
   * Get all cost entries
   */
  async getCosts(filters?: {
    category?: string;
    status?: string;
    from_date?: string;
    to_date?: string;
  }): Promise<{ items: Cost[]; total: number; sum: number }> {
    const params = new URLSearchParams();
    if (filters?.category) params.append('category', filters.category);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);

    const response = await api.get(`/financial/costs?${params.toString()}`);
    return response.data;
  }

  /**
   * Create new cost entry
   */
  async createCost(data: CreateCostDto): Promise<Cost> {
    const response = await api.post('/financial/costs', data);
    return response.data;
  }

  /**
   * Update cost entry
   */
  async updateCost(id: string, data: Partial<Cost>): Promise<Cost> {
    const response = await api.put(`/financial/costs/${id}`, data);
    return response.data;
  }

  /**
   * Delete cost entry
   */
  async deleteCost(id: string): Promise<void> {
    await api.delete(`/financial/costs/${id}`);
  }

  /**
   * Get comprehensive financial metrics
   */
  async getMetrics(period?: '7d' | '30d' | '90d' | 'all'): Promise<FinancialMetrics> {
    const params = period ? `?period=${period}` : '';
    const response = await api.get(`/financial/metrics${params}`);
    return response.data;
  }

  /**
   * Get cost breakdown by category
   */
  async getCostBreakdown(period?: '7d' | '30d' | '90d' | 'all'): Promise<CostBreakdown> {
    const params = period ? `?period=${period}` : '';
    const response = await api.get(`/financial/costs/breakdown${params}`);
    return response.data;
  }

  /**
   * Calculate ROI for specific campaign or period
   */
  async calculateROI(filters?: {
    campaign_id?: string;
    from_date?: string;
    to_date?: string;
  }): Promise<{
    revenue: number;
    costs: number;
    roi: number;
    roi_percentage: number;
  }> {
    const params = new URLSearchParams();
    if (filters?.campaign_id) params.append('campaign_id', filters.campaign_id);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);

    const response = await api.get(`/financial/roi?${params.toString()}`);
    return response.data;
  }

  /**
   * Get revenue forecast
   */
  async getRevenueForecast(months?: number): Promise<{
    forecast: Array<{ month: string; predicted_revenue: number; confidence: number }>;
  }> {
    const params = months ? `?months=${months}` : '';
    const response = await api.get(`/financial/forecast${params}`);
    return response.data;
  }

  /**
   * Export financial data
   */
  async exportData(format: 'csv' | 'xlsx', period?: string): Promise<Blob> {
    const params = new URLSearchParams();
    params.append('format', format);
    if (period) params.append('period', period);

    const response = await api.get(`/financial/export?${params.toString()}`, {
      responseType: 'blob',
    });
    return response.data;
  }
}

export default new FinancialService();
