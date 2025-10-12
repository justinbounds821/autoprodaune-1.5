import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Eye, 
  Heart, 
  Clock,
  Activity
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { 
  getFinancialBreakdown, 
  getSocialFollowers, 
  getVideoAnalyticsPerformance,
  getComprehensiveAnalytics 
} from '@/lib/api';
import type { 
  FinancialBreakdown, 
  SocialFollowers, 
  VideoPerformance,
  ComprehensiveAnalytics 
} from '@/types/api';

interface AnalyticsData {
  overview: {
    totalLeads: number;
    conversionRate: number;
    avgResponseTime: number;
    revenue: number;
    socialEngagement: number;
    videoViews: number;
  };
  leads: {
    daily: Array<{ date: string; leads: number; conversions: number }>;
    sources: Array<{ source: string; count: number; percentage: number }>;
    status: Array<{ status: string; count: number; color: string }>;
  };
  social: {
    platforms: Array<{ platform: string; followers: number; engagement: number; posts: number }>;
    engagement: Array<{ date: string; likes: number; shares: number; comments: number }>;
    topPosts: Array<{ id: string; content: string; engagement: number; platform: string }>;
  };
  financial: {
    revenue: Array<{ month: string; revenue: number; costs: number; profit: number }>;
    categories: Array<{ category: string; amount: number; percentage: number; color: string }>;
  };
  video: {
    performance: Array<{ date: string; views: number; completionRate: number }>;
    topics: Array<{ topic: string; views: number; engagement: number }>;
  };
}

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00', '#ff00ff'];

export default function AdvancedAnalytics() {
  const { toast } = useToast();
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');

  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Load data from multiple endpoints
      const [financialData, socialData, videoData, comprehensiveData] = await Promise.allSettled([
        getFinancialBreakdown(timeRange),
        getSocialFollowers(),
        getVideoAnalyticsPerformance(),
        getComprehensiveAnalytics()
      ]);

      const financial = financialData.status === 'fulfilled' ? financialData.value as FinancialBreakdown : null;
      const social = socialData.status === 'fulfilled' ? socialData.value as SocialFollowers : null;
      const video = videoData.status === 'fulfilled' ? videoData.value as VideoPerformance : null;
      const comprehensive = comprehensiveData.status === 'fulfilled' ? comprehensiveData.value as ComprehensiveAnalytics : null;

      // Build analytics data from responses
      const analyticsData: AnalyticsData = {
        overview: {
          totalLeads: comprehensive?.overview?.total_leads || 0,
          conversionRate: comprehensive?.overview?.conversion_rate || 0,
          avgResponseTime: comprehensive?.overview?.avg_response_time || 0,
          revenue: financial?.total_revenue || 0,
          socialEngagement: social?.engagement_rate || 0,
          videoViews: video?.total_views || 0
        },
        leads: {
          daily: comprehensive?.leads?.daily || [],
          sources: comprehensive?.leads?.sources || [],
          status: comprehensive?.leads?.status?.map((s, idx) => ({
            ...s,
            color: COLORS[idx % COLORS.length]
          })) || []
        },
        social: {
          platforms: social?.platforms || [],
          engagement: [],
          topPosts: []
        },
        financial: {
          revenue: financial?.revenue || [],
          categories: financial?.costs?.by_category?.map((cat, idx) => ({
            category: cat.category,
            amount: cat.total,
            percentage: 0,
            color: COLORS[idx % COLORS.length]
          })) || []
        },
        video: {
          performance: video?.performance || [],
          topics: video?.topics || []
        }
      };

      setData(analyticsData);
    } catch (error) {
      console.error('Failed to load analytics data:', error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca datele de analiză.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ro-RO', {
      style: 'currency',
      currency: 'RON'
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Activity className="w-8 h-8 animate-spin mx-auto mb-2" />
          <p>Se încarcă analizele...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-8">
        <p>Nu s-au putut încărca datele de analiză.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Time Range Selector */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Analize Avansate</h2>
        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7d">Ultimele 7 zile</SelectItem>
            <SelectItem value="30d">Ultimele 30 zile</SelectItem>
            <SelectItem value="90d">Ultimele 90 zile</SelectItem>
            <SelectItem value="1y">Ultimul an</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Leads</p>
                <p className="text-2xl font-bold">{formatNumber(data.overview.totalLeads)}</p>
              </div>
              <Users className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Rata Conversie</p>
                <p className="text-2xl font-bold">{data.overview.conversionRate}%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Timp Răspuns</p>
                <p className="text-2xl font-bold">{data.overview.avgResponseTime}h</p>
              </div>
              <Clock className="w-8 h-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Venituri</p>
                <p className="text-2xl font-bold">{formatCurrency(data.overview.revenue)}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Engagement</p>
                <p className="text-2xl font-bold">{data.overview.socialEngagement}%</p>
              </div>
              <Heart className="w-8 h-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Vizualizări</p>
                <p className="text-2xl font-bold">{formatNumber(data.overview.videoViews)}</p>
              </div>
              <Eye className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics */}
      <Tabs defaultValue="leads" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="leads">Leads</TabsTrigger>
          <TabsTrigger value="social">Social Media</TabsTrigger>
          <TabsTrigger value="financial">Financiar</TabsTrigger>
          <TabsTrigger value="video">Video</TabsTrigger>
          <TabsTrigger value="performance">Performanță</TabsTrigger>
        </TabsList>

        {/* Leads Analytics */}
        <TabsContent value="leads" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Leads Zilnice</CardTitle>
              </CardHeader>
              <CardContent>
                {data.leads.daily.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={data.leads.daily}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString('ro-RO', { month: 'short', day: 'numeric' })} />
                      <YAxis />
                      <Tooltip />
                      <Area type="monotone" dataKey="leads" stackId="1" stroke="#8884d8" fill="#8884d8" />
                      <Area type="monotone" dataKey="conversions" stackId="2" stroke="#82ca9d" fill="#82ca9d" />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center py-8 text-gray-500">Nu există date disponibile</div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Surse Leads</CardTitle>
              </CardHeader>
              <CardContent>
                {data.leads.sources.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={data.leads.sources}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ source, percentage }) => `${source} ${percentage}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="count"
                      >
                        {data.leads.sources.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center py-8 text-gray-500">Nu există date disponibile</div>
                )}
              </CardContent>
            </Card>
          </div>

          {data.leads.status.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Status Leads</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-5 gap-4">
                  {data.leads.status.map((status) => (
                    <div key={status.status} className="text-center">
                      <div 
                        className="w-16 h-16 rounded-full mx-auto mb-2"
                        style={{ backgroundColor: status.color }}
                      />
                      <p className="font-semibold">{status.status}</p>
                      <p className="text-2xl font-bold">{status.count}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Social Media Analytics */}
        <TabsContent value="social" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Platforme Sociale</CardTitle>
            </CardHeader>
            <CardContent>
              {data.social.platforms.length > 0 ? (
                <div className="space-y-4">
                  {data.social.platforms.map(platform => (
                    <div key={platform.platform} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <h3 className="font-semibold">{platform.platform}</h3>
                        <p className="text-sm text-gray-600">{formatNumber(platform.followers)} urmăritori</p>
                      </div>
                      <div className="text-right">
                        <Badge variant="outline">{platform.engagement}% engagement</Badge>
                        <p className="text-sm text-gray-500 mt-1">{platform.posts} postări</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">Nu există date disponibile</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Financial Analytics */}
        <TabsContent value="financial" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Venituri Lunare</CardTitle>
              </CardHeader>
              <CardContent>
                {data.financial.revenue.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={data.financial.revenue}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip formatter={(value) => [formatCurrency(value as number), '']} />
                      <Bar dataKey="revenue" fill="#8884d8" />
                      <Bar dataKey="costs" fill="#ff7300" />
                      <Bar dataKey="profit" fill="#82ca9d" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center py-8 text-gray-500">Nu există date disponibile</div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Categorii Costuri</CardTitle>
              </CardHeader>
              <CardContent>
                {data.financial.categories.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={data.financial.categories}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ category }) => category}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="amount"
                      >
                        {data.financial.categories.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => formatCurrency(value as number)} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center py-8 text-gray-500">Nu există date disponibile</div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Video Analytics */}
        <TabsContent value="video" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Performanță Video</CardTitle>
              </CardHeader>
              <CardContent>
                {data.video.performance.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={data.video.performance}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString('ro-RO', { month: 'short', day: 'numeric' })} />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Line yAxisId="left" type="monotone" dataKey="views" stroke="#8884d8" strokeWidth={2} />
                      <Line yAxisId="right" type="monotone" dataKey="completionRate" stroke="#82ca9d" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center py-8 text-gray-500">Nu există date disponibile</div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Topici Populare</CardTitle>
              </CardHeader>
              <CardContent>
                {data.video.topics.length > 0 ? (
                  <div className="space-y-3">
                    {data.video.topics.map((topic) => (
                      <div key={topic.topic} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <h3 className="font-semibold">{topic.topic}</h3>
                          <Badge variant="outline">{topic.engagement}% engagement</Badge>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold">{formatNumber(topic.views)}</p>
                          <p className="text-sm text-gray-500">vizualizări</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">Nu există date disponibile</div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Performance Analytics */}
        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Metrici Cheie</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                Metricile de performanță vor fi disponibile în curând
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
