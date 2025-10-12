import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Clock, 
  Settings,
  Trash2, 
  Plus,
  Calendar,
  AlertCircle
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { getAutomationStatus, toggleAutomation, updateAutomationSchedule } from '@/lib/api';
import type { CronJob } from '@/types/api';

const CRON_PRESETS = [
  {
    name: 'Orare (fiecare oră)',
    cron: '0 * * * *',
    description: 'Rulează la începutul fiecărei ore'
  },
  {
    name: 'Zilnic (9:00)',
    cron: '0 9 * * *',
    description: 'Rulează zilnic la ora 9:00'
  },
  {
    name: 'Zilnic (15:00)',
    cron: '0 15 * * *',
    description: 'Rulează zilnic la ora 15:00'
  },
  {
    name: 'Zilnic (21:00)',
    cron: '0 21 * * *',
    description: 'Rulează zilnic la ora 21:00'
  },
  {
    name: 'Săptămânal (Luni 9:00)',
    cron: '0 9 * * 1',
    description: 'Rulează în fiecare luni la 9:00'
  },
  {
    name: 'Weekend (Sâmbătă și Duminică)',
    cron: '0 10 * * 6,0',
    description: 'Rulează la 10:00 în weekend'
  }
];

const ACTIONS = [
  { value: 'post_content', label: 'Postare Conținut', description: 'Postează conținut pe social media' },
  { value: 'generate_video', label: 'Generare Video', description: 'Generează video-uri automate' },
  { value: 'send_notifications', label: 'Notificări', description: 'Trimite notificări către utilizatori' },
  { value: 'backup_data', label: 'Backup Date', description: 'Creează backup pentru date' }
];

const PLATFORMS = ['TikTok', 'Instagram', 'Facebook', 'YouTube'];

export default function CronScheduleEditor() {
  const { toast } = useToast();
  const [jobs, setJobs] = useState<CronJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [globalEnabled, setGlobalEnabled] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [editingJob, setEditingJob] = useState<CronJob | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    action: 'post_content' as CronJob['action'],
    platforms: [] as string[],
    schedule: {
      minute: '0',
      hour: '9',
      dayOfMonth: '*',
      month: '*',
      dayOfWeek: '*'
    }
  });

  useEffect(() => {
    loadCronJobs();
  }, []);

  const loadCronJobs = async () => {
    try {
      setLoading(true);
      const response = await getAutomationStatus();
      
      // Map automation status to cron jobs
      const automationJobs: CronJob[] = response.jobs?.map((job: {
        id: string;
        name: string;
        enabled: boolean;
        schedule: string;
        last_run: string | null;
        next_run: string;
      }) => {
        const scheduleParts = parseCronExpression(job.schedule);
        return {
          id: job.id,
          name: job.name,
          description: '',
          enabled: job.enabled,
          schedule: scheduleParts || {
            minute: '0',
            hour: '9',
            dayOfMonth: '*',
            month: '*',
            dayOfWeek: '*'
          },
          action: 'post_content' as CronJob['action'],
          platforms: ['TikTok'],
          lastRun: job.last_run,
          nextRun: job.next_run
        };
      }) || [];

      setJobs(automationJobs);
      setGlobalEnabled(response.enabled || false);
    } catch (error) {
      console.error('Failed to load cron jobs:', error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca job-urile cron.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const parseCronExpression = (cron: string) => {
    const parts = cron.split(' ');
    if (parts.length !== 5) return null;
    
    return {
      minute: parts[0],
      hour: parts[1],
      dayOfMonth: parts[2],
      month: parts[3],
      dayOfWeek: parts[4]
    };
  };

  const buildCronExpression = (schedule: CronJob['schedule']) => {
    return `${schedule.minute} ${schedule.hour} ${schedule.dayOfMonth} ${schedule.month} ${schedule.dayOfWeek}`;
  };

  const applyPreset = (preset: typeof CRON_PRESETS[0]) => {
    const schedule = parseCronExpression(preset.cron);
    if (schedule) {
      setFormData(prev => ({
        ...prev,
        schedule,
        description: preset.description
      }));
    }
  };

  const handleGlobalToggle = async (enabled: boolean) => {
    try {
      await toggleAutomation(enabled);
      setGlobalEnabled(enabled);
      
      toast({
        title: enabled ? "Automatizare activată" : "Automatizare dezactivată",
        description: enabled ? "Toate job-urile sunt acum active." : "Toate job-urile au fost oprite.",
      });
    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut actualiza statusul automatizării.",
        variant: "destructive",
      });
    }
  };

  const toggleJob = async (jobId: string) => {
    try {
      setJobs(prev => prev.map(job => 
        job.id === jobId ? { ...job, enabled: !job.enabled } : job
      ));
      
      // Update schedule on backend
      const updatedJobs = jobs.map(job => 
        job.id === jobId ? { ...job, enabled: !job.enabled } : job
      );
      
      await updateAutomationSchedule({
        jobs: updatedJobs.map(j => ({
          id: j.id,
          name: j.name,
          enabled: j.enabled,
          schedule: buildCronExpression(j.schedule)
        }))
      });
      
      toast({
        title: "Job actualizat",
        description: "Statusul job-ului a fost actualizat.",
      });
    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut actualiza job-ul.",
        variant: "destructive",
      });
      // Revert on error
      loadCronJobs();
    }
  };

  const saveJob = async () => {
    try {
      const cronExpression = buildCronExpression(formData.schedule);
      const newJob: CronJob = {
        id: editingJob?.id || Date.now().toString(),
        name: formData.name,
        description: formData.description,
        enabled: true,
        schedule: formData.schedule,
        action: formData.action,
        platforms: formData.platforms,
        lastRun: null,
        nextRun: calculateNextRun(cronExpression)
      };

      const updatedJobs = editingJob
        ? jobs.map(job => job.id === editingJob.id ? newJob : job)
        : [newJob, ...jobs];
      
      setJobs(updatedJobs);

      // Update backend
      await updateAutomationSchedule({
        jobs: updatedJobs.map(j => ({
          id: j.id,
          name: j.name,
          enabled: j.enabled,
          schedule: buildCronExpression(j.schedule)
        }))
      });

      toast({
        title: editingJob ? "Job actualizat" : "Job creat",
        description: `Job-ul "${newJob.name}" a fost ${editingJob ? 'actualizat' : 'creat'}.`,
      });

      // Reset form
      setFormData({
        name: '',
        description: '',
        action: 'post_content',
        platforms: [],
        schedule: { minute: '0', hour: '9', dayOfMonth: '*', month: '*', dayOfWeek: '*' }
      });
      setIsCreating(false);
      setEditingJob(null);

    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut salva job-ul.",
        variant: "destructive",
      });
    }
  };

  const deleteJob = async (jobId: string) => {
    try {
      const updatedJobs = jobs.filter(job => job.id !== jobId);
      setJobs(updatedJobs);
      
      await updateAutomationSchedule({
        jobs: updatedJobs.map(j => ({
          id: j.id,
          name: j.name,
          enabled: j.enabled,
          schedule: buildCronExpression(j.schedule)
        }))
      });

      toast({
        title: "Job șters",
        description: "Job-ul a fost șters cu succes.",
      });
    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut șterge job-ul.",
        variant: "destructive",
      });
      // Revert on error
      loadCronJobs();
    }
  };

  const calculateNextRun = (cronExpression: string): string => {
    // Simplified calculation - în producție ar folosi o librărie de cron
    return new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();
  };

  const formatNextRun = (nextRun: string) => {
    return new Date(nextRun).toLocaleString('ro-RO');
  };

  const formatLastRun = (lastRun: string | null) => {
    if (!lastRun) return 'Niciodată';
    return new Date(lastRun).toLocaleString('ro-RO');
  };

  return (
    <div className="space-y-6">
      {/* Global Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              Status Automatizare Globală
            </CardTitle>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">
                {globalEnabled ? 'Activată' : 'Dezactivată'}
              </span>
              <Switch
                checked={globalEnabled}
                onCheckedChange={handleGlobalToggle}
              />
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Presets */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Preset-uri Rapide
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {CRON_PRESETS.map((preset, index) => (
              <Button
                key={index}
                variant="outline"
                className="h-auto p-3 flex flex-col items-start"
                onClick={() => applyPreset(preset)}
              >
                <div className="font-medium text-sm">{preset.name}</div>
                <div className="text-xs text-gray-500 mt-1">{preset.description}</div>
                <Badge variant="secondary" className="mt-2 text-xs">
                  {preset.cron}
                </Badge>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Create/Edit Job Form */}
      {isCreating && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {editingJob ? 'Editează Job' : 'Creează Job Nou'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Nume Job</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="ex: Postare Dimineață"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Acțiune</label>
                <Select
                  value={formData.action}
                  onValueChange={(value: CronJob['action']) => 
                    setFormData(prev => ({ ...prev, action: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {ACTIONS.map(action => (
                      <SelectItem key={action.value} value={action.value}>
                        <div>
                          <div className="font-medium">{action.label}</div>
                          <div className="text-xs text-gray-500">{action.description}</div>
                        </div>
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
                placeholder="Descrierea job-ului..."
              />
            </div>

            {/* Cron Schedule */}
            <div>
              <label className="block text-sm font-medium mb-3">Programare Cron</label>
              <div className="grid grid-cols-5 gap-2">
                <div>
                  <label className="text-xs text-gray-500">Minute</label>
                  <Input
                    value={formData.schedule.minute}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      schedule: { ...prev.schedule, minute: e.target.value }
                    }))}
                    placeholder="0"
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-500">Ora</label>
                  <Input
                    value={formData.schedule.hour}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      schedule: { ...prev.schedule, hour: e.target.value }
                    }))}
                    placeholder="9"
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-500">Zi Luna</label>
                  <Input
                    value={formData.schedule.dayOfMonth}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      schedule: { ...prev.schedule, dayOfMonth: e.target.value }
                    }))}
                    placeholder="*"
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-500">Luna</label>
                  <Input
                    value={formData.schedule.month}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      schedule: { ...prev.schedule, month: e.target.value }
                    }))}
                    placeholder="*"
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-500">Zi Săptămână</label>
                  <Input
                    value={formData.schedule.dayOfWeek}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      schedule: { ...prev.schedule, dayOfWeek: e.target.value }
                    }))}
                    placeholder="*"
                  />
                </div>
              </div>
              <div className="mt-2">
                <Badge variant="outline">
                  Cron: {buildCronExpression(formData.schedule)}
                </Badge>
              </div>
            </div>

            {/* Platforms */}
            <div>
              <label className="block text-sm font-medium mb-2">Platforme</label>
              <div className="flex gap-2 flex-wrap">
                {PLATFORMS.map(platform => (
                  <Button
                    key={platform}
                    variant={formData.platforms.includes(platform) ? "default" : "outline"}
                    size="sm"
                    onClick={() => {
                      setFormData(prev => ({
                        ...prev,
                        platforms: prev.platforms.includes(platform)
                          ? prev.platforms.filter(p => p !== platform)
                          : [...prev.platforms, platform]
                      }));
                    }}
                  >
                    {platform}
                  </Button>
                ))}
              </div>
            </div>

            <div className="flex gap-2">
              <Button onClick={saveJob} disabled={!formData.name}>
                {editingJob ? 'Actualizează' : 'Creează'} Job
              </Button>
              <Button 
                variant="outline" 
                onClick={() => {
                  setIsCreating(false);
                  setEditingJob(null);
                }}
              >
                Anulează
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Jobs List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Job-uri Cron Active</CardTitle>
            <Button onClick={() => setIsCreating(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Job Nou
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Se încarcă...</div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Calendar className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>Nu există job-uri cron configurate.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {jobs.map(job => (
                <div key={job.id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${job.enabled ? 'bg-green-500' : 'bg-gray-400'}`} />
                      <h3 className="font-semibold">{job.name}</h3>
                      <Badge variant="outline">
                        {buildCronExpression(job.schedule)}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={job.enabled}
                        onCheckedChange={() => toggleJob(job.id)}
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setEditingJob(job);
                          setFormData({
                            name: job.name,
                            description: job.description,
                            action: job.action,
                            platforms: job.platforms,
                            schedule: job.schedule
                          });
                          setIsCreating(true);
                        }}
                      >
                        <Settings className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteJob(job.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  
                  {job.description && (
                    <p className="text-sm text-gray-600 mb-3">{job.description}</p>
                  )}
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Acțiune:</span>
                      <span className="ml-2 font-medium">
                        {ACTIONS.find(a => a.value === job.action)?.label || job.action}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">Platforme:</span>
                      <div className="flex gap-1 mt-1">
                        {job.platforms.map(platform => (
                          <Badge key={platform} variant="secondary" className="text-xs">
                            {platform}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-500">Următoarea rulare:</span>
                      <span className="ml-2 font-medium">{formatNextRun(job.nextRun)}</span>
                    </div>
                  </div>
                  
                  <div className="mt-3 pt-3 border-t text-xs text-gray-500">
                    Ultima rulare: {formatLastRun(job.lastRun)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
