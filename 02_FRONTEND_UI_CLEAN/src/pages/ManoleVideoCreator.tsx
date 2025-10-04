import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { Upload, Video, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

export default function ManoleVideoCreator() {
  const [prompt, setPrompt] = useState('');
  const [manolePhoto, setManolePhoto] = useState<File | null>(null);
  const [accidentFootage, setAccidentFootage] = useState<File[]>([]);
  const [displayMode, setDisplayMode] = useState('sequence');
  const [voiceEmotion, setVoiceEmotion] = useState('professional');
  const [progress, setProgress] = useState(0);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const { toast } = useToast();

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast({
          title: 'Eroare',
          description: 'Te rog încarcă o imagine (JPG, PNG, etc.)',
          variant: 'destructive'
        });
        return;
      }
      setManolePhoto(file);
    }
  };

  const handleFootageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setAccidentFootage(files);
  };

  const handleGenerate = async () => {
    // Validate inputs
    if (!prompt || prompt.length < 10) {
      toast({
        title: 'Eroare',
        description: 'Prompt-ul trebuie să aibă cel puțin 10 caractere',
        variant: 'destructive'
      });
      return;
    }

    if (!manolePhoto) {
      toast({
        title: 'Eroare',
        description: 'Te rog încarcă o foto cu Manole',
        variant: 'destructive'
      });
      return;
    }

    setGenerating(true);
    setProgress(0);
    setResult(null);

    try {
      // Create FormData
      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('manole_photo', manolePhoto);
      formData.append('display_mode', displayMode);
      formData.append('voice_emotion', voiceEmotion);
      
      // Add accident footage
      accidentFootage.forEach(file => {
        formData.append('accident_footage', file);
      });

      setProgress(20);

      // Make API call
      const response = await fetch('/api/video/manole/generate', {
        method: 'POST',
        body: formData,
      });

      setProgress(100);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to generate video');
      }

      const data = await response.json();
      
      setResult(data);
      toast({
        title: 'Success! 🎬',
        description: data.message || 'Video generat cu succes!',
      });

    } catch (error: any) {
      console.error('Video generation error:', error);
      toast({
        title: 'Eroare',
        description: error.message || 'Nu s-a putut genera video-ul',
        variant: 'destructive'
      });
    } finally {
      setGenerating(false);
    }
  };

  const resetForm = () => {
    setPrompt('');
    setManolePhoto(null);
    setAccidentFootage([]);
    setProgress(0);
    setResult(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Video className="w-6 h-6" />
            Manole Video Creator
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Creează video-uri profesionale cu Manole vorbind despre daune auto
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Prompt Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium">
              📝 Prompt (ce vrei să spună Manole)
            </label>
            <Textarea
              placeholder="Ex: Explică pas cu pas cum completezi constatarea amiabilă după un accident auto. Menționează că poți ajuta cu expertiza și recuperarea daunelor."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={4}
              className="resize-none"
              disabled={generating}
            />
            <p className="text-xs text-muted-foreground">
              Minim 10 caractere. Fie specific despre ce vrei să comunice Manole.
            </p>
          </div>

          {/* Manole Photo Upload */}
          <div className="space-y-2">
            <label className="text-sm font-medium">
              📷 Foto Manole
            </label>
            <div className="flex items-center gap-4">
              <Input
                type="file"
                accept="image/*"
                onChange={handlePhotoChange}
                disabled={generating}
                className="cursor-pointer"
              />
              {manolePhoto && (
                <div className="flex items-center gap-2 text-sm text-green-600">
                  <CheckCircle className="w-4 h-4" />
                  {manolePhoto.name}
                </div>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              Foto de calitate (preferabil 1080x1920 sau similar). Față clară, professional.
            </p>
          </div>

          {/* Accident Footage Upload */}
          <div className="space-y-2">
            <label className="text-sm font-medium">
              🚗 Accident Footage (opțional)
            </label>
            <Input
              type="file"
              accept="image/*,video/*"
              multiple
              onChange={handleFootageChange}
              disabled={generating}
              className="cursor-pointer"
            />
            {accidentFootage.length > 0 && (
              <div className="text-sm text-green-600">
                {accidentFootage.length} fișier(e) selectat(e)
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              Poți adăuga poze/video-uri cu accidente pentru a ilustra cazuri reale.
            </p>
          </div>

          {/* Display Mode */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">
                🎭 Display Mode
              </label>
              <Select
                value={displayMode}
                onValueChange={setDisplayMode}
                disabled={generating}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sequence">
                    Secvențial (Manole → Accident → Manole)
                  </SelectItem>
                  <SelectItem value="pip">
                    Picture-in-Picture
                  </SelectItem>
                  <SelectItem value="split">
                    Split Screen
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Voice Emotion */}
            <div className="space-y-2">
              <label className="text-sm font-medium">
                🎤 Voice Emotion
              </label>
              <Select
                value={voiceEmotion}
                onValueChange={setVoiceEmotion}
                disabled={generating}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="professional">
                    Professional
                  </SelectItem>
                  <SelectItem value="empathetic">
                    Empathetic (Empatic)
                  </SelectItem>
                  <SelectItem value="urgent">
                    Urgent
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Progress Bar */}
          {generating && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Progress:</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} />
              <p className="text-xs text-muted-foreground text-center">
                Generare în progres... Poate dura 30-60 secunde.
              </p>
            </div>
          )}

          {/* Result Display */}
          {result && (
            <Alert className="bg-green-50 border-green-200">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <AlertDescription>
                <div className="space-y-2">
                  <p className="font-medium text-green-900">
                    Video generat cu succes! 🎉
                  </p>
                  <div className="text-sm text-green-800 space-y-1">
                    <p>Job ID: {result.job_id}</p>
                    <p>Durată: {result.duration}s</p>
                    <p>Mărime: {(result.file_size / 1024 / 1024).toFixed(2)} MB</p>
                    <p>Mode: {result.mode}</p>
                    <p>Emotion: {result.emotion}</p>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    Video path: {result.video_path}
                  </p>
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              onClick={handleGenerate}
              disabled={generating || !prompt || !manolePhoto}
              className="flex-1"
              size="lg"
            >
              {generating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Video className="w-4 h-4 mr-2" />
                  🎬 Generate Video
                </>
              )}
            </Button>

            {result && (
              <Button
                onClick={resetForm}
                variant="outline"
                size="lg"
              >
                Reset
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">ℹ️ Cum funcționează?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>1. <strong>Prompt</strong>: Scrie ce vrei să spună Manole (ex: sfaturi despre daune auto)</p>
          <p>2. <strong>Foto</strong>: Încarcă o foto de calitate cu Manole (se va anima automat)</p>
          <p>3. <strong>Accident Footage</strong>: Opțional, adaugă poze/video-uri cu accidente</p>
          <p>4. <strong>Voice</strong>: Selectează emoția vocii (folosim ElevenLabs sau Edge-TTS)</p>
          <p>5. <strong>Generate</strong>: Apasă butonul și așteaptă 30-60 secunde</p>
          <p className="mt-4 pt-4 border-t">
            <strong>Output</strong>: Video profesional cu Manole vorbind, accident footage (dacă ai adăugat), și WhatsApp CTA overlay!
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
