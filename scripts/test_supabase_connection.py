#!/usr/bin/env python
"""Test Supabase PostgreSQL connection"""
import sys
from sqlalchemy import create_engine, text, inspect

SUPABASE_DB_URL = "postgresql://postgres.pqeiqbqqrmzrkgeqrlkv:06Kingbeast%232328@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres?sslmode=require"

print("=" * 70)
print("TESTING SUPABASE POSTGRESQL CONNECTION")
print("=" * 70)

try:
    print("\n1. Creating engine...")
    engine = create_engine(
        SUPABASE_DB_URL,
        connect_args={"connect_timeout": 10, "application_name": "NeuroHarmonics"},
        echo=False
    )
    print("   ✓ Engine created")

    print("\n2. Attempting connection...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.scalar()
        print(f"   ✓ Connected successfully!")
        print(f"   PostgreSQL version: {version[:60]}...")

    print("\n3. Checking existing tables...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if tables:
        print(f"   ✓ Found {len(tables)} table(s):")
        for table in tables:
            cols = inspector.get_columns(table)
            print(f"      - {table} ({len(cols)} columns)")
    else:
        print("   ℹ No tables found (will be created on first run)")

    print("\n" + "=" * 70)
    print("✓ SUPABASE CONNECTION SUCCESSFUL")
    print("=" * 70)
    sys.exit(0)

except Exception as e:
    print(f"\n✗ CONNECTION FAILED: {e}")
    print("\n" + "=" * 70)
    import traceback
    traceback.print_exc()
    sys.exit(1)
