# 🚀 Quick Start - ChatGPT cu Ngrok

## ⚡ Setup Instant (5 minute)

### Step 1: Pornește Sistemul MCP
```powershell
.\START_SYSTEM.ps1
```

Așteaptă până vezi:
```
✅ MCP Server started successfully on port 8012
✅ Orchestrator started successfully on port 3030
```

### Step 2: Instalează Ngrok (dacă nu ai)

**Windows:**
```powershell
# Download ngrok
choco install ngrok
# sau
scoop install ngrok
```

**Linux/Mac:**
```bash
# Download și install
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-*.tgz
sudo mv ngrok /usr/local/bin/
```

**Sau direct download:** https://ngrok.com/download

### Step 3: Autentifică Ngrok (prima dată)
1. Creează cont pe https://dashboard.ngrok.com/signup
2. Copiază authtoken din dashboard
3. Rulează:
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### Step 4: Expune MCP Server
```bash
ngrok http 8012
```

Vei vedea:
```
ngrok                                                                   

Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        Europe (eu)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc-123-def.ngrok-free.app -> http://localhost:8012

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

### Step 5: Copiază URL-ul HTTPS
Ia URL-ul de la "Forwarding":
```
https://abc-123-def.ngrok-free.app
```

### Step 6: Configurează ChatGPT

Deschide ChatGPT → Settings → New Connector:

```
Name:           AutoPro MCP Server
Description:    Model Context Protocol pentru automatizare
MCP Server URL: https://abc-123-def.ngrok-free.app
Authentication: API Key
Header Name:    X-API-Key
API Key Value:  dev-key-12345
```

✅ Bifează "I trust this application"
✅ Click "Create"

### Step 7: Testează

În ChatGPT, întreabă:
```
Can you check the health of the AutoPro MCP server?
```

Ar trebui să primești:
```json
{
  "status": "healthy",
  "service": "mcp_server",
  "version": "1.0.0",
  "port": 8012
}
```

## 🎯 Script Automat

Creează `start_with_ngrok.ps1`:

```powershell
# Start MCP System
Write-Host "🚀 Starting MCP System..." -ForegroundColor Cyan
Start-Job -ScriptBlock { 
    Set-Location $using:PWD
    .\START_SYSTEM.ps1 
}

# Wait for services
Start-Sleep -Seconds 10

# Start ngrok
Write-Host "🌐 Starting ngrok tunnel..." -ForegroundColor Cyan
$ngrokJob = Start-Job -ScriptBlock {
    ngrok http 8012 --log=stdout
}

# Wait for ngrok
Start-Sleep -Seconds 3

# Get ngrok URL
$ngrokUrl = (Invoke-RestMethod http://localhost:4040/api/tunnels).tunnels[0].public_url

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ MCP SYSTEM READY FOR CHATGPT!            ║" -ForegroundColor Green
Write-Host "╠═══════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║                                               ║" -ForegroundColor Green
Write-Host "║  🔗 ChatGPT URL:                             ║" -ForegroundColor Green
Write-Host "║     $ngrokUrl" -ForegroundColor Yellow
Write-Host "║                                               ║" -ForegroundColor Green
Write-Host "║  🔑 API Key:                                 ║" -ForegroundColor Green
Write-Host "║     dev-key-12345                            ║" -ForegroundColor Yellow
Write-Host "║                                               ║" -ForegroundColor Green
Write-Host "║  📋 Copy-paste în ChatGPT:                   ║" -ForegroundColor Green
Write-Host "║     Name: AutoPro MCP Server                 ║" -ForegroundColor White
Write-Host "║     URL: $ngrokUrl" -ForegroundColor White
Write-Host "║     Auth: API Key                            ║" -ForegroundColor White
Write-Host "║     Header: X-API-Key                        ║" -ForegroundColor White
Write-Host "║     Key: dev-key-12345                       ║" -ForegroundColor White
Write-Host "║                                               ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop..." -ForegroundColor Gray

# Keep running
while ($true) { Start-Sleep -Seconds 1 }
```

Apoi rulează:
```powershell
.\start_with_ngrok.ps1
```

## 🔍 Monitoring Ngrok

### Web Interface
Deschide http://localhost:4040 în browser pentru:
- Live requests
- Request/Response inspection
- Replay requests
- Traffic stats

### Command Line Status
```bash
# Check ngrok status
curl http://localhost:4040/api/tunnels

# Check MCP health through ngrok
curl https://your-ngrok-url.ngrok-free.app/health
```

## ⚠️ Limitări Ngrok Free

- **Session limited**: ~2 ore, apoi trebuie restart
- **URL changes**: La fiecare restart, URL nou (trebuie updatat în ChatGPT)
- **Request limit**: ~40 requests/min

### Soluții:
1. **Ngrok Pro**: URL persistent ($8/lună)
2. **Deploy Production**: Vercel/Railway cu URL permanent
3. **Local Only**: Folosește pentru testing, apoi deploy

## 🚀 Upgrade la Permanent URL

### Opțiunea 1: Ngrok Pro
```bash
# After upgrade la Pro
ngrok http 8012 --domain=autopro-mcp.ngrok.app
```

URL permanent: `https://autopro-mcp.ngrok.app`

### Opțiunea 2: Deploy Vercel
```bash
cd mcp_server
vercel --prod
```

URL permanent: `https://autopro-mcp.vercel.app`

### Opțiunea 3: Railway
```bash
cd mcp_server
railway up
railway domain
```

URL permanent: `https://autopro-mcp.up.railway.app`

## 🎉 Gata!

Acum ChatGPT poate:
- ✅ Crea Linear issues
- ✅ Gestiona GitHub PRs
- ✅ Query Supabase database
- ✅ Automatiza browser tasks
- ✅ Trimite Discord notifications
- ✅ Read/write files
- ✅ Execute complex tasks

**Enjoy your AI-powered automation! 🚀**
