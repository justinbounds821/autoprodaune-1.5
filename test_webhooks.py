#!/usr/bin/env python3
"""
🧪 COMPLETE WEBHOOK TESTING SCRIPT
Testează toate cele 6 webhook-uri funcționale ale sistemului AutoPro Daune
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8002"
TEST_IMAGE_PATH = "test_avatar.png"  # Creează un fișier de test sau folosește un placeholder

def create_test_avatar():
    """Creează o imagine de test pentru avatar."""
    try:
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (400, 400), color='blue')
        draw = ImageDraw.Draw(img)
        draw.text((150, 200), "TEST AVATAR", fill='white')
        img.save(TEST_IMAGE_PATH)
        print(f"✅ Created test avatar: {TEST_IMAGE_PATH}")
        return True
    except ImportError:
        print("⚠️ PIL not available, skipping test avatar creation")
        return False

def test_health():
    """Test 1: Health Check"""
    print("\n🏥 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health OK: {data}")
            return True
        else:
            print(f"❌ Health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health error: {e}")
        return False

def test_internal_video():
    """Test 2: Internal Video Generation"""
    print("\n🎥 Testing Internal Video Generation...")
    try:
        data = {
            'text': 'Test video generation pentru AutoPro Daune. Acest video a fost generat automat.',
            'voice_style': 'professional',
            'background_type': 'gradient',
            'aspect_ratio': '16:9',
            'resolution': '1080p'
        }
        
        response = requests.post(f"{BASE_URL}/api/video/internal-generate", data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Internal video generated: {result.get('message')}")
            print(f"   Video ID: {result.get('video_id')}")
            print(f"   Duration: {result.get('duration_seconds')}s")
            print(f"   Cost: {result.get('cost')} RON")
            return True
        else:
            print(f"❌ Internal video failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Internal video error: {e}")
        return False

def test_lipsync_video():
    """Test 3: Lip-sync Video Generation"""
    print("\n🎬 Testing Lip-sync Video Generation...")
    try:
        data = {
            'script': 'Salut, sunt Manole și vă explic cum să vă recuperați despăgubirile după un accident de mașină. Prima consultație este gratuită!',
            'voice_id': 'professional_male'
        }
        
        files = {}
        if Path(TEST_IMAGE_PATH).exists():
            files['avatar_image'] = open(TEST_IMAGE_PATH, 'rb')
        
        response = requests.post(f"{BASE_URL}/api/video/lipsync-generate", data=data, files=files, timeout=30)
        
        if files:
            files['avatar_image'].close()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Lip-sync video queued: {result.get('message')}")
            print(f"   Job ID: {result.get('job_id')}")
            print(f"   Provider: {result.get('provider')}")
            return result.get('job_id')
        else:
            print(f"❌ Lip-sync video failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Lip-sync video error: {e}")
        return None

def test_job_status(job_id):
    """Test 4: Job Status Check"""
    if not job_id:
        print("\n⏭️ Skipping job status test (no job ID)")
        return True
        
    print(f"\n📊 Testing Job Status Check for {job_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/video/job-status/{job_id}", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job status retrieved: {result.get('status')}")
            print(f"   Progress: {result.get('progress', 0)}%")
            if result.get('video_url'):
                print(f"   Video URL: {result.get('video_url')}")
            return True
        else:
            print(f"❌ Job status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Job status error: {e}")
        return False

def test_daily_summary():
    """Test 5: Daily Summary Video"""
    print("\n📈 Testing Daily Summary Video...")
    try:
        response = requests.post(f"{BASE_URL}/api/video/generate-daily-summary", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Daily summary generated: {result.get('message')}")
            print(f"   Video ID: {result.get('video_id')}")
            print(f"   Duration: {result.get('duration_seconds')}s")
            return True
        else:
            print(f"❌ Daily summary failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Daily summary error: {e}")
        return False

def test_business_analytics():
    """Test 6: Comprehensive Business Analytics"""
    print("\n📊 Testing Business Analytics...")
    try:
        response = requests.get(f"{BASE_URL}/api/advanced-bi/comprehensive-analytics?days_ahead=30", timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Business analytics retrieved: {result.get('status')}")
            
            data = result.get('data', {})
            overview = data.get('overview', {})
            print(f"   Total leads: {overview.get('total_leads', 'N/A')}")
            print(f"   Revenue (30 days): {overview.get('revenue_last_30_days', 'N/A')}")
            print(f"   Conversion rate: {overview.get('conversion_rate', 'N/A')}")
            
            predictions = data.get('predictions', {})
            print(f"   Predicted revenue: {predictions.get('predicted_revenue_next_30_days', 'N/A')}")
            
            return True
        else:
            print(f"❌ Business analytics failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Business analytics error: {e}")
        return False

def test_automated_decisions():
    """Test 7: Automated Business Decisions"""
    print("\n🤖 Testing Automated Business Decisions...")
    try:
        response = requests.get(f"{BASE_URL}/api/advanced-bi/automated-decisions", timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Automated decisions retrieved: {result.get('status')}")
            
            data = result.get('data', {})
            decisions = data.get('decisions', [])
            print(f"   Total decisions: {len(decisions)}")
            
            for i, decision in enumerate(decisions[:2], 1):  # Show first 2 decisions
                print(f"   Decision {i}: {decision.get('action', 'N/A')}")
                print(f"   Priority: {decision.get('implementation_priority', 'N/A')}")
                print(f"   Impact: {decision.get('expected_impact', 'N/A')}")
            
            summary = data.get('summary', {})
            print(f"   Estimated total impact: {summary.get('estimated_total_impact', 'N/A')}")
            
            return True
        else:
            print(f"❌ Automated decisions failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Automated decisions error: {e}")
        return False

def test_lead_video():
    """Test 8: Lead-based Video Generation (Mock)"""
    print("\n👤 Testing Lead-based Video Generation...")
    try:
        # Use a mock lead ID for testing
        lead_id = "test_lead_12345"
        data = {'video_type': 'testimonial'}
        
        response = requests.post(f"{BASE_URL}/api/video/generate-from-lead/{lead_id}", data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Lead video generated: {result.get('message')}")
            print(f"   Video ID: {result.get('video_id')}")
            return True
        else:
            print(f"❌ Lead video failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Lead video error: {e}")
        return False

def main():
    """Rulează toate testele webhook-urilor."""
    print("🚀 AUTO PRO DAUNE - WEBHOOK TESTING SUITE")
    print("=" * 50)
    
    # Create test avatar
    create_test_avatar()
    
    # Run tests
    tests_passed = 0
    total_tests = 8
    
    # Test 1: Health Check
    if test_health():
        tests_passed += 1
    
    # Test 2: Internal Video Generation
    if test_internal_video():
        tests_passed += 1
    
    # Test 3: Lip-sync Video Generation
    job_id = test_lipsync_video()
    if job_id:
        tests_passed += 1
    
    # Test 4: Job Status Check
    if test_job_status(job_id):
        tests_passed += 1
    
    # Test 5: Daily Summary Video
    if test_daily_summary():
        tests_passed += 1
    
    # Test 6: Business Analytics
    if test_business_analytics():
        tests_passed += 1
    
    # Test 7: Automated Decisions
    if test_automated_decisions():
        tests_passed += 1
    
    # Test 8: Lead-based Video
    if test_lead_video():
        tests_passed += 1
    
    # Cleanup
    if Path(TEST_IMAGE_PATH).exists():
        Path(TEST_IMAGE_PATH).unlink()
        print(f"\n🧹 Cleaned up test file: {TEST_IMAGE_PATH}")
    
    # Results
    print("\n" + "=" * 50)
    print(f"🎯 TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ ALL TESTS PASSED! System is fully functional.")
    elif tests_passed >= total_tests * 0.8:
        print("⚠️ Most tests passed. Check failed tests above.")
    else:
        print("❌ Multiple tests failed. Check backend configuration.")
    
    print("\n📋 Next steps:")
    print("1. Check failed tests above")
    print("2. Verify backend is running on localhost:8002")
    print("3. Check environment variables (.env file)")
    print("4. Review logs for detailed error messages")

if __name__ == "__main__":
    main()


