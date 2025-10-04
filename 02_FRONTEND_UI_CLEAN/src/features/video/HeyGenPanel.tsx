/**
 * FAZA 2.6: HeyGen Panel cu UX pentru cheia lipsă
 * Backend (handlerul existent de generate) + Frontend UX
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import autoproApi from '@/services/autoproApi';

interface HeyGenForm {
  script: string;
  avatar_id: string;
  voice_id: string;
  style: string;
  quality: string;
  language: string;
}

const HeyGenPanel: React.FC = () => {
  const [form, setForm] = useState<HeyGenForm>({
    script: '',
    avatar_id: '',
    voice_id: '',
    style: 'realistic',
    quality: 'high',
    language: 'ro'
  });
  
  const [configMissing, setConfigMissing] = useState(false);
  const [busy, setBusy] = useState(false);
  const { toast } = useToast();

  const onGenerate = async () => {
    setBusy(true);
    setConfigMissing(false);
    
    try {
      // Simulează apelul către autoproApi.generateHeygen(form)
      const response = await fetch('/api/video/heygen/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Eroare la generarea video');
      }
      
      const result = await response.json();
      toast.success("Cerere trimisă");
      
    } catch (e: any) {
      const msg = e?.message || String(e);
      if (msg.includes("HEYGEN_API_KEY")) {
        setConfigMissing(true);
      }
      toast.error(msg);
    } finally { 
      setBusy(false); 
    }
  };

  const updateForm = (field: keyof HeyGenForm, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          🎬 HeyGen Video Generator
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Script Input */}
        <div className="space-y-2">
          <Label htmlFor="script">Script Video (max 1000 caractere)</Label>
          <Textarea
            id="script"
            placeholder="Introdu textul pentru video..."
            value={form.script}
            onChange={(e) => updateForm('script', e.target.value)}
            maxLength={1000}
            rows={4}
          />
          <div className="text-sm text-gray-500">
            {form.script.length}/1000 caractere
          </div>
        </div>

        {/* Style Selection */}
        <div className="space-y-2">
          <Label htmlFor="style">Stil Video</Label>
          <Select value={form.style} onValueChange={(value) => updateForm('style', value)}>
            <SelectTrigger>
              <SelectValue placeholder="Selectează stilul" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="realistic">Realistic</SelectItem>
              <SelectItem value="animated">Animated</SelectItem>
              <SelectItem value="cartoon">Cartoon</SelectItem>
              <SelectItem value="documentary">Documentary</SelectItem>
              <SelectItem value="presentation">Presentation</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Quality Selection */}
        <div className="space-y-2">
          <Label htmlFor="quality">Calitate</Label>
          <Select value={form.quality} onValueChange={(value) => updateForm('quality', value)}>
            <SelectTrigger>
              <SelectValue placeholder="Selectează calitatea" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="low">Low</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="ultra">Ultra</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Language Selection */}
        <div className="space-y-2">
          <Label htmlFor="language">Limbă</Label>
          <Select value={form.language} onValueChange={(value) => updateForm('language', value)}>
            <SelectTrigger>
              <SelectValue placeholder="Selectează limba" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ro">Română</SelectItem>
              <SelectItem value="en">English</SelectItem>
              <SelectItem value="es">Español</SelectItem>
              <SelectItem value="fr">Français</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Avatar ID (Optional) */}
        <div className="space-y-2">
          <Label htmlFor="avatar_id">Avatar ID (opțional)</Label>
          <Input
            id="avatar_id"
            placeholder="ID avatar HeyGen..."
            value={form.avatar_id}
            onChange={(e) => updateForm('avatar_id', e.target.value)}
          />
        </div>

        {/* Voice ID (Optional) */}
        <div className="space-y-2">
          <Label htmlFor="voice_id">Voice ID (opțional)</Label>
          <Input
            id="voice_id"
            placeholder="ID voce HeyGen..."
            value={form.voice_id}
            onChange={(e) => updateForm('voice_id', e.target.value)}
          />
        </div>

        {/* Generate Button */}
        <Button 
          onClick={onGenerate}
          disabled={busy || configMissing || !form.script.trim()}
          className="w-full"
        >
          {busy ? 'Se generează...' : 'Generează Video'}
        </Button>

        {/* Config Missing Banner */}
        {configMissing && (
          <div className="mt-4 rounded border p-3 text-sm bg-yellow-100 border-yellow-400 text-yellow-800">
            ⚠️ <strong>Configurare necesară:</strong> Configurează <code className="bg-yellow-200 px-1 rounded">HEYGEN_API_KEY</code> în backend pentru a activa generarea video.
            <br />
            <small>Contactează administratorul pentru configurarea cheii API.</small>
          </div>
        )}

        {/* Info Panel */}
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm">
          <strong>💡 Informații:</strong>
          <ul className="mt-1 list-disc list-inside space-y-1">
            <li>Video-ul se va genera în aproximativ 2-5 minute</li>
            <li>Cost estimat: ~0.50 USD per video</li>
            <li>Format final: MP4, 1080p</li>
            <li>Subtitrări incluse automat</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};

export default HeyGenPanel;
