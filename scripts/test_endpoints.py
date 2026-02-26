#!/usr/bin/env python
"""Test NeuroHarmonics app endpoints"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("=" * 80)
print("TESTING NEUROHARMONICS APP ENDPOINTS")
print("=" * 80)

tests = [
    {
        "name": "Home page",
        "method": "GET",
        "endpoint": "/",
        "expected": 200
    },
    {
        "name": "Login page",
        "method": "GET",
        "endpoint": "/login",
        "expected": 200
    },
    {
        "name": "Register page",
        "method": "GET",
        "endpoint": "/register",
        "expected": 200
    },
    {
        "name": "Register new user",
        "method": "POST",
        "endpoint": "/api/register",
        "data": {"fullName": "Test User", "email": "testuser@example.com", "password": "TestPass123"},
        "expected": 200
    },
    {
        "name": "Login with correct credentials",
        "method": "POST",
        "endpoint": "/api/login",
        "data": {"email": "testuser@example.com", "password": "TestPass123"},
        "expected": 200
    },
    {
        "name": "Dashboard (should redirect without login)",
        "method": "GET",
        "endpoint": "/dashboard",
        "expected": 302
    },
]

passed = 0
failed = 0

for test in tests:
    print(f"\n{test['name']}:")
    print(f"  {test['method']} {test['endpoint']}")
    
    try:
        if test['method'] == 'GET':
            r = requests.get(f"{BASE_URL}{test['endpoint']}", allow_redirects=False)
        else:
            r = requests.post(
                f"{BASE_URL}{test['endpoint']}", 
                json=test.get('data'),
                headers={"Content-Type": "application/json"}
            )
        
        if r.status_code == test['expected']:
            print(f"  Status: {r.status_code} ✓ PASS")
            if test['method'] == 'POST' and 'data' in test:
                try:
                    resp = r.json()
                    if 'success' in resp:
                        print(f"  Response: {resp['success']}")
                except:
                    pass
            passed += 1
        else:
            print(f"  Status: {r.status_code} ✗ FAIL (expected {test['expected']})")
            failed += 1
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)[:60]}")
        failed += 1

print("\n" + "=" * 80)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 80)

if failed == 0:
    print("\n✓ ALL TESTS PASSED - APP IS WORKING!")
    print(f"\nAccess the app at: {BASE_URL}")
else:
    print(f"\n✗ {failed} test(s) failed")
