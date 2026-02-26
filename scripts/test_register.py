import requests

url = 'http://127.0.0.1:5000/api/register'
payload = {'fullName': 'Auto Test', 'email': 'ci_test_user4@example.com', 'password': 'pass12345'}

r = requests.post(url, json=payload)
print('STATUS:', r.status_code)
print('BODY:', r.text)
