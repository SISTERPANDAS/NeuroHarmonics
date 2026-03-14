# TODO: Feedback & Support Pages Fix

## Task: Make Feedback and Support pages in User Dashboard fully functional with:
- Working star rating system (5 stars)
- Database connectivity
- Proper UI with contrasting colors
- All buttons/forms working

## Steps:

### Step 1: Update dashboard.html
- [x] Replace number input with 5-star clickable rating UI
- [x] Update form structure for better JSON handling
- [x] Add proper IDs and classes

### Step 2: Update dashboard.js
- [x] Fix submitFeedback() to send JSON properly
- [x] Fix sendSupportMessage() to send JSON properly  
- [x] Add star rating click handlers
- [x] Add success/error feedback to user

### Step 3: Update dashboard.css
- [x] Add star rating styles (gold stars, hover effects)
- [x] Improve text contrast (white text on dark backgrounds)
- [x] Improve input field contrast
- [x] Style submit buttons better

### Step 4: Update index.html (Landing Page)
- [x] Ensure star ratings display for feedbacks (already existed)
- [x] Improve contrast for testimonial section

## Files Edited:
1. templates/dashboard/dashboard.html ✓
2. static/dashboard/dashboard.js ✓
3. static/dashboard/dashboard.css ✓
4. app.py (email integration) ✓

## Email Configuration:
To enable email notifications, set these environment variables:
- SMTP_SERVER (default: smtp.gmail.com)
- SMTP_PORT (default: 587)
- SMTP_USERNAME (your email)
- SMTP_PASSWORD (your app password)
- FROM_EMAIL (default: neuroharmonics@gmail.com)

