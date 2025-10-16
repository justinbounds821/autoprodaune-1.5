# 🚀 Tutorial Complet: MCP System cu GPT Developer Mode

**Ghid Practic pentru Proiectele AutoPro**

---

## 📋 Cuprins

1. [Setup Inițial](#1-setup-inițial)
2. [Pornire Sistem](#2-pornire-sistem)
3. [Configurare GPT Developer Mode](#3-configurare-gpt-developer-mode)
4. [Utilizare Maximă - Scenarii Practice](#4-utilizare-maximă---scenarii-practice)
5. [Workflow-uri Avansate](#5-workflow-uri-avansate)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Setup Inițial

### 1.1. Verificare Dependințe

```powershell
# Python 3.10+
python --version

# Node.js 18+
node --version

# Git
git --version
```

### 1.2. Instalare Dependencies

**Python (mcp_server):**
```powershell
cd mcp_server
pip install -r requirements.txt
```

**Node.js (orchestrator):**
```powershell
cd mcp-orchestrator
npm install
```

### 1.3. Configurare Environment Variables

Creează fișier `.env` în root:

```env
# === MCP Server ===
MCP_SERVER_PORT=8012
MCP_SERVER_HOST=127.0.0.1

# === Orchestrator ===
ORCHESTRATOR_URL=http://127.0.0.1:3030
ORCHESTRATOR_HTTP_PORT=3030

# === Project Paths ===
PROJECT_PATH=C:\Users\YourUser\Desktop\autoprodaune-1.5
FRONTEND_PATH=C:\Users\YourUser\Desktop\autoprodaune-1.5\02_FRONTEND_UI_CLEAN

# === Linear (Task Management) ===
LINEAR_API_KEY=lin_api_xxxxxxxxxxxxxxxxxxxxxx
LINEAR_TEAM_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# === GitHub ===
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=owner/repo-name
GITHUB_BRANCH=cursor/implementare-complete-sistem-mcp-c27b

# === Supabase (Database) ===
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# === OpenAI (pentru GPT) ===
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx

# === Optional: Deployment ===
VERCEL_TOKEN=xxxxxxxxxxxxxx
RAILWAY_TOKEN=xxxxxxxxxxxxxx
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

**Important**: Copiază `.env` și în directoarele `mcp_server/` și `mcp-orchestrator/`

---

## 2. Pornire Sistem

### 2.1. Pornire Automată (Recomandat)

```powershell
.\START_SYSTEM.ps1
```

**Output Așteptat:**
```
==================================================
    MCP System Startup
==================================================
[+] Starting MCP Orchestrator...
[+] Orchestrator PID: 12345
[+] Waiting for orchestrator...
[+] Orchestrator is ready!

[+] Starting MCP Server...
[+] MCP Server PID: 12346
[+] Waiting for MCP Server...
[+] MCP Server is ready!

==================================================
    System Health Check
==================================================
[+] Orchestrator Health: OK
[+] MCP Server Health: OK
[+] System is ready!
```

### 2.2. Pornire Manuală (Debugging)

**Terminal 1 - Orchestrator:**
```powershell
cd mcp-orchestrator
node dist/http-bridge.js
```

**Terminal 2 - MCP Server:**
```powershell
cd mcp_server
python main.py
```

### 2.3. Verificare Status

```powershell
# Orchestrator
curl http://127.0.0.1:3030/health

# MCP Server
curl http://127.0.0.1:8012/health

# System Health (End-to-End)
curl http://127.0.0.1:8012/mcp/tools/system/health
```

**Output OK:**
```json
{
  "ok": true,
  "overall_status": "healthy",
  "services": {
    "backend": {"status": "healthy"},
    "linear": {"status": "healthy", "user": "Your Name"},
    "github": {"status": "healthy", "user": "yourusername"},
    "supabase": {"status": "healthy"}
  }
}
```

---

## 3. Configurare GPT Developer Mode

### 3.1. Adaugă Custom Action în ChatGPT

1. **Deschide ChatGPT** → Settings → Beta Features → Actions
2. **Create New Action**
3. **Import OpenAPI Schema:**

```powershell
# Accesează schema
curl http://127.0.0.1:8012/openapi.json > mcp_openapi.json
```

4. **Sau folosește schema direct:**

```yaml
openapi: 3.0.0
info:
  title: AutoPro MCP Server
  version: 0.2.0
  description: |
    MCP Server for AutoPro project orchestration.
    Use /mcp/tools/gpt/* endpoints for optimal GPT integration.
servers:
  - url: http://127.0.0.1:8012
paths:
  /mcp/tools/gpt/orchestrate:
    post:
      summary: Orchestrate Complete Workflow
      description: |
        Create and execute multi-agent workflow for complex tasks.
        Returns: workflow_id, tasks, agent_prompts
      operationId: gptOrchestrate
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [command, context]
              properties:
                command:
                  type: string
                  description: High-level command (e.g., "FIX ALL CRITICAL BUGS")
                context:
                  type: object
                  description: Project context
                options:
                  type: object
                  description: Orchestration options
      responses:
        '200':
          description: Workflow created successfully

  /mcp/tools/gpt/create_task:
    post:
      summary: Create Linear Task
      description: Create task in Linear project management
      operationId: gptCreateTask
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [title]
              properties:
                title:
                  type: string
                description:
                  type: string
                priority:
                  type: integer
      responses:
        '200':
          description: Task created

  /mcp/tools/gpt/status:
    get:
      summary: Get System Status
      description: Get comprehensive system health
      operationId: gptStatus
      responses:
        '200':
          description: System status

  /mcp/tools/gpt/test:
    post:
      summary: Run Test
      description: Execute browser or API test
      operationId: gptTest
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [test_type, config]
              properties:
                test_type:
                  type: string
                  enum: [browser, api]
                config:
                  type: object
      responses:
        '200':
          description: Test completed
```

5. **Authentication**: None (local development)

### 3.2. Configurare în Cursor

**File: `.cursorrules`**

```markdown
# AutoPro MCP Integration

## MCP Server Endpoints

Base URL: http://127.0.0.1:8012

### Available Actions:

1. **Orchestrate Workflow**
   POST /mcp/tools/gpt/orchestrate
   - Create multi-agent workflow
   - Returns: workflow_id, tasks, agent_prompts

2. **Create Task**
   POST /mcp/tools/gpt/create_task
   - Create Linear task
   - Returns: task_id, url

3. **System Status**
   GET /mcp/tools/gpt/status
   - Check all services health
   - Returns: overall_status, services

4. **Run Test**
   POST /mcp/tools/gpt/test
   - Execute browser or API test
   - Returns: test results

## Usage Pattern:

When user requests complex work:
1. Call /mcp/tools/gpt/orchestrate to create plan
2. Execute agent prompts sequentially
3. Create tasks in Linear for tracking
4. Run tests to verify
5. Check status for health
```

---

## 4. Utilizare Maximă - Scenarii Practice

### 4.1. Scenario: Fix Critical Bugs în Backend

**Prompt GPT:**
```
Folosind MCP orchestrate, creează un plan complet pentru:
"FIX AND TEST ALL CRITICAL BACKEND ISSUES"

Context:
- Project: AutoPro Daune
- Backend: FastAPI services/api/
- Database: Supabase
- Current branch: cursor/fix-backend-critical
```

**Request GPT va face:**
```json
POST http://127.0.0.1:8012/mcp/tools/gpt/orchestrate
{
  "command": "FIX AND TEST ALL CRITICAL BACKEND ISSUES",
  "context": {
    "project": "AutoPro Daune",
    "backend": "services/api/",
    "database": "Supabase",
    "branch": "cursor/fix-backend-critical"
  },
  "options": {
    "create_linear_tasks": true,
    "create_github_issues": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "workflow_id": "WORKFLOW-1702345678",
  "summary": "Created 5 tasks across 3 agents",
  "tasks": [
    {
      "linear_id": "AUT-123",
      "title": "Fix authentication endpoint",
      "agent": "claude",
      "status": "pending"
    },
    {
      "linear_id": "AUT-124",
      "title": "Test API endpoints",
      "agent": "claude",
      "status": "pending"
    }
  ],
  "agent_prompts": [
    {
      "agent": "claude",
      "task_id": "AUT-123",
      "prompt": "=== CLAUDE AGENT ===\nTASK: AUT-123\nTITLE: Fix authentication endpoint\n..."
    }
  ],
  "next_steps": "Execute agent prompts and report back"
}
```

**Acțiune GPT:**
1. Primește prompt-urile pentru fiecare task
2. Execută task-urile secvențial
3. Raportează progres

### 4.2. Scenario: Deploy Frontend la Vercel

**Prompt GPT:**
```
Orchestrate deployment pentru frontend:
1. Test toate componente React
2. Build production
3. Deploy la Vercel
4. Verifică în Supabase că deployment e înregistrat
```

**Request:**
```json
POST /mcp/tools/gpt/orchestrate
{
  "command": "DEPLOY FRONTEND TO VERCEL WITH TESTS",
  "context": {
    "project": "AutoPro Daune",
    "frontend_path": "02_FRONTEND_UI_CLEAN",
    "deployment_target": "vercel"
  }
}
```

**Workflow Automat:**
1. **Task 1**: Test React components (browser_test)
2. **Task 2**: Build production (github_commit)
3. **Task 3**: Deploy Vercel
4. **Task 4**: Verify in Supabase (supabase_verify_fix)

### 4.3. Scenario: Create Feature Epic în Linear

**Prompt GPT:**
```
Creează un epic complet în Linear pentru:
"Implementare sistem de notificări push"

Include:
- Backend endpoints (FastAPI)
- Frontend UI (React)
- Database schema (Supabase)
- Tests (E2E)
```

**Request:**
```json
POST /mcp/tools/gpt/orchestrate
{
  "command": "CREATE FEATURE EPIC: Push Notifications System",
  "context": {
    "feature": "push_notifications",
    "components": ["backend", "frontend", "database", "tests"]
  },
  "options": {
    "create_linear_tasks": true,
    "generate_report": true
  }
}
```

**Output:**
- Epic creat în Linear: "Push Notifications - Sprint 2024-10"
- 8 task-uri create:
  - Backend API endpoints (AUT-130)
  - Supabase schema migration (AUT-131)
  - React notification component (AUT-132)
  - FCM integration (AUT-133)
  - E2E tests (AUT-134)
  - Documentation (AUT-135)
  - Deployment (AUT-136)
  - Monitoring (AUT-137)

### 4.4. Scenario: E2E Testing Complete

**Prompt GPT:**
```
Rulează teste complete E2E pentru:
1. Login flow
2. Lead creation
3. Financial operations
4. Video generation

Verifică în Supabase că datele sunt corecte.
```

**Request 1: Browser Test**
```json
POST /mcp/tools/gpt/test
{
  "test_type": "browser",
  "config": {
    "test_name": "Complete User Flow",
    "url": "http://localhost:5173",
    "steps": [
      {"action": "goto", "value": "http://localhost:5173"},
      {"action": "fill", "selector": "#email", "value": "test@example.com"},
      {"action": "fill", "selector": "#password", "value": "test123"},
      {"action": "click", "selector": "button[type=submit]"},
      {"action": "wait", "selector": ".dashboard", "timeout": 5000},
      {"action": "assert", "selector": ".user-name", "value": "Test User"}
    ],
    "verify_in_db": {
      "table": "users",
      "expected": {"email": "test@example.com"}
    }
  }
}
```

**Request 2: API Test**
```json
POST /mcp/tools/gpt/test
{
  "test_type": "api",
  "config": {
    "method": "POST",
    "url": "http://127.0.0.1:8011/api/leads",
    "body": {
      "name": "Test Lead",
      "phone": "0712345678",
      "email": "lead@test.com"
    },
    "expected_status": 201,
    "expected_response": {
      "id": "{{uuid}}",
      "status": "new"
    }
  }
}
```

### 4.5. Scenario: Debug Production Issue

**Prompt GPT:**
```
Un user raportează eroare 500 la /api/financial/invoices.
Investighează și repară:
1. Check logs în Supabase
2. Test endpoint local
3. Fix issue
4. Deploy fix
5. Verify în production
```

**Workflow Automat:**

**Step 1: Check Supabase Logs**
```json
POST /mcp/tools/supabase/query
{
  "table": "logs",
  "operation": "select",
  "filters": {
    "endpoint": "/api/financial/invoices",
    "status_code": 500
  },
  "limit": 10
}
```

**Step 2: Test Local API**
```json
POST /mcp/tools/gpt/test
{
  "test_type": "api",
  "config": {
    "method": "GET",
    "url": "http://127.0.0.1:8011/api/financial/invoices",
    "expected_status": 200
  }
}
```

**Step 3: Create Fix Task**
```json
POST /mcp/tools/gpt/create_task
{
  "title": "FIX: 500 error on /api/financial/invoices",
  "description": "Error details: [from logs]\nSteps to reproduce: ...",
  "priority": 1,
  "labels": ["bug", "critical", "backend"]
}
```

**Step 4: Commit Fix**
```json
POST /mcp/tools/github/commit
{
  "message": "fix: resolve 500 error in financial invoices endpoint",
  "files": ["services/api/app/routes/financial.py"],
  "linear_task_id": "AUT-150"
}
```

**Step 5: Verify Fix**
```json
POST /mcp/tools/supabase/verify
{
  "table": "logs",
  "expected": {
    "endpoint": "/api/financial/invoices",
    "status_code": 200
  },
  "description": "Verify fix is working in production"
}
```

---

## 5. Workflow-uri Avansate

### 5.1. Multi-Agent Collaboration

**Scenario**: Implementare feature complex cu 3 agenți

**Prompt GPT:**
```
Orchestrate feature "Real-time Chat" cu divizare:
- Agent 1 (Backend): WebSocket server + Redis
- Agent 2 (Frontend): React chat UI + real-time updates
- Agent 3 (Testing): E2E tests + load testing
```

**Workflow:**
1. GPT apelează `/mcp/tools/gpt/orchestrate`
2. Primește 3 agent prompts
3. Execută parallel:
   - Agent 1: Implementează backend
   - Agent 2: Implementează frontend
   - Agent 3: Creează teste
4. Sincronizare prin Linear tasks
5. Final integration test

### 5.2. Continuous Deployment Pipeline

**Setup:**

```json
POST /mcp/tools/gpt/orchestrate
{
  "command": "SETUP CI/CD PIPELINE",
  "context": {
    "project": "AutoPro Daune",
    "stages": ["test", "build", "deploy", "verify"]
  },
  "options": {
    "auto_execute": true
  }
}
```

**Pipeline Steps:**
1. **Test**: Run all tests (browser + API)
2. **Build**: Compile frontend + backend
3. **Deploy**: 
   - Frontend → Vercel
   - Backend → Railway
4. **Verify**: 
   - Health checks
   - Database migrations
   - Smoke tests

### 5.3. Monitoring & Alerting

**Setup Alert Workflow:**

```json
POST /mcp/tools/gpt/orchestrate
{
  "command": "SETUP MONITORING FOR CRITICAL SERVICES",
  "context": {
    "services": ["backend", "frontend", "database"],
    "alert_channels": ["discord", "linear"]
  }
}
```

**Monitoring Loop:**
```javascript
// Automatic health check every 5 minutes
setInterval(() => {
  fetch('http://127.0.0.1:8012/mcp/tools/gpt/status')
    .then(res => res.json())
    .then(data => {
      if (data.overall_status !== 'healthy') {
        // Create urgent Linear task
        // Send Discord notification
      }
    });
}, 5 * 60 * 1000);
```

---

## 6. Troubleshooting

### 6.1. Orchestrator nu pornește

**Problema**: `Error: Cannot find module '@linear/sdk'`

**Soluție:**
```powershell
cd mcp-orchestrator
rm -rf node_modules
rm package-lock.json
npm install
npm run build:bridge
node dist/http-bridge.js
```

### 6.2. MCP Server nu se conectează la Orchestrator

**Problema**: `orchestrator_connected: false`

**Verificare:**
```powershell
# Check orchestrator
curl http://127.0.0.1:3030/health

# Check port occupation
netstat -ano | findstr :3030
```

**Soluție:**
- Restart orchestrator
- Verifică ORCHESTRATOR_URL în `.env`
- Check firewall

### 6.3. GPT Actions nu funcționează

**Problema**: GPT nu poate accesa localhost

**Soluție**: Expune prin ngrok sau localtunnel:

```powershell
# Install ngrok
choco install ngrok

# Expose MCP Server
ngrok http 8012
```

Apoi în GPT Actions, folosește URL-ul ngrok:
```
https://xxxx-xxxx-xxxx.ngrok.io
```

### 6.4. Linear API Rate Limit

**Problema**: `429 Too Many Requests`

**Soluție**: Rate limiting în orchestrator client:

```python
# orchestrator_client.py
retry_strategy = Retry(
    total=3,
    backoff_factor=2,  # Increase backoff
    status_forcelist=[429, 500, 502, 503, 504],
)
```

### 6.5. Playwright Tests Fail

**Problema**: Browser nu pornește

**Soluție:**
```powershell
# Install browsers
cd mcp-orchestrator
npx playwright install chromium

# Run in headed mode for debugging
# In http-bridge.ts, change:
# chromium.launch({ headless: false })
```

---

## 7. Best Practices

### 7.1. Structurare Prompts pentru GPT

**❌ Prost:**
```
Fix toate bug-urile din backend
```

**✅ Bine:**
```
Folosind MCP orchestrate, creează workflow pentru:
"FIX AUTHENTICATION BUGS IN BACKEND"

Context:
- Files: services/api/app/routes/auth.py
- Issue: Users can't login with Google OAuth
- Database: Supabase users table
- Branch: cursor/fix-auth-bugs

Expected:
1. Investigate issue in auth.py
2. Create Linear task
3. Implement fix
4. Test login flow (browser test)
5. Verify in Supabase
6. Commit with task reference
```

### 7.2. Task Management

**Organizare în Linear:**
- **Epic**: Feature mare (ex: "Push Notifications System")
- **Task**: Unit de lucru (ex: "Implement FCM integration")
- **Subtask**: Pași specifici (ex: "Add FCM config to .env")

**Labeling:**
- `agent:claude` - Task pentru Claude
- `priority:critical` - Urgent
- `type:bug` / `type:feature` / `type:test`
- `status:in-progress` / `status:review` / `status:done`

### 7.3. Commit Messages

**Format:**
```
<type>(<scope>): <subject> [<Linear-ID>] [#<GitHub-Issue>]

<body>

<footer>
```

**Exemple:**
```
feat(auth): add Google OAuth login [AUT-123] [#45]

Implemented Google OAuth using passport.js strategy.
Added callback endpoint and user creation flow.

Linear: AUT-123
GitHub: #45
```

### 7.4. Testing Strategy

**Piramidă:**
1. **Unit Tests** (70%): Fast, izolate
2. **Integration Tests** (20%): API endpoints
3. **E2E Tests** (10%): Browser flows

**Rulare:**
```powershell
# Unit tests
pytest services/api/tests/

# E2E via MCP
curl -X POST http://127.0.0.1:8012/mcp/tools/gpt/test \
  -H "Content-Type: application/json" \
  -d '{"test_type": "browser", "config": {...}}'
```

---

## 8. Comenzi Rapide

### 8.1. Startup Quick Commands

```powershell
# Full system start
.\START_SYSTEM.ps1

# Individual services
node mcp-orchestrator/dist/http-bridge.js
python mcp_server/main.py

# Health checks
curl http://127.0.0.1:3030/health
curl http://127.0.0.1:8012/health
curl http://127.0.0.1:8012/mcp/tools/system/health

# Stop all
taskkill /F /IM node.exe
taskkill /F /IM python.exe
```

### 8.2. Common API Calls

```powershell
# Orchestrate workflow
curl -X POST http://127.0.0.1:8012/mcp/tools/gpt/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"command":"TEST","context":{"project":"AutoPro"}}'

# Create Linear task
curl -X POST http://127.0.0.1:8012/mcp/tools/gpt/create_task \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","description":"Test"}'

# System status
curl http://127.0.0.1:8012/mcp/tools/gpt/status

# Run test
curl -X POST http://127.0.0.1:8012/mcp/tools/gpt/test \
  -H "Content-Type: application/json" \
  -d '{"test_type":"api","config":{"method":"GET","url":"http://localhost:8011/health"}}'
```

---

## 9. Resurse

### 9.1. Documentație

- **MCP Server**: `mcp_server/README.md`
- **Orchestrator**: `mcp-orchestrator/README.md`
- **Implementation**: `IMPLEMENTATION_COMPLETE.md`
- **Validation**: `VALIDATION_CHECKLIST.md`

### 9.2. API Documentation

- **Interactive Docs**: http://127.0.0.1:8012/docs
- **ReDoc**: http://127.0.0.1:8012/redoc
- **OpenAPI JSON**: http://127.0.0.1:8012/openapi.json

### 9.3. Logs

- **Orchestrator**: Console output
- **MCP Server**: `mcp_server/logs/` (dacă configurat)
- **Tasks**: `mcp_server/data/tasks.json`

---

## 🎯 Checklist Success

- [ ] Environment variables configurate (`.env`)
- [ ] Dependencies instalate (Python + Node.js)
- [ ] Sistem pornit (`START_SYSTEM.ps1`)
- [ ] Health checks pass (toate serviciile healthy)
- [ ] GPT Actions configurat (OpenAPI schema)
- [ ] Test orchestration funcționează
- [ ] Linear integration activă
- [ ] GitHub integration activă
- [ ] Supabase connection stabilă

---

## 🚀 Ready to Go!

Sistemul este acum gata pentru **utilizare maximă**!

**Next Steps:**
1. Testează cu un workflow simplu
2. Escaladează la task-uri complexe
3. Automatizează procesele repetitive
4. Monitorizează și optimizează

**Questions?** Check `TROUBLESHOOTING.md` sau logs.

---

**Versiune**: 0.2.0  
**Data**: 2025-10-16  
**Status**: ✅ Production Ready
