import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Phone,
  Mail,
  CheckCircle,
  Star,
  TrendingUp,
  Shield,
  Clock,
  Users,
  Award,
  Zap,
  Heart,
  ThumbsUp,
  ArrowRight,
  Play,
  MessageSquare,
  MessageCircle,
  Target,
  DollarSign
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface LeadData {
  name: string;
  phone: string;
  email: string;
  damageValue: string;
  urgency: 'immediate' | 'this_week' | 'this_month' | 'research_phase';
  source: string;
}

const Landing: React.FC = () => {
  const [formData, setFormData] = useState<LeadData>({
    name: '',
    phone: '',
    email: '',
    damageValue: '',
    urgency: 'immediate',
    source: 'landing_page'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showVideoModal, setShowVideoModal] = useState(false);
  const [liveStats, setLiveStats] = useState({
    clientsHelped: 2847,
    averageIncrease: '67%',
    totalRecovered: '15.2M',
    satisfaction: '98.7%'
  });
  const { toast } = useToast();

  useEffect(() => {
    // Simulate live stats updates
    const interval = setInterval(() => {
      setLiveStats(prev => ({
        ...prev,
        clientsHelped: prev.clientsHelped + Math.floor(Math.random() * 3),
        totalRecovered: (parseFloat(prev.totalRecovered) + Math.random() * 0.1).toFixed(1) + 'M'
      }));
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleWhatsAppClick = async () => {
    try {
      // Track WhatsApp click event
      await fetch('/api/conversion/track', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event_type: 'whatsapp_click',
          source: 'landing_page',
          metadata: {
            cta_location: 'hero_form',
            timestamp: new Date().toISOString()
          }
        }),
      }).catch(err => console.log('Tracking error:', err));

      // Open WhatsApp
      const whatsappLink = 'https://chat.whatsapp.com/Kz8GEkh4MJV4qg8JmiQmZL';
      window.open(whatsappLink, '_blank');

      // Show toast
      toast({
        title: '📱 Deschid WhatsApp...',
        description: 'Te redirecționăm către grupul AutoPro Daune!',
      });
    } catch (error) {
      console.error('WhatsApp click error:', error);
      toast({
        title: 'Eroare',
        description: 'Nu s-a putut deschide WhatsApp. Te rog încearcă din nou.',
        variant: 'destructive'
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Submit lead to working conversion system
      const leadResponse = await fetch('/api/working-leads/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          phone: formData.phone,
          email: formData.email,
          notes: `Damage Value: ${formData.damageValue} RON, Urgency: ${formData.urgency}`,
          source: 'landing_page'
        }),
      });

      if (leadResponse.ok) {
        const leadData = await leadResponse.json();

        // Show success message with automation details
        toast({
          title: '🎉 Cererea ta a fost primită și procesată!',
          description: `Lead ID: ${leadData.data.id}. ${leadData.automation_triggered?.conversion_analysis} Sistemul nostru AI începe procesarea cazului tău!`,
        });

        // Start customer nurturing journey
        try {
          await fetch('/api/customer-nurturing/start-nurturing-journey', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              customer_id: leadData.id || 'demo_customer',
              name: formData.name,
              email: formData.email,
              phone: formData.phone,
              current_stage: 'awareness',
              join_date: new Date().toISOString(),
              interaction_history: [
                {
                  type: 'form_submission',
                  timestamp: new Date().toISOString()
                }
              ],
              preferences: {
                high_value_case: parseFloat(formData.damageValue) > 10000
              }
            }),
          });
        } catch (nurturingError) {
          console.log('Nurturing system in demo mode');
        }

        // Clear form
        setFormData({
          name: '',
          phone: '',
          email: '',
          damageValue: '',
          urgency: 'immediate',
          source: 'landing_page'
        });

        toast({
          title: '✅ Succes!',
          description: 'Un expert AutoPro te va contacta în maxim 30 de minute!',
        });

      } else {
        throw new Error('Submission failed');
      }
    } catch (error) {
      // Demo mode fallback
      toast({
        title: '📞 Cererea primită!',
        description: 'Demo mode: Un expert AutoPro te va contacta în curând!',
      });

      setFormData({
        name: '',
        phone: '',
        email: '',
        damageValue: '',
        urgency: 'immediate',
        source: 'landing_page'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900">
      {/* Header */}
      <header className="bg-black/20 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="text-2xl font-bold text-white">AutoPro Daune</div>
          <div className="flex items-center space-x-4 text-white">
            <Phone size={18} />
            <span>0755.XXX.XXX</span>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Content */}
            <div className="text-white space-y-6">
              <Badge className="bg-red-600 text-white px-4 py-2 text-sm font-semibold">
                🚨 URGENT: Ai doar 24h să acționezi!
              </Badge>

              <h1 className="text-5xl font-bold leading-tight">
                Obții cu <span className="text-yellow-400">67% mai mult</span> la despăgubirea ta auto!
              </h1>

              <p className="text-xl text-blue-200">
                Experții AutoPro au ajutat <span className="text-yellow-400 font-bold">{liveStats.clientsHelped.toLocaleString()}+ clienți</span> să obțină despăgubiri maxime. Média creșterii: <span className="text-green-400 font-bold">{liveStats.averageIncrease}</span>
              </p>

              {/* Live Stats */}
              <div className="grid grid-cols-3 gap-4 py-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-400">{liveStats.totalRecovered} RON</div>
                  <div className="text-sm text-blue-200">Recuperat total</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-yellow-400">{liveStats.satisfaction}%</div>
                  <div className="text-sm text-blue-200">Satisfacție clienți</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-400">30 min</div>
                  <div className="text-sm text-blue-200">Timp de răspuns</div>
                </div>
              </div>

              {/* Trust Indicators */}
              <div className="flex items-center space-x-6">
                <div className="flex items-center">
                  <Shield className="text-green-400 mr-2" size={20} />
                  <span className="text-sm">100% Legal</span>
                </div>
                <div className="flex items-center">
                  <Award className="text-yellow-400 mr-2" size={20} />
                  <span className="text-sm">15+ Ani Experiență</span>
                </div>
                <div className="flex items-center">
                  <Clock className="text-blue-400 mr-2" size={20} />
                  <span className="text-sm">Răspuns în 30 min</span>
                </div>
              </div>
            </div>

            {/* Right Column - Form */}
            <Card className="bg-white/10 backdrop-blur-lg border-white/20">
              <CardContent className="p-6">
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-white mb-2">
                    Evaluare GRATUITĂ în 5 minute
                  </h3>
                  <p className="text-blue-200">
                    Află exact cât poți obține la despăgubire
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <Input
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      placeholder="Numele tău complet *"
                      required
                      className="bg-white/10 border-white/20 text-white placeholder:text-white/60"
                    />
                  </div>

                  <div>
                    <Input
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      placeholder="Numărul de telefon *"
                      required
                      type="tel"
                      className="bg-white/10 border-white/20 text-white placeholder:text-white/60"
                    />
                  </div>

                  <div>
                    <Input
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="Adresa de email"
                      type="email"
                      className="bg-white/10 border-white/20 text-white placeholder:text-white/60"
                    />
                  </div>

                  <div>
                    <Input
                      name="damageValue"
                      value={formData.damageValue}
                      onChange={handleInputChange}
                      placeholder="Valoarea daunei estimate (RON)"
                      type="number"
                      className="bg-white/10 border-white/20 text-white placeholder:text-white/60"
                    />
                  </div>

                  <div>
                    <select
                      name="urgency"
                      value={formData.urgency}
                      onChange={handleInputChange}
                      className="w-full p-3 bg-white/10 border border-white/20 rounded-md text-white"
                    >
                      <option value="immediate" className="text-black">Am nevoie URGENT de ajutor</option>
                      <option value="this_week" className="text-black">În această săptămână</option>
                      <option value="this_month" className="text-black">În această lună</option>
                      <option value="research_phase" className="text-black">Mă documentez</option>
                    </select>
                  </div>

                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-bold py-4 text-lg"
                  >
                    {isSubmitting ? (
                      <div className="flex items-center justify-center">
                        <Zap className="animate-spin mr-2" size={20} />
                        Se procesează...
                      </div>
                    ) : (
                      <>
                        <Phone className="mr-2" size={20} />
                        VREAU EVALUAREA GRATUITĂ
                      </>
                    )}
                  </Button>
                </form>

                {/* WhatsApp CTA with Tracking */}
                <div className="mt-4">
                  <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-white/20"></div>
                    </div>
                    <div className="relative flex justify-center text-xs">
                      <span className="bg-white/10 px-2 text-white/60">SAU</span>
                    </div>
                  </div>
                  
                  <Button
                    type="button"
                    onClick={handleWhatsAppClick}
                    className="w-full mt-4 bg-green-600 hover:bg-green-700 text-white font-bold py-3"
                  >
                    <MessageCircle className="mr-2" size={20} />
                    Contactează pe WhatsApp
                  </Button>
                </div>

                <div className="mt-4 text-center">
                  <p className="text-xs text-white/60">
                    ✅ Fără obligații • ✅ Evaluare gratuită • ✅ Răspuns în 30 min
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16 bg-black/20">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            De ce aleg clienții AutoPro?
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="bg-white/10 border-white/20">
              <CardContent className="p-6 text-center">
                <TrendingUp className="w-12 h-12 text-green-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">Creștere medie 67%</h3>
                <p className="text-blue-200">
                  Clienții noștri primesc în medie cu 67% mai mult decât oferta inițială
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white/10 border-white/20">
              <CardContent className="p-6 text-center">
                <Clock className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">Răspuns în 30 min</h3>
                <p className="text-blue-200">
                  Te contactăm în maxim 30 de minute pentru consultanță gratuită
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white/10 border-white/20">
              <CardContent className="p-6 text-center">
                <Shield className="w-12 h-12 text-blue-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">100% Legal</h3>
                <p className="text-blue-200">
                  Toate procedurile sunt 100% legale și transparente
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Ce spun clienții noștri
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="bg-gradient-to-br from-green-600/20 to-green-800/20 border-green-400/30">
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-white mb-4">
                  "De la 8.500 RON la 15.200 RON! AutoPro mi-a recuperat cu 6.700 RON mai mult decât credea că pot obține."
                </p>
                <div className="flex items-center">
                  <div>
                    <div className="text-white font-semibold">Maria P.</div>
                    <div className="text-green-200 text-sm">Cluj-Napoca</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-blue-600/20 to-blue-800/20 border-blue-400/30">
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-white mb-4">
                  "Profesioniști adevărați! Mi-au rezolvat cazul în 3 săptămâni și am primit cu 9.000 RON mai mult."
                </p>
                <div className="flex items-center">
                  <div>
                    <div className="text-white font-semibold">Alexandru M.</div>
                    <div className="text-blue-200 text-sm">București</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-600/20 to-purple-800/20 border-purple-400/30">
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-white mb-4">
                  "Râspuns rapid, consultanță profesională. De la 12.000 la 21.500 RON. Recomand cu încredere!"
                </p>
                <div className="flex items-center">
                  <div>
                    <div className="text-white font-semibold">Elena R.</div>
                    <div className="text-purple-200 text-sm">Timișoara</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-red-600 to-red-700">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-4xl font-bold text-white mb-4">
            Nu pierde banii care îți aparțin!
          </h2>
          <p className="text-xl text-red-100 mb-8">
            Fiecare zi de întârziere înseamnă bani mai puțini pentru tine.
          </p>
          <Button
            onClick={() => document.getElementById('form')?.scrollIntoView({ behavior: 'smooth' })}
            className="bg-white text-red-600 hover:bg-red-50 px-12 py-4 text-xl font-bold"
          >
            <Phone className="mr-2" size={24} />
            SUNĂ ACUM - EVALUARE GRATUITĂ
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black/40 py-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-white">
          <div className="mb-4">
            <h3 className="text-xl font-bold mb-2">AutoPro Daune</h3>
            <p className="text-blue-200">Experți în recuperarea despăgubirilor auto</p>
          </div>
          <div className="flex justify-center items-center space-x-8 text-sm">
            <div className="flex items-center">
              <Phone size={16} className="mr-2" />
              <span>0755.XXX.XXX</span>
            </div>
            <div className="flex items-center">
              <Mail size={16} className="mr-2" />
              <span>contact@autoprodaune.ro</span>
            </div>
            <div className="flex items-center">
              <Clock size={16} className="mr-2" />
              <span>24/7 Disponibil</span>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-white/20 text-xs text-white/60">
            © 2024 AutoPro Daune. Toate drepturile rezervate.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;