import os
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
import requests
import json
import uuid

# generate users
email1 = f"test_{uuid.uuid4().hex[:6]}@example.com"
email2 = f"test_{uuid.uuid4().hex[:6]}@example.com"
requests.post(f"{API_URL}/signup", json={"name": "Owner", "email": email1, "password": "password123A"})
requests.post(f"{API_URL}/signup", json={"name": "Collaborator", "email": email2, "password": "password123A"})

r = requests.post(f"{API_URL}/login", data={"username": email1, "password": "password123A"})
token1 = r.json().get("access_token")

r = requests.post(f"{API_URL}/login", data={"username": email2, "password": "password123A"})
token2 = r.json().get("access_token")

# Create shelf
r = requests.post(f"{API_URL}/shelves/", headers={"Authorization": f"Bearer {token1}"}, json={"name": "My Shared Shelf"})
shelf_id = r.json()["id"]

# Share shelf
r = requests.post(ff"{API_URL}/sharing/shelves/{shelf_id}", headers={"Authorization": f"Bearer {token1}"}, json={"email": email2, "role": "viewer"})
print("Share response:", r.status_code)

# Fetch shelves
r = requests.get(f"{API_URL}/shelves/", headers={"Authorization": f"Bearer {token1}"})
shelves = r.json()
target_shelf = next((s for s in shelves if s["id"] == shelf_id), None)
print("Target shelf has shares:", len(target_shelf["shares"]))
share_id = target_shelf["shares"][0]["id"]
print("Shared user name:", target_shelf["shares"][0]["user"]["name"])
print("Shared role:", target_shelf["shares"][0]["role"])

# Update role
r = requests.put(ff"{API_URL}/sharing/{share_id}", headers={"Authorization": f"Bearer {token1}"}, json={"role": "editor"})
print("Update role status:", r.status_code)

# Fetch shelves again to verify
r = requests.get(f"{API_URL}/shelves/", headers={"Authorization": f"Bearer {token1}"})
target_shelf = next((s for s in r.json() if s["id"] == shelf_id), None)
print("Updated role:", target_shelf["shares"][0]["role"])

# Try to update role as the collaborator (should fail)
r = requests.put(ff"{API_URL}/sharing/{share_id}", headers={"Authorization": f"Bearer {token2}"}, json={"role": "viewer"})
print("Collaborator trying to update (EXPECTED 403):", r.status_code)

# Remove collaborator
r = requests.delete(ff"{API_URL}/sharing/{share_id}", headers={"Authorization": f"Bearer {token1}"})
print("Delete status:", r.status_code)

# Fetch shelves again to verify removal
r = requests.get(f"{API_URL}/shelves/", headers={"Authorization": f"Bearer {token1}"})
target_shelf = next((s for s in r.json() if s["id"] == shelf_id), None)
print("Shares after delete:", len(target_shelf["shares"]))

