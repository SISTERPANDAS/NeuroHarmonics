import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api/register'

test_cases = [
    # Valid registration
    {
        'name': 'Valid Registration',
        'data': {'fullName': 'John Doe', 'email': 'john.doe@example.com', 'password': 'ValidPass123'},
        'expected_status': 200
    },
    # Invalid email format
    {
        'name': 'Invalid Email Format',
        'data': {'fullName': 'Jane Smith', 'email': 'invalid.email', 'password': 'ValidPass123'},
        'expected_status': 400
    },
    # Weak password (no uppercase)
    {
        'name': 'Weak Password (no uppercase)',
        'data': {'fullName': 'Bob Johnson', 'email': 'bob.johnson@example.com', 'password': 'weakpass123'},
        'expected_status': 400
    },
    # Weak password (too short)
    {
        'name': 'Weak Password (too short)',
        'data': {'fullName': 'Alice Brown', 'email': 'alice.brown@example.com', 'password': 'Pass1'},
        'expected_status': 400
    },
    # Invalid name (with numbers)
    {
        'name': 'Invalid Name (with numbers)',
        'data': {'fullName': 'Charlie123', 'email': 'charlie@example.com', 'password': 'ValidPass123'},
        'expected_status': 400
    },
    # Missing fields
    {
        'name': 'Missing Password',
        'data': {'fullName': 'Diana Prince', 'email': 'diana@example.com'},
        'expected_status': 400
    },
    # Duplicate email
    {
        'name': 'Duplicate Email (should fail on 2nd attempt)',
        'data': {'fullName': 'Eve Wilson', 'email': 'eve.wilson@example.com', 'password': 'ValidPass123'},
        'expected_status': 200,
        'run_twice': True
    }
]

print("=" * 60)
print("REGISTRATION VALIDATION TEST SUITE")
print("=" * 60)

for test in test_cases:
    test_name = test['name']
    payload = test['data']
    expected = test['expected_status']
    
    print(f"\nTest: {test_name}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    # First request
    r = requests.post(BASE_URL, json=payload)
    print(f"Status: {r.status_code} (expected {expected})")
    response = r.json()
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if r.status_code == expected:
        print("✓ PASS")
    else:
        print("✗ FAIL")
    
    # Second request if needed (for duplicate test)
    if test.get('run_twice'):
        print("\n  Running again to test duplicate...")
        r2 = requests.post(BASE_URL, json=payload)
        print(f"  Status: {r2.status_code} (expected 400)")
        response2 = r2.json()
        print(f"  Response: {json.dumps(response2, indent=2)}")
        if r2.status_code == 400 and not response2.get('success'):
            print("  ✓ PASS (duplicate detected)")
        else:
            print("  ✗ FAIL (duplicate not detected)")

print("\n" + "=" * 60)
print("TEST SUITE COMPLETE")
print("=" * 60)
