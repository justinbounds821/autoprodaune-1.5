import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
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
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
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
  Edit,
  Trash2,
  Plus,
  Eye,
  Filter,
  Download,
  Search,
  Upload,
  Paperclip,
  X
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface Lead {
  id: string;
  name: string;
  phone: string;
  email?: string;
  details: string;
  status: 'new' | 'contacted' | 'in-progress' | 'completed' | 'rejected';
  priority: 'low' | 'medium' | 'high';
  createdAt: string;
  updatedAt: string;
  files: string[];
  notes: string[];
  source: 'website' | 'whatsapp' | 'referral' | 'social_media';
  assignedTo?: string;
  score?: number; // Lead score (0-100)
}

interface KPIData {
  totalLeads: number;
  newLeads: number;
  conversionRate: number;
  averageResponseTime: number;
  completedCases: number;
  monthlyGrowth: number;
}

const LeadManagement: React.FC = () => {
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

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [isDetailsDialogOpen, setIsDetailsDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [scoringLeadId, setScoringLeadId] = useState<string | null>(null);
  const [scoringAllLeads, setScoringAllLeads] = useState(false);
  
  // Timeline modal states
  const [showTimelineModal, setShowTimelineModal] = useState(false);
  const [timelineLeadId, setTimelineLeadId] = useState<string | null>(null);
  const [activities, setActivities] = useState<any[]>([]);
  const [loadingActivities, setLoadingActivities] = useState(false);
  const [newNote, setNewNote] = useState('');
  const [addingNote, setAddingNote] = useState(false);
  
  // Bulk operations states
  const [selectedLeads, setSelectedLeads] = useState<Set<string>>(new Set());
  const [bulkUpdating, setBulkUpdating] = useState(false);
  const [bulkStatus, setBulkStatus] = useState<string>('');

  // Load leads and KPI data
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        let mappedLeads: Lead[] = [];

        // Load leads from API
        const leadsResponse = await fetch('/api/leads/');
        if (leadsResponse.ok) {
          const leadsData = await leadsResponse.json();
          // Map API response to frontend format
          mappedLeads = (leadsData.items || []).map((lead: any) => ({
            id: lead.id.toString(),
            name: lead.name,
            phone: lead.phone,
            email: lead.email || '',
            details: lead.details,
            status: lead.status,
            priority: lead.priority || 'medium',
            damageType: lead.damage_type || 'Other',
            location: lead.location || '',
            createdAt: lead.created_at,
            updatedAt: lead.updated_at
          }));
          setLeads(mappedLeads);
        }

        // Calculate KPIs from leads data
        const totalLeads = mappedLeads ? mappedLeads.length : 0;
        const newLeads = mappedLeads ? mappedLeads.filter(lead => lead.status === 'new').length : 0;
        const completedCases = mappedLeads ? mappedLeads.filter(lead => lead.status === 'completed').length : 0;
        const conversionRate = totalLeads > 0 ? (completedCases / totalLeads) * 100 : 0;

        setKpis({
          totalLeads,
          newLeads,
          conversionRate: Math.round(conversionRate * 10) / 10,
          averageResponseTime: 2.5, // hours - placeholder
          completedCases,
          monthlyGrowth: 15.3 // percentage - placeholder
        });

      } catch (error) {
        console.error('Error loading lead data:', error);
        toast({
          title: "Eroare la încărcarea datelor",
          description: "Nu s-au putut încărca datele de la server.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [toast]);

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
      case 'high': return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'medium': return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'low': return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
  };

  const getSourceBadge = (source: Lead['source']) => {
    const sourceConfig = {
      website: { label: 'Website', variant: 'default' as const },
      whatsapp: { label: 'WhatsApp', variant: 'secondary' as const },
      referral: { label: 'Referral', variant: 'outline' as const },
      social_media: { label: 'Social', variant: 'secondary' as const }
    };

    return sourceConfig[source] || { label: source, variant: 'default' as const };
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
            lead.id === leadId ? { ...lead, status: newStatus, updatedAt: new Date().toISOString() } : lead
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

  const filteredLeads = (leads || []).filter(lead => {
    const matchesSearch = lead.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         lead.phone.includes(searchTerm) ||
                         lead.details.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (lead.email && lead.email.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesStatus = statusFilter === 'all' || lead.status === statusFilter;
    const matchesPriority = priorityFilter === 'all' || lead.priority === priorityFilter;

    return matchesSearch && matchesStatus && matchesPriority;
  });

  const handleViewDetails = (lead: Lead) => {
    setSelectedLead(lead);
    setIsDetailsDialogOpen(true);
  };

  const calculateLeadScore = async (leadId: string) => {
    try {
      setScoringLeadId(leadId);
      const response = await fetch(`/api/leads/${leadId}/score`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        // Update lead with new score
        setLeads(prevLeads => 
          prevLeads.map(lead => 
            lead.id === leadId 
              ? { ...lead, score: data.score, priority: data.priority }
              : lead
          )
        );
        toast({
          title: "Score calculat!",
          description: `Lead-ul a primit scorul: ${data.score}/100`,
        });
      } else {
        throw new Error('Failed to calculate score');
      }
    } catch (error) {
      console.error('Error calculating lead score:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut calcula scorul lead-ului.",
        variant: "destructive",
      });
    } finally {
      setScoringLeadId(null);
    }
  };

  // Timeline functions
  const openTimeline = async (leadId: string) => {
    setTimelineLeadId(leadId);
    setShowTimelineModal(true);
    await loadTimeline(leadId);
  };

  const loadTimeline = async (leadId: string) => {
    try {
      setLoadingActivities(true);
      const response = await fetch(`/api/leads/${leadId}/timeline`);
      
      if (response.ok) {
        const data = await response.json();
        setActivities(data.activities || []);
      }
    } catch (error) {
      console.error('Failed to load timeline:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut încărca timeline-ul.",
        variant: "destructive",
      });
    } finally {
      setLoadingActivities(false);
    }
  };

  const handleAddNote = async () => {
    if (!newNote.trim() || !timelineLeadId) return;

    try {
      setAddingNote(true);
      const response = await fetch(`/api/leads/${timelineLeadId}/activity`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          activity_type: 'note',
          description: newNote,
          performed_by: 'admin'
        }),
      });

      if (response.ok) {
        setNewNote('');
        await loadTimeline(timelineLeadId);
        toast({
          title: "Notă adăugată!",
          description: "Notița a fost salvată cu succes.",
        });
      }
    } catch (error) {
      console.error('Failed to add note:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut adăuga notița.",
        variant: "destructive",
      });
    } finally {
      setAddingNote(false);
    }
  };

  // Bulk operations
  const toggleLeadSelection = (leadId: string) => {
    setSelectedLeads(prev => {
      const newSet = new Set(prev);
      if (newSet.has(leadId)) {
        newSet.delete(leadId);
      } else {
        newSet.add(leadId);
      }
      return newSet;
    });
  };

  const selectAllLeads = () => {
    const allIds = new Set((filteredLeads || []).map(l => l.id));
    setSelectedLeads(allIds);
  };

  const deselectAllLeads = () => {
    setSelectedLeads(new Set());
  };

  const handleBulkUpdate = async () => {
    if (selectedLeads.size === 0 || !bulkStatus) {
      toast({
        title: "Selecție incompletă",
        description: "Selectează lead-uri și un status.",
        variant: "destructive",
      });
      return;
    }

    try {
      setBulkUpdating(true);
      const response = await fetch('/api/leads/bulk-update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lead_ids: Array.from(selectedLeads),
          updates: { status: bulkStatus }
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Update leads in UI
        setLeads(prev => prev.map(lead => 
          selectedLeads.has(lead.id) 
            ? { ...lead, status: bulkStatus as Lead['status'] }
            : lead
        ));
        
        setSelectedLeads(new Set());
        setBulkStatus('');
        
        toast({
          title: "✅ Actualizare completă!",
          description: `${data.updated_count} lead-uri au fost actualizate.`,
        });
      }
    } catch (error) {
      console.error('Bulk update failed:', error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut actualiza lead-urile.",
        variant: "destructive",
      });
    } finally {
      setBulkUpdating(false);
    }
  };

  const handleExportLeads = async () => {
    try {
      const response = await fetch('/api/leads/export?format=csv', {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        
        // Download CSV
        const blob = new Blob([data.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `leads-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        toast({
          title: "✅ Export complet!",
          description: `${data.count} lead-uri au fost exportate.`,
        });
      }
    } catch (error) {
      console.error('Export failed:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut exporta fișierul.",
        variant: "destructive",
      });
    }
  };

  const scoreAllLeads = async () => {
    try {
      setScoringAllLeads(true);
      const response = await fetch('/api/leads/batch-score', {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: "Toate lead-urile au fost scoruate!",
          description: `${data.scored_count} lead-uri au primit scoruri.`,
        });
        // Reload leads to get updated scores
        const leadsResponse = await fetch('/api/leads/');
        if (leadsResponse.ok) {
          const leadsData = await leadsResponse.json();
          const mappedLeads: Lead[] = (leadsData.items || []).map((lead: any) => ({
            id: String(lead.id),
            name: lead.name,
            phone: lead.phone,
            email: lead.email,
            details: lead.details || lead.damage_description || '',
            status: lead.status || 'new',
            priority: lead.priority || 'medium',
            createdAt: lead.created_at || new Date().toISOString(),
            updatedAt: lead.updated_at || new Date().toISOString(),
            files: lead.files || [],
            notes: [],
            source: lead.source || 'website',
            assignedTo: lead.assigned_to,
            score: lead.score
          }));
          setLeads(mappedLeads);
        }
      } else {
        throw new Error('Failed to score all leads');
      }
    } catch (error) {
      console.error('Error scoring all leads:', error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut scora toate lead-urile.",
        variant: "destructive",
      });
    } finally {
      setScoringAllLeads(false);
    }
  };

  const exportLeadsOld = () => {
    // OLD: Simple CSV export functionality (kept as backup)
    const csvData = (filteredLeads || []).map(lead => ({
      'Nume': lead.name,
      'Telefon': lead.phone,
      'Email': lead.email || '',
      'Status': lead.status,
      'Prioritate': lead.priority,
      'Score': lead.score || 0,
      'Sursa': lead.source,
      'Data Creare': new Date(lead.createdAt).toLocaleDateString('ro-RO')
    }));

    const csv = [
      Object.keys(csvData[0]).join(','),
      ...csvData.map(row => Object.values(row).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'leads-export.csv';
    a.click();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Lead Management</h1>
          <p className="text-muted-foreground">Manage and track all customer leads</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Bulk operations */}
          {selectedLeads.size > 0 && (
            <>
              <Badge variant="outline" className="text-base px-3 py-1">
                {selectedLeads.size} selectate
              </Badge>
              <Select value={bulkStatus} onValueChange={setBulkStatus}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="Status nou" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="contacted">Contactat</SelectItem>
                  <SelectItem value="in-progress">În progres</SelectItem>
                  <SelectItem value="completed">Finalizat</SelectItem>
                  <SelectItem value="rejected">Respins</SelectItem>
                </SelectContent>
              </Select>
              <Button 
                variant="default" 
                size="sm"
                onClick={handleBulkUpdate}
                disabled={bulkUpdating || !bulkStatus}
              >
                {bulkUpdating ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Actualizez...
                  </>
                ) : (
                  'Actualizează'
                )}
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={deselectAllLeads}
              >
                Deselectează
              </Button>
            </>
          )}
          
          <Button 
            variant="outline" 
            onClick={scoreAllLeads}
            disabled={scoringAllLeads || !leads || leads.length === 0}
          >
            {scoringAllLeads ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <BarChart3 className="w-4 h-4 mr-2" />
            )}
            {scoringAllLeads ? 'Calculez...' : 'Score All'}
          </Button>
          <Button variant="outline" onClick={handleExportLeads}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Lead
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
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

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Caută lead-uri..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>

            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toate</SelectItem>
                <SelectItem value="new">Nou</SelectItem>
                <SelectItem value="contacted">Contactat</SelectItem>
                <SelectItem value="in-progress">În progres</SelectItem>
                <SelectItem value="completed">Finalizat</SelectItem>
                <SelectItem value="rejected">Respins</SelectItem>
              </SelectContent>
            </Select>

            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Prioritate" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toate</SelectItem>
                <SelectItem value="high">Înaltă</SelectItem>
                <SelectItem value="medium">Medie</SelectItem>
                <SelectItem value="low">Scăzută</SelectItem>
              </SelectContent>
            </Select>

            <Button variant="outline" size="sm">
              <Filter className="w-4 h-4 mr-2" />
              Mai multe filtre
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Leads Table */}
      <Card>
        <CardHeader>
          <CardTitle>Lead-uri ({filteredLeads ? filteredLeads.length : 0})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredLeads.map((lead) => {
              const sourceConfig = getSourceBadge(lead.source);

              return (
                <div key={lead.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 relative">
                  <div className="absolute top-3 left-3">
                    <input
                      type="checkbox"
                      checked={selectedLeads.has(lead.id)}
                      onChange={() => toggleLeadSelection(lead.id)}
                      className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                    />
                  </div>
                  <div className="flex items-center space-x-4 flex-1 ml-8">
                    {getPriorityIcon(lead.priority)}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium">{lead.name}</h3>
                        <Badge variant={sourceConfig.variant}>{sourceConfig.label}</Badge>
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Phone className="w-3 h-3" />
                          <span>{lead.phone}</span>
                        </div>
                        {lead.email && (
                          <div className="flex items-center gap-1">
                            <Mail className="w-3 h-3" />
                            <span>{lead.email}</span>
                          </div>
                        )}
                        <div className="flex items-center gap-1">
                          <FileText className="w-3 h-3" />
                          <span>{lead.files ? lead.files.length : 0} fișiere</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          <span>{new Date(lead.createdAt).toLocaleDateString('ro-RO')}</span>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{lead.details}</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    {lead.score !== undefined && (
                      <Badge 
                        variant="outline"
                        className={
                          lead.score >= 75 ? 'bg-green-50 text-green-700 border-green-200' :
                          lead.score >= 50 ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
                          'bg-gray-50 text-gray-700 border-gray-200'
                        }
                      >
                        Score: {lead.score}
                      </Badge>
                    )}
                    
                    <Badge className={getStatusColor(lead.status)}>
                      {lead.status}
                    </Badge>

                    <Select
                      value={lead.status}
                      onValueChange={(value) => updateLeadStatus(lead.id, value as Lead['status'])}
                    >
                      <SelectTrigger className="w-[120px]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="new">Nou</SelectItem>
                        <SelectItem value="contacted">Contactat</SelectItem>
                        <SelectItem value="in-progress">În progres</SelectItem>
                        <SelectItem value="completed">Finalizat</SelectItem>
                        <SelectItem value="rejected">Respins</SelectItem>
                      </SelectContent>
                    </Select>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => calculateLeadScore(lead.id)}
                      disabled={scoringLeadId === lead.id}
                      title="Calculate Lead Score"
                    >
                      {scoringLeadId === lead.id ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                      ) : (
                        <BarChart3 className="w-4 h-4" />
                      )}
                    </Button>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => openTimeline(lead.id)}
                      title="Activity Timeline"
                    >
                      <Clock className="w-4 h-4" />
                    </Button>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewDetails(lead)}
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>

          {(!filteredLeads || filteredLeads.length === 0) && (
            <div className="text-center py-8 text-muted-foreground">
              Nu s-au găsit lead-uri cu criteriile specificate.
            </div>
          )}
        </CardContent>
      </Card>

      {/* Lead Details Dialog */}
      <Dialog open={isDetailsDialogOpen} onOpenChange={setIsDetailsDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Detalii Lead: {selectedLead?.name}</DialogTitle>
            <DialogDescription>
              Informații complete despre acest lead
            </DialogDescription>
          </DialogHeader>

          {selectedLead && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Nume</label>
                  <p className="text-sm text-muted-foreground">{selectedLead.name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium">Telefon</label>
                  <p className="text-sm text-muted-foreground">{selectedLead.phone}</p>
                </div>
                <div>
                  <label className="text-sm font-medium">Email</label>
                  <p className="text-sm text-muted-foreground">{selectedLead.email || 'N/A'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium">Status</label>
                  <Badge className={getStatusColor(selectedLead.status)}>
                    {selectedLead.status}
                  </Badge>
                </div>
                <div>
                  <label className="text-sm font-medium">Prioritate</label>
                  <div className="flex items-center gap-2">
                    {getPriorityIcon(selectedLead.priority)}
                    <span className="text-sm capitalize">{selectedLead.priority}</span>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium">Sursă</label>
                  <Badge variant={getSourceBadge(selectedLead.source).variant}>
                    {getSourceBadge(selectedLead.source).label}
                  </Badge>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Detalii</label>
                <p className="text-sm text-muted-foreground mt-1">{selectedLead.details}</p>
              </div>

              <div>
                <label className="text-sm font-medium">Fișiere ({selectedLead.files ? selectedLead.files.length : 0})</label>
                <div className="text-sm text-muted-foreground">
                  {(selectedLead.files && selectedLead.files.length > 0) ? selectedLead.files.join(', ') : 'Niciun fișier atașat'}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs text-muted-foreground">
                <div>
                  <strong>Creat:</strong> {new Date(selectedLead.createdAt).toLocaleString('ro-RO')}
                </div>
                <div>
                  <strong>Actualizat:</strong> {new Date(selectedLead.updatedAt).toLocaleString('ro-RO')}
                </div>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDetailsDialogOpen(false)}>
              Închide
            </Button>
            <Button onClick={() => {
              setIsDetailsDialogOpen(false);
              setIsEditDialogOpen(true);
            }}>
              <Edit className="w-4 h-4 mr-2" />
              Editează
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Timeline Modal */}
      <Dialog open={showTimelineModal} onOpenChange={setShowTimelineModal}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-500" />
              Activity Timeline
            </DialogTitle>
            <DialogDescription>
              Historical activities for this lead
            </DialogDescription>
          </DialogHeader>

          {/* Add Note Form */}
          <div className="border rounded-lg p-4 bg-blue-50">
            <label className="text-sm font-medium mb-2 block">Add New Note</label>
            <Textarea
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="Add a note about this lead..."
              className="mb-2"
              rows={3}
            />
            <Button 
              onClick={handleAddNote} 
              disabled={addingNote || !newNote.trim()}
              size="sm"
            >
              {addingNote ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Adding...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Note
                </>
              )}
            </Button>
          </div>

          {/* Activities List */}
          <div className="space-y-3">
            {loadingActivities ? (
              <div className="text-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
                <p className="text-sm text-muted-foreground">Loading timeline...</p>
              </div>
            ) : (!activities || activities.length === 0) ? (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No activities yet</p>
              </div>
            ) : (
              activities.map((activity, index) => (
                <div key={activity.id || index} className="flex gap-3 p-3 border rounded-lg">
                  <div className="flex-shrink-0">
                    {activity.activity_type === 'note' && <FileText className="w-5 h-5 text-blue-500" />}
                    {activity.activity_type === 'email' && <Mail className="w-5 h-5 text-green-500" />}
                    {activity.activity_type === 'call' && <Phone className="w-5 h-5 text-orange-500" />}
                    {activity.activity_type === 'status_change' && <Activity className="w-5 h-5 text-purple-500" />}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-sm">{activity.title}</span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(activity.created_at).toLocaleString('ro-RO')}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">{activity.description}</p>
                    {activity.performed_by && (
                      <span className="text-xs text-muted-foreground mt-1 block">
                        by {activity.performed_by}
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowTimelineModal(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LeadManagement;