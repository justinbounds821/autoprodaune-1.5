import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis } from 'recharts';
import { 
  DollarSign, 
  Plus, 
  Edit, 
  Trash2, 
  TrendingUp, 
  TrendingDown,
  PieChart,
  BarChart3
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface CostEntry {
  id: string;
  amount: number;
  category: string;
  description: string;
  date: string;
  recurring: boolean;
  tags: string[];
}

interface CategorySummary {
  category: string;
  total: number;
  count: number;
  percentage: number;
  color: string;
}

const COST_CATEGORIES = [
  'Marketing',
  'Development',
  'Infrastructure',
  'Personnel',
  'Software',
  'Hardware',
  'Travel',
  'Other'
];

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
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [editingCost, setEditingCost] = useState<CostEntry | null>(null);
  const [categorySummary, setCategorySummary] = useState<CategorySummary[]>([]);

  // Form state
  const [formData, setFormData] = useState({
    amount: '',
    category: '',
    description: '',
    date: new Date().toISOString().split('T')[0],
    recurring: false,
    tags: ''
  });

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
      // Simulated data - în producție ar fi API call
      const mockCosts: CostEntry[] = [
        {
          id: '1',
          amount: 1500,
          category: 'Marketing',
          description: 'Google Ads campaign',
          date: '2025-01-01',
          recurring: false,
          tags: ['ads', 'google']
        },
        {
          id: '2',
          amount: 800,
          category: 'Software',
          description: 'Supabase Pro subscription',
          date: '2025-01-01',
          recurring: true,
          tags: ['subscription', 'database']
        },
        {
          id: '3',
          amount: 200,
          category: 'Development',
          description: 'API keys and services',
          date: '2025-01-02',
          recurring: false,
          tags: ['api', 'external']
        }
      ];
      setCosts(mockCosts);
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
    const summary = COST_CATEGORIES.map((category, index) => {
      const categoryCosts = costs.filter(cost => cost.category === category);
      const categoryTotal = categoryCosts.reduce((sum, cost) => sum + cost.amount, 0);
      
      return {
        category,
        total: categoryTotal,
        count: categoryCosts.length,
        percentage: total > 0 ? (categoryTotal / total) * 100 : 0,
        color: COLORS[index]
      };
    }).filter(item => item.total > 0);

    setCategorySummary(summary);
  };

  const handleAddCost = async () => {
    try {
      const newCost: CostEntry = {
        id: Date.now().toString(),
        amount: parseFloat(formData.amount),
        category: formData.category,
        description: formData.description,
        date: formData.date,
        recurring: formData.recurring,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(Boolean)
      };

      setCosts(prev => [...prev, newCost]);
      
      toast({
        title: "Cost adăugat",
        description: `Cost de ${formData.amount} LEI adăugat cu succes.`,
      });

      setFormData({
        amount: '',
        category: '',
        description: '',
        date: new Date().toISOString().split('T')[0],
        recurring: false,
        tags: ''
      });
      setIsAddDialogOpen(false);

    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut adăuga costul.",
        variant: "destructive",
      });
    }
  };

  const handleEditCost = async (cost: CostEntry) => {
    // Implementation for edit
    setEditingCost(cost);
    setFormData({
      amount: cost.amount.toString(),
      category: cost.category,
      description: cost.description,
      date: cost.date,
      recurring: cost.recurring,
      tags: cost.tags.join(', ')
    });
    setIsAddDialogOpen(true);
  };

  const handleDeleteCost = async (id: string) => {
    try {
      setCosts(prev => prev.filter(cost => cost.id !== id));
      toast({
        title: "Cost șters",
        description: "Costul a fost șters cu succes.",
      });
    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut șterge costul.",
        variant: "destructive",
      });
    }
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
          <div className="space-y-3">
            {categorySummary.map((item, index) => (
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
        </CardContent>
      </Card>

      {/* Add Cost Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogTrigger asChild>
          <Button className="w-full">
            <Plus className="w-4 h-4 mr-2" />
            Adaugă Cost Nou
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingCost ? 'Editează Cost' : 'Adaugă Cost Nou'}
            </DialogTitle>
            <DialogDescription>
              Adaugă un nou cost în sistemul de tracking.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Sumă (LEI)</label>
              <Input
                type="number"
                value={formData.amount}
                onChange={(e) => setFormData(prev => ({ ...prev, amount: e.target.value }))}
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Categorie</label>
              <Select
                value={formData.category}
                onValueChange={(value) => setFormData(prev => ({ ...prev, category: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selectează categoria" />
                </SelectTrigger>
                <SelectContent>
                  {COST_CATEGORIES.map(category => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Descriere</label>
              <Textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Descriere cost..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Data</label>
              <Input
                type="date"
                value={formData.date}
                onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Tags (separate prin virgulă)</label>
              <Input
                value={formData.tags}
                onChange={(e) => setFormData(prev => ({ ...prev, tags: e.target.value }))}
                placeholder="ads, marketing, subscription"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsAddDialogOpen(false)}
            >
              Anulează
            </Button>
            <Button
              onClick={handleAddCost}
              disabled={!formData.amount || !formData.category}
            >
              {editingCost ? 'Actualizează' : 'Adaugă'} Cost
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Recent Costs List */}
      <Card>
        <CardHeader>
          <CardTitle>Costuri Recente</CardTitle>
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
                    {cost.tags.length > 0 && (
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
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEditCost(cost)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteCost(cost.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
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
