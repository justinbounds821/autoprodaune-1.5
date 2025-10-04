import React from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertTriangle } from 'lucide-react';

export const HeyGenKeyMissingBanner: React.FC = () => {
  return (
    <Alert variant="destructive" className="mb-4">
      <AlertTriangle className="h-4 w-4" />
      <AlertTitle>HeyGen API Key lipsește</AlertTitle>
      <AlertDescription>
        Configurarea HeyGen API key este necesară pentru a genera videoclipuri AI cu avatare profesionale.
        Contactează administratorul pentru a activa această funcționalitate.
      </AlertDescription>
    </Alert>
  );
};

export default HeyGenKeyMissingBanner;
