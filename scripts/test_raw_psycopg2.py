#!/usr/bin/env python
"""Test Supabase connection with raw psycopg2"""
import psycopg2
import sys

# Try different credential formats
configs = [
    {
        "name": "URL-encoded password (# as %23)",
        "params": {
            "host": "aws-1-ap-northeast-2.pooler.supabase.com",
            "port": 6543,
            "database": "postgres",
            "user": "postgres.pqeiqbqqrmzrkgeqrlkv",
            "password": "06Kingbeast#2328",
            "sslmode": "require"
        }
    },
    {
        "name": "Without project in username",
        "params": {
            "host": "aws-1-ap-northeast-2.pooler.supabase.com",
            "port": 6543,
            "database": "postgres",
            "user": "postgres",
            "password": "06Kingbeast#2328",
            "sslmode": "require"
        }
    },
]

print("=" * 80)
print("TESTING SUPABASE CONNECTION WITH RAW PSYCOPG2")
print("=" * 80)

for config in configs:
    print(f"\n{config['name']}:")
    params = config['params']
    print(f"  User: {params['user']}")
    print(f"  Host: {params['host']}:{params['port']}")
    print("  Testing...", end=" ", flush=True)
    
    try:
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print("✓ SUCCESS!")
        print(f"  Connected! PostgreSQL: {version[:70]}...")
        
        # Get tables
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cur.fetchall()]
        print(f"  Tables found: {len(tables)}")
        for table in tables[:5]:
            print(f"    - {table}")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✓ SUPABASE CONNECTION WORKING!")
        print("=" * 80)
        print(f"\nSuccessful config:")
        print(f"  User: {params['user']}")
        print(f"  Host: {params['host']}:{params['port']}")
        sys.exit(0)
        
    except psycopg2.OperationalError as e:
        error_str = str(e).lower()
        if "password" in error_str:
            print("✗ AUTH FAILED")
        elif "timeout" in error_str:
            print("✗ TIMEOUT")
        else:
            print(f"✗ ERROR: {str(e)[:50]}")

print("\n" + "=" * 80)
print("✗ CONNECTION FAILED - CHECKING CREDENTIALS")
print("=" * 80)
print("\nPlease verify in Supabase Dashboard:")
print("1. Project Settings → Database")
print("2. Pool Mode: Connection pooler enabled")
print("3. Port: 6543 (for pooler)")
print("4. User: postgres (or postgres.[PROJECT_ID])")
print("5. Password: correct and no special characters escaped")
sys.exit(1)
