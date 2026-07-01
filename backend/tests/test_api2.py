import os
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
import requests
import json
import uuid

# generate a unique email to avoid unique constraint errors
email = f"test_{uuid.uuid4().hex[:6]}@example.com"
r1 = requests.post(f"{API_URL}/signup", json={"name": "Test", "email": email, "password": "password123"})

r = requests.post(f"{API_URL}/login", data={"username": email, "password": "password123"})
token = r.json().get("access_token")

r2 = requests.get(f"{API_URL}/lending/borrowed", headers={"Authorization": f"Bearer {token}"})
print("Borrowed response code:", r2.status_code)
print(json.dumps(r2.json(), indent=2))
