import socket,sys,traceback
host='aws-1-ap-northeast-2.pooler.supabase.com'
port=6543
print('Resolving host...')
try:
    addr = socket.gethostbyname(host)
    print('Resolved to', addr)
except Exception:
    print('DNS resolution failed:')
    traceback.print_exc()
    sys.exit(2)

print('Testing TCP connect to', host, port)
try:
    s = socket.create_connection((host, port), timeout=5)
    print('TCP connect succeeded')
    s.close()
except Exception:
    print('TCP connect failed:')
    traceback.print_exc()
    sys.exit(3)
