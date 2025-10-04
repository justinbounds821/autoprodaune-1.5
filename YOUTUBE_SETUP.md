# 📺 YouTube API Setup Guide

**Time Required:** 5 minutes  
**Cost:** FREE (Google Cloud Free Tier)

---

## 🎯 Why You Need This

YouTube API allows AutoPro Daune to:
- ✅ Get real subscriber counts
- ✅ Track channel growth
- ✅ Display analytics in Subscriber Tracker tab
- ✅ Upload videos automatically (optional)

**Without API key:** System will use mock data (still works, just not real numbers).

---

## 📋 Step-by-Step Setup

### **Step 1: Access Google Cloud Console** (1 min)

1. Open in browser: **https://console.cloud.google.com/apis/credentials**
2. Login with your Google account (same one as YouTube channel)

---

### **Step 2: Create/Select Project** (1 min)

**Option A: Create New Project**
```
1. Click "Select a project" (top left)
2. Click "NEW PROJECT"
3. Project name: "AutoPro Daune API"
4. Click "CREATE"
5. Wait 30 seconds for project creation
```

**Option B: Use Existing Project**
```
1. Click "Select a project"
2. Choose existing project from list
```

---

### **Step 3: Enable YouTube Data API** (1 min)

```
1. In search bar, type: "YouTube Data API v3"
2. Click "YouTube Data API v3"
3. Click "ENABLE" button
4. Wait for activation (~10 seconds)
```

**Direct link:** https://console.cloud.google.com/apis/library/youtube.googleapis.com

---

### **Step 4: Create API Key** (2 min)

```
1. Go to: APIs & Services → Credentials
   Direct: https://console.cloud.google.com/apis/credentials
2. Click "CREATE CREDENTIALS" (top)
3. Select "API key"
4. Copy the generated API key (looks like: AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXX)
5. Click "RESTRICT KEY" (recommended for security)
```

**Security Restriction (Recommended):**
```
1. Name: "AutoPro Daune YouTube API"
2. Application restrictions: "HTTP referrers"
3. Add referrers:
   - http://localhost:3003/*
   - http://localhost:8001/*
   - https://your-domain.com/* (when deployed)
4. API restrictions: "Restrict key"
5. Select: "YouTube Data API v3"
6. Click "SAVE"
```

---

### **Step 5: Add to .env File** (30 seconds)

```bash
# Open .env file
# Find this line:
YOUTUBE_API_KEY=

# Replace with your key:
YOUTUBE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Save file and restart backend:**
```powershell
# Stop backend (Ctrl+C)
# Start again
cd services/api
uvicorn app.main:app --reload --port 8001
```

---

## ✅ Verify It Works

### **Test in Browser:**
```
1. Start backend + frontend
2. Open Dashboard → Subscribers tab
3. Should see real YouTube subscriber count
4. Click "Refresh" to update
```

### **Test API Directly:**
```bash
# Replace YOUR_CHANNEL_ID with your actual channel ID
curl "https://www.googleapis.com/youtube/v3/channels?part=statistics&id=YOUR_CHANNEL_ID&key=YOUR_API_KEY"

# Expected response:
{
  "items": [{
    "statistics": {
      "subscriberCount": "1234",
      "viewCount": "56789",
      "videoCount": "42"
    }
  }]
}
```

---

## 🔍 How to Find Your Channel ID

**Method 1: YouTube Studio**
```
1. Go to: https://studio.youtube.com
2. Click "Settings" (bottom left)
3. Click "Channel" → "Advanced settings"
4. Copy "Channel ID"
```

**Method 2: Your Channel URL**
```
If URL is: youtube.com/channel/UCxxxxxxxxxxxxxx
Then Channel ID is: UCxxxxxxxxxxxxxx
```

**Method 3: Custom URL**
```
If URL is: youtube.com/@YourName
1. Go to: https://www.youtube.com/@YourName
2. View page source (Ctrl+U)
3. Search for: "channelId"
4. Copy the ID
```

---

## 🚨 Troubleshooting

### **Error: "API key not valid"**
```
Solution:
1. Check key is copied correctly (no spaces)
2. Verify YouTube Data API v3 is enabled
3. Wait 5 minutes for API activation
4. Check API restrictions allow localhost
```

### **Error: "Quota exceeded"**
```
Cause: Free tier limit = 10,000 requests/day
Solution:
1. Reduce refresh frequency in code
2. Cache results (already implemented)
3. Request quota increase (free)
```

### **Error: "Access forbidden"**
```
Solution:
1. Check channel is public (not private)
2. Verify using correct Google account
3. Enable "Public statistics" in YouTube Studio
```

---

## 💰 Cost & Quota

### **Free Tier (Default):**
- ✅ 10,000 quota units/day
- ✅ 1 channel stats request = 1 unit
- ✅ AutoPro Daune uses ~50 units/day
- ✅ **Plenty for your needs!**

### **Request Quota Increase (If Needed):**
```
1. Go to: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas
2. Click "EDIT QUOTAS"
3. Request increase to 100,000/day
4. Approval: Usually automatic (free)
```

---

## 🔐 Security Best Practices

### **Do:**
- ✅ Restrict API key to specific domains
- ✅ Restrict to YouTube Data API v3 only
- ✅ Keep key in .env (never commit to Git)
- ✅ Use different keys for dev/prod

### **Don't:**
- ❌ Share API key publicly
- ❌ Commit .env to Git
- ❌ Use unrestricted API keys
- ❌ Hardcode key in source code

---

## 📊 What AutoPro Uses YouTube API For

### **Current Features:**
1. **Subscriber Count** - Real-time subscriber tracking
2. **Growth Analytics** - Daily/weekly/monthly growth
3. **Channel Stats** - Views, videos count

### **Future Features (Optional):**
4. **Video Upload** - Auto-upload generated videos
5. **Comment Monitoring** - Track engagement
6. **Analytics Dashboard** - Detailed insights

---

## 🔄 Alternative: Without API Key

**If you don't want to set up YouTube API now:**

System will use **mock data**:
- ✅ Subscriber count: Random realistic numbers
- ✅ Growth tracking: Simulated growth
- ✅ All features work (just not real data)

**To use mock data:**
```bash
# In .env file, leave empty:
YOUTUBE_API_KEY=

# System automatically falls back to mock data
```

---

## ✅ Summary

1. **Go to:** https://console.cloud.google.com/apis/credentials
2. **Enable:** YouTube Data API v3
3. **Create:** API Key
4. **Restrict:** To localhost + your domain
5. **Add to:** .env file
6. **Restart:** Backend server
7. **Test:** Dashboard → Subscribers tab

**Time:** 5 minutes  
**Cost:** FREE  
**Result:** Real YouTube subscriber tracking! 🎉

---

## 🆘 Need Help?

**Still stuck?**
- Check: https://developers.google.com/youtube/v3/getting-started
- Or: Leave `YOUTUBE_API_KEY=` empty to use mock data

**System works either way!** ✅
