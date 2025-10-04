# 🎬 HeyGen Integration Guide - Avatar Vorbitor Profesional

**Data:** 30 Septembrie 2025  
**Status:** ✅ Backend implementat, necesită API Key

---

## 🚀 **Ce este HeyGen?**

HeyGen este o platformă AI care generează **video-uri cu avatare vorbitori ultra-realiste**.

### **Features:**
- 🎭 **Avatare fotorealiste** (30+ avatare profesionale)
- 🗣️ **Lip sync perfect** în 40+ limbi (inclusiv română)
- 🎙️ **Voice cloning** (poți clona vocea lui Manole!)
- 📹 **Video HD/4K** (până la 10 minute)
- 🎨 **Backgrounds custom** (office, green screen, etc.)
- 💬 **Subtitrări auto** în orice limbă

---

## 💰 **Prețuri HeyGen:**

| Plan | Preț/Lună | Credits/Lună | Cost/Video (30s) |
|------|-----------|--------------|-------------------|
| **Free** | $0 | 1 video | $0 (trial) |
| **Creator** | $24 | 15 min | ~$1.60 |
| **Business** | $72 | 90 min | ~$0.80 |
| **Enterprise** | Custom | Unlimited | ~$0.50 |

**Recomandare:** Plan **Creator** pentru start ($24/lună = 15 minute video)

---

## 🔑 **Cum obții HeyGen API Key:**

### **PASO 1: Creează cont HeyGen**
1. Mergi pe: **https://app.heygen.com/signup**
2. Sign up cu email
3. Verifică email-ul

### **PASO 2: Upgrade la plan plătit**
1. Mergi la: **Settings → Billing**
2. Alege plan **Creator** ($24/lună)
3. Adaugă card de credit

### **PASO 3: Generează API Key**
1. Mergi la: **https://app.heygen.com/settings/api**
2. Click **"Generate API Key"**
3. **COPIAZĂ KEY-UL** (arată așa: `sk-xxxxxxxxxxxxx`)
4. **IMPORTANT:** Salvează-l sigur, nu se mai arată!

### **PASO 4: Adaugă în `.env`**
```bash
# HeyGen API Configuration
HEYGEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HEYGEN_BASE_URL=https://api.heygen.com/v2
```

---

## 🎭 **Avatare Disponibile (Exemple):**

| Avatar ID | Nume | Stil | Folosire |
|-----------|------|------|----------|
| `Josh_lite` | Josh - Business Professional | Formal | Prezentări corporate |
| `Anna_public` | Anna - Friendly Advisor | Casual | Customer support |
| `Monica_lite` | Monica - Expert | Professional | Training videos |
| `Eric_public` | Eric - Tech Presenter | Modern | Product demos |

**Lista completă:** https://app.heygen.com/avatars

---

## 🗣️ **Voice Cloning (Opțional):**

### **Pentru vocea lui Manole:**

1. **Înregistrează 2 minute** de vorbire clară
2. Upload pe HeyGen: **Settings → Voice Library**
3. Procesare: ~10 minute
4. Primești **Voice ID** (ex: `voice_manole_123`)
5. Folosește în API:
   ```json
   {
     "voice_id": "voice_manole_123",
     "script": "Bună ziua..."
   }
   ```

**Cost voice cloning:** $30 one-time (inclus în plan Business)

---

## 📡 **API Endpoints Implementate:**

### **1. Generează Video HeyGen:**
```http
POST /api/video/heygen/generate
Content-Type: multipart/form-data

script: "Bună ziua! Sunt avocat specialist în daune auto..."
avatar_id: "Josh_lite"
voice_id: "voice_manole_123" (optional)
style: "realistic"
quality: "high"
language: "ro"
```

**Response:**
```json
{
  "success": true,
  "video_id": "abc123",
  "status": "pending",
  "estimated_completion": "2025-09-30T19:00:00",
  "estimated_cost": 1.50,
  "check_status_url": "/api/video/heygen/status/abc123"
}
```

### **2. Check Status:**
```http
GET /api/video/heygen/status/{video_id}
```

**Response (când e gata):**
```json
{
  "success": true,
  "video_id": "abc123",
  "status": "completed",
  "video_url": "https://heygen.com/videos/abc123.mp4",
  "thumbnail_url": "https://heygen.com/thumbs/abc123.jpg",
  "duration": 30.5,
  "local_path": "generated_videos/heygen/heygen_video_abc123.mp4"
}
```

### **3. Listă Avatare:**
```http
GET /api/video/heygen/avatars
```

---

## 🎬 **Cum folosești în Admin Panel:**

### **Frontend Integration (deja pregătit):**

1. **Tab "Video Profesional AI"** în `VideoManagement.tsx`
2. User completează script
3. Selectează avatar, quality, style
4. Click **"Generează Video HeyGen"**
5. Polling automat pentru status
6. Download automat când e gata
7. Preview în modal

---

## 🔧 **Testing Local:**

### **Test 1: Generate Video**
```powershell
$headers = @{"Content-Type"="multipart/form-data"}
$body = @{
    script = "Bună ziua! Sunt specialist AutoPro Daune."
    style = "realistic"
    quality = "high"
    language = "ro"
}

Invoke-RestMethod -Uri "http://localhost:8001/api/video/heygen/generate" `
    -Method POST -Body $body
```

### **Test 2: Check Status**
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/api/video/heygen/status/abc123"
```

---

## ⚙️ **Configurare Avansată:**

### **Environment Variables Opționale:**

```bash
# Timeout pentru generare (default: 600s = 10 min)
HEYGEN_TIMEOUT=600

# Max retries pentru API calls
HEYGEN_MAX_RETRIES=3

# Cache pentru avatare
HEYGEN_AVATAR_CACHE_TTL=3600
```

---

## 📊 **Cost Estimation System:**

Sistemul calculează automat costul ÎNAINTE de generare:

```python
# În financial service
cost = duration_seconds * base_rate * avatar_multiplier * quality_multiplier

# Exemplu:
# 30s video cu avatar premium în 4K:
# 30 * $0.05 * 1.5 * 1.5 = $3.37
```

**Alertă automată** dacă costul depășește budget-ul setat!

---

## 🎯 **Next Steps După Setup:**

1. ✅ **Obține HeyGen API Key** (15 min)
2. ✅ **Adaugă în `.env`** file
3. ✅ **Restart backend** (`python -m uvicorn...`)
4. ✅ **Test din Admin Panel**
5. 🎙️ **Opțional: Voice clone** pentru Manole
6. 🎨 **Custom avatar** (dacă vrei)

---

## ❓ **Troubleshooting:**

### **Problem: API Key Invalid**
```
Error: HEYGEN_API_KEY nu este configurat
```
**Fix:** Verifică că key-ul e corect în `.env` și restart backend

### **Problem: Video generation failed**
```
Error: HeyGen API error: Insufficient credits
```
**Fix:** Upgrade plan sau add credits în HeyGen dashboard

### **Problem: Slow generation**
```
Status: pending după 5 minute
```
**Normal!** HeyGen ia 2-5 minute pentru 30s video high quality

---

## 📞 **Support HeyGen:**

- **Docs:** https://docs.heygen.com
- **API Reference:** https://docs.heygen.com/reference/api-overview
- **Support:** support@heygen.com
- **Discord:** https://discord.gg/heygen

---

## 🎉 **Ready to Go!**

După ce adaugi API key-ul, vei avea:
- ✅ Avatar vorbitor fotorealist
- ✅ Lip sync perfect în română
- ✅ Video HD/4K professional
- ✅ Download automat
- ✅ Cost tracking
- ✅ Integration completă în admin panel

**Cost estimat pentru demo:** $1-2/video (30-60 secunde)  
**Rezultat:** Video indistinguibil de unul filmat cu persoană reală! 🚀

---

**Generated:** 30 Septembrie 2025  
**By:** AutoPro Daune AI Assistant
