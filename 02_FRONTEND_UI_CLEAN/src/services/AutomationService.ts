import { api } from '@/lib/api';

export interface AutomationStatus {
  is_active: boolean;
  daily_target: number;
  videos_today: number;
  posts_today: number;
  next_scheduled_run: string;
  last_run: string;
  posting_schedule: string[];
}

export interface AutomationConfig {
  is_active: boolean;
  daily_target: number;
  posting_schedule: string[];
}

export interface AutomationMetrics {
  total_videos_generated: number;
  total_posts_published: number;
  total_engagement: number;
  avg_engagement_rate: number;
  total_leads_generated: number;
  automation_uptime: number;
}

export interface DailyCycleResult {
  success: boolean;
  videos_generated: number;
  posts_published: number;
  errors: string[];
  timestamp: string;
}

class AutomationService {
  /**
   * Get current automation status
   */
  async getStatus(): Promise<AutomationStatus> {
    const response = await api.get('/automation/status');
    return response.data;
  }

  /**
   * Start automation
   */
  async start(): Promise<{ message: string; status: AutomationStatus }> {
    const response = await api.post('/automation/start');
    return response.data;
  }

  /**
   * Stop automation
   */
  async stop(): Promise<{ message: string; status: AutomationStatus }> {
    const response = await api.post('/automation/stop');
    return response.data;
  }

  /**
   * Toggle automation on/off
   */
  async toggle(): Promise<{ message: string; is_active: boolean }> {
    const response = await api.post('/automation/toggle');
    return response.data;
  }

  /**
   * Update automation configuration
   */
  async updateConfig(config: Partial<AutomationConfig>): Promise<AutomationStatus> {
    const response = await api.put('/automation/config', config);
    return response.data;
  }

  /**
   * Get automation configuration
   */
  async getConfig(): Promise<AutomationConfig> {
    const response = await api.get('/automation/config');
    return response.data;
  }

  /**
   * Trigger immediate daily cycle
   */
  async triggerDailyCycle(): Promise<DailyCycleResult> {
    const response = await api.post('/automation/trigger-daily-cycle');
    return response.data;
  }

  /**
   * Generate and post single video
   */
  async generateAndPost(data?: {
    template_type?: string;
    platforms?: string[];
  }): Promise<{ job_id: string; message: string }> {
    const response = await api.post('/automation/generate-and-post', data || {});
    return response.data;
  }

  /**
   * Get automation metrics
   */
  async getMetrics(): Promise<AutomationMetrics> {
    const response = await api.get('/automation/metrics');
    return response.data;
  }

  /**
   * Get automation logs
   */
  async getLogs(filters?: {
    limit?: number;
    level?: string;
  }): Promise<{
    logs: Array<{
      timestamp: string;
      level: string;
      message: string;
      details: any;
    }>;
    total: number;
  }> {
    const params = new URLSearchParams();
    if (filters?.limit) params.append('limit', filters.limit.toString());
    if (filters?.level) params.append('level', filters.level);

    const response = await api.get(`/automation/logs?${params.toString()}`);
    return response.data;
  }

  /**
   * Test automation components
   */
  async testComponents(): Promise<{
    video_generator: boolean;
    social_poster: boolean;
    scheduler: boolean;
    database: boolean;
  }> {
    const response = await api.get('/automation/test');
    return response.data;
  }
}

export default new AutomationService();
