#!/usr/bin/env python
"""Test game launch endpoint after fix"""
import requests
import time

BASE = "http://127.0.0.1:5000"

print("Testing game launch after fix...\n")

# Wait a moment for server to be ready
time.sleep(1)

# Login first
sess = requests.Session()
print("1. Logging in...")
try:
    resp = sess.post(BASE + "/api/login", json={
        "email": "testuser@example.com",
        "password": "TestPass123"
    })
    print(f"   Status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"   Error: {resp.text}")
except Exception as e:
    print(f"   Error: {e}")
    exit(1)

# Test launch endpoint
print("\n2. Testing launch-game endpoint...")
try:
    resp = sess.post(BASE + "/launch-game", json={"game": "space_invaders"})
    print(f"   Status: {resp.status_code}")
    data = resp.json()
    print(f"   Response: {data}")
    
    if data.get("success"):
        print("\n✓ SUCCESS! Game should be launching in a new window!")
    else:
        print(f"\n✗ Error: {data.get('error')}")
except Exception as e:
    print(f"   Error: {e}")
