import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { 
  Target, 
  Plus, 
  Edit, 
  Trash2, 
  TrendingUp,
  TrendingDown,
  DollarSign,
  Calendar,
  AlertTriangle,
  CheckCircle,
  BarChart3
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface BudgetCategory {
  id: string;
  name: string;
  description: string;
  budget_amount: number;
  spent_amount: number;
  period: 'monthly' | 'quarterly' | 'yearly';
  color: string;
  alerts: {
    warning_threshold: number; // percentage
    critical_threshold: number; // percentage
  };
}

interface BudgetPlan {
  id: string;
  name: string;
  description: string;
  total_budget: number;
  period: 'monthly' | 'quarterly' | 'yearly';
  start_date: string;
  end_date: string;
  status: 'draft' | 'active' | 'completed' | 'paused';
  categories: BudgetCategory[];
  created_at: string;
  updated_at: string;
}

const BUDGET_PERIODS = [
  { value: 'monthly', label: 'Lunar' },
  { value: 'quarterly', label: 'Trimestrial' },
  { value: 'yearly', label: 'Anual' }
];

const CATEGORY_COLORS = [
  '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
  '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6366F1'
];

const DEFAULT_CATEGORIES = [
  { name: 'Marketing', description: 'Cheltuieli cu publicitate și promovare', budget_amount: 5000 },
  { name: 'Dezvoltare', description: 'Salarii dezvoltatori și infrastructură', budget_amount: 15000 },
  { name: 'Oficiu', description: 'Chirie, utilități, echipamente', budget_amount: 3000 },
  { name: 'Consultanță', description: 'Servicii externe și consultanți', budget_amount: 2000 },
  { name: 'Echipamente', description: 'Hardware, software, licențe', budget_amount: 4000 },
  { name: 'Deplasări', description: 'Transport și cazare', budget_amount: 1000 }
];

export default function BudgetPlanner() {
  const { toast } = useToast();
  const [budgetPlans, setBudgetPlans] = useState<BudgetPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingPlan, setEditingPlan] = useState<BudgetPlan | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    total_budget: '',
    period: 'monthly' as BudgetPlan['period'],
    start_date: '',
    end_date: ''
  });

  const [categories, setCategories] = useState<Omit<BudgetCategory, 'id'>[]>([]);

  useEffect(() => {
    loadBudgetPlans();
  }, []);

  const loadBudgetPlans = async () => {
    try {
      setLoading(true);
      // Simulated data - în producție ar fi API call
      const mockPlans: BudgetPlan[] = [
        {
          id: '1',
          name: 'Buget Q1 2025',
          description: 'Bugetul pentru primul trimestru al anului 2025',
          total_budget: 30000,
          period: 'quarterly',
          start_date: '2025-01-01',
          end_date: '2025-03-31',
          status: 'active',
          categories: [
            {
              id: '1',
              name: 'Marketing',
              description: 'Cheltuieli cu publicitate și promovare',
              budget_amount: 5000,
              spent_amount: 3200,
              period: 'quarterly',
              color: '#3B82F6',
              alerts: { warning_threshold: 70, critical_threshold: 90 }
            },
            {
              id: '2',
              name: 'Dezvoltare',
              description: 'Salarii dezvoltatori și infrastructură',
              budget_amount: 15000,
              spent_amount: 11200,
              period: 'quarterly',
              color: '#10B981',
              alerts: { warning_threshold: 70, critical_threshold: 90 }
            },
            {
              id: '3',
              name: 'Oficiu',
              description: 'Chirie, utilități, echipamente',
              budget_amount: 3000,
              spent_amount: 2800,
              period: 'quarterly',
              color: '#F59E0B',
              alerts: { warning_threshold: 70, critical_threshold: 90 }
            }
          ],
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-15T10:30:00Z'
        }
      ];
      setBudgetPlans(mockPlans);
    } catch (error) {
      console.error('Failed to load budget plans:', error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca planurile de buget.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const addDefaultCategories = () => {
    const newCategories = DEFAULT_CATEGORIES.map((cat, index) => ({
      name: cat.name,
      description: cat.description,
      budget_amount: cat.budget_amount,
      spent_amount: 0,
      period: formData.period,
      color: CATEGORY_COLORS[index % CATEGORY_COLORS.length],
      alerts: { warning_threshold: 70, critical_threshold: 90 }
    }));
    setCategories(newCategories);
  };

  const addCategory = () => {
    const newCategory: Omit<BudgetCategory, 'id'> = {
      name: '',
      description: '',
      budget_amount: 0,
      spent_amount: 0,
      period: formData.period,
      color: CATEGORY_COLORS[categories.length % CATEGORY_COLORS.length],
      alerts: { warning_threshold: 70, critical_threshold: 90 }
    };
    setCategories(prev => [...prev, newCategory]);
  };

  const updateCategory = (index: number, field: keyof BudgetCategory, value: any) => {
    setCategories(prev => prev.map((cat, i) => 
      i === index ? { ...cat, [field]: value } : cat
    ));
  };

  const removeCategory = (index: number) => {
    setCategories(prev => prev.filter((_, i) => i !== index));
  };

  const calculateTotalBudget = () => {
    return categories.reduce((sum, cat) => sum + cat.budget_amount, 0);
  };

  const calculateTotalSpent = () => {
    return categories.reduce((sum, cat) => sum + cat.spent_amount, 0);
  };

  const handleCreateBudgetPlan = async () => {
    if (categories.length === 0) {
      toast({
        title: "Lipsesc categoriile",
        description: "Adaugă cel puțin o categorie în buget.",
        variant: "destructive",
      });
      return;
    }

    try {
      const totalBudget = calculateTotalBudget();
      const newPlan: BudgetPlan = {
        id: Date.now().toString(),
        name: formData.name,
        description: formData.description,
        total_budget: totalBudget,
        period: formData.period,
        start_date: formData.start_date,
        end_date: formData.end_date,
        status: 'draft',
        categories: categories.map((cat, index) => ({
          ...cat,
          id: `${Date.now()}_${index}`
        })),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      setBudgetPlans(prev => [newPlan, ...prev]);
      
      toast({
        title: "Plan de buget creat",
        description: `Planul "${newPlan.name}" a fost creat cu succes.`,
      });

      // Reset form
      setFormData({
        name: '',
        description: '',
        total_budget: '',
        period: 'monthly',
        start_date: '',
        end_date: ''
      });
      setCategories([]);
      setIsCreateDialogOpen(false);

    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut crea planul de buget.",
        variant: "destructive",
      });
    }
  };

  const getStatusColor = (status: BudgetPlan['status']) => {
    switch (status) {
      case 'draft': return 'bg-gray-500';
      case 'active': return 'bg-green-500';
      case 'completed': return 'bg-blue-500';
      case 'paused': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: BudgetPlan['status']) => {
    switch (status) {
      case 'draft': return 'Ciornă';
      case 'active': return 'Activ';
      case 'completed': return 'Completat';
      case 'paused': return 'Pausat';
      default: return status;
    }
  };

  const getCategoryStatus = (category: BudgetCategory) => {
    const percentage = (category.spent_amount / category.budget_amount) * 100;
    if (percentage >= category.alerts.critical_threshold) {
      return { status: 'critical', color: 'bg-red-500', icon: AlertTriangle };
    } else if (percentage >= category.alerts.warning_threshold) {
      return { status: 'warning', color: 'bg-yellow-500', icon: AlertTriangle };
    } else {
      return { status: 'good', color: 'bg-green-500', icon: CheckCircle };
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

  const totalBudget = calculateTotalBudget();
  const totalSpent = calculateTotalSpent();

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Planuri Active</p>
                <p className="text-2xl font-bold">
                  {budgetPlans.filter(plan => plan.status === 'active').length}
                </p>
              </div>
              <Target className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Buget Total</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrency(budgetPlans.reduce((sum, plan) => sum + plan.total_budget, 0))}
                </p>
              </div>
              <DollarSign className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Cheltuit</p>
                <p className="text-2xl font-bold text-orange-600">
                  {formatCurrency(budgetPlans.reduce((sum, plan) => 
                    sum + plan.categories.reduce((catSum, cat) => catSum + cat.spent_amount, 0), 0
                  ))}
                </p>
              </div>
              <TrendingDown className="w-8 h-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Disponibil</p>
                <p className="text-2xl font-bold text-blue-600">
                  {formatCurrency(budgetPlans.reduce((sum, plan) => 
                    sum + plan.total_budget - plan.categories.reduce((catSum, cat) => catSum + cat.spent_amount, 0), 0
                  ))}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Create Budget Plan Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogTrigger asChild>
          <Button className="w-full">
            <Plus className="w-4 h-4 mr-2" />
            Creează Plan de Buget Nou
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Creează Plan de Buget Nou</DialogTitle>
            <DialogDescription>
              Planifică bugetul pentru perioada selectată cu categorii detaliate.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Nume Plan</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="ex: Buget Q1 2025"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Perioada</label>
                <Select
                  value={formData.period}
                  onValueChange={(value: BudgetPlan['period']) => 
                    setFormData(prev => ({ ...prev, period: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {BUDGET_PERIODS.map(period => (
                      <SelectItem key={period.value} value={period.value}>
                        {period.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Descriere</label>
              <Input
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Descrierea planului de buget..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Data Început</label>
                <Input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData(prev => ({ ...prev, start_date: e.target.value }))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Data Sfârșit</label>
                <Input
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData(prev => ({ ...prev, end_date: e.target.value }))}
                />
              </div>
            </div>

            {/* Categories */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Categorii Buget</h3>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={addDefaultCategories}>
                    Categorii Default
                  </Button>
                  <Button variant="outline" size="sm" onClick={addCategory}>
                    <Plus className="w-4 h-4 mr-2" />
                    Adaugă Categorie
                  </Button>
                </div>
              </div>

              <div className="space-y-3">
                {categories.map((category, index) => (
                  <div key={index} className="grid grid-cols-12 gap-2 p-3 border rounded-lg">
                    <div className="col-span-3">
                      <Input
                        value={category.name}
                        onChange={(e) => updateCategory(index, 'name', e.target.value)}
                        placeholder="Nume categorie"
                      />
                    </div>
                    <div className="col-span-4">
                      <Input
                        value={category.description}
                        onChange={(e) => updateCategory(index, 'description', e.target.value)}
                        placeholder="Descriere"
                      />
                    </div>
                    <div className="col-span-2">
                      <Input
                        type="number"
                        value={category.budget_amount}
                        onChange={(e) => updateCategory(index, 'budget_amount', parseFloat(e.target.value) || 0)}
                        placeholder="Buget"
                      />
                    </div>
                    <div className="col-span-2">
                      <Input
                        type="number"
                        value={category.spent_amount}
                        onChange={(e) => updateCategory(index, 'spent_amount', parseFloat(e.target.value) || 0)}
                        placeholder="Cheltuit"
                      />
                    </div>
                    <div className="col-span-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeCategory(index)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Totals */}
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex justify-between text-sm mb-2">
                  <span>Total Buget:</span>
                  <span className="font-bold">{formatCurrency(totalBudget)}</span>
                </div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Total Cheltuit:</span>
                  <span className="font-bold">{formatCurrency(totalSpent)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold pt-2 border-t">
                  <span>Disponibil:</span>
                  <span className={totalBudget - totalSpent >= 0 ? 'text-green-600' : 'text-red-600'}>
                    {formatCurrency(totalBudget - totalSpent)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsCreateDialogOpen(false)}
            >
              Anulează
            </Button>
            <Button
              onClick={handleCreateBudgetPlan}
              disabled={!formData.name || categories.length === 0}
            >
              Creează Plan de Buget
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Budget Plans List */}
      <Tabs defaultValue="plans" className="w-full">
        <TabsList>
          <TabsTrigger value="plans">Planuri de Buget</TabsTrigger>
          <TabsTrigger value="analytics">Analize</TabsTrigger>
        </TabsList>

        <TabsContent value="plans" className="space-y-4">
          {loading ? (
            <div className="text-center py-8">Se încarcă...</div>
          ) : budgetPlans.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Target className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>Nu există planuri de buget în sistem.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {budgetPlans.map(plan => (
                <Card key={plan.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="flex items-center gap-2">
                          {plan.name}
                          <Badge className={getStatusColor(plan.status)}>
                            {getStatusText(plan.status)}
                          </Badge>
                        </CardTitle>
                        <p className="text-sm text-gray-600 mt-1">{plan.description}</p>
                        <p className="text-xs text-gray-500">
                          {formatDate(plan.start_date)} - {formatDate(plan.end_date)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold">{formatCurrency(plan.total_budget)}</p>
                        <p className="text-sm text-gray-500">Buget total</p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {plan.categories.map(category => {
                        const percentage = (category.spent_amount / category.budget_amount) * 100;
                        const statusInfo = getCategoryStatus(category);
                        const StatusIcon = statusInfo.icon;
                        
                        return (
                          <div key={category.id} className="flex items-center justify-between p-3 border rounded-lg">
                            <div className="flex items-center gap-3">
                              <div 
                                className="w-4 h-4 rounded-full"
                                style={{ backgroundColor: category.color }}
                              />
                              <div>
                                <h4 className="font-medium">{category.name}</h4>
                                <p className="text-sm text-gray-600">{category.description}</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="flex items-center gap-2">
                                <StatusIcon className="w-4 h-4" />
                                <span className="text-sm font-medium">
                                  {formatCurrency(category.spent_amount)} / {formatCurrency(category.budget_amount)}
                                </span>
                              </div>
                              <div className="w-32 bg-gray-200 rounded-full h-2 mt-1">
                                <div 
                                  className={`h-2 rounded-full ${statusInfo.color}`}
                                  style={{ width: `${Math.min(percentage, 100)}%` }}
                                />
                              </div>
                              <p className="text-xs text-gray-500 mt-1">
                                {percentage.toFixed(1)}% utilizat
                              </p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Analize Buget
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <BarChart3 className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>Analizele detaliate vor fi disponibile în versiunea următoare.</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
