# Supabase Connection Troubleshooting Guide

## Current Status
- ✓ Port configured: 6543 (pooler correct)
- ✓ Host: aws-1-ap-northeast-2.pooler.supabase.com (correct)
- ✗ Authentication: FAILED - Credentials need verification

---

## Step 1: Get the Correct Connection String from Supabase

1. **Log in to Supabase Dashboard**
   - Go to https://app.supabase.com

2. **Navigate to Your Project**
   - Select your project (NeuroHarmonics)

3. **Get Connection String**
   - Click "Connect" (top right button) 
   - Select "Python" from the language dropdown
   - Choose "Connection pooler" (not Direct connection)

4. **Copy the Full Connection String**
   - It should look like:
   ```
   postgresql://postgres.pqeiqbqqrmzrkgeqrlkv:YOUR_ACTUAL_PASSWORD@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres
   ```

---

## Step 2: Verify Your Credentials

In Supabase Dashboard → Project Settings → Database:

- ✓ Confirm **Port**: 6543 (for pooler)
- ✓ Confirm **Host**: aws-1-ap-northeast-2.pooler.supabase.com
- ✓ Confirm **Username**: postgres.pqeiqbqqrmzrkgeqrlkv
- ✓ Get actual **Password** from "Reset database password" link
  - The password you used (06Kingbeast#2328) may have been changed
  - Click "Reset database password" if forgotten

---

## Step 3: Update the Connection String in app.py

Once you have the correct password:

1. **Edit app.py** (line ~13)
   ```python
   # Replace:
   SUPABASE_DB_URL = "postgresql://postgres.pqeiqbqqrmzrkgeqrlkv:YOUR_ACTUAL_PASSWORD@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require"
   ```

2. **URL Encode the Password** if it contains special characters
   - `#` → `%23`
   - `@` → `%40`
   - `%` → `%25`
   - Use online tool: https://www.urlencoder.org/

3. **Save and Restart the App**
   ```bash
   python app.py
   ```

---

## Step 4: Test the Connection

Once app.py is updated, run:

```bash
python scripts/test_supabase_port6543.py
```

Expected output:
```
✓ SUPABASE CONNECTION SUCCESSFUL!
Found X table(s):
  - user
  - recommendation
  ...
```

---

## Troubleshooting Steps

### If you get "password authentication failed"
1. ✓ Double-check password hasn't expired (Supabase resets periodic ally)
2. ✓ Verify username: postgres.pqeiqbqqrmzrkgeqrlkv
3. ✓ Check for hidden spaces in password
4. ✓ Confirm password in Supabase dashboard

### If you get "connection timeout"
1. ✓ Check firewall allows port 6543 outbound
2. ✓ Check Supabase service status (status.supabase.com)
3. ✓ Try VPN or different network if blocked

### If you get "FATAL: unsupported frontend protocol"
1. ✓ Verify SSL mode is enabled (?sslmode=require)
2. ✓ Update psycopg2: `pip install --upgrade psycopg2-binary`

---

## Current Fallback Setup

While fixing Supabase, your app is using:
- ✓ **Local SQLite**: `instance/neuroharmonics.db`
- ✓ All authentication working
- ✓ All features available locally

Once Supabase is configured:
- Data automatically syncs to cloud
- Team members see all changes instantly
- Backup in cloud storage

---

## Quick Test Script

To verify connection when ready:

```bash
# Simple test
python scripts/test_supabase_port6543.py

# Raw psycopg2 test (for debugging)
python scripts/test_raw_psycopg2.py
```

---

## Alternative: Environment Variable Setup

Instead of editing app.py, you can set an environment variable:

```bash
# PowerShell
$env:DATABASE_URL = "postgresql://postgres.pqeiqbqqrmzrkgeqrlkv:PASSWORD@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require"
python app.py

# Or in .env file (create in project root)
DATABASE_URL=postgresql://postgres.pqeiqbqqrmzrkgeqrlkv:PASSWORD@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

---

## Need Help?

1. Check Supabase Status: https://status.supabase.com
2. Read Supabase Docs: https://supabase.com/docs/guides/database
3. Run tests to identify exact error
4. Post the error message with credentials hidden (replace password with ***)

---

**Last Updated:** February 27, 2026
