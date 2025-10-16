# ⚡ Quick Start Guide - MCP System

**Start rapid în 5 minute**

---

## 🚀 Start Sistem

### Variantă 1: Automatic (Recomandat)

```powershell
.\START_SYSTEM.ps1
```

✅ Gata! Sistemul pornește automat.

### Variantă 2: Manual

**Terminal 1:**
```powershell
cd mcp-orchestrator
node dist/http-bridge.js
```

**Terminal 2:**
```powershell
cd mcp_server
python main.py
```

---

## ✅ Verificare

```powershell
curl http://127.0.0.1:3030/health  # Orchestrator
curl http://127.0.0.1:8012/health  # MCP Server
```

**Output OK:**
```json
{"status": "ok", "orchestrator_connected": true}
```

---

## 🎯 Primul Workflow

### 1. Via GPT (ChatGPT cu Actions)

**Prompt:**
```
Folosește MCP orchestrate pentru:
"Create test workflow for AutoPro project"
```

**GPT va apela automat:**
```
POST /mcp/tools/gpt/orchestrate
```

### 2. Via Curl (Testing)

```powershell
curl -X POST http://127.0.0.1:8012/mcp/tools/gpt/orchestrate `
  -H "Content-Type: application/json" `
  -d '{
    "command": "Test workflow",
    "context": {"project": "AutoPro"},
    "options": {}
  }'
```

### 3. Via Cursor

**Prompt în Cursor:**
```
@mcp orchestrate: "Fix authentication bugs in backend"
```

---

## 📋 Endpoints Esențiale

| Endpoint | Metodă | Descriere |
|----------|--------|-----------|
| `/health` | GET | Server health |
| `/mcp/tools/gpt/orchestrate` | POST | Orchestrate workflow |
| `/mcp/tools/gpt/create_task` | POST | Create Linear task |
| `/mcp/tools/gpt/status` | GET | System status |
| `/mcp/tools/gpt/test` | POST | Run tests |

---

## 🔥 Top 5 Use Cases

### 1. Fix & Test Bugs
```json
POST /mcp/tools/gpt/orchestrate
{
  "command": "FIX AND TEST CRITICAL BUGS",
  "context": {"project": "AutoPro", "component": "backend"}
}
```

### 2. Deploy Frontend
```json
POST /mcp/tools/gpt/orchestrate
{
  "command": "DEPLOY FRONTEND TO VERCEL",
  "context": {"frontend_path": "02_FRONTEND_UI_CLEAN"}
}
```

### 3. Create Epic
```json
POST /mcp/tools/gpt/create_task
{
  "title": "Implement Push Notifications",
  "description": "Complete system...",
  "priority": 1
}
```

### 4. Run E2E Tests
```json
POST /mcp/tools/gpt/test
{
  "test_type": "browser",
  "config": {
    "test_name": "Login Flow",
    "url": "http://localhost:5173",
    "steps": [...]
  }
}
```

### 5. Health Check
```
GET /mcp/tools/gpt/status
```

---

## 🛠️ Troubleshooting Rapid

### Orchestrator nu pornește
```powershell
cd mcp-orchestrator
npm install
node dist/http-bridge.js
```

### MCP Server erori
```powershell
cd mcp_server
pip install -r requirements.txt
python main.py
```

### Port ocupat
```powershell
# Check ports
netstat -ano | findstr :8012
netstat -ano | findstr :3030

# Kill process
taskkill /F /PID <PID>
```

---

## 📚 Documentație Completă

Pentru detalii: Vezi **TUTORIAL_MCP_GPT_COMPLETE.md**

---

**Status**: ✅ Ready  
**Timp Setup**: ~5 minute  
**Dificultate**: ⭐ Beginner-friendly
