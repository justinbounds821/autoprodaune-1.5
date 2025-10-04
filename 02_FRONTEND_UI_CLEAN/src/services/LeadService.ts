import { api } from '@/lib/api';

export interface Lead {
  id: number | string;
  name: string;
  phone: string;
  email?: string;
  details: string;
  status: 'new' | 'contacted' | 'in-progress' | 'completed' | 'rejected';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  location?: string;
  damage_type?: string;
  source?: string;
  files: string[] | null;
  createdAt: string;
}

export interface CreateLeadDto {
  name: string;
  phone: string;
  email?: string;
  details: string;
  location?: string;
  damage_type?: string;
  source?: string;
}

export interface LeadStats {
  total_leads: number;
  new_leads: number;
  contacted_leads: number;
  in_progress_leads: number;
  completed_leads: number;
  conversion_rate: number;
}

class LeadService {
  /**
   * Get all leads with optional filters
   */
  async getLeads(filters?: {
    status?: string;
    priority?: string;
    search?: string;
  }): Promise<{ items: Lead[]; total: number }> {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.priority) params.append('priority', filters.priority);
    if (filters?.search) params.append('search', filters.search);

    const response = await api.get(`/leads/?${params.toString()}`);
    return response.data;
  }

  /**
   * Get a single lead by ID
   */
  async getLeadById(id: string | number): Promise<Lead> {
    const response = await api.get(`/leads/${id}`);
    return response.data;
  }

  /**
   * Create a new lead
   */
  async createLead(data: CreateLeadDto): Promise<Lead> {
    const response = await api.post('/leads/', data);
    return response.data;
  }

  /**
   * Update lead status
   */
  async updateLeadStatus(
    id: string | number,
    status: Lead['status']
  ): Promise<Lead> {
    const response = await api.put(`/leads/${id}`, { status });
    return response.data;
  }

  /**
   * Update lead priority
   */
  async updateLeadPriority(
    id: string | number,
    priority: Lead['priority']
  ): Promise<Lead> {
    const response = await api.put(`/leads/${id}`, { priority });
    return response.data;
  }

  /**
   * Update entire lead
   */
  async updateLead(id: string | number, data: Partial<Lead>): Promise<Lead> {
    const response = await api.put(`/leads/${id}`, data);
    return response.data;
  }

  /**
   * Delete a lead
   */
  async deleteLead(id: string | number): Promise<void> {
    await api.delete(`/leads/${id}`);
  }

  /**
   * Get lead statistics
   */
  async getLeadStats(): Promise<LeadStats> {
    const response = await api.get('/leads/stats');
    return response.data;
  }

  /**
   * Upload files for a lead
   */
  async uploadLeadFiles(
    id: string | number,
    files: FileList
  ): Promise<{ file_urls: string[] }> {
    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append('files', file);
    });

    const response = await api.post(`/leads/${id}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * Add note to lead
   */
  async addLeadNote(
    id: string | number,
    note: string
  ): Promise<Lead> {
    const response = await api.post(`/leads/${id}/notes`, { note });
    return response.data;
  }
}

export default new LeadService();
