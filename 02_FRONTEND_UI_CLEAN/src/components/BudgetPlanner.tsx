import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Target, 
  DollarSign,
  TrendingUp,
  TrendingDown,
  BarChart3,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { getFinancialBreakdown, getFinancialCostCategories } from '@/lib/api';
import type { BudgetPlan } from '@/types/api';

interface BudgetCategory {
  id: string;
  name: string;
  description: string;
  budget_amount: number;
  spent_amount: number;
  period: 'monthly' | 'quarterly' | 'yearly';
  color: string;
  alerts: {
    warning_threshold: number;
    critical_threshold: number;
  };
}

const CATEGORY_COLORS = [
  '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
  '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6366F1'
];

export default function BudgetPlanner() {
  const { toast } = useToast();
  const [budgetPlans, setBudgetPlans] = useState<BudgetPlan[]>([]);
  const [categories, setCategories] = useState<BudgetCategory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBudgetPlans();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadBudgetPlans = async () => {
    try {
      setLoading(true);
      
      // Load data from multiple endpoints
      const [financialData, categoriesData] = await Promise.allSettled([
        getFinancialBreakdown('30d'),
        getFinancialCostCategories()
      ]);

      const financial = financialData.status === 'fulfilled' ? financialData.value : null;
      const categoriesResult = categoriesData.status === 'fulfilled' ? categoriesData.value : null;

      // Map categories from backend
      const mappedCategories: BudgetCategory[] = categoriesResult?.categories?.map((cat: {
        id: string;
        name: string;
        description: string;
        budget_amount: number;
        spent_amount: number;
        period: 'monthly' | 'quarterly' | 'yearly';
        alerts: { warning_threshold: number; critical_threshold: number };
      }, index: number) => ({
        ...cat,
        color: CATEGORY_COLORS[index % CATEGORY_COLORS.length]
      })) || [];

      setCategories(mappedCategories);

      // Build a single plan from the data (view-only)
      if (financial || mappedCategories.length > 0) {
        const plan: BudgetPlan = {
          id: '1',
          name: 'Plan Curent',
          description: 'Planul de buget consolidat din datele sistemului',
          total_budget: mappedCategories.reduce((sum, cat) => sum + cat.budget_amount, 0),
          period: 'monthly',
          start_date: financial?.start_date || new Date().toISOString(),
          end_date: financial?.end_date || new Date().toISOString(),
          status: 'active',
          categories: mappedCategories,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        setBudgetPlans([plan]);
      }
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

<<<<<<< Current (Your changes)
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

  const updateCategory = (index: number, field: keyof BudgetCategory, value: string | number) => {
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

=======
>>>>>>> Incoming (Background Agent changes)
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

  const handleCreateDisabled = () => {
    toast({
      title: "Funcție neimplementată",
      description: "Crearea de planuri de buget nu este implementată în backend.",
      variant: "default",
    });
  };

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

      {/* Create Budget Plan Button (Disabled) */}
      <Button 
        className="w-full" 
        disabled 
        onClick={handleCreateDisabled}
        title="Funcție neimplementată în backend"
      >
        Creează Plan de Buget Nou (Neimplementat)
      </Button>

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
                    {plan.categories.length > 0 ? (
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
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        Nu există categorii în acest plan.
                      </div>
                    )}
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
