import { api } from '@/lib/api';

export interface Video {
  id: string;
  title: string;
  url: string;
  thumbnail: string;
  status: 'generating' | 'completed' | 'failed';
  provider: 'ManoleVideoGenerator' | 'Custom';
  createdAt: string;
  metrics: {
    views: number;
    likes: number;
    shares: number;
  };
}

export interface GenerateVideoDto {
  title: string;
  description?: string;
  template_type?: 'educational' | 'testimonial' | 'promotional';
  duration?: number;
}

export interface VideoStats {
  total_videos: number;
  videos_today: number;
  total_views: number;
  total_engagement: number;
  avg_completion_rate: number;
}

class VideoService {
  /**
   * Get all videos with optional filters
   */
  async getVideos(filters?: {
    status?: string;
    limit?: number;
  }): Promise<{ items: Video[]; total: number }> {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.limit) params.append('limit', filters.limit.toString());

    const response = await api.get(`/video/?${params.toString()}`);
    return response.data;
  }

  /**
   * Get a single video by ID
   */
  async getVideoById(id: string): Promise<Video> {
    const response = await api.get(`/video/${id}`);
    return response.data;
  }

  /**
   * Generate a new video
   */
  async generateVideo(data: GenerateVideoDto): Promise<{ job_id: string; message: string }> {
    const response = await api.post('/video/generate', data);
    return response.data;
  }

  /**
   * Get video generation status
   */
  async getVideoStatus(jobId: string): Promise<{
    status: string;
    progress: number;
    video_url?: string;
  }> {
    const response = await api.get(`/video/status/${jobId}`);
    return response.data;
  }

  /**
   * Delete a video
   */
  async deleteVideo(id: string): Promise<void> {
    await api.delete(`/video/${id}`);
  }

  /**
   * Get video statistics
   */
  async getVideoStats(): Promise<VideoStats> {
    const response = await api.get('/video/stats');
    return response.data;
  }

  /**
   * Download video
   */
  async downloadVideo(id: string): Promise<Blob> {
    const response = await api.get(`/video/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  }

  /**
   * Regenerate video
   */
  async regenerateVideo(id: string): Promise<{ job_id: string; message: string }> {
    const response = await api.post(`/video/${id}/regenerate`);
    return response.data;
  }

  /**
   * Get video analytics
   */
  async getVideoAnalytics(id: string): Promise<{
    views: number;
    likes: number;
    shares: number;
    comments: number;
    avg_watch_time: number;
    completion_rate: number;
  }> {
    const response = await api.get(`/video/${id}/analytics`);
    return response.data;
  }
}

export default new VideoService();
