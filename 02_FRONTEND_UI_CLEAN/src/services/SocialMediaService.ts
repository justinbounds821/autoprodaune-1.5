import { api } from '@/lib/api';

export interface SocialPost {
  id: string;
  title: string;
  content: string;
  platforms: string[];
  video_url?: string;
  thumbnail_url?: string;
  status: 'scheduled' | 'published' | 'failed';
  scheduled_for?: string;
  posted_at?: string;
  metrics: {
    views: number;
    likes: number;
    shares: number;
    comments: number;
    engagement: number;
  };
}

export interface CreatePostDto {
  title: string;
  content: string;
  platforms: string[];
  video_url?: string;
  scheduled_for?: string;
}

export interface SocialStats {
  tiktok: PlatformStats;
  instagram: PlatformStats;
  facebook: PlatformStats;
  youtube: PlatformStats;
}

export interface PlatformStats {
  total_posts: number;
  total_views: number;
  total_engagement: number;
  followers: number;
  engagement_rate: number;
  top_post?: {
    id: string;
    title: string;
    views: number;
    engagement: number;
  };
}

export interface SocialAnalytics {
  total_posts: number;
  total_views: number;
  total_engagement: number;
  total_leads: number;
  conversion_rate: number;
  best_posting_times: string[];
  top_performing_content: string[];
}

class SocialMediaService {
  /**
   * Get all social media posts
   */
  async getPosts(filters?: {
    platform?: string;
    status?: string;
    limit?: number;
  }): Promise<{ items: SocialPost[]; total: number }> {
    const params = new URLSearchParams();
    if (filters?.platform) params.append('platform', filters.platform);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.limit) params.append('limit', filters.limit.toString());

    const response = await api.get(`/social/?${params.toString()}`);
    return response.data;
  }

  /**
   * Get a single post by ID
   */
  async getPostById(id: string): Promise<SocialPost> {
    const response = await api.get(`/social/${id}`);
    return response.data;
  }

  /**
   * Create and publish a new post
   */
  async createPost(data: CreatePostDto): Promise<SocialPost> {
    const response = await api.post('/social/post', data);
    return response.data;
  }

  /**
   * Delete a post
   */
  async deletePost(id: string): Promise<void> {
    await api.delete(`/social/${id}`);
  }

  /**
   * Get social media statistics for all platforms
   */
  async getStats(): Promise<SocialStats> {
    const response = await api.get('/social/stats');
    return response.data;
  }

  /**
   * Get platform-specific statistics
   */
  async getPlatformStats(platform: 'tiktok' | 'instagram' | 'facebook' | 'youtube'): Promise<PlatformStats> {
    const response = await api.get(`/social/stats/${platform}`);
    return response.data;
  }

  /**
   * Get comprehensive social analytics
   */
  async getAnalytics(period?: '7d' | '30d' | '90d'): Promise<SocialAnalytics> {
    const params = period ? `?period=${period}` : '';
    const response = await api.get(`/social/analytics${params}`);
    return response.data;
  }

  /**
   * Refresh metrics for a post
   */
  async refreshPostMetrics(id: string): Promise<SocialPost> {
    const response = await api.post(`/social/${id}/refresh-metrics`);
    return response.data;
  }

  /**
   * Get posting recommendations
   */
  async getRecommendations(): Promise<{
    best_times: string[];
    trending_topics: string[];
    suggested_hashtags: string[];
    content_ideas: string[];
  }> {
    const response = await api.get('/social/recommendations');
    return response.data;
  }

  /**
   * Schedule a post for later
   */
  async schedulePost(data: CreatePostDto): Promise<SocialPost> {
    const response = await api.post('/social/schedule', data);
    return response.data;
  }

  /**
   * Get scheduled posts
   */
  async getScheduledPosts(): Promise<SocialPost[]> {
    const response = await api.get('/social/scheduled');
    return response.data;
  }

  /**
   * Cancel scheduled post
   */
  async cancelScheduledPost(id: string): Promise<void> {
    await api.delete(`/social/scheduled/${id}`);
  }

  /**
   * Get engagement breakdown
   */
  async getEngagementBreakdown(postId: string): Promise<{
    views_by_day: Record<string, number>;
    likes_by_day: Record<string, number>;
    shares_by_day: Record<string, number>;
    comments_by_day: Record<string, number>;
    demographics: {
      age_groups: Record<string, number>;
      locations: Record<string, number>;
    };
  }> {
    const response = await api.get(`/social/${postId}/engagement`);
    return response.data;
  }
}

export default new SocialMediaService();
