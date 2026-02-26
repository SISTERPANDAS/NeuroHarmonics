"""Test multiple DSN variants against Supabase pooler to isolate auth issue"""
from sqlalchemy import create_engine, text
from urllib.parse import quote

host = "aws-1-ap-northeast-2.pooler.supabase.com"
port = 6543
project = "pqeiqbqqrmzrkgeqrlkv"
password_raw = "06Kingbeast#2328"
password_enc = quote(password_raw, safe='')

usernames = [
    f"postgres.{project}",
    "postgres",
]

passwords = [
    (password_raw, "raw"),
    (password_enc, "encoded")
]

results = []

for user in usernames:
    for pwd, tag in passwords:
        url = f"postgresql://{user}:{pwd}@{host}:{port}/postgres?sslmode=require"
        print("Testing:", url.replace(pwd, '***'))
        try:
            engine = create_engine(url, connect_args={"connect_timeout":10}, pool_pre_ping=True)
            with engine.connect() as conn:
                v = conn.execute(text("SELECT 1")).scalar()
                print("  SUCCESS -> returned:", v)
                results.append((user, tag, True, None))
        except Exception as e:
            err = str(e)
            print("  FAIL ->", err.splitlines()[0])
            results.append((user, tag, False, err.splitlines()[0]))

print("\nSummary:")
for r in results:
    user, tag, ok, err = r
    print(f"- user={user}, password={tag}, ok={ok}, err={err}")
