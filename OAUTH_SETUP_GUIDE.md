# OAuth Setup Guide - TikTok & Instagram 🔐

**Quick guide to complete OAuth flows and get access tokens**

---

## 🎯 TikTok OAuth Flow (5-10 minutes)

### Current Status:
✅ **Client Key**: `awna26k858tnrwwn`  
✅ **Client Secret**: `u4J3JYbSD30WKFFYLUdPfwFiuabhqzc5`  
⚠️ **Need**: Access Token, Refresh Token, User ID

### Step-by-Step:

1. **Go to TikTok Developer Portal**:
   ```
   https://developers.tiktok.com/app/7551067868255815685/pending
   ```
   (This is your app from screenshot #2)

2. **Generate Access Token**:
   - Click "App review" or "Scopes" section
   - Enable scopes:
     - ✅ `user.info.basic` (get follower count)
     - ✅ `video.list` (get video count)
     - ✅ `video.upload` (upload videos)
   - Click "Generate Access Token" or "Authorize"

3. **Authorize App**:
   - Log in with your TikTok account
   - Accept permissions
   - Copy the generated **Access Token**
   - Copy the **Refresh Token**
   - Copy your **User ID** (shown in response)

4. **Add to `.env`**:
   ```env
   TIKTOK_ACCESS_TOKEN=paste-here
   TIKTOK_REFRESH_TOKEN=paste-here
   TIKTOK_USER_ID=paste-here
   ```

5. **Test**:
   ```bash
   # Restart backend
   cd services/api
   python -m uvicorn app.main:app --reload
   
   # Test endpoint
   curl http://localhost:8001/api/social/followers/tiktok
   ```

### Troubleshooting:
- **Token expired?** → Use refresh token to get new access token (automatic in code)
- **Scopes missing?** → Re-authorize with correct scopes
- **User ID not shown?** → Check API response or use `/user/info/` endpoint

---

## 📸 Instagram OAuth Flow (10-15 minutes)

### Current Status:
⚠️ **Need**: Access Token from Facebook Graph API

### Step-by-Step:

1. **Go to Facebook Developers**:
   ```
   https://developers.facebook.com/apps/
   ```

2. **Create App** (if not exists):
   - Click "Create App"
   - Choose "Business" type
   - App Name: "AutoPro Daune"
   - Click "Create App"

3. **Add Instagram Basic Display**:
   - In app dashboard → "Add Product"
   - Find "Instagram" → Click "Set Up"
   - Choose "Instagram Basic Display"

4. **Configure Instagram Basic Display**:
   - Go to Settings → Basic Display
   - Add "Valid OAuth Redirect URIs":
     ```
     https://localhost/
     http://localhost:3003/auth/callback
     ```
   - Save changes

5. **Get Access Token**:
   - Go to "User Token Generator"
   - Click "Generate Token"
   - Log in with Instagram Business Account
   - Accept permissions
   - Copy **Access Token**

6. **Add to `.env`**:
   ```env
   INSTAGRAM_ACCESS_TOKEN=paste-here
   ```

7. **Test**:
   ```bash
   # Restart backend
   curl http://localhost:8001/api/social/followers/instagram
   ```

### Important Notes:
- ⚠️ Token expires in 60 days (short-lived)
- ✅ Use token exchange to get long-lived token (60 days → 60 days renewable)
- ✅ Must use **Instagram Business Account** (not personal)

### Long-Lived Token Exchange:
```bash
curl -X GET "https://graph.instagram.com/access_token
  ?grant_type=ig_exchange_token
  &client_secret=YOUR_APP_SECRET
  &access_token=SHORT_LIVED_TOKEN"
```

---

## 🎥 YouTube OAuth (Optional - For Video Uploads)

### Current Status:
✅ **API Key**: `AIzaSyDj7oPCt9Z6R6xMBqIynEhFhadWjbJ3voI` (read-only)  
⚠️ **Need OAuth**: For video uploads

### Step-by-Step:

1. **Go to Google Cloud Console**:
   ```
   https://console.cloud.google.com/apis/credentials
   ```

2. **Create OAuth 2.0 Client**:
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Web application"
   - Name: "AutoPro Daune"
   - Authorized redirect URIs:
     ```
     http://localhost:8001/auth/youtube/callback
     ```
   - Click "Create"
   - Download JSON credentials

3. **Enable YouTube Data API v3**:
   - Go to "Library"
   - Search "YouTube Data API v3"
   - Click "Enable"

4. **Run OAuth Flow** (Python script):
   ```python
   from google_auth_oauthlib.flow import InstalledAppFlow
   
   SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
             'https://www.googleapis.com/auth/youtube.readonly']
   
   flow = InstalledAppFlow.from_client_secrets_file(
       'client_secrets.json', SCOPES)
   
   credentials = flow.run_local_server(port=8080)
   
   print(f"Access Token: {credentials.token}")
   print(f"Refresh Token: {credentials.refresh_token}")
   ```

5. **Add to `.env`**:
   ```env
   YOUTUBE_CLIENT_ID=from-json
   YOUTUBE_CLIENT_SECRET=from-json
   YOUTUBE_ACCESS_TOKEN=from-oauth-flow
   YOUTUBE_REFRESH_TOKEN=from-oauth-flow
   ```

---

## 🚀 Quick Setup Script

Save this as `get-oauth-tokens.py`:

```python
#!/usr/bin/env python3
"""Quick OAuth setup for AutoPro Daune"""

print("🔐 AutoPro Daune - OAuth Token Generator\n")

# TikTok OAuth
print("📱 TikTok OAuth:")
print("1. Visit: https://developers.tiktok.com/app/7551067868255815685/pending")
print("2. Generate access token with scopes: user.info.basic, video.list, video.upload")
print("3. Copy tokens:\n")

tiktok_access = input("   TikTok Access Token: ").strip()
tiktok_refresh = input("   TikTok Refresh Token: ").strip()
tiktok_user_id = input("   TikTok User ID: ").strip()

# Instagram OAuth
print("\n📸 Instagram OAuth:")
print("1. Visit: https://developers.facebook.com/apps/")
print("2. Create app → Instagram Basic Display")
print("3. Generate token:\n")

instagram_token = input("   Instagram Access Token: ").strip()

# Write to .env
env_content = f"""
# TikTok OAuth Tokens
TIKTOK_ACCESS_TOKEN={tiktok_access}
TIKTOK_REFRESH_TOKEN={tiktok_refresh}
TIKTOK_USER_ID={tiktok_user_id}

# Instagram Token
INSTAGRAM_ACCESS_TOKEN={instagram_token}
"""

with open('services/api/.env', 'a') as f:
    f.write(env_content)

print("\n✅ Tokens added to .env!")
print("🚀 Restart backend to use new tokens")
```

Run it:
```bash
python get-oauth-tokens.py
```

---

## 📊 OAuth Status Checklist

### TikTok:
- [ ] Client Key configured ✅
- [ ] Client Secret configured ✅
- [ ] Access Token obtained ⚠️
- [ ] Refresh Token obtained ⚠️
- [ ] User ID obtained ⚠️
- [ ] Tested follower tracking ⚠️

### Instagram:
- [ ] Facebook app created ⚠️
- [ ] Instagram Basic Display added ⚠️
- [ ] Access Token obtained ⚠️
- [ ] Long-lived token exchanged ⚠️
- [ ] Tested follower tracking ⚠️

### YouTube:
- [ ] API Key configured ✅
- [ ] OAuth Client created ⚠️
- [ ] Access Token obtained ⚠️
- [ ] Tested upload ⚠️

---

## 🎯 Priority Order

1. **TikTok OAuth** (5-10 min) → **HIGH PRIORITY** 🔥
   - Most important for follower tracking
   - App already exists (from screenshot)

2. **Instagram OAuth** (10-15 min) → **MEDIUM PRIORITY**
   - Important for social media tracking
   - Needs Facebook app creation

3. **YouTube OAuth** (15-20 min) → **LOW PRIORITY**
   - API key already works for follower tracking
   - OAuth only needed for video uploads

---

## 💡 Tips

- **Test incrementally**: Get one platform working before moving to next
- **Save tokens**: Store in password manager (1Password, LastPass)
- **Refresh tokens**: Some expire, use refresh flow to renew
- **Scopes**: Request only needed permissions
- **Rate limits**: Be aware of API quotas

---

## 🆘 Need Help?

### TikTok OAuth Issues:
- Docs: https://developers.tiktok.com/doc/login-kit-web/
- Support: TikTok Developer Support

### Instagram Issues:
- Docs: https://developers.facebook.com/docs/instagram-basic-display-api/
- Tool: Facebook Graph API Explorer

### YouTube Issues:
- Docs: https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps
- Console: https://console.cloud.google.com/

---

**After completing OAuth, test with**:
```bash
curl http://localhost:8001/api/social/followers
```

Should return follower counts from all 3 platforms! 🎉
