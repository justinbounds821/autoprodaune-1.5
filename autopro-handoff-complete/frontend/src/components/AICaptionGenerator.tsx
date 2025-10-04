import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Sparkles,
  Copy,
  RefreshCw,
  Check,
  Hash,
  Heart,
  MessageSquare,
  Share2
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface CaptionOptions {
  tone: 'professional' | 'casual' | 'funny' | 'inspiring' | 'urgent';
  platform: 'TikTok' | 'Instagram' | 'Facebook';
  includeHashtags: boolean;
  maxLength: number;
  topic: string;
}

interface GeneratedCaption {
  caption: string;
  hashtags: string[];
  engagement: {
    estimated: number;
    factors: string[];
  };
}

const TONE_EXAMPLES = {
  professional: 'Profesional, clar, focus pe rezultate',
  casual: 'Relaxat, prietenos, conversațional',
  funny: 'Amuzant, cu umor, memorable',
  inspiring: 'Motivant, pozitiv, inspirational',
  urgent: 'Urgent, cu call-to-action puternic'
};

const PLATFORM_LIMITS = {
  TikTok: { maxLength: 300, hashtags: 5 },
  Instagram: { maxLength: 2200, hashtags: 30 },
  Facebook: { maxLength: 63206, hashtags: 10 }
};

const TOPIC_SUGGESTIONS = [
  'Accidente auto',
  'Daune auto',
  'Asigurări',
  'Reparații auto',
  'Servicii juridice',
  'Compensatii',
  'Expertize auto',
  'Consultanță legală'
];

export default function AICaptionGenerator() {
  const { toast } = useToast();
  const [options, setOptions] = useState<CaptionOptions>({
    tone: 'professional',
    platform: 'TikTok',
    includeHashtags: true,
    maxLength: 300,
    topic: ''
  });
  const [generatedCaption, setGeneratedCaption] = useState<GeneratedCaption | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    if (!options.topic.trim()) {
      toast({
        title: "Lipsește topicul",
        description: "Introdu un topic pentru a genera caption-ul.",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      
      // Simulated AI generation - în producție ar fi API call către OpenAI
      const mockCaption = generateMockCaption(options);
      setGeneratedCaption(mockCaption);
      
      toast({
        title: "Caption generat!",
        description: "AI-ul a creat un caption optimizat pentru platforma ta.",
      });

    } catch (error) {
      console.error('Caption generation failed:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut genera caption-ul.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const generateMockCaption = (opts: CaptionOptions): GeneratedCaption => {
    const baseCaptions = {
      professional: `Aveți un accident auto? Nu lăsați lucrurile să se complice! 
      
      Echipa noastră de experți vă ajută să obțineți compensația cuvenită pentru daunele auto. 

      ✅ Expertize gratuite
      ✅ Consultanță juridică
      ✅ Negociere cu asigurătorii
      ✅ Suport complet proces

      Contactați-ne acum pentru o evaluare gratuită!`,

      casual: `Hey! Știai că după un accident auto ai drepturi? 🚗

      Nu te lăsa păcălit de asigurători! Noi te ajutăm să obții ce îți revine.

      🆓 Expertiză gratuită
      📞 Răspundem rapid
      💪 Luptăm pentru tine

      Dă-ne un mesaj să vorbim!`,

      funny: `Accident auto? Been there, done that! 😅

      Dar știi ce nu am făcut? Să mă las păcălit de asigurătorii care încearcă să mă facă să cred că o zgârietură valorează 50 de lei! 

      Noi îi facem să plătească ce trebuie! 💪

      #AccidentAuto #DauneAuto #NuMaPacalesc`,
    };

    const hashtags = generateHashtags(opts);
    const caption = baseCaptions[opts.tone] || baseCaptions.professional;

    return {
      caption: opts.includeHashtags ? `${caption}\n\n${hashtags.join(' ')}` : caption,
      hashtags,
      engagement: {
        estimated: Math.floor(Math.random() * 1000) + 500,
        factors: ['Topic trending', 'Hashtags relevante', 'Call-to-action clar']
      }
    };
  };

  const generateHashtags = (opts: CaptionOptions): string[] => {
    const baseHashtags = ['#AutoProDaune', '#AccidenteAuto', '#DauneAuto'];
    
    const topicHashtags = {
      'Accidente auto': ['#Accident', '#Auto'],
      'Daune auto': ['#Daune', '#Reparatie'],
      'Asigurări': ['#Asigurari', '#Asigurator'],
      'Reparații auto': ['#Reparatie', '#Service'],
      'Servicii juridice': ['#Avocat', '#Drept'],
      'Compensatii': ['#Compensatie', '#Banii'],
      'Expertize auto': ['#Expertiza', '#Evaluare'],
      'Consultanță legală': ['#Consultanta', '#Legal']
    };

    const additional = topicHashtags[opts.topic as keyof typeof topicHashtags] || ['#Auto', '#Daune'];
    return [...baseHashtags, ...additional].slice(0, PLATFORM_LIMITS[opts.platform].hashtags);
  };

  const handleCopy = async () => {
    if (!generatedCaption) return;

    try {
      await navigator.clipboard.writeText(generatedCaption.caption);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      
      toast({
        title: "Copiat!",
        description: "Caption-ul a fost copiat în clipboard.",
      });
    } catch (error) {
      toast({
        title: "Eroare",
        description: "Nu s-a putut copia caption-ul.",
        variant: "destructive",
      });
    }
  };

  const handlePlatformChange = (platform: string) => {
    const newPlatform = platform as CaptionOptions['platform'];
    const limits = PLATFORM_LIMITS[newPlatform];
    
    setOptions(prev => ({
      ...prev,
      platform: newPlatform,
      maxLength: limits.maxLength
    }));
  };

  return (
    <div className="space-y-6">
      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            AI Caption Generator
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Topic Input */}
          <div>
            <label className="block text-sm font-medium mb-2">Topic/Subiect</label>
            <Input
              value={options.topic}
              onChange={(e) => setOptions(prev => ({ ...prev, topic: e.target.value }))}
              placeholder="ex: Accidente auto, Daune auto, Asigurări..."
            />
            <div className="flex flex-wrap gap-1 mt-2">
              {TOPIC_SUGGESTIONS.map(topic => (
                <Button
                  key={topic}
                  variant="outline"
                  size="sm"
                  onClick={() => setOptions(prev => ({ ...prev, topic }))}
                  className="text-xs"
                >
                  {topic}
                </Button>
              ))}
            </div>
          </div>

          {/* Platform Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">Platformă</label>
            <Select value={options.platform} onValueChange={handlePlatformChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="TikTok">TikTok (300 chars)</SelectItem>
                <SelectItem value="Instagram">Instagram (2200 chars)</SelectItem>
                <SelectItem value="Facebook">Facebook (unlimited)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Tone Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">Ton</label>
            <Select
              value={options.tone}
              onValueChange={(value: CaptionOptions['tone']) => 
                setOptions(prev => ({ ...prev, tone: value }))
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(TONE_EXAMPLES).map(([tone, description]) => (
                  <SelectItem key={tone} value={tone}>
                    <div>
                      <div className="font-medium capitalize">{tone}</div>
                      <div className="text-xs text-gray-500">{description}</div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Options */}
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={options.includeHashtags}
                onChange={(e) => setOptions(prev => ({ ...prev, includeHashtags: e.target.checked }))}
                className="rounded"
              />
              <span className="text-sm">Include hashtags</span>
            </label>
          </div>

          {/* Generate Button */}
          <Button
            onClick={handleGenerate}
            disabled={loading || !options.topic.trim()}
            className="w-full"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Generez...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generează Caption AI
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Generated Caption */}
      {generatedCaption && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Caption Generat</CardTitle>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={handleCopy}>
                  {copied ? (
                    <>
                      <Check className="w-4 h-4 mr-2" />
                      Copiat!
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4 mr-2" />
                      Copiază
                    </>
                  )}
                </Button>
                <Button variant="outline" size="sm" onClick={handleGenerate}>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Regenerare
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Caption Preview */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="whitespace-pre-wrap text-sm">
                  {generatedCaption.caption}
                </div>
              </div>

              {/* Hashtags */}
              {generatedCaption.hashtags.length > 0 && (
                <div>
                  <p className="text-sm font-medium mb-2 flex items-center gap-2">
                    <Hash className="w-4 h-4" />
                    Hashtags ({generatedCaption.hashtags.length})
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {generatedCaption.hashtags.map(tag => (
                      <Badge key={tag} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Engagement Prediction */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Heart className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium">Engagement Estimat</span>
                  </div>
                  <p className="text-lg font-bold text-blue-600">
                    {generatedCaption.engagement.estimated}
                  </p>
                </div>

                <div className="p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <MessageSquare className="w-4 h-4 text-green-600" />
                    <span className="text-sm font-medium">Factori Pozitivi</span>
                  </div>
                  <div className="space-y-1">
                    {generatedCaption.engagement.factors.map(factor => (
                      <div key={factor} className="text-xs text-green-600">
                        • {factor}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
