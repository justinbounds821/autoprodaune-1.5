// API Response Types for AutoPro Daune

export interface FinancialBreakdown {
  total_revenue: number;
  total_costs: number;
  net_profit: number;
  roi_percentage: number;
  start_date: string;
  end_date: string;
  revenue: Array<{
    month: string;
    revenue: number;
    costs: number;
    profit: number;
  }>;
  costs: {
    top: Array<{
      id: string;
      provider: string;
      operation: string;
      timestamp: string;
      cost: number;
    }>;
    by_category: Array<{
      category: string;
      total: number;
      count: number;
    }>;
  };
  timeline: Array<{
    date: string;
    revenue: number;
    costs: number;
    profit: number;
  }>;
}

export interface FinancialCostCategories {
  categories: Array<{
    id: string;
    name: string;
    description: string;
    budget_amount: number;
    spent_amount: number;
    period: 'monthly' | 'quarterly' | 'yearly';
    alerts: {
      warning_threshold: number;
      critical_threshold: number;
    };
  }>;
}

export interface SocialFollowers {
  platforms: Array<{
    platform: string;
    followers: number;
    engagement: number;
    posts: number;
  }>;
  total_followers: number;
  engagement_rate: number;
}

export interface VideoPerformance {
  total_videos: number;
  total_views: number;
  avg_completion_rate: number;
  performance: Array<{
    date: string;
    views: number;
    completionRate: number;
  }>;
  topics: Array<{
    topic: string;
    views: number;
    engagement: number;
  }>;
}

export interface AutomationStatus {
  enabled: boolean;
  jobs: Array<{
    id: string;
    name: string;
    enabled: boolean;
    schedule: string;
    last_run: string | null;
    next_run: string;
  }>;
  schedule: {
    daily_posts: number;
    video_generation_enabled: boolean;
    auto_response_enabled: boolean;
  };
}

export interface AutomationRecentAction {
  id: string;
  timestamp: string;
  action: string;
  status: 'success' | 'failed' | 'pending';
  details: string;
}

export interface BusinessInsight {
  id: string;
  title: string;
  description: string;
  impact_score: number;
  confidence: number;
  tags: string[];
  category: string;
  type: string;
  metrics: Record<string, number>;
  created_at: string;
}

export interface PredictiveAnalytics {
  predictions: Array<{
    metric: string;
    current_value: number;
    predicted_value: number;
    confidence: number;
    timeframe: string;
  }>;
  trends: Array<{
    metric: string;
    direction: 'up' | 'down' | 'stable';
    percentage_change: number;
  }>;
}

export interface ComprehensiveAnalytics {
  overview: {
    total_leads: number;
    conversion_rate: number;
    avg_response_time: number;
    revenue: number;
    social_engagement: number;
    video_views: number;
  };
  leads: {
    daily: Array<{
      date: string;
      leads: number;
      conversions: number;
    }>;
    sources: Array<{
      source: string;
      count: number;
      percentage: number;
    }>;
    status: Array<{
      status: string;
      count: number;
    }>;
  };
}

export interface CaptionGenerationRequest {
  topic: string;
  tone: 'professional' | 'casual' | 'funny' | 'inspiring' | 'urgent';
  platform: 'TikTok' | 'Instagram' | 'Facebook';
  include_hashtags: boolean;
  max_length: number;
}

export interface CaptionGenerationResponse {
  caption: string;
  hashtags: string[];
  engagement: {
    estimated: number;
    factors: string[];
  };
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

export interface CostEntry {
  id: string;
  amount: number;
  category: string;
  description: string;
  date: string;
  recurring: boolean;
  tags: string[];
  provider?: string;
  operation?: string;
  timestamp?: string;
  cost?: number;
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
  categories: Array<{
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
  }>;
  created_at: string;
  updated_at: string;
}

export interface Lead {
  id: string;
  name: string;
  phone: string;
  email?: string;
  location?: string;
  damageType?: string;
  priority: 'low' | 'medium' | 'high';
  status: 'new' | 'contacted' | 'in-progress' | 'completed' | 'rejected';
  details: string;
  files: string[];
  createdAt: string;
  updatedAt: string;
}
