/**
 * Comprehensive API Type Definitions for AutoPro Daune
 * Single source of truth for all API data structures
 */

// ==================== FINANCIAL TYPES ====================

export interface FinancialBreakdown {
  total_revenue: number;
  total_costs: number;
  net_profit: number;
  roi_percentage: number;
  start_date: string;
  end_date: string;
  timeline: FinancialTimelinePoint[];
  costs: CostBreakdown;
}

export interface FinancialTimelinePoint {
  date: string;
  revenue: number;
  costs: number;
  profit: number;
}

export interface CostBreakdown {
  top: CostEntry[];
  by_provider: Record<string, number>;
  by_category: Record<string, number>;
  total: number;
}

export interface CostEntry {
  id: string;
  provider: string;
  operation: string;
  amount: number;
  currency: string;
  timestamp: string;
  category?: string;
  metadata?: Record<string, any>;
}

export interface CostCategory {
  id: string;
  name: string;
  description?: string;
  budget_limit?: number;
  alert_threshold?: number;
}

export interface BudgetCategory {
  id: string;
  name: string;
  description: string;
  budget_amount: number;
  spent_amount: number;
  period: 'monthly' | 'quarterly' | 'yearly';
  color: string;
  alerts: {
    warning_threshold: number;
    critical_threshold: number;
  };
}

export interface BudgetPlan {
  id: string;
  name: string;
  description: string;
  total_budget: number;
  period: 'monthly' | 'quarterly' | 'yearly';
  start_date: string;
  end_date: string;
  status: 'draft' | 'active' | 'completed' | 'paused';
  categories: BudgetCategory[];
  created_at: string;
  updated_at: string;
}

// ==================== SOCIAL MEDIA TYPES ====================

export interface SocialFollowers {
  total: number;
  by_platform: Record<string, PlatformFollowers>;
}

export interface PlatformFollowers {
  followers: number;
  growth_rate: number;
  engagement_rate: number;
  posts_count: number;
}

export interface SocialPost {
  id: string;
  content: string;
  platform: 'TikTok' | 'Instagram' | 'Facebook' | 'YouTube';
  status: 'scheduled' | 'posted' | 'failed';
  scheduled_for?: string;
  posted_at?: string;
  engagement?: EngagementMetrics;
  video_id?: string;
  thumbnail?: string;
}

export interface EngagementMetrics {
  likes: number;
  comments: number;
  shares: number;
  views?: number;
  engagement_rate?: number;
}

export interface CaptionGenerateRequest {
  topic: string;
  tone: 'professional' | 'casual' | 'funny' | 'inspiring' | 'urgent';
  platform: 'TikTok' | 'Instagram' | 'Facebook';
  include_hashtags: boolean;
  max_length: number;
}

export interface CaptionResponse {
  caption: string;
  hashtags: string[];
  engagement_prediction?: {
    estimated: number;
    factors: string[];
  };
}

// ==================== VIDEO TYPES ====================

export interface VideoPerformance {
  total_videos: number;
  total_views: number;
  avg_completion_rate: number;
  top_performing: VideoStats[];
  by_topic?: Record<string, TopicStats>;
}

export interface VideoStats {
  id: string;
  title: string;
  views: number;
  completion_rate: number;
  engagement: number;
  created_at: string;
}

export interface TopicStats {
  topic: string;
  views: number;
  engagement: number;
  video_count: number;
}

// ==================== LEAD TYPES ====================

export interface Lead {
  id: string;
  name: string;
  phone: string;
  email?: string;
  location?: string;
  damage_type?: string;
  priority: 'low' | 'medium' | 'high';
  status: 'new' | 'contacted' | 'in-progress' | 'completed' | 'rejected';
  details: string;
  files?: string[];
  created_at: string;
  updated_at: string;
  source?: string;
}

export interface LeadStats {
  total: number;
  by_status: Record<string, number>;
  by_source: Record<string, number>;
  conversion_rate: number;
  timeline: LeadTimelinePoint[];
}

export interface LeadTimelinePoint {
  date: string;
  leads: number;
  conversions: number;
}

// ==================== AUTOMATION TYPES ====================

export interface AutomationStatus {
  automation_active: boolean;
  daily_target: number;
  posts_today: number;
  next_scheduled_post: string;
  schedule: string[];
  last_action?: AutomationAction;
  uptime?: string;
  performance?: {
    total_posts_this_week: number;
    success_rate: number;
    average_engagement: number;
  };
}

export interface AutomationAction {
  action: string;
  timestamp: string;
  user: string;
  details?: string;
  status?: 'success' | 'failed' | 'pending';
}

export interface CronJob {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  schedule: {
    minute: string;
    hour: string;
    dayOfMonth: string;
    month: string;
    dayOfWeek: string;
  };
  action: 'post_content' | 'generate_video' | 'send_notifications' | 'backup_data';
  platforms: string[];
  lastRun: string | null;
  nextRun: string;
}

// ==================== AI INSIGHTS TYPES ====================

export interface BusinessInsight {
  id: string;
  type: 'trend' | 'prediction' | 'recommendation' | 'alert';
  title: string;
  description: string;
  confidence: number;
  impact: 'low' | 'medium' | 'high' | 'critical';
  category: 'leads' | 'financial' | 'social' | 'operations';
  data: Record<string, any>;
  tags?: string[];
  metrics?: Record<string, number>;
  created_at: string;
}

export interface AIInsightsResponse {
  insights: BusinessInsight[];
  metrics: {
    total_insights: number;
    high_confidence_insights: number;
    critical_alerts: number;
    categories: Record<string, number>;
  };
  context: {
    window: { start: string; end: string };
    source_counts: Record<string, number>;
  };
}

export interface PredictiveAnalytics {
  forecasts: Forecast[];
  trends: Trend[];
  recommendations: Recommendation[];
}

export interface Forecast {
  metric: string;
  current: number;
  predicted: number;
  confidence: number;
  timeframe: string;
}

export interface Trend {
  name: string;
  direction: 'up' | 'down' | 'stable';
  change_percentage: number;
  significance: 'low' | 'medium' | 'high';
}

export interface Recommendation {
  title: string;
  description: string;
  impact: string;
  effort: 'low' | 'medium' | 'high';
  priority: number;
}

// ==================== ANALYTICS TYPES ====================

export interface AnalyticsData {
  overview: {
    totalLeads: number;
    conversionRate: number;
    avgResponseTime: number;
    revenue: number;
    socialEngagement: number;
    videoViews: number;
  };
  leads: {
    daily: LeadTimelinePoint[];
    sources: Array<{ source: string; count: number; percentage: number }>;
    status: Array<{ status: string; count: number; color: string }>;
  };
  social: {
    platforms: Array<{ 
      platform: string; 
      followers: number; 
      engagement: number; 
      posts: number;
    }>;
    engagement: Array<{ 
      date: string; 
      likes: number; 
      shares: number; 
      comments: number;
    }>;
    topPosts: Array<{ 
      id: string; 
      content: string; 
      engagement: number; 
      platform: string;
    }>;
  };
  financial: {
    revenue: FinancialTimelinePoint[];
    categories: Array<{ 
      category: string; 
      amount: number; 
      percentage: number; 
      color: string;
    }>;
  };
  video: {
    performance: Array<{ date: string; views: number; completionRate: number }>;
    topics: Array<{ topic: string; views: number; engagement: number }>;
  };
}

// ==================== API RESPONSE WRAPPERS ====================

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

// ==================== ERROR TYPES ====================

export interface ApiError {
  status: number;
  message: string;
  details?: any;
}
