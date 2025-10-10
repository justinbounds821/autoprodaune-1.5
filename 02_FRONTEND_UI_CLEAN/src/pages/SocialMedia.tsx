import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Share2, TrendingUp, MessageSquare, Heart, Calendar, Plus, RefreshCw, BarChart3, Send } from 'lucide-react';
import AutoProApiService from '@/services/autoproApi';
import { SocialPost, PostData, Analytics } from '@/types/admin';
import { useToast } from '@/hooks/use-toast';

interface FollowerStats {
  platform: string;
  followers: number;
  growth_rate: number;
  engagement_rate: number;
  last_updated: string;
}

const SocialMedia: React.FC = () => {
  const { toast } = useToast();
  const [posts, setPosts] = useState<SocialPost[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [followerStats, setFollowerStats] = useState<FollowerStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [posting, setPosting] = useState(false);
  const [loadingFollowers, setLoadingFollowers] = useState(false);

  // Create post form state
  const [newPost, setNewPost] = useState<PostData>({
    content: '',
    platform: 'TikTok'
  });

  // Schedule post form state
  const [scheduledPost, setScheduledPost] = useState<PostData>({
    content: '',
    platform: 'TikTok',
    scheduledFor: ''
  });

  // Video upload state
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoCaption, setVideoCaption] = useState('');
  const [videoHashtags, setVideoHashtags] = useState('#AutoProDaune #DespagubirAuto #AsistentaAuto');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['tiktok']);
  const [uploadingVideo, setUploadingVideo] = useState(false);
  const [scheduleDate, setScheduleDate] = useState('');

  useEffect(() => {
    loadPosts();
    loadAnalytics();
    loadFollowerStats();
  }, []);

  const loadPosts = async () => {
    try {
      setLoading(true);
      const response = await AutoProApiService.getSocialPosts();

      if (response.posts || response.data || Array.isArray(response)) {
        setPosts(response.posts || response.data || response);
      } else {
        console.error('Failed to load posts:', response.error);
        toast({
          title: "Eroare",
          description: "Nu s-au putut încărca postările.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Failed to load posts:', error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca postările.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await AutoProApiService.getPostAnalytics();

      if (response.analytics || response.data || response.total_engagement !== undefined) {
        setAnalytics(response.analytics || response.data || response);
      } else {
        console.error('Failed to load analytics:', response.error);
      }
    } catch (error) {
      console.error('Failed to load analytics:', error);
    }
  };

  const loadFollowerStats = async () => {
    try {
      setLoadingFollowers(true);
      const response = await fetch('/api/social/followers');
      
      if (response.ok) {
        const data = await response.json();
        if (data.followers || data.total !== undefined || Array.isArray(data)) {
          setFollowerStats(data.followers || data);
        }
      } else {
        console.error('Failed to load follower stats');
      }
    } catch (error) {
      console.error('Failed to load follower stats:', error);
    } finally {
      setLoadingFollowers(false);
    }
  };

  const handleVideoFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate video file
      const validTypes = ['video/mp4', 'video/webm', 'video/quicktime'];
      if (!validTypes.includes(file.type)) {
        toast({
          title: "Fișier invalid",
          description: "Doar fișiere MP4, WebM sau MOV sunt acceptate.",
          variant: "destructive",
        });
        return;
      }
      
      // Check file size (max 500MB)
      if (file.size > 500 * 1024 * 1024) {
        toast({
          title: "Fișier prea mare",
          description: "Video-ul nu poate depăși 500MB.",
          variant: "destructive",
        });
        return;
      }
      
      setVideoFile(file);
      toast({
        title: "Video încărcat",
        description: `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`,
      });
    }
  };

  const togglePlatform = (platform: string) => {
    setSelectedPlatforms(prev => 
      prev.includes(platform)
        ? prev.filter(p => p !== platform)
        : [...prev, platform]
    );
  };

  const handleUploadVideo = async () => {
    if (!videoFile || !videoCaption.trim()) {
      toast({
        title: "Date incomplete",
        description: "Selectează un video și adaugă o descriere.",
        variant: "destructive",
      });
      return;
    }

    if (selectedPlatforms.length === 0) {
      toast({
        title: "Platformă nespecificată",
        description: "Selectează cel puțin o platformă pentru postare.",
        variant: "destructive",
      });
      return;
    }

    try {
      setUploadingVideo(true);

      const formData = new FormData();
      formData.append('video', videoFile);
      formData.append('caption', videoCaption + ' ' + videoHashtags);
      formData.append('platforms', JSON.stringify(selectedPlatforms));
      if (scheduleDate) {
        formData.append('scheduled_for', scheduleDate);
      }

      const response = await fetch('/api/social/upload-video', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        
        toast({
          title: "✅ Video postat cu succes!",
          description: `Postat pe: ${selectedPlatforms.join(', ')}`,
        });

        // Reset form
        setVideoFile(null);
        setVideoCaption('');
        setScheduleDate('');
        
        // Reload posts
        await loadPosts();
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Video upload error:', error);
      toast({
        title: "Eroare la postare",
        description: "Video-ul nu a putut fi postat. Verifică conexiunea.",
        variant: "destructive",
      });
    } finally {
      setUploadingVideo(false);
    }
  };

  const handleCreatePost = async () => {
    if (!newPost.content.trim()) return;

    try {
      setPosting(true);
      const response = await AutoProApiService.createPost(newPost);

      if (response.post || response.id || response.data) {
        const postData = response.post || response.data || response;
        setPosts(prev => [postData, ...prev]);
        setNewPost({ content: '', platform: 'TikTok' });
        toast({
          title: "Post creat",
          description: "Postarea a fost creată cu succes!",
        });
      } else {
        throw new Error(response.error || 'Failed to create post');
      }
    } catch (error) {
      console.error('Failed to create post:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut crea postarea.",
        variant: "destructive",
      });
    } finally {
      setPosting(false);
    }
  };

  const handleSchedulePost = async () => {
    if (!scheduledPost.content.trim() || !scheduledPost.scheduledFor) return;

    try {
      setPosting(true);
      const response = await AutoProApiService.schedulePost(scheduledPost);

      if (response.post || response.id || response.data || response.scheduled) {
        const postData = response.post || response.data || response;
        setPosts(prev => [postData, ...prev]);
        setScheduledPost({ content: '', platform: 'TikTok', scheduledFor: '' });
        toast({
          title: "Post programat",
          description: "Postarea a fost programată cu succes!",
        });
      } else {
        throw new Error(response.error || 'Failed to schedule post');
      }
    } catch (error) {
      console.error('Failed to schedule post:', error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut programa postarea.",
        variant: "destructive",
      });
    } finally {
      setPosting(false);
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'tiktok':
        return '🎵';
      case 'instagram':
        return '📸';
      case 'facebook':
        return '👥';
      default:
        return '📱';
    }
  };

  const getStatusColor = (status: SocialPost['status']) => {
    switch (status) {
      case 'posted':
        return 'bg-green-500 text-white';
      case 'scheduled':
        return 'bg-blue-500 text-white';
      case 'failed':
        return 'bg-red-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  const getStatusText = (status: SocialPost['status']) => {
    switch (status) {
      case 'posted':
        return 'Postat';
      case 'scheduled':
        return 'Programat';
      case 'failed':
        return 'Eșuat';
      default:
        return 'Necunoscut';
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('ro-RO', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Social Media Management</h1>
        <Button onClick={loadPosts} variant="outline" disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Follower Stats Cards */}
      {followerStats.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {followerStats.map((stat) => (
            <Card key={stat.platform}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.platform}</CardTitle>
                <span className="text-2xl">{getPlatformIcon(stat.platform)}</span>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.followers.toLocaleString('ro-RO')}</div>
                <p className="text-xs text-muted-foreground">urmăritori</p>
                <div className="flex items-center gap-4 mt-2 text-xs">
                  <div className={`flex items-center gap-1 ${stat.growth_rate >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    <TrendingUp className="w-3 h-3" />
                    <span>{stat.growth_rate >= 0 ? '+' : ''}{stat.growth_rate}%</span>
                  </div>
                  <div className="text-muted-foreground">
                    Engagement: {stat.engagement_rate}%
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Tabs defaultValue="posts" className="w-full">
        <TabsList>
          <TabsTrigger value="posts">Postări Recente</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="upload">🎬 Upload Video</TabsTrigger>
          <TabsTrigger value="create">Creează Post</TabsTrigger>
          <TabsTrigger value="schedule">Programează</TabsTrigger>
        </TabsList>

        <TabsContent value="posts" className="space-y-4">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p>Se încarcă postările...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {posts.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Share2 className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Nu există postări încă.</p>
                  <p className="text-sm mt-2">Creează prima postare folosind tab-ul "Creează Post".</p>
                </div>
              ) : (
                posts.map((post) => (
                  <Card key={post.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl">{getPlatformIcon(post.platform)}</span>
                          <div>
                            <span className="font-medium capitalize">{post.platform}</span>
                            <div className="text-sm text-gray-500">
                              {formatDate(post.createdAt)}
                            </div>
                          </div>
                        </div>
                        <Badge className={getStatusColor(post.status)}>
                          {getStatusText(post.status)}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-700 mb-4 line-clamp-3">{post.content}</p>

                      {post.status === 'posted' && post.engagement && (
                        <div className="flex items-center gap-6 text-sm text-gray-500 pt-3 border-t">
                          <div className="flex items-center gap-1">
                            <Heart className="w-4 h-4" />
                            <span>{post.engagement.likes || 0}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <MessageSquare className="w-4 h-4" />
                            <span>{post.engagement.comments || 0}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Share2 className="w-4 h-4" />
                            <span>{post.engagement.shares || 0}</span>
                          </div>
                          {post.engagement.views && (
                            <div className="flex items-center gap-1">
                              <span className="text-xs">👁️</span>
                              <span>{post.engagement.views}</span>
                            </div>
                          )}
                        </div>
                      )}

                      {post.status === 'failed' && (
                        <div className="mt-3 p-2 bg-red-50 rounded text-sm text-red-600">
                          Postarea a eșuat. Încearcă din nou sau verifică configurările platformei.
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          )}
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Total Postări</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analytics?.totalPosts || posts.length}</div>
                <p className="text-xs text-gray-500">Toate platformele</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Engagement Mediu</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analytics?.averageEngagement || 0}</div>
                <p className="text-xs text-gray-500">Pe postare</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Rată de Creștere</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  +{analytics?.growthRate || 0}%
                </div>
                <p className="text-xs text-gray-500">Această lună</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Analytics pe Platformă
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {['TikTok', 'Instagram', 'Facebook'].map((platform) => {
                  const platformPosts = posts.filter(p => p.platform === platform);
                  const totalEngagement = platformPosts.reduce((sum, post) => {
                    return sum + (post.engagement?.likes || 0) + (post.engagement?.comments || 0) + (post.engagement?.shares || 0);
                  }, 0);

                  return (
                    <div key={platform} className="flex items-center justify-between p-3 border rounded">
                      <div className="flex items-center gap-2">
                        <span className="text-xl">{getPlatformIcon(platform)}</span>
                        <span className="font-medium">{platform}</span>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <span>{platformPosts.length} postări</span>
                        <span>{totalEngagement} engagement</span>
                        <Badge variant="outline">
                          {platformPosts.filter(p => p.status === 'posted').length} active
                        </Badge>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="upload" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                🎬 Upload Video pe Social Media
              </CardTitle>
              <p className="text-sm text-muted-foreground mt-2">
                Încarcă video-uri generate (HeyGen, Manole) direct pe platformele social media
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Video File Upload */}
              <div>
                <label className="block text-sm font-medium mb-2">Video File</label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors">
                  <input
                    type="file"
                    accept="video/mp4,video/webm,video/quicktime"
                    onChange={handleVideoFileChange}
                    className="hidden"
                    id="video-upload"
                  />
                  <label htmlFor="video-upload" className="cursor-pointer">
                    <div className="flex flex-col items-center">
                      <Plus className="w-12 h-12 text-gray-400 mb-2" />
                      <p className="text-sm font-medium text-gray-700">
                        Click pentru a selecta video
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        MP4, WebM sau MOV (max 500MB)
                      </p>
                    </div>
                  </label>
                </div>
                {videoFile && (
                  <div className="mt-2 p-3 bg-green-50 rounded-lg flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-green-600">✓</span>
                      <span className="text-sm font-medium">{videoFile.name}</span>
                      <span className="text-xs text-gray-500">
                        ({(videoFile.size / 1024 / 1024).toFixed(2)} MB)
                      </span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setVideoFile(null)}
                    >
                      ✕
                    </Button>
                  </div>
                )}
              </div>

              {/* Caption */}
              <div>
                <label className="block text-sm font-medium mb-2">Descriere Video</label>
                <Textarea
                  value={videoCaption}
                  onChange={(e) => setVideoCaption(e.target.value)}
                  placeholder="Ex: Află cum să obții despăgubiri complete după un accident auto! 🚗💰 Procesul nostru simplu te ajută să recuperezi toate daunele rapid și eficient."
                  className="min-h-[100px]"
                  disabled={uploadingVideo}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {videoCaption.length} caractere
                </p>
              </div>

              {/* Hashtags */}
              <div>
                <label className="block text-sm font-medium mb-2">Hashtag-uri</label>
                <Input
                  value={videoHashtags}
                  onChange={(e) => setVideoHashtags(e.target.value)}
                  placeholder="#AutoProDaune #DespagubirAuto"
                  disabled={uploadingVideo}
                />
              </div>

              {/* Platform Selection */}
              <div>
                <label className="block text-sm font-medium mb-2">Platforme (selectează multiple)</label>
                <div className="grid grid-cols-3 gap-3">
                  <Button
                    type="button"
                    variant={selectedPlatforms.includes('tiktok') ? 'default' : 'outline'}
                    onClick={() => togglePlatform('tiktok')}
                    className="flex items-center gap-2"
                  >
                    🎵 TikTok
                    {selectedPlatforms.includes('tiktok') && <span>✓</span>}
                  </Button>
                  <Button
                    type="button"
                    variant={selectedPlatforms.includes('instagram') ? 'default' : 'outline'}
                    onClick={() => togglePlatform('instagram')}
                    className="flex items-center gap-2"
                    disabled
                    title="Instagram API blocked"
                  >
                    📸 Instagram
                    <span className="text-xs">(blocked)</span>
                  </Button>
                  <Button
                    type="button"
                    variant={selectedPlatforms.includes('youtube') ? 'default' : 'outline'}
                    onClick={() => togglePlatform('youtube')}
                    className="flex items-center gap-2"
                  >
                    ▶️ YouTube
                    {selectedPlatforms.includes('youtube') && <span>✓</span>}
                  </Button>
                </div>
              </div>

              {/* Schedule Date (Optional) */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Data Programată (opțional)
                </label>
                <Input
                  type="datetime-local"
                  value={scheduleDate}
                  onChange={(e) => setScheduleDate(e.target.value)}
                  min={new Date().toISOString().slice(0, 16)}
                  disabled={uploadingVideo}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Lasă gol pentru postare imediată
                </p>
              </div>

              {/* Info Box */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">ℹ️ Informații Importante:</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• TikTok: Video-uri între 15s-10min, format vertical (9:16) recomandat</li>
                  <li>• YouTube: Orice durată, format landscape (16:9) recomandat</li>
                  <li>• Video-urile generate cu HeyGen sunt perfect optimizate!</li>
                  <li>• Hashtag-urile cresc vizibilitatea cu până la 300%</li>
                </ul>
              </div>

              {/* Upload Button */}
              <Button
                onClick={handleUploadVideo}
                disabled={uploadingVideo || !videoFile || !videoCaption.trim()}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                size="lg"
              >
                {uploadingVideo ? (
                  <>
                    <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                    Se încarcă pe {selectedPlatforms.join(', ')}...
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5 mr-2" />
                    {scheduleDate ? 'Programează Video' : 'Postează Video Acum'}
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="create" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Creează Post Nou</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Platformă</label>
                <Select
                  value={newPost.platform}
                  onValueChange={(value: 'TikTok' | 'Instagram' | 'Facebook') =>
                    setNewPost(prev => ({ ...prev, platform: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="TikTok">🎵 TikTok</SelectItem>
                    <SelectItem value="Instagram">📸 Instagram</SelectItem>
                    <SelectItem value="Facebook">👥 Facebook</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Conținut</label>
                <Textarea
                  value={newPost.content}
                  onChange={(e) => setNewPost(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Scrie conținutul postării aici... (ex: 'Știai că în România ai dreptul la despăgubiri complete după un accident auto? Iată ce trebuie să știi...')"
                  className="min-h-[120px]"
                  disabled={posting}
                />
                <div className="flex justify-between items-center mt-1">
                  <p className="text-xs text-gray-500">
                    Caracteristici: {newPost.content.length}/280
                  </p>
                  {newPost.content.length > 280 && (
                    <p className="text-xs text-red-500">
                      Prea lung pentru unele platforme
                    </p>
                  )}
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-800 mb-2">Sfaturi pentru postări eficiente:</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Include întrebări pentru a stimula interacțiunea</li>
                  <li>• Folosește hashtag-uri relevante (#daune #asigurari #avocat)</li>
                  <li>• Împărtășește sfaturi practice și utile</li>
                  <li>• Menționează beneficiile serviciilor tale</li>
                </ul>
              </div>

              <Button
                onClick={handleCreatePost}
                disabled={!newPost.content.trim() || posting}
                className="w-full"
              >
                <Send className="w-4 h-4 mr-2" />
                {posting ? 'Se postează...' : 'Postează Acum'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="schedule" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Programează Post
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Platformă</label>
                <Select
                  value={scheduledPost.platform}
                  onValueChange={(value: 'TikTok' | 'Instagram' | 'Facebook') =>
                    setScheduledPost(prev => ({ ...prev, platform: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="TikTok">🎵 TikTok</SelectItem>
                    <SelectItem value="Instagram">📸 Instagram</SelectItem>
                    <SelectItem value="Facebook">👥 Facebook</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Data și Ora</label>
                <Input
                  type="datetime-local"
                  value={scheduledPost.scheduledFor}
                  onChange={(e) => setScheduledPost(prev => ({ ...prev, scheduledFor: e.target.value }))}
                  min={new Date().toISOString().slice(0, 16)}
                  disabled={posting}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Conținut</label>
                <Textarea
                  value={scheduledPost.content}
                  onChange={(e) => setScheduledPost(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Scrie conținutul postării programate..."
                  className="min-h-[120px]"
                  disabled={posting}
                />
              </div>

              <Button
                onClick={handleSchedulePost}
                disabled={!scheduledPost.content.trim() || !scheduledPost.scheduledFor || posting}
                className="w-full"
              >
                <Calendar className="w-4 h-4 mr-2" />
                {posting ? 'Se programează...' : 'Programează Post'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SocialMedia;