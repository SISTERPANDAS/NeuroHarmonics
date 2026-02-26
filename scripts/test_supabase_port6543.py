#!/usr/bin/env python
"""Test Supabase connection with correct port 6543"""
import sys
from sqlalchemy import create_engine, text

# Use the exact URL provided
SUPABASE_DB_URL = "postgresql://postgres.pqeiqbqqrmzrkgeqrlkv:06Kingbeast%232328@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require"

print("=" * 80)
print("TESTING SUPABASE POOLER CONNECTION (Port 6543)")
print("=" * 80)
print(f"\nURL: postgresql://postgres.pqeiqbqqrmzrkgeqrlkv:***@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres")

try:
    print("\n1. Creating SQLAlchemy engine...")
    engine = create_engine(
        SUPABASE_DB_URL,
        connect_args={
            "connect_timeout": 30,
            "application_name": "NeuroHarmonics"
        },
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False
    )
    print("   ✓ Engine created successfully")

    print("\n2. Testing connection...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.scalar()
        print(f"   ✓ Connected to PostgreSQL!")
        print(f"   Version: {version[:80]}...")

    print("\n3. Checking tables...")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """))
        tables = [row[0] for row in result.fetchall()]
        print(f"   ✓ Found {len(tables)} table(s):")
        for table in tables:
            print(f"      - {table}")

    print("\n" + "=" * 80)
    print("✓ SUPABASE CONNECTION SUCCESSFUL!")
    print("=" * 80)
    print("\nThe app will now use Supabase PostgreSQL for all data storage.")
    print("All team members' changes will sync instantly.")
    sys.exit(0)

except Exception as e:
    print(f"\n✗ CONNECTION FAILED")
    print(f"Error: {str(e)[:200]}")
    
    if "password authentication failed" in str(e).lower():
        print("\n⚠ Authentication Error:")
        print("  - Verify username: postgres.pqeiqbqqrmzrkgeqrlkv")
        print("  - Verify password: 06Kingbeast#2328")
        print("  - Check Supabase dashboard for correct credentials")
    elif "timeout" in str(e).lower():
        print("\n⚠ Connection Timeout:")
        print("  - Check firewall allows port 6543")
        print("  - Verify network connectivity")
        print("  - Check Supabase service status")
    
    print("\n" + "=" * 80)
    import traceback
    traceback.print_exc()
    sys.exit(1)
