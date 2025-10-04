/**
 * AI Insights ViewModel - UI State Management
 * Single Responsibility: Manage UI state and user interactions
 * File Length: < 200 lines ✅
 */

import { AIInsightsManager, InsightData } from './AIInsightsManager';

export interface UIState {
  loading: boolean;
  error: string | null;
  selectedCategory: InsightData['category'] | 'all';
  selectedType: InsightData['type'] | 'all';
  showFilters: boolean;
  insights: InsightData[];
  metrics: ReturnType<AIInsightsManager['getMetrics']> | null;
}

export class AIInsightsViewModel {
  private manager: AIInsightsManager;
  private state: UIState;
  private listeners: ((state: UIState) => void)[] = [];

  constructor(manager: AIInsightsManager) {
    this.manager = manager;
    this.state = {
      loading: false,
      error: null,
      selectedCategory: 'all',
      selectedType: 'all',
      showFilters: false,
      insights: [],
      metrics: null
    };
  }

  subscribe(listener: (state: UIState) => void): () => void {
    this.listeners.push(listener);
    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  private notify(): void {
    this.listeners.forEach(listener => listener({ ...this.state }));
  }

  getState(): UIState {
    return { ...this.state };
  }

  async loadInsights(): Promise<void> {
    this.setState({ loading: true, error: null });
    
    try {
      const insights = await this.manager.loadInsights();
      const metrics = this.manager.getMetrics();
      
      this.setState({
        insights,
        metrics,
        loading: false
      });
    } catch (error) {
      this.setState({
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load insights'
      });
    }
  }

  async generateInsight(type: InsightData['type'], category: InsightData['category']): Promise<void> {
    this.setState({ loading: true, error: null });
    
    try {
      const newInsight = await this.manager.generateInsight(type, category);
      const metrics = this.manager.getMetrics();
      
      this.setState({
        insights: [newInsight, ...this.state.insights],
        metrics,
        loading: false
      });
    } catch (error) {
      this.setState({
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to generate insight'
      });
    }
  }

  setCategory(category: InsightData['category'] | 'all'): void {
    this.setState({ selectedCategory: category });
  }

  setType(type: InsightData['type'] | 'all'): void {
    this.setState({ selectedType: type });
  }

  toggleFilters(): void {
    this.setState({ showFilters: !this.state.showFilters });
  }

  getFilteredInsights(): InsightData[] {
    let filtered = [...this.state.insights];

    if (this.state.selectedCategory !== 'all') {
      filtered = filtered.filter(insight => insight.category === this.state.selectedCategory);
    }

    if (this.state.selectedType !== 'all') {
      filtered = filtered.filter(insight => insight.type === this.state.selectedType);
    }

    return filtered;
  }

  getInsightsByImpact(): Record<InsightData['impact'], InsightData[]> {
    const insights = this.getFilteredInsights();
    return insights.reduce((acc, insight) => {
      if (!acc[insight.impact]) {
        acc[insight.impact] = [];
      }
      acc[insight.impact].push(insight);
      return acc;
    }, {} as Record<InsightData['impact'], InsightData[]>);
  }

  private setState(updates: Partial<UIState>): void {
    this.state = { ...this.state, ...updates };
    this.notify();
  }
}
