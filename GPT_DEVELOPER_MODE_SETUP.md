# 🤖 GPT Developer Mode - Setup Complete

**Configurare ChatGPT Actions pentru MCP System**

---

## 📋 Pași Setup

### 1. Accesează ChatGPT Settings

1. Deschide **ChatGPT**
2. Click **Settings** (⚙️)
3. **Beta Features** → **Actions**
4. Click **Create New Action**

---

### 2. Import OpenAPI Schema

**Opțiune A: Direct din MCP Server**

```powershell
# Pornește MCP Server
.\START_SYSTEM.ps1

# Deschide în browser
start http://127.0.0.1:8012/docs
```

Copiază JSON-ul din: http://127.0.0.1:8012/openapi.json

**Opțiune B: Schema Manuală**

Paste acest JSON în GPT Actions:

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "AutoPro MCP Server",
    "version": "0.2.0",
    "description": "MCP Server for AutoPro project orchestration with GPT Developer Mode support"
  },
  "servers": [
    {
      "url": "http://127.0.0.1:8012",
      "description": "Local MCP Server"
    }
  ],
  "paths": {
    "/mcp/tools/gpt/orchestrate": {
      "post": {
        "summary": "Orchestrate Workflow (GPT Mode)",
        "description": "Create and orchestrate multi-agent workflow. Returns workflow_id, tasks, and agent prompts.",
        "operationId": "gptOrchestrate",
        "tags": ["GPT Developer Mode"],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["command", "context"],
                "properties": {
                  "command": {
                    "type": "string",
                    "description": "High-level command (e.g., 'FIX ALL CRITICAL BUGS', 'DEPLOY FRONTEND')"
                  },
                  "context": {
                    "type": "object",
                    "description": "Project context (project name, paths, branch, etc.)"
                  },
                  "options": {
                    "type": "object",
                    "description": "Orchestration options (auto_execute, create_linear_tasks, etc.)"
                  }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Workflow created successfully",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "success": {"type": "boolean"},
                    "workflow_id": {"type": "string"},
                    "summary": {"type": "string"},
                    "tasks": {"type": "array"},
                    "agent_prompts": {"type": "array"},
                    "next_steps": {"type": "string"}
                  }
                }
              }
            }
          }
        }
      }
    },
    "/mcp/tools/gpt/create_task": {
      "post": {
        "summary": "Create Linear Task (GPT Mode)",
        "description": "Create task in Linear project management system",
        "operationId": "gptCreateTask",
        "tags": ["GPT Developer Mode"],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["title"],
                "properties": {
                  "title": {"type": "string"},
                  "description": {"type": "string"},
                  "priority": {"type": "integer", "minimum": 0, "maximum": 4},
                  "labels": {"type": "array", "items": {"type": "string"}},
                  "epic_id": {"type": "string"},
                  "assignee": {"type": "string"}
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Task created",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "success": {"type": "boolean"},
                    "task_id": {"type": "string"},
                    "url": {"type": "string"},
                    "message": {"type": "string"}
                  }
                }
              }
            }
          }
        }
      }
    },
    "/mcp/tools/gpt/status": {
      "get": {
        "summary": "System Status (GPT Mode)",
        "description": "Get comprehensive system health including all services",
        "operationId": "gptStatus",
        "tags": ["GPT Developer Mode"],
        "responses": {
          "200": {
            "description": "System status",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "success": {"type": "boolean"},
                    "overall_status": {"type": "string"},
                    "services": {"type": "object"},
                    "timestamp": {"type": "string"}
                  }
                }
              }
            }
          }
        }
      }
    },
    "/mcp/tools/gpt/test": {
      "post": {
        "summary": "Run Test (GPT Mode)",
        "description": "Execute browser E2E or API test",
        "operationId": "gptTest",
        "tags": ["GPT Developer Mode"],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["test_type", "config"],
                "properties": {
                  "test_type": {
                    "type": "string",
                    "enum": ["browser", "api"]
                  },
                  "config": {
                    "type": "object",
                    "description": "Test configuration (depends on test_type)"
                  }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Test completed",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "success": {"type": "boolean"},
                    "test_type": {"type": "string"},
                    "results": {"type": "object"},
                    "message": {"type": "string"}
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

---

### 3. Configurare Authentication

**Setări:**
- **Authentication**: None
- **Privacy**: Server-side only

**Note**: Pentru producție, configurează ngrok sau VPN.

---

### 4. Test Action

**În ChatGPT, prompt:**

```
Check system status using MCP
```

**GPT va apela:**
```
GET http://127.0.0.1:8012/mcp/tools/gpt/status
```

**Response așteptat:**
```json
{
  "success": true,
  "overall_status": "healthy",
  "services": {
    "backend": {"status": "healthy"},
    "linear": {"status": "healthy"},
    "github": {"status": "healthy"}
  }
}
```

---

## 🎯 Prompt-uri Optimizate pentru GPT

### Pattern 1: Orchestrate Workflow

**Prompt:**
```
Folosind MCP orchestrate, creează workflow pentru:
"[TASK DESCRIPTION]"

Context:
- Project: AutoPro Daune
- Component: [backend/frontend/fullstack]
- Branch: cursor/[branch-name]
- Priority: [low/medium/high/critical]

Outputs:
- Linear tasks
- GitHub issues
- Agent prompts pentru fiecare task
```

**Exemplu Concret:**
```
Folosind MCP orchestrate, creează workflow pentru:
"FIX AUTHENTICATION BUGS IN BACKEND"

Context:
- Project: AutoPro Daune
- Component: backend
- Files: services/api/app/routes/auth.py
- Branch: cursor/fix-auth-critical
- Priority: critical

Outputs:
- 3-5 Linear tasks
- GitHub issues linkate
- Detailed agent prompts
```

### Pattern 2: Create Task

**Prompt:**
```
Creează Linear task:
Title: [TASK TITLE]
Description: [DETAILED DESCRIPTION]
Priority: [0-4]
Labels: [bug/feature/test/deploy]
```

### Pattern 3: Run Tests

**Prompt:**
```
Rulează E2E test pentru:
- Flow: [login/registration/checkout/etc]
- URL: http://localhost:5173
- Verificare în Supabase: [table/conditions]
```

### Pattern 4: System Check

**Prompt:**
```
Check complete system health:
- Backend API
- Frontend
- Database (Supabase)
- External services (Linear, GitHub)
```

---

## 🔥 Advanced: GPT Custom Instructions

**În ChatGPT Settings → Custom Instructions:**

```markdown
# AutoPro MCP Integration

I have access to MCP (Model Context Protocol) Server at http://127.0.0.1:8012

## Available Actions:

1. **orchestrate**: Create multi-agent workflows
   - Use for: Complex multi-step tasks
   - Returns: workflow_id, tasks, agent_prompts

2. **create_task**: Create Linear tasks
   - Use for: Single task creation
   - Returns: task_id, url

3. **status**: Check system health
   - Use for: Health checks, monitoring
   - Returns: overall_status, services

4. **test**: Run browser/API tests
   - Use for: E2E testing, verification
   - Returns: test results

## When to Use:

- Complex tasks → Use `orchestrate` first
- Create tracking → Use `create_task`
- Before/after work → Use `status` to check health
- Verification → Use `test` for E2E validation

## Workflow Pattern:

1. Check status
2. Orchestrate workflow (if complex)
3. Execute tasks sequentially
4. Create Linear tasks for tracking
5. Run tests to verify
6. Check final status

## Important:

- Always provide context (project, branch, component)
- Use descriptive task titles
- Include verification steps
- Report back results clearly
```

---

## 📱 Mobile: GPT App Setup

**Pe telefon (iOS/Android):**

1. Deschide GPT App
2. Settings → Actions
3. Add Action → Paste OpenAPI schema
4. **Important**: Folosește ngrok pentru localhost:

```powershell
# Install ngrok
choco install ngrok

# Start tunnel
ngrok http 8012

# Use ngrok URL în schema
https://xxxx-xxxx.ngrok.io
```

---

## 🌐 Production: External Access

### Opțiune 1: ngrok (Simplă)

```powershell
ngrok http 8012
```

**Avantaje**: Setup rapid
**Dezavantaje**: URL se schimbă

### Opțiune 2: Cloudflare Tunnel (Permanent)

```powershell
# Install cloudflared
choco install cloudflared

# Login
cloudflared login

# Create tunnel
cloudflared tunnel create mcp-server

# Configure
cloudflared tunnel route dns mcp-server mcp.yourdomain.com

# Run
cloudflared tunnel run mcp-server
```

**Avantaje**: URL permanent, HTTPS
**Dezavantaje**: Setup mai complex

### Opțiune 3: VPS Deployment

```bash
# Deploy pe VPS (Ubuntu)
ssh user@your-vps.com

# Install dependencies
sudo apt install python3 nodejs npm

# Clone repo
git clone https://github.com/yourusername/autopro.git

# Setup
cd autopro
./setup.sh

# Start with PM2
pm2 start mcp_server/main.py --name mcp-server
pm2 start mcp-orchestrator/dist/http-bridge.js --name orchestrator

# Configure nginx reverse proxy
sudo nano /etc/nginx/sites-available/mcp
```

---

## ✅ Verification Checklist

- [ ] MCP Server running (port 8012)
- [ ] Orchestrator running (port 3030)
- [ ] OpenAPI schema importat în GPT
- [ ] Test call successful
- [ ] Custom instructions configured
- [ ] Production access configured (dacă necesar)

---

## 🎓 Training Prompts

### Prompt 1: Basic Orchestration
```
Check system status, then orchestrate a test workflow with context: {project: "AutoPro", task: "health check"}
```

### Prompt 2: Task Creation
```
Create a Linear task titled "Test GPT Integration" with priority 2
```

### Prompt 3: E2E Test
```
Run API test for backend health: GET http://127.0.0.1:8011/health, expect 200 OK
```

### Prompt 4: Complex Workflow
```
Orchestrate deployment workflow:
1. Run all tests
2. Build frontend
3. Deploy to Vercel
4. Verify in production
5. Create deployment record in Linear
```

---

## 📚 Resources

- **Full Tutorial**: `TUTORIAL_MCP_GPT_COMPLETE.md`
- **Quick Start**: `QUICK_START_GUIDE.md`
- **API Docs**: http://127.0.0.1:8012/docs
- **OpenAPI Spec**: http://127.0.0.1:8012/openapi.json

---

**Status**: ✅ Ready for GPT Integration  
**Version**: 0.2.0  
**Updated**: 2025-10-16
