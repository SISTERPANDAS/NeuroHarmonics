#!/usr/bin/env python
"""Simple test for community chat API"""
import requests

BASE = "http://127.0.0.1:5000"

# login to obtain session cookie
def login():
    sess = requests.Session()
    resp = sess.post(BASE + "/api/login", json={
        "email": "testuser@example.com",
        "password": "TestPass123"
    })
    print("login status", resp.status_code, resp.json())
    return sess

s = login()
print("posting message")
r = s.post(BASE + "/post-community", json={"message":"Hello world from test"})
print(r.status_code, r.text)

print("fetch dashboard to see message list")
r2 = s.get(BASE + "/dashboard")
print(r2.status_code, "dashboard contains community" , "Community Chat" in r2.text)
