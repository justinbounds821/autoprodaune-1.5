# AutoPro Video Engine - Troubleshooting Guide

## Common Issues and Solutions

### 1. "Internal video engine disabled"

**Error Message**:
```
HTTP 412: Internal video engine disabled (set USE_INTERNAL_VIDEO_ENGINE=true)
```

**Causes**:
- `USE_INTERNAL_VIDEO_ENGINE` environment variable not set to `true`
- Environment file not loaded properly
- Server not restarted after configuration changes

**Solutions**:
1. **Check environment variable**:
   ```bash
   echo $USE_INTERNAL_VIDEO_ENGINE
   # Should return: true
   ```

2. **Verify .env file**:
   ```bash
   cat services/api/.env | grep USE_INTERNAL_VIDEO_ENGINE
   # Should show: USE_INTERNAL_VIDEO_ENGINE=true
   ```

3. **Restart server**:
   ```powershell
   .\scripts\run-video-engine.ps1
   ```

4. **Check server logs** for environment loading errors

---

### 2. "Script must be at least 10 characters"

**Error Message**:
```
HTTP 400: Script-ul trebuie să aibă cel puțin 10 caractere
```

**Causes**:
- Script text is too short
- Empty or whitespace-only script

**Solutions**:
1. **Ensure script has content**:
   ```javascript
   // Bad
   script: "Hi"

   // Good
   script: "Bună! Acesta este un test al motorului video AutoPro. Sistemul generează videoclipuri de înaltă calitate."
   ```

2. **Check for hidden characters** or encoding issues

---

### 3. "No avatar source provided"

**Error Message**:
```
HTTP 400: Provide avatar_image_url OR avatar_video_url for lip-sync realism
```

**Causes**:
- Missing both `avatar_image_url` and `avatar_video_url`
- URLs are empty or invalid
- Lip-sync backend requires avatar input

**Solutions**:
1. **Provide at least one avatar source**:
   ```javascript
   // Image only
   avatar_image_url: "https://example.com/avatar.jpg"

   // Video only
   avatar_video_url: "https://example.com/avatar.mp4"

   // Both (video takes precedence)
   avatar_image_url: "https://example.com/avatar.jpg"
   avatar_video_url: "https://example.com/avatar.mp4"
   ```

2. **Verify URLs are accessible**:
   ```bash
   curl -I "https://example.com/avatar.jpg"
   # Should return 200 OK
   ```

3. **For testing without lip-sync**:
   ```bash
   LIPSYNC_BACKEND=none
   ```

---

### 4. FFmpeg not found

**Error Message**:
```
FFmpeg not found. Please install FFmpeg for video processing.
```

**Causes**:
- FFmpeg not installed
- FFmpeg not in system PATH
- Windows: FFmpeg executable not accessible

**Solutions**:
1. **Install FFmpeg**:
   - **Windows**: Download from https://ffmpeg.org/download.html#build-windows
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`

2. **Add to PATH**:
   - **Windows**: Add FFmpeg bin folder to system PATH
   - **Linux/macOS**: Ensure `/usr/bin` or `/usr/local/bin` contains FFmpeg

3. **Verify installation**:
   ```bash
   ffmpeg -version
   # Should show version information
   ```

---

### 5. Supabase connection failed

**Error Message**:
```
Error saving job to Supabase: connection failed
```

**Causes**:
- Invalid Supabase credentials
- Network connectivity issues
- IP not whitelisted in Supabase
- Service key incorrect

**Solutions**:
1. **Verify credentials**:
   ```bash
   # Check .env file
   cat services/api/.env | grep SUPABASE
   ```

2. **Test connection manually**:
   ```bash
   curl -H "apikey: YOUR_SERVICE_KEY" "YOUR_SUPABASE_URL/rest/v1/"
   ```

3. **Check Supabase dashboard**:
   - Go to Settings → API
   - Verify service key
   - Check IP restrictions

4. **Network troubleshooting**:
   ```bash
   ping your-project.supabase.co
   ```

---

### 6. ElevenLabs TTS failed

**Error Message**:
```
ElevenLabs API error: 401
```

**Causes**:
- Invalid API key
- API key not configured
- Network issues
- Rate limiting

**Solutions**:
1. **Verify API key**:
   ```bash
   # Check .env file
   cat services/api/.env | grep ELEVENLABS_API_KEY
   ```

2. **Test API key**:
   ```bash
   curl -H "xi-api-key: YOUR_KEY" "https://api.elevenlabs.io/v1/voices"
   ```

3. **Check rate limits**:
   - ElevenLabs has rate limits per account
   - Consider upgrading plan for production

4. **Fallback available**:
   - System automatically falls back to local TTS
   - Check logs for fallback activation

---

### 7. Lip-sync processing failed

**Error Message**:
```
SadTalker generation failed: [specific error]
```

**Causes**:
- SadTalker not properly installed
- Missing dependencies
- Invalid input files
- GPU/memory issues

**Solutions**:
1. **Check SadTalker installation**:
   ```bash
   ls -la third_party/SadTalker/
   # Should contain inference.py and other files
   ```

2. **Install dependencies**:
   ```bash
   cd third_party/SadTalker
   pip install -r requirements.txt
   ```

3. **Verify input files**:
   ```bash
   # Check avatar image
   file avatar.jpg
   # Should be valid image format

   # Check audio file
   file audio.wav
   # Should be valid WAV format
   ```

4. **Alternative backend**:
   ```bash
   # Try Wav2Lip instead
   LIPSYNC_BACKEND=wav2lip

   # Or disable lip-sync
   LIPSYNC_BACKEND=none
   ```

---

### 8. Video composition failed

**Error Message**:
```
FFmpeg composition failed: [specific FFmpeg error]
```

**Causes**:
- Invalid timeline configuration
- Missing input files
- FFmpeg codec issues
- Disk space full

**Solutions**:
1. **Check input files**:
   ```bash
   # Verify audio file
   ffprobe audio.mp3

   # Verify video files (if any)
   ffprobe avatar.mp4
   ```

2. **Check disk space**:
   ```bash
   df -h  # Linux/macOS
   # or
   wmic logicaldisk get size,freespace  # Windows
   ```

3. **Simplify timeline**:
   ```json
   {
     "duration": 30,
     "layers": [
       {
         "type": "bg",
         "params": {"type": "color", "color": "black"}
       }
     ]
   }
   ```

4. **Check FFmpeg logs** for detailed error information

---

### 9. R2 storage issues

**Error Message**:
```
Failed to save video to R2: [boto3 error]
```

**Causes**:
- Invalid R2 credentials
- Bucket doesn't exist
- Permissions incorrect
- Network connectivity

**Solutions**:
1. **Verify R2 configuration**:
   ```bash
   # Check .env file
   cat services/api/.env | grep R2_
   ```

2. **Test R2 connection**:
   ```python
   import boto3
   s3 = boto3.client('s3', endpoint_url='your-endpoint', ...)
   s3.head_bucket(Bucket='your-bucket')
   ```

3. **Check bucket exists**:
   - Go to Cloudflare R2 dashboard
   - Verify bucket name and region

4. **Permissions**:
   - Ensure API token has R2 read/write permissions
   - Check CORS settings if needed

---

### 10. Webhook delivery failed

**Error Message**:
```
Webhook failed: timeout after 10 seconds
```

**Causes**:
- Target URL not accessible
- Network timeout
- SSL certificate issues
- Server not responding

**Solutions**:
1. **Test webhook URL**:
   ```bash
   curl -X POST https://your-webhook-url.com/api/video/webhook \
     -H "Content-Type: application/json" \
     -d '{"test": "webhook"}'
   ```

2. **Check network connectivity**:
   ```bash
   ping your-webhook-domain.com
   ```

3. **Verify SSL certificate**:
   ```bash
   curl -v https://your-webhook-url.com/api/video/webhook
   ```

4. **Disable webhooks for testing**:
   ```bash
   # Remove or comment out WEBHOOK_COMPLETED_URL
   ```

---

## Performance Issues

### Slow video generation

**Possible causes**:
- High-quality preset (`VIDEO_ENGINE_PRESET=high`)
- Complex lip-sync processing
- Large input files
- Insufficient system resources

**Solutions**:
1. **Lower quality**:
   ```bash
   VIDEO_ENGINE_PRESET=low
   ```

2. **Disable lip-sync**:
   ```bash
   LIPSYNC_BACKEND=none
   ```

3. **Optimize input files**:
   - Use smaller avatar images (512x512)
   - Compress audio files
   - Reduce video resolution

4. **System optimization**:
   - Ensure sufficient RAM (8GB+ recommended)
   - Use SSD storage
   - Close unnecessary applications

---

### High memory usage

**Symptoms**:
- System becomes unresponsive
- Out of memory errors
- Video generation fails

**Solutions**:
1. **Monitor resource usage**:
   ```bash
   # Linux/macOS
   top -o mem

   # Windows
   taskmgr
   ```

2. **Reduce concurrent jobs**:
   - Process jobs sequentially
   - Limit number of workers

3. **Optimize processing**:
   ```bash
   VIDEO_ENGINE_PRESET=low
   LIPSYNC_BACKEND=none
   ```

---

## Logs and Debugging

### Enable verbose logging

```bash
# In development mode
.\scripts\run-video-engine.ps1 -Dev
```

### Check specific log locations

1. **Server logs**: Terminal output
2. **Supabase logs**: Dashboard → Database → Logs
3. **System logs**: `/var/log/system.log` (macOS/Linux)
4. **Application logs**: Check `/api/logs` endpoints

### Debug specific issues

1. **Test individual services**:
   ```bash
   # Test TTS
   curl -X POST http://localhost:8001/api/test/tts \
     -H "Content-Type: application/json" \
     -d '{"text": "test"}'

   # Test storage
   curl -X POST http://localhost:8001/api/test/storage \
     -H "Content-Type: application/json" \
     -d '{"data": "test"}'
   ```

2. **Check service health**:
   ```bash
   curl http://localhost:8001/api/video/video/heygen/health
   ```

---

## Getting Help

### Logs to include when reporting issues:
1. Server startup logs
2. Video generation logs
3. Supabase connection logs
4. System resource information

### Environment information:
- Operating system and version
- Python version
- FFmpeg version
- Available disk space
- Memory usage

### Configuration details:
- Relevant environment variables (without sensitive values)
- Database connection status
- External service connectivity

---

**Last Updated**: 2025-01-04
**Version**: 1.0.0