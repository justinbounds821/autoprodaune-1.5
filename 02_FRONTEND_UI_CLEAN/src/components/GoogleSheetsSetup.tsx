import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { GoogleSheetsService } from "@/utils/GoogleSheetsService";
import { Settings, CheckCircle, AlertCircle } from "lucide-react";

interface GoogleSheetsSetupProps {
  onSetupComplete?: () => void;
}

export const GoogleSheetsSetup = ({ onSetupComplete }: GoogleSheetsSetupProps) => {
  const { toast } = useToast();
  const [apiKey, setApiKey] = useState("");
  const [sheetId, setSheetId] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isConfigured, setIsConfigured] = useState(() => {
    const { apiKey: savedKey, sheetId: savedId } = GoogleSheetsService.getCredentials();
    return !!(savedKey && savedId);
  });

  const handleSetup = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!apiKey.trim() || !sheetId.trim()) {
      toast({
        title: "Eroare",
        description: "Te rugăm să completezi toate câmpurile",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      // Test connection
      const isValid = await GoogleSheetsService.testConnection(apiKey, sheetId);
      
      if (!isValid) {
        toast({
          title: "Eroare conexiune",
          description: "Nu pot accesa Google Sheet-ul. Verifică API Key și Sheet ID.",
          variant: "destructive",
        });
        return;
      }

      // Save credentials
      GoogleSheetsService.saveCredentials(apiKey, sheetId);
      setIsConfigured(true);
      
      toast({
        title: "Configurare completă!",
        description: "Google Sheets a fost configurat cu succes. Lead-urile vor fi salvate automat.",
      });

      onSetupComplete?.();
      
    } catch (error) {
      toast({
        title: "Eroare",
        description: "A apărut o eroare în timpul configurării.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    localStorage.removeItem('google_sheets_api_key');
    localStorage.removeItem('google_sheet_id');
    setIsConfigured(false);
    setApiKey("");
    setSheetId("");
    
    toast({
      title: "Configurare resetată",
      description: "Credențialele Google Sheets au fost șterse.",
    });
  };

  // Show configuration form

  return (
    <Card className="w-full max-w-2xl mx-auto mb-8 border-orange-200 bg-orange-50">
      <CardHeader>
        <CardTitle className="flex items-center text-orange-600">
          <AlertCircle className="h-5 w-5 mr-2" />
          Configurare Google Sheets
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h4 className="font-semibold text-yellow-800 mb-2">Pași pentru configurare:</h4>
          <ol className="text-sm text-yellow-700 space-y-1 list-decimal list-inside">
            <li>Mergi la <a href="https://console.developers.google.com/" target="_blank" rel="noopener noreferrer" className="underline">Google Cloud Console</a></li>
            <li>Activează Google Sheets API</li>
            <li>Creează un API Key</li>
            <li>Creează un Google Sheet și copiază ID-ul din URL</li>
            <li>Asigură-te că Sheet-ul este public sau partajat</li>
          </ol>
        </div>

        <form onSubmit={handleSetup} className="space-y-4">
          <div>
            <Label htmlFor="apiKey">Google Sheets API Key</Label>
            <Input
              id="apiKey"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="AIzaSy..."
              className="mt-1"
            />
          </div>

          <div>
            <Label htmlFor="sheetId">Google Sheet ID</Label>
            <Input
              id="sheetId"
              type="text"
              value={sheetId}
              onChange={(e) => setSheetId(e.target.value)}
              placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
              className="mt-1"
            />
            <p className="text-xs text-muted-foreground mt-1">
              ID-ul din URL-ul Google Sheet-ului (între /d/ și /edit)
            </p>
          </div>

          <Button 
            type="submit" 
            className="w-full" 
            disabled={isLoading}
          >
            {isLoading ? "Se testează conexiunea..." : "Configurează Google Sheets"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};