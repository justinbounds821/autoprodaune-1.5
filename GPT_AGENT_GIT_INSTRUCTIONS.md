# Git Instructions for GPT Agent - CI/CD Complete
**Date**: 2025-10-28
**Branch**: cursor/gather-project-architecture-details-for-refactoring-a309

---

## ✅ STATUS: ALL YOUR PATCHES APPLIED

Toate patch-urile sugerate de tine au fost aplicate și testate:

1. ✅ **ci-cd.yml** - Matrix strategy cu fail-fast: false, trigger pe cursor/**
2. ✅ **smoke-tests.yml** - Trigger pe cursor/**, workflow_dispatch
3. ✅ **Dockerfiles** - Multi-stage cu common pentru toate 10 serviciile
4. ✅ **.env.example** - Config completă cu toate variabilele
5. ✅ **celery_config.py** - Redis DB0 (broker) + DB1 (results)
6. ✅ **prometheus.yml** - Toate 10 targets formatate corect

---

## 🎯 CE AI DE VERIFICAT PE GIT

### 1. Check Remote Branch Status

```bash
# Vezi ultimele commit-uri
git log origin/cursor/gather-project-architecture-details-for-refactoring-a309 --oneline -10

# Expected output:
# d9e1384 - docs: Add CI/CD fixes verification report
# ebbc48a - fix: CI/CD workflow Docker builds and smoke tests
# c976d27 - feat: Add GPT agent context response documentation
```

### 2. Verifică Workflow Files

**Path**: `.github/workflows/ci-cd.yml`

**Key lines să verifici:**
```yaml
name: AutoPro Daune CI/CD Pipeline (Microservices + GHCR)

on:
  push:
    branches: [ main, develop, cursor/** ]  # ✅ cursor/** added

strategy:
  fail-fast: false  # ✅ Added
  matrix:
    service: [lead-service, video-service, ...]  # ✅ 10 services

with:
  context: autopro_refactor_full_connected  # ✅ Fixed
  file: autopro_refactor_full_connected/microservices/${{ matrix.service }}/Dockerfile  # ✅ Fixed
```

**Path**: `.github/workflows/smoke-tests.yml`

**Key lines:**
```yaml
on:
  workflow_dispatch:  # ✅ Manual trigger
  push:
    branches: [main, develop, cursor/**]  # ✅ cursor/** added
```

### 3. Verifică Dockerfiles Multi-Stage

**Oricare serviciu** (ex: lead-service):

```bash
cd autopro_refactor_full_connected/microservices/lead-service
cat Dockerfile | head -15
```

**Expected:**
```dockerfile
# Stage 1: Build common library
FROM python:3.11-slim AS common
WORKDIR /autopro-common
COPY ../../autopro-common/ /autopro-common/
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Service
FROM python:3.11-slim
WORKDIR /app

# Copy common library from stage 1
COPY --from=common /autopro-common /usr/local/lib/python3.11/site-packages/autopro_common
```

✅ **Toate 10 serviciile au acest pattern**

### 4. Verifică Celery Config

**Path**: `autopro_refactor_full_connected/microservices/automation-service/app/celery_config.py`

**Expected:**
```python
celery_app.conf.update(
    broker_url=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    result_backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
    task_serializer="json",
    ...
)
```

### 5. Verifică .env.example

**Path**: `autopro_refactor_full_connected/.env.example`

**Should contain:**
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/autopro
REDIS_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
SUPABASE_URL=...
GITHUB_TOKEN=...
LINEAR_API_KEY=...
```

### 6. Verifică Prometheus Config

**Path**: `autopro_refactor_full_connected/monitoring/prometheus.yml`

**Expected targets (multi-line):**
```yaml
static_configs:
  - targets:
    - lead-service:8001
    - video-service:8002
    - social-service:8003
    - financial-service:8004
    - referral-service:8005
    - automation-service:8006
    - notification-service:8007
    - analytics-service:8008
    - whatsapp-service:8009
    - mcp-service:8010
```

---

## 🚀 COMENZI PENTRU VERIFICARE GIT

### Option 1: Web Interface (GitHub)

1. Go to: https://github.com/justinbounds821/autoprodaune-1.5
2. Switch to branch: `cursor/gather-project-architecture-details-for-refactoring-a309`
3. Navigate to `.github/workflows/ci-cd.yml`
4. Check lines 1-10 (name + on.push.branches)
5. Check lines 220-240 (strategy.fail-fast + matrix)

### Option 2: gh CLI

```bash
# View ci-cd.yml on remote branch
gh api repos/justinbounds821/autoprodaune-1.5/contents/.github/workflows/ci-cd.yml?ref=cursor/gather-project-architecture-details-for-refactoring-a309 \
  | jq -r '.content' | base64 -d | head -30

# View smoke-tests.yml
gh api repos/justinbounds821/autoprodaune-1.5/contents/.github/workflows/smoke-tests.yml?ref=cursor/gather-project-architecture-details-for-refactoring-a309 \
  | jq -r '.content' | base64 -d
```

### Option 3: Git Clone (Full verification)

```bash
# Clone repo
git clone https://github.com/justinbounds821/autoprodaune-1.5
cd autoprodaune-1.5

# Checkout branch
git checkout cursor/gather-project-architecture-details-for-refactoring-a309

# Verify files
ls -la .github/workflows/
cat .github/workflows/ci-cd.yml | grep -A 5 "strategy:"
cat .github/workflows/smoke-tests.yml | head -15

# Verify Dockerfiles
for svc in autopro_refactor_full_connected/microservices/*/; do
  echo "=== $svc ==="
  head -5 "$svc/Dockerfile" | grep "AS common"
done

# Verify .env.example
cat autopro_refactor_full_connected/.env.example | grep -E "(DATABASE_URL|CELERY_RESULT_BACKEND)"

# Verify prometheus
cat autopro_refactor_full_connected/monitoring/prometheus.yml | grep -A 15 "targets:"
```

---

## 🎯 CE TREBUIE SĂ VALIDEZI (CHECKLIST)

### Workflow Files
- [ ] ci-cd.yml name include "(Microservices + GHCR)"
- [ ] Push trigger include `cursor/**`
- [ ] Strategy has `fail-fast: false`
- [ ] Matrix lists all 10 services
- [ ] Context is `autopro_refactor_full_connected`
- [ ] File path is `autopro_refactor_full_connected/microservices/${{ matrix.service }}/Dockerfile`
- [ ] Test job installs deps for all services
- [ ] Build trigger is main OR develop

### Smoke Tests
- [ ] smoke-tests.yml exists
- [ ] Has workflow_dispatch
- [ ] Triggers on cursor/**
- [ ] Tests lead-service:8001 and mcp-service:8010
- [ ] Dumps logs on failure

### Dockerfiles
- [ ] All 10 have "AS common" stage
- [ ] All 10 have COPY --from=common
- [ ] video-service includes ffmpeg install

### Config Files
- [ ] .env.example exists with all vars
- [ ] celery_config.py exists in automation-service
- [ ] prometheus.yml has all 10 targets formatted correctly

---

## 📊 EXPECTED GITHUB ACTIONS BEHAVIOR

### On Push to `cursor/gather-project-architecture-details-for-refactoring-a309`:

**Workflows that should trigger:**

1. ✅ **CI/CD Pipeline** (ci-cd.yml)
   - test-backend (with all deps)
   - test-frontend
   - security-scan
   - lint
   - build-and-push (if main/develop)

2. ✅ **Smoke Tests** (smoke-tests.yml)
   - Build all services
   - Start core stack
   - Health checks
   - Logs on failure

**What should NOT fail:**
- ❌ "stage name common not found"
- ❌ "failed to read dockerfile"
- ❌ "module not found" errors in tests
- ❌ Health check failures (after 20s wait)

---

## 🔍 DEBUG COMMANDS (If Actions Fail)

### Check Workflow Runs
```bash
gh run list --branch cursor/gather-project-architecture-details-for-refactoring-a309 --limit 5

# View specific run
gh run view <run-id> --log
```

### Test Docker Build Locally
```bash
cd autopro_refactor_full_connected

# Test lead-service build
docker build -f microservices/lead-service/Dockerfile . -t test/lead:local

# Should succeed with common stage
```

### Test Smoke Tests Locally
```bash
cd autopro_refactor_full_connected

# Build
docker-compose -f docker-compose.yml -f docker-compose.override.yml build

# Up
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d lead-service mcp-service redis postgres

# Wait
sleep 20

# Test
curl -f http://localhost:8001/health
curl -f http://localhost:8010/health

# Should both return 200 OK
```

---

## 📝 SUMMARY FOR GPT AGENT

**Branch**: `cursor/gather-project-architecture-details-for-refactoring-a309`
**Status**: ✅ All patches applied
**Last commit**: d9e1384 (docs: Add CI/CD fixes verification report)
**Total commits on branch**: 6

**Changes applied:**
1. ci-cd.yml - fail-fast false, cursor/** trigger, 10 services matrix
2. smoke-tests.yml - new workflow with docker-compose tests
3. All Dockerfiles - multi-stage with common
4. .env.example - complete config template
5. celery_config.py - Redis DB0 + DB1 separation
6. prometheus.yml - all 10 targets formatted

**Next Actions:**
1. Review changes on GitHub web interface or via gh CLI
2. Verify all checklist items above
3. Wait for GitHub Actions to run (or trigger manually via workflow_dispatch)
4. If all green, approve PR to main

**Key verification points:**
- Workflows should trigger on cursor/** branches ✅
- Docker builds should succeed with common stage ✅
- Smoke tests should pass health checks ✅
- GHCR push should work on main/develop ✅

---

## 🔗 Quick Links

**Branch on GitHub:**
https://github.com/justinbounds821/autoprodaune-1.5/tree/cursor/gather-project-architecture-details-for-refactoring-a309

**Workflows:**
- https://github.com/justinbounds821/autoprodaune-1.5/blob/cursor/gather-project-architecture-details-for-refactoring-a309/.github/workflows/ci-cd.yml
- https://github.com/justinbounds821/autoprodaune-1.5/blob/cursor/gather-project-architecture-details-for-refactoring-a309/.github/workflows/smoke-tests.yml

**Actions runs:**
https://github.com/justinbounds821/autoprodaune-1.5/actions?query=branch%3Acursor%2Fgather-project-architecture-details-for-refactoring-a309

---

**Generated**: 2025-10-28 21:00 UTC
**Status**: ✅ READY FOR VERIFICATION
