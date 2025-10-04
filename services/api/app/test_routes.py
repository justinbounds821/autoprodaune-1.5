#!/usr/bin/env python3
"""Test script to check router imports"""

import os
os.environ['SUPABASE_URL'] = 'https://orctxxpyiqzbordibqxi.supabase.co'
os.environ['SUPABASE_SERVICE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yY3R4eHB5aXF6Ym9yZGlicXhpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzkzMTkxNSwiZXhwIjoyMDczNTA3OTE1fQ.mqpjr7frHPqtQqLoZJiO-8e5KOP_yeX_AvCoEGbnYGY'

try:
    from routes.social import router
    print("✅ Social router imported successfully")
    print(f"Router prefix: {router.prefix}")
    print(f"Router tags: {router.tags}")
except Exception as e:
    print(f"❌ Social router error: {e}")

try:
    from routes.financial import router
    print("✅ Financial router imported successfully")
except Exception as e:
    print(f"❌ Financial router error: {e}")

try:
    from routes.health import router
    print("✅ Health router imported successfully")
except Exception as e:
    print(f"❌ Health router error: {e}")

try:
    from routes.leads import router
    print("✅ Leads router imported successfully")
except Exception as e:
    print(f"❌ Leads router error: {e}")
