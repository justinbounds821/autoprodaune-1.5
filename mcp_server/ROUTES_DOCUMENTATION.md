# MCP Server Routes Documentation

## 🎯 Route Organization

All routes are now logically organized into 6 main categories:

### 1. **System Routes** (`/system/*`)
Health checks, status monitoring, and system information

### 2. **Core MCP Routes** (`/mcp/*`)
Task execution and task management

### 3. **Workflow Routes** (`/mcp/workflows/*`)
Workflow orchestration and templates

### 4. **Integration Routes** (`/mcp/tools/{linear,github,supabase}/*`)
External service integrations

### 5. **Testing Routes** (`/mcp/tools/test/*`)
Browser and API testing capabilities

### 6. **GPT Routes** (`/mcp/tools/gpt/*`)
ChatGPT developer mode optimized endpoints

---

## 📋 Complete Route List

### System Routes (9 routes)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/system/health` | System health check with orchestrator status |
| `GET` | `/system/status` | Detailed system status with all components |
| `GET` | `/system/tools` | List all available MCP tools |
| `GET` | `/system/info` | System configuration and runtime information |
| `GET` | `/` | Root endpoint with API information |
| `GET` | `/health` | Legacy health check (backwards compatibility) |
| `GET` | `/favicon.ico` | Favicon endpoint (prevents 404s) |
| `POST` | `/events/error` | Log error events from clients |

### Core MCP Routes (5 routes)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/mcp/execute` | Execute free-form MCP task |
| `GET` | `/mcp/task/{task_id}/status` | Get task status and result |
| `GET` | `/mcp/tasks` | List all tasks with filtering |
| `DELETE` | `/mcp/task/{task_id}` | Delete a task by ID |
| `POST` | `/mcp/tasks/clear` | Clear tasks (optionally by status) |

### Workflow Routes (5 routes)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/mcp/workflows/orchestrate` | Orchestrate complete workflow |
| `POST` | `/mcp/workflows/analyze` | Analyze workflow without executing |
| `GET` | `/mcp/workflows/status/{workflow_id}` | Get workflow execution status |
| `GET` | `/mcp/workflows/templates` | List workflow templates |
| `POST` | `/mcp/workflows/template/{template_id}` | Execute workflow template |

### Integration Routes (12 routes)

#### Linear (4 routes)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/mcp/tools/linear/task` | Create Linear task |
| `PUT` | `/mcp/tools/linear/task` | Update Linear task |
| `GET` | `/mcp/tools/linear/tasks` | List Linear tasks |
| `GET` | `/mcp/tools/linear/task/{task_id}` | Get Linear task details |

#### GitHub (3 routes)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/mcp/tools/github/issue` | Create GitHub issue |
| `POST` | `/mcp/tools/github/commit` | Create Git commit |
| `GET` | `/mcp/tools/github/status` | GitHub integration status |

#### Supabase (5 routes)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/mcp/tools/supabase/query` | Execute Supabase query |
| `POST` | `/mcp/tools/supabase/verify` | Verify database fix |
| `GET` | `/mcp/tools/supabase/tables` | List available tables |
| `GET` | `/mcp/tools/supabase/status` | Supabase integration status |

### Testing Routes (8 routes)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/mcp/tools/test/browser` | Execute browser E2E test |
| `GET` | `/mcp/tools/test/browser/history` | Browser test history |
| `POST` | `/mcp/tools/test/api` | Execute API test |
| `GET` | `/mcp/tools/test/api/history` | API test history |
| `POST` | `/mcp/tools/test/suite` | Execute test suite |
| `GET` | `/mcp/tools/test/suites` | List test suites |
| `GET` | `/mcp/tools/system/health` | System health check (detailed) |
| `GET` | `/mcp/tools/system/metrics` | System performance metrics |

### GPT Routes (9 routes)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/mcp/tools/gpt/orchestrate` | GPT-optimized workflow orchestration |
| `POST` | `/mcp/tools/gpt/orchestrate/stream` | Streaming workflow orchestration |
| `POST` | `/mcp/tools/gpt/create_task` | GPT-optimized task creation |
| `GET` | `/mcp/tools/gpt/tasks` | List tasks with GPT formatting |
| `POST` | `/mcp/tools/gpt/test` | Unified test execution |
| `GET` | `/mcp/tools/gpt/status` | System status for GPT |
| `GET` | `/mcp/tools/gpt/capabilities` | List GPT capabilities |
| `GET` | `/mcp/tools/gpt/help` | Help and usage examples |
| `GET` | `/mcp/tools/gpt/examples` | Complete usage examples |

---

## 🎯 Total Route Count: 48 Routes

- **System Routes:** 8 routes
- **Core MCP Routes:** 5 routes
- **Workflow Routes:** 5 routes
- **Integration Routes:** 12 routes (Linear: 4, GitHub: 3, Supabase: 5)
- **Testing Routes:** 8 routes
- **GPT Routes:** 9 routes

---

## 🔧 Route Structure Benefits

### 1. **Logical Organization**
- Routes grouped by functionality
- Clear hierarchical structure
- Easy to find and understand

### 2. **Maintainability**
- Each category in separate file
- Isolated concerns
- Easy to modify and extend

### 3. **Scalability**
- Easy to add new routes
- Can add new categories
- Modular design

### 4. **Documentation**
- Self-documenting structure
- Clear naming conventions
- OpenAPI schema generation

### 5. **Testing**
- Easy to test by category
- Isolated test suites
- Clear test boundaries

---

## 📊 OpenAPI Schema

The OpenAPI schema is automatically generated and includes:

- **Standard OpenAPI:** `/openapi.json` (full schema)
- **ChatGPT Optimized:** `/chatgpt/openapi.json` (GPT-friendly)
- **Interactive Docs:** `/docs` (Swagger UI)
- **Alternative Docs:** `/redoc` (ReDoc)

---

## 🚀 Testing Routes

### Quick Health Check
```bash
curl http://localhost:8012/system/health
```

### List All Tools
```bash
curl http://localhost:8012/system/tools
```

### Create Task
```bash
curl -X POST http://localhost:8012/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "Test task", "context": {}}'
```

### Orchestrate Workflow
```bash
curl -X POST http://localhost:8012/mcp/workflows/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"command": "Create test task", "context": {}}'
```

### GPT Status
```bash
curl http://localhost:8012/mcp/tools/gpt/status
```

---

## 📝 Migration Notes

### What Changed
1. All routes moved from `main.py` to dedicated route files
2. Routes organized by category/functionality
3. Added new helper routes (status, info, tools list)
4. Added GPT-optimized endpoints
5. Added workflow templates
6. Added test suite support

### Backwards Compatibility
- `/health` endpoint maintained for backwards compatibility
- All existing endpoints preserved with same paths
- Additional functionality added without breaking changes

### New Features
- Route organization and categorization
- System information endpoints
- Workflow templates
- Test suites
- GPT help and examples
- Error event logging

---

## 🎉 Summary

The MCP Server routes are now **100% organized** with a clear, logical structure that:
- ✅ Groups related functionality together
- ✅ Makes routes easy to find and understand
- ✅ Improves maintainability and scalability
- ✅ Provides better documentation
- ✅ Maintains backwards compatibility
- ✅ Adds new capabilities (GPT, workflows, testing)

All **48 routes** are properly categorized and documented!
