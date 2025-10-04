/**
 * AI Insights Manager - Business Logic Layer
 * Single Responsibility: Manage AI insights data and calculations
 * File Length: < 200 lines ✅
 */

export interface InsightData {
  id: string;
  type: 'trend' | 'prediction' | 'recommendation' | 'alert';
  title: string;
  description: string;
  confidence: number;
  impact: 'low' | 'medium' | 'high' | 'critical';
  category: 'leads' | 'financial' | 'social' | 'operations';
  data: Record<string, any>;
  created_at: string;
}

export interface AIInsightMetrics {
  total_insights: number;
  high_confidence_insights: number;
  critical_alerts: number;
  categories: Record<string, number>;
}

export class AIInsightsManager {
  private insights: InsightData[] = [];
  private metrics: AIInsightMetrics | null = null;

  async loadInsights(): Promise<InsightData[]> {
    try {
      // Simulated AI insights - în producție ar fi API call
      const mockInsights: InsightData[] = [
        {
          id: '1',
          type: 'prediction',
          title: 'Creștere Așteptată în Leads',
          description: 'AI prezice o creștere de 23% în leads pentru următoarele 30 de zile',
          confidence: 87,
          impact: 'high',
          category: 'leads',
          data: { predicted_increase: 23, period: '30d', factors: ['seasonal', 'marketing_campaign'] },
          created_at: '2025-01-15T10:00:00Z'
        },
        {
          id: '2',
          type: 'alert',
          title: 'Costuri Marketing Peste Buget',
          description: 'Costurile de marketing au depășit bugetul cu 15%',
          confidence: 95,
          impact: 'critical',
          category: 'financial',
          data: { overspend_percentage: 15, budget_category: 'marketing', amount: 750 },
          created_at: '2025-01-15T09:30:00Z'
        },
        {
          id: '3',
          type: 'recommendation',
          title: 'Optimizare Postare Social Media',
          description: 'Postează pe Instagram între 18:00-20:00 pentru engagement maxim',
          confidence: 78,
          impact: 'medium',
          category: 'social',
          data: { platform: 'Instagram', optimal_time: '18:00-20:00', expected_engagement: '+34%' },
          created_at: '2025-01-15T08:45:00Z'
        }
      ];
      
      this.insights = mockInsights;
      return this.insights;
    } catch (error) {
      console.error('Failed to load AI insights:', error);
      throw new Error('Failed to load AI insights');
    }
  }

  async generateInsight(type: InsightData['type'], category: InsightData['category']): Promise<InsightData> {
    try {
      const newInsight: InsightData = {
        id: Date.now().toString(),
        type,
        title: this.generateInsightTitle(type, category),
        description: this.generateInsightDescription(type, category),
        confidence: Math.floor(Math.random() * 30) + 70, // 70-100%
        impact: this.determineImpact(type),
        category,
        data: this.generateInsightData(type, category),
        created_at: new Date().toISOString()
      };

      this.insights.unshift(newInsight);
      return newInsight;
    } catch (error) {
      console.error('Failed to generate insight:', error);
      throw new Error('Failed to generate insight');
    }
  }

  getMetrics(): AIInsightMetrics {
    const total_insights = this.insights.length;
    const high_confidence_insights = this.insights.filter(i => i.confidence >= 80).length;
    const critical_alerts = this.insights.filter(i => i.impact === 'critical').length;
    
    const categories = this.insights.reduce((acc, insight) => {
      acc[insight.category] = (acc[insight.category] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      total_insights,
      high_confidence_insights,
      critical_alerts,
      categories
    };
  }

  getInsightsByCategory(category: InsightData['category']): InsightData[] {
    return this.insights.filter(insight => insight.category === category);
  }

  getInsightsByType(type: InsightData['type']): InsightData[] {
    return this.insights.filter(insight => insight.type === type);
  }

  private generateInsightTitle(type: InsightData['type'], category: InsightData['category']): string {
    const titles = {
      trend: {
        leads: 'Tendințe în Leads',
        financial: 'Tendințe Financiare',
        social: 'Tendințe Social Media',
        operations: 'Tendințe Operaționale'
      },
      prediction: {
        leads: 'Predicție Leads',
        financial: 'Predicție Financiară',
        social: 'Predicție Social Media',
        operations: 'Predicție Operațională'
      },
      recommendation: {
        leads: 'Recomandare Leads',
        financial: 'Recomandare Financiară',
        social: 'Recomandare Social Media',
        operations: 'Recomandare Operațională'
      },
      alert: {
        leads: 'Alertă Leads',
        financial: 'Alertă Financiară',
        social: 'Alertă Social Media',
        operations: 'Alertă Operațională'
      }
    };
    return titles[type][category];
  }

  private generateInsightDescription(type: InsightData['type'], category: InsightData['category']): string {
    const descriptions = {
      trend: 'AI a identificat o tendință interesantă în datele tale',
      prediction: 'AI prezice o evoluție pozitivă în următoarea perioadă',
      recommendation: 'AI recomandă o optimizare pentru îmbunătățirea performanței',
      alert: 'AI a detectat o situație care necesită atenția ta'
    };
    return descriptions[type];
  }

  private determineImpact(type: InsightData['type']): InsightData['impact'] {
    const impactMap = {
      alert: 'critical' as const,
      prediction: 'high' as const,
      recommendation: 'medium' as const,
      trend: 'low' as const
    };
    return impactMap[type];
  }

  private generateInsightData(type: InsightData['type'], category: InsightData['category']): Record<string, any> {
    return {
      type,
      category,
      generated_at: new Date().toISOString(),
      source: 'ai_analysis'
    };
  }
}
