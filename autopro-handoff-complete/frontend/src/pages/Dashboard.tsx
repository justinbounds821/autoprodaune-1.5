import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Users,
  TrendingUp,
  Clock,
  Phone,
  Mail,
  FileText,
  Calendar,
  BarChart3,
  Activity,
  CheckCircle,
  AlertCircle,
  Video,
  Settings,
  Share2,
  DollarSign,
  Brain
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import NotificationBell from '@/components/NotificationBell';
import AIInsightsDashboard from '@/components/ai-insights/AIInsightsDashboard';

// Import new admin page components
import VideoManagement from './VideoManagement';
import ManoleVideoCreator from './ManoleVideoCreator';
import AutomationControl from './AutomationControl';
import SocialMedia from './SocialMedia';
import SubscriberTracker from './SubscriberTracker';
import FinancialDashboard from './FinancialDashboard';
import AutoProApiService from '@/services/autoproApi';
import { OverviewStats } from '@/types/admin';

interface Lead {
  id: number | string;
  name: string;
  phone: string;
  details: string;
  status: 'new' | 'contacted' | 'in-progress' | 'completed' | 'rejected';
  createdAt: string;
  files: string[] | null;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  email?: string;
  location?: string;
  damage_type?: string;
  source?: string;
}

interface KPIData {
  totalLeads: number;
  newLeads: number;
  conversionRate: number;
  averageResponseTime: number;
  completedCases: number;
  monthlyGrowth: number;
}

const Dashboard = () => {
  const { toast } = useToast();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [kpis, setKpis] = useState<KPIData>({
    totalLeads: 0,
    newLeads: 0,
    conversionRate: 0,
    averageResponseTime: 0,
    completedCases: 0,
    monthlyGrowth: 0
  });
  const [overviewStats, setOverviewStats] = useState<OverviewStats | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [previousLeadsCount, setPreviousLeadsCount] = useState<number>(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Load real data from API
  useEffect(() => {
    const loadData = async (isAutoRefresh = false) => {
      try {
        if (!isAutoRefresh) setLoading(true);
        else setIsRefreshing(true);
        setError(null);

        // Load leads from API (using Vite proxy in dev)
        const leadsResponse = await fetch('/api/leads/');
        if (leadsResponse.ok) {
          const leadsData = await leadsResponse.json();
          console.log('Leads data from API:', leadsData);
          const newLeads = leadsData.items || [];
          
          // Check for new leads and show notification
          if (isAutoRefresh && previousLeadsCount > 0 && newLeads.length > previousLeadsCount) {
            const newCount = newLeads.length - previousLeadsCount;
            toast({
              title: "🎉 Lead-uri noi!",
              description: `${newCount} lead${newCount > 1 ? '-uri' : ''} nou${newCount > 1 ? 'e' : ''} adăugat${newCount > 1 ? 'e' : ''}!`,
            });
          }
          
          setPreviousLeadsCount(newLeads.length);
          setLeads(newLeads);
        }

        // Load KPIs from API
        const kpisResponse = await fetch('/api/financial/dashboard');
        if (kpisResponse.ok) {
          const kpisData = await kpisResponse.json();
          setKpis({
            totalLeads: kpisData.data?.total_leads || 0,
            newLeads: kpisData.data?.new_leads || 0,
            conversionRate: kpisData.data?.conversion_rate || 0,
            averageResponseTime: kpisData.data?.average_response_time || 0,
            completedCases: kpisData.data?.completed_cases || 0,
            monthlyGrowth: kpisData.data?.monthly_growth || 0
          });
        }

        // Load overview stats for admin
        try {
          const overviewResponse = await AutoProApiService.getOverviewStats();
          if (overviewResponse.success && overviewResponse.data) {
            setOverviewStats(overviewResponse.data);
          }
        } catch (overviewError) {
          // Overview stats are optional, don't show error to user
          console.log('Overview stats not available:', overviewError);
        }

      } catch (error) {
        console.error('Error loading dashboard data:', error);
        setError('Nu s-au putut încărca datele de la server.');
        toast({
          title: "Eroare la încărcarea datelor",
          description: "Nu s-au putut încărca datele de la server.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
        setIsRefreshing(false);
      }
    };

    // Initial load
    loadData();
    
    // Setup polling for real-time updates (every 30 seconds)
    const pollInterval = setInterval(() => {
      loadData(true); // Auto-refresh without full loading state
    }, 30000); // 30 seconds
    
    // Cleanup on unmount
    return () => {
      clearInterval(pollInterval);
    };
  }, [toast, previousLeadsCount]);

  const getStatusColor = (status: Lead['status']) => {
    switch (status) {
      case 'new': return 'bg-blue-500';
      case 'contacted': return 'bg-yellow-500';
      case 'in-progress': return 'bg-orange-500';
      case 'completed': return 'bg-green-500';
      case 'rejected': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getPriorityIcon = (priority: Lead['priority']) => {
    switch (priority) {
      case 'urgent': return <AlertCircle className="w-4 h-4 text-red-600" />;
      case 'high': return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'medium': return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'low': return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
  };

  const updateLeadStatus = async (leadId: string, newStatus: Lead['status']) => {
    try {
      const response = await fetch(`/api/leads/${leadId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
      });

      if (response.ok) {
        setLeads(prev => 
          prev.map(lead => 
            lead.id === leadId ? { ...lead, status: newStatus } : lead
          )
        );
        toast({
          title: "Status actualizat",
          description: "Statusul lead-ului a fost actualizat cu succes."
        });
      } else {
        throw new Error('Failed to update status');
      }
    } catch (error) {
      console.error('Error updating lead status:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut actualiza statusul lead-ului.",
        variant: "destructive",
      });
    }
  };

  const filteredLeads = leads.filter(lead => 
    lead.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lead.phone.includes(searchTerm) ||
    lead.details.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-6 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Se încarcă datele...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background p-6 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>
            Încearcă din nou
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold text-foreground">AutoPro Daune Admin</h1>
              {isRefreshing && (
                <Badge variant="outline" className="flex items-center gap-1">
                  <Activity className="w-3 h-3 animate-pulse" />
                  <span className="text-xs">Actualizare...</span>
                </Badge>
              )}
            </div>
            <p className="text-muted-foreground">Manage your complete automation ecosystem • Auto-refresh: 30s</p>
          </div>
          <div className="flex items-center gap-2">
            <NotificationBell />
            <Button>
              <Calendar className="w-4 h-4 mr-2" />
              Export Raport
            </Button>
          </div>
        </div>

        {/* Admin Tabs */}
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-9">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="videos" className="flex items-center gap-2">
              <Video className="w-4 h-4" />
              Videos
            </TabsTrigger>
            <TabsTrigger value="manole" className="flex items-center gap-2">
              <Video className="w-4 h-4" />
              Manole Creator
            </TabsTrigger>
            <TabsTrigger value="automation" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Automation
            </TabsTrigger>
            <TabsTrigger value="social" className="flex items-center gap-2">
              <Share2 className="w-4 h-4" />
              Social
            </TabsTrigger>
            <TabsTrigger value="subscribers" className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Subscribers
            </TabsTrigger>
            <TabsTrigger value="financial" className="flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              Financial
            </TabsTrigger>
            <TabsTrigger value="leads" className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Leads
            </TabsTrigger>
            <TabsTrigger value="ai-insights" className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              AI Insights
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Overview Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Videos Generated</CardTitle>
                  <Video className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{overviewStats?.videosGenerated || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    +2 from yesterday
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Posts Today</CardTitle>
                  <Share2 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{overviewStats?.postsToday || 0}/3</div>
                  <Badge variant={overviewStats?.automationStatus === 'active' ? 'default' : 'secondary'} className="text-xs">
                    {overviewStats?.automationStatus === 'active' ? 'On Schedule' : 'Inactive'}
                  </Badge>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">New Leads</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{overviewStats?.newLeads || kpis.newLeads}</div>
                  <p className="text-xs text-muted-foreground">
                    +{kpis.monthlyGrowth}% from yesterday
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Revenue</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{overviewStats?.revenue ? `${overviewStats.revenue.toLocaleString()} LEI` : '2,400 LEI'}</div>
                  <p className="text-xs text-muted-foreground">
                    +12% from last month
                  </p>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <Activity className="w-4 h-4 text-green-500" />
                      <div>
                        <p className="text-sm">Video "Accident Tips" generated</p>
                        <p className="text-xs text-gray-500">2 minutes ago</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Share2 className="w-4 h-4 text-blue-500" />
                      <div>
                        <p className="text-sm">Post published on TikTok</p>
                        <p className="text-xs text-gray-500">1 hour ago</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Users className="w-4 h-4 text-purple-500" />
                      <div>
                        <p className="text-sm">New lead from WhatsApp</p>
                        <p className="text-xs text-gray-500">3 hours ago</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>System Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Backend API</span>
                      <Badge variant="default">Online</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Database</span>
                      <Badge variant="default">Connected</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Automation</span>
                      <Badge variant={overviewStats?.automationStatus === 'active' ? 'default' : 'secondary'}>
                        {overviewStats?.automationStatus === 'active' ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Social Media</span>
                      <Badge variant="secondary">3/3 Platforms</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Growth System Quick Access */}
            <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  🚀 Growth Command Center
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="mb-4 text-blue-100">
                  Access the complete growth ecosystem with mass content production, AI conversion, and viral affiliate systems.
                </p>
                <div className="flex gap-3">
                  <Button
                    onClick={() => window.open('/growth', '_blank')}
                    variant="secondary"
                    className="bg-white/20 hover:bg-white/30 text-white border-white/20"
                  >
                    <TrendingUp className="mr-2 w-4 h-4" />
                    Growth Dashboard
                  </Button>
                  <Button
                    onClick={() => window.open('http://localhost:8001/docs', '_blank')}
                    variant="outline"
                    className="border-white/20 text-white hover:bg-white/10"
                  >
                    <Activity className="mr-2 w-4 h-4" />
                    API Docs
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="videos">
            <VideoManagement />
          </TabsContent>

          <TabsContent value="manole">
            <ManoleVideoCreator />
          </TabsContent>

          <TabsContent value="automation">
            <AutomationControl />
          </TabsContent>

          <TabsContent value="social">
            <SocialMedia />
          </TabsContent>

          <TabsContent value="subscribers">
            <SubscriberTracker />
          </TabsContent>

          <TabsContent value="financial">
            <FinancialDashboard />
          </TabsContent>

          <TabsContent value="leads" className="space-y-4">
            {/* Legacy Lead Management - Keep existing functionality */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Lead-uri</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{kpis.totalLeads}</div>
                  <p className="text-xs text-muted-foreground">
                    +{kpis.monthlyGrowth}% față de luna trecută
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Lead-uri Noi</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{kpis.newLeads}</div>
                  <p className="text-xs text-muted-foreground">
                    Ultima săptămână
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Rata Conversie</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{kpis.conversionRate}%</div>
                  <p className="text-xs text-muted-foreground">
                    Lead-uri → Clienți
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Timp Răspuns</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{kpis.averageResponseTime}min</div>
                  <p className="text-xs text-muted-foreground">
                    Medie răspuns
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Cazuri Finalizate</CardTitle>
                  <CheckCircle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{kpis.completedCases}</div>
                  <p className="text-xs text-muted-foreground">
                    Această lună
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Creștere</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">+{kpis.monthlyGrowth}%</div>
                  <p className="text-xs text-muted-foreground">
                    Față de luna trecută
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Search and Filters */}
            <div className="flex items-center space-x-4">
              <Input
                placeholder="Caută lead-uri..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="max-w-sm"
              />
              <Button variant="outline">
                Filtrează
              </Button>
            </div>

            {/* Leads Table */}
            <Card>
              <CardHeader>
                <CardTitle>Lead-uri Recente</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {filteredLeads.map((lead) => (
                    <div key={lead.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        {getPriorityIcon(lead.priority)}
                        <div>
                          <h3 className="font-medium">{lead.name}</h3>
                          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                            <Phone className="w-3 h-3" />
                            <span>{lead.phone}</span>
                            {lead.location && (
                              <>
                                <span>•</span>
                                <span>{lead.location}</span>
                              </>
                            )}
                            {lead.damage_type && (
                              <>
                                <span>•</span>
                                <span>{lead.damage_type}</span>
                              </>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">{lead.details}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(lead.status)}>
                          {lead.status}
                        </Badge>
                        <select
                          value={lead.status}
                          onChange={(e) => updateLeadStatus(String(lead.id), e.target.value as Lead['status'])}
                          className="text-sm border rounded px-2 py-1"
                        >
                          <option value="new">Nou</option>
                          <option value="contacted">Contactat</option>
                          <option value="in-progress">În progres</option>
                          <option value="completed">Finalizat</option>
                          <option value="rejected">Respins</option>
                        </select>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Dashboard;