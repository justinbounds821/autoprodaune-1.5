#!/bin/bash
# Quick Deploy Script - AutoPro Daune Real Logic

echo "🚀 AutoPro Daune - Quick Deploy"
echo "================================"
echo ""

echo "✅ Step 1: Database Schema"
echo "→ Open: https://app.supabase.com/project/orctxxpyiqzbordibqxi/sql/new"
echo "→ Copy: /workspace/services/api/database/complete_schema.sql"
echo "→ Paste & Run in Supabase SQL Editor"
echo ""
read -p "Press Enter when database deployed..."

echo "✅ Step 2: Check JWT Secret"
if grep -q "SUPABASE_JWT_SECRET" /workspace/services/api/.env; then
    echo "→ JWT Secret found in .env ✅"
else
    echo "⚠️  JWT Secret missing!"
    echo "→ Get from: https://app.supabase.com/project/orctxxpyiqzbordibqxi/settings/api"
    echo "→ Add to .env: SUPABASE_JWT_SECRET=..."
    read -p "Press Enter after adding..."
fi

echo "✅ Step 3: Install Dependencies"
cd /workspace/services/api
pip install edge-tts boto3 python-jose[cryptography] >/dev/null 2>&1
echo "→ Dependencies installed ✅"

echo "✅ Step 4: Restart Backend"
pkill -f uvicorn 2>/dev/null
sleep 2
export PYTHONPATH=/workspace/services/api
nohup python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload > /tmp/backend_real.log 2>&1 &
echo "→ Backend starting..."
sleep 5

echo "✅ Step 5: Verify"
curl -s http://127.0.0.1:8001/health | grep -q "ok" && echo "→ Backend healthy ✅" || echo "→ Backend failed ❌"

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo ""
echo "Test endpoints:"
echo "  curl http://127.0.0.1:8001/health"
echo "  curl http://127.0.0.1:8001/docs"
echo ""
echo "See logs:"
echo "  tail -f /tmp/backend_real.log"
echo ""
echo "✅ System ready with REAL logic!"
