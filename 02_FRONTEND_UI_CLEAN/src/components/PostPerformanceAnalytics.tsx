import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, Heart, MessageSquare, Share2, Eye, BarChart3 } from 'lucide-react';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { Bar, BarChart, Line, LineChart, ResponsiveContainer, XAxis, YAxis } from 'recharts';

interface PostMetrics {
  id: string;
  content: string;
  platform: string;
  likes: number;
  comments: number;
  shares: number;
  views: number;
  engagement_rate: number;
  createdAt: string;
}

interface PostPerformanceAnalyticsProps {
  posts: PostMetrics[];
}

export default function PostPerformanceAnalytics({ posts }: PostPerformanceAnalyticsProps) {
  const [topPosts, setTopPosts] = useState<PostMetrics[]>([]);
  const [platformStats, setPlatformStats] = useState<any[]>([]);
  const [engagementTrend, setEngagementTrend] = useState<any[]>([]);

  useEffect(() => {
    analyzePerformance();
  }, [posts]);

  const analyzePerformance = () => {
    if (!posts || posts.length === 0) return;

    // Top performing posts
    const sorted = [...posts]
      .sort((a, b) => b.engagement_rate - a.engagement_rate)
      .slice(0, 5);
    setTopPosts(sorted);

    // Platform statistics
    const platforms = ['TikTok', 'Instagram', 'Facebook'];
    const stats = platforms.map(platform => {
      const platformPosts = posts.filter(p => p.platform === platform);
      const totalEngagement = platformPosts.reduce((sum, p) => 
        sum + p.likes + p.comments + p.shares, 0
      );
      const avgEngagement = platformPosts.length > 0 
        ? totalEngagement / platformPosts.length 
        : 0;

      return {
        platform,
        posts: platformPosts.length,
        engagement: Math.round(avgEngagement),
        views: platformPosts.reduce((sum, p) => sum + p.views, 0)
      };
    });
    setPlatformStats(stats);

    // Engagement trend (last 7 days)
    const trend = posts
      .slice(-7)
      .map(post => ({
        date: new Date(post.createdAt).toLocaleDateString('ro-RO', { 
          month: 'short', 
          day: 'numeric' 
        }),
        engagement: post.likes + post.comments + post.shares,
        views: post.views
      }));
    setEngagementTrend(trend);
  };

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'TikTok': return 'bg-pink-500';
      case 'Instagram': return 'bg-purple-500';
      case 'Facebook': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getTrend = (current: number, previous: number) => {
    if (previous === 0) return 0;
    return ((current - previous) / previous * 100).toFixed(1);
  };

  return (
    <div className="space-y-6">
      {/* Platform Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {platformStats.map(stat => (
          <Card key={stat.platform}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${getPlatformColor(stat.platform)}`} />
                  <h3 className="font-semibold">{stat.platform}</h3>
                </div>
                <Badge variant="outline">{stat.posts} posts</Badge>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Avg Engagement</span>
                  <span className="font-bold">{stat.engagement}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Views</span>
                  <span className="font-bold">{stat.views.toLocaleString()}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Engagement Trend Chart */}
      {engagementTrend.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Engagement Trend (Ultimele 7 zile)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={{
              engagement: {
                label: "Engagement",
                color: "hsl(var(--chart-1))",
              },
            }} className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={engagementTrend}>
                  <XAxis 
                    dataKey="date" 
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis hide />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Line 
                    type="monotone" 
                    dataKey="engagement" 
                    stroke="var(--color-engagement)"
                    strokeWidth={2}
                    dot={{ fill: "var(--color-engagement)", strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>
      )}

      {/* Top Performing Posts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Top 5 Postări Performante
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {topPosts.length > 0 ? (
              topPosts.map((post, index) => (
                <div
                  key={post.id}
                  className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge className={getPlatformColor(post.platform)}>
                          {post.platform}
                        </Badge>
                        <span className="text-xs text-gray-500">
                          {new Date(post.createdAt).toLocaleDateString('ro-RO')}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {post.content}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">
                        {post.engagement_rate.toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-500">engagement</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-4 gap-2 mt-3 pt-3 border-t">
                    <div className="flex items-center gap-1 text-xs">
                      <Eye className="w-3 h-3 text-gray-400" />
                      <span>{post.views.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center gap-1 text-xs">
                      <Heart className="w-3 h-3 text-red-400" />
                      <span>{post.likes}</span>
                    </div>
                    <div className="flex items-center gap-1 text-xs">
                      <MessageSquare className="w-3 h-3 text-blue-400" />
                      <span>{post.comments}</span>
                    </div>
                    <div className="flex items-center gap-1 text-xs">
                      <Share2 className="w-3 h-3 text-green-400" />
                      <span>{post.shares}</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-400">
                <BarChart3 className="w-12 h-12 mx-auto mb-2" />
                <p className="text-sm">Nu există date de performanță</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

