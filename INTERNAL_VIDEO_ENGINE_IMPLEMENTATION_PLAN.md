# INTERNAL VIDEO ENGINE - IMPLEMENTATION PLAN

## 🎯 ANALIZA PROIECTULUI ACTUAL

### **Structura existentă:**
- ✅ **FastAPI app** în `services/api/app/main.py`
- ✅ **Router system** modular în `services/api/app/routes/`
- ✅ **Services** organizate în `services/api/app/services/`
- ✅ **Models** în `services/api/app/models/`
- ✅ **Video infrastructure** existentă în `services/video/`
- ✅ **HeyGen integration** deja implementată în `routes/video.py`

### **Principii respectate:**
- ✅ **SRP**: Fiecare fișier are o responsabilitate clară
- ✅ **Modular**: Routeri separați, servicii separate
- ✅ **OOP-first**: Clase și modele structurate
- ✅ **Fișiere < 500 linii**: Toate fișierele respectă limita

## 🚀 PLAN DE IMPLEMENTARE ORGANIZAT

### **FAZA 1: Environment & Dependencies**
1. **Environment variables** - adăugare în `.env`
2. **Dependencies** - instalare prin script PowerShell
3. **Third-party modules** - SadTalker și Wav2Lip

### **FAZA 2: Models & Schemas**
1. **Video models** - extindere `models/video_models.py`
2. **DTO consistency** - păstrare contracte existente

### **FAZA 3: Core Services**
1. **Job store** - `services/job_store.py` (SRP)
2. **TTS service** - `services/voice_elevenlabs.py` (SRP)
3. **Lip-sync engine** - `services/video_engine_lipsync.py` (SRP)

### **FAZA 4: API Integration**
1. **Internal video router** - `routes/video_internal_alias.py`
2. **Router registration** - în `main.py`
3. **Route compatibility** - păstrare `/api/video/video/heygen/*`

### **FAZA 5: Testing & Validation**
1. **E2E tests** - PowerShell scripts
2. **Integration tests** - cu sistemul existent
3. **Performance validation** - timpul de procesare

## 📁 FIȘIERE DE CREAT/MODIFICAT

### **Nou:**
- `services/api/app/models/video_models.py` (extindere)
- `services/api/app/services/job_store.py`
- `services/api/app/services/voice_elevenlabs.py`
- `services/api/app/services/video_engine_lipsync.py`
- `services/api/app/routes/video_internal_alias.py`
- `third_party/SadTalker/` (submodule)
- `third_party/Wav2Lip/` (submodule)

### **Modificat:**
- `.env` (environment variables)
- `services/api/app/main.py` (router registration)
- `requirements.txt` (dependencies)

### **Scripts:**
- `scripts/install-internal-video-engine.ps1`
- `scripts/test-internal-video-engine.ps1`

## 🔧 COMPATIBILITATE

### **UI/Admin rămân neschimbate:**
- ✅ Rutele `/api/video/video/heygen/*` se păstrează
- ✅ Contractele JSON rămân identice
- ✅ Frontend nu necesită modificări

### **Backward compatibility:**
- ✅ HeyGen rămâne funcțional când `USE_INTERNAL_VIDEO_ENGINE=false`
- ✅ Fallback la HeyGen dacă engine-ul intern eșuează
- ✅ Environment-based switching

## 🎯 BENEFICII

1. **Cost reduction** - Nu mai depindem de HeyGen API
2. **Quality control** - Control total asupra procesului
3. **Customization** - Avatare și stiluri proprii
4. **Performance** - Procesare locală, fără network latency
5. **Privacy** - Datele rămân în infrastructura noastră

## 📋 CHECKLIST IMPLEMENTARE

- [ ] **FAZA 1**: Environment & Dependencies
- [ ] **FAZA 2**: Models & Schemas  
- [ ] **FAZA 3**: Core Services
- [ ] **FAZA 4**: API Integration
- [ ] **FAZA 5**: Testing & Validation

**Gata pentru implementare! 🚀**
