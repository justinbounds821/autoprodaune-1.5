/**
 * AI Insights Manager - Business Logic Layer
 * Single Responsibility: Manage AI insights data and calculations
 * File Length: < 200 lines ✅
 */

import { getBusinessInsights } from '@/services/apiService';
import type { BusinessInsight, AIInsightsResponse } from '@/types/api';

export type InsightData = BusinessInsight;

export interface AIInsightMetrics {
  total_insights: number;
  high_confidence_insights: number;
  critical_alerts: number;
  categories: Record<string, number>;
}

export interface AIInsightsAPIContext {
  window: { start: string; end: string };
  source_counts: Record<string, number>;
}

export type AIInsightsAPIResponse = AIInsightsResponse;

export class AIInsightsManager {
  private insights: InsightData[] = [];
  private metrics: AIInsightMetrics | null = null;
  private context: AIInsightsAPIContext | null = null;

  async loadInsights(filters?: Record<string, unknown>): Promise<InsightData[]> {
    try {
      const response = await getBusinessInsights(filters);
      this.insights = response.insights;
      this.metrics = response.metrics;
      this.context = response.context;
      return this.insights;
    } catch (error) {
      console.error('Failed to load AI insights:', error);
      // Return empty array on error instead of throwing
      this.insights = [];
      this.metrics = {
        total_insights: 0,
        high_confidence_insights: 0,
        critical_alerts: 0,
        categories: {}
      };
      return this.insights;
    }
  }

  async generateInsight(type: InsightData['type'], category: InsightData['category']): Promise<InsightData> {
    try {
      const newInsight: InsightData = {
        id: Date.now().toString(),
        type,
        title: this.generateInsightTitle(type, category),
        description: this.generateInsightDescription(type, category),
        confidence: Math.floor(Math.random() * 30) + 70,
        impact: this.determineImpact(type),
        category,
        data: this.generateInsightData(type, category),
        created_at: new Date().toISOString()
      };

      this.insights.unshift(newInsight);
      if (this.metrics) {
        this.metrics.total_insights += 1;
        if (newInsight.confidence >= 80) this.metrics.high_confidence_insights += 1;
        if (newInsight.impact === 'critical') this.metrics.critical_alerts += 1;
        this.metrics.categories[newInsight.category] =
          (this.metrics.categories[newInsight.category] || 0) + 1;
      }
      return newInsight;
    } catch (error) {
      console.error('Failed to generate insight:', error);
      throw new Error('Failed to generate insight');
    }
  }

  getMetrics(): AIInsightMetrics {
    if (this.metrics) {
      return this.metrics;
    }

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

  getContext(): AIInsightsAPIContext | null {
    return this.context;
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
        social: 'Predicție Socială',
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
        social: 'Alertă Socială',
        operations: 'Alertă Operațională'
      }
    } as const;
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
