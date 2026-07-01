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

# Add a book for this user
book_res = requests.post(f"{API_URL}/books/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Test Book", "author": "Test Author", "isbn": "123", "status": "WANT_TO_READ"})
book_id = book_res.json().get("id")

# Create another user to borrow
email2 = f"test_{uuid.uuid4().hex[:6]}@example.com"
r2 = requests.post(f"{API_URL}/signup", json={"name": "Test Borrower", "email": email2, "password": "password123"})

# Lend the book
lend_res = requests.post(ff"{API_URL}/lending/{book_id}/lend", headers={"Authorization": f"Bearer {token}"}, json={"borrower_email": email2})
print(f"Lend Status: {lend_res.status_code}")
print("Lend Response:", lend_res.text)

# Check /lending/lent
lent_res = requests.get(f"{API_URL}/lending/lent", headers={"Authorization": f"Bearer {token}"})
print(f"Lent list Status: {lent_res.status_code}")
print("Lent List:", lent_res.text)

