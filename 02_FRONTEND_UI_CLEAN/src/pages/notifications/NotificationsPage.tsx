import React, { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import AutoProApiService from "@/services/autoproApi";
import { Loader2, Trash2 } from "lucide-react";

const NotificationsPage: React.FC = () => {
  const { toast } = useToast();
  const [userId, setUserId] = useState("admin");
  const [preferences, setPreferences] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    channel: "email",
    destination: "",
    enabled: true,
    quietHoursStart: "",
    quietHoursEnd: "",
  });

  useEffect(() => {
    if (userId) {
      loadPreferences(userId);
    }
  }, [userId]);

  const loadPreferences = async (id: string) => {
    try {
      setLoading(true);
      const response = await AutoProApiService.listNotificationPreferences(id);
      setPreferences(response.preferences ?? []);
    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca preferințele.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!form.destination) {
      toast({ title: "Destinație necesară", description: "Introduceți emailul sau numărul." });
      return;
    }
    try {
      setSaving(true);
      await AutoProApiService.upsertNotificationPreference({
        userId,
        channel: form.channel,
        destination: form.destination,
        enabled: form.enabled,
        quietHoursStart: form.quietHoursStart || null,
        quietHoursEnd: form.quietHoursEnd || null,
      });
      toast({ title: "Preferință salvată" });
      await loadPreferences(userId);
      setForm((prev) => ({ ...prev, destination: "" }));
    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut salva preferința.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (channel: string) => {
    try {
      await AutoProApiService.deleteNotificationPreference(userId, channel);
      toast({ title: "Preferință eliminată" });
      await loadPreferences(userId);
    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut șterge preferința.",
        variant: "destructive",
      });
    }
  };

  const sendTest = async () => {
    try {
      await AutoProApiService.sendTestNotification();
      toast({ title: "Notificare de test trimisă" });
    } catch (error) {
      toast({ title: "Eroare", description: "Nu s-a putut trimite notificarea de test.", variant: "destructive" });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold">Center notificări</h1>
          <p className="text-muted-foreground">
            Configurează canalele de notificare și trimite mesaje prin email sau SMS.
          </p>
        </div>
        <Button onClick={sendTest} variant="outline">
          Trimite test
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Preferințe utilizator</CardTitle>
          <CardDescription>Gestiunea preferințelor pentru notificări multi-canal.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="userId">Utilizator</Label>
              <Input
                id="userId"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Canal</Label>
              <Select value={form.channel} onValueChange={(value) => setForm((prev) => ({ ...prev, channel: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Selectează canal" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="email">Email</SelectItem>
                  <SelectItem value="sms">SMS</SelectItem>
                  <SelectItem value="whatsapp">WhatsApp</SelectItem>
                  <SelectItem value="push">Push</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="destination">Destinație</Label>
              <Input
                id="destination"
                placeholder={form.channel === "email" ? "ex: contact@example.com" : "+40700..."}
                value={form.destination}
                onChange={(e) => setForm((prev) => ({ ...prev, destination: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <Label>Status</Label>
              <div className="flex items-center gap-2">
                <Switch
                  checked={form.enabled}
                  onCheckedChange={(checked) => setForm((prev) => ({ ...prev, enabled: checked }))}
                />
                <span>{form.enabled ? "Activ" : "Inactiv"}</span>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="quietStart">Quiet hours start</Label>
              <Input
                id="quietStart"
                type="time"
                value={form.quietHoursStart}
                onChange={(e) => setForm((prev) => ({ ...prev, quietHoursStart: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="quietEnd">Quiet hours end</Label>
              <Input
                id="quietEnd"
                type="time"
                value={form.quietHoursEnd}
                onChange={(e) => setForm((prev) => ({ ...prev, quietHoursEnd: e.target.value }))}
              />
            </div>
          </div>
          <Button onClick={handleSave} disabled={saving}>
            {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Salvează preferința
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Preferințe configurate</CardTitle>
          <CardDescription>Listă de destinații și canale active pentru utilizatorul selectat.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {loading && <Loader2 className="h-6 w-6 animate-spin" />}
          {!loading && preferences.length === 0 && (
            <p className="text-sm text-muted-foreground">Nu există preferințe configurate.</p>
          )}
          {!loading &&
            preferences.map((pref) => (
              <Card key={pref.id} className="border border-border/60">
                <CardContent className="pt-4 flex flex-wrap items-center justify-between gap-2 text-sm">
                  <div className="space-y-1">
                    <div className="flex gap-2 items-center">
                      <Badge variant="secondary">{pref.channel}</Badge>
                      <span>{pref.destination}</span>
                    </div>
                    <div className="text-xs text-muted-foreground flex gap-4">
                      <span>Quiet start: {pref.quietHoursStart ?? "-"}</span>
                      <span>Quiet end: {pref.quietHoursEnd ?? "-"}</span>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-destructive"
                    onClick={() => handleDelete(pref.channel)}
                  >
                    <Trash2 className="mr-1 h-4 w-4" /> Șterge
                  </Button>
                </CardContent>
              </Card>
            ))}
        </CardContent>
      </Card>
    </div>
  );
};

export default NotificationsPage;

