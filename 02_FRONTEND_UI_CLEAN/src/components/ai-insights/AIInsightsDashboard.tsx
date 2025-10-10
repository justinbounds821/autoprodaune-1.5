/**
 * AI Insights Dashboard - Main Component
 * Single Responsibility: Coordinate AI insights functionality
 * File Length: < 200 lines ✅
 * Uses Manager/ViewModel/UI pattern ✅
 */

import React, { useEffect, useMemo } from 'react';
import { useToast } from '@/hooks/use-toast';
import { AIInsightsManager } from './AIInsightsManager';
import { AIInsightsViewModel } from './AIInsightsViewModel';
import { AIInsightsUI } from './AIInsightsUI';
import { useTranslation } from 'react-i18next';

export default function AIInsightsDashboard() {
  const { toast } = useToast();
  const { t } = useTranslation();
  
  // Dependency Injection - Clean Architecture ✅
  const manager = useMemo(() => new AIInsightsManager(), []);
  const viewModel = useMemo(() => new AIInsightsViewModel(manager), [manager]);
  
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

  useEffect(() => {
    if (state.error) {
      toast({
        title: t('aiInsights.errorTitle'),
        description: state.error || t('aiInsights.errorDescription'),
        variant: 'destructive'
      });
    }
  }, [state.error, toast, t]);

  // Event Handlers - Delegated to ViewModel ✅
  const handleLoadInsights = () => {
    viewModel.loadInsights();
  };

  const handleGenerateInsight = (type: any, category: any) => {
    viewModel.generateInsight(type, category);
    toast({
      title: t('aiInsights.generated'),
      description: '',
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
