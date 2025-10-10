import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  Target,
  PieChart as PieChartIcon,
  BarChart3,
  Download,
  RefreshCw,
  Calendar,
  Calculator,
  FileText,
  LineChart as LineChartIcon,
  Layers,
} from 'lucide-react';
import AutoProApiService from '@/services/autoproApi';
import {
  FinancialData,
  Revenue,
  Cost,
  FinancialBreakdown,
  FinancialForecast,
  FinancialTimelinePoint,
  CostCategory,
} from '@/types/admin';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import {
  Bar,
  BarChart,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Cell,
} from 'recharts';
import { useToast } from '@/hooks/use-toast';
import { RecurringRevenueManager, MRRReport } from '@/components/recurring-revenue/RecurringRevenueManager';

const FinancialDashboard: React.FC = () => {
  const { toast } = useToast();
  const [financialData, setFinancialData] = useState<FinancialData | null>(null);
  const [revenueData, setRevenueData] = useState<Revenue[]>([]);
  const [costData, setCostData] = useState<Cost[]>([]);
  const [breakdownData, setBreakdownData] = useState<FinancialBreakdown | null>(null);
  const [forecastData, setForecastData] = useState<FinancialForecast | null>(null);
  const [profitLossData, setProfitLossData] = useState<any>(null);
  const [costCategories, setCostCategories] = useState<CostCategory[]>([]);
  const [newCategory, setNewCategory] = useState({
    name: '',
    description: '',
    budget_cap: '',
    color: '#2563eb',
  });
  const [mrrReport, setMrrReport] = useState<MRRReport | null>(null);
  const recurringManager = useMemo(() => new RecurringRevenueManager(), []);
  const [taxSummary, setTaxSummary] = useState({
    vat: 0,
    corporate: 0,
    profitAfterTax: 0,
  });
  const [invoiceExportId, setInvoiceExportId] = useState('');
  const [invoiceExportFormat, setInvoiceExportFormat] = useState<'pdf' | 'json'>('pdf');
  const [isSavingCategory, setIsSavingCategory] = useState(false);
  const [isExportingInvoice, setIsExportingInvoice] = useState(false);
  const [loading, setLoading] = useState(true);

  // Date range state
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [selectedPreset, setSelectedPreset] = useState('7d');

  useEffect(() => {
    loadAllData();
  }, [selectedPreset, dateFrom, dateTo]);

  useEffect(() => {
    recurringManager
      .loadSubscriptions()
      .then(() => setMrrReport(recurringManager.generateMRRReport(selectedPreset.toUpperCase())))
      .catch((error) => console.error('Failed to load subscriptions:', error));
  }, [recurringManager, selectedPreset]);

  useEffect(() => {
    if (!financialData) {
      setTaxSummary({ vat: 0, corporate: 0, profitAfterTax: 0 });
      return;
    }

    const revenue = financialData.total_revenue ?? financialData.revenue ?? 0;
    const costs = financialData.total_costs ?? financialData.costs ?? 0;
    const profit = financialData.net_profit ?? financialData.profit ?? 0;
    const vatDue = Math.max((revenue - costs) * 0.19, 0);
    const corporateTax = profit > 0 ? profit * 0.16 : 0;
    setTaxSummary({
      vat: Math.round(vatDue * 100) / 100,
      corporate: Math.round(corporateTax * 100) / 100,
      profitAfterTax: Math.round((profit - vatDue - corporateTax) * 100) / 100,
    });
  }, [financialData]);

  const loadFinancialData = async () => {
    try {
      const params = new URLSearchParams();
      if (dateFrom && dateTo) {
        params.append('date_from', dateFrom);
        params.append('date_to', dateTo);
        params.append('period', 'custom');
      } else {
        params.append('period', selectedPreset);
      }

      const response = await fetch(`/api/financial/dashboard?${params.toString()}`);
      const data = await response.json();

      if (response.ok && data) {
        setFinancialData({
          revenue: data.total_revenue || 0,
          costs: data.total_costs || 0,
          profit: data.net_profit || 0,
          roi: data.roi_percentage || 0,
          referralRewards: data.referral_rewards || 0,
          period: data.period || selectedPreset,
          total_revenue: data.total_revenue || 0,
          total_costs: data.total_costs || 0,
          net_profit: data.net_profit || 0,
          roi_percentage: data.roi_percentage || 0,
          start_date: data.start_date,
          end_date: data.end_date
        });
      } else {
        toast({
          title: "Eroare",
          description: "Nu s-au putut încărca datele financiare.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Failed to load financial data:', error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca datele financiare.",
        variant: "destructive",
      });
    }
  };

  const loadRevenueData = async () => {
    try {
      const response = await AutoProApiService.getRevenueData();

      if (response.success && response.data) {
        setRevenueData(response.data);
      } else {
        console.error('Failed to load revenue data:', response.error);
      }
    } catch (error) {
      console.error('Failed to load revenue data:', error);
    }
  };

  const loadCostData = async () => {
    try {
      const response = await AutoProApiService.getCostData();

      if (response.success && response.data) {
        setCostData(response.data);
      } else {
        console.error('Failed to load cost data:', response.error);
      }
    } catch (error) {
      console.error('Failed to load cost data:', error);
    }
  };

  const buildPeriodParams = () => {
    const params: Record<string, string> = {};
    if (dateFrom && dateTo) {
      params.date_from = dateFrom;
      params.date_to = dateTo;
      params.period = 'custom';
    } else {
      params.period = selectedPreset;
    }
    return params;
  };

  const loadBreakdownData = async () => {
    try {
      const response = await AutoProApiService.getFinancialBreakdown(buildPeriodParams());
      setBreakdownData(response);
    } catch (error) {
      console.error('Failed to load breakdown data:', error);
    }
  };

  const loadForecastData = async () => {
    try {
      const response = await AutoProApiService.getFinancialForecast(buildPeriodParams());
      setForecastData(response);
    } catch (error) {
      console.error('Failed to load forecast data:', error);
    }
  };

  const loadProfitLossData = async () => {
    try {
      const params: Record<string, string> = {};
      if (dateFrom && dateTo) {
        params.start_date = dateFrom;
        params.end_date = dateTo;
      } else {
        const now = new Date();
        const start = new Date();
        const presetDays = selectedPreset.endsWith('d') ? parseInt(selectedPreset.replace('d', ''), 10) : 30;
        start.setDate(now.getDate() - (isNaN(presetDays) ? 30 : presetDays));
        params.start_date = start.toISOString().split('T')[0];
        params.end_date = now.toISOString().split('T')[0];
      }
      const response = await AutoProApiService.getProfitLoss(params);
      setProfitLossData(response);
    } catch (error) {
      console.error('Failed to load profit/loss data:', error);
    }
  };

  const loadCostCategoryData = async () => {
    try {
      const response = await AutoProApiService.listCostCategories();
      setCostCategories(response);
    } catch (error) {
      console.error('Failed to load cost categories:', error);
    }
  };

  const loadAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadFinancialData(),
        loadRevenueData(),
        loadCostData(),
        loadBreakdownData(),
        loadForecastData(),
        loadProfitLossData(),
        loadCostCategoryData(),
      ]);
    } finally {
      setLoading(false);
    }
  };

  const refreshAllData = async () => {
    await loadAllData();
  };

  const handleCreateCategory = async () => {
    if (!newCategory.name.trim()) {
      toast({
        title: 'Completează numele categoriei',
        description: 'Numele categoriei este obligatoriu pentru salvare.',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsSavingCategory(true);
      const payload: any = {
        name: newCategory.name,
        description: newCategory.description || undefined,
        color: newCategory.color || undefined,
      };
      if (newCategory.budget_cap) {
        payload.budget_cap = parseFloat(newCategory.budget_cap);
      }

      const response = await AutoProApiService.createCostCategory(payload);
      setCostCategories((prev) => [response, ...prev.filter((cat) => cat.slug !== response.slug)]);
      setNewCategory({ name: '', description: '', budget_cap: '', color: '#2563eb' });
      toast({ title: 'Categorie salvată', description: `Categoria ${response.name} a fost creată.` });
    } catch (error) {
      console.error('Failed to save category:', error);
      toast({
        title: 'Eroare',
        description: 'Nu s-a putut salva categoria.',
        variant: 'destructive',
      });
    } finally {
      setIsSavingCategory(false);
    }
  };

  const handleDeleteCategory = async (slug: string, isDefault?: boolean) => {
    if (isDefault) {
      toast({
        title: 'Categorie implicită',
        description: 'Categoriile implicite nu pot fi șterse.',
      });
      return;
    }

    try {
      await AutoProApiService.deleteCostCategory(slug);
      setCostCategories((prev) => prev.filter((cat) => cat.slug !== slug));
      toast({ title: 'Categorie ștearsă', description: 'Categoria a fost eliminată.' });
    } catch (error) {
      console.error('Failed to delete category:', error);
      toast({
        title: 'Eroare',
        description: 'Nu s-a putut șterge categoria.',
        variant: 'destructive',
      });
    }
  };

  const handleInvoiceExport = async () => {
    if (!invoiceExportId.trim()) {
      toast({
        title: 'ID factură necesar',
        description: 'Introduceți un ID de factură valid pentru export.',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsExportingInvoice(true);
      const blob = await AutoProApiService.exportInvoice(invoiceExportId, invoiceExportFormat);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `invoice-${invoiceExportId}.${invoiceExportFormat}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast({ title: 'Factură exportată', description: `Factura ${invoiceExportId} a fost descărcată.` });
    } catch (error) {
      console.error('Failed to export invoice:', error);
      toast({
        title: 'Eroare',
        description: 'Nu s-a putut exporta factura.',
        variant: 'destructive',
      });
    } finally {
      setIsExportingInvoice(false);
    }
  };

  const exportFinancialReport = async () => {
    try {
      const response = await fetch('/api/financial/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          period: selectedPreset,
          format: 'csv'
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `financial-report-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        toast({
          title: "Raport exportat!",
          description: "Raportul financiar a fost descărcat cu succes.",
        });
      } else {
        throw new Error('Export failed');
      }
    } catch (error) {
      console.error('Failed to export financial report:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut exporta raportul financiar.",
        variant: "destructive",
      });
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ro-RO', {
      style: 'currency',
      currency: 'RON',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('ro-RO', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const getRoiColor = (roi: number) => {
    if (roi >= 50) return 'text-green-600';
    if (roi >= 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRoiStatus = (roi: number) => {
    if (roi >= 50) return { color: 'bg-green-500', text: 'Excelent' };
    if (roi >= 20) return { color: 'bg-yellow-500', text: 'Bun' };
    return { color: 'bg-red-500', text: 'Slab' };
  };

  const handlePresetChange = (preset: string) => {
    setSelectedPreset(preset);
    setDateFrom('');
    setDateTo('');
  };

  const handleCustomDateApply = () => {
    if (dateFrom && dateTo) {
      setSelectedPreset('custom');
    } else {
      toast({
        title: "Eroare",
        description: "Selectează ambele date (început și sfârșit).",
        variant: "destructive",
      });
    }
  };

  const getPresetLabel = () => {
    const labels: Record<string, string> = {
      'today': 'Azi',
      '7d': 'Ultimele 7 zile',
      '30d': 'Ultimele 30 zile',
      'mtd': 'Luna curentă',
      'ytd': 'Anul curent',
      'custom': 'Personalizat'
    };
    return labels[selectedPreset] || 'Selectează perioadă';
  };

  // Calculate cost breakdown for demonstration
  const getCostBreakdown = () => {
    if (!financialData || !financialData.costs) return [];

    const total = financialData.costs;
    return [
      { category: 'API și Servicii AI', amount: total * 0.45, percentage: 45 },
      { category: 'Marketing Digital', amount: total * 0.25, percentage: 25 },
      { category: 'Infrastructură', amount: total * 0.15, percentage: 15 },
      { category: 'Recompense Referral', amount: financialData.referralRewards || total * 0.10, percentage: 10 },
      { category: 'Altele', amount: total * 0.05, percentage: 5 }
    ];
  };

  const costBreakdown = getCostBreakdown();
  const timelineData: FinancialTimelinePoint[] = useMemo(() => breakdownData?.timeline ?? [], [breakdownData]);
  const costCategoryEntries = useMemo(() => Object.entries(breakdownData?.costs?.by_category ?? {}), [breakdownData]);
  const revenueCategoryEntries = useMemo(() => Object.entries(breakdownData?.revenue?.by_category ?? {}), [breakdownData]);
  const forecastSeries = useMemo(() => forecastData?.series ?? [], [forecastData]);
  const categoryPalette = ['#2563eb', '#f97316', '#16a34a', '#9333ea', '#0ea5e9', '#facc15'];

  if (loading) {
    return (
      <div className="container mx-auto p-6 flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Se încarcă datele financiare...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Financial Dashboard</h1>
          {financialData?.start_date && financialData?.end_date && (
            <p className="text-sm text-muted-foreground mt-1">
              Perioada: {formatDate(financialData.start_date)} - {formatDate(financialData.end_date)}
            </p>
          )}
        </div>
        <div className="flex gap-2 items-center flex-wrap">
          {/* Preset Buttons */}
          <div className="flex gap-1">
            <Button 
              size="sm"
              variant={selectedPreset === 'today' ? 'default' : 'outline'}
              onClick={() => handlePresetChange('today')}
            >
              Azi
            </Button>
            <Button 
              size="sm"
              variant={selectedPreset === '7d' ? 'default' : 'outline'}
              onClick={() => handlePresetChange('7d')}
            >
              7 Zile
            </Button>
            <Button 
              size="sm"
              variant={selectedPreset === '30d' ? 'default' : 'outline'}
              onClick={() => handlePresetChange('30d')}
            >
              30 Zile
            </Button>
            <Button 
              size="sm"
              variant={selectedPreset === 'mtd' ? 'default' : 'outline'}
              onClick={() => handlePresetChange('mtd')}
            >
              Luna asta
            </Button>
          </div>

          {/* Custom Date Range Picker */}
          <div className="flex gap-2 items-center">
            <Input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              placeholder="De la"
              className="w-36"
            />
            <span className="text-sm text-muted-foreground">-</span>
            <Input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              placeholder="Până la"
              className="w-36"
            />
            {(dateFrom && dateTo) && (
              <Button 
                size="sm"
                onClick={handleCustomDateApply}
                variant="default"
              >
                Aplică
              </Button>
            )}
          </div>
          
          <Button onClick={refreshAllData} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={exportFinancialReport} variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="charts">📊 Charts</TabsTrigger>
          <TabsTrigger value="revenue">Venituri</TabsTrigger>
          <TabsTrigger value="costs">Costuri</TabsTrigger>
          <TabsTrigger value="analysis">Analize</TabsTrigger>
          <TabsTrigger value="categories">Categorii Cost</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Venituri Totale</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {financialData ? formatCurrency(financialData.revenue) : '0 LEI'}
                </div>
                <p className="text-xs text-muted-foreground">
                  {financialData?.period || 'Această lună'}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Costuri Totale</CardTitle>
                <TrendingDown className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {financialData ? formatCurrency(financialData.costs) : '0 LEI'}
                </div>
                <p className="text-xs text-muted-foreground">
                  API, servicii, marketing
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Profit Net</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {financialData ? formatCurrency(financialData.profit) : '0 LEI'}
                </div>
                <p className="text-xs text-muted-foreground">
                  Venituri - Costuri
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">ROI</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${getRoiColor(financialData?.roi || 0)}`}>
                  {financialData?.roi?.toFixed(1) || '0'}%
                </div>
                {financialData && (
                  <Badge variant="outline" className={getRoiStatus(financialData.roi).color}>
                    {getRoiStatus(financialData.roi).text}
                  </Badge>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Charts and Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Recompense Referral</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold mb-2">
                  {financialData ? formatCurrency(financialData.referralRewards) : '0 LEI'}
                </div>
                <p className="text-sm text-muted-foreground mb-4">
                  Total plătit în recompense referral (200 LEI per referral)
                </p>
                <div className="bg-blue-50 p-3 rounded">
                  <p className="text-sm text-blue-700">
                    <strong>{financialData ? Math.floor(financialData.referralRewards / 200) : 0}</strong> referral-uri reușite
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChartIcon className="w-5 h-5" />
                  Distribuția Costurilor
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {costBreakdown.map((item, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: `hsl(${index * 60}, 70%, 50%)` }}
                        />
                        <span className="text-sm">{item.category}</span>
                      </div>
                      <div className="text-sm font-medium">
                        {formatCurrency(item.amount)} ({item.percentage}%)
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Financial Health */}
          <Card>
            <CardHeader>
              <CardTitle>Sănătatea Financiară</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {financialData ? ((financialData.profit / financialData.revenue) * 100).toFixed(1) : '0'}%
                  </div>
                  <p className="text-sm text-gray-600">Marjă de Profit</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {financialData ? ((financialData.costs / financialData.revenue) * 100).toFixed(1) : '0'}%
                  </div>
                  <p className="text-sm text-gray-600">Rata Costurilor</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {financialData ? (financialData.revenue / (financialData.costs || 1)).toFixed(1) : '0'}x
                  </div>
                  <p className="text-sm text-gray-600">Multiplicator Venituri</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="categories" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Adaugă categorie de cost</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Input
                  placeholder="Nume categorie"
                  value={newCategory.name}
                  onChange={(e) => setNewCategory((prev) => ({ ...prev, name: e.target.value }))}
                />
                <Input
                  type="number"
                  min="0"
                  placeholder="Buget (RON)"
                  value={newCategory.budget_cap}
                  onChange={(e) => setNewCategory((prev) => ({ ...prev, budget_cap: e.target.value }))}
                />
                <div className="flex items-center gap-2">
                  <Input
                    type="color"
                    value={newCategory.color}
                    onChange={(e) => setNewCategory((prev) => ({ ...prev, color: e.target.value }))}
                    className="h-10"
                  />
                  <span className="text-sm text-gray-500">Culoare</span>
                </div>
                <Button onClick={handleCreateCategory} disabled={isSavingCategory}>
                  {isSavingCategory ? 'Se salvează...' : 'Adaugă categorie'}
                </Button>
              </div>
              <Textarea
                placeholder="Descriere (opțional)"
                value={newCategory.description}
                onChange={(e) => setNewCategory((prev) => ({ ...prev, description: e.target.value }))}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Categorii existente</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {costCategories.length > 0 ? (
                costCategories.map((category) => {
                  const allocated = breakdownData?.costs?.by_category?.[category.name] ?? 0;
                  const budget = category.budget_cap ? Number(category.budget_cap) : undefined;
                  const usage = budget ? Math.min((allocated / budget) * 100, 100) : 0;
                  return (
                    <div key={category.slug} className="border rounded-lg p-4 flex flex-col gap-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span
                              className="w-3 h-3 rounded-full"
                              style={{ backgroundColor: category.color || '#2563eb' }}
                            />
                            <h4 className="font-semibold">{category.name}</h4>
                          </div>
                          {category.description && (
                            <p className="text-sm text-gray-500 mt-1">{category.description}</p>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-500">
                            {budget ? `${Math.round(usage)}% din ${formatCurrency(budget)}` : 'Fără buget setat'}
                          </span>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDeleteCategory(category.slug, category.is_default)}
                          >
                            Șterge
                          </Button>
                        </div>
                      </div>
                      <div className="bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{ width: `${budget ? usage : 100}%`, backgroundColor: category.color || '#2563eb' }}
                        />
                      </div>
                      <div className="text-sm text-gray-600">
                        Costuri înregistrate: <span className="font-medium">{formatCurrency(allocated)}</span>
                      </div>
                    </div>
                  );
                })
              ) : (
                <p className="text-sm text-gray-500">Nu există categorii definite încă.</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Export factură</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Input
                  placeholder="ID factură"
                  value={invoiceExportId}
                  onChange={(e) => setInvoiceExportId(e.target.value)}
                />
                <div className="flex items-center gap-2">
                  <Button
                    variant={invoiceExportFormat === 'pdf' ? 'default' : 'outline'}
                    onClick={() => setInvoiceExportFormat('pdf')}
                  >
                    PDF
                  </Button>
                  <Button
                    variant={invoiceExportFormat === 'json' ? 'default' : 'outline'}
                    onClick={() => setInvoiceExportFormat('json')}
                  >
                    JSON
                  </Button>
                </div>
                <Button onClick={handleInvoiceExport} disabled={isExportingInvoice}>
                  {isExportingInvoice ? 'Se exportă...' : 'Exportă factură'}
                </Button>
              </div>
              <p className="text-xs text-gray-500">Introduceți ID-ul facturii pentru a genera un PDF rapid sau un export JSON.</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="charts" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Revenue Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  Revenue Trend (Last 30 Days)
                </CardTitle>
              </CardHeader>
              <CardContent>
                {financialData && revenueData.length > 0 ? (
                  <ChartContainer config={{
                    revenue: {
                      label: "Venituri",
                      color: "hsl(var(--chart-1))",
                    },
                  }} className="h-[200px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={revenueData.slice(0, 7)}>
                        <XAxis 
                          dataKey="date" 
                          tickLine={false}
                          axisLine={false}
                          tickFormatter={(value) => new Date(value).toLocaleDateString('ro-RO', { month: 'short', day: 'numeric' })}
                        />
                        <YAxis hide />
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Bar 
                          dataKey="amount" 
                          fill="var(--color-revenue)"
                          radius={[4, 4, 0, 0]}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <BarChart3 className="w-12 h-12 mx-auto mb-2" />
                    <p className="text-sm">Nu există date pentru chart</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Costs Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingDown className="w-5 h-5 text-red-600" />
                  Cost Distribution (Last 30 Days)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {financialData && costData.length > 0 ? (
                    <>
                      {costData.slice(0, 10).map((cost, index) => {
                        const maxCost = Math.max(...costData.map(c => c.amount));
                        const percentage = (cost.amount / maxCost) * 100;
                        
                        return (
                          <div key={index} className="space-y-1">
                            <div className="flex justify-between text-sm">
                              <span className="text-gray-600 truncate">{cost.category}</span>
                              <span className="font-medium text-red-600">{formatCurrency(cost.amount)}</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                              <div
                                className="bg-gradient-to-r from-red-500 to-red-600 h-full rounded-full transition-all duration-500"
                                style={{ width: `${percentage}%` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </>
                  ) : (
                    <div className="text-center py-8 text-gray-400">
                      <PieChartIcon className="w-12 h-12 mx-auto mb-2" />
                      <p className="text-sm">Nu există date pentru chart</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Profit Chart */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-blue-600" />
                  Profit Margin Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="relative inline-flex items-center justify-center w-32 h-32">
                      <svg className="w-32 h-32 transform -rotate-90">
                        <circle
                          className="text-gray-200"
                          strokeWidth="12"
                          stroke="currentColor"
                          fill="transparent"
                          r="56"
                          cx="64"
                          cy="64"
                        />
                        <circle
                          className="text-green-500"
                          strokeWidth="12"
                          strokeDasharray={`${2 * Math.PI * 56}`}
                          strokeDashoffset={`${2 * Math.PI * 56 * (1 - (financialData?.revenue || 0) / ((financialData?.revenue || 0) + (financialData?.costs || 1)))}`}
                          strokeLinecap="round"
                          stroke="currentColor"
                          fill="transparent"
                          r="56"
                          cx="64"
                          cy="64"
                        />
                      </svg>
                      <span className="absolute text-xl font-bold text-gray-700">
                        {financialData ? Math.round(((financialData.revenue) / (financialData.revenue + financialData.costs)) * 100) : 0}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">Revenue</p>
                    <p className="font-medium text-green-600">{formatCurrency(financialData?.revenue || 0)}</p>
                  </div>

                  <div className="text-center">
                    <div className="relative inline-flex items-center justify-center w-32 h-32">
                      <svg className="w-32 h-32 transform -rotate-90">
                        <circle
                          className="text-gray-200"
                          strokeWidth="12"
                          stroke="currentColor"
                          fill="transparent"
                          r="56"
                          cx="64"
                          cy="64"
                        />
                        <circle
                          className="text-red-500"
                          strokeWidth="12"
                          strokeDasharray={`${2 * Math.PI * 56}`}
                          strokeDashoffset={`${2 * Math.PI * 56 * (1 - (financialData?.costs || 0) / ((financialData?.revenue || 1) + (financialData?.costs || 0)))}`}
                          strokeLinecap="round"
                          stroke="currentColor"
                          fill="transparent"
                          r="56"
                          cx="64"
                          cy="64"
                        />
                      </svg>
                      <span className="absolute text-xl font-bold text-gray-700">
                        {financialData ? Math.round((financialData.costs / (financialData.revenue + financialData.costs)) * 100) : 0}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">Costs</p>
                    <p className="font-medium text-red-600">{formatCurrency(financialData?.costs || 0)}</p>
                  </div>

                  <div className="text-center">
                    <div className="relative inline-flex items-center justify-center w-32 h-32">
                      <svg className="w-32 h-32 transform -rotate-90">
                        <circle
                          className="text-gray-200"
                          strokeWidth="12"
                          stroke="currentColor"
                          fill="transparent"
                          r="56"
                          cx="64"
                          cy="64"
                        />
                        <circle
                          className="text-blue-500"
                          strokeWidth="12"
                          strokeDasharray={`${2 * Math.PI * 56}`}
                          strokeDashoffset={`${2 * Math.PI * 56 * (1 - Math.max(0, Math.min(1, (financialData?.profit || 0) / (financialData?.revenue || 1))))}`}
                          strokeLinecap="round"
                          stroke="currentColor"
                          fill="transparent"
                          r="56"
                          cx="64"
                          cy="64"
                        />
                      </svg>
                      <span className="absolute text-xl font-bold text-gray-700">
                        {financialData ? Math.round((financialData.profit / financialData.revenue) * 100) : 0}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">Profit Margin</p>
                    <p className="font-medium text-blue-600">{formatCurrency(financialData?.profit || 0)}</p>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">Insights:</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Profit margin optimal: &gt;30% pentru servicii juridice</li>
                    <li>• Current margin: {financialData ? ((financialData.profit / financialData.revenue) * 100).toFixed(1) : 0}%
                      {financialData && (financialData.profit / financialData.revenue) * 100 > 30 ? ' ✓ Excelent!' : ' - Poate fi îmbunătățit'}
                    </li>
                    <li>• ROI: {financialData?.roi.toFixed(1) || 0}% {financialData && financialData.roi > 50 ? '🚀' : ''}</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChartIcon className="w-5 h-5 text-sky-600" />
                  Revenue vs Costs vs Profit
                </CardTitle>
              </CardHeader>
              <CardContent>
                {timelineData.length > 0 ? (
                  <ChartContainer
                    config={{
                      revenue: { label: 'Venituri', color: 'hsl(var(--chart-1))' },
                      costs: { label: 'Costuri', color: 'hsl(var(--chart-2))' },
                      profit: { label: 'Profit', color: 'hsl(var(--chart-3))' },
                    }}
                    className="h-[280px]"
                  >
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={timelineData}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                        <XAxis
                          dataKey="date"
                          tickLine={false}
                          axisLine={false}
                          tickFormatter={(value) => new Date(value).toLocaleDateString('ro-RO', { month: 'short', day: 'numeric' })}
                        />
                        <YAxis hide />
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Line type="monotone" dataKey="revenue" stroke="var(--color-revenue)" strokeWidth={2} dot={false} />
                        <Line type="monotone" dataKey="costs" stroke="var(--color-costs, #ef4444)" strokeWidth={2} dot={false} />
                        <Line type="monotone" dataKey="profit" stroke="var(--chart-3)" strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                ) : (
                  <div className="text-center py-10 text-gray-400">
                    <LineChartIcon className="w-10 h-10 mx-auto mb-2" />
                    <p className="text-sm">Nu există suficiente date pentru a genera graficul.</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChartIcon className="w-5 h-5" />
                  Distribuție Categorii Cost
                </CardTitle>
              </CardHeader>
              <CardContent>
                {costCategoryEntries.length > 0 ? (
                  <ResponsiveContainer width="100%" height={240}>
                    <PieChart>
                      <Pie
                        data={costCategoryEntries.map(([name, value]) => ({ name, value }))}
                        dataKey="value"
                        nameKey="name"
                        innerRadius={50}
                        outerRadius={90}
                        paddingAngle={4}
                      >
                        {costCategoryEntries.map((entry, index) => (
                          <Cell key={entry[0]} fill={categoryPalette[index % categoryPalette.length]} />
                        ))}
                      </Pie>
                      <ChartTooltip content={<ChartTooltipContent />} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <PieChartIcon className="w-10 h-10 mx-auto mb-2" />
                    <p className="text-sm">Nu există date agregate pentru categorii.</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Layers className="w-5 h-5 text-purple-600" />
                  Distribuție Surse Venit
                </CardTitle>
              </CardHeader>
              <CardContent>
                {revenueCategoryEntries.length > 0 ? (
                  <ResponsiveContainer width="100%" height={240}>
                    <PieChart>
                      <Pie
                        data={revenueCategoryEntries.map(([name, value]) => ({ name, value }))}
                        dataKey="value"
                        nameKey="name"
                        innerRadius={40}
                        outerRadius={90}
                        paddingAngle={4}
                      >
                        {revenueCategoryEntries.map((entry, index) => (
                          <Cell key={entry[0]} fill={categoryPalette[(index + 2) % categoryPalette.length]} />
                        ))}
                      </Pie>
                      <ChartTooltip content={<ChartTooltipContent />} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Layers className="w-10 h-10 mx-auto mb-2" />
                    <p className="text-sm">Nu există date agregate pentru sursele de venit.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="revenue" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Istoric Venituri
              </CardTitle>
            </CardHeader>
            <CardContent>
              {revenueData.length > 0 ? (
                <ChartContainer config={{
                  revenue: {
                    label: "Venituri",
                    color: "hsl(var(--chart-1))",
                  },
                }} className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={revenueData.slice(0, 12)}>
                      <XAxis 
                        dataKey="date" 
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(value) => new Date(value).toLocaleDateString('ro-RO', { month: 'short', day: 'numeric' })}
                      />
                      <YAxis hide />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Line 
                        type="monotone" 
                        dataKey="amount" 
                        stroke="var(--color-revenue)"
                        strokeWidth={2}
                        dot={{ fill: "var(--color-revenue)", strokeWidth: 2, r: 4 }}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartContainer>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Nu există date despre venituri încă.</p>
                  <p className="text-sm mt-2">Datele vor apărea pe măsură ce primești clienți și contracte.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="costs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Istoric Costuri</CardTitle>
            </CardHeader>
            <CardContent>
              {costData.length > 0 ? (
                <div className="space-y-3">
                  {costData.slice(0, 10).map((cost, index) => (
                    <div key={index} className="flex justify-between items-center p-3 border rounded">
                      <div>
                        <span className="font-medium">{cost.category}</span>
                        <div className="text-sm text-gray-500">{cost.description}</div>
                        <div className="text-xs text-gray-400">{formatDate(cost.date)}</div>
                      </div>
                      <div className="text-lg font-bold text-red-600">
                        -{formatCurrency(cost.amount)}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <TrendingDown className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Nu există date despre costuri încă.</p>
                  <p className="text-sm mt-2">Costurile vor fi înregistrate automat pe măsură ce folosești serviciile.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-6">
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Analiza ROI</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg">
                    <h4 className="font-medium mb-2">Performanță Generală</h4>
                    <p className="text-sm text-gray-600">
                      {financialData && financialData.roi > 0 ?
                        `Investiția ta generează ${financialData.roi.toFixed(1)}% ROI, ceea ce este ` +
                        (financialData.roi >= 50 ? 'excelent' : financialData.roi >= 20 ? 'bun' : 'în creștere') +
                        ' pentru o afacere de servicii juridice.' :
                        'ROI-ul va fi calculat pe măsură ce generezi venituri.'
                      }
                    </p>
                  </div>
                  {breakdownData && (
                    <div className="grid grid-cols-1 gap-3 text-sm">
                      <div className="flex justify-between">
                        <span>Profit net:</span>
                        <span className="font-medium text-green-600">{formatCurrency(breakdownData.profitability.net_profit)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Marjă profit:</span>
                        <span className="font-medium">{breakdownData.profitability.profit_margin.toFixed(2)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>ROI:</span>
                        <span className="font-medium">{breakdownData.profitability.roi.toFixed(2)}%</span>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChartIcon className="w-5 h-5 text-sky-600" />
                  Forecast (30 zile)
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {forecastData ? (
                  <>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">Venit mediu</p>
                        <p className="font-semibold">{formatCurrency(forecastData.averages.revenue)}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Cost mediu</p>
                        <p className="font-semibold">{formatCurrency(forecastData.averages.costs)}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Profit mediu</p>
                        <p className="font-semibold text-green-600">{formatCurrency(forecastData.averages.profit)}</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-xs">
                      <div className="bg-slate-50 p-3 rounded">
                        <p className="text-gray-500 mb-1">7 zile</p>
                        <p className="font-semibold">{formatCurrency(forecastData.forecasts['7d'].revenue)}</p>
                        <p className="text-green-600">Profit: {formatCurrency(forecastData.forecasts['7d'].profit)}</p>
                      </div>
                      <div className="bg-slate-50 p-3 rounded">
                        <p className="text-gray-500 mb-1">30 zile</p>
                        <p className="font-semibold">{formatCurrency(forecastData.forecasts['30d'].revenue)}</p>
                        <p className="text-green-600">Profit: {formatCurrency(forecastData.forecasts['30d'].profit)}</p>
                      </div>
                      <div className="bg-slate-50 p-3 rounded">
                        <p className="text-gray-500 mb-1">90 zile</p>
                        <p className="font-semibold">{formatCurrency(forecastData.forecasts['90d'].revenue)}</p>
                        <p className="text-green-600">Profit: {formatCurrency(forecastData.forecasts['90d'].profit)}</p>
                      </div>
                    </div>
                    <div className="h-[180px]">
                      <ChartContainer
                        config={{
                          revenue: { label: 'Venituri', color: 'hsl(var(--chart-1))' },
                          costs: { label: 'Costuri', color: 'hsl(var(--chart-2))' },
                        }}
                        className="h-full"
                      >
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={forecastSeries}>
                            <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                            <XAxis dataKey="date" tickLine={false} axisLine={false} />
                            <YAxis hide />
                            <ChartTooltip content={<ChartTooltipContent />} />
                            <Line type="monotone" dataKey="revenue" stroke="var(--color-revenue)" strokeWidth={2} dot={false} />
                            <Line type="monotone" dataKey="costs" stroke="var(--color-costs, #ef4444)" strokeWidth={2} dot={false} />
                          </LineChart>
                        </ResponsiveContainer>
                      </ChartContainer>
                    </div>
                  </>
                ) : (
                  <p className="text-sm text-gray-500">Datele pentru forecast nu sunt disponibile momentan.</p>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  MRR & Subscriptions
                </CardTitle>
              </CardHeader>
              <CardContent>
                {mrrReport ? (
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="bg-slate-50 p-3 rounded">
                      <p className="text-gray-500">Total MRR</p>
                      <p className="text-lg font-semibold text-green-600">{formatCurrency(mrrReport.metrics.total_mrr)}</p>
                    </div>
                    <div className="bg-slate-50 p-3 rounded">
                      <p className="text-gray-500">Active Subscriptions</p>
                      <p className="text-lg font-semibold">{mrrReport.metrics.active_subscriptions}</p>
                    </div>
                    <div className="bg-slate-50 p-3 rounded">
                      <p className="text-gray-500">Churn Rate</p>
                      <p className="text-lg font-semibold">{mrrReport.metrics.churn_rate}%</p>
                    </div>
                    <div className="bg-slate-50 p-3 rounded">
                      <p className="text-gray-500">CLV estimat</p>
                      <p className="text-lg font-semibold">{formatCurrency(mrrReport.metrics.customer_lifetime_value)}</p>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">Se încarcă abonamentele recurente...</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calculator className="w-5 h-5" />
                  Calcul fiscal estimativ
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className="bg-slate-50 p-3 rounded">
                    <p className="text-gray-500">TVA estimat</p>
                    <p className="text-lg font-semibold">{formatCurrency(taxSummary.vat)}</p>
                  </div>
                  <div className="bg-slate-50 p-3 rounded">
                    <p className="text-gray-500">Impozit profit</p>
                    <p className="text-lg font-semibold">{formatCurrency(taxSummary.corporate)}</p>
                  </div>
                  <div className="bg-slate-50 p-3 rounded">
                    <p className="text-gray-500">Profit după taxe</p>
                    <p className="text-lg font-semibold text-green-600">{formatCurrency(taxSummary.profitAfterTax)}</p>
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-3">Calcule aproximative pentru TVA 19% și impozit profit 16%.</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Profit & Loss Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              {profitLossData ? (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                  <div className="bg-slate-50 p-3 rounded">
                    <p className="text-gray-500">Perioadă</p>
                    <p className="font-semibold">{profitLossData.start_date} - {profitLossData.end_date}</p>
                  </div>
                  <div className="bg-slate-50 p-3 rounded">
                    <p className="text-gray-500">Profit mediu zilnic</p>
                    <p className="font-semibold text-green-600">{formatCurrency(profitLossData.avg_daily_profit)}</p>
                  </div>
                  <div className="bg-slate-50 p-3 rounded">
                    <p className="text-gray-500">Zi de vârf</p>
                    <p className="font-semibold">{formatCurrency(profitLossData.best_day_profit)}</p>
                  </div>
                  <div className="bg-slate-50 p-3 rounded">
                    <p className="text-gray-500">Zi slabă</p>
                    <p className="font-semibold text-red-600">{formatCurrency(profitLossData.worst_day_profit)}</p>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-gray-500">Nu există suficiente date pentru analiza profit/pierdere.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FinancialDashboard;