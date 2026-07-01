import os
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
import requests
import json

r = requests.post(f"{API_URL}/auth/login", json={"email": "alice@example.com", "password": "password"})
token = r.json().get("access_token")

print("Token:", token)
r2 = requests.get(f"{API_URL}/lending/borrowed", headers={"Authorization": f"Bearer {token}"})
print(r2.status_code)
print(json.dumps(r2.json(), indent=2))
