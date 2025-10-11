import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { RefreshCw, Save, ShieldCheck, Undo2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { NotificationPreferences } from '@/types/admin';

const DEFAULT_PREFERENCES: NotificationPreferences = {
  email: true,
  sms: false,
  whatsapp: true,
  in_app: true,
  lead_updates: true,
  video_updates: true,
  financial_reports: true,
  social_alerts: true,
  digest_frequency: 'daily',
  quiet_hours_start: null,
  quiet_hours_end: null,
};

const USER_ID = 'global-admin';

const digestOptions: { value: NotificationPreferences['digest_frequency']; label: string; description: string }[] = [
  { value: 'instant', label: 'Instant', description: 'Primești imediat fiecare notificare importantă.' },
  { value: 'hourly', label: 'La oră', description: 'Rapoarte consolidate la fiecare oră.' },
  { value: 'daily', label: 'Zilnic', description: 'Rezumat trimis în fiecare dimineață.' },
  { value: 'weekly', label: 'Săptămânal', description: 'Raport complet în fiecare luni.' },
];

const channelConfig = [
  {
    key: 'email' as const,
    label: 'Email',
    description: 'Trimite rezumate și alerte pe adresa principală.',
  },
  {
    key: 'sms' as const,
    label: 'SMS',
    description: 'Mesaje text pentru evenimente critice (lead VIP, erori).',
  },
  {
    key: 'whatsapp' as const,
    label: 'WhatsApp',
    description: 'Notificări rapide prin botul WhatsApp Business.',
  },
  {
    key: 'in_app' as const,
    label: 'In-App',
    description: 'Notificări vizibile în dashboard-ul admin.',
  },
];

const categoryConfig = [
  {
    key: 'lead_updates' as const,
    label: 'Lead-uri',
    description: 'Lead nou, schimbare de status, scor actualizat.',
  },
  {
    key: 'video_updates' as const,
    label: 'Video & Automatizare',
    description: 'Job video finalizat, automatizare programată, erori.',
  },
  {
    key: 'financial_reports' as const,
    label: 'Financiar',
    description: 'Rapoarte de venituri, costuri și alerte de cashflow.',
  },
  {
    key: 'social_alerts' as const,
    label: 'Social Media',
    description: 'Postare publicată, creșteri de engagement, comentarii.',
  },
];

const NotificationSettings: React.FC = () => {
  const { toast } = useToast();
  const [preferences, setPreferences] = useState<NotificationPreferences>(DEFAULT_PREFERENCES);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);

  const quietHoursEnabled = useMemo(
    () => Boolean(preferences.quiet_hours_start && preferences.quiet_hours_end),
    [preferences.quiet_hours_start, preferences.quiet_hours_end],
  );

  const markDirty = useCallback(() => setDirty(true), []);

  const mergePreferences = useCallback((payload: Partial<NotificationPreferences>) => {
    setPreferences((prev) => ({ ...prev, ...payload }));
    markDirty();
  }, [markDirty]);

  const loadPreferences = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/notify/preferences?user_id=${USER_ID}`);
      if (!response.ok) {
        throw new Error('Failed to load preferences');
      }
      const data = await response.json();
      const merged: NotificationPreferences = {
        ...DEFAULT_PREFERENCES,
        ...(data?.preferences ?? {}),
      };
      setPreferences(merged);
      setDirty(false);
    } catch (error) {
      console.error('Failed to load preferences', error);
      toast({
        title: 'Eroare la încărcare',
        description: 'Nu am putut încărca preferințele de notificare.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  const savePreferences = useCallback(async () => {
    try {
      setSaving(true);
      const response = await fetch(`/api/notify/preferences?user_id=${USER_ID}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(preferences),
      });

      if (!response.ok) {
        const errorPayload = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorPayload.detail || 'Failed to save preferences');
      }

      const data = await response.json();
      const merged: NotificationPreferences = {
        ...DEFAULT_PREFERENCES,
        ...(data?.preferences ?? {}),
      };
      setPreferences(merged);
      setDirty(false);
      toast({
        title: 'Preferințe salvate',
        description: 'Configurările de notificare au fost actualizate.',
      });
    } catch (error) {
      console.error('Failed to save preferences', error);
      const description =
        error instanceof Error ? error.message : 'A apărut o eroare neașteptată.';
      toast({
        title: 'Nu am putut salva',
        description,
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  }, [preferences, toast]);

  const resetPreferences = useCallback(async () => {
    try {
      setSaving(true);
      const response = await fetch(`/api/notify/preferences/reset?user_id=${USER_ID}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to reset preferences');
      }

      const data = await response.json();
      const merged: NotificationPreferences = {
        ...DEFAULT_PREFERENCES,
        ...(data?.preferences ?? {}),
      };
      setPreferences(merged);
      setDirty(false);
      toast({
        title: 'Preferințe resetate',
        description: 'Am revenit la setările implicite recomandate de sistem.',
      });
    } catch (error) {
      console.error('Failed to reset preferences', error);
      toast({
        title: 'Nu am putut reseta',
        description: 'Te rugăm să încerci din nou sau să contactezi suportul.',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  }, [toast]);

  useEffect(() => {
    loadPreferences();
  }, [loadPreferences]);

  const toggleQuietHours = useCallback(
    (enabled: boolean) => {
      if (enabled) {
        mergePreferences({
          quiet_hours_start: preferences.quiet_hours_start ?? '22:00',
          quiet_hours_end: preferences.quiet_hours_end ?? '07:00',
        });
      } else {
        mergePreferences({ quiet_hours_start: null, quiet_hours_end: null });
      }
    },
    [mergePreferences, preferences.quiet_hours_end, preferences.quiet_hours_start],
  );

  if (loading) {
    return (
      <div className="flex min-h-[320px] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-b-2 border-blue-600" />
          <p className="text-sm text-muted-foreground">Se încarcă preferințele de notificare...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold">Preferințe notificări</h1>
          <p className="text-muted-foreground">
            Controlează canalele și tipurile de notificări automate livrate de AutoPro Daune.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            onClick={loadPreferences}
            disabled={saving}
          >
            <RefreshCw className="mr-2 h-4 w-4" /> Reîncarcă
          </Button>
          <Button
            variant="secondary"
            onClick={resetPreferences}
            disabled={saving}
          >
            <Undo2 className="mr-2 h-4 w-4" /> Reset implicit
          </Button>
          <Button
            onClick={savePreferences}
            disabled={saving || !dirty}
          >
            <Save className="mr-2 h-4 w-4" /> Salvează
          </Button>
        </div>
      </div>

      {dirty && (
        <Card className="border-yellow-300 bg-yellow-50/60">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <ShieldCheck className="h-4 w-4 text-yellow-600" />
              Modificări nesalvate
            </CardTitle>
            <CardDescription>
              Apasă „Salvează” pentru a păstra noile setări. Resetul revine la recomandările implicite.
            </CardDescription>
          </CardHeader>
        </Card>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Canale de comunicare</CardTitle>
            <CardDescription>Alege pe ce canale primești alertele principale.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {channelConfig.map(({ key, label, description }) => (
              <div key={key} className="flex items-start justify-between gap-4 rounded-lg border p-4">
                <div>
                  <p className="font-medium">{label}</p>
                  <p className="text-sm text-muted-foreground">{description}</p>
                </div>
                <Switch
                  checked={Boolean(preferences[key])}
                  onCheckedChange={(value) => mergePreferences({ [key]: value } as Partial<NotificationPreferences>)}
                />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Tipuri de alerte</CardTitle>
            <CardDescription>Selectează ce evenimente sunt importante pentru echipa ta.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {categoryConfig.map(({ key, label, description }) => (
              <div key={key} className="flex items-start justify-between gap-4 rounded-lg border p-4">
                <div>
                  <p className="font-medium">{label}</p>
                  <p className="text-sm text-muted-foreground">{description}</p>
                </div>
                <Switch
                  checked={Boolean(preferences[key])}
                  onCheckedChange={(value) => mergePreferences({ [key]: value } as Partial<NotificationPreferences>)}
                />
              </div>
            ))}

            <Separator className="my-2" />

            <div className="space-y-2">
              <Label className="text-sm font-medium">Frecvență raport consolidat</Label>
              <Select
                value={preferences.digest_frequency}
                onValueChange={(value: NotificationPreferences['digest_frequency']) =>
                  mergePreferences({ digest_frequency: value })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selectează frecvența" />
                </SelectTrigger>
                <SelectContent>
                  {digestOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      <div>
                        <p className="font-medium">{option.label}</p>
                        <p className="text-xs text-muted-foreground">{option.description}</p>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Quiet hours & detalii livrare</CardTitle>
          <CardDescription>
            Configurează intervalul fără notificări și verifică ultima actualizare a setărilor.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-start gap-3">
              <Switch checked={quietHoursEnabled} onCheckedChange={toggleQuietHours} />
              <div>
                <p className="font-medium">Activează quiet hours</p>
                <p className="text-sm text-muted-foreground">
                  Blochează notificările între orele selectate pentru a nu deranja echipa.
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-4">
              <div className="space-y-1">
                <Label htmlFor="quiet-start">De la</Label>
                <Input
                  id="quiet-start"
                  type="time"
                  value={preferences.quiet_hours_start ?? ''}
                  onChange={(event) =>
                    mergePreferences({ quiet_hours_start: event.target.value || null })
                  }
                  disabled={!quietHoursEnabled}
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="quiet-end">Până la</Label>
                <Input
                  id="quiet-end"
                  type="time"
                  value={preferences.quiet_hours_end ?? ''}
                  onChange={(event) =>
                    mergePreferences({ quiet_hours_end: event.target.value || null })
                  }
                  disabled={!quietHoursEnabled}
                />
              </div>
            </div>
          </div>

          <Separator />

          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant={preferences.email ? 'default' : 'outline'}>Email</Badge>
              <Badge variant={preferences.sms ? 'default' : 'outline'}>SMS</Badge>
              <Badge variant={preferences.whatsapp ? 'default' : 'outline'}>WhatsApp</Badge>
              <Badge variant={preferences.in_app ? 'default' : 'outline'}>In-App</Badge>
            </div>
            <div className="text-sm text-muted-foreground">
              Ultima actualizare:{' '}
              {preferences.updated_at
                ? new Date(preferences.updated_at).toLocaleString('ro-RO')
                : 'nu există istoric'}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default NotificationSettings;
