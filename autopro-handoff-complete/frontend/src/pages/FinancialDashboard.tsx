import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { DollarSign, TrendingUp, TrendingDown, Target, PieChart as PieChartIcon, BarChart3, Download, RefreshCw, Calendar } from 'lucide-react';
import AutoProApiService from '@/services/autoproApi';
import { FinancialData, Revenue, Cost } from '@/types/admin';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { Bar, BarChart, Line, LineChart, Pie, PieChart, ResponsiveContainer, XAxis, YAxis } from 'recharts';
import { useToast } from '@/hooks/use-toast';

const FinancialDashboard: React.FC = () => {
  const { toast } = useToast();
  const [financialData, setFinancialData] = useState<FinancialData | null>(null);
  const [revenueData, setRevenueData] = useState<Revenue[]>([]);
  const [costData, setCostData] = useState<Cost[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Date range state
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [selectedPreset, setSelectedPreset] = useState('7d');

  useEffect(() => {
    loadFinancialData();
    loadRevenueData();
    loadCostData();
  }, [selectedPreset, dateFrom, dateTo]);

  const loadFinancialData = async () => {
    try {
      setLoading(true);
      
      // Build query params
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
    } finally {
      setLoading(false);
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

  const refreshAllData = async () => {
    await Promise.all([
      loadFinancialData(),
      loadRevenueData(),
      loadCostData()
    ]);
  };

  const exportFinancialReport = async () => {
    try {
      const response = await fetch('/api/financial/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          period: 'current_month',
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

        <TabsContent value="analysis" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                        (financialData.roi >= 50 ? 'excelent' : financialData.roi >= 20 ? 'bun' : 'decent') +
                        ' pentru o afacere de servicii juridice.' :
                        'ROI-ul va fi calculat pe măsură ce generezi venituri.'
                      }
                    </p>
                  </div>

                  {financialData && (
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span>Cost per Lead:</span>
                        <span className="font-medium">
                          {financialData.costs > 0 ? formatCurrency(financialData.costs / 30) : '0 LEI'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Revenue per Client:</span>
                        <span className="font-medium">
                          {formatCurrency(2500)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Break-even Point:</span>
                        <span className="font-medium">
                          {Math.ceil(financialData.costs / 2500)} clienți/lună
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Proiecții</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-2">Creștere Proiectată (6 luni)</h4>
                    {financialData && (
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">Venituri proiectate:</span>
                          <span className="font-medium">
                            {formatCurrency(financialData.revenue * 1.5)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Profit proiectat:</span>
                          <span className="font-medium text-green-600">
                            {formatCurrency(financialData.profit * 1.8)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">ROI proiectat:</span>
                          <span className="font-medium">
                            {(financialData.roi * 1.3).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="bg-yellow-50 p-3 rounded">
                    <h4 className="font-medium text-yellow-800 mb-1">Recomandări</h4>
                    <ul className="text-sm text-yellow-700 space-y-1">
                      <li>• Optimizează costurile de marketing digital</li>
                      <li>• Crește rata de conversie prin automation</li>
                      <li>• Expandează programul de referral-uri</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FinancialDashboard;