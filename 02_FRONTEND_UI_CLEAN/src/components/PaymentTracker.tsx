import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { 
  CreditCard, 
  Plus, 
  Search, 
  Filter, 
  Download,
  Edit,
  Trash2,
  DollarSign,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import AutoProApiService from '@/services/autoproApi';

interface Payment {
  id: string;
  invoice_id: string;
  client_id: string;
  amount: number;
  payment_method: string;
  payment_date: string;
  reference?: string;
  notes?: string;
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  created_at: string;
  updated_at?: string;
}

interface PaymentOverview {
  period: string;
  start_date: string;
  end_date: string;
  total_payments: number;
  total_amount: number;
  completed_count: number;
  completed_amount: number;
  pending_count: number;
  pending_amount: number;
  failed_count: number;
  failed_amount: number;
  payment_methods: Record<string, number>;
  daily_trends: Record<string, { count: number; amount: number }>;
}

const PAYMENT_METHODS = [
  { value: 'cash', label: 'Numerar' },
  { value: 'transfer', label: 'Transfer bancar' },
  { value: 'card', label: 'Card bancar' },
  { value: 'paypal', label: 'PayPal' },
  { value: 'stripe', label: 'Stripe' },
  { value: 'other', label: 'Altă metodă' }
];

const PAYMENT_STATUSES = [
  { value: 'pending', label: 'În așteptare', color: 'bg-yellow-500' },
  { value: 'completed', label: 'Completată', color: 'bg-green-500' },
  { value: 'failed', label: 'Eșuată', color: 'bg-red-500' },
  { value: 'refunded', label: 'Rambursată', color: 'bg-blue-500' }
];

export default function PaymentTracker() {
  const { toast } = useToast();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [overview, setOverview] = useState<PaymentOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingPayment, setEditingPayment] = useState<Payment | null>(null);

  // Filters
  const [filters, setFilters] = useState({
    status: '',
    date_from: '',
    date_to: '',
    client_id: '',
    period: '30d'
  });

  // Form state
  const [formData, setFormData] = useState({
    invoice_id: '',
    amount: '',
    payment_method: 'transfer',
    payment_date: '',
    reference: '',
    notes: ''
  });

  useEffect(() => {
    loadPayments();
    loadOverview();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  const loadPayments = async () => {
    try {
      setLoading(true);
      const response = await AutoProApiService.getPayments(filters);
      
      if (response.payments || response.data?.payments || Array.isArray(response)) {
        setPayments(response.payments || response.data?.payments || response);
      } else {
        console.error('Failed to load payments:', response.error);
        toast({
          title: "Eroare",
          description: "Nu s-au putut încărca plățile.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Failed to load payments:', error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca plățile.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadOverview = async () => {
    try {
      const response = await AutoProApiService.getPaymentOverview(filters.period);
      
      if (response.overview || response.data?.overview || response.total_amount !== undefined) {
        setOverview(response.overview || response.data?.overview || response);
      }
    } catch (error) {
      console.error('Failed to load payment overview:', error);
    }
  };

  const handleCreatePayment = async () => {
    try {
      const paymentData = {
        invoice_id: formData.invoice_id,
        amount: parseFloat(formData.amount),
        payment_method: formData.payment_method,
        payment_date: formData.payment_date || new Date().toISOString().split('T')[0],
        reference: formData.reference,
        notes: formData.notes
      };

      const response = await AutoProApiService.createPayment(paymentData);

      if (response.payment || response.id || response.success) {
        toast({
          title: "Plată creată",
          description: "Plata a fost înregistrată cu succes.",
        });
        
        // Reset form
        setFormData({
          invoice_id: '',
          amount: '',
          payment_method: 'transfer',
          payment_date: '',
          reference: '',
          notes: ''
        });
        setIsCreateDialogOpen(false);
        
        // Reload data
        loadPayments();
        loadOverview();
      } else {
        throw new Error(response.error || 'Failed to create payment');
      }
    } catch (error) {
      console.error('Failed to create payment:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut crea plata.",
        variant: "destructive",
      });
    }
  };

  const handleUpdatePayment = async (paymentId: string, updates: Partial<Payment>) => {
    try {
      const response = await AutoProApiService.updatePayment(paymentId, updates);

      if (response.success || response.payment || response.updated || response.message) {
        toast({
          title: "Plată actualizată",
          description: "Plata a fost actualizată cu succes.",
        });
        loadPayments();
        loadOverview();
      } else {
        throw new Error(response.error || 'Failed to update payment');
      }
    } catch (error) {
      console.error('Failed to update payment:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut actualiza plata.",
        variant: "destructive",
      });
    }
  };

  const handleDeletePayment = async (paymentId: string) => {
    try {
      const response = await AutoProApiService.deletePayment(paymentId);

      if (response.success || response.deleted || response.message) {
        toast({
          title: "Plată ștearsă",
          description: "Plata a fost ștearsă cu succes.",
        });
        loadPayments();
        loadOverview();
      } else {
        throw new Error(response.error || 'Failed to delete payment');
      }
    } catch (error) {
      console.error('Failed to delete payment:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut șterge plata.",
        variant: "destructive",
      });
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ro-RO', {
      style: 'currency',
      currency: 'RON'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ro-RO');
  };

  const getStatusIcon = (status: Payment['status']) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'pending': return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'refunded': return <AlertCircle className="w-4 h-4 text-blue-500" />;
      default: return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: Payment['status']) => {
    const statusInfo = PAYMENT_STATUSES.find(s => s.value === status);
    return (
      <Badge className={`${statusInfo?.color} text-white`}>
        {statusInfo?.label || status}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      {overview && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Plăți</p>
                  <p className="text-2xl font-bold">{overview.total_payments}</p>
                </div>
                <CreditCard className="w-8 h-8 text-blue-500" />
              </div>
              <div className="mt-2">
                <p className="text-sm text-gray-500">
                  {formatCurrency(overview.total_amount)}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Completate</p>
                  <p className="text-2xl font-bold text-green-600">{overview.completed_count}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-500" />
              </div>
              <div className="mt-2">
                <p className="text-sm text-gray-500">
                  {formatCurrency(overview.completed_amount)}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">În Așteptare</p>
                  <p className="text-2xl font-bold text-yellow-600">{overview.pending_count}</p>
                </div>
                <Clock className="w-8 h-8 text-yellow-500" />
              </div>
              <div className="mt-2">
                <p className="text-sm text-gray-500">
                  {formatCurrency(overview.pending_amount)}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Eșuate</p>
                  <p className="text-2xl font-bold text-red-600">{overview.failed_count}</p>
                </div>
                <XCircle className="w-8 h-8 text-red-500" />
              </div>
              <div className="mt-2">
                <p className="text-sm text-gray-500">
                  {formatCurrency(overview.failed_amount)}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters and Actions */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Urmărire Plăți</CardTitle>
            <div className="flex gap-2">
              <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Adaugă Plată
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Adaugă Plată Nouă</DialogTitle>
                    <DialogDescription>
                      Completează detaliile pentru plata nouă.
                    </DialogDescription>
                  </DialogHeader>

                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">ID Factură</label>
                        <Input
                          value={formData.invoice_id}
                          onChange={(e) => setFormData(prev => ({ ...prev, invoice_id: e.target.value }))}
                          placeholder="INV-2025-001"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Sumă</label>
                        <Input
                          type="number"
                          step="0.01"
                          value={formData.amount}
                          onChange={(e) => setFormData(prev => ({ ...prev, amount: e.target.value }))}
                          placeholder="1500.00"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Metodă Plată</label>
                        <Select
                          value={formData.payment_method}
                          onValueChange={(value) => setFormData(prev => ({ ...prev, payment_method: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {PAYMENT_METHODS.map(method => (
                              <SelectItem key={method.value} value={method.value}>
                                {method.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Data Plății</label>
                        <Input
                          type="date"
                          value={formData.payment_date}
                          onChange={(e) => setFormData(prev => ({ ...prev, payment_date: e.target.value }))}
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">Referință</label>
                      <Input
                        value={formData.reference}
                        onChange={(e) => setFormData(prev => ({ ...prev, reference: e.target.value }))}
                        placeholder="TXN123456789"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">Note</label>
                      <Input
                        value={formData.notes}
                        onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                        placeholder="Note suplimentare..."
                      />
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
                      onClick={handleCreatePayment}
                      disabled={!formData.invoice_id || !formData.amount}
                    >
                      Adaugă Plată
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>

              <Button variant="outline">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium mb-2">Status</label>
              <Select
                value={filters.status}
                onValueChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Toate statusurile" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toate statusurile</SelectItem>
                  {PAYMENT_STATUSES.map(status => (
                    <SelectItem key={status.value} value={status.value}>
                      {status.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Perioada</label>
              <Select
                value={filters.period}
                onValueChange={(value) => setFilters(prev => ({ ...prev, period: value }))}
              >
                <SelectTrigger>
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

            <div>
              <label className="block text-sm font-medium mb-2">De la</label>
              <Input
                type="date"
                value={filters.date_from}
                onChange={(e) => setFilters(prev => ({ ...prev, date_from: e.target.value }))}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Până la</label>
              <Input
                type="date"
                value={filters.date_to}
                onChange={(e) => setFilters(prev => ({ ...prev, date_to: e.target.value }))}
              />
            </div>
          </div>

          {/* Payments List */}
          {loading ? (
            <div className="text-center py-8">Se încarcă...</div>
          ) : payments.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <CreditCard className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>Nu există plăți în sistem.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {payments.map(payment => (
                <div key={payment.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    {getStatusIcon(payment.status)}
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold">
                          {formatCurrency(payment.amount)}
                        </h3>
                        {getStatusBadge(payment.status)}
                      </div>
                      <p className="text-sm text-gray-600">
                        {PAYMENT_METHODS.find(m => m.value === payment.payment_method)?.label || payment.payment_method}
                        {payment.reference && ` • ${payment.reference}`}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatDate(payment.payment_date)}
                        {payment.notes && ` • ${payment.notes}`}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setEditingPayment(payment)}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeletePayment(payment.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Payment Methods Breakdown */}
      {overview && (
        <Card>
          <CardHeader>
            <CardTitle>Metode de Plată</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {Object.entries(overview.payment_methods).map(([method, count]) => (
                <div key={method} className="text-center">
                  <div className="text-2xl font-bold">{count}</div>
                  <div className="text-sm text-gray-600">
                    {PAYMENT_METHODS.find(m => m.value === method)?.label || method}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
