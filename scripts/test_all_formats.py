#!/usr/bin/env python
"""Test Supabase connections with different password encodings"""
import sys
from urllib.parse import quote
from sqlalchemy import create_engine, text

password = "06Kingbeast#2328"
password_encoded = quote(password, safe='')

# Try with and without password encoding
connection_configs = [
    {
        "name": "Direct connection (unencoded password)",
        "url": f"postgresql://postgres:{password}@db.pqeiqbqqrmzrkgeqrlkv.supabase.co:5432/postgres"
    },
    {
        "name": "Direct connection (URL-encoded password)",
        "url": f"postgresql://postgres:{password_encoded}@db.pqeiqbqqrmzrkgeqrlkv.supabase.co:5432/postgres"
    },
    {
        "name": "Pooler connection (unencoded)",
        "url": f"postgresql://postgres.pqeiqbqqrmzrkgeqrlkv:{password}@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres"
    },
    {
        "name": "Pooler connection (encoded)",
        "url": f"postgresql://postgres.pqeiqbqqrmzrkgeqrlkv:{password_encoded}@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres"
    },
]

print("=" * 85)
print("SUPABASE CONNECTION TEST - TRYING MULTIPLE FORMATS")
print("=" * 85)

for config in connection_configs:
    print(f"\n{config['name']}:")
    # Hide password in display
    display_url = config['url'].replace(password, "***").replace(password_encoded, "***")
    print(f"  URL: {display_url}")
    print("  Testing...", end=" ", flush=True)
    
    try:
        engine = create_engine(
            config['url'],
            connect_args={"connect_timeout": 20},
            pool_pre_ping=True,
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_val = result.scalar()
            
        print("✓ SUCCESS!")
        print(f"  ✓ Connection verified!")
        
        # Show table info
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' LIMIT 10
            """))
            tables = [row[0] for row in result.fetchall()]
            table_count = len(tables)
            
        print(f"  ✓ Found {table_count} existing table(s): {tables}")
        
        print("\n" + "=" * 85)
        print("✓ CONNECTION SUCCESSFUL - Using this configuration")
        print("=" * 85)
        
        # Save the working URL for app.py
        print(f"\nWorking configuration:")
        print(f"SUPABASE_DB_URL = \"{config['url']}?sslmode=require\"")
        
        sys.exit(0)
        
    except Exception as e:
        error_str = str(e).lower()
        if "timeout" in error_str:
            print("✗ TIMEOUT")
        elif "auth" in error_str or "password" in error_str:
            print("✗ AUTH FAILED")
        else:
            print(f"✗ ERROR: {str(e)[:60]}")

print("\n" + "=" * 85)
print("✗ ALL ATTEMPTS FAILED")
print("=" * 85)
print("\nTroubleshooting steps:")
print("1. Verify credentials in Supabase dashboard")
print("2. Check if firewall blocks port 5432")
print("3. Check Supabase status page")
print("4. Verify database user exists and is enabled")
sys.exit(1)
