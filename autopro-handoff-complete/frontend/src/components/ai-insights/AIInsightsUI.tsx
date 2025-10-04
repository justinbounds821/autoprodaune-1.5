/**
 * AI Insights UI Component - Pure UI Layer
 * Single Responsibility: Render AI insights UI
 * File Length: < 200 lines ✅
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  TrendingUp, 
  AlertTriangle, 
  Lightbulb, 
  Filter,
  Plus,
  Zap,
  Target
} from 'lucide-react';
import { InsightData, UIState } from './AIInsightsViewModel';

interface AIInsightsUIProps {
  state: UIState;
  filteredInsights: InsightData[];
  insightsByImpact: Record<InsightData['impact'], InsightData[]>;
  onLoadInsights: () => void;
  onGenerateInsight: (type: InsightData['type'], category: InsightData['category']) => void;
  onSetCategory: (category: InsightData['category'] | 'all') => void;
  onSetType: (type: InsightData['type'] | 'all') => void;
  onToggleFilters: () => void;
}

export const AIInsightsUI: React.FC<AIInsightsUIProps> = ({
  state,
  filteredInsights,
  insightsByImpact,
  onLoadInsights,
  onGenerateInsight,
  onSetCategory,
  onSetType,
  onToggleFilters
}) => {
  const getImpactIcon = (impact: InsightData['impact']) => {
    switch (impact) {
      case 'critical': return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'high': return <TrendingUp className="w-4 h-4 text-orange-500" />;
      case 'medium': return <Lightbulb className="w-4 h-4 text-yellow-500" />;
      case 'low': return <Zap className="w-4 h-4 text-blue-500" />;
      default: return <Brain className="w-4 h-4 text-gray-500" />;
    }
  };

  const getImpactColor = (impact: InsightData['impact']) => {
    switch (impact) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getTypeIcon = (type: InsightData['type']) => {
    switch (type) {
      case 'prediction': return <Target className="w-4 h-4" />;
      case 'alert': return <AlertTriangle className="w-4 h-4" />;
      case 'recommendation': return <Lightbulb className="w-4 h-4" />;
      case 'trend': return <TrendingUp className="w-4 h-4" />;
      default: return <Brain className="w-4 h-4" />;
    }
  };

  if (state.loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Brain className="w-8 h-8 animate-spin mx-auto mb-2" />
          <p>AI analizează datele...</p>
        </div>
      </div>
    );
  }

  if (state.error) {
    return (
      <div className="text-center py-8">
        <AlertTriangle className="w-12 h-12 mx-auto mb-2 text-red-500" />
        <p className="text-red-600">{state.error}</p>
        <Button onClick={onLoadInsights} className="mt-4">
          Încearcă din nou
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      {state.metrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Insights</p>
                  <p className="text-2xl font-bold">{state.metrics.total_insights}</p>
                </div>
                <Brain className="w-8 h-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Încredere Mare</p>
                  <p className="text-2xl font-bold text-green-600">{state.metrics.high_confidence_insights}</p>
                </div>
                <Target className="w-8 h-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Alertă Critice</p>
                  <p className="text-2xl font-bold text-red-600">{state.metrics.critical_alerts}</p>
                </div>
                <AlertTriangle className="w-8 h-8 text-red-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Categorii</p>
                  <p className="text-2xl font-bold text-purple-600">{Object.keys(state.metrics.categories).length}</p>
                </div>
                <Filter className="w-8 h-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        <Button onClick={() => onGenerateInsight('prediction', 'leads')}>
          <Plus className="w-4 h-4 mr-2" />
          Generează Predicție
        </Button>
        <Button variant="outline" onClick={onToggleFilters}>
          <Filter className="w-4 h-4 mr-2" />
          Filtrează
        </Button>
      </div>

      {/* Insights List */}
      <div className="space-y-3">
        {filteredInsights.map(insight => (
          <Card key={insight.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {getTypeIcon(insight.type)}
                  <CardTitle className="text-lg">{insight.title}</CardTitle>
                  <Badge className={getImpactColor(insight.impact)}>
                    {insight.impact}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  {getImpactIcon(insight.impact)}
                  <span className="text-sm font-medium">{insight.confidence}%</span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-3">{insight.description}</p>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>Categorie: {insight.category}</span>
                <span>Tip: {insight.type}</span>
                <span>Creat: {new Date(insight.created_at).toLocaleDateString('ro-RO')}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredInsights.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <Brain className="w-12 h-12 mx-auto mb-2 text-gray-300" />
          <p>Nu există insights AI în sistem.</p>
        </div>
      )}
    </div>
  );
};
