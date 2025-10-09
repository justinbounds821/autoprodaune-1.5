import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Play, Download, Trash2, Plus, RefreshCw, Video, User, Palette, Monitor, Sparkles } from 'lucide-react';
import AutoProApiService from '@/services/autoproApi';
import { useToast } from '@/hooks/use-toast';
import HeyGenKeyMissingBanner from '@/components/HeyGenKeyMissingBanner';

interface ProfessionalVideo {
  id: string;
  title: string;
  status: 'completed' | 'generating' | 'failed';
  url?: string;
  thumbnail?: string;
  thumbnail_base64?: string; // Generated thumbnail from video
  preview_base64?: string;
  createdAt: string;
  provider: string;
  avatar_type: string;
  background_type: string;
  aspect_ratio: string;
  metrics?: {
    views: number;
    likes: number;
    shares: number;
  };
}

interface Avatar {
  id: string;
  name: string;
  description: string;
  preview: string;
}

interface Background {
  id: string;
  name: string;
  description: string;
}

const VideoManagement: React.FC = () => {
  const { toast } = useToast();
  const [videos, setVideos] = useState<ProfessionalVideo[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [prompt, setPrompt] = useState('AutoPro Daune - Experții tăi în daune auto. Rezolvăm rapid și eficient!');

  // Professional video generation states
  const [avatars, setAvatars] = useState<Avatar[]>([]);
  const [backgrounds, setBackgrounds] = useState<Background[]>([]);
  const [selectedAvatar, setSelectedAvatar] = useState('professional');
  const [selectedBackground, setSelectedBackground] = useState('office');
  const [aspectRatio, setAspectRatio] = useState('portrait');
  const [resolution, setResolution] = useState('1080p');
  const [videoCapabilities, setVideoCapabilities] = useState<any>(null);
  
  // Video preview modal state
  const [previewVideo, setPreviewVideo] = useState<ProfessionalVideo | null>(null);
  const [showPreviewModal, setShowPreviewModal] = useState(false);

  // HeyGen video generation states
  const [heygenScript, setHeygenScript] = useState('Bună ziua! Sunt avocat AutoPro Daune. Vă ajut să obțineți despăgubiri complete pentru daunele auto. Apelați acum!');
  const [heygenAvatarId, setHeygenAvatarId] = useState('');
  const [heygenVoiceId, setHeygenVoiceId] = useState('');
  const [heygenStyle, setHeygenStyle] = useState('realistic');
  const [heygenQuality, setHeygenQuality] = useState('high');
  const [heygenGenerating, setHeygenGenerating] = useState(false);
  const [heygenProgress, setHeygenProgress] = useState<string>('');
  const [heygenAvatars, setHeygenAvatars] = useState<any[]>([]);
  const [heygenKeyAvailable, setHeygenKeyAvailable] = useState<boolean>(true);

  // Batch delete state
  const [selectedVideos, setSelectedVideos] = useState<Set<string>>(new Set());
  const [isDeletingBatch, setIsDeletingBatch] = useState(false);
  
  // Filter state
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [providerFilter, setProviderFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    loadVideos();
    loadAvatars();
    loadBackgrounds();
    loadCapabilities();
    loadHeyGenAvatars();
  }, []);

  const loadVideos = async () => {
    try {
      setLoading(true);

      // Load advanced video list from professional API
      const response = await fetch('/api/advanced-video/list-generated');
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.videos) {
          setVideos(data.videos.map((v: any) => ({
            id: v.filename.replace('.png', ''),
            title: v.config?.request?.text || 'Professional Video',
            status: 'completed' as const,
            url: v.preview_path,
            thumbnail: v.preview_path,
            preview_base64: v.preview_base64,
            createdAt: v.created || new Date().toISOString(),
            provider: 'AutoPro Professional',
            avatar_type: v.config?.request?.avatar_id || 'professional',
            background_type: v.config?.request?.background_id || 'office',
            aspect_ratio: v.config?.request?.aspect_ratio || 'portrait'
          })));
        }
      } else {
        // Fallback to older API if advanced not available
        const fallbackResponse = await AutoProApiService.getVideos();
        if (fallbackResponse.success && fallbackResponse.data) {
          setVideos(fallbackResponse.data.map((v: any) => ({
            ...v,
            avatar_type: v.avatar_type || 'professional',
            background_type: v.background_type || 'office',
            aspect_ratio: v.aspect_ratio || 'portrait'
          })));
        }
      }
    } catch (error) {
      console.error('Failed to load videos:', error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca video-urile.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadAvatars = async () => {
    try {
      const response = await fetch('/api/professional-video/avatars');
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.avatars) {
          setAvatars(data.avatars);
        }
      }
    } catch (error) {
      console.error('Failed to load avatars:', error);
    }
  };

  const loadBackgrounds = async () => {
    try {
      const response = await fetch('/api/professional-video/backgrounds');
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.backgrounds) {
          setBackgrounds(data.backgrounds);
        }
      }
    } catch (error) {
      console.error('Failed to load backgrounds:', error);
    }
  };

  const loadCapabilities = async () => {
    try {
      const response = await fetch('/api/advanced-video/capabilities');
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setVideoCapabilities(data);
        }
      }
    } catch (error) {
      console.error('Failed to load capabilities:', error);
    }
  };

  const generateThumbnail = async (videoId: string) => {
    try {
      const response = await fetch(`/api/video/${videoId}/thumbnail`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.thumbnail_base64) {
          // Update video în listă cu thumbnail-ul nou
          setVideos(prevVideos =>
            prevVideos.map(video =>
              video.id === videoId
                ? { ...video, thumbnail_base64: data.thumbnail_base64 }
                : video
            )
          );
        }
      }
    } catch (error) {
      console.error(`Failed to generate thumbnail for ${videoId}:`, error);
    }
  };

  const toggleVideoSelection = (videoId: string) => {
    setSelectedVideos(prev => {
      const newSet = new Set(prev);
      if (newSet.has(videoId)) {
        newSet.delete(videoId);
      } else {
        newSet.add(videoId);
      }
      return newSet;
    });
  };

  const selectAllVideos = () => {
    const allIds = new Set(videos.map(v => v.id));
    setSelectedVideos(allIds);
  };

  const deselectAllVideos = () => {
    setSelectedVideos(new Set());
  };

  const handleBatchDelete = async () => {
    if (selectedVideos.size === 0) {
      toast({
        title: "Nicio selecție",
        description: "Selectează cel puțin un video pentru ștergere.",
        variant: "destructive",
      });
      return;
    }

    if (!confirm(`Ești sigur că vrei să ștergi ${selectedVideos.size} video-uri?`)) {
      return;
    }

    try {
      setIsDeletingBatch(true);
      const videoIdsArray = Array.from(selectedVideos);

      const response = await fetch('/api/video/batch', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(videoIdsArray),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Remove deleted videos from list
        setVideos(prev => prev.filter(v => !selectedVideos.has(v.id)));
        setSelectedVideos(new Set());

        toast({
          title: "✅ Video-uri șterse!",
          description: `${data.deleted_count}/${data.total_requested} video-uri au fost șterse cu succes.`,
        });
      } else {
        throw new Error('Batch delete failed');
      }
    } catch (error) {
      console.error('Failed to delete videos:', error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut șterge toate video-urile.",
        variant: "destructive",
      });
    } finally {
      setIsDeletingBatch(false);
    }
  };

  const handleGenerateVideo = async () => {
    if (!prompt.trim()) return;

    try {
      setGenerating(true);

      // Use advanced professional video generation API
      const requestBody = {
        text: prompt,
        avatar_type: selectedAvatar,
        background_type: selectedBackground,
        aspect_ratio: aspectRatio,
        resolution: resolution
      };

      const response = await fetch('/api/advanced-video/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Create new video entry
          const newVideo: ProfessionalVideo = {
            id: data.video_preview_path?.split('/').pop()?.replace('.png', '') || Date.now().toString(),
            title: prompt.substring(0, 50) + (prompt.length > 50 ? '...' : ''),
            status: 'completed',
            url: data.video_preview_path,
            thumbnail: data.video_preview_path,
            preview_base64: data.preview_image_base64,
            createdAt: new Date().toISOString(),
            provider: 'AutoPro Professional AI',
            avatar_type: selectedAvatar,
            background_type: selectedBackground,
            aspect_ratio: aspectRatio
          };

          setVideos(prev => [newVideo, ...prev]);
          toast({
            title: "🎬 Video profesional generat!",
            description: `Video cu avatar ${selectedAvatar} și fundal ${selectedBackground} a fost creat cu succes!`,
          });

          // Reload videos to get updated list
          loadVideos();
        } else {
          throw new Error(data.message || 'Failed to generate video');
        }
      } else {
        throw new Error('Network error');
      }
    } catch (error) {
      console.error('Failed to generate video:', error);
      toast({
        title: "Eroare generare video",
        description: "Nu s-a putut genera video-ul profesional. Verifică conexiunea.",
        variant: "destructive",
      });
    } finally {
      setGenerating(false);
    }
  };

  const handlePlayVideo = (video: ProfessionalVideo) => {
    setPreviewVideo(video);
    setShowPreviewModal(true);
    toast({
      title: "🎬 Preview video",
      description: `Deschid preview pentru: ${video.title}`,
    });
  };

  const handleDeleteVideo = async (id: string) => {
    try {
      // Use the new autoproApi method
      const response = await AutoProApiService.deleteVideoJob(id);

      if (response.success) {
        setVideos(prev => prev.filter(v => v.id !== id));
        toast({
          title: "✅ Video șters",
          description: response.message || "Video-ul a fost șters cu succes din sistem!",
        });
      } else {
        throw new Error(response.error || 'Delete failed');
      }
    } catch (error) {
      console.error('Failed to delete video:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut șterge video-ul.",
        variant: "destructive",
      });
    }
  };

  const handleDownloadVideo = (video: ProfessionalVideo) => {
    if (video.preview_base64) {
      // Create download link for base64 image
      const link = document.createElement('a');
      link.href = `data:image/png;base64,${video.preview_base64}`;
      link.download = `autopro_video_${video.id}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      toast({
        title: "Video descărcat",
        description: "Preview-ul video-ului a fost descărcat cu succes!",
      });
    } else if (video.url) {
      // Fallback to URL download
      window.open(video.url, '_blank');
    }
  };

  const getStatusColor = (status: ProfessionalVideo['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500 text-white';
      case 'generating':
        return 'bg-yellow-500 text-white';
      case 'failed':
        return 'bg-red-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  const getStatusText = (status: ProfessionalVideo['status']) => {
    switch (status) {
      case 'completed':
        return 'Completat';
      case 'generating':
        return 'Se generează';
      case 'failed':
        return 'Eșuat';
      default:
        return 'Necunoscut';
    }
  };

  const filteredVideos = videos.filter(video => {
    const statusMatch = statusFilter === 'all' || video.status === statusFilter;
    const providerMatch = providerFilter === 'all' || video.provider.toLowerCase().includes(providerFilter.toLowerCase());
    const searchMatch = searchQuery === '' || video.title.toLowerCase().includes(searchQuery.toLowerCase());
    return statusMatch && providerMatch && searchMatch;
  });

  // HeyGen functions
  const loadHeyGenAvatars = async () => {
    try {
      const response = await fetch('/api/video/heygen/avatars');
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.avatars) {
          setHeygenAvatars(data.avatars);
          setHeygenKeyAvailable(true);
        }
      } else if (response.status === 400) {
        const errorData = await response.json();
        if (errorData.detail && errorData.detail.includes('HEYGEN_API_KEY')) {
          setHeygenKeyAvailable(false);
        }
      }
    } catch (error) {
      console.error('Failed to load HeyGen avatars:', error);
    }
  };

  const handleGenerateHeyGenVideo = async () => {
    if (!heygenScript.trim()) {
      toast({
        title: "Eroare",
        description: "Te rog completează scriptul pentru video!",
        variant: "destructive",
      });
      return;
    }

    if (heygenScript.length > 1000) {
      toast({
        title: "Script prea lung",
        description: "Scriptul nu poate depăși 1000 de caractere!",
        variant: "destructive",
      });
      return;
    }

    try {
      setHeygenGenerating(true);
      setHeygenProgress('Inițializare generare video...');

      const formData = new FormData();
      formData.append('script', heygenScript);
      formData.append('quality', heygenQuality);
      formData.append('style', heygenStyle);
      formData.append('language', 'ro');
      if (heygenAvatarId) formData.append('avatar_id', heygenAvatarId);
      if (heygenVoiceId) formData.append('voice_id', heygenVoiceId);

      const response = await fetch('/api/video/heygen/generate', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.video_id) {
          toast({
            title: "🎬 Video HeyGen în generare!",
            description: `Video ID: ${data.video_id}. Estimare: ${data.estimated_completion || '2-5 min'}`,
          });

          // Start polling for status
          pollHeyGenStatus(data.video_id);
        } else {
          throw new Error(data.message || 'Failed to start generation');
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Network error');
      }
    } catch (error: any) {
      console.error('Failed to generate HeyGen video:', error);
      toast({
        title: "Eroare generare video",
        description: error.message || "Nu s-a putut porni generarea video-ului HeyGen.",
        variant: "destructive",
      });
      setHeygenGenerating(false);
      setHeygenProgress('');
    }
  };

  const pollHeyGenStatus = async (videoId: string) => {
    const maxAttempts = 60; // 10 minutes (60 x 10s)
    let attempts = 0;

    const interval = setInterval(async () => {
      attempts++;
      
      try {
        const response = await fetch(`/api/video/heygen/status/${videoId}`);
        if (response.ok) {
          const data = await response.json();
          
          if (data.status === 'completed') {
            clearInterval(interval);
            setHeygenGenerating(false);
            setHeygenProgress('');
            
            toast({
              title: "✅ Video HeyGen gata!",
              description: "Video-ul a fost generat cu succes! Se descarcă automat...",
            });

            // Reload videos to show new HeyGen video
            loadVideos();

            // Auto-download if URL available
            if (data.url) {
              window.open(data.url, '_blank');
            }
          } else if (data.status === 'failed' || data.status === 'error') {
            clearInterval(interval);
            setHeygenGenerating(false);
            setHeygenProgress('');
            
            toast({
              title: "Eroare generare",
              description: data.error || "Video-ul nu a putut fi generat.",
              variant: "destructive",
            });
          } else {
            // Still generating
            const progress = data.progress || Math.min((attempts / maxAttempts) * 100, 95);
            setHeygenProgress(`Generare în curs... ${Math.round(progress)}%`);
          }
        }
      } catch (error) {
        console.error('Polling error:', error);
      }

      if (attempts >= maxAttempts) {
        clearInterval(interval);
        setHeygenGenerating(false);
        setHeygenProgress('');
        toast({
          title: "Timeout",
          description: "Generarea durează prea mult. Verifică mai târziu în listă.",
          variant: "destructive",
        });
      }
    }, 10000); // Poll every 10 seconds
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Video Management</h1>
          <p className="text-sm text-gray-500 mt-1">
            Total: {videos.length} | Afișate: {filteredVideos.length}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Search */}
          <Input
            type="text"
            placeholder="Caută video după titlu..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-[220px]"
          />
          
          {/* Filters */}
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toate statusurile</SelectItem>
              <SelectItem value="completed">Completat</SelectItem>
              <SelectItem value="generating">Generare</SelectItem>
              <SelectItem value="failed">Eșuat</SelectItem>
            </SelectContent>
          </Select>

          <Select value={providerFilter} onValueChange={setProviderFilter}>
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Provider" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toți providerii</SelectItem>
              <SelectItem value="heygen">HeyGen</SelectItem>
              <SelectItem value="autopro">AutoPro</SelectItem>
              <SelectItem value="manole">Manole</SelectItem>
            </SelectContent>
          </Select>

          {/* Batch actions */}
          {selectedVideos.size > 0 && (
            <>
              <Badge variant="outline" className="text-base px-3 py-1">
                {selectedVideos.size} selected
              </Badge>
              <Button 
                onClick={selectAllVideos} 
                variant="outline" 
                size="sm"
                disabled={selectedVideos.size === videos.length}
              >
                Select All
              </Button>
              <Button 
                onClick={deselectAllVideos} 
                variant="outline" 
                size="sm"
              >
                Deselect All
              </Button>
              <Button 
                onClick={handleBatchDelete} 
                variant="destructive" 
                size="sm"
                disabled={isDeletingBatch}
              >
                {isDeletingBatch ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete Selected
                  </>
                )}
              </Button>
            </>
          )}
          <Button onClick={loadVideos} variant="outline" disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      <Tabs defaultValue="list" className="w-full">
        <TabsList>
          <TabsTrigger value="list">Lista Video-uri</TabsTrigger>
          <TabsTrigger value="heygen">🎬 HeyGen Video Real</TabsTrigger>
          <TabsTrigger value="generate">Video Profesional AI</TabsTrigger>
          <TabsTrigger value="capabilities">Capacități Sistem</TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="space-y-4">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p>Se încarcă video-urile...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredVideos.length === 0 ? (
                <div className="col-span-full text-center py-8 text-gray-500">
                  <p>
                    {videos.length === 0 
                      ? "Nu există video-uri generate încă." 
                      : "Niciun video nu corespunde filtrelor selectate."}
                  </p>
                  <p className="text-sm mt-2">
                    {videos.length === 0 
                      ? "Folosește tab-ul \"Generează Nou\" pentru a crea primul video." 
                      : "Încearcă să modifici filtrele de mai sus."}
                  </p>
                </div>
              ) : (
                filteredVideos.map((video) => (
                  <Card key={video.id} className="hover:shadow-lg transition-shadow relative">
                    <div className="absolute top-3 left-3 z-10">
                      <input
                        type="checkbox"
                        checked={selectedVideos.has(video.id)}
                        onChange={() => toggleVideoSelection(video.id)}
                        className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                      />
                    </div>
                    <CardHeader>
                      <div className="flex justify-between items-start pl-8">
                        <CardTitle className="text-lg truncate">{video.title}</CardTitle>
                        <Badge className={getStatusColor(video.status)}>
                          {getStatusText(video.status)}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="aspect-video bg-gray-100 rounded mb-4 flex items-center justify-center overflow-hidden">
                        {video.status === 'completed' && (video.preview_base64 || video.url) ? (
                          <div className="relative w-full h-full">
                            <img
                              src={
                                video.thumbnail_base64 
                                  ? `data:image/jpeg;base64,${video.thumbnail_base64}` 
                                  : video.preview_base64 
                                  ? `data:image/png;base64,${video.preview_base64}` 
                                  : video.url
                              }
                              className="w-full h-full rounded object-cover"
                              alt={video.title}
                            />
                            <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center">
                              <Play className="w-12 h-12 text-white" />
                            </div>
                          </div>
                        ) : video.status === 'generating' ? (
                          <div className="flex flex-col items-center">
                            <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mb-2" />
                            <p className="text-sm text-gray-500">Se generează...</p>
                          </div>
                        ) : video.status === 'failed' ? (
                          <div className="flex flex-col items-center text-red-500">
                            <p className="text-sm">Generarea a eșuat</p>
                          </div>
                        ) : (
                          <div className="text-gray-400">
                            <p className="text-sm">Video indisponibil</p>
                          </div>
                        )}
                      </div>

                      <div className="space-y-2 mb-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-500 font-medium">{video.provider}</span>
                          <span className="text-xs text-gray-400">
                            {new Date(video.createdAt).toLocaleDateString('ro-RO')}
                          </span>
                        </div>
                        <div className="flex gap-2">
                          <Badge variant="outline" className="text-xs">
                            <User className="w-3 h-3 mr-1" />
                            {video.avatar_type}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            <Palette className="w-3 h-3 mr-1" />
                            {video.background_type}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            <Monitor className="w-3 h-3 mr-1" />
                            {video.aspect_ratio}
                          </Badge>
                        </div>
                      </div>

                      {video.metrics && (
                        <div className="flex justify-between text-xs text-gray-500 mb-3">
                          <span>{video.metrics.views || 0} vizualizări</span>
                          <span>{video.metrics.likes || 0} like-uri</span>
                          <span>{video.metrics.shares || 0} share-uri</span>
                        </div>
                      )}

                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={video.status !== 'completed'}
                          onClick={() => handlePlayVideo(video)}
                          title="Previzualizează video"
                        >
                          <Play className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={video.status !== 'completed'}
                          onClick={() => handleDownloadVideo(video)}
                          title="Descarcă video"
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDeleteVideo(video.id)}
                          className="ml-auto"
                          title="Șterge video"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          )}
        </TabsContent>

        <TabsContent value="heygen" className="space-y-4">
          {!heygenKeyAvailable && <HeyGenKeyMissingBanner />}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-purple-500" />
                HeyGen - Generare Video REAL cu Avatar Vorbitor
              </CardTitle>
              <p className="text-sm text-gray-600 mt-2">
                Generează video MP4 cu avatar fotorealist care vorbește scriptul tău! Lip-sync perfect, voce naturală română.
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="heygen-script">Script Video (max 1000 caractere)</Label>
                    <Textarea
                      id="heygen-script"
                      value={heygenScript}
                      onChange={(e) => setHeygenScript(e.target.value)}
                      placeholder="Bună ziua! Sunt avocat AutoPro Daune. Vă ajut să obțineți despăgubiri complete pentru daunele auto. Apelați acum!"
                      className="w-full h-32"
                      disabled={heygenGenerating}
                      maxLength={1000}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      {heygenScript.length}/1000 caractere | Avatar va vorbi acest text cu lip-sync perfect
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="heygen-quality">Calitate Video</Label>
                      <Select value={heygenQuality} onValueChange={setHeygenQuality} disabled={heygenGenerating}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low (720p)</SelectItem>
                          <SelectItem value="medium">Medium (1080p)</SelectItem>
                          <SelectItem value="high">High (1080p+)</SelectItem>
                          <SelectItem value="ultra">Ultra (4K)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="heygen-style">Stil Video</Label>
                      <Select value={heygenStyle} onValueChange={setHeygenStyle} disabled={heygenGenerating}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="realistic">Realistic (Recomandat)</SelectItem>
                          <SelectItem value="animated">Animated</SelectItem>
                          <SelectItem value="cartoon">Cartoon</SelectItem>
                          <SelectItem value="documentary">Documentary</SelectItem>
                          <SelectItem value="presentation">Presentation</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="heygen-avatar">Avatar (Opțional)</Label>
                    <Select value={heygenAvatarId} onValueChange={setHeygenAvatarId} disabled={heygenGenerating}>
                      <SelectTrigger>
                        <SelectValue placeholder="Avatar default" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="default">Avatar default HeyGen</SelectItem>
                        {heygenAvatars.map((avatar) => (
                          <SelectItem key={avatar.id} value={avatar.id}>
                            {avatar.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-gray-500 mt-1">
                      Lasă gol pentru avatar default fotorealist
                    </p>
                  </div>

                  <Button
                    onClick={handleGenerateHeyGenVideo}
                    disabled={!heygenKeyAvailable || !heygenScript.trim() || heygenGenerating}
                    className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                    size="lg"
                  >
                    {heygenGenerating ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Generare în curs...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        Generează Video HeyGen REAL
                      </>
                    )}
                  </Button>

                  {heygenProgress && (
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <RefreshCw className="w-4 h-4 text-purple-600 animate-spin" />
                        <p className="text-sm font-medium text-purple-900">{heygenProgress}</p>
                      </div>
                      <p className="text-xs text-purple-700">
                        Video-ul va apărea în listă când va fi gata. Durată estimată: 2-5 minute.
                      </p>
                    </div>
                  )}
                </div>

                <div className="space-y-4">
                  <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-6 border-2 border-purple-200">
                    <h4 className="font-bold text-purple-900 mb-3 flex items-center gap-2">
                      <Sparkles className="w-5 h-5" />
                      Funcționalități HeyGen
                    </h4>
                    <ul className="space-y-2 text-sm text-purple-800">
                      <li className="flex items-start gap-2">
                        <span className="text-purple-600 font-bold">•</span>
                        <span><strong>Avatar fotorealist</strong> - Persoană reală care vorbește</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-purple-600 font-bold">•</span>
                        <span><strong>Lip-sync perfect</strong> - Buzele sincronizate cu textul</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-purple-600 font-bold">•</span>
                        <span><strong>Voce naturală</strong> - Text-to-speech AI românesc</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-purple-600 font-bold">•</span>
                        <span><strong>Video MP4</strong> - Descarcabil și partajabil</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-purple-600 font-bold">•</span>
                        <span><strong>HD/4K quality</strong> - Professional output</span>
                      </li>
                    </ul>
                  </div>

                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <h4 className="font-medium text-blue-900 mb-2">Cost estimat:</h4>
                    <p className="text-sm text-blue-700">
                      • Script 30s: <strong>~$1.60</strong> per video
                      <br />
                      • Script 60s: <strong>~$3.20</strong> per video
                      <br />
                      • Plan Creator: <strong>$24/lună</strong> (15 min video)
                    </p>
                  </div>

                  <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                    <h4 className="font-medium text-green-900 mb-2">Status API:</h4>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <p className="text-sm text-green-700">
                        <strong>API Key configurată</strong> - Ready to generate!
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="generate" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-blue-500" />
                  Generator Video AI Profesional
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="video-text">Textul pentru Video</Label>
                  <Textarea
                    id="video-text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="AutoPro Daune - Experții tăi în daune auto. Rezolvăm rapid și eficient!"
                    className="w-full h-20"
                    disabled={generating}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Textul care va fi afișat în video cu avatarul profesional
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="avatar-select">Avatar Profesional</Label>
                    <Select value={selectedAvatar} onValueChange={setSelectedAvatar}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="professional">Alexandra - Business Professional</SelectItem>
                        <SelectItem value="casual">Maria - Friendly Advisor</SelectItem>
                        <SelectItem value="friendly">Elena - Customer Care</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="background-select">Fundal</Label>
                    <Select value={selectedBackground} onValueChange={setSelectedBackground}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="office">Birou Modern</SelectItem>
                        <SelectItem value="modern">Tech Modern</SelectItem>
                        <SelectItem value="gradient">AutoPro Gradient</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="aspect-ratio">Format Video</Label>
                    <Select value={aspectRatio} onValueChange={setAspectRatio}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="portrait">Portrait (9:16) - Social Media</SelectItem>
                        <SelectItem value="landscape">Landscape (16:9) - Desktop</SelectItem>
                        <SelectItem value="square">Pătrat (1:1) - Instagram</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="resolution">Rezoluție</Label>
                    <Select value={resolution} onValueChange={setResolution}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="720p">720p (HD)</SelectItem>
                        <SelectItem value="1080p">1080p (Full HD)</SelectItem>
                        <SelectItem value="4k">4K (Ultra HD)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <Button
                  onClick={handleGenerateVideo}
                  disabled={!prompt.trim() || generating}
                  className="w-full"
                  size="lg"
                >
                  <Video className="w-4 h-4 mr-2" />
                  {generating ? 'Se generează video profesional...' : 'Generează Video AI Profesional'}
                </Button>

                {generating && (
                  <div className="text-center py-4">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3"></div>
                    <p className="text-sm text-gray-600 mb-2">
                      Se generează video-ul cu avatar profesional...
                    </p>
                    <div className="bg-blue-50 rounded p-3">
                      <p className="text-xs text-blue-600">
                        Avatar: {selectedAvatar} | Fundal: {selectedBackground} | Format: {aspectRatio}
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Preview Configurație</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="bg-gray-100 rounded-lg p-4 aspect-video flex items-center justify-center">
                    <div className="text-center">
                      <Video className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                      <p className="text-sm text-gray-500">Preview video va apărea aici</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {aspectRatio} @ {resolution}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Avatar:</span>
                      <Badge variant="outline">
                        <User className="w-3 h-3 mr-1" />
                        {selectedAvatar}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Fundal:</span>
                      <Badge variant="outline">
                        <Palette className="w-3 h-3 mr-1" />
                        {selectedBackground}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Format:</span>
                      <Badge variant="outline">
                        <Monitor className="w-3 h-3 mr-1" />
                        {aspectRatio}
                      </Badge>
                    </div>
                  </div>

                  <div className="bg-blue-50 p-3 rounded-lg">
                    <h4 className="font-medium text-blue-800 mb-2">Funcționalități Avansate:</h4>
                    <ul className="text-sm text-blue-700 space-y-1">
                      <li>• Avatar AI cu lip sync indicators</li>
                      <li>• Layout profesional cu branding AutoPro</li>
                      <li>• Text overlay cu font professional</li>
                      <li>• Aspect ratio optimizat pentru social media</li>
                      <li>• Preview instant în base64 pentru download rapid</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="capabilities" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">System Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Advanced Video API</span>
                    <Badge variant={videoCapabilities?.status === 'Advanced professional video generation ready' ? 'default' : 'secondary'}>
                      {videoCapabilities?.status ? 'Online' : 'Offline'}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Libraries Available</span>
                    <Badge variant={videoCapabilities?.libraries_available ? 'default' : 'destructive'}>
                      {videoCapabilities?.libraries_available ? 'Yes' : 'No'}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Professional Avatars</span>
                    <Badge variant="outline">
                      {videoCapabilities?.capabilities?.professional_avatars || 3}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Background Styles</span>
                    <Badge variant="outline">
                      {videoCapabilities?.capabilities?.background_styles || 3}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Avatars Disponibili</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {videoCapabilities?.avatar_database ? Object.entries(videoCapabilities.avatar_database).map(([key, value]) => (
                    <div key={key} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                      <User className="w-4 h-4 text-blue-500" />
                      <div>
                        <p className="text-sm font-medium capitalize">{key}</p>
                        <p className="text-xs text-gray-500">{value as string}</p>
                      </div>
                    </div>
                  )) : (
                    <p className="text-sm text-gray-500">Loading avatars...</p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Backgrounds Disponibile</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {videoCapabilities?.background_database ? Object.entries(videoCapabilities.background_database).map(([key, value]) => (
                    <div key={key} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                      <Palette className="w-4 h-4 text-green-500" />
                      <div>
                        <p className="text-sm font-medium capitalize">{key}</p>
                        <p className="text-xs text-gray-500">{value as string}</p>
                      </div>
                    </div>
                  )) : (
                    <p className="text-sm text-gray-500">Loading backgrounds...</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {videoCapabilities?.capabilities?.features && (
            <Card>
              <CardHeader>
                <CardTitle>Funcționalități Avansate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {videoCapabilities.capabilities.features.map((feature: string, index: number) => (
                    <div key={index} className="flex items-start gap-2 p-3 bg-green-50 rounded-lg">
                      <Sparkles className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-green-700">{feature}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Video Preview Modal */}
      <Dialog open={showPreviewModal} onOpenChange={setShowPreviewModal}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Play className="w-5 h-5 text-blue-500" />
              {previewVideo?.title || 'Preview Video'}
            </DialogTitle>
            <DialogDescription>
              Video generat cu avatar {previewVideo?.avatar_type} și fundal {previewVideo?.background_type}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {previewVideo && (
              <>
                <div className="bg-gray-100 rounded-lg overflow-hidden">
                  {previewVideo.url && (previewVideo.url.endsWith('.mp4') || previewVideo.url.endsWith('.webm') || previewVideo.provider === 'HeyGen') ? (
                    <video
                      src={previewVideo.url}
                      className="w-full h-auto"
                      controls
                      autoPlay
                      loop
                      playsInline
                    >
                      <source src={previewVideo.url} type="video/mp4" />
                      Browser-ul tău nu suportă video HTML5.
                    </video>
                  ) : previewVideo.preview_base64 ? (
                    <img
                      src={`data:image/png;base64,${previewVideo.preview_base64}`}
                      alt={previewVideo.title}
                      className="w-full h-auto"
                    />
                  ) : previewVideo.url ? (
                    <img
                      src={previewVideo.url}
                      alt={previewVideo.title}
                      className="w-full h-auto"
                    />
                  ) : (
                    <div className="aspect-video flex items-center justify-center text-gray-400">
                      <Video className="w-16 h-16" />
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-600">Provider:</span>
                    <p className="text-gray-900">{previewVideo.provider}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Status:</span>
                    <Badge className={getStatusColor(previewVideo.status)}>
                      {getStatusText(previewVideo.status)}
                    </Badge>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Avatar:</span>
                    <p className="text-gray-900">{previewVideo.avatar_type}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Background:</span>
                    <p className="text-gray-900">{previewVideo.background_type}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Aspect Ratio:</span>
                    <p className="text-gray-900">{previewVideo.aspect_ratio}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Created:</span>
                    <p className="text-gray-900">
                      {new Date(previewVideo.createdAt).toLocaleString('ro-RO')}
                    </p>
                  </div>
                </div>

                <div className="flex gap-2 justify-end pt-4 border-t">
                  <Button
                    variant="outline"
                    onClick={() => handleDownloadVideo(previewVideo)}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Descarcă
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={() => {
                      handleDeleteVideo(previewVideo.id);
                      setShowPreviewModal(false);
                    }}
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Șterge
                  </Button>
                  <Button onClick={() => setShowPreviewModal(false)}>
                    Închide
                  </Button>
                </div>
              </>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default VideoManagement;