# Message for GPT Agent

## Status Actual

✅ Arhivă v1 generată: `autopro_refactor_full_connected.zip` (46KB, 109 fișiere)
⚠️ Cod generic/minimal - TREBUIE perfecționat cu cod real din repo

---

## Documentație Completă

**Citește:** `/workspace/DOCUMENTATION_FOR_GPT_AGENT.md`

Conține:
- Cod real din 6+ servicii production (`/workspace/services/api/app/services/`)
- Pattern-uri actuale (Supabase sync, Celery, HeyGen, OAuth)
- Exemple concrete de refactorizare
- Checklist complet pentru regenerare

---

## Task

**Regenerează arhiva cu cod real** folosind documentația furnizată.

**Modificări cheie:**

1. **autopro-common/db.py** → Supabase client (nu SQLAlchemy async)
2. **video-service** → HeyGen + VideoOrchestrator real
3. **automation-service** → Celery tasks cu logică reală
4. **social-service** → TikTok/Instagram clients
5. **Toate serviciile** → Dependency injection corect

---

## Output Așteptat

```
autopro_refactor_full_connected_v2.zip
Mărime: 200-500KB (nu 46KB)
Fișiere: 150-200 (cu cod real)
```

---

## Comenzi Validare

```bash
# Test structure
unzip -l autopro_refactor_full_connected_v2.zip | grep -E "video_orchestrator|heygen|celery"

# Verifică dimensiune
ls -lh autopro_refactor_full_connected_v2.zip

# Test local
cd autopro_refactor_full_connected
docker-compose up -d redis
cd microservices/video-service && pytest tests/
```

---

## GO! 🚀

Citește documentația și regenerează arhiva **ACUM**.
