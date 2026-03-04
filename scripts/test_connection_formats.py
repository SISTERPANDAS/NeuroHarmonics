#!/usr/bin/env python
"""Test different Supabase connection formats"""
import sys
from sqlalchemy import create_engine, text

# Try different connection string formats; allow env override for convenience
import os

default_password = "06Kingbeast%232328"  # URL-encoded password ("#" → "%23")

connection_strings = [
    {
        "name": "Neon (pooler) - ap-southeast-1",
        "url": "postgresql://neondb_owner:npg_oOATQs5K7iFc@ep-falling-cherry-a172ybng-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=disable"
    },
    {
        "name": "Pooler (port 6543) with encoded username",
        "url": f"postgresql://postgres.pqeiqbqqrmzrkgeqrlkv:{default_password}@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require"
    },
    {
        "name": "Pooler (port 5432) with encoded username",
        "url": f"postgresql://postgres.pqeiqbqqrmzrkgeqrlkv:{default_password}@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres?sslmode=require"
    },
    {
        "name": "Direct connection (port 5432 non-pooler)",
        "url": f"postgresql://postgres:{default_password}@db.pqeiqbqqrmzrkgeqrlkv.supabase.co:5432/postgres?sslmode=require"
    },
]

# if DATABASE_URL is defined in environment, try it first
env_url = os.environ.get("DATABASE_URL")
if env_url:
    connection_strings.insert(0, {"name": "From DATABASE_URL environment", "url": env_url})

print("=" * 80)
print("TESTING SUPABASE CONNECTION FORMATS")
print("=" * 80)

for config in connection_strings:
    print(f"\n\nTesting: {config['name']}")
    print(f"URL: {config['url'][:80]}...")
    print("-" * 80)
    
    try:
        engine = create_engine(
            config['url'],
            connect_args={"connect_timeout": 15},
            pool_size=5,
            max_overflow=10,
            echo=False
        )
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✓ CONNECTION SUCCESSFUL!")
            print(f"  PostgreSQL: {version[:70]}...")
            
            # Check existing tables
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"  Tables in database: {tables if tables else 'None (will be created on app startup)'}")
            
            print("\n" + "=" * 80)
            print("✓ READY TO RUN APP")
            print("=" * 80)
            sys.exit(0)
            
    except Exception as e:
        error_msg = str(e)
        if "password authentication failed" in error_msg:
            print(f"✗ Authentication failed - check credentials")
        elif "connection refused" in error_msg.lower():
            print(f"✗ Connection refused - check host and port")
        elif "timeout" in error_msg.lower():
            print(f"✗ Connection timeout - check network/firewall")
        else:
            print(f"✗ Error: {error_msg[:100]}")

print("\n" + "=" * 80)
print("✗ ALL CONNECTION ATTEMPTS FAILED")
print("=" * 80)
print("\nPlease verify:")
print("1. Supabase project URL and credentials are correct")
print("2. Network/firewall allows connection to Supabase")
print("3. Database user and password are correct")
sys.exit(1)
