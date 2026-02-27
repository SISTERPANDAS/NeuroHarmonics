import psycopg2, traceback, sys, socket
print('Python executable:', sys.executable)
print('Starting psycopg2 connect test...')
try:
    conn = psycopg2.connect(
        host='aws-1-ap-northeast-2.pooler.supabase.com',
        port=6543,
        user='postgres.pqeiqbqqrmzrkgeqrlkv',
        password='06Kingbeast#232328',
        dbname='postgres',
        connect_timeout=5,
        sslmode='require'
    )
    print('Connected OK')
    conn.close()
except Exception:
    print('Connection failed:')
    traceback.print_exc()
    sys.exit(2)
