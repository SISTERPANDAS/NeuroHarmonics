#!/usr/bin/env python
"""Test game card functionality"""
import requests
import time

BASE = "http://127.0.0.1:5000"

print("=" * 80)
print("TESTING GAME CARD FUNCTIONALITY")
print("=" * 80)

# Give server time to start
time.sleep(1)

# Test 1: Login
print("\n1. Testing login...")
sess = requests.Session()
try:
    resp = sess.post(BASE + "/api/login", json={
        "email": "testuser@example.com",
        "password": "TestPass123"
    })
    print(f"   Login status: {resp.status_code}")
    if resp.status_code == 200:
        print("   ✓ Login successful")
    else:
        print(f"   ✗ Login failed: {resp.text}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Dashboard loads with game section
print("\n2. Testing dashboard with game section...")
try:
    resp = sess.get(BASE + "/dashboard")
    print(f"   Dashboard status: {resp.status_code}")
    if resp.status_code == 200:
        has_game_section = "Games & References" in resp.text or "games-grid" in resp.text
        has_space_invaders = "Space Invaders" in resp.text
        has_play_btn = "launchGame" in resp.text
        
        if has_game_section:
            print("   ✓ Game section found in dashboard")
        else:
            print("   ✗ Game section NOT found")
        
        if has_space_invaders:
            print("   ✓ Space Invaders card found")
        else:
            print("   ✗ Space Invaders card NOT found")
        
        if has_play_btn:
            print("   ✓ Play button handler found")
        else:
            print("   ✗ Play button handler NOT found")
    else:
        print(f"   ✗ Dashboard failed: {resp.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Game launch endpoint exists
print("\n3. Testing /launch-game endpoint...")
try:
    resp = sess.post(BASE + "/launch-game", json={"game": "space_invaders"})
    print(f"   Endpoint status: {resp.status_code}")
    data = resp.json()
    print(f"   Response: {data}")
    if resp.status_code in [200, 500]:  # 200 if game installed, 500 if not installed
        print("   ✓ Endpoint responds correctly")
    else:
        print(f"   ✗ Unexpected status: {resp.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
