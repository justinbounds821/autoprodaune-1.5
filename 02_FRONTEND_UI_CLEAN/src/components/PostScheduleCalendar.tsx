import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calendar, Clock, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ScheduledPost {
  id: string;
  content: string;
  platform: string;
  scheduledFor: string;
  status: string;
}

interface PostScheduleCalendarProps {
  posts: ScheduledPost[];
}

export default function PostScheduleCalendar({ posts }: PostScheduleCalendarProps) {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [calendarDays, setCalendarDays] = useState<Date[]>([]);

  useEffect(() => {
    generateCalendar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentMonth]);

  const generateCalendar = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days: Date[] = [];
    
    // Add empty days for previous month
    for (let i = 0; i < startingDayOfWeek; i++) {
      const prevDate = new Date(year, month, -(startingDayOfWeek - i - 1));
      days.push(prevDate);
    }
    
    // Add days of current month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    setCalendarDays(days);
  };

  const getPostsForDate = (date: Date) => {
    return posts.filter(post => {
      const postDate = new Date(post.scheduledFor);
      return (
        postDate.getDate() === date.getDate() &&
        postDate.getMonth() === date.getMonth() &&
        postDate.getFullYear() === date.getFullYear()
      );
    });
  };

  const getPlatformColor = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'tiktok':
        return 'bg-pink-500';
      case 'instagram':
        return 'bg-purple-500';
      case 'facebook':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  const isCurrentMonth = (date: Date) => {
    return date.getMonth() === currentMonth.getMonth();
  };

  const isToday = (date: Date) => {
    const today = new Date();
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    );
  };

  const previousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  const weekDays = ['Dum', 'Lun', 'Mar', 'Mie', 'Joi', 'Vin', 'Sâm'];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Calendar Postări Programate
          </CardTitle>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={previousMonth}>
              ←
            </Button>
            <span className="text-sm font-medium flex items-center px-3">
              {currentMonth.toLocaleDateString('ro-RO', { month: 'long', year: 'numeric' })}
            </span>
            <Button variant="outline" size="sm" onClick={nextMonth}>
              →
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-7 gap-2">
          {/* Week day headers */}
          {weekDays.map(day => (
            <div key={day} className="text-center text-xs font-medium text-gray-500 py-2">
              {day}
            </div>
          ))}
          
          {/* Calendar days */}
          {calendarDays.map((date, index) => {
            const dayPosts = getPostsForDate(date);
            const isCurrent = isCurrentMonth(date);
            const isNow = isToday(date);
            
            return (
              <div
                key={index}
                className={`min-h-[80px] p-2 border rounded-lg ${
                  !isCurrent ? 'bg-gray-50 opacity-50' : ''
                } ${isNow ? 'border-blue-500 border-2' : ''}`}
              >
                <div className={`text-sm font-medium mb-1 ${
                  isNow ? 'text-blue-600' : isCurrent ? 'text-gray-700' : 'text-gray-400'
                }`}>
                  {date.getDate()}
                </div>
                
                <div className="space-y-1">
                  {dayPosts.map(post => (
                    <div
                      key={post.id}
                      className="text-xs p-1 rounded truncate"
                      style={{ backgroundColor: `${getPlatformColor(post.platform)}20` }}
                    >
                      <div className="flex items-center gap-1">
                        <div
                          className={`w-2 h-2 rounded-full ${getPlatformColor(post.platform)}`}
                        />
                        <span className="truncate">
                          {new Date(post.scheduledFor).toLocaleTimeString('ro-RO', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Legend */}
        <div className="mt-4 pt-4 border-t flex gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-pink-500" />
            <span>TikTok</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-purple-500" />
            <span>Instagram</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500" />
            <span>Facebook</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

