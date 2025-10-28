# ✅ AutoPro Daune 1.5 - Browser Verification Checklist

**Purpose:** Verificare sistematică a tuturor funcționalităților prin browser  
**Prerequisites:** Backend și Frontend pornite (see START_SYSTEM.md)  
**Date:** 2025-10-10

---

## 🚀 BEFORE STARTING

### Pre-Flight Checks
```bash
# 1. Verifică backend running
curl http://127.0.0.1:8001/health
# Expected: {"status":"ok","service":"autopro-daune","port":8001}

# 2. Verifică frontend running  
curl http://localhost:3006
# Should return HTML (not error)

# 3. Open browser DevTools
# F12 → Console tab (watch for errors)
# F12 → Network tab (monitor API calls)
```

---

## ✅ VERIFICATION PROTOCOL

### Phase 1: CRITICAL FUNCTIONALITY (Must Pass)

#### 1.1 🔐 Authentication Flow
**URL:** http://localhost:3006

**Steps:**
```
□ 1. Open http://localhost:3006
   Expected: Redirect to /login

□ 2. Click "Register" (if available) or use existing account
   Test credentials: 
   - Email: test@autoprodaune.ro
   - Password: Test123!@#

□ 3. Submit login form
   Expected: 
   - No console errors
   - Redirect to /admin
   - JWT token in localStorage (F12 → Application → Local Storage)

□ 4. Test protected route without login:
   - Open new incognito window
   - Go to http://localhost:3006/admin
   Expected: Redirect to /login

□ 5. Logout
   - Click user menu → Logout
   Expected:
   - Redirect to /login
   - localStorage cleared
   - Can't access /admin

□ 6. Test invalid credentials
   - Enter wrong password
   Expected: Error message displayed
```

**Status:** ⬜ Pass | ⬜ Fail  
**Notes:** _______________________________________________

---

#### 1.2 📊 Dashboard Loading
**URL:** http://localhost:3006/admin

**Steps:**
```
□ 1. Login and navigate to dashboard
   Expected: Dashboard loads in <3 seconds

□ 2. Check all metric cards display:
   □ Total Leads (number)
   □ Videos Generated (number)
   □ Revenue This Month (RON amount)
   □ Social Followers (total count)

□ 3. Console check (F12):
   Expected: 0 errors, warnings acceptable

□ 4. Network check (F12 → Network):
   □ API call to /api/dashboard/overview - 200 OK
   □ Response time < 500ms
   □ Response JSON valid

□ 5. Responsive test:
   - F12 → Toggle device toolbar
   - Select iPhone SE (375x667)
   Expected: Layout adapts, no horizontal scroll

□ 6. Refresh page (Ctrl+R):
   Expected: Data reloads, no flash of empty state
```

**Status:** ⬜ Pass | ⬜ Fail  
**Notes:** _______________________________________________

---

#### 1.3 🎬 Video Generation (Internal Engine)
**URL:** http://localhost:3006/admin/videos

**Steps:**
```
□ 1. Navigate to Video Management tab

□ 2. Click "Create New Video" or similar button

□ 3. Fill video generation form:
   - Script: "AutoPro Daune vă ajută cu despăgubiri RCA"
   - Template: Select "Educational"
   - Duration: Auto or 30s
   - Background: Select option or upload image

□ 4. Click "Generate Video"
   Expected:
   - Success toast notification
   - Job ID returned
   - Status: "generating"
   - Progress indicator (if available)

□ 5. Wait 30-60 seconds, then refresh or auto-update
   Expected:
   - Status changes to "completed"
   - Video thumbnail appears
   - Preview button enabled

□ 6. Click "Preview" button
   Expected:
   - Video player opens (modal or new page)
   - Video plays smoothly
   - Audio audible (Romanian TTS)
   - WhatsApp CTA overlay visible (if configured)

□ 7. Click "Download" button
   Expected:
   - File downloads (.mp4 format)
   - File size 2-5 MB (for 30s video)
   - Video playable locally

□ 8. Error handling test:
   - Try generate without script
   Expected: Validation error before submit
```

**Status:** ⬜ Pass | ⬜ Fail  
**Notes:** _______________________________________________

---

### Phase 2: HIGH PRIORITY FEATURES

#### 2.1 👥 Lead Management
**URL:** http://localhost:3006/admin/leads

**Steps:**
```
□ CREATE Lead:
  1. Click "+ New Lead" button
  2. Fill form:
     - Name: "Ion Popescu Test"
     - Phone: "+40712345678"
     - Email: "ion.test@email.com"
     - Source: "TikTok"
     - Notes: "Lead de test pentru verificare"
  3. Click "Save"
  Expected: Success toast, lead appears in list

□ READ Lead:
  1. Find created lead in list
  2. Click to view details
  Expected: All fields display correctly, score calculated

□ UPDATE Lead:
  1. Click "Edit" on lead
  2. Change status to "Contacted"
  3. Add note: "Apelat client - interesat"
  4. Click "Save"
  Expected: Changes saved, timeline updated

□ DELETE Lead:
  1. Select test lead
  2. Click "Delete" (or trash icon)
  3. Confirm deletion
  Expected: Lead removed from list

□ TIMELINE:
  1. Click lead → "Timeline" button
  2. Verify activities shown:
     - Lead created (timestamp)
     - Status changed (timestamp)
     - Note added (timestamp)
  3. Add new note from timeline
  Expected: Note appears immediately

□ SCORING:
  1. Create lead with just name: Score = 0
  2. Add email: Score += 10
  3. Add phone: Score += 10
  4. Set source = "Referral": Score += 20
  Expected: Total score = 40

□ BULK OPERATIONS:
  1. Select 3 leads (checkboxes)
  2. Choose "Change Status" → "Qualified"
  3. Apply
  Expected: All 3 leads status updated

□ EXPORT:
  1. Click "Export CSV"
  2. Select all leads or filtered
  3. Download
  Expected: CSV file with correct data
```

**Status:** ⬜ Pass | ⬜ Fail  
**Notes:** _______________________________________________

---

#### 2.2 💰 Financial Dashboard
**URL:** http://localhost:3006/admin/financial

**Steps:**
```
□ REVENUE SECTION:
  1. Verify "Total Revenue" displays (RON)
  2. Select period: "Last 30 Days"
  3. Check breakdown shows:
     - Revenue by source (TikTok, Referrals, etc.)
     - Daily/weekly chart (if implemented)
  Expected: Data refreshes on period change

□ COSTS SECTION:
  1. Verify "Total Costs" displays (RON)
  2. Check breakdown:
     - API Costs (OpenAI, HeyGen, ElevenLabs)
     - Infrastructure (Supabase, R2, hosting)
     - Marketing (TikTok ads, Instagram ads)
  3. Verify percentages add to 100%
  Expected: Pie chart or table with correct distribution

□ PROFIT CALCULATION:
  1. Note Total Revenue: R
  2. Note Total Costs: C
  3. Verify Profit = R - C
  Expected: Math checks out, profit displayed

□ DATE RANGE FILTER:
  1. Click "Custom Range"
  2. Select: 2025-09-01 to 2025-09-30
  3. Apply filter
  Expected: Data updates to show only September

□ EXPORT CSV:
  1. Click "Export Report"
  2. Select format: CSV
  3. Choose date range
  4. Download
  Expected: 
  - File downloads: financial_report_YYYY-MM-DD.csv
  - Columns: Date, Type, Description, Amount, Currency
  - Data matches dashboard
```

**Status:** ⬜ Pass | ⬜ Fail  
**Notes:** _______________________________________________

---

#### 2.3 📱 Social Media Integration
**URL:** http://localhost:3006/admin/social

**Steps:**
```
□ YOUTUBE INTEGRATION:
  1. Locate YouTube card
  2. Click "Refresh" button
  3. Wait for API call
  Expected:
  - Subscriber count updates
  - Total views shown
  - Video count shown
  - Last updated timestamp

□ TIKTOK INTEGRATION:
  1. Check TikTok card status
  Expected: Shows "Connect TikTok" or follower count if OAuth done
  
  2. If needs OAuth:
     - Click "Connect TikTok"
     - Should redirect to TikTok auth page
     - Authorize app
     - Redirect back with token
     Expected: Follower count now loads

□ POST VIDEO TO SOCIAL:
  1. Click "New Post" or "Schedule Post"
  2. Select video from library
  3. Choose platforms: ☑ TikTok ☑ Instagram
  4. Enter caption: "AutoPro Daune - Despăgubiri RCA #RCA #asigurari"
  5. Add hashtags
  6. Schedule or post immediately
  Expected:
  - Job created
  - Status visible
  - After posting: verify manually on TikTok/Instagram

□ ANALYTICS:
  1. View "Analytics" tab
  2. Check metrics per platform:
     - Followers growth
     - Engagement rate
     - Top performing posts
  Expected: Charts/tables with real data
```

**Status:** ⬜ Pass | ⬜ Fail  
**Notes:** _______________________________________________

---

### Phase 3: MEDIUM PRIORITY FEATURES

#### 3.1 📁 File Upload System
**URL:** Various pages (Profile, Video Creator)

**Steps:**
```
□ UPLOAD PROFILE PICTURE:
  1. Go to Settings/Profile page
  2. Click "Upload Picture" or avatar
  3. Select image file (< 5MB, .jpg/.png)
  4. Click "Upload" or auto-upload
  Expected:
  - Upload progress bar (if large file)
  - Success notification
  - Image displays immediately
  - URL format: https://...r2.cloudflarestorage.com/...

□ UPLOAD VALIDATION:
  1. Try upload >10MB file
  Expected: Error "File too large"
  
  2. Try upload .exe file
  Expected: Error "Invalid file type"
  
  3. Upload without authentication
  Expected: 401 Unauthorized

□ UPLOAD FOR VIDEO:
  1. Video Creator → Upload Background Image
  2. Select accident photo
  3. Upload
  Expected:
  - Thumbnail preview
  - Image stored in R2
  - Usable in video generation

□ FILE PERSISTENCE:
  1. Upload image
  2. Logout
  3. Login again
  Expected: Uploaded image still displays
```

**Status:** ⬜ Pass | ⬜ Fail  
**Notes:** _______________________________________________

---

#### 3.2 🔔 Notification System
**URL:** All pages (toasts), dedicated Notifications page

**Steps:**
```
□ TOAST NOTIFICATIONS:
  1. Create a lead
  Expected: Green success toast "Lead created successfully"
  
  2. Try invalid action (e.g., empty form submit)
  Expected: Red error toast with message
  
  3. Start video generation
  Expected: Blue info toast "Video generation started"
  
  4. Check toast behavior:
     - Auto-dismiss after 3-5 seconds
     - Positioned top-right (or configurable)
     - Multiple toasts stack vertically
     - Close button works

□ EMAIL NOTIFICATIONS (if configured):
  1. Register new user with real email
  2. Check inbox
  Expected: Welcome email received
  
  3. Verify email content:
     - From: noreply@autoprodaune.ro (or configured)
     - Subject: "Welcome to AutoPro Daune"
     - Body: HTML formatted, logo, CTA button

□ IN-APP NOTIFICATION CENTER (if implemented):
  1. Look for bell icon in navbar
  2. Click bell
  Expected:
  - Dropdown with recent notifications
  - Badge with unread count
  - Notifications categorized
  
  3. Click a notification
  Expected: Navigates to relevant page
  
  4. Mark as read
  Expected: Badge count decreases
```

**Status:** ⬜ Pass | ⬜ Fail  
**Notes:** _______________________________________________

---

#### 3.3 🤖 Automation System
**URL:** http://localhost:3006/admin/automation

**Steps:**
```
□ AUTOMATION STATUS:
  1. View automation dashboard
  2. Check status: Enabled/Disabled
  3. View next scheduled run (should be 09:00, 15:00, or 21:00)
  4. Check daily progress: X/3 videos today

□ TOGGLE AUTOMATION:
  1. Click "Disable Automation" switch
  Expected: Status changes, next run cleared
  
  2. Enable again
  Expected: Status enabled, next run calculated

□ SCHEDULE CONFIGURATION:
  1. View posting times: 09:00, 15:00, 21:00
  2. If editable - change a time
  3. Save
  Expected: Schedule updated, next run recalculates

□ CONTENT TEMPLATES:
  1. View template rotation:
     - Educational: 40%
     - Testimonial: 30%
     - Promotional: 30%
  2. Edit template (if editable)
  3. Preview template
  Expected: Template preview shows correctly

□ AUTOMATION LOGS:
  1. Click "Logs" tab
  2. Verify recent entries shown:
     - Timestamp (sorted newest first)
     - Action: "video_generated", "posted_tiktok", etc.
     - Status: success/failed
     - Details or error message
  
  3. Filter logs:
     - By date range
     - By task type
     - By status
  
  4. Export logs
  Expected: CSV with all log entries

□ MANUAL TRIGGER (if available):
  1. Click "Run Now" or "Generate Video Now"
  Expected:
  - Automation executes immediately
  - Log entry created
  - Video generated and posted
```

**Status:** ⬜ Pass | ⬜ Fail  
**Notes:** _______________________________________________

---

### Phase 4: LOW PRIORITY FEATURES

#### 4.1 🎁 Referral System
**URL:** http://localhost:3006/admin/referrals

**Steps:**
```
□ REFERRAL CODE:
  1. View unique referral code (e.g., REF-ABC123)
  2. Click "Copy Code"
  Expected: Copied to clipboard confirmation
  
  3. View referral link
  Expected: Format: https://autoprodaune.ro/?ref=REF-ABC123

□ REFERRAL STATS:
  1. View dashboard metrics:
     - Total referrals
     - Pending referrals  
     - Confirmed referrals
     - Total earnings (count × 200 LEI)
     - Conversion rate %

□ CREATE TEST REFERRAL:
  1. Copy referral link
  2. Open in incognito/different browser
  3. Click link - verify tracking parameter
  4. Register new user
  5. Return to referral dashboard
  Expected:
  - New referral appears
  - Status: "Pending"
  - Referral details shown (user email, date)

□ CONFIRM REFERRAL:
  1. Simulate referred user completing qualifying action
  2. Check referral status
  Expected: Status → "Confirmed", reward added

□ REQUEST PAYOUT:
  1. If balance > 0, click "Request Payout"
  2. Enter bank details
  3. Submit request
  Expected:
  - Payout request created
  - Status: "Processing"
  - Email confirmation sent
```

**Status:** ⬜ Pass | ⬜ Fail  
**Notes:** _______________________________________________

---

## 🔍 CROSS-CUTTING VERIFICATION

### Performance
```
□ Page Load Times (F12 → Network → Disable cache):
  - Homepage: < 3s
  - Dashboard: < 3s
  - Any page: < 5s

□ API Response Times (F12 → Network → Check timing):
  - GET requests: < 500ms
  - POST requests: < 1s
  - File uploads: < 5s (for 5MB)

□ Memory Leaks:
  1. Open Performance tab (F12)
  2. Record session
  3. Navigate through pages
  4. Take heap snapshot
  Expected: No significant memory increase
```

### Responsive Design
```
□ Mobile (375px width):
  - Layout adapts
  - No horizontal scroll
  - Touch targets ≥44px
  - Navigation accessible

□ Tablet (768px width):
  - Columns adjust
  - Images scale
  - Sidebar behavior correct

□ Desktop (1920px width):
  - Full layout utilized
  - No excessive white space
  - Content centered or justified
```

### Accessibility
```
□ Keyboard Navigation:
  - Tab through all interactive elements
  - Enter/Space activate buttons
  - Esc closes modals

□ Screen Reader (basic test):
  - Alt text on images
  - Labels on form inputs
  - ARIA attributes where needed

□ Color Contrast:
  - Text readable on backgrounds
  - Meets WCAG AA standards
```

### Security
```
□ No secrets in client code:
  - View source - no API keys
  - LocalStorage - only client-safe data
  - Network tab - no sensitive data in URLs

□ HTTPS (in production):
  - All resources loaded over HTTPS
  - Mixed content warnings: 0

□ XSS Prevention:
  - User input sanitized
  - No eval() or dangerouslySetInnerHTML
```

---

## 📊 FINAL VERIFICATION SUMMARY

| Category | Items | Passed | Failed | Notes |
|----------|-------|--------|--------|-------|
| Authentication | 6 | __ | __ | _____________ |
| Dashboard | 6 | __ | __ | _____________ |
| Video Generation | 8 | __ | __ | _____________ |
| Lead Management | 7 | __ | __ | _____________ |
| Financial | 5 | __ | __ | _____________ |
| Social Media | 3 | __ | __ | _____________ |
| File Upload | 4 | __ | __ | _____________ |
| Notifications | 3 | __ | __ | _____________ |
| Automation | 6 | __ | __ | _____________ |
| Referrals | 5 | __ | __ | _____________ |
| **TOTAL** | **53** | **__** | **__** | **___________** |

**Pass Rate:** ___% (Target: >90%)

---

## ✅ SIGN-OFF

**Verification completed by:** _____________________  
**Date:** _____________________  
**Overall Status:** ⬜ Pass | ⬜ Conditional Pass | ⬜ Fail

**Critical Issues Found:** __________________________________________  
**Next Steps:** __________________________________________________

---

**AutoPro Daune 1.5 - Browser Verification Complete** 🎉
