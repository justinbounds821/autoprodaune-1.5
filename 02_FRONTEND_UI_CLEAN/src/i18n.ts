import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  ro: {
    translation: {
      header: {
        home: 'Acasă',
        track: 'Urmărește Status',
        call: 'Sună-ne',
        dashboard: 'Dashboard'
      },
      aiInsights: {
        loading: 'AI analizează datele…',
        retry: 'Încearcă din nou',
        noData: 'Nu există insights AI în sistem.',
        totalInsights: 'Total Insights',
        highConfidence: 'Încredere Mare',
        criticalAlerts: 'Alerte Critice',
        categories: 'Categorii',
        generated: 'AI a generat un insight nou pentru tine.',
        generatePrediction: 'Generează Predicție',
        errorTitle: 'Eroare la încărcarea insight-urilor',
        errorDescription: 'A apărut o eroare la comunicarea cu serviciul de analytics.'
      }
    }
  },
  en: {
    translation: {
      header: {
        home: 'Home',
        track: 'Track Status',
        call: 'Call us',
        dashboard: 'Dashboard'
      },
      aiInsights: {
        loading: 'AI is analysing your data…',
        retry: 'Try again',
        noData: 'No AI insights found.',
        totalInsights: 'Total insights',
        highConfidence: 'High confidence',
        criticalAlerts: 'Critical alerts',
        categories: 'Categories',
        generated: 'AI generated a new insight for you.',
        generatePrediction: 'Generate prediction',
        errorTitle: 'Failed to load AI insights',
        errorDescription: 'There was a problem communicating with the analytics service.'
      }
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'ro',
    interpolation: { escapeValue: false },
    detection: {
      order: ['querystring', 'localStorage', 'navigator'],
      caches: ['localStorage']
    }
  });

export default i18n;
