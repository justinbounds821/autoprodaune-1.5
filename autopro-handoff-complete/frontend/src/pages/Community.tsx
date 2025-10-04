import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import {
  MessageCircle,
  Users,
  Shield,
  Clock,
  CheckCircle,
  ArrowLeft,
  ExternalLink,
  Upload,
  FileText,
  Camera,
  Phone,
  Star,
  Award,
  Zap,
  HeartHandshake,
  TrendingUp
} from 'lucide-react';

const Community = () => {
  const { toast } = useToast();
  const [joinedGroup, setJoinedGroup] = useState(false);

  const handleJoinGroup = () => {
    setJoinedGroup(true);
    toast({
      title: "Bun venit în comunitate!",
      description: "Ai fost adăugat cu succes în grupul WhatsApp AutoPro Daune.",
      variant: "default",
    });

    // Redirect to WhatsApp group (in real implementation)
    window.open('https://wa.me/40723456789', '_blank');
  };

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
                <h1 className="text-xl font-bold text-gray-900">Comunitatea AutoPro Daune</h1>
                <p className="text-sm text-gray-500">Suport 24/7 prin WhatsApp</p>
              </div>
            </div>
            <Badge className="bg-green-100 text-green-700">
              <Users className="h-4 w-4 mr-1" />
              2,847 membri activi
            </Badge>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        {/* Welcome Section */}
        <div className="max-w-4xl mx-auto mb-12">
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <MessageCircle className="h-10 w-10 text-green-600" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Bun venit în comunitatea noastră!
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Te-ai alăturat celei mai mari comunități din România de persoane care au obținut
              despăgubiri auto complete și rapide.
            </p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
            <Card className="text-center">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-green-600 mb-1">2,847</div>
                <div className="text-sm text-gray-600">Membri activi</div>
              </CardContent>
            </Card>
            <Card className="text-center">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-blue-600 mb-1">24/7</div>
                <div className="text-sm text-gray-600">Suport available</div>
              </CardContent>
            </Card>
            <Card className="text-center">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-purple-600 mb-1">~30 min</div>
                <div className="text-sm text-gray-600">Timp de răspuns</div>
              </CardContent>
            </Card>
            <Card className="text-center">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-orange-600 mb-1">98%</div>
                <div className="text-sm text-gray-600">Satisfacție clienți</div>
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 max-w-6xl mx-auto">
          {/* WhatsApp Group Card */}
          <Card className="shadow-xl">
            <CardHeader className="text-center pb-6">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageCircle className="h-8 w-8 text-green-600" />
              </div>
              <CardTitle className="text-2xl text-gray-900">
                Alătură-te grupului WhatsApp
              </CardTitle>
              <CardDescription className="text-lg">
                Comunicate direct cu experții noștri și primește actualizări în timp real despre cazul tău.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-semibold text-green-800 mb-2 flex items-center">
                  <CheckCircle className="h-5 w-5 mr-2" />
                  Ce vei găsi în grup:
                </h3>
                <ul className="text-green-700 space-y-1 text-sm">
                  <li>• Actualizări instant despre cazul tău</li>
                  <li>• Consiliere gratuită de la experți</li>
                  <li>• Suport pentru documente și formulare</li>
                  <li>• Comunitate de oameni în situații similare</li>
                  <li>• Anunțuri despre noi servicii și promoții</li>
                </ul>
              </div>

              {!joinedGroup ? (
                <Button
                  onClick={handleJoinGroup}
                  className="w-full h-14 text-lg bg-green-600 hover:bg-green-700"
                >
                  <MessageCircle className="mr-2 h-6 w-6" />
                  Alătură-te ACUM în grupa WhatsApp
                </Button>
              ) : (
                <div className="text-center p-6 bg-green-50 rounded-lg">
                  <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-3" />
                  <h3 className="font-semibold text-green-800 mb-2">Felicitări!</h3>
                  <p className="text-green-700">Ai fost adăugat cu succes în grupa noastră WhatsApp.</p>
                </div>
              )}

              <div className="flex justify-center space-x-4 text-sm text-gray-500">
                <div className="flex items-center">
                  <Shield className="h-4 w-4 mr-1 text-green-500" />
                  Privat & Securizat
                </div>
                <div className="flex items-center">
                  <Users className="h-4 w-4 mr-1 text-blue-500" />
                  Comunitate verificată
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Document Upload Card */}
          <Card className="shadow-xl">
            <CardHeader className="text-center pb-6">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Upload className="h-8 w-8 text-blue-600" />
              </div>
              <CardTitle className="text-2xl text-gray-900">
                Încarcă documentele
              </CardTitle>
              <CardDescription className="text-lg">
                Trimite-ne documentele direct prin WhatsApp pentru o analiză rapidă.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 gap-4">
                <div className="flex items-center p-3 bg-gray-50 rounded-lg">
                  <FileText className="h-8 w-8 text-blue-600 mr-3" />
                  <div>
                    <h4 className="font-medium text-gray-900">Documente esențiale</h4>
                    <p className="text-sm text-gray-600">Proces verbal, constatare amiabilă</p>
                  </div>
                </div>

                <div className="flex items-center p-3 bg-gray-50 rounded-lg">
                  <Camera className="h-8 w-8 text-green-600 mr-3" />
                  <div>
                    <h4 className="font-medium text-gray-900">Fotografii accident</h4>
                    <p className="text-sm text-gray-600">Mașini, drum, plăci de înmatriculare</p>
                  </div>
                </div>

                <div className="flex items-center p-3 bg-gray-50 rounded-lg">
                  <Phone className="h-8 w-8 text-purple-600 mr-3" />
                  <div>
                    <h4 className="font-medium text-gray-900">Suport instant</h4>
                    <p className="text-sm text-gray-600">Răspuns în maxim 30 de minute</p>
                  </div>
                </div>
              </div>

              <Button
                variant="outline"
                className="w-full h-12 border-2 border-blue-600 text-blue-600 hover:bg-blue-50"
                asChild
              >
                <a href="https://wa.me/40723456789" target="_blank" rel="noopener noreferrer">
                  <Upload className="mr-2 h-5 w-5" />
                  Trimite documente pe WhatsApp
                  <ExternalLink className="ml-2 h-4 w-4" />
                </a>
              </Button>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-semibold text-blue-800 mb-2">📋 Sfat expert:</h4>
                <p className="text-blue-700 text-sm">
                  Cu cât trimiți documentele mai repede, cu atât putem începe mai rapid procesul
                  de recuperare a despăgubirilor tale.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Benefits Section */}
        <section className="mt-16 max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            De ce să alegi comunitatea noastră?
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Star className="h-6 w-6 text-yellow-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Experți cu experiență</h3>
                <p className="text-gray-600 text-sm">
                  Peste 15 ani în domeniul despăgubirilor auto cu mii de cazuri rezolvate cu succes.
                </p>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Zap className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Rapiditate garantată</h3>
                <p className="text-gray-600 text-sm">
                  Majoritatea cazurilor sunt rezolvate în 24-48 ore, nu în luni sau ani.
                </p>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <HeartHandshake className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Suport emoțional</h3>
                <p className="text-gray-600 text-sm">
                  Înțelegem prin ce treci și îți oferim suport complet pe toată durata procesului.
                </p>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Shield className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Fără riscuri</h3>
                <p className="text-gray-600 text-sm">
                  Plătești doar după ce primești despăgubirile. Fără costuri ascunse.
                </p>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="h-6 w-6 text-orange-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Rezultate maxime</h3>
                <p className="text-gray-600 text-sm">
                  Obții întotdeauna suma maximă posibilă, nu doar ce oferă asigurătorul.
                </p>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Award className="h-6 w-6 text-red-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Recomandă și câștigă</h3>
                <p className="text-gray-600 text-sm">
                  200 LEI pentru fiecare prieten recomandat care devine client.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Testimonials */}
        <section className="mt-16 bg-gradient-to-r from-green-600 to-blue-600 rounded-3xl p-8 text-white">
          <h2 className="text-3xl font-bold text-center mb-8">
            Experiențe din comunitate
          </h2>

          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardContent className="p-6">
                <div className="flex mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-white mb-4">
                  "Grupa WhatsApp m-a ajutat enorm! Am fost ghidat pas cu pas și am primit toate
                  informațiile de care aveam nevoie. Recomand cu încredere!"
                </p>
                <div className="flex justify-between items-center">
                  <span className="text-white/80 font-medium">Alexandra M.</span>
                  <Badge className="bg-green-500 text-white">6,800 LEI primit</Badge>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardContent className="p-6">
                <div className="flex mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-white mb-4">
                  "Comunitatea este incredibilă! M-au ajutat să înțeleg tot procesul și să-mi
                  primesc banii mult mai repede decât mă așteptam."
                </p>
                <div className="flex justify-between items-center">
                  <span className="text-white/80 font-medium">Cristian P.</span>
                  <Badge className="bg-green-500 text-white">4,500 LEI primit</Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Contact Section */}
        <section className="mt-16 text-center max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Ai întrebări? Contactează-ne direct!
          </h2>
          <p className="text-gray-600 mb-8">
            Echipa noastră de experți este disponibilă 24/7 pentru a te ajuta cu orice întrebare.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              className="bg-green-600 hover:bg-green-700"
              asChild
            >
              <a href="https://wa.me/40723456789" target="_blank" rel="noopener noreferrer">
                <MessageCircle className="mr-2 h-5 w-5" />
                WhatsApp Direct
              </a>
            </Button>

            <Button
              size="lg"
              variant="outline"
              className="border-2 border-blue-600 text-blue-600 hover:bg-blue-50"
              asChild
            >
              <Link to="/referral">
                <Award className="mr-2 h-5 w-5" />
                Program Recomandări
              </Link>
            </Button>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Community;