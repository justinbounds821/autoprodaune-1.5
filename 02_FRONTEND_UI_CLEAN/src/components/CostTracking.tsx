import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis } from 'recharts';
import { 
  DollarSign, 
  TrendingUp,
  PieChart,
  BarChart3
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { getFinancialBreakdown } from '@/lib/api';
import type { CostEntry } from '@/types/api';

interface CategorySummary {
  category: string;
  total: number;
  count: number;
  percentage: number;
  color: string;
}

const COLORS = [
  'bg-red-500',
  'bg-blue-500',
  'bg-green-500',
  'bg-yellow-500',
  'bg-purple-500',
  'bg-pink-500',
  'bg-indigo-500',
  'bg-gray-500'
];

export default function CostTracking() {
  const { toast } = useToast();
  const [costs, setCosts] = useState<CostEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [categorySummary, setCategorySummary] = useState<CategorySummary[]>([]);

  useEffect(() => {
    loadCosts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    calculateCategorySummary();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [costs]);

  const loadCosts = async () => {
    try {
      setLoading(true);
      const response = await getFinancialBreakdown('30d');
      
      // Map backend costs to CostEntry format
      const costEntries: CostEntry[] = response.costs?.top?.map((cost: {
        id: string;
        provider: string;
        operation: string;
        timestamp: string;
        cost: number;
      }) => ({
        id: cost.id,
        amount: cost.cost,
        category: cost.provider || 'Other',
        description: cost.operation,
        date: cost.timestamp,
        recurring: false,
        tags: [cost.provider, cost.operation],
        provider: cost.provider,
        operation: cost.operation,
        timestamp: cost.timestamp
      })) || [];

      setCosts(costEntries);
    } catch (error) {
      console.error('Failed to load costs:', error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca costurile.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const calculateCategorySummary = () => {
    const total = costs.reduce((sum, cost) => sum + cost.amount, 0);
    const categoryMap = new Map<string, { total: number; count: number }>();

    costs.forEach(cost => {
      const existing = categoryMap.get(cost.category) || { total: 0, count: 0 };
      categoryMap.set(cost.category, {
        total: existing.total + cost.amount,
        count: existing.count + 1
      });
    });

    const summary = Array.from(categoryMap.entries()).map(([category, data], index) => ({
      category,
      total: data.total,
      count: data.count,
      percentage: total > 0 ? (data.total / total) * 100 : 0,
      color: COLORS[index % COLORS.length]
    })).sort((a, b) => b.total - a.total);

    setCategorySummary(summary);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ro-RO', {
      style: 'currency',
      currency: 'RON'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ro-RO');
  };

  const totalCosts = costs.reduce((sum, cost) => sum + cost.amount, 0);
  const monthlyRecurring = costs
    .filter(cost => cost.recurring)
    .reduce((sum, cost) => sum + cost.amount, 0);

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Costuri</p>
                <p className="text-2xl font-bold text-red-600">
                  {formatCurrency(totalCosts)}
                </p>
              </div>
              <DollarSign className="w-8 h-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Recurring Lunar</p>
                <p className="text-2xl font-bold text-blue-600">
                  {formatCurrency(monthlyRecurring)}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Categorii Active</p>
                <p className="text-2xl font-bold text-green-600">
                  {categorySummary.length}
                </p>
              </div>
              <PieChart className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Cost Distribution Chart */}
      {categorySummary.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Distribuția Costurilor pe Categorii
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={{
              total: {
                label: "Costuri",
                color: "hsl(var(--chart-1))",
              },
            }} className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categorySummary}>
                  <XAxis 
                    dataKey="category" 
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis hide />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar 
                    dataKey="total" 
                    fill="var(--color-total)"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>
      )}

      {/* Category Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Breakdown pe Categorii</CardTitle>
        </CardHeader>
        <CardContent>
          {categorySummary.length > 0 ? (
            <div className="space-y-3">
              {categorySummary.map((item) => (
                <div key={item.category} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded-full ${item.color}`} />
                    <div>
                      <p className="font-medium">{item.category}</p>
                      <p className="text-sm text-gray-500">{item.count} costuri</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">{formatCurrency(item.total)}</p>
                    <p className="text-sm text-gray-500">{item.percentage.toFixed(1)}%</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <DollarSign className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>Nu există breakdown disponibil.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Costs List */}
      <Card>
        <CardHeader>
          <CardTitle>Costuri Recente (Read-Only)</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Se încarcă...</div>
          ) : costs.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <DollarSign className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>Nu există costuri înregistrate.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {costs.map(cost => (
                <div key={cost.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="outline">{cost.category}</Badge>
                      {cost.recurring && (
                        <Badge variant="secondary">Recurring</Badge>
                      )}
                    </div>
                    <p className="font-medium">{cost.description}</p>
                    <p className="text-sm text-gray-500">{formatDate(cost.date)}</p>
                    {cost.tags && cost.tags.length > 0 && (
                      <div className="flex gap-1 mt-1">
                        {cost.tags.map(tag => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <p className="text-lg font-bold text-red-600">
                      {formatCurrency(cost.amount)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
