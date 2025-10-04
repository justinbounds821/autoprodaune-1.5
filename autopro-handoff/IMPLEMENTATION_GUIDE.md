# AutoPro Video Engine - Implementation Guide

## Prerequisites

### System Requirements
- **Python 3.8+** with pip
- **FFmpeg** installed and available in PATH
- **Supabase** account and project
- **ElevenLabs** API key (optional, fallback available)
- **Cloudflare R2** account (for production storage)

### Optional Dependencies
- **SadTalker** for lip-sync (install in `third_party/SadTalker`)
- **Wav2Lip** for lip-sync (install in `third_party/Wav2Lip`)

## Step 1: Environment Setup

### 1.1 Configure Environment Variables

Copy the example environment file:
```bash
cp services/api/env.example services/api/.env
```

Edit `services/api/.env` with your actual values:
```bash
# Required for video engine
USE_INTERNAL_VIDEO_ENGINE=true
LIPSYNC_BACKEND=sadtalker  # or 'wav2lip' or 'none'

# ElevenLabs TTS (optional - fallback available)
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=Rachel

# Video settings
VIDEO_ENGINE_FPS=25
VIDEO_ENGINE_CANVAS=1280x720
VIDEO_ENGINE_PRESET=medium  # low/medium/high
VIDEO_ENGINE_STORAGE=local   # local/r2

# Supabase (required for production)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key

# R2 Storage (for production)
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=autopro-videos

# Webhook (optional)
WEBHOOK_COMPLETED_URL=http://127.0.0.1:3007/api/video/webhook
```

### 1.2 Install Python Dependencies

```bash
cd services/api
pip install -r requirements.txt
cd ../..
```

## Step 2: Database Setup

### 2.1 Run Database Migration

Apply the video engine schema to Supabase:

```powershell
# Using environment variables
.\scripts\db-migrate-video.ps1

# Or with explicit credentials
.\scripts\db-migrate-video.ps1 -SupabaseUrl "your-url" -SupabaseKey "your-key"

# Dry run to preview changes
.\scripts\db-migrate-video.ps1 -DryRun
```

This creates the following tables:
- `video_jobs` - Job tracking and metadata
- `video_assets` - Asset references and metadata
- `video_costs` - Cost tracking and billing
- `video_webhooks` - Webhook delivery tracking

## Step 3: Start the Video Engine

### 3.1 Development Mode

```powershell
.\scripts\run-video-engine.ps1 -Dev
```

This starts the FastAPI server with:
- Hot reload enabled
- Detailed logging
- Development-friendly settings

### 3.2 Production Mode

```powershell
.\scripts\run-video-engine.ps1
```

This starts with:
- Multiple workers (4)
- Production logging level
- Optimized settings

### 3.3 Verify Startup

Check that the server starts successfully:
```bash
curl http://127.0.0.1:8001/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "autopro-daune",
  "port": 8001
}
```

## Step 4: Run Smoke Tests

### 4.1 Complete Test Suite

```powershell
.\scripts\smoke-video-engine.ps1
```

Tests performed:
1. ✅ Health check endpoint
2. ✅ Avatars listing
3. ✅ Video generation (form data)
4. ✅ Status polling until completion
5. ✅ Video download (local storage)
6. ✅ JSON API compatibility

### 4.2 Verbose Mode

```powershell
.\scripts\smoke-video-engine.ps1 -Verbose
```

Provides detailed output for debugging.

### 4.3 Custom Base URL

```powershell
.\scripts\smoke-video-engine.ps1 -BaseUrl "http://your-server:port"
```

## Step 5: Admin Panel Integration

### 5.1 Verify Admin Panel

The existing HeyGenPanel component should work without changes:

1. Navigate to `/admin` in your frontend
2. Look for the "HeyGen Video Generator" section
3. The component should detect the internal engine automatically

### 5.2 Test Video Generation

1. Fill in the script (minimum 10 characters)
2. Select voice and avatar options
3. Click "Generează Video"
4. Monitor status updates
5. Download completed video

## Step 6: Production Deployment

### 6.1 R2 Storage Setup

For production, configure R2 storage:

1. **Create R2 Bucket**: `autopro-videos`
2. **Set Environment Variables**:
   ```bash
   VIDEO_ENGINE_STORAGE=r2
   R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
   R2_ACCESS_KEY_ID=your_access_key
   R2_SECRET_ACCESS_KEY=your_secret_key
   R2_BUCKET_NAME=autopro-videos
   ```

3. **Update CORS Origins** in `services/api/.env`:
   ```bash
   BACKEND_CORS_ORIGINS=https://your-frontend-domain.com,http://localhost:3007
   ```

### 6.2 Webhook Configuration

Set up webhook for job completion notifications:

```bash
WEBHOOK_COMPLETED_URL=https://your-api.com/api/video/webhook
```

### 6.3 Monitoring Setup

Enable cost tracking and monitoring:

```bash
# Cost rates (adjust based on your pricing)
TTS_COST_PER_SECOND=0.0001
PROCESSING_COST_PER_SECOND=0.001
STORAGE_COST_PER_MB=0.01
```

## Configuration Options

### Video Engine Settings

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `VIDEO_ENGINE_FPS` | `25` | `15-60` | Video frame rate |
| `VIDEO_ENGINE_CANVAS` | `1280x720` | Various | Output resolution |
| `VIDEO_ENGINE_PRESET` | `medium` | `low/medium/high` | Quality preset |
| `LIPSYNC_BACKEND` | `sadtalker` | `sadtalker/wav2lip/none` | Lip-sync provider |

### Storage Options

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `VIDEO_ENGINE_STORAGE` | `local` | `local/r2` | Storage backend |
| `R2_BUCKET_NAME` | `autopro-videos` | Any | R2 bucket name |

### Cost Tracking

| Variable | Default | Description |
|----------|---------|-------------|
| `TTS_COST_PER_SECOND` | `0.0001` | Cost per second of TTS |
| `PROCESSING_COST_PER_SECOND` | `0.001` | Cost per second of processing |
| `STORAGE_COST_PER_MB` | `0.01` | Cost per MB of storage |

## Troubleshooting

### Common Issues

#### 1. "Internal video engine disabled"
**Solution**: Set `USE_INTERNAL_VIDEO_ENGINE=true` in `.env`

#### 2. "Script must be at least 10 characters"
**Solution**: Ensure script has minimum 10 characters

#### 3. "No avatar source provided"
**Solution**: Provide either `avatar_image_url` or `avatar_video_url`

#### 4. FFmpeg not found
**Solution**: Install FFmpeg and ensure it's in PATH

#### 5. Supabase connection failed
**Solution**: Check credentials and network access

### Logs and Debugging

Enable verbose logging:
```bash
# In development mode
.\scripts\run-video-engine.ps1 -Dev
```

Check logs in:
- **Server logs**: Terminal output
- **Supabase logs**: Dashboard → Database → Logs
- **Application logs**: Check `/api/logs` endpoints

### Performance Tuning

For better performance:
- Use `VIDEO_ENGINE_PRESET=low` for faster processing
- Disable lip-sync: `LIPSYNC_BACKEND=none`
- Use R2 storage for production scale

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/video/video/heygen/avatars` | List available avatars |
| `POST` | `/api/video/video/heygen/generate` | Generate video (form) |
| `POST` | `/api/video/video/heygen/generate-json` | Generate video (JSON) |
| `GET` | `/api/video/video/heygen/status/{job_id}` | Get job status |
| `GET` | `/api/video/video/heygen/download/{job_id}` | Download video |

### Request Format

#### Form Data
```bash
script: "Your video script here"
voice_id: "Rachel"
avatar_image_url: "https://example.com/avatar.jpg"
style: "realistic"
quality: "high"
language: "ro"
```

#### JSON
```json
{
  "script": "Your video script here",
  "voice_id": "Rachel",
  "avatar_image_url": "https://example.com/avatar.jpg",
  "avatar_video_url": "https://example.com/avatar.mp4",
  "quality": "high",
  "style": "realistic",
  "extra": {
    "captions_enabled": true,
    "background_color": "black"
  }
}
```

### Response Format

#### Generation Response
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "provider": "internal",
  "status": "queued",
  "message": "Video generation queued successfully"
}
```

#### Status Response
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "video_url": "/api/video/video/heygen/download/123e4567-e89b-12d3-a456-426614174000",
  "error": null,
  "meta": {
    "processing_time": 45.2,
    "backend": "sadtalker"
  }
}
```

## Maintenance

### Regular Tasks

1. **Clean up old jobs**:
   ```sql
   SELECT cleanup_old_video_jobs();
   ```

2. **Monitor costs**:
   ```bash
   curl http://localhost:8001/api/video/analytics/costs
   ```

3. **Check system health**:
   ```bash
   curl http://localhost:8001/api/video/video/heygen/health
   ```

### Backup Strategy

1. **Database**: Supabase automatic backups
2. **Videos**: R2 automatic versioning
3. **Code**: Git version control

---

**Status**: ✅ **IMPLEMENTATION COMPLETE**
**Ready for Production**: ✅ **YES**