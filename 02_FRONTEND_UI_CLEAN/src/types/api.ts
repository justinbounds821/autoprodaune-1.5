/**
 * API type definitions for AutoPro Daune
 * Replaces 'any' types with proper TypeScript interfaces
 */

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  items: T[];
  total: number;
  page: number;
  pages: number;
  limit?: number;
}

// Lead types
export interface Lead {
  id: string;
  name: string;
  phone_number: string;
  email?: string;
  source: string;
  status: string;
  created_at: string;
  [key: string]: unknown;
}

// Financial types
export interface FinancialDashboard {
  total_costs: number;
  total_revenue: number;
  roi_percentage: number;
  videos_generated: number;
  period: string;
  date_from?: string;
  date_to?: string;
}

export interface Invoice {
  id: string;
  number: string;
  client_name: string;
  client_email: string;
  total: number;
  status: string;
  created_at: string;
  [key: string]: unknown;
}

export interface Payment {
  id: string;
  invoice_id: string;
  amount: number;
  payment_method: string;
  status: string;
  payment_date: string;
  created_at: string;
  [key: string]: unknown;
}

export interface PaymentOverview {
  period: string;
  total_payments: number;
  total_amount: number;
  completed_count: number;
  completed_amount: number;
  pending_count: number;
  pending_amount: number;
  [key: string]: unknown;
}

export interface CreditBalance {
  provider: string;
  credits_available: number;
  credits_used?: number;
  currency?: string;
}

// Automation types
export interface AutomationStatus {
  automation_active?: boolean;
  isActive: boolean;
  status: string;
  daily_target: number;
  postsToday: number;
  posts_today?: number;
  lastRun?: string;
  nextRun?: string;
  platforms?: string[];
  recent_posts?: unknown[];
  recent_videos?: unknown[];
  performance?: {
    total_views_today: number;
    total_engagement_today: number;
    leads_generated_today: number;
  };
}

export interface AutomationLog {
  id: string;
  task_type: string;
  status: string;
  message: string;
  action?: string;
  platform?: string;
  details?: string;
  timestamp: string;
  created_at?: string;
  error?: string;
}

// Video types
export interface VideoJob {
  id: string;
  client_job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  template_type?: string;
  created_at: string;
  output_url?: string;
}

export interface VideoStats {
  total_videos: number;
  completion_rate: number;
  videos_generated_today?: number;
  [key: string]: unknown;
}

// Notification types
export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  read: boolean;
  created_at: string;
  [key: string]: unknown;
}

// AI Insights types
export interface AIInsight {
  id: string;
  title: string;
  description: string;
  category: string;
  confidence: number;
  created_at: string;
  [key: string]: unknown;
}

// Social Media types
export interface SocialPost {
  id: string;
  title: string;
  content: string;
  platforms: string[];
  status: string;
  views?: number;
  likes?: number;
  shares?: number;
  created_at: string;
  [key: string]: unknown;
}

export interface PostAnalytics {
  total_posts: number;
  total_views: number;
  total_engagement: number;
  average_engagement_rate: number;
  [key: string]: unknown;
}

// Tax Calculator types
export interface TaxRate {
  id: string;
  name: string;
  rate: number;
  description?: string;
}

export interface TaxCalculation {
  subtotal: number;
  tax_amount: number;
  total: number;
  tax_rate: number;
  breakdown?: Record<string, number>;
}

// Generic request types
export interface DashboardParams {
  date_from?: string;
  date_to?: string;
  period?: string;
}

export interface NotificationParams {
  limit?: number;
  read?: boolean;
  type?: string;
}

export interface AutomationSettings {
  enabled: boolean;
  posting_times?: string[];
  platforms?: string[];
  [key: string]: unknown;
}
