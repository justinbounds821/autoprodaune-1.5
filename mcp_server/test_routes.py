"""Test script to validate route organization"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("=" * 60)
    print("🧪 Testing MCP Server Route Organization")
    print("=" * 60)
    
    # Test imports
    print("\n1️⃣ Testing imports...")
    from models import (
        ExecuteRequest,
        ExecuteResponse,
        TaskStatusResponse,
        OrchestrateWorkflowRequest,
        LinearTaskRequest,
        LinearUpdateRequest,
        GitHubIssueRequest,
        GitHubCommitRequest,
        SupabaseQueryRequest,
        SupabaseVerifyRequest,
        BrowserTestRequest,
        APITestRequest,
        GPTTestRequest,
    )
    print("   ✅ Models imported successfully")
    
    from routers import (
        health_router,
        tasks_router,
        workflows_router,
        tools_router,
        gpt_router,
    )
    print("   ✅ Routers imported successfully")
    
    # Test router structure
    print("\n2️⃣ Testing router structure...")
    
    routers = {
        "health_router": health_router,
        "tasks_router": tasks_router,
        "workflows_router": workflows_router,
        "tools_router": tools_router,
        "gpt_router": gpt_router,
    }
    
    for name, router in routers.items():
        print(f"   ✅ {name}: {len(router.routes)} routes")
    
    # Test main app
    print("\n3️⃣ Testing main app...")
    from main import app
    print(f"   ✅ App created: {app.title}")
    print(f"   ✅ Total routes: {len(app.routes)}")
    
    # List all routes
    print("\n4️⃣ Route summary:")
    routes_by_tag = {}
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = list(route.methods)
            path = route.path
            tags = getattr(route, 'tags', ['Untagged'])
            tag = tags[0] if tags else 'Untagged'
            
            if tag not in routes_by_tag:
                routes_by_tag[tag] = []
            routes_by_tag[tag].append(f"{', '.join(methods):10} {path}")
    
    for tag, routes in sorted(routes_by_tag.items()):
        print(f"\n   📁 {tag}:")
        for route in sorted(routes):
            print(f"      {route}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Route organization successful.")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
