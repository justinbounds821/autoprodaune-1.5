# 🔗 ChatGPT Connector Setup - Ghid Complet

## 📋 Informații de Conectare

### 🌐 URL și Credențiale

```
╔════════════════════════════════════════════╗
║   MCP SERVER CONNECTION DETAILS            ║
╠════════════════════════════════════════════╣
║                                            ║
║  🔗 Server URL:                            ║
║     http://localhost:8012                  ║
║     (sau https://your-domain.com)          ║
║                                            ║
║  🔐 Authentication Type:                   ║
║     API Key                                ║
║                                            ║
║  📝 Header Name:                           ║
║     X-API-Key                              ║
║                                            ║
║  🔑 API Key Value (Development):           ║
║     dev-key-12345                          ║
║                                            ║
║  🔑 API Key Value (Production):            ║
║     prod-key-67890                         ║
║                                            ║
╚════════════════════════════════════════════╝
```

## 🎯 Pași de Configurare în ChatGPT

### Pasul 1: Deschide ChatGPT Settings
1. Click pe **profilul tău** (stânga jos)
2. Click pe **Settings**
3. Navighează la secțiunea **Beta Features** sau **Integrations**

### Pasul 2: Activează MCP/Custom Actions
1. Caută opțiunea **"Custom GPT Actions"** sau **"MCP Connectors"**
2. **Activează** toggle-ul
3. Click pe **"New Connector"** sau **"Add Action"**

### Pasul 3: Completează Formularul (conform imaginii tale)

```
┌─────────────────────────────────────────────┐
│  New Connector                              │
├─────────────────────────────────────────────┤
│                                             │
│  Icon (optional)                            │
│  [ Upload Icon ]  Minimum 128 x 128 px      │
│                                             │
│  Name *                                     │
│  ┌───────────────────────────────────────┐ │
│  │ AutoPro MCP Server                    │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Description (optional)                     │
│  ┌───────────────────────────────────────┐ │
│  │ Model Context Protocol pentru         │ │
│  │ automatizare AutoPro                  │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  MCP Server URL *                          │
│  ┌───────────────────────────────────────┐ │
│  │ http://localhost:8012                 │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Authentication *                           │
│  ┌───────────────────────────────────────┐ │
│  │ API Key                         ▼     │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ⚠️  Beta intended for developer use only  │
│      Learn more                            │
│                                             │
│  ☐  I trust this application              │
│                                             │
│  📖  Read the guide                        │
│                                             │
│            [ Cancel ]    [ Create ]        │
│                                             │
└─────────────────────────────────────────────┘
```

### Pasul 4: Configurare API Key

După ce selectezi **"API Key"** în dropdown-ul Authentication:

```
┌─────────────────────────────────────────────┐
│  API Key Configuration                      │
├─────────────────────────────────────────────┤
│                                             │
│  Header Name *                              │
│  ┌───────────────────────────────────────┐ │
│  │ X-API-Key                             │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  API Key Value *                            │
│  ┌───────────────────────────────────────┐ │
│  │ dev-key-12345                         │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ℹ️  Pentru producție folosește:           │
│     prod-key-67890                         │
│                                             │
└─────────────────────────────────────────────┘
```

### Pasul 5: Trust și Salvare
1. ✅ **Bifează** "I trust this application"
2. Click pe **"Create"** sau **"Save"**
3. Așteaptă confirmarea **"Connection successful ✅"**

## 🧪 Testare Conexiune

### Test 1: În ChatGPT
Întreabă ChatGPT:
```
Can you check the health of the MCP server?
```

Răspuns așteptat:
```json
{
  "status": "healthy",
  "service": "mcp_server",
  "version": "1.0.0",
  "port": 8012
}
```

### Test 2: Direct API
```bash
curl -H "X-API-Key: dev-key-12345" \
     http://localhost:8012/api/gpt/capabilities
```

## 🌐 Deployment pentru Producție

### Opțiuni de Deploy

#### 1. Vercel (Recomandat pentru MCP Server)
```bash
cd mcp_server
vercel --prod
# Notează URL-ul: https://your-app.vercel.app
```

#### 2. Railway (Pentru ambele servicii)
```bash
# Deploy orchestrator
cd mcp_orchestrator
railway up

# Deploy MCP server  
cd mcp_server
railway up
```

#### 3. VPS/Cloud Server
```bash
# SSH în server
ssh user@your-server

# Clone repo
git clone your-repo
cd your-repo

# Setup și pornire
./START_SYSTEM.ps1  # Windows
# sau
bash start_system.sh  # Linux
```

### Actualizare URL în ChatGPT

După deploy:
1. **Edit Connector** în ChatGPT
2. **Actualizează MCP Server URL**:
   - De la: `http://localhost:8012`
   - La: `https://your-domain.com` sau `https://your-app.vercel.app`
3. **Actualizează API Key** la unul securizat:
   - Generează: `openssl rand -hex 32`
   - Adaugă în `.env`: `VALID_API_KEYS=["new-secure-key-here"]`
4. **Save** și **Test Connection**

## 🔒 Securitate

### Generare API Keys Securizate

```bash
# Linux/Mac
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# PowerShell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

### Best Practices

1. **HTTPS Obligatoriu** pentru producție
2. **API Keys unice** pentru fiecare environment
3. **Rate limiting** activat
4. **IP whitelist** dacă e posibil
5. **Logs monitorizate** pentru acces suspicious

## 📊 Capabilities Disponibile

ChatGPT va avea acces la:

### ✅ Linear Operations
- Creare și management issues
- Actualizare status tasks
- Queries pentru planning

### ✅ GitHub Operations  
- Creare issues și PRs
- Git commits
- Code management

### ✅ Database Operations
- Queries Supabase
- CRUD operations
- Analytics queries

### ✅ Browser Automation
- Web scraping
- Form filling
- Screenshots

### ✅ Notifications
- Discord webhooks
- Status updates
- Alerts

### ✅ File Operations
- Read/write files
- Code generation
- Config management

## 🎉 Exemple de Comenzi pentru ChatGPT

După conectare, poți să ceri:

```
1. "Create a Linear issue: Bug in auth system"

2. "Check Supabase for users registered today"

3. "Open https://example.com and take a screenshot"

4. "Send a Discord message: Deploy completed successfully"

5. "Read the config.json file and show me the settings"

6. "Create a GitHub PR for the feature branch"

7. "Execute a task: analyze user engagement metrics"
```

## 🆘 Troubleshooting

### Eroare: "Connection failed"
- ✅ Verifică că serverele rulează: `./START_SYSTEM.ps1`
- ✅ Check URL: trebuie să fie accesibil din browser
- ✅ Verifică firewall și ports (8012, 3030)

### Eroare: "Unauthorized"  
- ✅ API Key corect în ChatGPT
- ✅ Header name exact: `X-API-Key`
- ✅ API Key în `config.py`: `VALID_API_KEYS`

### Eroare: "Service unavailable"
- ✅ Check health: `curl http://localhost:8012/health`
- ✅ Check orchestrator: `curl http://localhost:3030/health`
- ✅ Restart: `pkill python && pkill node && ./START_SYSTEM.ps1`

### Pentru localhost din ChatGPT
⚠️ ChatGPT nu poate accesa localhost direct!

**Soluții**:
1. **Ngrok** (Quick test):
   ```bash
   ngrok http 8012
   # Folosește URL-ul ngrok în ChatGPT
   ```

2. **Deploy cloud** (Production):
   - Vercel, Railway, sau VPS
   - Folosește URL-ul public

## 📞 Support

- 📚 Docs: http://localhost:8012/docs
- 🔍 Schema: http://localhost:8012/api/gpt/schema
- 💬 Issues: Create în repo
- 📊 Logs: `/tmp/mcp_server.log`, `/tmp/orchestrator.log`

---

✅ **Sistemul este 100% funcțional și ready pentru ChatGPT!** 🚀
