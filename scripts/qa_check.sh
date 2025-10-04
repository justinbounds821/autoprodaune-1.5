#!/bin/bash

# AutoPro Daune - Script QA pentru verificarea completă a sistemului
# Verifică toate componentele și endpoint-urile

set -e  # Exit on any error

echo "🚀 AutoPro Daune - QA Check Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
ADMIN_URL="http://localhost:8501"

# Counter for results
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Function to run a check
check_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking $name... "
    
    if response=$(curl -s -w "%{http_code}" -o /dev/null "$url" 2>/dev/null); then
        if [ "$response" = "$expected_status" ]; then
            echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            echo -e "${RED}✗ FAIL${NC} (Expected HTTP $expected_status, got HTTP $response)"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (Connection error)"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

# Function to check API endpoint with JSON response
check_api_endpoint() {
    local name="$1"
    local url="$2"
    local expected_field="$3"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking API $name... "
    
    if response=$(curl -sSf "$url" 2>/dev/null); then
        if echo "$response" | grep -q "$expected_field"; then
            echo -e "${GREEN}✓ PASS${NC} (Contains $expected_field)"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            echo -e "${RED}✗ FAIL${NC} (Missing $expected_field)"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (API error)"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

echo -e "${BLUE}🔍 Backend API Checks${NC}"
echo "------------------------"

# Core API endpoints
check_endpoint "FastAPI Health" "$API_BASE_URL/health"
check_endpoint "FastAPI Docs" "$API_BASE_URL/docs"
check_endpoint "FastAPI OpenAPI" "$API_BASE_URL/openapi.json"

echo -e "\n${BLUE}📊 Financial API Checks${NC}"
echo "-------------------------"

check_api_endpoint "Financial Dashboard" "$API_BASE_URL/api/financial/dashboard" "total_costs"
check_api_endpoint "Financial Profit/Loss" "$API_BASE_URL/api/financial/profit-loss?start_date=2024-01-01&end_date=2024-12-31" "total_revenue"

echo -e "\n${BLUE}📱 Social Media API Checks${NC}"
echo "----------------------------"

check_api_endpoint "Social Summary" "$API_BASE_URL/api/social/summary" "total_posts"
check_api_endpoint "Social Posts" "$API_BASE_URL/api/social/posts" "posts"
check_api_endpoint "Social Analytics" "$API_BASE_URL/api/social/analytics" "total_engagement"

echo -e "\n${BLUE}🎬 Video API Checks${NC}"
echo "---------------------"

check_api_endpoint "Video Queue" "$API_BASE_URL/api/video/queue" "items"
check_api_endpoint "Video Stats" "$API_BASE_URL/api/video/stats" "total_jobs"

echo -e "\n${BLUE}📋 Leads API Checks${NC}"
echo "---------------------"

check_api_endpoint "Leads List" "$API_BASE_URL/api/leads" "leads"
check_endpoint "Leads Create" "$API_BASE_URL/api/leads" "405" # Should return Method Not Allowed for GET

echo -e "\n${BLUE}💬 WhatsApp API Checks${NC}"
echo "------------------------"

check_endpoint "WhatsApp Webhook" "$API_BASE_URL/api/whatsapp/webhook" "405" # Should return Method Not Allowed for GET
check_endpoint "WhatsApp Send" "$API_BASE_URL/api/whatsapp/send" "405" # Should return Method Not Allowed for GET

echo -e "\n${BLUE}🌐 Frontend Checks${NC}"
echo "--------------------"

check_endpoint "Frontend Home" "$FRONTEND_URL/"
check_endpoint "Frontend Dashboard" "$FRONTEND_URL/dashboard"
check_endpoint "Frontend Financial" "$FRONTEND_URL/financial"
check_endpoint "Frontend Social" "$FRONTEND_URL/social"
check_endpoint "Frontend Video" "$FRONTEND_URL/video"

echo -e "\n${BLUE}📊 Admin Dashboard Checks${NC}"
echo "----------------------------"

check_endpoint "Streamlit Admin" "$ADMIN_URL"

echo -e "\n${BLUE}🔧 Environment Checks${NC}"
echo "-------------------------"

# Check if .env file exists
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if [ -f ".env" ]; then
    echo -e "Environment file: ${GREEN}✓ PASS${NC} (.env exists)"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "Environment file: ${YELLOW}⚠ WARN${NC} (.env not found, using config.env)"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

# Check if config.env exists
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if [ -f "config.env" ]; then
    echo -e "Config file: ${GREEN}✓ PASS${NC} (config.env exists)"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "Config file: ${RED}✗ FAIL${NC} (config.env not found)"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

# Check Python dependencies
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if python -c "import fastapi, supabase, moviepy, streamlit" 2>/dev/null; then
    echo -e "Python dependencies: ${GREEN}✓ PASS${NC} (All required packages installed)"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "Python dependencies: ${RED}✗ FAIL${NC} (Missing packages)"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

# Check Node.js dependencies (if in frontend directory)
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if [ -d "auto-claim-hero" ] && [ -f "auto-claim-hero/package.json" ]; then
    if cd auto-claim-hero && npm list --depth=0 >/dev/null 2>&1; then
        echo -e "Node.js dependencies: ${GREEN}✓ PASS${NC} (All packages installed)"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "Node.js dependencies: ${RED}✗ FAIL${NC} (Missing packages)"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    cd ..
else
    echo -e "Node.js dependencies: ${YELLOW}⚠ SKIP${NC} (Frontend directory not found)"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

echo -e "\n${BLUE}📁 File Structure Checks${NC}"
echo "---------------------------"

# Check critical files
critical_files=(
    "services/api/app/main.py"
    "services/api/app/routes/financial.py"
    "services/api/app/routes/social.py"
    "services/api/app/routes/video.py"
    "services/api/app/routes/whatsapp.py"
    "services/api/app/services/supabase_client.py"
    "supabase_schema.sql"
    "auto-claim-hero/src/App.tsx"
    "auto-claim-hero/src/pages/Financial.jsx"
    "auto-claim-hero/src/pages/Social.jsx"
    "auto-claim-hero/src/pages/Video.jsx"
    "auto-claim-hero/src/components/WhatsAppForm.jsx"
    "auto-claim-hero/src/components/Navigation.jsx"
)

for file in "${critical_files[@]}"; do
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if [ -f "$file" ]; then
        echo -e "File $file: ${GREEN}✓ PASS${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "File $file: ${RED}✗ FAIL${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
done

echo -e "\n${BLUE}🎯 Summary${NC}"
echo "=========="
echo -e "Total checks: ${TOTAL_CHECKS}"
echo -e "Passed: ${GREEN}${PASSED_CHECKS}${NC}"
echo -e "Failed: ${RED}${FAILED_CHECKS}${NC}"

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All checks passed! System is ready.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some checks failed. Please review the errors above.${NC}"
    exit 1
fi
