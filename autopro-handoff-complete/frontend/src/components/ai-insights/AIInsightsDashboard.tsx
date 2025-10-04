/**
 * AI Insights Dashboard - Main Component
 * Single Responsibility: Coordinate AI insights functionality
 * File Length: < 200 lines ✅
 * Uses Manager/ViewModel/UI pattern ✅
 */

import React, { useEffect } from 'react';
import { useToast } from '@/hooks/use-toast';
import { AIInsightsManager } from './AIInsightsManager';
import { AIInsightsViewModel } from './AIInsightsViewModel';
import { AIInsightsUI } from './AIInsightsUI';

export default function AIInsightsDashboard() {
  const { toast } = useToast();
  
  // Dependency Injection - Clean Architecture ✅
  const manager = new AIInsightsManager();
  const viewModel = new AIInsightsViewModel(manager);
  
  // UI State Management
  const [state, setState] = React.useState(viewModel.getState());
  const [filteredInsights, setFilteredInsights] = React.useState(viewModel.getFilteredInsights());
  const [insightsByImpact, setInsightsByImpact] = React.useState(viewModel.getInsightsByImpact());

  // Subscribe to ViewModel changes
  useEffect(() => {
    const unsubscribe = viewModel.subscribe((newState) => {
      setState(newState);
      setFilteredInsights(viewModel.getFilteredInsights());
      setInsightsByImpact(viewModel.getInsightsByImpact());
    });

    // Load initial data
    viewModel.loadInsights();

    return unsubscribe;
  }, [viewModel]);

  // Event Handlers - Delegated to ViewModel ✅
  const handleLoadInsights = () => {
    viewModel.loadInsights();
  };

  const handleGenerateInsight = (type: any, category: any) => {
    viewModel.generateInsight(type, category);
    toast({
      title: "Insight generat",
      description: "AI a generat un insight nou pentru tine.",
    });
  };

  const handleSetCategory = (category: any) => {
    viewModel.setCategory(category);
  };

  const handleSetType = (type: any) => {
    viewModel.setType(type);
  };

  const handleToggleFilters = () => {
    viewModel.toggleFilters();
  };

  // Pure UI Component - No Business Logic ✅
  return (
    <AIInsightsUI
      state={state}
      filteredInsights={filteredInsights}
      insightsByImpact={insightsByImpact}
      onLoadInsights={handleLoadInsights}
      onGenerateInsight={handleGenerateInsight}
      onSetCategory={handleSetCategory}
      onSetType={handleSetType}
      onToggleFilters={handleToggleFilters}
    />
  );
}
