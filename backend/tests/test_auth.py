import os
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
import requests
import json
import uuid

# generate a unique email
email = f"test_{uuid.uuid4().hex[:6]}@example.com"
r1 = requests.post(f"{API_URL}/signup", json={"name": "Test", "email": email, "password": "password123A"})
r = requests.post(f"{API_URL}/login", data={"username": email, "password": "password123A"})
print("Login Status:", r.status_code)
tokens = r.json()
access = tokens.get("access_token")
refresh = tokens.get("refresh_token")

# Test valid access token
res1 = requests.get(f"{API_URL}/books/", headers={"Authorization": f"Bearer {access}"})
print("Access token test:", res1.status_code)

# Test refresh token as access token (should fail)
res2 = requests.get(f"{API_URL}/books/", headers={"Authorization": f"Bearer {refresh}"})
print("Refresh token as access test (EXPECTED 401):", res2.status_code)

# Test valid refresh endpoint
res3 = requests.post(f"{API_URL}/refresh", json={"refresh_token": refresh})
print("Refresh token refresh test:", res3.status_code)

# Test access token as refresh token (should fail)
res4 = requests.post(f"{API_URL}/refresh", json={"refresh_token": access})
print("Access token as refresh test (EXPECTED 401):", res4.status_code)

