# AutoPro Daune - Final Implementation Plan (ADAPTED TO EXISTING STRUCTURE)

**Date**: September 30, 2025  
**Strategy**: UPDATE existing code, NOT recreate  
**Goal**: Perfect implementation on current folder structure

---

## 🔍 WHAT WE HAVE (Existing Structure Analysis)

### Backend (services/api/app/)

**Services Already Exist:**
```
services/
├── video_generator.py ✅ (Uses Pika/HeyGen - needs Manole extension)
├── audio_tts.py ✅ (Has TTS - needs voice cloning)
├── social_poster.py ✅ (Posts to social - complete)
├── whatsapp_bot.py ✅ (WhatsApp API - complete)
├── automation_scheduler.py ✅ (Scheduler - complete)
├── financial/ ✅ (Cost tracking - complete)
├── autoposter/
│   ├── tiktok.py ✅ (Upload working - MISSING follower count)
│   ├── ig.py ✅ (Upload working - MISSING follower count)
│   └── youtube.py ✅ (Upload working - MISSING follower count)
├── instagram/
│   └── api_client.py ✅ (Posts - MISSING analytics)
├── youtube/
│   └── api_client.py ✅ (Posts - MISSING analytics)
└── content/ ✅ (Content management - complete)
```

**Routes Already Exist:**
```
routes/
├── video.py ✅ (Generate, status - MISSING delete, download)
├── automation.py ✅ (Toggle, logs - complete)
├── leads.py ✅ (CRUD - MISSING scoring)
├── financial.py ✅ (Revenue, costs - MISSING export)
├── social.py ✅ (Social posting - complete)
├── whatsapp.py ✅ (WhatsApp integration - complete)
├── customer_nurturing.py ✅ (VERIFY if has sequences)
└── autoposter.py ✅ (Autoposter control - complete)
```

### Frontend (02_FRONTEND_UI_CLEAN/src/)

**Pages Already Exist:**
```
pages/
├── Dashboard.tsx ✅ (6 tabs: Overview, Videos, Automation, Social, Financial, Leads)
├── Landing.tsx ✅ (Public landing - needs WhatsApp CTA enhancement)
├── VideoManagement.tsx ✅ (In Dashboard - may need Manole creator)
├── AutomationControl.tsx ✅ (In Dashboard - complete)
├── SocialMedia.tsx ✅ (In Dashboard - needs subscriber display)
├── FinancialDashboard.tsx ✅ (In Dashboard - needs export button)
└── LeadManagement.tsx ✅ (In Dashboard - needs scoring display)
```

**Services Created (Session Previous):**
```
services/
├── LeadService.ts ✅
├── VideoService.ts ✅
├── AutomationService.ts ✅
├── SocialMediaService.ts ✅
├── FinancialService.ts ✅
└── index.ts ✅
```

---

## 🎯 IMPLEMENTATION TASKS (15 Concrete Updates)

### PHASE 0: Prerequisites (USER ACTION - 1 hour)

#### Task 0.1: Execute Database Schema
**File**: N/A (Supabase Dashboard)
**Action**: 
1. Open https://supabase.com/dashboard
2. Go to SQL Editor
3. Copy `services/api/database/supabase_schema.sql`
4. Execute
5. Verify 11 tables created

**Time**: 5 minutes

---

#### Task 0.2: Collect API Keys & Add to .env
**File**: `services/api/.env`
**Action**: Add these keys (user provides):

```env
# TikTok API
TIKTOK_CLIENT_KEY=xxx
TIKTOK_CLIENT_SECRET=xxx
TIKTOK_ACCESS_TOKEN=xxx
TIKTOK_REFRESH_TOKEN=xxx

# Instagram/Facebook
FACEBOOK_ACCESS_TOKEN=xxx
INSTAGRAM_ACCESS_TOKEN=xxx

# YouTube
YOUTUBE_CLIENT_ID=xxx
YOUTUBE_CLIENT_SECRET=xxx
YOUTUBE_REFRESH_TOKEN=xxx

# WhatsApp
WHATSAPP_DIRECT_NUMBER=40XXXXXXXXX
WHATSAPP_GROUP_LINK=https://chat.whatsapp.com/XXX

# ElevenLabs (optional)
ELEVENLABS_API_KEY=xxx
ELEVENLABS_VOICE_ID=manole_voice
```

**Time**: User provides (30 min)

---

### PHASE 1: Manole Video Generator (Extension of Existing Code)

#### Task 1.1: Extend video_generator.py - Add Manole Photo Animation
**File**: `services/api/app/services/video_generator.py`
**Action**: ADD these methods to existing `VideoGenerator` class:

```python
def animate_manole_photo(self, photo_path: str, duration: int = 30) -> VideoClip:
    """Animate Manole's photo with Ken Burns effect"""
    from moviepy.editor import ImageClip
    from PIL import Image
    import numpy as np
    
    img = Image.open(photo_path)
    img_array = np.array(img)
    
    # Ken Burns effect (zoom + pan)
    clip = ImageClip(img_array).with_duration(duration)
    
    # Slow zoom in
    clip = clip.resized(lambda t: 1 + 0.15 * (t / duration))
    
    # Slow pan down
    clip = clip.with_position(lambda t: ('center', int(50 - t * 2)))
    
    return clip

def overlay_accident_footage(
    self, 
    main_clip: VideoClip, 
    footage_path: str, 
    mode: str = "sequence",
    start_time: float = 10.0
) -> VideoClip:
    """Overlay accident footage in main video"""
    from moviepy.editor import VideoFileClip, CompositeVideoClip
    
    accident_clip = VideoFileClip(footage_path).resized(height=400)
    
    if mode == "pip":  # Picture-in-picture
        accident_clip = accident_clip.with_position(("right", "bottom"))
        final = CompositeVideoClip([main_clip, accident_clip.with_start(start_time)])
        
    elif mode == "split":  # Split screen
        accident_clip = accident_clip.resized(width=main_clip.w // 2)
        final = clips_array([[main_clip.resized(width=main_clip.w // 2), accident_clip]])
        
    else:  # sequence (default)
        final = concatenate_videoclips([
            main_clip.subclip(0, start_time),
            accident_clip,
            main_clip.subclip(start_time)
        ])
    
    return final
```

**Test**:
```python
generator = VideoGenerator()
photo_clip = generator.animate_manole_photo("manole_photo.jpg", duration=30)
# Should create 30s video with zoom/pan effect
```

**Time**: 3-4 hours

---

#### Task 1.2: Extend audio_tts.py - Add Manole Voice Cloning
**File**: `services/api/app/services/audio_tts.py`
**Action**: ADD voice cloning support:

```python
import os
from elevenlabs import Voice, VoiceSettings, generate

class ManoleVoiceCloner:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "manole_voice")
        
    async def generate_manole_voice(
        self, 
        text: str, 
        emotion: str = "professional"
    ) -> str:
        """Generate audio with Manole's cloned voice"""
        if not self.api_key:
            # Fallback to Edge-TTS Romanian
            return await self.edge_tts_fallback(text)
        
        # Use ElevenLabs voice cloning
        audio = generate(
            text=text,
            voice=self.voice_id,
            api_key=self.api_key,
            model="eleven_multilingual_v2"
        )
        
        # Save to temp file
        audio_path = f"/tmp/manole_voice_{hash(text)}.mp3"
        with open(audio_path, 'wb') as f:
            f.write(audio)
        
        return audio_path
    
    async def edge_tts_fallback(self, text: str) -> str:
        """Fallback to Edge-TTS Romanian voice"""
        import edge_tts
        
        audio_path = f"/tmp/edge_tts_{hash(text)}.mp3"
        communicate = edge_tts.Communicate(text, "ro-RO-EmilNeural")
        await communicate.save(audio_path)
        
        return audio_path
```

**Test**:
```python
cloner = ManoleVoiceCloner()
audio_file = await cloner.generate_manole_voice(
    "Bună, sunt Manole. Te ajut cu daune auto.",
    emotion="professional"
)
# Should generate MP3 file
```

**Time**: 2-3 hours

---

#### Task 1.3: Add Manole Video Endpoint
**File**: `services/api/app/routes/video.py` (ADD new route)
**Action**: ADD this endpoint:

```python
from fastapi import File, Form, UploadFile
from typing import List, Optional

@router.post("/video/manole/generate")
async def generate_manole_video(
    prompt: str = Form(...),
    manole_photo: UploadFile = File(...),
    accident_footage: List[UploadFile] = File(None),
    display_mode: str = Form("sequence"),
    voice_emotion: str = Form("professional")
):
    """Generate video with Manole talking + accident footage"""
    # Save uploaded photo
    photo_path = f"/tmp/manole_{manole_photo.filename}"
    with open(photo_path, 'wb') as f:
        f.write(await manole_photo.read())
    
    # Generate script from prompt
    generator = VideoGenerator()
    script = generator.generate_prompt()["script"]  # Or use prompt directly
    
    # Clone Manole's voice
    cloner = ManoleVoiceCloner()
    audio_path = await cloner.generate_manole_voice(script, voice_emotion)
    
    # Animate Manole's photo
    photo_clip = generator.animate_manole_photo(photo_path, duration=30)
    
    # Add audio
    audio_clip = AudioFileClip(audio_path)
    video_with_audio = photo_clip.with_audio(audio_clip)
    
    # Overlay accident footage if provided
    if accident_footage:
        for footage in accident_footage:
            footage_path = f"/tmp/accident_{footage.filename}"
            with open(footage_path, 'wb') as f:
                f.write(await footage.read())
            
            video_with_audio = generator.overlay_accident_footage(
                video_with_audio,
                footage_path,
                mode=display_mode
            )
    
    # Add WhatsApp CTA
    whatsapp_link = os.getenv("WHATSAPP_GROUP_LINK")
    final_video = generator.add_cta_overlay(video_with_audio, whatsapp_link)
    
    # Save final video
    output_path = f"/tmp/manole_video_{datetime.now().timestamp()}.mp4"
    final_video.write_videofile(output_path, fps=24)
    
    # Upload to storage
    video_url = await upload_to_storage(output_path)
    
    return {
        "success": True,
        "video_url": video_url,
        "duration": final_video.duration
    }
```

**Time**: 2 hours

---

#### Task 1.4: Create ManoleVideoCreator.tsx UI
**File**: `02_FRONTEND_UI_CLEAN/src/pages/ManoleVideoCreator.tsx` (NEW)
**Action**: Create component:

```typescript
import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';

export default function ManoleVideoCreator() {
  const [prompt, setPrompt] = useState('');
  const [manolePhoto, setManolePhoto] = useState<File | null>(null);
  const [accidentFootage, setAccidentFootage] = useState<File[]>([]);
  const [displayMode, setDisplayMode] = useState('sequence');
  const [voiceEmotion, setVoiceEmotion] = useState('professional');
  const [progress, setProgress] = useState(0);
  const [generating, setGenerating] = useState(false);
  const { toast } = useToast();

  const handleGenerate = async () => {
    if (!prompt || !manolePhoto) {
      toast({ title: 'Eroare', description: 'Prompt și foto Manole sunt obligatorii' });
      return;
    }

    setGenerating(true);
    setProgress(0);

    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('manole_photo', manolePhoto);
    formData.append('display_mode', displayMode);
    formData.append('voice_emotion', voiceEmotion);
    accidentFootage.forEach(file => formData.append('accident_footage', file));

    try {
      const response = await fetch('/api/video/manole/generate', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (data.success) {
        toast({ title: 'Success!', description: 'Video generat cu succes!' });
        setProgress(100);
      }
    } catch (error) {
      toast({ title: 'Eroare', description: 'Nu s-a putut genera video-ul' });
    } finally {
      setGenerating(false);
    }
  };

  return (
    <Card className="p-6">
      <h2 className="text-2xl font-bold mb-4">Manole Video Creator</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block mb-2">📝 Prompt (ce vrei să spună Manole):</label>
          <Textarea
            placeholder="Ex: Explică cum funcționează procesul de daună auto..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={4}
          />
        </div>

        <div>
          <label className="block mb-2">📷 Foto Manole:</label>
          <Input
            type="file"
            accept="image/*"
            onChange={(e) => setManolePhoto(e.target.files?.[0] || null)}
          />
        </div>

        <div>
          <label className="block mb-2">🚗 Accident Footage (opțional):</label>
          <Input
            type="file"
            accept="image/*,video/*"
            multiple
            onChange={(e) => setAccidentFootage(Array.from(e.target.files || []))}
          />
        </div>

        <div>
          <label className="block mb-2">🎭 Display Mode:</label>
          <Select value={displayMode} onValueChange={setDisplayMode}>
            <option value="sequence">Secvențial (Manole → Accident → Manole)</option>
            <option value="pip">Picture-in-Picture</option>
            <option value="split">Split Screen</option>
          </Select>
        </div>

        <div>
          <label className="block mb-2">🎤 Voice Emotion:</label>
          <Select value={voiceEmotion} onValueChange={setVoiceEmotion}>
            <option value="professional">Professional</option>
            <option value="empathetic">Empathetic</option>
            <option value="urgent">Urgent</option>
          </Select>
        </div>

        {generating && (
          <div>
            <label className="block mb-2">Progress:</label>
            <Progress value={progress} />
          </div>
        )}

        <Button onClick={handleGenerate} disabled={generating} className="w-full">
          {generating ? 'Generating...' : '🎬 Generate Video'}
        </Button>
      </div>
    </Card>
  );
}
```

**Time**: 2 hours

---

#### Task 1.5: Add ManoleVideoCreator to Dashboard
**File**: `02_FRONTEND_UI_CLEAN/src/pages/Dashboard.tsx`
**Action**: UPDATE Dashboard tabs:

```typescript
// Add import
import ManoleVideoCreator from './ManoleVideoCreator';

// Update TabsList (find existing one and add new tab)
<TabsList className="grid w-full grid-cols-7"> {/* Changed from 6 to 7 */}
  <TabsTrigger value="overview">Overview</TabsTrigger>
  <TabsTrigger value="videos">Videos</TabsTrigger>
  <TabsTrigger value="manole">Manole Creator</TabsTrigger> {/* NEW */}
  <TabsTrigger value="automation">Automation</TabsTrigger>
  <TabsTrigger value="social">Social</TabsTrigger>
  <TabsTrigger value="financial">Financial</TabsTrigger>
  <TabsTrigger value="leads">Leads</TabsTrigger>
</TabsList>

// Add new TabsContent (after existing tabs)
<TabsContent value="manole">
  <ManoleVideoCreator />
</TabsContent>
```

**Time**: 15 minutes

---

### PHASE 2: Subscriber Tracking (Extend Existing Autoposter Services)

#### Task 2.1: Add Follower Count to tiktok.py
**File**: `services/api/app/services/autoposter/tiktok.py`
**Action**: ADD these methods to `TikTokUploader` class:

```python
async def get_follower_count(self) -> int:
    """Get current follower count"""
    url = "https://open.tiktokapis.com/v2/user/info/"
    headers = {"Authorization": f"Bearer {self.access_token}"}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    return data.get("data", {}).get("follower_count", 0)

async def get_follower_growth(self, days: int = 7) -> dict:
    """Get follower growth over time"""
    current_count = await self.get_follower_count()
    
    # Get previous count from database
    # (Assuming you store daily snapshots in performance_metrics table)
    from .supabase_client import get_supabase_client
    supabase = get_supabase_client()
    
    result = await supabase.table("performance_metrics")\\
        .select("metric_value")\\
        .eq("metric_name", "tiktok_followers")\\
        .gte("created_at", f"now() - interval '{days} days'")\\
        .order("created_at")\\
        .execute()
    
    previous_count = result.data[0]["metric_value"] if result.data else current_count
    
    return {
        "current": current_count,
        "previous": previous_count,
        "growth": current_count - previous_count,
        "growth_percentage": ((current_count - previous_count) / previous_count * 100) if previous_count > 0 else 0
    }
```

**Time**: 1 hour

---

#### Task 2.2-2.3: Add Follower Count to Instagram & YouTube
**Files**: 
- `services/api/app/services/instagram/api_client.py`
- `services/api/app/services/youtube/api_client.py`

**Action**: Similar to Task 2.1, add `get_follower_count()` methods

**Time**: 2 hours total

---

#### Task 2.4: Add Subscriber Tracking Route
**File**: `services/api/app/routes/social.py` (ADD)
**Action**:

```python
@router.get("/social/subscribers")
async def get_all_subscribers():
    """Get follower counts from all platforms"""
    from app.services.autoposter.tiktok import TikTokUploader
    from app.services.instagram.api_client import InstagramClient
    from app.services.youtube.api_client import YouTubeClient
    
    tiktok = TikTokUploader()
    instagram = InstagramClient()
    youtube = YouTubeClient()
    
    return {
        "tiktok": await tiktok.get_follower_growth(),
        "instagram": await instagram.get_follower_growth(),
        "youtube": await youtube.get_follower_growth(),
        "total": sum([
            await tiktok.get_follower_count(),
            await instagram.get_follower_count(),
            await youtube.get_follower_count()
        ])
    }
```

**Time**: 30 minutes

---

#### Task 2.5: Add Subscriber Display to SocialMedia.tsx
**File**: `02_FRONTEND_UI_CLEAN/src/pages/SocialMedia.tsx`
**Action**: ADD subscriber tracker component at the top:

```typescript
const [subscribers, setSubscribers] = useState(null);

useEffect(() => {
  const fetchSubscribers = async () => {
    const response = await fetch('/api/social/subscribers');
    const data = await response.json();
    setSubscribers(data);
  };
  
  fetchSubscribers();
  const interval = setInterval(fetchSubscribers, 300000); // Refresh every 5 min
  
  return () => clearInterval(interval);
}, []);

// Add UI at top of component return
{subscribers && (
  <Card className="mb-6 p-6">
    <h3 className="text-xl font-bold mb-4">📈 Subscriber Growth</h3>
    <div className="grid grid-cols-3 gap-4">
      <div>
        <p className="text-sm text-gray-600">TikTok</p>
        <p className="text-2xl font-bold">{subscribers.tiktok.current.toLocaleString()}</p>
        <p className={subscribers.tiktok.growth > 0 ? 'text-green-600' : 'text-red-600'}>
          {subscribers.tiktok.growth > 0 ? '▲' : '▼'} {Math.abs(subscribers.tiktok.growth_percentage).toFixed(1)}%
        </p>
      </div>
      {/* Repeat for Instagram, YouTube */}
    </div>
  </Card>
)}
```

**Time**: 1 hour

---

### PHASE 3: Conversion Tracking & Lead Scoring

#### Task 3.1: Create Conversion Tracking Service
**File**: `services/api/app/services/conversion_tracking.py` (NEW)
**Action**: Create service:

```python
from datetime import datetime
from typing import Optional
from .supabase_client import get_supabase_client

class ConversionTracker:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def track_event(
        self,
        session_id: str,
        stage: str,  # video_view, landing_visit, whatsapp_click, lead_captured, converted
        video_id: Optional[str] = None,
        lead_id: Optional[str] = None,
        source: Optional[str] = None
    ):
        """Track user journey through conversion funnel"""
        await self.supabase.table("conversion_funnel").insert({
            "session_id": session_id,
            "stage": stage,
            "video_id": video_id,
            "lead_id": lead_id,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }).execute()
        
        # Update daily metrics
        await self._update_daily_metrics(stage)
    
    async def _update_daily_metrics(self, stage: str):
        """Increment daily conversion metrics"""
        today = datetime.now().date().isoformat()
        
        # Get or create today's record
        result = await self.supabase.table("conversion_metrics")\\
            .select("*")\\
            .eq("date", today)\\
            .execute()
        
        if result.data:
            # Update existing
            record = result.data[0]
            stage_column = {
                "video_view": "video_views",
                "landing_visit": "landing_visits",
                "whatsapp_click": "whatsapp_clicks",
                "lead_captured": "leads_captured",
                "converted": "conversions"
            }.get(stage)
            
            if stage_column:
                await self.supabase.table("conversion_metrics")\\
                    .update({stage_column: record[stage_column] + 1})\\
                    .eq("id", record["id"])\\
                    .execute()
        else:
            # Create new record
            await self.supabase.table("conversion_metrics").insert({
                "date": today,
                stage: 1
            }).execute()
    
    async def get_funnel_stats(self, days: int = 7) -> dict:
        """Get conversion funnel statistics"""
        result = await self.supabase.table("conversion_metrics")\\
            .select("*")\\
            .gte("date", f"now() - interval '{days} days'")\\
            .execute()
        
        totals = {
            "video_views": 0,
            "landing_visits": 0,
            "whatsapp_clicks": 0,
            "leads_captured": 0,
            "conversions": 0
        }
        
        for record in result.data:
            for key in totals:
                totals[key] += record.get(key, 0)
        
        return {
            **totals,
            "conversion_rate": (totals["conversions"] / totals["video_views"] * 100) if totals["video_views"] > 0 else 0
        }
```

**Time**: 2 hours

---

#### Task 3.2: Add Lead Scoring to leads.py
**File**: `services/api/app/routes/leads.py` (ADD)
**Action**:

```python
def calculate_lead_score(lead: dict) -> int:
    """Calculate lead quality score (0-50)"""
    score = 0
    
    # Source scoring (0-10)
    source_scores = {
        "whatsapp_direct": 10,
        "whatsapp_group": 8,
        "landing_form": 6,
        "social_comment": 4,
        "organic": 5
    }
    score += source_scores.get(lead.get("source", ""), 0)
    
    # Priority from details (0-10)
    if lead.get("priority") == "urgent":
        score += 10
    elif lead.get("priority") == "high":
        score += 7
    elif lead.get("priority") == "medium":
        score += 4
    
    # Response time (0-10)
    created_at = datetime.fromisoformat(lead["created_at"])
    hours_since_creation = (datetime.now() - created_at).total_seconds() / 3600
    
    if hours_since_creation < 1:
        score += 10
    elif hours_since_creation < 24:
        score += 7
    elif hours_since_creation < 168:
        score += 4
    
    # Damage type complexity (0-10)
    damage_type = lead.get("damage_type", "").lower()
    if "total loss" in damage_type or "major" in damage_type:
        score += 10
    elif "moderate" in damage_type:
        score += 7
    elif "minor" in damage_type:
        score += 4
    
    # Location (0-10)
    location = lead.get("location", "").lower()
    major_cities = ["bucuresti", "cluj", "timisoara", "iasi", "brasov"]
    if any(city in location for city in major_cities):
        score += 10
    else:
        score += 5
    
    return min(score, 50)  # Cap at 50

@router.post("/leads/score/{lead_id}")
async def score_lead(lead_id: str):
    """Calculate and update lead score"""
    # Get lead from database
    result = await supabase.table("leads").select("*").eq("id", lead_id).execute()
    lead = result.data[0] if result.data else None
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Calculate score
    score = calculate_lead_score(lead)
    
    # Determine priority based on score
    if score >= 35:
        priority = "urgent"
    elif score >= 20:
        priority = "high"
    elif score >= 10:
        priority = "medium"
    else:
        priority = "low"
    
    # Update lead
    await supabase.table("leads").update({
        "lead_score": score,
        "priority": priority
    }).eq("id", lead_id).execute()
    
    return {"score": score, "priority": priority}
```

**Time**: 2 hours

---

### PHASE 4: Missing Backend Endpoints

#### Task 4.1: Add Video Delete & Download
**File**: `services/api/app/routes/video.py` (ADD)
**Action**:

```python
@router.delete("/video/{video_id}")
async def delete_video(video_id: str):
    """Delete video from database and storage"""
    # Get video info
    result = await supabase.table("video_jobs").select("*").eq("id", video_id).execute()
    video = result.data[0] if result.data else None
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Delete from storage
    if video.get("video_url"):
        await delete_from_storage(video["video_url"])
    
    # Delete from database
    await supabase.table("video_jobs").delete().eq("id", video_id).execute()
    
    return {"success": True, "message": "Video deleted"}

@router.get("/video/{video_id}/download")
async def download_video(video_id: str):
    """Download video file"""
    from fastapi.responses import FileResponse
    
    result = await supabase.table("video_jobs").select("*").eq("id", video_id).execute()
    video = result.data[0] if result.data else None
    
    if not video or not video.get("video_url"):
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Download from storage to temp file
    local_path = await download_from_storage(video["video_url"])
    
    return FileResponse(
        local_path,
        media_type="video/mp4",
        filename=f"video_{video_id}.mp4"
    )
```

**Time**: 1 hour

---

#### Task 4.2: Add Financial Export
**File**: `services/api/app/routes/financial.py` (ADD)
**Action**:

```python
@router.post("/financial/export")
async def export_financial_report(format: str = "excel", period: str = "30d"):
    """Export financial report as Excel or PDF"""
    import pandas as pd
    from io import BytesIO
    
    # Get data
    revenues = await get_revenues(period)
    costs = await get_costs(period)
    
    # Create DataFrame
    df = pd.DataFrame({
        "Type": ["Revenue"] * len(revenues) + ["Cost"] * len(costs),
        "Amount": [r["amount"] for r in revenues] + [c["amount"] for c in costs],
        "Date": [r["date"] for r in revenues] + [c["date"] for c in costs],
        "Description": [r["description"] for r in revenues] + [c["description"] for c in costs]
    })
    
    # Export
    if format == "excel":
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        
        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=financial_report.xlsx"}
        )
    
    # PDF export would go here
    return {"error": "PDF export not implemented yet"}
```

**Time**: 1.5 hours

---

## 📊 TOTAL TIME ESTIMATE

| Phase | Tasks | Time |
|-------|-------|------|
| PHASE 0 | Prerequisites | 1 hour (user) |
| PHASE 1 | Manole Video Generator | 12-14 hours |
| PHASE 2 | Subscriber Tracking | 5-6 hours |
| PHASE 3 | Conversion & Scoring | 4 hours |
| PHASE 4 | Missing Endpoints | 2.5 hours |

**Total Development Time**: ~23-26 hours (3-4 days of focused work)

---

## ✅ DEFINITION OF DONE

Each task is complete when:

1. ✅ Code compiles with no errors
2. ✅ Manual testing shows feature works
3. ✅ Existing functionality not broken
4. ✅ API endpoint returns expected data
5. ✅ UI displays data correctly
6. ✅ No console errors in browser/terminal

---

## 🎯 NEXT IMMEDIATE ACTION

**START HERE:**

1. User: Execute `supabase_schema.sql` in Supabase (5 min)
2. User: Provide API keys in `.env` file (30 min)
3. Dev: Start PHASE 1 - Task 1.1 (Extend video_generator.py)

**Priority Order**: PHASE 0 → PHASE 1 → PHASE 2 → PHASE 3 → PHASE 4

---

**Document Status**: ✅ READY FOR EXECUTION  
**Last Updated**: September 30, 2025  
**Adapted to**: EXISTING project structure (no recreation)
