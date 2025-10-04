import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Upload, X, Paperclip, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

interface LeadFileUploadProps {
  leadId: string;
  onUploadComplete?: () => void;
}

export default function LeadFileUpload({ leadId, onUploadComplete }: LeadFileUploadProps) {
  const { toast } = useToast();
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [open, setOpen] = useState(false);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (selectedFiles.length === 0) return;

    try {
      setUploading(true);

      for (const file of selectedFiles) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('lead_id', leadId);

        const response = await fetch('/api/leads/upload-attachment', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Failed to upload ${file.name}`);
        }
      }

      toast({
        title: "Fișiere încărcate",
        description: `${selectedFiles.length} fișiere au fost încărcate cu succes.`,
      });

      setSelectedFiles([]);
      setOpen(false);
      
      if (onUploadComplete) {
        onUploadComplete();
      }

    } catch (error) {
      console.error('Upload error:', error);
      toast({
        title: "Eroare la încărcare",
        description: "Nu s-au putut încărca fișierele.",
        variant: "destructive",
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Paperclip className="w-4 h-4 mr-2" />
          Atașează fișiere
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Încarcă Fișiere</DialogTitle>
          <DialogDescription>
            Adaugă documente, imagini sau alte fișiere pentru acest lead (max 10MB per fișier)
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* File Input */}
          <div>
            <Input
              type="file"
              onChange={handleFileSelect}
              multiple
              disabled={uploading}
              className="cursor-pointer"
            />
          </div>

          {/* Selected Files List */}
          {selectedFiles.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium">Fișiere selectate:</p>
              {selectedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 bg-gray-50 rounded"
                >
                  <span className="text-sm truncate flex-1">{file.name}</span>
                  <span className="text-xs text-gray-500 mx-2">
                    {(file.size / 1024).toFixed(1)} KB
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(index)}
                    disabled={uploading}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          {/* Upload Button */}
          <Button
            onClick={uploadFiles}
            disabled={selectedFiles.length === 0 || uploading}
            className="w-full"
          >
            {uploading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Se încarcă...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4 mr-2" />
                Încarcă {selectedFiles.length} fișier{selectedFiles.length !== 1 ? 'e' : ''}
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

