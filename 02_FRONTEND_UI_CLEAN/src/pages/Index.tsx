import React, { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import Header from '@/components/Header';
import { 
  Phone, 
  Mail, 
  MapPin, 
  Upload, 
  CheckCircle, 
  Clock, 
  Shield,
  Activity,
  ExternalLink,
  FileImage,
  MessageCircle
} from 'lucide-react';
import autoProLogo from '@/assets/autopro-logo.png';
// Google Sheets integration removed - using Supabase now

interface FormData {
  name: string;
  phone: string;
  details: string;
  files: File[];
}

const Index = () => {
  const { toast } = useToast();
  const formRef = useRef<HTMLDivElement>(null);
  const [formData, setFormData] = useState<FormData>({
    name: "",
    phone: "",
    details: "",
    files: []
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateForm = () => {
    const errors: string[] = [];
    
    if (!formData.name.trim()) {
      errors.push("Numele este obligatoriu");
    }
    
    const phoneRegex = /^(\+4)?0?7\d{8}$/;
    if (!phoneRegex.test(formData.phone.replace(/\s/g, ""))) {
      errors.push("Numărul de telefon nu este valid (format: 07XXXXXXXX)");
    }
    
    if (!formData.details.trim()) {
      errors.push("Descrierea accidentului este obligatorie");
    }
    
    if (formData.files.length < 2) {
      errors.push("Încarcă cel puțin 2 fotografii cu daunele");
    }
    
    return errors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errors = validateForm();
    
    if (errors.length > 0) {
      toast({
        title: "Eroare validare",
        description: errors.join(", "),
        variant: "destructive",
      });
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // Submit to Google Sheets
      const sheetsResult = await GoogleSheetsService.submitLead(formData);
      
      if (!sheetsResult.success) {
        console.warn('Google Sheets submission failed:', sheetsResult.error);
        // Continue with the process even if Google Sheets fails
      }

      // Create FormData for file upload (if you have other API endpoints)
      const submitData = new FormData();
      submitData.append('name', formData.name);
      submitData.append('phone', formData.phone);
      submitData.append('details', formData.details);
      
      // Add files
      formData.files.forEach((file, index) => {
        submitData.append(`file_${index}`, file);
      });

      // Optional: Send to additional webhook/API endpoint
      try {
        await fetch('/api/leads', {
          method: 'POST',
          body: submitData,
        });
      } catch (apiError) {
        console.warn('API submission failed:', apiError);
        // Continue with success message since Google Sheets worked
      }

      // Generate lead ID for tracking
      const leadId = `AP${Date.now()}${Math.random().toString(36).substr(2, 4)}`.toUpperCase();

      toast({
        title: "Cererea a fost trimisă cu succes!",
        description: sheetsResult.success 
          ? `Lead-ul a fost salvat în Google Sheets! ID urmărire: ${leadId}. Vei fi contactat în maximum 15 minute.`
          : `Cererea a fost trimisă! ID urmărire: ${leadId}. Te rugăm să ne contactezi pe Telegram pentru confirmarea rapidă.`,
      });

      // Show tracking link
      setTimeout(() => {
        toast({
          title: "Urmăriți statusul evaluării",
          description: (
            <div className="flex items-center space-x-2">
              <span>ID: {leadId}</span>
              <Link 
                to={`/track/${leadId}`}
                className="inline-flex items-center text-primary hover:text-primary-dark"
              >
                <ExternalLink className="w-3 h-3 ml-1" />
              </Link>
            </div>
          ),
        });
      }, 3000);
      
      // Reset form
      setFormData({ name: "", phone: "", details: "", files: [] });
      
      // Optional: redirect to Telegram group after successful submission
      setTimeout(() => {
        window.open('https://t.me/AUTOPRODAUNE_BOT', '_blank');
      }, 2000);
      
    } catch (error) {
      console.error('Submission error:', error);
      toast({
        title: "Eroare la trimiterea cererii",
        description: "Te rugăm să ne contactezi direct pe Telegram: @AUTOPRODAUNE_BOT",
        variant: "destructive",
      });
      
      // Fallback: open Telegram for direct contact
      setTimeout(() => {
        window.open('https://t.me/AUTOPRODAUNE_BOT', '_blank');
      }, 1000);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setFormData(prev => ({ ...prev, files }));
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <img src={autoProLogo} alt="AutoPro Daune" className="h-12 w-auto mr-3" />
            <div>
              <span className="text-xl font-bold text-foreground">AutoPro Daune</span>
              <p className="text-sm text-muted-foreground hidden sm:block">Soluții Auto Complete</p>
            </div>
          </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center text-sm text-muted-foreground">
                <Phone className="h-4 w-4 mr-1" />
                <span className="hidden sm:inline">0742 123 456</span>
              </div>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => window.open('https://t.me/AUTOPRODAUNE_BOT', '_blank')}
              >
                <MessageCircle className="h-4 w-4 mr-1" />
                Telegram
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary to-primary-light text-primary-foreground py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold mb-6">
                Constatări Accident
                <br />
                <span className="text-primary-green">Rapid și Profesional</span>
              </h1>
              <p className="text-xl mb-8 text-primary-foreground/90">
                Completează formularul și primești suport expert în 15 minute. 
                Procesul este simplu, rapid și complet online. Plus, câștigă 200 lei pentru fiecare recomandare finalizată!
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
                <div className="flex items-center bg-white/10 backdrop-blur-sm rounded-lg p-3">
                  <CheckCircle className="text-primary-green mr-2 h-5 w-5" />
                  <span className="text-sm font-medium">Răspuns în 15 min</span>
                </div>
                <div className="flex items-center bg-white/10 backdrop-blur-sm rounded-lg p-3">
                  <Shield className="text-primary-green mr-2 h-5 w-5" />
                  <span className="text-sm font-medium">Expert certificat</span>
                </div>
                <div className="flex items-center bg-white/10 backdrop-blur-sm rounded-lg p-3">
                  <Clock className="text-primary-green mr-2 h-5 w-5" />
                  <span className="text-sm font-medium">200 lei/recomandare</span>
                </div>
              </div>
            </div>
            <div className="relative">
              <Card className="backdrop-blur-sm bg-white/95 border-white/20">
                <CardHeader>
                  <CardTitle className="text-2xl text-primary">Startează procesul</CardTitle>
                  <p className="text-muted-foreground">
                    Îți ajutăm să obții constatarea daunelor rapid și eficient
                  </p>
                </CardHeader>
                <CardContent>
                  <Button 
                    className="w-full bg-primary-green hover:bg-primary-green/90 text-white"
                    onClick={() => document.getElementById('lead-form')?.scrollIntoView({ behavior: 'smooth' })}
                  >
                    Completează Formularul
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Lead Form Section */}
      <section id="lead-form" className="py-16 bg-gray-50">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Google Sheets Setup */}
          {/* Google Sheets integration removed - using Supabase now */}
          
          <Card className="shadow-xl">
            <CardHeader className="text-center">
              <CardTitle className="text-3xl font-bold text-foreground mb-2">
                Completează Detaliile
              </CardTitle>
              <p className="text-muted-foreground">
                Toate câmpurile marcate cu * sunt obligatorii
              </p>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Name Field */}
                <div className="space-y-2">
                  <label htmlFor="name" className="text-sm font-medium text-foreground">
                    Nume complet *
                  </label>
                  <Input
                    id="name"
                    type="text"
                    required
                    placeholder="Introdu numele complet"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    className="h-12 text-base"
                  />
                </div>

                {/* Phone Field */}
                <div className="space-y-2">
                  <label htmlFor="phone" className="text-sm font-medium text-foreground">
                    Număr de telefon *
                  </label>
                  <Input
                    id="phone"
                    type="tel"
                    required
                    placeholder="0 725 399 235"
                    value={formData.phone}
                    onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
                    className="h-12 text-base"
                  />
                  <p className="text-sm text-muted-foreground">
                    Format: 07XXXXXXXX (10 cifre)
                  </p>
                </div>

                {/* Description Field */}
                <div className="space-y-2">
                  <label htmlFor="details" className="text-sm font-medium text-foreground">
                    Descrierea accidentului *
                  </label>
                  <Textarea
                    id="details"
                    required
                    rows={4}
                    placeholder="Descrie pe scurt ce s-a întâmplat: locul, ora, daunele vizibile..."
                    value={formData.details}
                    onChange={(e) => setFormData(prev => ({ ...prev, details: e.target.value }))}
                    className="text-base resize-none"
                  />
                </div>

                {/* File Upload */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">
                    Fotografii cu daunele * (minim 2)
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer">
                    <input
                      type="file"
                      multiple
                      accept="image/*"
                      onChange={handleFileChange}
                      className="hidden"
                      id="file-upload"
                    />
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <div className="space-y-4">
                        <div className="mx-auto w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                          <Upload className="h-6 w-6 text-gray-400" />
                        </div>
                        <div>
                          <p className="text-lg font-medium text-foreground">
                            Trage și plasează fotografiile aici
                          </p>
                          <p className="text-sm text-muted-foreground">
                            sau <span className="text-primary hover:underline">browsează fișierele</span>
                          </p>
                        </div>
                        <p className="text-xs text-gray-400">
                          JPG, PNG (max 20MB per fișier)
                        </p>
                      </div>
                    </label>
                  </div>
                  
                  {formData.files.length > 0 && (
                    <div className="mt-4">
                      <p className="text-sm font-medium text-foreground mb-2">
                        Fișiere selectate ({formData.files.length}):
                      </p>
                      <div className="space-y-2">
                        {formData.files.map((file, index) => (
                          <div key={index} className="flex items-center text-sm text-muted-foreground">
                            <FileImage className="h-4 w-4 mr-2" />
                            {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full h-12 text-lg font-semibold bg-primary hover:bg-primary/90"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Se trimite..." : "Trimite Cererea"}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground mb-4">
              De ce AutoPro Daune?
            </h2>
            <p className="text-xl text-muted-foreground">
              Procesul nostru este optimizat pentru rapiditate și acuratețe
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="text-center p-6">
              <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <Clock className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Răspuns Rapid</h3>
              <p className="text-muted-foreground">
                Echipa noastră răspunde în maximum 15 minute, 24/7
              </p>
            </Card>
            
            <Card className="text-center p-6">
              <div className="mx-auto w-16 h-16 bg-primary-green/10 rounded-full flex items-center justify-center mb-4">
                <Shield className="h-8 w-8 text-primary-green" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Experți Certificați</h3>
              <p className="text-muted-foreground">
                Constatatori licențiați cu experiență de peste 10 ani
              </p>
            </Card>
            
            <Card className="text-center p-6">
              <div className="mx-auto w-16 h-16 bg-info/10 rounded-full flex items-center justify-center mb-4">
                <CheckCircle className="h-8 w-8 text-info" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Proces Simplu</h3>
              <p className="text-muted-foreground">
                Totul online - nu mai pierzi timp cu deplasări inutile
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-card border-t py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center mb-4 md:mb-0">
              <img src={autoProLogo} alt="AutoPro Daune" className="h-8 w-auto mr-2" />
              <div>
                <span className="font-semibold text-foreground">AutoPro Daune</span>
                <p className="text-xs text-muted-foreground">Soluții Auto Complete</p>
              </div>
            </div>
            <div className="text-sm text-muted-foreground flex items-center space-x-4">
              <span>© 2024 AutoPro Daune. Toate drepturile rezervate.</span>
              <a 
                href="https://t.me/AUTOPRODAUNE_BOT" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center hover:text-primary transition-colors"
              >
                <MessageCircle className="h-4 w-4 mr-1" />
                Telegram: @AUTOPRODAUNE_BOT
              </a>
              <a 
                href="tel:0742123456" 
                className="flex items-center hover:text-primary transition-colors"
              >
                <Phone className="h-4 w-4 mr-1" />
                0742 123 456
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;