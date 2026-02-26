#!/usr/bin/env python
"""Test game launch with direct requests"""
import requests
import time

BASE = "http://127.0.0.1:5000"
time.sleep(1)

# Login
sess = requests.Session()
resp = sess.post(BASE + "/api/login", json={
    "email": "testuser@example.com",
    "password": "TestPass123"
})
print("Login:", resp.status_code)

# Test game launch
print("Launching Space Invaders...")
resp = sess.post(BASE + "/launch-game", json={"game": "space_invaders"})
print("Status:", resp.status_code)
print("Response:", resp.json())
