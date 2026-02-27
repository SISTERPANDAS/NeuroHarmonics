import sys, traceback, os
from sqlalchemy import create_engine, text

# Use the same URL as in app.py
URL = "postgresql://postgres.pqeiqbqqrmzrkgeqrlkv:06Kingbeast%232328@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require"

print('Python executable:', sys.executable)
print('Current cwd:', os.getcwd())

try:
    engine = create_engine(URL, connect_args={"connect_timeout": 5})
    with engine.connect() as conn:
        r = conn.execute(text('SELECT 1'))
        print('Query result:', r.scalar())
    print('Connection succeeded')
except Exception as e:
    print('Connection failed:')
    traceback.print_exc()
    sys.exit(2)
