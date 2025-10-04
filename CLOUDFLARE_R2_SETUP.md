# Cloudflare R2 Storage Setup Guide 📦

**Quick guide to configure R2 for video storage**

---

## ✅ CURRENT STATUS

**R2 Endpoint**: `https://026d4eb7409b0baea2767863f22a76c1.r2.cloudflarestorage.com`  
**Bucket Name**: `autoprodaune`  
**Status**: ⚠️ Need Access Keys

---

## 🚀 SETUP STEPS (5 MINUTES)

### 1. Go to Cloudflare Dashboard
```
https://dash.cloudflare.com/
```

### 2. Navigate to R2
- Click "R2" in left sidebar
- Or go to: https://dash.cloudflare.com/r2

### 3. Verify Bucket Exists
- Should see bucket: **`autoprodaune`**
- If not, create it:
  - Click "Create bucket"
  - Name: `autoprodaune`
  - Region: Auto
  - Click "Create bucket"

### 4. Create API Token
- Click "Manage R2 API Tokens"
- Click "Create API token"
- Settings:
  - **Token name**: `autoprodaune-backend`
  - **Permissions**: 
    - ✅ Object Read & Write
    - ✅ Admin Read & Write (for bucket management)
  - **TTL**: No expiry (or 1 year)
  - **Bucket**: Select `autoprodaune` (or "All buckets")
- Click "Create API Token"

### 5. Copy Credentials
You'll see:
```
Access Key ID: xxxxxxxxxxxxxxxxxxxxxxxx
Secret Access Key: yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
```

**⚠️ IMPORTANT**: Copy both now - Secret Key won't be shown again!

### 6. Add to `.env`
```env
# Cloudflare R2 Storage
CLOUDFLARE_R2_ENDPOINT=https://026d4eb7409b0baea2767863f22a76c1.r2.cloudflarestorage.com
CLOUDFLARE_R2_BUCKET=autoprodaune
AWS_ACCESS_KEY_ID=paste-access-key-id-here
AWS_SECRET_ACCESS_KEY=paste-secret-access-key-here
AWS_REGION=auto
```

### 7. Restart Backend
```bash
cd services/api
python -m uvicorn app.main:app --reload
```

---

## 📦 HOW IT WORKS

### Video Upload Flow:
```
1. User generates Manole video
   ↓
2. Backend creates video locally (/tmp/manole_video_xxx.mp4)
   ↓
3. Upload to R2: autoprodaune/{job_id}.mp4
   ↓
4. Get public URL: https://026d4eb7409b0baea2767863f22a76c1.r2.cloudflarestorage.com/autoprodaune/{job_id}.mp4
   ↓
5. Save URL to database
   ↓
6. Delete local temp file
```

### Storage Structure:
```
autoprodaune/
├── videos/
│   ├── manole_video_abc123.mp4
│   ├── manole_video_def456.mp4
│   └── ...
├── images/
│   ├── manole_photo_ghi789.jpg
│   └── accident_footage_jkl012.jpg
└── exports/
    └── financial_report_2025-09.pdf
```

---

## 🔧 BACKEND INTEGRATION

### Current Implementation:
The backend already has R2 client configured in `services/api/app/services/storage_s3.py`:

```python
from .storage_s3 import S3StorageClient

# Initialize R2 client
storage = S3StorageClient()

# Upload video
video_url = storage.upload_from_path(
    bucket="autoprodaune",
    key=f"videos/{job_id}.mp4",
    local_path="/tmp/manole_video_xxx.mp4"
)

# Returns: https://026d4eb7409b0baea2767863f22a76c1.r2.cloudflarestorage.com/autoprodaune/videos/{job_id}.mp4
```

### Enable Auto-Upload:
In `services/api/app/routes/video.py`, the endpoint already has upload logic:

```python
# After video generation
output_url = self.supabase.upload_from_path(
    "video-outputs", 
    f"{job_id}.mp4", 
    video_path
)

# Cleanup local file
os.remove(video_path)
```

Just add R2 keys to `.env` and it will automatically upload!

---

## 🌐 PUBLIC ACCESS (OPTIONAL)

### Option 1: Keep Private
- Videos only accessible with signed URLs
- More secure
- Recommended for client uploads

### Option 2: Make Public
- Enable public access in R2 settings
- Videos accessible without authentication
- Easier for sharing

**To enable public access**:
1. Go to R2 bucket settings
2. Click "Settings" → "Public Access"
3. Enable "Allow public access"
4. Optionally add custom domain

---

## 📊 PRICING

### Cloudflare R2:
- **Storage**: $0.015/GB/month
- **Class A Operations** (writes): $4.50 per million
- **Class B Operations** (reads): $0.36 per million
- **Egress**: **FREE** (no bandwidth charges!)

### Example Cost:
- 1,000 videos/month (3 MB each) = 3 GB storage
- Cost: **~$0.05/month** 🎉

**Much cheaper than S3!**

---

## 🧪 TESTING

### Test Upload (Python):
```python
import os
from app.services.storage_s3 import S3StorageClient

storage = S3StorageClient()

# Upload test file
url = storage.upload_from_path(
    bucket="autoprodaune",
    key="test/hello.txt",
    local_path="test.txt"
)

print(f"Uploaded to: {url}")
```

### Test via API:
```bash
# Generate Manole video (will auto-upload to R2)
curl -X POST "http://localhost:8001/api/video/manole/generate" \
  -F "prompt=Test video" \
  -F "manole_photo=@manole.jpg"

# Response will include R2 URL:
# {
#   "video_url": "https://026d4eb7409b0baea2767863f22a76c1.r2.cloudflarestorage.com/autoprodaune/videos/abc123.mp4"
# }
```

---

## 🔐 SECURITY BEST PRACTICES

### 1. Restrict API Token Permissions
- Only give access to `autoprodaune` bucket
- Use separate tokens for dev/prod

### 2. Use Signed URLs for Private Content
```python
# Generate temporary access URL (expires in 1 hour)
signed_url = storage.generate_presigned_url(
    bucket="autoprodaune",
    key="videos/private_video.mp4",
    expiration=3600
)
```

### 3. Enable Versioning (Optional)
- Protects against accidental deletion
- Keeps history of file changes

### 4. Set Up Lifecycle Rules
- Auto-delete temp files after 7 days
- Move old videos to cheaper storage

---

## 🆘 TROUBLESHOOTING

### Error: "Access Denied"
**Solution**: Check API token permissions, ensure bucket name is correct

### Error: "Invalid credentials"
**Solution**: Verify Access Key ID and Secret Access Key in `.env`

### Error: "Bucket not found"
**Solution**: Create bucket `autoprodaune` in R2 dashboard

### Videos not uploading?
**Check**:
1. R2 keys in `.env`
2. Backend logs for errors
3. Bucket permissions

---

## 📝 SUMMARY

### ✅ Already Configured:
- R2 endpoint
- Bucket name (`autoprodaune`)

### ⚠️ Need to Add:
1. Get R2 API token from Cloudflare Dashboard (5 min)
2. Add `AWS_ACCESS_KEY_ID` to `.env`
3. Add `AWS_SECRET_ACCESS_KEY` to `.env`
4. Restart backend

### 🎉 Then:
- Videos auto-upload to R2 after generation
- Public URLs for sharing
- Automatic cleanup of local temp files
- **FREE egress** (no bandwidth costs!)

---

**Ready to configure R2?** Follow steps above or run:
```bash
# Add keys to .env manually, then:
.\scripts\start-all.ps1
```

🚀 **After configuring, all Manole videos will be automatically stored in R2!**
