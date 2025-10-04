# Phase 9 Quick Reference

## 🚀 Quick Start

### 1. Enable Features (Optional)
```bash
# Edit .env file
AI_ENABLE_WHISPER=true
AI_ENABLE_BROLL=true
AI_ENABLE_VECTOR_SEARCH=true
```

### 2. Install Dependencies (Optional)
```bash
# For Whisper auto-captions
pip install openai-whisper

# For vector embeddings (production)
pip install sentence-transformers
```

### 3. Apply Database Migration
```bash
psql "$SUPABASE_URL" -f services/api/database/video_phase9.sql
```

### 4. Start API
```bash
cd services/api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

## 📡 API Endpoints

### Health Check
```bash
GET /api/video/ai/health
```

### Get Video Insights
```bash
GET /api/video/ai/insights/{job_id}
```

### Search Similar Videos
```bash
POST /api/video/ai/search/similar
{
  "query": "asigurari auto",
  "min_score": 0.7,
  "limit": 10
}
```

## 🔧 Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_ENABLE_WHISPER` | false | Auto-captions with Whisper |
| `WHISPER_BIN` | whisper | Whisper binary path |
| `WHISPER_MODEL` | base | Model size (tiny/base/small/medium/large) |
| `AI_CAPTIONS_LANG` | ro | Caption language |
| `AI_ENABLE_BROLL` | false | B-roll auto-injection |
| `BROLL_RULES_JSON` | services/api/.../broll_rules.json | B-roll rules file |
| `AI_ENABLE_VECTOR_SEARCH` | false | Semantic search |
| `AI_VECTOR_DIM` | 384 | Embedding dimension |

## 📁 Project Structure

```
services/api/app/
├── routes/
│   └── video_ai.py              # NEW: AI endpoints
├── services/
│   ├── whisper_captions.py      # NEW: Auto-captions
│   ├── broll_injector.py        # NEW: B-roll overlay
│   ├── vector_store.py          # NEW: Semantic search
│   ├── tagging_service.py       # NEW: Content tagging
│   ├── scene_detect.py          # NEW: Scene detection
│   ├── job_repo_supabase.py     # NEW: DB accessor
│   └── video_engine_lipsync.py  # MODIFIED: Phase 9 hook
├── templates/
│   └── broll_rules.json         # NEW: B-roll config
└── database/
    └── video_phase9.sql         # NEW: DB schema
```

## 🎬 Video Pipeline Flow

```
1. TTS Generation (ElevenLabs)
         ↓
2. Lip-sync (SadTalker/Wav2Lip)
         ↓
3. Phase 9 Enhancement ← YOU ARE HERE
   ├─ Whisper Captions (if enabled)
   ├─ Content Tagging
   ├─ Scene Detection
   └─ B-roll Injection (if enabled)
         ↓
4. Video Composition
         ↓
5. Storage & Delivery
```

## 🧪 Testing Commands

### Test with Flags OFF (default)
```powershell
# Should work exactly as before
curl -X POST http://127.0.0.1:8001/api/video/video/heygen/generate `
  -H "Content-Type: application/json" `
  -d '{"script":"Test","avatar_image_url":"https://..."}'
```

### Test with Whisper ON
```powershell
$env:AI_ENABLE_WHISPER="true"
# Generate video - check logs for Whisper execution
```

### Test with B-roll ON
```powershell
$env:AI_ENABLE_BROLL="true"
# Video with tag "asigurari" will get office.mp4 overlay
```

### Test AI Endpoints
```bash
# Health
curl http://127.0.0.1:8001/api/video/ai/health

# Insights
curl http://127.0.0.1:8001/api/video/ai/insights/<job_id>

# Search
curl -X POST http://127.0.0.1:8001/api/video/ai/search/similar \
  -H "Content-Type: application/json" \
  -d '{"query":"test","limit":5}'
```

## 🐛 Troubleshooting

### Whisper not working
```bash
# Check binary
which whisper

# Install if missing
pip install openai-whisper

# Test manually
whisper --help
```

### B-roll not appearing
1. Check `AI_ENABLE_BROLL=true`
2. Verify asset paths in `broll_rules.json` exist
3. Check script contains matching tags (e.g., "asigurari")
4. Review logs: `services/api/app/services/broll_injector.py`

### Vector search returns empty
1. Check `AI_ENABLE_VECTOR_SEARCH=true`
2. Run migration: `video_phase9.sql`
3. Verify pgvector extension installed
4. Check embeddings exist in `video_insights` table

### Database errors
```bash
# Check tables exist
psql "$SUPABASE_URL" -c "\dt video_*"

# Re-run migration
psql "$SUPABASE_URL" -f services/api/database/video_phase9.sql
```

## 📊 Database Tables

### video_jobs
- Job tracking and status
- Links to insights and captions

### video_insights
- `tags` - Content tags (text[])
- `scene_cuts` - Timestamps (float[])
- `vector_embedding` - Semantic vector (vector(384))
- `metadata` - Additional data (jsonb)

### video_captions
- `srt_url` - Caption file path
- `text_content` - Full transcript
- `lang` - Language code

## 🎯 B-roll Rules Format

```json
{
  "rules": [
    {
      "when_tag": "asigurari",
      "asset_path": "assets/broll/office.mp4",
      "start_offset": 0.0,
      "duration": 3.5,
      "opacity": 1.0,
      "track": 2
    }
  ]
}
```

**Fields:**
- `when_tag` - Tag that triggers this B-roll
- `asset_path` - Path to video file
- `start_offset` - Delay from scene start (seconds)
- `duration` - B-roll length (seconds)
- `opacity` - Transparency (0.0-1.0)
- `track` - Video layer number

## 📝 Logs

Watch for Phase 9 activity:
```bash
tail -f logs/api.log | grep -E "(Whisper|B-roll|Phase 9)"
```

Key log messages:
- `Whisper captions enabled: ...`
- `Added B-roll layer: tag=...`
- `Phase 9 enhancements: {...}`
- `Generated Whisper captions for job ...`

## 🔒 Security Notes

- Whisper runs locally (no API keys needed)
- B-roll assets must exist on filesystem
- Feature flags prevent accidental activation
- Database migrations are idempotent

## 📚 Further Reading

- [OpenAI Whisper Docs](https://github.com/openai/whisper)
- [pgvector Extension](https://github.com/pgvector/pgvector)
- [FFmpeg Scene Detection](https://ffmpeg.org/ffmpeg-filters.html#select_002c-aselect)

---

**Phase 9 Ready!** All features are optional and default OFF. Turn on when ready. 🎉
