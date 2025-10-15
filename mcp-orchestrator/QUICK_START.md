# ⚡ Quick Start - 5 Minutes to Orchestration

## 1️⃣ Install (2 min)

```powershell
cd c:\Users\JJ\Desktop\autoprodaune-1.5\mcp-orchestrator
powershell -ExecutionPolicy Bypass -File setup.ps1
```

## 2️⃣ Configure (2 min)

Edit `.env` file:

```env
LINEAR_API_KEY=lin_api_YOUR_KEY
GITHUB_TOKEN=ghp_YOUR_TOKEN
SUPABASE_URL=https://orctxxpyiqzbordibqxi.supabase.co
SUPABASE_ANON_KEY=YOUR_KEY
```

Get keys:
- Linear: https://linear.app/settings/api
- GitHub: https://github.com/settings/tokens (scopes: repo, workflow, project)
- Supabase: Project settings → API

## 3️⃣ Add to Cursor (1 min)

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
      "args": ["c:\\Users\\JJ\\Desktop\\autoprodaune-1.5\\mcp-orchestrator\\dist\\index.js"]
    }
  }
}
```

Restart Cursor.

## 4️⃣ Test (30 sec)

In Cursor, ask Claude:

```
Use system_health_check to check AutoPro Daune system
```

Expected: ✅ All services healthy

## 5️⃣ Orchestrate! (instant)

In Cursor, ask Claude:

```
Use orchestrate_workflow tool:

Command: "FIX AND TEST ALL CRITICAL ISSUES"
Context:
- project: AutoPro Daune
- branch: safe/apply-2025-10-12
- critical_issues: ["Supabase", "Frontend", "UTM"]
```

Claude will:
1. Create Linear epic + 6 tasks
2. Create 6 GitHub issues
3. Generate agent prompts
4. Display everything

Copy prompts → Execute in agents → Report back → Done! 🚀

---

**That's it!** Full multi-agent orchestration in 5 minutes.

## 🎯 What You Just Got

- ✅ Master orchestration through MCP
- ✅ Auto Linear task creation
- ✅ Auto GitHub issue creation
- ✅ Agent prompt generation (Claude, Cursor, Browser)
- ✅ Test automation (Playwright + API)
- ✅ Progress tracking
- ✅ Report generation

## 📚 Learn More

- [README.md](README.md) - Full documentation
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup
- [GPT_MASTER_PROMPT.md](GPT_MASTER_PROMPT.md) - Use with ChatGPT

## 🆘 Troubleshooting

**"MCP server not connecting"**
- Check path in mcp.json is absolute
- Run `npm run build`
- Restart Cursor

**"LINEAR_API_KEY not set"**
- Check `.env` exists
- No spaces around `=`
- Restart Cursor

**"Tools not appearing"**
- Wait 30 seconds after Cursor restart
- Check output panel (View → Output → MCP)

---

**Setup time**: 5 minutes
**Learning curve**: Minimal
**Power**: Maximum 💪
