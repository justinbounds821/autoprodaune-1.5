/**
 * Recurring Revenue Manager - Business Logic Layer
 * Single Responsibility: Manage MRR calculations and subscriptions
 * File Length: < 200 lines ✅
 */

export interface Subscription {
  id: string;
  client_id: string;
  client_name: string;
  service_type: 'legal_consultation' | 'case_management' | 'document_processing' | 'expert_witness';
  billing_cycle: 'monthly' | 'quarterly' | 'yearly';
  amount: number;
  start_date: string;
  end_date?: string;
  status: 'active' | 'paused' | 'cancelled' | 'expired';
  next_billing_date: string;
  created_at: string;
  updated_at: string;
}

export interface MRRMetrics {
  total_mrr: number;
  new_mrr: number;
  expansion_mrr: number;
  churn_mrr: number;
  net_mrr_growth: number;
  active_subscriptions: number;
  churn_rate: number;
  average_revenue_per_user: number;
  customer_lifetime_value: number;
}

export interface MRRReport {
  period: string;
  metrics: MRRMetrics;
  subscriptions: Subscription[];
  trends: {
    month_over_month_growth: number;
    quarter_over_quarter_growth: number;
    year_over_year_growth: number;
  };
}

export class RecurringRevenueManager {
  private subscriptions: Subscription[] = [];

  async loadSubscriptions(): Promise<Subscription[]> {
    try {
      // Simulated data - în producție ar fi API call
      const mockSubscriptions: Subscription[] = [
        {
          id: '1',
          client_id: 'client_1',
          client_name: 'Ion Popescu',
          service_type: 'legal_consultation',
          billing_cycle: 'monthly',
          amount: 500,
          start_date: '2024-01-01',
          status: 'active',
          next_billing_date: '2025-02-01',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2025-01-15T10:00:00Z'
        },
        {
          id: '2',
          client_id: 'client_2',
          client_name: 'Maria Ionescu',
          service_type: 'case_management',
          billing_cycle: 'quarterly',
          amount: 1200,
          start_date: '2024-03-01',
          status: 'active',
          next_billing_date: '2025-03-01',
          created_at: '2024-03-01T00:00:00Z',
          updated_at: '2025-01-10T14:30:00Z'
        },
        {
          id: '3',
          client_id: 'client_3',
          client_name: 'Alexandru Dumitrescu',
          service_type: 'document_processing',
          billing_cycle: 'yearly',
          amount: 4800,
          start_date: '2024-06-01',
          status: 'active',
          next_billing_date: '2025-06-01',
          created_at: '2024-06-01T00:00:00Z',
          updated_at: '2024-12-15T09:15:00Z'
        }
      ];
      
      this.subscriptions = mockSubscriptions;
      return this.subscriptions;
    } catch (error) {
      console.error('Failed to load subscriptions:', error);
      throw new Error('Failed to load subscriptions');
    }
  }

  calculateMRR(): MRRMetrics {
    const activeSubscriptions = this.subscriptions.filter(sub => sub.status === 'active');
    
    let totalMRR = 0;
    let totalARPU = 0;
    
    activeSubscriptions.forEach(subscription => {
      let monthlyAmount = subscription.amount;
      
      // Convert to monthly amount based on billing cycle
      switch (subscription.billing_cycle) {
        case 'quarterly':
          monthlyAmount = subscription.amount / 3;
          break;
        case 'yearly':
          monthlyAmount = subscription.amount / 12;
          break;
        case 'monthly':
        default:
          monthlyAmount = subscription.amount;
          break;
      }
      
      totalMRR += monthlyAmount;
      totalARPU += monthlyAmount;
    });

    const averageRevenuePerUser = activeSubscriptions.length > 0 ? totalARPU / activeSubscriptions.length : 0;
    
    // Calculate churn rate (simplified - would need historical data in production)
    const churnedSubscriptions = this.subscriptions.filter(sub => sub.status === 'cancelled').length;
    const totalSubscriptions = this.subscriptions.length;
    const churnRate = totalSubscriptions > 0 ? (churnedSubscriptions / totalSubscriptions) * 100 : 0;
    
    // Calculate CLV (simplified)
    const customerLifetimeValue = averageRevenuePerUser / (churnRate / 100 || 0.01);

    return {
      total_mrr: Math.round(totalMRR * 100) / 100,
      new_mrr: 0, // Would need historical data
      expansion_mrr: 0, // Would need historical data
      churn_mrr: 0, // Would need historical data
      net_mrr_growth: 0, // Would need historical data
      active_subscriptions: activeSubscriptions.length,
      churn_rate: Math.round(churnRate * 100) / 100,
      average_revenue_per_user: Math.round(averageRevenuePerUser * 100) / 100,
      customer_lifetime_value: Math.round(customerLifetimeValue * 100) / 100
    };
  }

  generateMRRReport(period: string): MRRReport {
    const metrics = this.calculateMRR();
    
    return {
      period,
      metrics,
      subscriptions: this.subscriptions,
      trends: {
        month_over_month_growth: 12.5, // Simulated
        quarter_over_quarter_growth: 28.3, // Simulated
        year_over_year_growth: 156.7 // Simulated
      }
    };
  }

  createSubscription(subscriptionData: Omit<Subscription, 'id' | 'created_at' | 'updated_at'>): Subscription {
    const newSubscription: Subscription = {
      ...subscriptionData,
      id: Date.now().toString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    this.subscriptions.push(newSubscription);
    return newSubscription;
  }

  updateSubscription(id: string, updates: Partial<Subscription>): Subscription | null {
    const index = this.subscriptions.findIndex(sub => sub.id === id);
    if (index === -1) return null;
    
    this.subscriptions[index] = {
      ...this.subscriptions[index],
      ...updates,
      updated_at: new Date().toISOString()
    };
    
    return this.subscriptions[index];
  }

  cancelSubscription(id: string): Subscription | null {
    return this.updateSubscription(id, { 
      status: 'cancelled',
      end_date: new Date().toISOString().split('T')[0]
    });
  }

  getSubscriptionsByStatus(status: Subscription['status']): Subscription[] {
    return this.subscriptions.filter(sub => sub.status === status);
  }

  getSubscriptionsByServiceType(serviceType: Subscription['service_type']): Subscription[] {
    return this.subscriptions.filter(sub => sub.service_type === serviceType);
  }

  getUpcomingBilling(): Subscription[] {
    const nextMonth = new Date();
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    const nextMonthStr = nextMonth.toISOString().split('T')[0];
    
    return this.subscriptions.filter(sub => 
      sub.status === 'active' && sub.next_billing_date <= nextMonthStr
    );
  }
}
