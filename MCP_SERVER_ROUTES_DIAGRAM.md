# MCP SERVER ROUTES ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MCP SERVER (Port 8012)                              │
│                         FastAPI Application                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │
                    ┌────────────────┴────────────────┐
                    │        main.py                  │
                    │  - App Configuration            │
                    │  - Middleware Setup             │
                    │  - Router Registration          │
                    │  - OpenAPI Customization        │
                    └────────────────┬────────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
    ┌─────────┐              ┌─────────────┐           ┌─────────────┐
    │ Models  │              │ Middleware  │           │   Config    │
    │         │              │             │           │             │
    │ - All   │              │ - CORS      │           │ - Settings  │
    │   Pydantic│            │ - Logging   │           │ - Env Vars  │
    │   Models │             │ - Health    │           │             │
    └─────────┘              └─────────────┘           └─────────────┘
          │
          │ (imported by all routers)
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ROUTERS DIRECTORY                                │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ├──────────────────┬──────────────┬──────────────┬──────────────┐
          │                  │              │              │              │
          ▼                  ▼              ▼              ▼              ▼
    ┌──────────┐      ┌──────────┐   ┌──────────┐  ┌──────────┐   ┌──────────┐
    │ health.py│      │ tasks.py │   │workflows │  │ tools.py │   │  gpt.py  │
    └──────────┘      └──────────┘   │   .py    │  └──────────┘   └──────────┘
          │                  │        └──────────┘       │              │
          │                  │              │            │              │
          │                  │              │            │              │
          ▼                  ▼              ▼            ▼              ▼

┌─────────────┐    ┌─────────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   HEALTH    │    │   TASKS     │    │WORKFLOWS │    │  TOOLS   │    │   GPT    │
│             │    │             │    │          │    │          │    │ DEV MODE │
└─────────────┘    └─────────────┘    └──────────┘    └──────────┘    └──────────┘
      │                   │                  │              │               │
      │                   │                  │              │               │
      ▼                   ▼                  ▼              ▼               ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│                            API ENDPOINTS                                    │
└─────────────────────────────────────────────────────────────────────────────┘

╔═════════════════════════════════════════════════════════════════════════════╗
║                        HEALTH ENDPOINTS (1)                                 ║
╚═════════════════════════════════════════════════════════════════════════════╝

    GET    /health
           ↳ System health check, orchestrator status


╔═════════════════════════════════════════════════════════════════════════════╗
║                        TASK ENDPOINTS (2)                                   ║
╚═════════════════════════════════════════════════════════════════════════════╝

    POST   /mcp/execute
           ↳ Execute free-form MCP task (async)
    
    GET    /mcp/task/{task_id}/status
           ↳ Get task execution status and results


╔═════════════════════════════════════════════════════════════════════════════╗
║                      WORKFLOW ENDPOINTS (1)                                 ║
╚═════════════════════════════════════════════════════════════════════════════╝

    POST   /mcp/workflows/orchestrate
           ↳ Orchestrate complex multi-step workflow


╔═════════════════════════════════════════════════════════════════════════════╗
║                        TOOL ENDPOINTS (11)                                  ║
╚═════════════════════════════════════════════════════════════════════════════╝

    ┌─────────────────────────────────────────────────────┐
    │           LINEAR INTEGRATION (3)                     │
    └─────────────────────────────────────────────────────┘
    
    POST   /mcp/tools/linear/task
           ↳ Create Linear task with title, description, priority
    
    PUT    /mcp/tools/linear/task
           ↳ Update Linear task status or add comment
    
    GET    /mcp/tools/linear/tasks?limit=50
           ↳ List Linear tasks


    ┌─────────────────────────────────────────────────────┐
    │           GITHUB INTEGRATION (2)                     │
    └─────────────────────────────────────────────────────┘
    
    POST   /mcp/tools/github/issue
           ↳ Create GitHub issue (can link to Linear task)
    
    POST   /mcp/tools/github/commit
           ↳ Create Git commit (can link to Linear/GitHub)


    ┌─────────────────────────────────────────────────────┐
    │          SUPABASE INTEGRATION (2)                    │
    └─────────────────────────────────────────────────────┘
    
    POST   /mcp/tools/supabase/query
           ↳ Execute database query (select/insert/update/delete)
    
    POST   /mcp/tools/supabase/verify
           ↳ Verify database fix matches expected state


    ┌─────────────────────────────────────────────────────┐
    │               TESTING TOOLS (2)                      │
    └─────────────────────────────────────────────────────┘
    
    POST   /mcp/tools/test/browser
           ↳ Execute browser E2E test with Playwright
    
    POST   /mcp/tools/test/api
           ↳ Execute API test with expected responses


    ┌─────────────────────────────────────────────────────┐
    │              SYSTEM TOOLS (1)                        │
    └─────────────────────────────────────────────────────┘
    
    GET    /mcp/tools/system/health?detailed=false
           ↳ Detailed system health check


╔═════════════════════════════════════════════════════════════════════════════╗
║                   GPT DEVELOPER MODE ENDPOINTS (4)                          ║
╚═════════════════════════════════════════════════════════════════════════════╝

    POST   /mcp/tools/gpt/orchestrate
           ↳ GPT-optimized workflow orchestration
           ↳ Enhanced response formatting for ChatGPT
    
    POST   /mcp/tools/gpt/create_task
           ↳ GPT-optimized Linear task creation
           ↳ Returns success/task_id/url/message
    
    POST   /mcp/tools/gpt/test
           ↳ Unified test endpoint (browser or API)
           ↳ GPT-friendly test results
    
    GET    /mcp/tools/gpt/status
           ↳ Comprehensive system status for GPT
           ↳ Overall status + all services


╔═════════════════════════════════════════════════════════════════════════════╗
║                      OPENAPI ENDPOINTS (auto)                               ║
╚═════════════════════════════════════════════════════════════════════════════╝

    GET    /openapi.json
           ↳ Full OpenAPI 3.0 schema (4310 characters)
    
    GET    /chatgpt/openapi.json
           ↳ ChatGPT-optimized schema (275 characters)
    
    GET    /docs
           ↳ Swagger UI interactive documentation
    
    GET    /redoc
           ↳ ReDoc documentation


┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL INTEGRATIONS                                │
└─────────────────────────────────────────────────────────────────────────────┘

                            ┌────────────────┐
                            │ Orchestrator   │
                            │ (Port 3030)    │
                            └────────────────┘
                                     ▲
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    │                │                │
          ┌─────────▼──────┐  ┌──────▼─────┐  ┌──────▼─────┐
          │ Linear API     │  │ GitHub API │  │ Supabase   │
          └────────────────┘  └────────────┘  └────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW EXAMPLE                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    ChatGPT Client
         │
         │ POST /mcp/tools/gpt/orchestrate
         │ { "command": "Create task and test", "context": {...} }
         │
         ▼
    GPT Router (gpt.py)
         │
         │ orchestrator.orchestrate_workflow(...)
         │
         ▼
    Orchestrator Client
         │
         │ HTTP → Orchestrator Service (Port 3030)
         │
         ▼
    Orchestrator Service
         │
         ├─► Linear API (create task)
         │
         ├─► GitHub API (create issue)
         │
         └─► Supabase API (verify data)
         │
         ▼
    Response formatted for GPT
         │
         │ { "success": true, "workflow_id": "...", "tasks": [...] }
         │
         ▼
    ChatGPT Client receives structured response


┌─────────────────────────────────────────────────────────────────────────────┐
│                         ROUTER STATISTICS                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    Router            Lines    Routes    Prefix              Tag
    ────────────────────────────────────────────────────────────────────────
    health.py           25        1      /                   Health
    tasks.py           100        2      /mcp                Tasks
    workflows.py        30        1      /mcp/workflows      Workflows
    tools.py           200       11      /mcp/tools          Tools
    gpt.py             130        4      /mcp/tools/gpt      GPT Dev Mode
    ────────────────────────────────────────────────────────────────────────
    TOTAL              485       19

    Supporting Files:
    - main.py          130 lines  (app configuration)
    - models.py        100 lines  (Pydantic models)
    - __init__.py       15 lines  (router exports)


┌─────────────────────────────────────────────────────────────────────────────┐
│                      BACKWARD COMPATIBILITY                                 │
└─────────────────────────────────────────────────────────────────────────────┘

    ✅ ALL ROUTES UNCHANGED
    ✅ ALL PATHS IDENTICAL
    ✅ ALL MODELS UNCHANGED
    ✅ ALL RESPONSES IDENTICAL
    ✅ 100% BACKWARD COMPATIBLE

    Only internal organization changed:
    - 605-line main.py → 6 focused routers (25-200 lines each)
    - Better maintainability
    - Same API surface


┌─────────────────────────────────────────────────────────────────────────────┐
│                         TESTING ENDPOINTS                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    # PowerShell Examples

    # 1. Health Check
    Invoke-WebRequest "http://127.0.0.1:8012/health"

    # 2. OpenAPI Schema
    Invoke-WebRequest "http://127.0.0.1:8012/openapi.json"

    # 3. Execute Task
    Invoke-WebRequest -Method POST `
      -Uri "http://127.0.0.1:8012/mcp/execute" `
      -ContentType "application/json" `
      -Body '{"task":"test","context":{}}'

    # 4. Orchestrate Workflow
    Invoke-WebRequest -Method POST `
      -Uri "http://127.0.0.1:8012/mcp/workflows/orchestrate" `
      -ContentType "application/json" `
      -Body '{"command":"test","context":{}}'

    # 5. Create Linear Task
    Invoke-WebRequest -Method POST `
      -Uri "http://127.0.0.1:8012/mcp/tools/linear/task" `
      -ContentType "application/json" `
      -Body '{"title":"Test Task"}'

    # 6. GPT Status
    Invoke-WebRequest "http://127.0.0.1:8012/mcp/tools/gpt/status"


┌─────────────────────────────────────────────────────────────────────────────┐
│                             SUMMARY                                         │
└─────────────────────────────────────────────────────────────────────────────┘

    ✅ 19 application routes organized into 5 logical routers
    ✅ 100% backward compatible - no API changes
    ✅ Reduced main.py from 605 lines to 130 lines
    ✅ Clear separation of concerns
    ✅ Easy to maintain and extend
    ✅ Better IDE support and navigation
    ✅ Follows FastAPI best practices
    ✅ OpenAPI documentation organized by tags
    ✅ Ready for ChatGPT Developer Mode integration


    STATUS: ✅ REFACTORING COMPLETE
    NEXT STEP: Deploy and test in Docker environment
```
