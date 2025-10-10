# 🎬 VIDEO GENERATION REAL - REQUIREMENTS & SETUP

**Data:** 10 Octombrie 2025  
**Scop:** Activare generare video REALĂ (nu mock)  
**Status:** ⚠️ **PARȚIAL GATA - 1 dependință critică lipsă**

---

## ✅ **CE AVEM DEJA CONFIGURAT**

### **1️⃣ API Keys - TOATE CONFIGURATE** ✅

```env
# Supabase (Database + Auth + Storage)
SUPABASE_URL=https://yfbhmbjtauhxgalvdfns.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... ✅

# ElevenLabs (Voice Cloning)
ELEVENLABS_API_KEY=62798d465549b18268cb163a5be9e0ec... ✅
ELEVENLABS_VOICE_ID=manole_voice ✅

# HeyGen (AI Avatar Video)
HEYGEN_API_KEY=81d606ae1d67497d8c677aceca982c23-1759246585 ✅
HEYGEN_BASE_URL=https://api.heygen.com/v2 ✅

# OpenAI (AI Features)
OPENAI_API_KEY=sk-proj-ZZDuRH1Wq1HAhn-QaE6mZ20axU... ✅

# Cloudflare R2 (CDN Storage)
R2_ACCOUNT_ID=026d4eb7409b0baea2767863f22a76c1 ✅
R2_ACCESS_KEY_ID=19899ebc1069a1575fadb26db3e357a3 ✅
R2_SECRET_ACCESS_KEY=9f74dd9018281f2a91579728922c49d0... ✅
R2_BUCKET_NAME=autoprodaune ✅

# TikTok API
TIKTOK_CLIENT_KEY=awna26k858tnrwwn ✅
TIKTOK_CLIENT_SECRET=u4J5JYbSD30WKFFYLUdPIwFiuqbhqzc5 ✅
```

**STATUS:** ✅ **TOATE API KEYS CONFIGURATE!**

---

### **2️⃣ Python Dependencies - TOATE INSTALATE** ✅

```
✅ Python: 3.13.5
✅ PIL/Pillow: 11.3.0
✅ OpenCV: 4.12.0
✅ NumPy: 2.2.6
✅ PyTorch: 2.7.1+cpu
```

**STATUS:** ✅ **TOATE BIBLIOTECILE PYTHON INSTALATE!**

---

### **3️⃣ Configuration Updates** ✅

**Fișier creat:** `services/api/.env`
```env
FAKE_MODE=false  # ✅ Generare reală activată!
USE_INTERNAL_VIDEO_ENGINE=true
LIPSYNC_BACKEND=sadtalker
```

**STATUS:** ✅ **CONFIGURARE COMPLETĂ!**

---

## ✅ **DEPENDINȚE COMPLETE - FFMPEG INSTALAT!** 🎉

### **FFmpeg 8.0 - INSTALAT CU SUCCES** ✅

**Instalat:** FFmpeg 8.0-full_build (via winget)  
**Verificat:** `ffmpeg -version` funcționează perfect!

**FFmpeg este necesar pentru:**
- Procesare video (encoding, decoding)
- Conversie audio (mp3 → wav)
- Concatenare clips
- Adăugare audio la video
- Redimensionare și crop
- Export în diferite formate

---

## 🛠️ **FIX: INSTALARE FFMPEG**

### **OPȚIUNEA 1: Chocolatey (Recomandat pentru Windows)**

```powershell
# Instalare Chocolatey (dacă nu e instalat)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalare FFmpeg
choco install ffmpeg -y

# Verificare
ffmpeg -version
```

### **OPȚIUNEA 2: Manual Download**

1. **Download:** https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
2. **Extract:** `C:\ffmpeg\`
3. **Add to PATH:**
   ```powershell
   $env:Path += ";C:\ffmpeg\bin"
   [Environment]::SetEnvironmentVariable("Path", $env:Path, "Machine")
   ```
4. **Verificare:**
   ```powershell
   ffmpeg -version
   ```

### **OPȚIUNEA 3: Winget (Windows 11)**

```powershell
winget install ffmpeg
```

---

## 📋 **VERIFICARE COMPLETĂ DUPĂ INSTALARE FFMPEG**

### **Checklist Final:**

```bash
# 1. Verificare FFmpeg
ffmpeg -version

# 2. Verificare API Keys
cd services/api
grep "FAKE_MODE" .env  # Should be: FAKE_MODE=false
grep "OPENAI_API_KEY" .env  # Should have real key
grep "ELEVENLABS_API_KEY" .env  # Should have real key
grep "HEYGEN_API_KEY" .env  # Should have real key

# 3. Restart Backend
# Stop backend (Ctrl+C)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 4. Test Video Generation
curl -X POST http://localhost:8001/api/advanced-video/generate \
  -H "Content-Type: application/json" \
  -d '{
    "script": "AutoPro Daune - Test video generation real",
    "avatar_type": "professional",
    "background_type": "office",
    "aspect_ratio": "portrait",
    "resolution": "1080p"
  }'

# 5. Verificare Job Processing
curl http://localhost:8001/api/advanced-video/jobs
```

---

## 🎯 **PENTRU GPT AGENT - TASK COMPLET**

### **TASK: Activare Video Generation Real**

**Status Actual:**
- ✅ API Keys: TOATE configurate
- ✅ Python deps: TOATE instalate
- ✅ .env: Creat cu FAKE_MODE=false
- ❌ FFmpeg: NU este instalat

**Pași pentru GPT:**

1. **Instalare FFmpeg (CRÍTICA):**
   ```powershell
   # Alegeți una din opțiuni:
   choco install ffmpeg -y
   # SAU
   winget install ffmpeg
   # SAU download manual + add to PATH
   ```

2. **Verificare instalare:**
   ```powershell
   ffmpeg -version
   # Ar trebui să afișeze: ffmpeg version N-XXX...
   ```

3. **Restart Backend:**
   ```powershell
   cd services/api
   # Stop procesul curent (Ctrl+C în terminal)
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

4. **Test Video Generation:**
   ```powershell
   # Din frontend sau cu curl
   curl -X POST http://localhost:8001/api/advanced-video/generate \
     -H "Content-Type: application/json" \
     -d '{"script": "Test", "avatar_type": "professional", ...}'
   ```

5. **Monitorizare Progres:**
   ```powershell
   # Watch logs în terminal backend
   # Ar trebui să vezi:
   # - TTS generation cu ElevenLabs
   # - Avatar processing cu PIL
   # - Video composition cu FFmpeg
   # - Upload la R2
   # - Job status: completed
   ```

6. **Verificare Rezultat:**
   ```powershell
   # Check generated videos
   curl http://localhost:8001/api/advanced-video/list-generated
   
   # Ar trebui să apară un video nou în listă
   # cu timestamp recent și preview_path
   ```

---

## ⚠️ **IMPORTANT NOTES**

### **Timp de Generare:**
- **FAKE_MODE:** Instant (mock response)
- **REAL MODE:** 2-15 minute depending on:
  - TTS generation: ~30-60 secunde (ElevenLabs API)
  - Avatar processing: ~1-2 minute (PIL + lip sync)
  - Video composition: ~30-90 secunde (FFmpeg)
  - Upload la R2: ~10-30 secunde

### **Costuri per Video:**
- ElevenLabs TTS: ~$0.30 (30 secunde audio)
- OpenAI (opcional): ~$0.01 (caption generation)
- R2 Storage: ~$0.015/GB (~$0.002 per video)
- **Total:** ~$0.31 per video

### **Limitări:**
- ElevenLabs: 10,000 caractere/lună free tier
- HeyGen: Poate avea limitări per API key
- R2: Storage costs după 10GB

---

## 🚀 **DUPĂ INSTALARE FFMPEG**

Sistemul va fi **100% COMPLET** pentru:
- ✅ Generare video profesionale cu avatars AI
- ✅ Text-to-Speech cu voce clonată (ElevenLabs)
- ✅ Lip sync realist (SadTalker/Wav2Lip)
- ✅ Background personalizat
- ✅ Export multiple formate (portrait/landscape/square)
- ✅ Upload automat la CDN (Cloudflare R2)
- ✅ Thumbnail generation
- ✅ Progress tracking în real-time

---

## 📋 **CHECKLIST FINAL PENTRU GPT**

- [ ] Instalare FFmpeg (choco/winget/manual)
- [ ] Verificare: `ffmpeg -version` funcționează
- [ ] Restart backend cu FAKE_MODE=false
- [ ] Test generare video prin frontend
- [ ] Verificare logs backend pentru progres
- [ ] Verificare video apare în listă după ~5-10 minute
- [ ] Test preview și download video
- [ ] Verificare upload la R2 bucket
- [ ] Update documentație cu rezultate

---

**READY FOR GPT AGENT - DOAR FFmpeg LIPSEȘTE! 🎯**
