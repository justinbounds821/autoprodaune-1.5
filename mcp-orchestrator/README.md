# 🎯 AutoPro MCP Orchestrator

**FastMCP Master Orchestration Server** for coordinating multiple AI agents (Cursor, Claude, Browser, Codex) through a single interface.

## 🚀 Features

- **Master Orchestration**: Single command orchestrates entire workflows
- **Linear Integration**: Auto-create epics, tasks, and track progress
- **GitHub Integration**: Auto-create issues, PRs, and commits
- **Supabase Integration**: Query and verify database changes
- **Multi-Agent Dispatch**: Generate prompts for Cursor, Claude, Browser, Codex
- **Browser Testing**: Execute Playwright E2E tests
- **API Testing**: Test backend endpoints
- **Report Generation**: Comprehensive markdown/HTML/JSON reports

## 📦 Installation

```bash
cd mcp-orchestrator
npm install
```

## ⚙️ Configuration

1. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

2. Fill in your credentials:

```env
# Required
LINEAR_API_KEY=lin_api_xxxxx
LINEAR_TEAM_ID=your-team-id
GITHUB_TOKEN=ghp_xxxxx
GITHUB_REPO=your-username/autoprodaune-1.5
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=your-key
PROJECT_PATH=c:\Users\JJ\Desktop\autoprodaune-1.5

# Optional
OPENAI_API_KEY=sk-xxxxx (for GPT integration)
ANTHROPIC_API_KEY=sk-ant-xxxxx (for Claude API)
GOOGLE_DRIVE_FOLDER_ID=xxx (for report upload)
```

3. Build the TypeScript code:

```bash
npm run build
```

## 🔧 Setup in Cursor

Add to your `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "supabase": {
      "url": "https://mcp.supabase.com/mcp?project_ref=orctxxpyiqzbordibqxi",
      "headers": {}
    },
    "autopro-orchestrator": {
      "command": "node",
      "args": [
        "c:\\Users\\JJ\\Desktop\\autoprodaune-1.5\\mcp-orchestrator\\dist\\index.js"
      ],
      "env": {
        "PATH": "c:\\Users\\JJ\\Desktop\\autoprodaune-1.5\\mcp-orchestrator"
      }
    }
  }
}
```

Restart Cursor to load the MCP server.

## 📖 Usage

### In Cursor

Once configured, you'll have access to all MCP tools. Use them like this:

**1. Master Orchestration (Recommended)**

```
Use the orchestrate_workflow tool with this command:

"FIX AND TEST ALL CRITICAL ISSUES"

Context:
- project: AutoPro Daune
- branch: safe/apply-2025-10-12
- critical_issues: ["Supabase insert bug", "Frontend proxy", "UTM tracking"]
- current_status: "Supabase fix applied, needs testing"

Options:
- create_linear_tasks: true
- create_github_issues: true
- generate_report: true
```

This will:
1. Create Linear epic
2. Create 6 Linear tasks (one per issue)
3. Create GitHub issues linked to Linear
4. Generate copy-paste prompts for each agent
5. Generate comprehensive report

**2. Individual Tools**

```
# Create a Linear task
Use linear_create_task tool:
- title: "Fix landing page form"
- description: "Update Index.tsx"
- priority: 1
- labels: ["agent:cursor", "priority:high"]

# Test API endpoint
Use api_test tool:
- method: "POST"
- url: "http://127.0.0.1:8011/api/leads/"
- body: {"name": "Test", "phone": "0740123456"}
- expected_status: 200

# Run browser test
Use browser_test tool:
- test_name: "Landing Page Form"
- url: "http://localhost:3006"
- steps: [
    {action: "goto", value: "http://localhost:3006"},
    {action: "fill", selector: "input[name='name']", value: "Test"},
    {action: "click", selector: "button[type='submit']"}
  ]
```

## 🤖 Agent Prompts

The orchestrator generates ready-to-use prompts for each agent:

### Claude Code Agent

```
=== CLAUDE CODE AGENT ===
TASK: LINEAR-DEV-1
TITLE: Test backend health

INSTRUCTIONS:
1. Check if backend is running
2. Start if needed
3. Test health endpoint
...

SUCCESS CRITERIA:
Backend responds with 200 OK

COMMIT MESSAGE FORMAT:
fix(backend): test health check [LINEAR-DEV-1] [#123]
===
```

Copy this prompt to Claude Code and it will execute automatically.

### Cursor Agent

```
=== CURSOR AGENT ===
TASK: LINEAR-DEV-2
TITLE: Fix form validation

OPEN FILES:
- 02_FRONTEND_UI_CLEAN/src/pages/Index.tsx

CHANGES TO MAKE:
1. Add phone regex validation
2. Update error messages
...
===
```

Copy to Cursor AI Chat and it will apply changes.

### Browser Agent

```
=== BROWSER AGENT ===
TASK: LINEAR-DEV-3
TITLE: Test landing page

PLAYWRIGHT SCRIPT:
...generated Playwright code...

RUN:
1. Save as test-linear-dev-3.js
2. Run: node test-linear-dev-3.js
===
```

Save and run the generated test script.

## 📊 Workflow Example

### Single Master Command

**Input**:
```
orchestrate_workflow(
  command: "FIX AND TEST ALL CRITICAL ISSUES",
  context: {
    project: "AutoPro Daune",
    branch: "safe/apply-2025-10-12",
    critical_issues: ["Supabase insert", "Frontend proxy", "UTM tracking"]
  }
)
```

**Output**:
```
✅ Workflow Orchestration Complete

Workflow ID: WORKFLOW-1729012345678
Execution Time: 2500ms

## Linear Epic
ID: AUT-EPIC-1

## Tasks Created (6)

### LINEAR-DEV-1: Test backend health
- Agent: claude
- GitHub: #123
- Status: pending

### LINEAR-DEV-2: Test lead creation
- Agent: claude
- GitHub: #124
- Status: pending

... (4 more tasks)

## Agent Prompts (Copy-Paste Ready)

### LINEAR-DEV-1 - CLAUDE Agent
Estimated Time: 5 minutes

```
=== CLAUDE CODE AGENT ===
[full prompt here]
===
```

... (5 more prompts)

## Next Steps
Copy each agent prompt above and execute in the respective agent.
```

### Execute Agent Prompts

1. **Claude Code** (DEV-1, DEV-2, DEV-5):
   - Copy prompt from orchestrator output
   - Paste in Claude Code
   - Claude executes automatically
   - Reports back results

2. **Browser Agent** (DEV-3, DEV-4):
   - Copy Playwright script
   - Save as `test-dev-3.js`
   - Run: `node test-dev-3.js`
   - Verify results

3. **Cursor** (quick UI fixes):
   - Copy prompt
   - Paste in Cursor AI Chat
   - Cursor applies changes
   - Test manually

### Track Progress

All tasks are tracked in Linear. Update status after each completion:

```
Use linear_update_task:
- task_id: "LINEAR-DEV-1"
- status: "done"
- comment: "Backend health check passed. Response time: 150ms"
```

## 🔧 Available Tools

### Master Orchestration
- `orchestrate_workflow` - Orchestrate entire workflow with one command

### Linear
- `linear_create_epic` - Create epic
- `linear_create_task` - Create task
- `linear_update_task` - Update task status
- `linear_list_tasks` - List tasks with filters

### GitHub
- `github_create_issue` - Create issue
- `github_create_pr` - Create pull request
- `github_commit` - Create commit with proper formatting

### Supabase
- `supabase_query` - Execute query (select/insert/update/delete)
- `supabase_verify_fix` - Verify database changes

### Agent Dispatch
- `agent_dispatch` - Dispatch task to agent
- `agent_get_status` - Get agent task status

### Testing
- `browser_test` - Execute Playwright E2E test
- `api_test` - Test API endpoint

### Reporting
- `generate_report` - Generate comprehensive report

### Utility
- `system_health_check` - Check system health
- `analyze_codebase` - Analyze code for issues

## 🎯 GPT Integration (Future)

To use with ChatGPT as Master Coordinator:

```
Custom Instructions → "What would you like ChatGPT to know?"

I manage AutoPro Daune with MCP Orchestrator at:
c:\Users\JJ\Desktop\autoprodaune-1.5\mcp-orchestrator

When I give you a command, use the MCP tools to:
1. Create Linear tasks
2. Create GitHub issues
3. Generate agent prompts
4. Track progress
5. Generate reports

Always use the orchestrate_workflow tool for complex tasks.
```

Then in GPT:
```
Execute workflow: "FIX AND TEST ALL CRITICAL ISSUES"

Context:
- Project: AutoPro Daune
- Branch: safe/apply-2025-10-12
- Issues: ["Supabase", "Frontend", "UTM"]
```

GPT will use MCP tools to orchestrate everything.

## 🐛 Troubleshooting

### "LINEAR_API_KEY not set"
- Copy `.env.example` to `.env`
- Add your Linear API key from https://linear.app/settings/api

### "GITHUB_TOKEN not set"
- Get token from https://github.com/settings/tokens
- Scopes needed: repo, workflow, project

### "Module not found"
- Run `npm install`
- Run `npm run build`

### "MCP server not connecting"
- Check path in `.cursor/mcp.json` is absolute
- Restart Cursor after config changes
- Check `dist/index.js` exists (run `npm run build`)

## 📚 Architecture

```
┌─────────────────────────────────────────┐
│         MCP Orchestrator Server         │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Workflow Engine                │   │
│  │   - Analyze commands             │   │
│  │   - Create plans                 │   │
│  │   - Coordinate agents            │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌──────────┬──────────┬──────────┐   │
│  │ Linear   │ GitHub   │ Supabase │   │
│  │ Client   │ Client   │ Client   │   │
│  └──────────┴──────────┴──────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Agent Dispatcher               │   │
│  │   - Generate prompts             │   │
│  │   - Execute tests                │   │
│  │   - Track status                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Report Generator               │   │
│  │   - Markdown/HTML/JSON           │   │
│  │   - Local/Drive/Linear/GitHub    │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
            │
            ↓ MCP Protocol
┌─────────────────────────────────────────┐
│              Cursor IDE                  │
│  (or any MCP-compatible client)         │
└─────────────────────────────────────────┘
```

## 🤝 Contributing

This is a custom MCP server for AutoPro Daune project.

## 📝 License

MIT

---

**Built with FastMCP** | **Powered by Model Context Protocol**
