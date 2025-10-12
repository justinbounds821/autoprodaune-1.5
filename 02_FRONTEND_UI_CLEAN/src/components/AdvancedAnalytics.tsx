import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
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
  Share2, 
  MessageCircle,
  Calendar,
  Target,
  Activity,
  Clock
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { 
  getFinancialBreakdown, 
  getSocialFollowers, 
  getVideoAnalytics,
  handleApiError 
} from '@/services/apiService';
import type { AnalyticsData } from '@/types/api';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#10B981', '#8B5CF6'];

export default function AdvancedAnalytics() {
  const { toast } = useToast();
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');

  useEffect(() => {
    loadAnalyticsData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timeRange]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Fetch data from multiple endpoints in parallel
      const [financialData, socialData, videoData] = await Promise.all([
        getFinancialBreakdown(timeRange),
        getSocialFollowers(),
        getVideoAnalytics()
      ]);

      // Build analytics data from API responses with fallbacks
      const analyticsData: AnalyticsData = {
        overview: {
          totalLeads: 0, // TODO: Add leads endpoint
          conversionRate: 0,
          avgResponseTime: 0,
          revenue: financialData.total_revenue || 0,
          socialEngagement: calculateOverallEngagement(socialData),
          videoViews: videoData.total_views || 0
        },
        leads: {
          daily: [],
          sources: [],
          status: []
        },
        social: {
          platforms: Object.entries(socialData.by_platform || {}).map(([platform, data]) => ({
            platform,
            followers: data.followers || 0,
            engagement: data.engagement_rate || 0,
            posts: data.posts_count || 0
          })),
          engagement: [],
          topPosts: []
        },
        financial: {
          revenue: (financialData.timeline || []).map(point => ({
            month: new Date(point.date).toLocaleDateString('ro-RO', { month: 'short' }),
            revenue: point.revenue,
            costs: point.costs,
            profit: point.profit
          })),
          categories: Object.entries(financialData.costs?.by_category || {}).map(([category, amount], idx) => ({
            category,
            amount: amount as number,
            percentage: financialData.costs?.total ? ((amount as number) / financialData.costs.total) * 100 : 0,
            color: COLORS[idx % COLORS.length]
          }))
        },
        video: {
          performance: (videoData.top_performing || []).map(video => ({
            date: video.created_at,
            views: video.views,
            completionRate: video.completion_rate || 0
          })),
          topics: Object.entries(videoData.by_topic || {}).map(([topic, stats]) => ({
            topic,
            views: (stats as { views?: number; engagement?: number }).views || 0,
            engagement: (stats as { views?: number; engagement?: number }).engagement || 0
          }))
        }
      };

      setData(analyticsData);
    } catch (error) {
      console.error('Failed to load analytics data:', error);
      toast({
        title: "Eroare",
        description: handleApiError(error),
        variant: "destructive",
      });
      
      // Set empty data structure on error
      setData({
        overview: { totalLeads: 0, conversionRate: 0, avgResponseTime: 0, revenue: 0, socialEngagement: 0, videoViews: 0 },
        leads: { daily: [], sources: [], status: [] },
        social: { platforms: [], engagement: [], topPosts: [] },
        financial: { revenue: [], categories: [] },
        video: { performance: [], topics: [] }
      });
    } finally {
      setLoading(false);
    }
  };

  const calculateOverallEngagement = (socialData: { by_platform?: Record<string, { engagement_rate?: number }> }): number => {
    if (!socialData.by_platform) return 0;
    const platforms = Object.values(socialData.by_platform);
    if (platforms.length === 0) return 0;
    const total = platforms.reduce((sum, p) => sum + (p.engagement_rate || 0), 0);
    return total / platforms.length;
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
            <div className="flex items-center mt-2">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">+12.5%</span>
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
              <Target className="w-8 h-8 text-green-500" />
            </div>
            <div className="flex items-center mt-2">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">+2.1%</span>
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
            <div className="flex items-center mt-2">
              <TrendingDown className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">-0.5h</span>
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
            <div className="flex items-center mt-2">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">+18.3%</span>
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
            <div className="flex items-center mt-2">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">+3.2%</span>
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
            <div className="flex items-center mt-2">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">+25.7%</span>
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
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Surse Leads</CardTitle>
              </CardHeader>
              <CardContent>
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
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Status Leads</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-5 gap-4">
                {data.leads.status.map((status, index) => (
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
        </TabsContent>

        {/* Social Media Analytics */}
        <TabsContent value="social" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Platforme Sociale</CardTitle>
              </CardHeader>
              <CardContent>
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
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Engagement Zilnic</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={data.social.engagement}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString('ro-RO', { month: 'short', day: 'numeric' })} />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="likes" stroke="#8884d8" strokeWidth={2} />
                    <Line type="monotone" dataKey="shares" stroke="#82ca9d" strokeWidth={2} />
                    <Line type="monotone" dataKey="comments" stroke="#ffc658" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Top Postări</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {data.social.topPosts.map(post => (
                  <div key={post.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium">{post.content}</p>
                      <Badge variant="secondary" className="mt-1">{post.platform}</Badge>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold">{formatNumber(post.engagement)}</p>
                      <p className="text-sm text-gray-500">engagement</p>
                    </div>
                  </div>
                ))}
              </div>
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
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={data.financial.revenue}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value, name) => [formatCurrency(value as number), name]} />
                    <Bar dataKey="revenue" fill="#8884d8" />
                    <Bar dataKey="costs" fill="#ff7300" />
                    <Bar dataKey="profit" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Categorii Venituri</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={data.financial.categories}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ category, percentage }) => `${category} ${percentage}%`}
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
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Topici Populare</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {data.video.topics.map((topic, index) => (
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
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Performance Analytics */}
        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Metrici Cheie</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">ROI Marketing</span>
                    <span className="text-lg font-bold text-green-600">340%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Cost per Lead</span>
                    <span className="text-lg font-bold">45 RON</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Lifetime Value</span>
                    <span className="text-lg font-bold">1,250 RON</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Churn Rate</span>
                    <span className="text-lg font-bold text-red-600">8.2%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Obiective</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Leads Lunar</span>
                      <span className="text-sm text-gray-600">450 / 500</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-600 h-2 rounded-full" style={{ width: '90%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Venituri Anuale</span>
                      <span className="text-sm text-gray-600">45K / 60K RON</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{ width: '75%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Engagement Social</span>
                      <span className="text-sm text-gray-600">15.8% / 20%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-purple-600 h-2 rounded-full" style={{ width: '79%' }}></div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
