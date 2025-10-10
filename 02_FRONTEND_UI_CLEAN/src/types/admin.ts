// AutoPro Daune Admin Interface Type Definitions

export interface Video {
  id: string;
  title: string;
  url: string;
  thumbnail: string;
  status: 'generating' | 'completed' | 'failed';
  provider: 'Pika' | 'HeyGen';
  createdAt: string;
  metrics: {
    views: number;
    likes: number;
    shares: number;
  };
}

export interface AutomationStatus {
  isActive: boolean;
  nextRun: string;
  lastRun: string;
  postsToday: number;
  dailyTarget: number;
  platforms: string[];
}

export interface SocialPost {
  id: string;
  content: string;
  platform: 'TikTok' | 'Instagram' | 'Facebook';
  status: 'scheduled' | 'posted' | 'failed';
  engagement: {
    likes: number;
    comments: number;
    shares: number;
  };
  createdAt: string;
}

export interface FinancialData {
  revenue: number;
  costs: number;
  profit: number;
  roi: number;
  referralRewards: number;
  period: string;
  total_revenue?: number;
  total_costs?: number;
  net_profit?: number;
  roi_percentage?: number;
  start_date?: string;
  end_date?: string;
}

export interface FinancialTimelinePoint {
  date: string;
  revenue: number;
  costs: number;
  profit: number;
  cumulative_profit?: number;
}

export interface FinancialBreakdown {
  period: string;
  start_date?: string;
  end_date?: string;
  costs: {
    total: number;
    by_category: Record<string, number>;
    by_provider: Record<string, number>;
    top: Array<{
      id?: number | string;
      provider?: string;
      operation?: string;
      category?: string;
      amount: number;
      timestamp?: string;
    }>;
  };
  revenue: {
    total: number;
    by_category: Record<string, number>;
    by_source: Record<string, number>;
    top: Array<{
      id?: number | string;
      source?: string;
      category?: string;
      amount: number;
      timestamp?: string;
    }>;
  };
  timeline: FinancialTimelinePoint[];
  profitability: {
    net_profit: number;
    roi: number;
    profit_margin: number;
  };
}

export interface FinancialForecast {
  period: string;
  start_date?: string;
  end_date?: string;
  averages: Record<string, number>;
  growth_rates: Record<string, number>;
  forecasts: Record<string, { revenue: number; costs: number; profit: number; trend: string }>;
  confidence: number;
  series: FinancialTimelinePoint[];
}

export interface CostCategory {
  slug: string;
  name: string;
  description?: string;
  budget_cap?: number | string;
  color?: string;
  is_default?: boolean;
}

export interface LeadDetails {
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

export interface LeadFilters {
  status?: string;
  priority?: string;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
}

export interface VideoMetrics {
  views: number;
  likes: number;
  shares: number;
  comments: number;
  engagement_rate: number;
}

export interface EngagementMetrics {
  likes: number;
  comments: number;
  shares: number;
  views: number;
  engagement_rate: number;
}

export interface PostData {
  content: string;
  platform: 'TikTok' | 'Instagram' | 'Facebook';
  scheduledFor?: string;
  videoId?: string;
}

export interface Analytics {
  platform: string;
  totalPosts: number;
  totalEngagement: number;
  averageEngagement: number;
  topPerformingPost: string;
  growthRate: number;
}

export interface Revenue {
  date: string;
  amount: number;
  source: string;
  currency: string;
}

export interface Cost {
  date: string;
  amount: number;
  category: string;
  description: string;
  currency: string;
}

export interface SystemStatus {
  backend: 'online' | 'offline' | 'error';
  database: 'connected' | 'disconnected' | 'error';
  automation: 'active' | 'inactive' | 'error';
  socialMedia: {
    platform: string;
    status: 'connected' | 'disconnected' | 'error';
  }[];
}

export interface ActivityLog {
  id: string;
  type: 'video_generated' | 'post_published' | 'lead_received' | 'automation_triggered';
  description: string;
  timestamp: string;
  details?: any;
}

export interface AutomationLog {
  id: string;
  timestamp: string;
  action: string;
  status: 'success' | 'failed' | 'pending';
  platform?: string;
  error?: string;
  details: string;
}

export interface OverviewStats {
  videosGenerated: number;
  postsToday: number;
  newLeads: number;
  revenue: number;
  automationStatus: 'active' | 'inactive';
  systemHealth: 'good' | 'warning' | 'critical';
}