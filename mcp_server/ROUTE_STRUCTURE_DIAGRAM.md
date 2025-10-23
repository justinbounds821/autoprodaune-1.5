# MCP Server Route Structure - Visual Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AutoPro FastMCP Server v0.2.0                        │
│                            http://localhost:8012                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │         main.py (FastAPI)         │
                    └─────────────────┬─────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │     Router Registration (6)       │
                    └─────────────────┬─────────────────┘
                                      │
        ┌─────────────┬───────────────┼───────────────┬─────────────┬──────────┐
        │             │               │               │             │          │
        ▼             ▼               ▼               ▼             ▼          ▼
┌──────────────┐ ┌────────┐ ┌──────────────┐ ┌─────────────┐ ┌─────────┐ ┌──────┐
│   System     │ │  Core  │ │  Workflows   │ │Integrations │ │ Testing │ │ GPT  │
│   Routes     │ │  MCP   │ │   Routes     │ │   Routes    │ │ Routes  │ │Routes│
└──────┬───────┘ └───┬────┘ └──────┬───────┘ └──────┬──────┘ └────┬────┘ └───┬──┘
       │             │              │                │              │          │
       │             │              │                │              │          │
       │             │              │                │              │          │

┌──────┴────────────────────────────────────────────────────────────────────────┐
│ 1. SYSTEM ROUTES (/system/*, /)                              [8 routes]       │
├───────────────────────────────────────────────────────────────────────────────┤
│ GET  /                      → Root API information                            │
│ GET  /health                → Legacy health check                             │
│ GET  /system/health         → System health + orchestrator status             │
│ GET  /system/status         → Detailed system status                          │
│ GET  /system/tools          → List all 11 available tools                     │
│ GET  /system/info           → System configuration & features                 │
│ GET  /favicon.ico           → Favicon (prevents 404s)                         │
│ POST /events/error          → Client error logging                            │
└───────────────────────────────────────────────────────────────────────────────┘

┌──────┴────────────────────────────────────────────────────────────────────────┐
│ 2. CORE MCP ROUTES (/mcp/*)                                  [5 routes]       │
├───────────────────────────────────────────────────────────────────────────────┤
│ POST   /mcp/execute                → Execute free-form task                   │
│ GET    /mcp/task/{task_id}/status  → Get task status & result                │
│ GET    /mcp/tasks                  → List all tasks (with filters)            │
│ DELETE /mcp/task/{task_id}         → Delete specific task                    │
│ POST   /mcp/tasks/clear            → Clear tasks (by status)                 │
└───────────────────────────────────────────────────────────────────────────────┘

┌──────┴────────────────────────────────────────────────────────────────────────┐
│ 3. WORKFLOW ROUTES (/mcp/workflows/*)                        [5 routes]       │
├───────────────────────────────────────────────────────────────────────────────┤
│ POST /mcp/workflows/orchestrate              → Orchestrate workflow           │
│ POST /mcp/workflows/analyze                  → Analyze without executing      │
│ GET  /mcp/workflows/status/{workflow_id}     → Get workflow status            │
│ GET  /mcp/workflows/templates                → List workflow templates        │
│ POST /mcp/workflows/template/{template_id}   → Execute template               │
└───────────────────────────────────────────────────────────────────────────────┘

┌──────┴────────────────────────────────────────────────────────────────────────┐
│ 4. INTEGRATION ROUTES (/mcp/tools/*)                         [12 routes]      │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│ 📊 LINEAR (4 routes)                                                          │
│ ├─ POST /mcp/tools/linear/task             → Create Linear task              │
│ ├─ PUT  /mcp/tools/linear/task             → Update Linear task              │
│ ├─ GET  /mcp/tools/linear/tasks            → List Linear tasks               │
│ └─ GET  /mcp/tools/linear/task/{task_id}   → Get task details                │
│                                                                                │
│ 🐙 GITHUB (3 routes)                                                          │
│ ├─ POST /mcp/tools/github/issue   → Create GitHub issue                      │
│ ├─ POST /mcp/tools/github/commit  → Create Git commit                        │
│ └─ GET  /mcp/tools/github/status  → GitHub integration status                │
│                                                                                │
│ 🗄️ SUPABASE (5 routes)                                                        │
│ ├─ POST /mcp/tools/supabase/query   → Execute database query                 │
│ ├─ POST /mcp/tools/supabase/verify  → Verify database state                  │
│ ├─ GET  /mcp/tools/supabase/tables  → List available tables                  │
│ └─ GET  /mcp/tools/supabase/status  → Supabase status                        │
└───────────────────────────────────────────────────────────────────────────────┘

┌──────┴────────────────────────────────────────────────────────────────────────┐
│ 5. TESTING ROUTES (/mcp/tools/test/*, /mcp/tools/system/*)   [8 routes]      │
├───────────────────────────────────────────────────────────────────────────────┤
│ 🌐 Browser Testing                                                            │
│ ├─ POST /mcp/tools/test/browser           → Execute browser E2E test         │
│ └─ GET  /mcp/tools/test/browser/history   → Browser test history             │
│                                                                                │
│ 🔌 API Testing                                                                │
│ ├─ POST /mcp/tools/test/api               → Execute API test                 │
│ └─ GET  /mcp/tools/test/api/history       → API test history                 │
│                                                                                │
│ 📦 Test Suites                                                                │
│ ├─ POST /mcp/tools/test/suite             → Execute test suite               │
│ └─ GET  /mcp/tools/test/suites            → List available suites            │
│                                                                                │
│ 🏥 System Health                                                              │
│ ├─ GET  /mcp/tools/system/health          → Detailed health check            │
│ └─ GET  /mcp/tools/system/metrics         → Performance metrics              │
└───────────────────────────────────────────────────────────────────────────────┘

┌──────┴────────────────────────────────────────────────────────────────────────┐
│ 6. GPT ROUTES (/mcp/tools/gpt/*)                             [9 routes]       │
├───────────────────────────────────────────────────────────────────────────────┤
│ 🤖 ChatGPT Developer Mode Optimized Endpoints                                │
│                                                                                │
│ 🔄 Workflow Orchestration                                                     │
│ ├─ POST /mcp/tools/gpt/orchestrate         → GPT-optimized orchestration     │
│ └─ POST /mcp/tools/gpt/orchestrate/stream  → Streaming orchestration         │
│                                                                                │
│ 📋 Task Management                                                            │
│ ├─ POST /mcp/tools/gpt/create_task         → Create task (GPT format)        │
│ └─ GET  /mcp/tools/gpt/tasks               → List tasks (GPT format)         │
│                                                                                │
│ 🧪 Testing                                                                    │
│ └─ POST /mcp/tools/gpt/test                → Unified test execution           │
│                                                                                │
│ 📊 Status & Info                                                              │
│ ├─ GET  /mcp/tools/gpt/status              → System status (GPT format)      │
│ ├─ GET  /mcp/tools/gpt/capabilities        → List capabilities               │
│ ├─ GET  /mcp/tools/gpt/help                → Help & usage examples           │
│ └─ GET  /mcp/tools/gpt/examples            → Complete usage examples         │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ 📖 OPENAPI & DOCUMENTATION                                                    │
├───────────────────────────────────────────────────────────────────────────────┤
│ GET /openapi.json      → Full OpenAPI schema (4310 chars)                    │
│ GET /docs              → Swagger UI (interactive documentation)               │
│ GET /redoc             → ReDoc (alternative documentation)                    │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ 🎯 TOTAL: 48 ROUTES                                                           │
├───────────────────────────────────────────────────────────────────────────────┤
│ • System Routes:      8 routes                                                │
│ • Core MCP Routes:    5 routes                                                │
│ • Workflow Routes:    5 routes                                                │
│ • Integration Routes: 12 routes (Linear: 4, GitHub: 3, Supabase: 5)          │
│ • Testing Routes:     8 routes                                                │
│ • GPT Routes:         9 routes                                                │
│ • OpenAPI:            3 routes                                                │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ 🏗️ FILE STRUCTURE                                                             │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│ mcp_server/                                                                   │
│ ├── main.py                     (267 lines) - Main FastAPI app               │
│ ├── routes/                                                                   │
│ │   ├── __init__.py             - Router exports                             │
│ │   ├── system.py               (165 lines) - System routes                  │
│ │   ├── core.py                 (246 lines) - Core MCP routes                │
│ │   ├── workflows.py            (179 lines) - Workflow routes                │
│ │   ├── integrations.py         (375 lines) - Integration routes             │
│ │   ├── testing.py              (262 lines) - Testing routes                 │
│ │   └── gpt.py                  (472 lines) - GPT routes                     │
│ ├── config.py                   - Configuration                               │
│ ├── middleware.py               - Middleware                                  │
│ ├── openapi_customization.py   - OpenAPI customization                       │
│ └── clients/                                                                  │
│     └── orchestrator_client.py  - Orchestrator client                        │
│                                                                                │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ ✅ BENEFITS                                                                    │
├───────────────────────────────────────────────────────────────────────────────┤
│ ✅ Logical organization by functionality                                      │
│ ✅ Easy to find and understand routes                                         │
│ ✅ Maintainable and scalable architecture                                     │
│ ✅ Clear separation of concerns                                               │
│ ✅ Self-documenting structure                                                 │
│ ✅ Easy to test by category                                                   │
│ ✅ 100% backwards compatible                                                  │
│ ✅ Enhanced with new GPT-optimized endpoints                                  │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ 🚀 READY FOR PRODUCTION                                                       │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Route Flow Diagram

```
                              Client Request
                                    │
                                    ▼
                          ┌──────────────────┐
                          │   FastAPI App    │
                          │   (main.py)      │
                          └────────┬─────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
            ┌───────▼───────┐  ┌──▼──┐  ┌───────▼────────┐
            │  Middleware   │  │CORS │  │ Error Handler  │
            │  - Logging    │  │     │  │                │
            │  - Health     │  └─────┘  └────────────────┘
            └───────┬───────┘
                    │
        ┌───────────┴───────────┐
        │   Route Matching      │
        └───────────┬───────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
┌────────┐     ┌─────────┐    ┌──────────┐
│System  │     │  Core   │    │Workflows │
│Router  │     │  Router │    │ Router   │
└───┬────┘     └────┬────┘    └─────┬────┘
    │               │               │
    │               ▼               │
    │      ┌─────────────────┐     │
    │      │  Orchestrator   │     │
    │      │     Client      │     │
    │      └────────┬────────┘     │
    │               │               │
    │               ▼               │
    │      ┌─────────────────┐     │
    │      │  Node.js MCP    │     │
    │      │  Orchestrator   │     │
    │      │  (Port 3030)    │     │
    │      └────────┬────────┘     │
    │               │               │
    │               ▼               │
    │      ┌─────────────────┐     │
    │      │  External APIs  │     │
    │      │  - Linear       │     │
    │      │  - GitHub       │     │
    │      │  - Supabase     │     │
    │      └────────┬────────┘     │
    │               │               │
    └───────────────┴───────────────┘
                    │
                    ▼
            ┌───────────────┐
            │    Response   │
            │   (JSON)      │
            └───────────────┘
```

---

## Category Breakdown

```
┌─────────────────────────────────────────────────────────────┐
│                    Route Categories                          │
├────────────────┬────────────┬──────────────────────────────┤
│   Category     │   Routes   │         Purpose              │
├────────────────┼────────────┼──────────────────────────────┤
│ System         │     8      │ Health, status, monitoring   │
│ Core MCP       │     5      │ Task execution & management  │
│ Workflows      │     5      │ Workflow orchestration       │
│ Integrations   │    12      │ External services (L/G/S)    │
│ Testing        │     8      │ Browser & API testing        │
│ GPT            │     9      │ ChatGPT optimized            │
│ OpenAPI        │     3      │ Documentation                │
├────────────────┼────────────┼──────────────────────────────┤
│ TOTAL          │    48      │ All functionality            │
└────────────────┴────────────┴──────────────────────────────┘
```

---

**Status:** ✅ **100% COMPLETE AND ORGANIZED**
