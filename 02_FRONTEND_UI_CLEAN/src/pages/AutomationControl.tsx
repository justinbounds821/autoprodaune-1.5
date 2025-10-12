import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Clock, Play, Pause, RefreshCw, Settings, Activity, Calendar, AlertCircle } from 'lucide-react';
import AutoProApiService from '@/services/autoproApi';
import { AutomationStatus, AutomationLog } from '@/types/admin';
import { useToast } from '@/hooks/use-toast';
import CronScheduleEditor from '@/components/CronScheduleEditor';
import AutomationRulesEditor from '@/components/AutomationRulesEditor';

const AutomationControl: React.FC = () => {
  const { toast } = useToast();
  const [status, setStatus] = useState<AutomationStatus | null>(null);
  const [logs, setLogs] = useState<AutomationLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadStatus();
    loadLogs();
  }, []);

  const loadStatus = async () => {
    try {
      setLoading(true);
      const response = await AutoProApiService.getAutomationStatus();

      if (response.automation_active !== undefined || response.daily_target !== undefined) {
        setStatus(response);
      } else {
        console.error('Failed to load automation status:', response.error);
        toast({
          title: "Eroare",
          description: "Nu s-a putut încărca statusul automation.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Failed to load automation status:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut încărca statusul automation.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadLogs = async () => {
    try {
      const response = await AutoProApiService.getAutomationLogs();

      if (response.logs || Array.isArray(response)) {
        setLogs(response.logs || response);
      } else {
        console.error('Failed to load automation logs:', response.error);
      }
    } catch (error) {
      console.error('Failed to load automation logs:', error);
    }
  };

  const handleToggleAutomation = async (enabled: boolean) => {
    try {
      setActionLoading(true);
      let response;

      if (enabled) {
        response = await AutoProApiService.startAutomation();
      } else {
        response = await AutoProApiService.stopAutomation();
      }

      if (response.status === "started" || response.status === "stopped" || response.automation_active !== undefined) {
        await loadStatus();
        toast({
          title: enabled ? "Automation pornit" : "Automation oprit",
          description: response.message || (enabled ? "Automation-ul a fost pornit cu succes." : "Automation-ul a fost oprit cu succes."),
        });
      } else {
        throw new Error(response.error || 'Failed to toggle automation');
      }
    } catch (error) {
      console.error('Failed to toggle automation:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut modifica statusul automation.",
        variant: "destructive",
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleManualTrigger = async () => {
    try {
      setActionLoading(true);
      const response = await AutoProApiService.triggerAutomation();

      if (response.triggered || response.status === "triggered" || response.message) {
        await loadStatus();
        await loadLogs();
        toast({
          title: "Automation declanșat",
          description: response.message || "Automation-ul a fost declanșat manual cu succes.",
        });
      } else {
        throw new Error(response.error || 'Failed to trigger automation');
      }
    } catch (error) {
      console.error('Failed to trigger automation:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut declanșa automation-ul manual.",
        variant: "destructive",
      });
    } finally {
      setActionLoading(false);
    }
  };

  const formatTime = (timeString: string) => {
    if (!timeString) return 'Nu este programat';
    try {
      return new Date(timeString).toLocaleString('ro-RO');
    } catch {
      return timeString;
    }
  };

  const getLogStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-green-500 text-white';
      case 'failed':
        return 'bg-red-500 text-white';
      case 'pending':
        return 'bg-yellow-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  const getLogStatusText = (status: string) => {
    switch (status) {
      case 'success':
        return 'Succes';
      case 'failed':
        return 'Eșuat';
      case 'pending':
        return 'În așteptare';
      default:
        return 'Necunoscut';
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6 flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Se încarcă statusul automation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Automation Control</h1>
        <Button onClick={loadStatus} variant="outline" disabled={actionLoading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${actionLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <Tabs defaultValue="status" className="w-full">
        <TabsList>
          <TabsTrigger value="status">Status & Control</TabsTrigger>
          <TabsTrigger value="schedule">Programare</TabsTrigger>
          <TabsTrigger value="logs">Loguri</TabsTrigger>
        </TabsList>

        <TabsContent value="status" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Status Automation
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Automation Activ</span>
                  <Switch
                    checked={status?.isActive || false}
                    onCheckedChange={handleToggleAutomation}
                    disabled={actionLoading}
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span>Status:</span>
                    <Badge variant={status?.isActive ? 'default' : 'secondary'}>
                      {status?.isActive ? 'ACTIV' : 'INACTIV'}
                    </Badge>
                  </div>

                  <div className="flex justify-between items-center">
                    <span>Postări Astăzi:</span>
                    <Badge variant="outline">
                      {status?.postsToday || 0} / {status?.dailyTarget || 3}
                    </Badge>
                  </div>

                  <div className="flex justify-between items-center">
                    <span>Ultima Rulare:</span>
                    <span className="text-sm text-gray-500">
                      {formatTime(status?.lastRun || '')}
                    </span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span>Următoarea Rulare:</span>
                    <span className="text-sm text-gray-500">
                      {formatTime(status?.nextRun || '')}
                    </span>
                  </div>
                </div>

                <div className="pt-4 border-t">
                  <Button
                    onClick={handleManualTrigger}
                    disabled={actionLoading}
                    className="w-full"
                    variant="outline"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    {actionLoading ? 'Se declanșează...' : 'Declanșează Manual'}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  Platforme Active
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {status?.platforms && status.platforms.length > 0 ? (
                    status.platforms.map((platform) => (
                      <div key={platform} className="flex justify-between items-center">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl">
                            {platform.toLowerCase() === 'tiktok' ? '🎵' :
                             platform.toLowerCase() === 'instagram' ? '📸' :
                             platform.toLowerCase() === 'facebook' ? '👥' : '📱'}
                          </span>
                          <span className="capitalize">{platform}</span>
                        </div>
                        <Badge variant="default">Conectat</Badge>
                      </div>
                    ))
                  ) : (
                    <div className="text-center text-gray-500 py-4">
                      <AlertCircle className="w-6 h-6 mx-auto mb-2" />
                      <p>Nu sunt platforme configurate</p>
                      <p className="text-sm mt-1">Configurează platformele sociale în setări.</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Statistici Automation</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{status?.postsToday || 0}</div>
                  <div className="text-sm text-gray-500">Postări Astăzi</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{status?.dailyTarget || 3}</div>
                  <div className="text-sm text-gray-500">Target Zilnic</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{status?.platforms?.length || 0}</div>
                  <div className="text-sm text-gray-500">Platforme</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {status?.postsToday && status?.dailyTarget ?
                      Math.round((status.postsToday / status.dailyTarget) * 100) : 0}%
                  </div>
                  <div className="text-sm text-gray-500">Progres Zilnic</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="schedule" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Cron Schedule Editor
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CronScheduleEditor />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Loguri Automation</CardTitle>
                <Button onClick={loadLogs} variant="outline" size="sm">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Actualizează
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {logs.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Activity className="w-8 h-8 mx-auto mb-2" />
                    <p>Nu există loguri de afișat încă.</p>
                    <p className="text-sm mt-1">Logurile vor apărea când automation-ul va fi executat.</p>
                  </div>
                ) : (
                  logs.map((log) => (
                    <div key={log.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-2">
                          <Badge className={getLogStatusColor(log.status)}>
                            {getLogStatusText(log.status)}
                          </Badge>
                          <span className="font-medium">{log.action}</span>
                          {log.platform && (
                            <span className="text-sm text-gray-500">• {log.platform}</span>
                          )}
                        </div>
                        <span className="text-sm text-gray-400">
                          {formatTime(log.timestamp)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">{log.details}</p>
                      {log.error && (
                        <div className="mt-2 p-2 bg-red-50 rounded text-sm text-red-600">
                          <strong>Eroare:</strong> {log.error}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AutomationControl;