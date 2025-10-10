import React, { useEffect, useMemo, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import AutoProApiService from "@/services/autoproApi";
import { useToast } from "@/hooks/use-toast";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Play, Plus, Trash2 } from "lucide-react";

interface AutomationRuleForm {
  name: string;
  description: string;
  cronExpression: string;
  timezone: string;
  isActive: boolean;
  triggerType: string;
  maxRetries: number;
  conditions: Array<{
    field: string;
    operator: string;
    target_value?: string;
    value_type: string;
  }>;
  actions: Array<{
    action_type: string;
    action_payload: Record<string, any>;
  }>;
}

const DEFAULT_FORM: AutomationRuleForm = {
  name: "",
  description: "",
  cronExpression: "0 9 * * *",
  timezone: "Europe/Bucharest",
  isActive: true,
  triggerType: "time",
  maxRetries: 3,
  conditions: [],
  actions: [
    {
      action_type: "send_email",
      action_payload: { subject: "Reminder", message: "Rule triggered" },
    },
  ],
};

const OPERATORS = [
  { value: "equals", label: "Este egal cu" },
  { value: "not_equals", label: "Nu este egal" },
  { value: "contains", label: "Conține" },
  { value: "greater_than", label: ">" },
  { value: "less_than", label: "<" },
];

const ACTIONS = [
  { value: "send_email", label: "Trimite Email" },
  { value: "send_sms", label: "Trimite SMS" },
  { value: "trigger_video_generation", label: "Generează Video" },
];

const AutomationPage: React.FC = () => {
  const { toast } = useToast();
  const [status, setStatus] = useState<any | null>(null);
  const [rules, setRules] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState<AutomationRuleForm>(DEFAULT_FORM);

  const validCron = useMemo(() => /^(\*|[0-9*/,-]+) (\*|[0-9*/,-]+) (\*|[0-9*/,-]+) (\*|[0-9*/,-]+) (\*|[0-9*/,-]+)$/.test(form.cronExpression), [form.cronExpression]);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    try {
      setLoading(true);
      const [statusRes, rulesRes, historyRes] = await Promise.all([
        AutoProApiService.getAutomationStatus(),
        AutoProApiService.listAutomationRules(),
        AutoProApiService.getAutomationHistory(20),
      ]);
      setStatus(statusRes);
      setRules(statusRes.rules ?? rulesRes.rules ?? []);
      setHistory(historyRes.history ?? []);
    } catch (error: any) {
      console.error("Failed to load automation data", error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca datele de automatizare.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => setForm(DEFAULT_FORM);

  const handleCreateRule = async () => {
    if (!form.name) {
      toast({ title: "Nume necesar", description: "Introduceți un nume pentru regulă." });
      return;
    }
    if (!validCron) {
      toast({
        title: "Cron invalid",
        description: "Expresia cron trebuie să aibă formatul corect.",
        variant: "destructive",
      });
      return;
    }

    try {
      setSubmitting(true);
      const payload = {
        ...form,
        conditions: form.conditions.map(({ field, operator, target_value, value_type }) => ({
          field,
          operator,
          value_type,
          target_value,
        })),
        actions: form.actions.map(({ action_type, action_payload }) => ({
          action_type,
          action_payload,
        })),
      };
      await AutoProApiService.createAutomationRule(payload);
      toast({ title: "Regulă creată" });
      resetForm();
      await loadAll();
    } catch (error: any) {
      console.error("Failed to create rule", error);
      toast({
        title: "Eroare",
        description: error?.response?.data?.detail ?? "Nu s-a putut crea regula.",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteRule = async (id: number) => {
    try {
      await AutoProApiService.deleteAutomationRule(id);
      toast({ title: "Regulă ștearsă" });
      await loadAll();
    } catch (error) {
      toast({ title: "Eroare", description: "Nu s-a putut șterge regula.", variant: "destructive" });
    }
  };

  const handleTriggerRule = async (id: number) => {
    try {
      await AutoProApiService.triggerAutomationRule(id);
      toast({ title: "Regulă programată" });
      await loadAll();
    } catch (error) {
      toast({ title: "Eroare", description: "Nu s-a putut declanșa regula.", variant: "destructive" });
    }
  };

  const handleRunDue = async () => {
    try {
      await AutoProApiService.runDueAutomationRules();
      toast({ title: "Reguli programate", description: "Worker-ul va procesa regulile." });
      await loadAll();
    } catch (error) {
      toast({ title: "Eroare", description: "Nu s-au putut lansa regulile programate.", variant: "destructive" });
    }
  };

  const addCondition = () =>
    setForm((prev) => ({
      ...prev,
      conditions: [
        ...prev.conditions,
        { field: "status", operator: "equals", value_type: "string", target_value: "" },
      ],
    }));

  const updateCondition = (idx: number, key: string, value: string) => {
    setForm((prev) => ({
      ...prev,
      conditions: prev.conditions.map((c, i) => (i === idx ? { ...c, [key]: value } : c)),
    }));
  };

  const removeCondition = (idx: number) =>
    setForm((prev) => ({
      ...prev,
      conditions: prev.conditions.filter((_, i) => i !== idx),
    }));

  const addAction = () =>
    setForm((prev) => ({
      ...prev,
      actions: [
        ...prev.actions,
        { action_type: "send_email", action_payload: { subject: "", message: "" } },
      ],
    }));

  const removeAction = (idx: number) =>
    setForm((prev) => ({
      ...prev,
      actions: prev.actions.filter((_, i) => i !== idx),
    }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold">Automation Orchestrator</h1>
          <p className="text-muted-foreground">
            Configurează reguli IF-THEN și programează-le cu editorul cron.
          </p>
        </div>
        <Button onClick={loadAll} variant="outline" disabled={loading}>
          {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Actualizează
        </Button>
      </div>

      <Tabs defaultValue="rules" className="w-full">
        <TabsList>
          <TabsTrigger value="rules">Reguli</TabsTrigger>
          <TabsTrigger value="history">Istoric</TabsTrigger>
          <TabsTrigger value="status">Status</TabsTrigger>
        </TabsList>

        <TabsContent value="rules" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Reguli existente</CardTitle>
              <CardDescription>Gestionează regulile active și declanșează-le manual.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-end">
                <Button variant="secondary" onClick={handleRunDue}>
                  <Play className="mr-2 h-4 w-4" /> Rulează regulile programate
                </Button>
              </div>
              <div className="space-y-3">
                {rules.length === 0 && (
                  <p className="text-sm text-muted-foreground">
                    Nu există încă reguli configurate. Adaugă prima regulă folosind formularul de mai jos.
                  </p>
                )}
                {rules.map((rule) => (
                  <Card key={rule.id} className="border border-border/60">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="flex items-center gap-2 text-lg">
                            {rule.name}
                            {rule.isActive && <Badge variant="outline">Activă</Badge>}
                          </CardTitle>
                          <CardDescription>{rule.description}</CardDescription>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button size="sm" variant="outline" onClick={() => handleTriggerRule(rule.id)}>
                            <Play className="mr-1 h-4 w-4" /> Rulează
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleDeleteRule(rule.id)}
                            className="text-destructive"
                          >
                            <Trash2 className="mr-1 h-4 w-4" /> Șterge
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="text-sm space-y-2">
                      <div className="flex flex-wrap gap-2">
                        <Badge variant="secondary">Cron: {rule.cronExpression ?? rule.cron_expression}</Badge>
                        <Badge variant="secondary">Timezone: {rule.timezone}</Badge>
                        <Badge variant="secondary">Trigger: {rule.triggerType ?? rule.trigger_type}</Badge>
                        <Badge variant="secondary">Max retries: {rule.maxRetries ?? rule.max_retries}</Badge>
                      </div>
                      <div>
                        <p className="font-medium">Condiții:</p>
                        <ul className="ml-4 list-disc">
                          {(rule.conditionLogic ?? rule.conditions ?? []).map((condition: any, idx: number) => (
                            <li key={idx}>
                              {condition.field} {condition.operator} {condition.target_value ?? condition.targetValue ?? condition.value}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <p className="font-medium">Acțiuni:</p>
                        <ul className="ml-4 list-disc">
                          {(rule.actionConfig ?? rule.actions ?? []).map((action: any, idx: number) => (
                            <li key={idx}>{action.action_type ?? action.actionType}</li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Adaugă regulă nouă</CardTitle>
              <CardDescription>Definește cron-ul și regulile IF/THEN pentru workflow automatizat.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="ruleName">Nume regulă</Label>
                  <Input
                    id="ruleName"
                    placeholder="ex: Follow-up lead nou"
                    value={form.name}
                    onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="timezone">Timezone</Label>
                  <Input
                    id="timezone"
                    value={form.timezone}
                    onChange={(e) => setForm((prev) => ({ ...prev, timezone: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cron">Cron Expression</Label>
                  <Input
                    id="cron"
                    value={form.cronExpression}
                    onChange={(e) => setForm((prev) => ({ ...prev, cronExpression: e.target.value }))}
                    className={!validCron ? "border-destructive" : ""}
                  />
                  {!validCron && (
                    <p className="text-xs text-destructive">Expresie cron invalidă. Exemplu: 0 9 * * *</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label>Activă</Label>
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={form.isActive}
                      onCheckedChange={(checked) => setForm((prev) => ({ ...prev, isActive: checked }))}
                    />
                    <span>{form.isActive ? "Regula este activă" : "Regula este dezactivată"}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Descriere</Label>
                <Textarea
                  value={form.description}
                  onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
                  placeholder="Descrie ce face această regulă"
                />
              </div>

              <Separator />

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Condiții IF</h3>
                  <Button onClick={addCondition} variant="outline" size="sm">
                    <Plus className="mr-1 h-4 w-4" /> Adaugă condiție
                  </Button>
                </div>
                {form.conditions.length === 0 && (
                  <p className="text-sm text-muted-foreground">
                    Fără condiții - regula se execută întotdeauna.
                  </p>
                )}
                <div className="space-y-3">
                  {form.conditions.map((condition, idx) => (
                    <Card key={idx} className="bg-muted/30">
                      <CardContent className="grid gap-3 md:grid-cols-4 pt-4">
                        <div className="space-y-2">
                          <Label>Field</Label>
                          <Input
                            value={condition.field}
                            onChange={(e) => updateCondition(idx, "field", e.target.value)}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Operator</Label>
                          <Select
                            value={condition.operator}
                            onValueChange={(value) => updateCondition(idx, "operator", value)}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Selectează" />
                            </SelectTrigger>
                            <SelectContent>
                              {OPERATORS.map((item) => (
                                <SelectItem key={item.value} value={item.value}>
                                  {item.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label>Valoare</Label>
                          <Input
                            value={condition.target_value ?? ""}
                            onChange={(e) => updateCondition(idx, "target_value", e.target.value)}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Tip</Label>
                          <Select
                            value={condition.value_type}
                            onValueChange={(value) => updateCondition(idx, "value_type", value)}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="string" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="string">String</SelectItem>
                              <SelectItem value="int">Integer</SelectItem>
                              <SelectItem value="float">Float</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <Button
                          variant="ghost"
                          className="md:col-span-4 justify-start text-destructive"
                          onClick={() => removeCondition(idx)}
                        >
                          <Trash2 className="mr-2 h-4 w-4" /> Elimină condiția
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              <Separator />

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Acțiuni THEN</h3>
                  <Button onClick={addAction} variant="outline" size="sm">
                    <Plus className="mr-1 h-4 w-4" /> Adaugă acțiune
                  </Button>
                </div>
                <div className="space-y-3">
                  {form.actions.map((action, idx) => (
                    <Card key={idx} className="bg-muted/30">
                      <CardContent className="grid gap-3 md:grid-cols-3 pt-4">
                        <div className="space-y-2">
                          <Label>Tip acțiune</Label>
                          <Select
                            value={action.action_type}
                            onValueChange={(value) =>
                              setForm((prev) => ({
                                ...prev,
                                actions: prev.actions.map((a, i) =>
                                  i === idx ? { ...a, action_type: value } : a
                                ),
                              }))
                            }
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Selectează" />
                            </SelectTrigger>
                            <SelectContent>
                              {ACTIONS.map((item) => (
                                <SelectItem key={item.value} value={item.value}>
                                  {item.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2 md:col-span-2">
                          <Label>Parametri</Label>
                          <Textarea
                            value={JSON.stringify(action.action_payload)}
                            onChange={(e) => {
                              try {
                                const parsed = JSON.parse(e.target.value || "{}");
                                setForm((prev) => ({
                                  ...prev,
                                  actions: prev.actions.map((a, i) =>
                                    i === idx ? { ...a, action_payload: parsed } : a
                                  ),
                                }));
                              } catch (err) {
                                // ignore invalid JSON until user fixes it
                              }
                            }}
                          />
                        </div>
                        <Button
                          variant="ghost"
                          className="md:col-span-3 justify-start text-destructive"
                          onClick={() => removeAction(idx)}
                        >
                          <Trash2 className="mr-2 h-4 w-4" /> Elimină acțiunea
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              <Button onClick={handleCreateRule} disabled={submitting}>
                {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Salvează regula
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Istoric execuții</CardTitle>
              <CardDescription>Monitorizează ultimele execuții și retry-uri.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {history.length === 0 && <p className="text-sm text-muted-foreground">Nu există rulări recente.</p>}
              {history.map((entry) => (
                <Card key={entry.id} className="border border-muted">
                  <CardContent className="pt-4 text-sm space-y-2">
                    <div className="flex justify-between">
                      <span className="font-medium">Regulă #{entry.ruleId}</span>
                      <Badge variant={entry.status === "success" ? "default" : entry.status === "failed" ? "destructive" : "outline"}>
                        {entry.status}
                      </Badge>
                    </div>
                    <div className="grid md:grid-cols-2 text-muted-foreground text-xs gap-2">
                      <span>Start: {entry.startedAt ?? "-"}</span>
                      <span>Final: {entry.finishedAt ?? "-"}</span>
                      <span>Trigger: {entry.triggeredBy}</span>
                      <span>Încercare: {entry.attempt}</span>
                    </div>
                    {entry.errorMessage && (
                      <p className="text-xs text-destructive">Eroare: {entry.errorMessage}</p>
                    )}
                  </CardContent>
                </Card>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="status" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Status automatizare</CardTitle>
              <CardDescription>Un rezumat rapid al regulilor și execuțiilor.</CardDescription>
            </CardHeader>
            <CardContent className="grid md:grid-cols-3 gap-4">
              <Card className="border border-muted">
                <CardContent className="pt-6">
                  <p className="text-sm text-muted-foreground">Total reguli</p>
                  <p className="text-3xl font-bold">{status?.totalRules ?? rules.length}</p>
                </CardContent>
              </Card>
              <Card className="border border-muted">
                <CardContent className="pt-6">
                  <p className="text-sm text-muted-foreground">Reguli active</p>
                  <p className="text-3xl font-bold">{status?.activeRules ?? rules.filter((r) => r.isActive).length}</p>
                </CardContent>
              </Card>
              <Card className="border border-muted">
                <CardContent className="pt-6">
                  <p className="text-sm text-muted-foreground">Ultima execuție</p>
                  <p className="text-3xl font-bold">
                    {status?.lastRuns?.[0]?.startedAt ? new Date(status.lastRuns[0].startedAt).toLocaleString("ro-RO") : "-"}
                  </p>
                </CardContent>
              </Card>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AutomationPage;

