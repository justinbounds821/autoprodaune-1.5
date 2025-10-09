import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
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
  FileText, 
  Plus, 
  Edit, 
  Trash2, 
  Download, 
  Send,
  Calculator,
  DollarSign
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface InvoiceItem {
  id: string;
  description: string;
  quantity: number;
  unitPrice: number;
  total: number;
}

interface Invoice {
  id: string;
  number: string;
  clientName: string;
  clientEmail: string;
  clientAddress: string;
  issueDate: string;
  dueDate: string;
  items: InvoiceItem[];
  subtotal: number;
  taxRate: number;
  taxAmount: number;
  total: number;
  status: 'draft' | 'sent' | 'paid' | 'overdue';
  notes: string;
}

const TAX_RATES = [0, 0.05, 0.19, 0.24]; // 0%, 5%, 19%, 24%

export default function InvoiceGenerator() {
  const { toast } = useToast();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingInvoice, setEditingInvoice] = useState<Invoice | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    clientName: '',
    clientEmail: '',
    clientAddress: '',
    dueDate: '',
    taxRate: 0.19,
    notes: ''
  });

  const [items, setItems] = useState<InvoiceItem[]>([]);

  useEffect(() => {
    loadInvoices();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadInvoices = async () => {
    try {
      setLoading(true);
      // Simulated data - în producție ar fi API call
      const mockInvoices: Invoice[] = [
        {
          id: '1',
          number: 'INV-2025-001',
          clientName: 'Ion Popescu',
          clientEmail: 'ion@example.com',
          clientAddress: 'București, România',
          issueDate: '2025-01-01',
          dueDate: '2025-01-31',
          items: [
            { id: '1', description: 'Consultanță juridică accident auto', quantity: 2, unitPrice: 500, total: 1000 },
            { id: '2', description: 'Expertiză daune auto', quantity: 1, unitPrice: 300, total: 300 }
          ],
          subtotal: 1300,
          taxRate: 0.19,
          taxAmount: 247,
          total: 1547,
          status: 'sent',
          notes: 'Servicii pentru cazul accidentului din 15 decembrie 2024'
        }
      ];
      setInvoices(mockInvoices);
    } catch (error) {
      console.error('Failed to load invoices:', error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca facturile.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const addItem = () => {
    const newItem: InvoiceItem = {
      id: Date.now().toString(),
      description: '',
      quantity: 1,
      unitPrice: 0,
      total: 0
    };
    setItems(prev => [...prev, newItem]);
  };

  const updateItem = (id: string, field: keyof InvoiceItem, value: string | number) => {
    setItems(prev => prev.map(item => {
      if (item.id === id) {
        const updated = { ...item, [field]: value };
        if (field === 'quantity' || field === 'unitPrice') {
          updated.total = updated.quantity * updated.unitPrice;
        }
        return updated;
      }
      return item;
    }));
  };

  const removeItem = (id: string) => {
    setItems(prev => prev.filter(item => item.id !== id));
  };

  const calculateTotals = () => {
    const subtotal = items.reduce((sum, item) => sum + item.total, 0);
    const taxAmount = subtotal * formData.taxRate;
    const total = subtotal + taxAmount;
    return { subtotal, taxAmount, total };
  };

  const generateInvoiceNumber = () => {
    const year = new Date().getFullYear();
    const month = String(new Date().getMonth() + 1).padStart(2, '0');
    const count = invoices.length + 1;
    return `INV-${year}-${month}-${String(count).padStart(3, '0')}`;
  };

  const handleCreateInvoice = async () => {
    if (items.length === 0) {
      toast({
        title: "Lipsesc itemii",
        description: "Adaugă cel puțin un item în factură.",
        variant: "destructive",
      });
      return;
    }

    try {
      const { subtotal, taxAmount, total } = calculateTotals();
      const newInvoice: Invoice = {
        id: Date.now().toString(),
        number: generateInvoiceNumber(),
        clientName: formData.clientName,
        clientEmail: formData.clientEmail,
        clientAddress: formData.clientAddress,
        issueDate: new Date().toISOString().split('T')[0],
        dueDate: formData.dueDate,
        items: [...items],
        subtotal,
        taxRate: formData.taxRate,
        taxAmount,
        total,
        status: 'draft',
        notes: formData.notes
      };

      setInvoices(prev => [newInvoice, ...prev]);
      
      toast({
        title: "Factură creată",
        description: `Factura ${newInvoice.number} a fost creată cu succes.`,
      });

      // Reset form
      setFormData({
        clientName: '',
        clientEmail: '',
        clientAddress: '',
        dueDate: '',
        taxRate: 0.19,
        notes: ''
      });
      setItems([]);
      setIsCreateDialogOpen(false);

    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut crea factura.",
        variant: "destructive",
      });
    }
  };

  const handleSendInvoice = async (invoice: Invoice) => {
    try {
      // Update status to sent
      setInvoices(prev => prev.map(inv => 
        inv.id === invoice.id ? { ...inv, status: 'sent' as const } : inv
      ));
      
      toast({
        title: "Factură trimisă",
        description: `Factura ${invoice.number} a fost trimisă către ${invoice.clientEmail}.`,
      });
    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut trimite factura.",
        variant: "destructive",
      });
    }
  };

  const handleDownloadInvoice = async (invoice: Invoice) => {
    try {
      // In production, generate PDF
      toast({
        title: "Download început",
        description: `Se generează PDF pentru factura ${invoice.number}.`,
      });
    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut genera PDF-ul.",
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

  const getStatusColor = (status: Invoice['status']) => {
    switch (status) {
      case 'draft': return 'bg-gray-500';
      case 'sent': return 'bg-blue-500';
      case 'paid': return 'bg-green-500';
      case 'overdue': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: Invoice['status']) => {
    switch (status) {
      case 'draft': return 'Ciornă';
      case 'sent': return 'Trimisă';
      case 'paid': return 'Plătită';
      case 'overdue': return 'Restantă';
      default: return status;
    }
  };

  const { subtotal, taxAmount, total } = calculateTotals();

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Facturi</p>
                <p className="text-2xl font-bold">{invoices.length}</p>
              </div>
              <FileText className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Valoare Totală</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrency(invoices.reduce((sum, inv) => sum + inv.total, 0))}
                </p>
              </div>
              <DollarSign className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Plătite</p>
                <p className="text-2xl font-bold text-blue-600">
                  {invoices.filter(inv => inv.status === 'paid').length}
                </p>
              </div>
              <Calculator className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Restante</p>
                <p className="text-2xl font-bold text-red-600">
                  {formatCurrency(invoices.filter(inv => inv.status === 'overdue').reduce((sum, inv) => sum + inv.total, 0))}
                </p>
              </div>
              <FileText className="w-8 h-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Create Invoice Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogTrigger asChild>
          <Button className="w-full">
            <Plus className="w-4 h-4 mr-2" />
            Creează Factură Nouă
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Creează Factură Nouă</DialogTitle>
            <DialogDescription>
              Completează datele clientului și adaugă itemii pentru factură.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Client Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Nume Client</label>
                <Input
                  value={formData.clientName}
                  onChange={(e) => setFormData(prev => ({ ...prev, clientName: e.target.value }))}
                  placeholder="Ion Popescu"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Email Client</label>
                <Input
                  type="email"
                  value={formData.clientEmail}
                  onChange={(e) => setFormData(prev => ({ ...prev, clientEmail: e.target.value }))}
                  placeholder="ion@example.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Adresă Client</label>
              <Textarea
                value={formData.clientAddress}
                onChange={(e) => setFormData(prev => ({ ...prev, clientAddress: e.target.value }))}
                placeholder="Strada, Nr, Oraș, Țară"
                rows={2}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Data Scadență</label>
                <Input
                  type="date"
                  value={formData.dueDate}
                  onChange={(e) => setFormData(prev => ({ ...prev, dueDate: e.target.value }))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Rată TVA</label>
                <Select
                  value={formData.taxRate.toString()}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, taxRate: parseFloat(value) }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">0% (Scutit)</SelectItem>
                    <SelectItem value="0.05">5%</SelectItem>
                    <SelectItem value="0.19">19% (Standard)</SelectItem>
                    <SelectItem value="0.24">24% (Înalt)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Invoice Items */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Itemi Factură</h3>
                <Button variant="outline" size="sm" onClick={addItem}>
                  <Plus className="w-4 h-4 mr-2" />
                  Adaugă Item
                </Button>
              </div>

              <div className="space-y-3">
                {items.map(item => (
                  <div key={item.id} className="grid grid-cols-12 gap-2 p-3 border rounded-lg">
                    <div className="col-span-5">
                      <Input
                        value={item.description}
                        onChange={(e) => updateItem(item.id, 'description', e.target.value)}
                        placeholder="Descriere serviciu"
                      />
                    </div>
                    <div className="col-span-2">
                      <Input
                        type="number"
                        value={item.quantity}
                        onChange={(e) => updateItem(item.id, 'quantity', parseInt(e.target.value) || 0)}
                        placeholder="Cantitate"
                      />
                    </div>
                    <div className="col-span-2">
                      <Input
                        type="number"
                        value={item.unitPrice}
                        onChange={(e) => updateItem(item.id, 'unitPrice', parseFloat(e.target.value) || 0)}
                        placeholder="Preț unitar"
                      />
                    </div>
                    <div className="col-span-2">
                      <Input
                        value={formatCurrency(item.total)}
                        disabled
                        className="bg-gray-50"
                      />
                    </div>
                    <div className="col-span-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeItem(item.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Totals */}
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex justify-between text-sm mb-2">
                  <span>Subtotal:</span>
                  <span>{formatCurrency(subtotal)}</span>
                </div>
                <div className="flex justify-between text-sm mb-2">
                  <span>TVA ({(formData.taxRate * 100).toFixed(0)}%):</span>
                  <span>{formatCurrency(taxAmount)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold pt-2 border-t">
                  <span>Total:</span>
                  <span>{formatCurrency(total)}</span>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Note (opțional)</label>
              <Textarea
                value={formData.notes}
                onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                placeholder="Informații suplimentare pentru client..."
                rows={3}
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
              onClick={handleCreateInvoice}
              disabled={items.length === 0 || !formData.clientName || !formData.clientEmail}
            >
              Creează Factură
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Invoices List */}
      <Card>
        <CardHeader>
          <CardTitle>Facturi</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Se încarcă...</div>
          ) : invoices.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>Nu există facturi în sistem.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {invoices.map(invoice => (
                <div key={invoice.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold">{invoice.number}</h3>
                      <Badge className={getStatusColor(invoice.status)}>
                        {getStatusText(invoice.status)}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-1">{invoice.clientName}</p>
                    <p className="text-xs text-gray-500">
                      Emisă: {formatDate(invoice.issueDate)} | Scadență: {formatDate(invoice.dueDate)}
                    </p>
                  </div>
                  <div className="text-right mr-4">
                    <p className="text-lg font-bold">{formatCurrency(invoice.total)}</p>
                    <p className="text-sm text-gray-500">{invoice.items.length} itemi</p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDownloadInvoice(invoice)}
                    >
                      <Download className="w-4 h-4" />
                    </Button>
                    {invoice.status === 'draft' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleSendInvoice(invoice)}
                      >
                        <Send className="w-4 h-4" />
                      </Button>
                    )}
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
