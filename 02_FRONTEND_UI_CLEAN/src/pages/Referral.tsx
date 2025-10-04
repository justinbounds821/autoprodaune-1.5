import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import {
  DollarSign,
  Users,
  Share2,
  Copy,
  ArrowLeft,
  TrendingUp,
  Award,
  MessageCircle,
  ExternalLink,
  CheckCircle,
  Clock,
  Star,
  Target,
  Gift,
  Zap,
  Phone
} from 'lucide-react';

interface ReferralData {
  referrer_phone: string;
  referrer_name: string;
  referral_code: string;
  total_referrals: number;
  completed_referrals: number;
  pending_referrals: number;
  total_earnings: number;
  pending_earnings: number;
  referrals: Array<{
    id: string;
    referred_name: string;
    referred_phone: string;
    status: string;
    reward_amount: number;
    created_at: string;
    converted_at?: string;
  }>;
}

const Referral = () => {
  const { toast } = useToast();
  const [phoneNumber, setPhoneNumber] = useState('');
  const [name, setName] = useState('');
  const [referralData, setReferralData] = useState<ReferralData | null>(null);
  const [loading, setLoading] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phoneNumber.trim() || !name.trim()) {
      toast({
        title: "Eroare",
        description: "Te rugăm să completezi toate câmpurile",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);

    try {
      // Get or create referral account
      const response = await fetch('/api/referrals/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          referrer_phone: phoneNumber,
          referrer_name: name,
        }),
      });

      if (response.ok) {
        // Fetch referral data
        const statsResponse = await fetch(`/api/referrals/stats?phone=${encodeURIComponent(phoneNumber)}`);
        if (statsResponse.ok) {
          const data = await statsResponse.json();
          setReferralData(data);
          setShowDashboard(true);

          toast({
            title: "Conectat cu succes!",
            description: "Bun venit în dashboard-ul tău de recomandări",
          });
        }
      }
    } catch (error) {
      console.error('Error:', error);
      toast({
        title: "Eroare",
        description: "Nu am putut încărca datele. Încearcă din nou.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const copyReferralLink = () => {
    const referralLink = `${window.location.origin}/?ref=${referralData?.referral_code}`;
    navigator.clipboard.writeText(referralLink);
    toast({
      title: "Link copiat!",
      description: "Link-ul de recomandare a fost copiat în clipboard",
    });
  };

  const shareWhatsApp = () => {
    const referralLink = `${window.location.origin}/?ref=${referralData?.referral_code}`;
    const message = encodeURIComponent(
      `🚗 Salut! Tocmai am descoperit AutoPro Daune - cei mai buni experți în despăgubiri auto din România!\n\n` +
      `✅ Rezolvă cazurile în 24-48h (nu luni!)\n` +
      `✅ Obții banii COMPLET, nu doar o parte\n` +
      `✅ Fără costuri dacă nu câștigi\n\n` +
      `Dacă ai nevoie de ajutor cu un accident auto, folosește link-ul meu și vei primi consultația gratuită:\n\n` +
      `${referralLink}\n\n` +
      `P.S. - Și eu câștig 200 LEI dacă devii client, deci win-win! 😊`
    );
    window.open(`https://wa.me/?text=${message}`, '_blank');
  };

  if (!showDashboard) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-sm sticky top-0 z-50 border-b">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" asChild>
                <Link to="/">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Înapoi
                </Link>
              </Button>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Program de Recomandări</h1>
                <p className="text-sm text-gray-500">Câștigă 200 LEI pentru fiecare recomandare</p>
              </div>
            </div>
          </div>
        </header>

        <div className="container mx-auto px-4 py-12">
          {/* Hero Section */}
          <div className="max-w-4xl mx-auto text-center mb-12">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <DollarSign className="h-10 w-10 text-green-600" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Câștigă <span className="text-green-600">200 LEI</span> pentru fiecare recomandare!
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Ajută-ți prietenii să obțină despăgubirile pe care le merită și câștigă bani pentru fiecare persoană pe care o recomanzi.
            </p>

            {/* Benefits */}
            <div className="grid md:grid-cols-3 gap-6 mb-12">
              <Card className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <DollarSign className="h-6 w-6 text-green-600" />
                  </div>
                  <h3 className="font-semibold mb-2">200 LEI garantați</h3>
                  <p className="text-gray-600 text-sm">Pentru fiecare prieten care devine client</p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Zap className="h-6 w-6 text-blue-600" />
                  </div>
                  <h3 className="font-semibold mb-2">Plata rapidă</h3>
                  <p className="text-gray-600 text-sm">Primești banii în maxim 7 zile</p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Users className="h-6 w-6 text-purple-600" />
                  </div>
                  <h3 className="font-semibold mb-2">Fără limită</h3>
                  <p className="text-gray-600 text-sm">Recomandă câte persoane vrei</p>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Login Form */}
          <div className="max-w-md mx-auto">
            <Card className="shadow-xl">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl">Începe să câștigi ACUM</CardTitle>
                <CardDescription>
                  Creează-ți contul de recomandare și obține link-ul tău personal
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleLogin} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Numele tău complet
                    </label>
                    <Input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Ex: Ion Popescu"
                      className="h-12"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Numărul tău de telefon
                    </label>
                    <Input
                      type="tel"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      placeholder="Ex: 0721 123 456"
                      className="h-12"
                      required
                    />
                  </div>

                  <Button
                    type="submit"
                    className="w-full h-12 bg-green-600 hover:bg-green-700"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Clock className="mr-2 h-4 w-4 animate-spin" />
                        Se încarcă...
                      </>
                    ) : (
                      <>
                        <Gift className="mr-2 h-4 w-4" />
                        Creează cont și începe să câștigi
                      </>
                    )}
                  </Button>
                </form>

                <div className="mt-6 text-center text-sm text-gray-500">
                  <p>
                    Prin crearea contului accepți{' '}
                    <a href="#" className="text-blue-600 hover:underline">
                      termenii și condițiile
                    </a>{' '}
                    programului de recomandări.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* How it works */}
          <section className="mt-16 max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
              Cum funcționează?
            </h2>

            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6 relative">
                  <Share2 className="h-8 w-8 text-blue-600" />
                  <span className="absolute -top-2 -right-2 bg-blue-600 text-white text-sm rounded-full w-6 h-6 flex items-center justify-center">1</span>
                </div>
                <h3 className="text-xl font-semibold mb-4">Distribuie link-ul</h3>
                <p className="text-gray-600">
                  Trimite link-ul tău personal de recomandare prietenilor care au avut accidente auto.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6 relative">
                  <CheckCircle className="h-8 w-8 text-green-600" />
                  <span className="absolute -top-2 -right-2 bg-green-600 text-white text-sm rounded-full w-6 h-6 flex items-center justify-center">2</span>
                </div>
                <h3 className="text-xl font-semibold mb-4">Prietenul devine client</h3>
                <p className="text-gray-600">
                  După ce prietenul tău folosește serviciile noastre și primește despăgubirile, recomandarea se validează.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6 relative">
                  <DollarSign className="h-8 w-8 text-purple-600" />
                  <span className="absolute -top-2 -right-2 bg-purple-600 text-white text-sm rounded-full w-6 h-6 flex items-center justify-center">3</span>
                </div>
                <h3 className="text-xl font-semibold mb-4">Primești 200 LEI</h3>
                <p className="text-gray-600">
                  Îți transferăm 200 LEI direct în cont în maxim 7 zile lucrătoare.
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm sticky top-0 z-50 border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" asChild>
                <Link to="/">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Înapoi
                </Link>
              </Button>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Dashboard Recomandări</h1>
                <p className="text-sm text-gray-500">Bun venit, {referralData?.referrer_name}</p>
              </div>
            </div>
            <Badge className="bg-green-100 text-green-700">
              <Award className="h-4 w-4 mr-1" />
              {referralData?.total_earnings || 0} LEI câștigați
            </Badge>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total câștigat</p>
                  <p className="text-2xl font-bold text-green-600">{referralData?.total_earnings || 0} LEI</p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <DollarSign className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">În așteptare</p>
                  <p className="text-2xl font-bold text-orange-600">{referralData?.pending_earnings || 0} LEI</p>
                </div>
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                  <Clock className="h-6 w-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Recomandări totale</p>
                  <p className="text-2xl font-bold text-blue-600">{referralData?.total_referrals || 0}</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Rata de succes</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {referralData?.total_referrals ? Math.round((referralData.completed_referrals / referralData.total_referrals) * 100) : 0}%
                  </p>
                </div>
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Sharing Tools */}
          <div className="lg:col-span-2">
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Share2 className="h-5 w-5 mr-2 text-blue-600" />
                  Distribuie și câștigă
                </CardTitle>
                <CardDescription>
                  Link-ul tău personal de recomandare
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    value={`${window.location.origin}/?ref=${referralData?.referral_code}`}
                    readOnly
                    className="font-mono text-sm"
                  />
                  <Button onClick={copyReferralLink} variant="outline">
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>

                <div className="flex gap-2">
                  <Button onClick={shareWhatsApp} className="flex-1 bg-green-600 hover:bg-green-700">
                    <MessageCircle className="h-4 w-4 mr-2" />
                    Trimite pe WhatsApp
                  </Button>

                  <Button variant="outline" className="flex-1" onClick={() => {
                    const url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.origin + '/?ref=' + referralData?.referral_code)}`;
                    window.open(url, '_blank');
                  }}>
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Facebook
                  </Button>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-800 mb-2">💡 Sfaturi pentru mai multe recomandări:</h4>
                  <ul className="text-blue-700 text-sm space-y-1">
                    <li>• Postează în grupurile de mașini din orașul tău</li>
                    <li>• Trimite direct prietenilor care au avut accidente</li>
                    <li>• Folosește-te de experiența ta pozitivă ca exemplu</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Referrals List */}
            <Card>
              <CardHeader>
                <CardTitle>Recomandările tale</CardTitle>
                <CardDescription>
                  Istoricul tuturor recomandărilor făcute
                </CardDescription>
              </CardHeader>
              <CardContent>
                {referralData?.referrals && referralData.referrals.length > 0 ? (
                  <div className="space-y-4">
                    {referralData.referrals.map((referral) => (
                      <div key={referral.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                          <p className="font-medium">{referral.referred_name}</p>
                          <p className="text-sm text-gray-600">{referral.referred_phone}</p>
                          <p className="text-xs text-gray-500">
                            {new Date(referral.created_at).toLocaleDateString('ro-RO')}
                          </p>
                        </div>
                        <div className="text-right">
                          <Badge
                            className={
                              referral.status === 'completed'
                                ? 'bg-green-100 text-green-800'
                                : referral.status === 'pending'
                                ? 'bg-orange-100 text-orange-800'
                                : 'bg-gray-100 text-gray-800'
                            }
                          >
                            {referral.status === 'completed' ? '✅ Finalizat' :
                             referral.status === 'pending' ? '⏳ În așteptare' :
                             '📋 Nou'}
                          </Badge>
                          <p className="text-sm font-semibold text-green-600 mt-1">
                            {referral.status === 'completed' ? `+${referral.reward_amount} LEI` : `${referral.reward_amount} LEI`}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Încă nu ai recomandări</h3>
                    <p className="text-gray-600 mb-4">Începe să distribui link-ul tău și câștigă primii 200 LEI!</p>
                    <Button onClick={shareWhatsApp} className="bg-green-600 hover:bg-green-700">
                      <Share2 className="h-4 w-4 mr-2" />
                      Distribuie acum
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Next Payout */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <Target className="h-5 w-5 mr-2 text-green-600" />
                  Următoarea plată
                </CardTitle>
              </CardHeader>
              <CardContent>
                {referralData?.pending_earnings && referralData.pending_earnings > 0 ? (
                  <div className="text-center">
                    <p className="text-3xl font-bold text-green-600 mb-2">{referralData.pending_earnings} LEI</p>
                    <p className="text-sm text-gray-600 mb-4">Se procesează</p>
                    <Badge className="bg-orange-100 text-orange-800">
                      <Clock className="h-3 w-3 mr-1" />
                      Maxim 7 zile
                    </Badge>
                  </div>
                ) : (
                  <div className="text-center text-gray-500">
                    <p className="text-sm">Nicio plată în așteptare</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Achievements */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <Award className="h-5 w-5 mr-2 text-purple-600" />
                  Realizări
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className={`flex items-center p-2 rounded-lg ${(referralData?.total_referrals || 0) >= 1 ? 'bg-green-50' : 'bg-gray-50'}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${(referralData?.total_referrals || 0) >= 1 ? 'bg-green-100' : 'bg-gray-200'}`}>
                      {(referralData?.total_referrals || 0) >= 1 ?
                        <CheckCircle className="h-4 w-4 text-green-600" /> :
                        <Target className="h-4 w-4 text-gray-400" />
                      }
                    </div>
                    <div>
                      <p className="text-sm font-medium">Prima recomandare</p>
                      <p className="text-xs text-gray-600">Fă prima ta recomandare</p>
                    </div>
                  </div>

                  <div className={`flex items-center p-2 rounded-lg ${(referralData?.completed_referrals || 0) >= 5 ? 'bg-green-50' : 'bg-gray-50'}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${(referralData?.completed_referrals || 0) >= 5 ? 'bg-green-100' : 'bg-gray-200'}`}>
                      {(referralData?.completed_referrals || 0) >= 5 ?
                        <Star className="h-4 w-4 text-green-600" /> :
                        <Star className="h-4 w-4 text-gray-400" />
                      }
                    </div>
                    <div>
                      <p className="text-sm font-medium">Expert în recomandări</p>
                      <p className="text-xs text-gray-600">5 recomandări finalizate</p>
                    </div>
                  </div>

                  <div className={`flex items-center p-2 rounded-lg ${(referralData?.total_earnings || 0) >= 1000 ? 'bg-green-50' : 'bg-gray-50'}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${(referralData?.total_earnings || 0) >= 1000 ? 'bg-green-100' : 'bg-gray-200'}`}>
                      {(referralData?.total_earnings || 0) >= 1000 ?
                        <DollarSign className="h-4 w-4 text-green-600" /> :
                        <DollarSign className="h-4 w-4 text-gray-400" />
                      }
                    </div>
                    <div>
                      <p className="text-sm font-medium">Câștigător</p>
                      <p className="text-xs text-gray-600">1000 LEI câștigați</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Support */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <Phone className="h-5 w-5 mr-2 text-blue-600" />
                  Ai nevoie de ajutor?
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  Echipa noastră te poate ajuta cu întrebări despre programul de recomandări.
                </p>
                <Button className="w-full bg-green-600 hover:bg-green-700" asChild>
                  <a href="https://wa.me/40723456789" target="_blank" rel="noopener noreferrer">
                    <MessageCircle className="h-4 w-4 mr-2" />
                    WhatsApp Support
                  </a>
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Referral;