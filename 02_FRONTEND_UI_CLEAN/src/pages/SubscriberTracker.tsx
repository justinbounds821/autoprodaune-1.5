import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Video, 
  RefreshCw,
  Youtube,
  Instagram,
  AlertCircle
} from 'lucide-react';

interface PlatformMetrics {
  platform: string;
  follower_count?: number;
  subscriber_count?: number;
  following_count?: number;
  video_count?: number;
  media_count?: number;
  likes_count?: number;
  view_count?: number;
  username?: string;
  display_name?: string;
  channel_title?: string;
  error?: string;
  timestamp: string;
}

interface FollowerData {
  success: boolean;
  platforms: {
    tiktok: PlatformMetrics;
    instagram: PlatformMetrics;
    youtube: PlatformMetrics;
  };
  totals: {
    total_followers: number;
    total_content: number;
  };
  timestamp: string;
}

export default function SubscriberTracker() {
  const [data, setData] = useState<FollowerData | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const { toast } = useToast();

  const fetchFollowers = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/social/followers');
      
      if (!response.ok) {
        throw new Error('Failed to fetch follower data');
      }

      const result = await response.json();
      setData(result);
      setLastUpdate(new Date().toLocaleString('ro-RO'));
      
      toast({
        title: 'Date actualizate! 📊',
        description: `Total: ${result.totals.total_followers.toLocaleString()} urmăritori`,
      });

    } catch (error: any) {
      console.error('Error fetching followers:', error);
      toast({
        title: 'Eroare',
        description: error.message || 'Nu s-au putut încărca datele',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFollowers();
  }, []);

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'tiktok':
        return <Video className="w-5 h-5" />;
      case 'instagram':
        return <Instagram className="w-5 h-5" />;
      case 'youtube':
        return <Youtube className="w-5 h-5" />;
      default:
        return <Users className="w-5 h-5" />;
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'tiktok':
        return 'bg-black text-white';
      case 'instagram':
        return 'bg-gradient-to-r from-purple-500 to-pink-500 text-white';
      case 'youtube':
        return 'bg-red-600 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const renderPlatformCard = (platform: string, metrics: PlatformMetrics) => {
    const followerCount = metrics.follower_count || metrics.subscriber_count || 0;
    const contentCount = metrics.video_count || metrics.media_count || 0;
    const displayName = metrics.username || metrics.display_name || metrics.channel_title || 'N/A';

    const hasError = !!metrics.error;

    return (
      <Card key={platform} className={hasError ? 'border-red-200' : ''}>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`p-2 rounded-lg ${getPlatformColor(platform)}`}>
                {getPlatformIcon(platform)}
              </div>
              <span className="capitalize">{platform}</span>
            </div>
            {hasError && (
              <Badge variant="destructive" className="text-xs">
                <AlertCircle className="w-3 h-3 mr-1" />
                Error
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {hasError ? (
            <div className="text-sm text-red-600">
              {metrics.error}
            </div>
          ) : (
            <>
              {/* Account Name */}
              <div className="text-sm text-muted-foreground">
                @{displayName}
              </div>

              {/* Followers */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    {platform === 'youtube' ? 'Subscribers' : 'Followers'}
                  </span>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-green-500" />
                    <span className="text-2xl font-bold">
                      {formatNumber(followerCount)}
                    </span>
                  </div>
                </div>
                <div className="text-xs text-muted-foreground">
                  {followerCount.toLocaleString()} urmăritori
                </div>
              </div>

              {/* Content Count */}
              <div className="flex items-center justify-between pt-2 border-t">
                <span className="text-sm text-muted-foreground">
                  {platform === 'instagram' ? 'Posts' : 'Videos'}
                </span>
                <span className="font-semibold">
                  {contentCount.toLocaleString()}
                </span>
              </div>

              {/* Additional Metrics */}
              {metrics.following_count !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Following</span>
                  <span className="text-sm">
                    {metrics.following_count.toLocaleString()}
                  </span>
                </div>
              )}

              {metrics.likes_count !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Total Likes</span>
                  <span className="text-sm">
                    {formatNumber(metrics.likes_count)}
                  </span>
                </div>
              )}

              {metrics.view_count !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Total Views</span>
                  <span className="text-sm">
                    {formatNumber(metrics.view_count)}
                  </span>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Subscriber Tracker</h2>
          <p className="text-muted-foreground">
            Monitorizează urmăritorii din toate platformele
          </p>
        </div>
        <Button 
          onClick={fetchFollowers} 
          disabled={loading}
          className="flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Last Update */}
      {lastUpdate && (
        <div className="text-sm text-muted-foreground">
          Ultima actualizare: {lastUpdate}
        </div>
      )}

      {/* Total Stats */}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-6 h-6" />
                Total Followers
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">
                {formatNumber(data.totals.total_followers)}
              </div>
              <div className="text-sm opacity-90 mt-1">
                {data.totals.total_followers.toLocaleString()} urmăritori
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-green-500 to-teal-600 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Video className="w-6 h-6" />
                Total Content
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">
                {data.totals.total_content}
              </div>
              <div className="text-sm opacity-90 mt-1">
                video-uri & postări
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Platform Cards */}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {renderPlatformCard('tiktok', data.platforms.tiktok)}
          {renderPlatformCard('instagram', data.platforms.instagram)}
          {renderPlatformCard('youtube', data.platforms.youtube)}
        </div>
      )}

      {/* Loading State */}
      {loading && !data && (
        <div className="flex items-center justify-center h-64">
          <div className="text-center space-y-4">
            <RefreshCw className="w-12 h-12 animate-spin text-blue-500 mx-auto" />
            <p className="text-muted-foreground">Se încarcă datele...</p>
          </div>
        </div>
      )}

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">ℹ️ Cum funcționează?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>
            <strong>Actualizare automată:</strong> Datele se actualizează automat la încărcarea paginii.
          </p>
          <p>
            <strong>Refresh manual:</strong> Apasă butonul "Refresh" pentru a actualiza datele.
          </p>
          <p>
            <strong>API Keys:</strong> Asigură-te că ai configurat API keys pentru TikTok, Instagram și YouTube în `.env`.
          </p>
          <p className="mt-4 pt-4 border-t">
            <strong>Platforme suportate:</strong>
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li><strong>TikTok:</strong> Followers, Videos, Likes</li>
            <li><strong>Instagram:</strong> Followers, Posts, Following</li>
            <li><strong>YouTube:</strong> Subscribers, Videos, Total Views</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
