#!/usr/bin/env python
"""Test different Supabase connection formats"""
import sys
from sqlalchemy import create_engine, text

# Try different connection string formats
connection_strings = [
    {
        "name": "Pooler with base64-like username",
        "url": "postgresql://postgres.pqeiqbqqrmzrkgeqrlkv:06Kingbeast%232328@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres?sslmode=require"
    },
    {
        "name": "Direct connection (non-pooler)",
        "url": "postgresql://postgres:06Kingbeast%232328@db.pqeiqbqqrmzrkgeqrlkv.supabase.co:5432/postgres?sslmode=require"
    },
]

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
