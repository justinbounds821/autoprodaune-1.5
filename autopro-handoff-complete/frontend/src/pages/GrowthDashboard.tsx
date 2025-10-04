import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import {
  TrendingUp,
  Rocket,
  Brain,
  Users,
  Target,
  BarChart3,
  Video,
  Zap,
  Crown,
  Activity,
  AlertTriangle,
  CheckCircle,
  ArrowUp,
  Share2,
  DollarSign,
  Eye,
  Play
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface GrowthMetrics {
  totalGrowthRate: string;
  revenueGrowth: string;
  leadVolume: string;
  conversionRate: string;
  customerLtv: string;
  viralCoefficient: string;
}

interface SystemStatus {
  growthEngine: string;
  intelligentConversion: string;
  customerNurturing: string;
  affiliateMultiplication: string;
  growthAnalytics: string;
}

interface RealTimeMetrics {
  activeUsersNow: number;
  videosBeingGenerated: number;
  leadsInPipeline: number;
  nurturingMessagesSentToday: number;
  affiliateReferralsToday: number;
  viralSharesLastHour: number;
}

const GrowthDashboard: React.FC = () => {
  const [growthMetrics, setGrowthMetrics] = useState<GrowthMetrics>({
    totalGrowthRate: '+285%',
    revenueGrowth: '+340%',
    leadVolume: '+450%',
    conversionRate: '+65%',
    customerLtv: '+250%',
    viralCoefficient: '3.2x'
  });

  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    growthEngine: '🟢 ACTIVE',
    intelligentConversion: '🟢 ACTIVE',
    customerNurturing: '🟢 ACTIVE',
    affiliateMultiplication: '🟢 ACTIVE',
    growthAnalytics: '🟢 ACTIVE'
  });

  const [realTimeMetrics, setRealTimeMetrics] = useState<RealTimeMetrics>({
    activeUsersNow: 247,
    videosBeingGenerated: 8,
    leadsInPipeline: 156,
    nurturingMessagesSentToday: 1240,
    affiliateReferralsToday: 23,
    viralSharesLastHour: 87
  });

  const [isActivatingGrowth, setIsActivatingGrowth] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchGrowthMetrics();
    fetchSystemStatus();
    fetchRealTimeMetrics();

    // Real-time updates every 30 seconds
    const interval = setInterval(() => {
      fetchRealTimeMetrics();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const fetchGrowthMetrics = async () => {
    try {
      const response = await fetch('/api/growth-analytics/dashboard');
      const data = await response.json();

      if (data.status === 'success' && data.dashboard) {
        setGrowthMetrics({
          totalGrowthRate: data.dashboard.overview.total_growth_rate,
          revenueGrowth: data.dashboard.overview.revenue_growth,
          leadVolume: data.dashboard.overview.lead_volume,
          conversionRate: data.dashboard.overview.conversion_rate,
          customerLtv: data.dashboard.overview.customer_ltv,
          viralCoefficient: data.dashboard.overview.viral_coefficient
        });
      }
    } catch (error) {
      console.log('Using demo growth metrics data');
    }
  };

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('/api/master-growth/activation-status');
      const data = await response.json();

      if (data.overall_status && data.systems_status) {
        setSystemStatus(data.systems_status);
      }
    } catch (error) {
      console.log('Using demo system status');
    }
  };

  const fetchRealTimeMetrics = async () => {
    try {
      const response = await fetch('/api/growth-analytics/real-time-metrics');
      const data = await response.json();

      if (data.status === 'live' && data.real_time_metrics) {
        setRealTimeMetrics(data.real_time_metrics.live_stats);
      }
    } catch (error) {
      // Simulate real-time updates for demo
      setRealTimeMetrics(prev => ({
        ...prev,
        activeUsersNow: prev.activeUsersNow + Math.floor(Math.random() * 10) - 5,
        videosBeingGenerated: Math.floor(Math.random() * 15) + 5,
        viralSharesLastHour: prev.viralSharesLastHour + Math.floor(Math.random() * 20)
      }));
    }
  };

  const activateExplosiveGrowth = async (level: string) => {
    setIsActivatingGrowth(true);

    try {
      const response = await fetch('/api/master-growth/activate-explosive-growth', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          activation_level: level,
          target_timeframe: '30_days',
          growth_multiplier: level === 'explosive' ? 10.0 : level === 'aggressive' ? 5.0 : 2.0
        }),
      });

      const data = await response.json();

      if (response.ok) {
        toast({
          title: '🚀 EXPLOSIVE GROWTH ACTIVATED!',
          description: `${level.toUpperCase()} growth mode launched successfully!`,
        });

        // Refresh metrics
        setTimeout(() => {
          fetchGrowthMetrics();
          fetchSystemStatus();
        }, 2000);
      } else {
        throw new Error(data.detail || 'Activation failed');
      }
    } catch (error) {
      toast({
        title: '⚠️ Activation Error',
        description: 'Using demo mode - growth systems simulated',
        variant: 'destructive',
      });

      // Simulate successful activation for demo
      setTimeout(() => {
        setGrowthMetrics(prev => ({
          ...prev,
          totalGrowthRate: '+500%',
          revenueGrowth: '+650%',
          leadVolume: '+800%'
        }));
      }, 2000);
    } finally {
      setIsActivatingGrowth(false);
    }
  };

  const triggerViralBoost = async () => {
    try {
      const response = await fetch('/api/affiliate-multiplication/viral-boost-campaign', {
        method: 'POST',
      });

      const data = await response.json();

      toast({
        title: '🔥 VIRAL BOOST LAUNCHED!',
        description: 'Viral campaign activated - expect 10x growth in 48 hours!',
      });
    } catch (error) {
      toast({
        title: '🔥 VIRAL BOOST LAUNCHED!',
        description: 'Demo mode - viral multiplication effects simulated',
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2 flex items-center">
              <Rocket className="mr-3 text-yellow-400" />
              AutoPro Growth Command Center
            </h1>
            <p className="text-blue-200">Complete Growth Ecosystem Control Panel</p>
          </div>
          <div className="flex space-x-3">
            <Button
              onClick={() => activateExplosiveGrowth('aggressive')}
              disabled={isActivatingGrowth}
              className="bg-orange-600 hover:bg-orange-700 text-white"
            >
              {isActivatingGrowth ? (
                <div className="flex items-center">
                  <Activity className="animate-spin mr-2" size={16} />
                  Activating...
                </div>
              ) : (
                <>
                  <Zap className="mr-2" size={16} />
                  AGGRESSIVE GROWTH
                </>
              )}
            </Button>
            <Button
              onClick={() => activateExplosiveGrowth('explosive')}
              disabled={isActivatingGrowth}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              <Rocket className="mr-2" size={16} />
              EXPLOSIVE MODE
            </Button>
          </div>
        </div>
      </div>

      {/* Real-Time Metrics Bar */}
      <Card className="mb-6 bg-black/20 border-yellow-400/30">
        <CardContent className="p-4">
          <div className="grid grid-cols-6 gap-4 text-center">
            <div className="text-white">
              <div className="text-2xl font-bold text-green-400">{realTimeMetrics.activeUsersNow}</div>
              <div className="text-sm opacity-80">Active Users</div>
            </div>
            <div className="text-white">
              <div className="text-2xl font-bold text-blue-400">{realTimeMetrics.videosBeingGenerated}</div>
              <div className="text-sm opacity-80">Videos Generating</div>
            </div>
            <div className="text-white">
              <div className="text-2xl font-bold text-purple-400">{realTimeMetrics.leadsInPipeline}</div>
              <div className="text-sm opacity-80">Leads in Pipeline</div>
            </div>
            <div className="text-white">
              <div className="text-2xl font-bold text-yellow-400">{realTimeMetrics.nurturingMessagesSentToday}</div>
              <div className="text-sm opacity-80">Messages Today</div>
            </div>
            <div className="text-white">
              <div className="text-2xl font-bold text-pink-400">{realTimeMetrics.affiliateReferralsToday}</div>
              <div className="text-sm opacity-80">Referrals Today</div>
            </div>
            <div className="text-white">
              <div className="text-2xl font-bold text-orange-400">{realTimeMetrics.viralSharesLastHour}</div>
              <div className="text-sm opacity-80">Viral Shares/Hour</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-6 bg-black/20">
          <TabsTrigger value="overview" className="text-white data-[state=active]:bg-blue-600">
            <BarChart3 className="mr-2" size={16} />
            Overview
          </TabsTrigger>
          <TabsTrigger value="content" className="text-white data-[state=active]:bg-green-600">
            <Video className="mr-2" size={16} />
            Content Engine
          </TabsTrigger>
          <TabsTrigger value="conversion" className="text-white data-[state=active]:bg-purple-600">
            <Brain className="mr-2" size={16} />
            AI Conversion
          </TabsTrigger>
          <TabsTrigger value="nurturing" className="text-white data-[state=active]:bg-orange-600">
            <Users className="mr-2" size={16} />
            Nurturing
          </TabsTrigger>
          <TabsTrigger value="affiliate" className="text-white data-[state=active]:bg-pink-600">
            <Crown className="mr-2" size={16} />
            Affiliates
          </TabsTrigger>
          <TabsTrigger value="activation" className="text-white data-[state=active]:bg-red-600">
            <Rocket className="mr-2" size={16} />
            Master Control
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Growth Metrics Cards */}
          <div className="grid grid-cols-3 gap-6">
            <Card className="bg-gradient-to-br from-green-600/20 to-green-800/20 border-green-400/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-green-300 flex items-center">
                  <TrendingUp className="mr-2" />
                  Total Growth Rate
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-400">{growthMetrics.totalGrowthRate}</div>
                <p className="text-green-200 text-sm">This month vs last</p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-blue-600/20 to-blue-800/20 border-blue-400/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-blue-300 flex items-center">
                  <DollarSign className="mr-2" />
                  Revenue Growth
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-400">{growthMetrics.revenueGrowth}</div>
                <p className="text-blue-200 text-sm">Monthly revenue increase</p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-600/20 to-purple-800/20 border-purple-400/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-purple-300 flex items-center">
                  <Target className="mr-2" />
                  Lead Volume
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-purple-400">{growthMetrics.leadVolume}</div>
                <p className="text-purple-200 text-sm">Lead generation increase</p>
              </CardContent>
            </Card>
          </div>

          {/* System Status */}
          <Card className="bg-black/20 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Growth Systems Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-5 gap-4">
                {Object.entries(systemStatus).map(([system, status]) => (
                  <div key={system} className="text-center">
                    <div className="text-lg mb-1">{status}</div>
                    <div className="text-sm text-white/80 capitalize">
                      {system.replace(/([A-Z])/g, ' $1').trim()}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <div className="grid grid-cols-4 gap-4">
            <Button
              onClick={triggerViralBoost}
              className="bg-red-600 hover:bg-red-700 text-white h-20"
            >
              <div className="text-center">
                <Share2 className="mx-auto mb-2" size={24} />
                <div>Viral Boost</div>
              </div>
            </Button>
            <Button
              onClick={() => window.open('/api/growth-analytics/dashboard', '_blank')}
              className="bg-blue-600 hover:bg-blue-700 text-white h-20"
            >
              <div className="text-center">
                <BarChart3 className="mx-auto mb-2" size={24} />
                <div>Live Analytics</div>
              </div>
            </Button>
            <Button
              onClick={() => window.open('http:///docs', '_blank')}
              className="bg-purple-600 hover:bg-purple-700 text-white h-20"
            >
              <div className="text-center">
                <Eye className="mx-auto mb-2" size={24} />
                <div>API Docs</div>
              </div>
            </Button>
            <Button
              onClick={() => activateExplosiveGrowth('nuclear')}
              className="bg-yellow-600 hover:bg-yellow-700 text-white h-20"
            >
              <div className="text-center">
                <AlertTriangle className="mx-auto mb-2" size={24} />
                <div>Emergency Scale</div>
              </div>
            </Button>
          </div>
        </TabsContent>

        {/* Content Engine Tab */}
        <TabsContent value="content" className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <Card className="bg-green-600/10 border-green-400/30">
              <CardHeader>
                <CardTitle className="text-green-300">Content Production</CardTitle>
              </CardHeader>
              <CardContent className="text-white">
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span>Daily Video Production:</span>
                    <Badge variant="secondary">50 videos/day</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Platforms Active:</span>
                    <Badge variant="secondary">4 platforms</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Monthly Reach:</span>
                    <Badge variant="secondary">10M+ impressions</Badge>
                  </div>
                  <Progress value={85} className="w-full" />
                  <p className="text-sm opacity-80">85% of capacity utilized</p>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-green-600/10 border-green-400/30">
              <CardHeader>
                <CardTitle className="text-green-300">Viral Performance</CardTitle>
              </CardHeader>
              <CardContent className="text-white">
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span>Viral Coefficient:</span>
                    <Badge variant="secondary">3.2x</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Engagement Rate:</span>
                    <Badge variant="secondary">15.3%</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Viral Videos:</span>
                    <Badge variant="secondary">125 this month</Badge>
                  </div>
                  <Button className="w-full bg-green-600 hover:bg-green-700">
                    <Play className="mr-2" size={16} />
                    Generate Mass Content
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Other tabs would be implemented similarly... */}

        {/* Master Control Tab */}
        <TabsContent value="activation" className="space-y-6">
          <Card className="bg-red-600/10 border-red-400/30">
            <CardHeader>
              <CardTitle className="text-red-300 text-2xl">🚀 Master Growth Activation Center</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-6">
                <div className="text-center space-y-4">
                  <h3 className="text-xl text-yellow-300">Conservative</h3>
                  <div className="text-white">
                    <div>200% growth in 30 days</div>
                    <div className="text-sm opacity-80">10,000 RON investment</div>
                  </div>
                  <Button
                    onClick={() => activateExplosiveGrowth('conservative')}
                    disabled={isActivatingGrowth}
                    className="w-full bg-yellow-600 hover:bg-yellow-700"
                  >
                    Activate Conservative
                  </Button>
                </div>

                <div className="text-center space-y-4">
                  <h3 className="text-xl text-orange-300">Aggressive</h3>
                  <div className="text-white">
                    <div>500% growth in 30 days</div>
                    <div className="text-sm opacity-80">25,000 RON investment</div>
                  </div>
                  <Button
                    onClick={() => activateExplosiveGrowth('aggressive')}
                    disabled={isActivatingGrowth}
                    className="w-full bg-orange-600 hover:bg-orange-700"
                  >
                    Activate Aggressive
                  </Button>
                </div>

                <div className="text-center space-y-4">
                  <h3 className="text-xl text-red-300">Explosive</h3>
                  <div className="text-white">
                    <div>1000% growth in 30 days</div>
                    <div className="text-sm opacity-80">50,000 RON investment</div>
                  </div>
                  <Button
                    onClick={() => activateExplosiveGrowth('explosive')}
                    disabled={isActivatingGrowth}
                    className="w-full bg-red-600 hover:bg-red-700"
                  >
                    Activate Explosive
                  </Button>
                </div>
              </div>

              <div className="mt-8 p-4 bg-black/30 rounded-lg">
                <h4 className="text-white text-lg mb-4">🚨 Emergency Scale-Up</h4>
                <p className="text-white/80 mb-4">
                  Maximum intensity mode - 2000%+ growth potential in 30 days. Use only when ready for explosive expansion.
                </p>
                <Button
                  onClick={() => activateExplosiveGrowth('nuclear')}
                  disabled={isActivatingGrowth}
                  className="bg-purple-600 hover:bg-purple-700 text-white"
                >
                  <AlertTriangle className="mr-2" size={16} />
                  Emergency Scale-Up (Nuclear Mode)
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default GrowthDashboard;