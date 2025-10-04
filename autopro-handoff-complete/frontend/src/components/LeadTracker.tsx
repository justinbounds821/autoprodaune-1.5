import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  CheckCircle, 
  Clock, 
  Phone, 
  FileText, 
  User, 
  Calendar,
  MessageCircle
} from 'lucide-react';

interface TrackingStep {
  id: string;
  title: string;
  description: string;
  status: 'completed' | 'current' | 'pending';
  timestamp?: string;
}

interface LeadStatus {
  id: string;
  steps: TrackingStep[];
  estimatedCompletion: string;
  progress: number;
}

const LeadTracker = ({ leadId }: { leadId: string }) => {
  const [status, setStatus] = useState<LeadStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      const mockStatus: LeadStatus = {
        id: leadId,
        progress: 60,
        estimatedCompletion: '24 ore',
        steps: [
          {
            id: '1',
            title: 'Lead-ul a fost înregistrat',
            description: 'Formularul și fotografiile au fost primite cu succes',
            status: 'completed',
            timestamp: new Date(Date.now() - 3600000).toLocaleString('ro-RO')
          },
          {
            id: '2',
            title: 'Validare inițială',
            description: 'Documentele și fotografiile sunt verificate',
            status: 'completed',
            timestamp: new Date(Date.now() - 1800000).toLocaleString('ro-RO')
          },
          {
            id: '3',
            title: 'Contact cu expertul',
            description: 'Un expert AutoPro Daune vă va contacta pentru programare',
            status: 'current'
          },
          {
            id: '4',
            title: 'Evaluare la fața locului',
            description: 'Expertul va evalua daunele și va întocmi raportul',
            status: 'pending'
          },
          {
            id: '5',
            title: 'Raport finalizat',
            description: 'Raportul de expertiză va fi trimis către dvs.',
            status: 'pending'
          }
        ]
      };
      setStatus(mockStatus);
      setLoading(false);
    }, 1000);
  }, [leadId]);

  if (loading) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-muted rounded w-3/4"></div>
            <div className="h-20 bg-muted rounded"></div>
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-16 bg-muted rounded"></div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!status) return null;

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <FileText className="w-5 h-5" />
          <span>Urmărire Lead #{status.id}</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Progress Overview */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progres</span>
            <span>{status.progress}%</span>
          </div>
          <Progress value={status.progress} className="w-full" />
          <p className="text-sm text-muted-foreground">
            Timp estimat de finalizare: {status.estimatedCompletion}
          </p>
        </div>

        {/* Steps */}
        <div className="space-y-4">
          {status.steps.map((step, index) => (
            <div key={step.id} className="flex items-start space-x-4">
              {/* Step Icon */}
              <div className="flex-shrink-0 mt-1">
                {step.status === 'completed' ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : step.status === 'current' ? (
                  <Clock className="w-5 h-5 text-blue-500" />
                ) : (
                  <div className="w-5 h-5 rounded-full border-2 border-muted-foreground"></div>
                )}
              </div>

              {/* Step Content */}
              <div className="flex-1 space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className={`font-medium ${
                    step.status === 'completed' ? 'text-green-600' :
                    step.status === 'current' ? 'text-blue-600' :
                    'text-muted-foreground'
                  }`}>
                    {step.title}
                  </h3>
                  <Badge variant={
                    step.status === 'completed' ? 'default' :
                    step.status === 'current' ? 'secondary' :
                    'outline'
                  }>
                    {step.status === 'completed' ? 'Finalizat' :
                     step.status === 'current' ? 'În progres' :
                     'În așteptare'}
                  </Badge>
                </div>
                
                <p className="text-sm text-muted-foreground">
                  {step.description}
                </p>
                
                {step.timestamp && (
                  <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                    <Calendar className="w-3 h-3" />
                    <span>{step.timestamp}</span>
                  </div>
                )}

                {/* Connection line */}
                {index < status.steps.length - 1 && (
                  <div className="ml-2.5 h-8 w-0.5 bg-border"></div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Contact Section */}
        <div className="border-t pt-4 space-y-3">
          <h4 className="font-medium flex items-center space-x-2">
            <MessageCircle className="w-4 h-4" />
            <span>Ai întrebări?</span>
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <Button variant="outline" className="justify-start">
              <Phone className="w-4 h-4 mr-2" />
              Sună acum
            </Button>
            <Button variant="outline" className="justify-start">
              <MessageCircle className="w-4 h-4 mr-2" />
              Trimite mesaj
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default LeadTracker;