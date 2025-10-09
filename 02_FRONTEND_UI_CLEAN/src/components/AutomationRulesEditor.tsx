import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { 
  Zap, 
  Plus, 
  Edit, 
  Trash2, 
  Play, 
  Pause,
  Settings,
  Clock,
  CheckCircle,
  AlertTriangle,
  Users,
  Mail,
  MessageSquare,
  Calendar,
  FileText
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface AutomationRule {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  trigger: {
    type: 'lead_created' | 'lead_status_changed' | 'payment_received' | 'email_opened' | 'time_based';
    conditions: Array<{
      field: string;
      operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than';
      value: string;
    }>;
  };
  actions: Array<{
    type: 'send_email' | 'send_sms' | 'update_lead_status' | 'create_task' | 'send_notification';
    parameters: Record<string, string | number | boolean>;
  }>;
  last_executed: string | null;
  execution_count: number;
  success_count: number;
  created_at: string;
}

const TRIGGER_TYPES = [
  {
    value: 'lead_created',
    label: 'Lead Creat',
    description: 'Se declanșează când un lead nou este creat',
    icon: Users
  },
  {
    value: 'lead_status_changed',
    label: 'Status Lead Schimbat',
    description: 'Se declanșează când statusul unui lead se schimbă',
    icon: CheckCircle
  },
  {
    value: 'payment_received',
    label: 'Plată Primită',
    description: 'Se declanșează când o plată este confirmată',
    icon: CheckCircle
  },
  {
    value: 'email_opened',
    label: 'Email Deschis',
    description: 'Se declanșează când un email este deschis',
    icon: Mail
  },
  {
    value: 'time_based',
    label: 'Bazat pe Timp',
    description: 'Se declanșează la ore specifice sau intervale',
    icon: Clock
  }
];

const ACTION_TYPES = [
  {
    value: 'send_email',
    label: 'Trimite Email',
    description: 'Trimite un email automat',
    icon: Mail
  },
  {
    value: 'send_sms',
    label: 'Trimite SMS',
    description: 'Trimite un SMS automat',
    icon: MessageSquare
  },
  {
    value: 'update_lead_status',
    label: 'Actualizează Status Lead',
    description: 'Schimbă statusul unui lead',
    icon: CheckCircle
  },
  {
    value: 'create_task',
    label: 'Creează Task',
    description: 'Creează un task automat',
    icon: FileText
  },
  {
    value: 'send_notification',
    label: 'Trimite Notificare',
    description: 'Trimite notificare în aplicație',
    icon: AlertTriangle
  }
];

const OPERATORS = [
  { value: 'equals', label: 'Este egal cu' },
  { value: 'not_equals', label: 'Nu este egal cu' },
  { value: 'contains', label: 'Conține' },
  { value: 'greater_than', label: 'Mai mare decât' },
  { value: 'less_than', label: 'Mai mic decât' }
];

const LEAD_STATUSES = ['new', 'contacted', 'in-progress', 'completed', 'rejected'];

export default function AutomationRulesEditor() {
  const { toast } = useToast();
  const [rules, setRules] = useState<AutomationRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<AutomationRule | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    trigger: {
      type: 'lead_created' as AutomationRule['trigger']['type'],
      conditions: [{ field: 'status', operator: 'equals' as const, value: '' }]
    },
    actions: [{ type: 'send_email' as const, parameters: {} }]
  });

  useEffect(() => {
    loadAutomationRules();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadAutomationRules = async () => {
    try {
      setLoading(true);
      // Simulated data - în producție ar fi API call
      const mockRules: AutomationRule[] = [
        {
          id: '1',
          name: 'Welcome Email pentru Leads Noi',
          description: 'Trimite email de bun venit când un lead nou este creat',
          enabled: true,
          trigger: {
            type: 'lead_created',
            conditions: []
          },
          actions: [
            {
              type: 'send_email',
              parameters: {
                template: 'welcome',
                subject: 'Bun venit la AutoPro Daune',
                delay: 0
              }
            }
          ],
          last_executed: '2025-01-15T10:30:00Z',
          execution_count: 45,
          success_count: 42,
          created_at: '2025-01-01T00:00:00Z'
        },
        {
          id: '2',
          name: 'Follow-up pentru Leads în Progres',
          description: 'Trimite email de follow-up când un lead trece în status "in-progress"',
          enabled: true,
          trigger: {
            type: 'lead_status_changed',
            conditions: [
              { field: 'status', operator: 'equals', value: 'in-progress' }
            ]
          },
          actions: [
            {
              type: 'send_email',
              parameters: {
                template: 'follow_up',
                subject: 'Actualizare caz - AutoPro Daune',
                delay: 3600 // 1 hour delay
              }
            },
            {
              type: 'create_task',
              parameters: {
                title: 'Contactare client pentru update',
                description: 'Contactează clientul pentru a discuta progresul cazului',
                due_date: '+3 days'
              }
            }
          ],
          last_executed: '2025-01-14T15:20:00Z',
          execution_count: 23,
          success_count: 21,
          created_at: '2025-01-01T00:00:00Z'
        },
        {
          id: '3',
          name: 'Reminder Plăți Restante',
          description: 'Trimite reminder pentru plăți care au trecut de scadență',
          enabled: false,
          trigger: {
            type: 'time_based',
            conditions: [
              { field: 'time', operator: 'equals', value: 'daily' },
              { field: 'hour', operator: 'equals', value: '09:00' }
            ]
          },
          actions: [
            {
              type: 'send_email',
              parameters: {
                template: 'payment_reminder',
                subject: 'Reminder: Factură restantă',
                delay: 0
              }
            }
          ],
          last_executed: null,
          execution_count: 0,
          success_count: 0,
          created_at: '2025-01-10T00:00:00Z'
        }
      ];
      setRules(mockRules);
    } catch (error) {
      console.error('Failed to load automation rules:', error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca regulile de automatizare.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const addCondition = () => {
    setFormData(prev => ({
      ...prev,
      trigger: {
        ...prev.trigger,
        conditions: [...prev.trigger.conditions, { field: '', operator: 'equals', value: '' }]
      }
    }));
  };

  const updateCondition = (index: number, field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      trigger: {
        ...prev.trigger,
        conditions: prev.trigger.conditions.map((condition, i) => 
          i === index ? { ...condition, [field]: value } : condition
        )
      }
    }));
  };

  const removeCondition = (index: number) => {
    setFormData(prev => ({
      ...prev,
      trigger: {
        ...prev.trigger,
        conditions: prev.trigger.conditions.filter((_, i) => i !== index)
      }
    }));
  };

  const addAction = () => {
    setFormData(prev => ({
      ...prev,
      actions: [...prev.actions, { type: 'send_email', parameters: {} }]
    }));
  };

  const updateAction = (index: number, field: string, value: string | number | boolean) => {
    setFormData(prev => ({
      ...prev,
      actions: prev.actions.map((action, i) => 
        i === index ? { ...action, [field]: value } : action
      )
    }));
  };

  const removeAction = (index: number) => {
    setFormData(prev => ({
      ...prev,
      actions: prev.actions.filter((_, i) => i !== index)
    }));
  };

  const handleCreateRule = async () => {
    try {
      const newRule: AutomationRule = {
        id: Date.now().toString(),
        name: formData.name,
        description: formData.description,
        enabled: true,
        trigger: formData.trigger,
        actions: formData.actions,
        last_executed: null,
        execution_count: 0,
        success_count: 0,
        created_at: new Date().toISOString()
      };

      setRules(prev => [newRule, ...prev]);
      
      toast({
        title: "Regulă creată",
        description: `Regula "${newRule.name}" a fost creată cu succes.`,
      });

      // Reset form
      setFormData({
        name: '',
        description: '',
        trigger: {
          type: 'lead_created',
          conditions: [{ field: 'status', operator: 'equals', value: '' }]
        },
        actions: [{ type: 'send_email', parameters: {} }]
      });
      setIsCreateDialogOpen(false);

    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut crea regula.",
        variant: "destructive",
      });
    }
  };

  const toggleRule = async (ruleId: string) => {
    try {
      setRules(prev => prev.map(rule => 
        rule.id === ruleId ? { ...rule, enabled: !rule.enabled } : rule
      ));
      
      toast({
        title: "Regulă actualizată",
        description: "Statusul regulii a fost actualizat.",
      });
    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut actualiza regula.",
        variant: "destructive",
      });
    }
  };

  const deleteRule = async (ruleId: string) => {
    try {
      setRules(prev => prev.filter(rule => rule.id !== ruleId));
      toast({
        title: "Regulă ștearsă",
        description: "Regula a fost ștearsă cu succes.",
      });
    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut șterge regula.",
        variant: "destructive",
      });
    }
  };

  const getTriggerIcon = (type: AutomationRule['trigger']['type']) => {
    const triggerType = TRIGGER_TYPES.find(t => t.value === type);
    return triggerType ? triggerType.icon : Settings;
  };

  const getActionIcon = (type: AutomationRule['actions'][0]['type']) => {
    const actionType = ACTION_TYPES.find(a => a.value === type);
    return actionType ? actionType.icon : Settings;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ro-RO');
  };

  const getSuccessRate = (rule: AutomationRule) => {
    if (rule.execution_count === 0) return 0;
    return Math.round((rule.success_count / rule.execution_count) * 100);
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Reguli</p>
                <p className="text-2xl font-bold">{rules.length}</p>
              </div>
              <Zap className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active</p>
                <p className="text-2xl font-bold text-green-600">
                  {rules.filter(rule => rule.enabled).length}
                </p>
              </div>
              <Play className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Execuții Totale</p>
                <p className="text-2xl font-bold text-blue-600">
                  {rules.reduce((sum, rule) => sum + rule.execution_count, 0)}
                </p>
              </div>
              <Clock className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Rata Succes</p>
                <p className="text-2xl font-bold text-purple-600">
                  {rules.length > 0 ? Math.round(rules.reduce((sum, rule) => sum + getSuccessRate(rule), 0) / rules.length) : 0}%
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Create Rule Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogTrigger asChild>
          <Button className="w-full">
            <Plus className="w-4 h-4 mr-2" />
            Creează Regulă Nouă
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Creează Regulă de Automatizare</DialogTitle>
            <DialogDescription>
              Configurează o regulă IF-THEN pentru automatizarea proceselor.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Nume Regulă</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="ex: Welcome Email pentru Leads Noi"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Tip Trigger</label>
                <Select
                  value={formData.trigger.type}
                  onValueChange={(value: AutomationRule['trigger']['type']) => 
                    setFormData(prev => ({
                      ...prev,
                      trigger: { ...prev.trigger, type: value }
                    }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {TRIGGER_TYPES.map(trigger => {
                      const TriggerIcon = trigger.icon;
                      return (
                        <SelectItem key={trigger.value} value={trigger.value}>
                          <div className="flex items-center gap-2">
                            <TriggerIcon className="w-4 h-4" />
                            <div>
                              <div className="font-medium">{trigger.label}</div>
                              <div className="text-xs text-gray-500">{trigger.description}</div>
                            </div>
                          </div>
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Descriere</label>
              <Input
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Descrierea regulii de automatizare..."
              />
            </div>

            {/* Trigger Conditions */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Condiții Trigger (IF)</h3>
                <Button variant="outline" size="sm" onClick={addCondition}>
                  <Plus className="w-4 h-4 mr-2" />
                  Adaugă Condiție
                </Button>
              </div>

              <div className="space-y-3">
                {formData.trigger.conditions.map((condition, index) => (
                  <div key={index} className="grid grid-cols-12 gap-2 p-3 border rounded-lg">
                    <div className="col-span-3">
                      <Select
                        value={condition.field}
                        onValueChange={(value) => updateCondition(index, 'field', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Câmp" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="status">Status</SelectItem>
                          <SelectItem value="priority">Prioritate</SelectItem>
                          <SelectItem value="source">Sursă</SelectItem>
                          <SelectItem value="amount">Sumă</SelectItem>
                          <SelectItem value="time">Timp</SelectItem>
                          <SelectItem value="hour">Ora</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="col-span-3">
                      <Select
                        value={condition.operator}
                        onValueChange={(value) => updateCondition(index, 'operator', value)}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {OPERATORS.map(op => (
                            <SelectItem key={op.value} value={op.value}>
                              {op.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="col-span-4">
                      {condition.field === 'status' ? (
                        <Select
                          value={condition.value}
                          onValueChange={(value) => updateCondition(index, 'value', value)}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Valoare" />
                          </SelectTrigger>
                          <SelectContent>
                            {LEAD_STATUSES.map(status => (
                              <SelectItem key={status} value={status}>
                                {status}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      ) : (
                        <Input
                          value={condition.value}
                          onChange={(e) => updateCondition(index, 'value', e.target.value)}
                          placeholder="Valoare"
                        />
                      )}
                    </div>
                    <div className="col-span-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeCondition(index)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Acțiuni (THEN)</h3>
                <Button variant="outline" size="sm" onClick={addAction}>
                  <Plus className="w-4 h-4 mr-2" />
                  Adaugă Acțiune
                </Button>
              </div>

              <div className="space-y-3">
                {formData.actions.map((action, index) => {
                  const ActionIcon = getActionIcon(action.type);
                  return (
                    <div key={index} className="grid grid-cols-12 gap-2 p-3 border rounded-lg">
                      <div className="col-span-3">
                        <Select
                          value={action.type}
                          onValueChange={(value) => updateAction(index, 'type', value)}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {ACTION_TYPES.map(actionType => {
                              const ActionTypeIcon = actionType.icon;
                              return (
                                <SelectItem key={actionType.value} value={actionType.value}>
                                  <div className="flex items-center gap-2">
                                    <ActionTypeIcon className="w-4 h-4" />
                                    <div>
                                      <div className="font-medium">{actionType.label}</div>
                                      <div className="text-xs text-gray-500">{actionType.description}</div>
                                    </div>
                                  </div>
                                </SelectItem>
                              );
                            })}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="col-span-7">
                        {action.type === 'send_email' && (
                          <div className="grid grid-cols-2 gap-2">
                            <Input
                              placeholder="Template"
                              value={action.parameters.template || ''}
                              onChange={(e) => updateAction(index, 'parameters', {
                                ...action.parameters,
                                template: e.target.value
                              })}
                            />
                            <Input
                              placeholder="Delay (secunde)"
                              type="number"
                              value={action.parameters.delay || ''}
                              onChange={(e) => updateAction(index, 'parameters', {
                                ...action.parameters,
                                delay: parseInt(e.target.value) || 0
                              })}
                            />
                          </div>
                        )}
                        {action.type === 'update_lead_status' && (
                          <Select
                            value={action.parameters.status || ''}
                            onValueChange={(value) => updateAction(index, 'parameters', {
                              ...action.parameters,
                              status: value
                            })}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Status nou" />
                            </SelectTrigger>
                            <SelectContent>
                              {LEAD_STATUSES.map(status => (
                                <SelectItem key={status} value={status}>
                                  {status}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        )}
                      </div>
                      <div className="col-span-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeAction(index)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsCreateDialogOpen(false)}
            >
              Anulează
            </Button>
            <Button
              onClick={handleCreateRule}
              disabled={!formData.name || formData.actions.length === 0}
            >
              Creează Regulă
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Rules List */}
      <Card>
        <CardHeader>
          <CardTitle>Reguli de Automatizare</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Se încarcă...</div>
          ) : rules.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Zap className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>Nu există reguli de automatizare în sistem.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {rules.map(rule => {
                const TriggerIcon = getTriggerIcon(rule.trigger.type);
                const successRate = getSuccessRate(rule);
                
                return (
                  <div key={rule.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className={`w-3 h-3 rounded-full ${rule.enabled ? 'bg-green-500' : 'bg-gray-400'}`} />
                      <TriggerIcon className="w-5 h-5 text-blue-500" />
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold">{rule.name}</h3>
                          <Badge variant={rule.enabled ? "default" : "secondary"}>
                            {rule.enabled ? 'Activ' : 'Inactiv'}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-1">{rule.description}</p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>Execuții: {rule.execution_count}</span>
                          <span>Succes: {successRate}%</span>
                          {rule.last_executed && (
                            <span>Ultima: {formatDate(rule.last_executed)}</span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      <Switch
                        checked={rule.enabled}
                        onCheckedChange={() => toggleRule(rule.id)}
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setEditingRule(rule)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteRule(rule.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
