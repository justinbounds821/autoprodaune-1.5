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
  Activity
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

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
      // Simulated data - în producție ar fi API call
      const mockData: AnalyticsData = {
        overview: {
          totalLeads: 1247,
          conversionRate: 23.4,
          avgResponseTime: 2.3,
          revenue: 45670,
          socialEngagement: 15.8,
          videoViews: 89234
        },
        leads: {
          daily: [
            { date: '2025-01-01', leads: 45, conversions: 12 },
            { date: '2025-01-02', leads: 52, conversions: 15 },
            { date: '2025-01-03', leads: 38, conversions: 9 },
            { date: '2025-01-04', leads: 61, conversions: 18 },
            { date: '2025-01-05', leads: 47, conversions: 13 },
            { date: '2025-01-06', leads: 55, conversions: 16 },
            { date: '2025-01-07', leads: 43, conversions: 11 }
          ],
          sources: [
            { source: 'Website', count: 456, percentage: 36.6 },
            { source: 'Social Media', count: 312, percentage: 25.0 },
            { source: 'Referrals', count: 234, percentage: 18.8 },
            { source: 'Google Ads', count: 189, percentage: 15.2 },
            { source: 'Other', count: 56, percentage: 4.5 }
          ],
          status: [
            { status: 'New', count: 234, color: '#8884d8' },
            { status: 'Contacted', count: 189, color: '#82ca9d' },
            { status: 'In Progress', count: 156, color: '#ffc658' },
            { status: 'Completed', count: 123, color: '#00ff00' },
            { status: 'Rejected', count: 45, color: '#ff7300' }
          ]
        },
        social: {
          platforms: [
            { platform: 'TikTok', followers: 15420, engagement: 12.5, posts: 89 },
            { platform: 'Instagram', followers: 8930, engagement: 8.3, posts: 67 },
            { platform: 'Facebook', followers: 5670, engagement: 6.1, posts: 45 }
          ],
          engagement: [
            { date: '2025-01-01', likes: 234, shares: 45, comments: 67 },
            { date: '2025-01-02', likes: 289, shares: 52, comments: 78 },
            { date: '2025-01-03', likes: 198, shares: 38, comments: 54 },
            { date: '2025-01-04', likes: 345, shares: 67, comments: 89 },
            { date: '2025-01-05', likes: 267, shares: 48, comments: 71 },
            { date: '2025-01-06', likes: 312, shares: 59, comments: 82 },
            { date: '2025-01-07', likes: 278, shares: 51, comments: 75 }
          ],
          topPosts: [
            { id: '1', content: 'Cum să faci cerere de despăgubire...', engagement: 2345, platform: 'TikTok' },
            { id: '2', content: 'Drepturile tale ca șofer în caz de accident', engagement: 1876, platform: 'Instagram' },
            { id: '3', content: '5 pași pentru a-ți recupera daunele', engagement: 1567, platform: 'Facebook' }
          ]
        },
        financial: {
          revenue: [
            { month: 'Ian', revenue: 12000, costs: 8000, profit: 4000 },
            { month: 'Feb', revenue: 15000, costs: 9500, profit: 5500 },
            { month: 'Mar', revenue: 18000, costs: 11000, profit: 7000 },
            { month: 'Apr', revenue: 16000, costs: 10000, profit: 6000 },
            { month: 'Mai', revenue: 22000, costs: 13000, profit: 9000 },
            { month: 'Iun', revenue: 25000, costs: 14000, profit: 11000 }
          ],
          categories: [
            { category: 'Consultanță', amount: 25000, percentage: 45.2, color: '#8884d8' },
            { category: 'Expertize', amount: 18000, percentage: 32.5, color: '#82ca9d' },
            { category: 'Reprezentare', amount: 12000, percentage: 21.7, color: '#ffc658' },
            { category: 'Altele', amount: 670, percentage: 1.2, color: '#ff7300' }
          ]
        },
        video: {
          performance: [
            { date: '2025-01-01', views: 1234, completionRate: 78 },
            { date: '2025-01-02', views: 1456, completionRate: 82 },
            { date: '2025-01-03', views: 987, completionRate: 74 },
            { date: '2025-01-04', views: 1678, completionRate: 85 },
            { date: '2025-01-05', views: 1345, completionRate: 79 },
            { date: '2025-01-06', views: 1567, completionRate: 83 },
            { date: '2025-01-07', views: 1423, completionRate: 81 }
          ],
          topics: [
            { topic: 'Accidente Auto', views: 45670, engagement: 12.3 },
            { topic: 'Drepturi Șofer', views: 32150, engagement: 10.8 },
            { topic: 'Despăgubiri', views: 28930, engagement: 9.5 },
            { topic: 'Asigurări', views: 23450, engagement: 8.7 },
            { topic: 'Proceduri', views: 19870, engagement: 7.2 }
          ]
        }
      };
      setData(mockData);
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
