# 🚀 Setup Guide - MCP Orchestrator for AutoPro Daune

## 📋 Prerequisites

- Node.js 18+ installed
- Git installed
- Cursor IDE
- Access to:
  - Linear workspace
  - GitHub repository
  - Supabase project

## 🔑 Step 1: Get API Keys

### Linear API Key
1. Go to https://linear.app/settings/api
2. Click "Create new API key"
3. Name it "MCP Orchestrator"
4. Copy the key (starts with `lin_api_`)

### GitHub Personal Access Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✅ repo (all)
   - ✅ workflow
   - ✅ project
   - ✅ write:packages
4. Generate and copy token (starts with `ghp_`)

### Supabase Keys
1. Go to your Supabase project settings
2. Go to API section
3. Copy:
   - Project URL (https://xxx.supabase.co)
   - `anon` public key
   - `service_role` key (for admin operations)

## ⚙️ Step 2: Install MCP Orchestrator

```bash
cd c:\Users\JJ\Desktop\autoprodaune-1.5\mcp-orchestrator
npm install
```

## 📝 Step 3: Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Linear
LINEAR_API_KEY=lin_api_YOUR_KEY_HERE
LINEAR_TEAM_ID=DEV  # or your team ID
LINEAR_WORKSPACE_ID=autopro-daune

# GitHub
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
GITHUB_REPO=your-username/autoprodaune-1.5
GITHUB_OWNER=your-username

# Supabase
SUPABASE_URL=https://orctxxpyiqzbordibqxi.supabase.co
SUPABASE_ANON_KEY=YOUR_ANON_KEY_HERE
SUPABASE_SERVICE_KEY=YOUR_SERVICE_KEY_HERE

# Project
PROJECT_PATH=c:\Users\JJ\Desktop\autoprodaune-1.5
GIT_BRANCH=safe/apply-2025-10-12
BACKEND_URL=http://127.0.0.1:8011
FRONTEND_URL=http://localhost:3006

# Agents (all enabled by default)
AGENT_CURSOR_ENABLED=true
AGENT_CLAUDE_ENABLED=true
AGENT_BROWSER_ENABLED=true
AGENT_CODEX_ENABLED=true
```

## 🏗️ Step 4: Build TypeScript

```bash
npm run build
```

This compiles TypeScript to `dist/index.js`.

## 🔌 Step 5: Configure Cursor MCP

Edit `c:\Users\JJ\.cursor\mcp.json`:

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
        "NODE_ENV": "production"
      }
    }
  }
}
```

**Important**: Use absolute paths with double backslashes `\\` on Windows.

## 🔄 Step 6: Restart Cursor

1. Close Cursor completely
2. Reopen Cursor
3. Open AutoPro Daune project
4. MCP servers will auto-connect

## ✅ Step 7: Verify Setup

In Cursor, ask Claude:

```
List available MCP tools
```

You should see:
- orchestrate_workflow
- linear_create_task
- github_create_issue
- supabase_query
- agent_dispatch
- browser_test
- api_test
- generate_report
- system_health_check
- ... (20+ tools total)

## 🧪 Step 8: Test with Sample Command

In Cursor, ask Claude:

```
Use the system_health_check tool to check the AutoPro Daune system health
```

Expected output:
```json
{
  "overall_status": "healthy",
  "services": {
    "backend": { "status": "healthy", "url": "http://127.0.0.1:8011" },
    "supabase": { "status": "healthy" },
    "linear": { "status": "healthy" },
    "github": { "status": "not_tested" }
  }
}
```

## 🎯 Step 9: Test Master Orchestration

In Cursor, ask Claude:

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

Expected behavior:
1. Creates Linear epic
2. Creates 6 Linear tasks
3. Creates 6 GitHub issues
4. Generates agent prompts
5. Saves report to `reports/WORKFLOW-xxx-report.md`

## 🐛 Troubleshooting

### Issue: "LINEAR_API_KEY not set"
**Fix**:
- Check `.env` file exists in `mcp-orchestrator/` folder
- Verify `LINEAR_API_KEY=lin_api_...` is set (no spaces)
- Restart Cursor

### Issue: "MCP server not connecting"
**Fix**:
- Check path in `mcp.json` is correct and absolute
- Run `npm run build` to ensure `dist/index.js` exists
- Check Cursor output panel for errors
- Restart Cursor

### Issue: "Cannot find module '@modelcontextprotocol/sdk'"
**Fix**:
```bash
cd mcp-orchestrator
npm install
npm run build
```

### Issue: "GitHub API: Bad credentials"
**Fix**:
- Regenerate GitHub token with correct scopes
- Update `GITHUB_TOKEN` in `.env`
- Restart Cursor

### Issue: "Supabase query failed"
**Fix**:
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct
- Test in browser: `https://orctxxpyiqzbordibqxi.supabase.co`
- Check Supabase project is not paused

## 📊 Verify Linear Setup

1. Go to https://linear.app/autopro-daune
2. Check that your team exists (e.g., "DEV")
3. Create labels:
   - `agent:cursor`
   - `agent:claude`
   - `agent:browser`
   - `agent:codex`
   - `priority:critical`
   - `priority:high`
   - `priority:medium`
   - `priority:low`

## 🔐 Security Notes

- `.env` file is in `.gitignore` - never commit API keys
- Use `service_role` key only for admin operations
- GitHub token should have minimal required scopes
- Linear API key should be workspace-specific

## 🎉 Success Indicators

✅ **Setup Complete** when:
1. `npm run build` succeeds with no errors
2. Cursor shows MCP tools available
3. `system_health_check` returns healthy status
4. `orchestrate_workflow` creates Linear tasks and GitHub issues

## 📚 Next Steps

- Read [README.md](README.md) for usage guide
- Try `orchestrate_workflow` with your own commands
- Customize agent prompts in `src/orchestrators/agent-dispatcher.ts`
- Add custom tools in `src/index.ts`

## 🤝 Need Help?

1. Check Cursor output panel (View → Output → MCP)
2. Check MCP server logs: `npm run dev` (watch mode)
3. Review [README.md](README.md) for examples
4. Check `.env` values are correct

---

**Setup Time**: ~15 minutes
**Difficulty**: Medium
**Once configured**: Works automatically! 🚀
