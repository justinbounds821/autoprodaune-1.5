import { AutoProApiService, LeadData as ApiLeadData } from '../services/autoproApi';

interface LeadData {
  name: string;
  phone: string;
  details: string;
  files: File[];
  timestamp?: string;
  email?: string;
  location?: string;
  damageType?: string;
  priority?: string;
}

export class GoogleSheetsService {
  private static SHEETS_API_KEY_STORAGE = 'google_sheets_api_key';
  private static SHEET_ID_STORAGE = 'google_sheet_id';

  static saveCredentials(apiKey: string, sheetId: string): void {
    localStorage.setItem(this.SHEETS_API_KEY_STORAGE, apiKey);
    localStorage.setItem(this.SHEET_ID_STORAGE, sheetId);
    console.log('Google Sheets credentials saved');
  }

  static getCredentials(): { apiKey: string | null; sheetId: string | null } {
    return {
      apiKey: localStorage.getItem(this.SHEETS_API_KEY_STORAGE),
      sheetId: localStorage.getItem(this.SHEET_ID_STORAGE)
    };
  }

  static async submitLead(leadData: LeadData): Promise<{ success: boolean; error?: string }> {
    try {
      console.log('🔄 Adaugă lead prin Supabase Edge Function');
      
      // Apelează direct Supabase Edge Function
      const response = await fetch('https://orctxxpyiqzbordibqxi.supabase.co/functions/v1/google-sheets-append', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yY3R4eHB5aXF6Ym9yZGlicXhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc5MzE5MTUsImV4cCI6MjA3MzUwNzkxNX0.DBfz7Ho3QebEgOwjXh8ciWD83jOT_bgVIl7uVknv4D4'
        },
        body: JSON.stringify({
          name: leadData.name,
          phone: leadData.phone,
          details: leadData.details,
          files: leadData.files.map(f => f.name)
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('✅ Lead adăugat cu succes în Google Sheets:', result);
      return { success: true };
      
    } catch (error) {
      console.error('❌ Eroare la adăugarea lead-ului:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Eroare necunoscută' 
      };
    }
  }

  static async getLeads(): Promise<{ success: boolean; data?: any[]; error?: string }> {
    try {
      console.log('🔄 Obține lead-uri prin Streamlit API Backend');
      
      const result = await AutoProApiService.getLeads();
      
      if (result.success) {
        console.log('✅ Lead-uri obținute cu succes prin Streamlit API');
        return { success: true, data: result.data };
      } else {
        console.error('❌ Eroare la obținerea lead-urilor:', result.error);
        return { success: false, error: result.error };
      }
      
    } catch (error) {
      console.error('❌ Eroare la obținerea lead-urilor:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Eroare necunoscută' 
      };
    }
  }

  static async checkConnection(): Promise<{ success: boolean; error?: string }> {
    try {
      console.log('🔄 Verifică conectivitatea cu Streamlit API');
      
      const result = await AutoProApiService.checkApiHealth();
      
      if (result.success) {
        console.log('✅ Conectivitate OK cu Streamlit API');
        return { success: true };
      } else {
        console.error('❌ Problema de conectivitate:', result.error);
        return { success: false, error: result.error };
      }
      
    } catch (error) {
      console.error('❌ Eroare la verificarea conectivității:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Eroare necunoscută' 
      };
    }
  }

  static async testConnection(apiKey: string, sheetId: string): Promise<boolean> {
    try {
      const response = await fetch(
        `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}?key=${apiKey}`,
        { method: 'GET' }
      );
      return response.ok;
    } catch (error) {
      console.error('Error testing Google Sheets connection:', error);
      return false;
    }
  }
}