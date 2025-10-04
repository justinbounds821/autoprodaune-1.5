import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import LeadTracker from '@/components/LeadTracker';

const TrackPage = () => {
  const { leadId } = useParams<{ leadId: string }>();

  if (!leadId) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">ID Lead invalid</h1>
          <Link to="/">
            <Button>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Înapoi la pagina principală
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center space-x-2 text-foreground hover:text-primary transition-colors">
              <ArrowLeft className="w-5 h-5" />
              <span>AutoPro Daune</span>
            </Link>
            <div className="text-sm text-muted-foreground">
              Urmărire Lead #{leadId}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Urmărire Status Lead
          </h1>
          <p className="text-muted-foreground">
            Monitorizează progresul evaluării daunelor auto
          </p>
        </div>

        <LeadTracker leadId={leadId} />
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-sm text-muted-foreground">
            <p>&copy; 2024 AutoPro Daune. Toate drepturile rezervate.</p>
            <p className="mt-2">
              Pentru întrebări: <span className="text-primary">0747.694.114</span> | 
              <span className="text-primary"> contact@autoprodaune.ro</span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default TrackPage;