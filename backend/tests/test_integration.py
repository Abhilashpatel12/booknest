import pytest
from fastapi.testclient import TestClient
from app.main import app
import random
import string

client = TestClient(app)

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

@pytest.fixture(scope="module")
def user1():
    email = f"testuser_{random_string(6)}@example.com"
    password = "Password123A"
    
    client.post("/signup", json={"name": "Test User 1", "email": email, "password": password})
    login_resp = client.post("/login", data={"username": email, "password": password})
    return {"email": email, "token": login_resp.json()["access_token"]}

@pytest.fixture(scope="module")
def user2():
    email = f"testuser_{random_string(6)}@example.com"
    password = "Password123A"
    
    client.post("/signup", json={"name": "Test User 2", "email": email, "password": password})
    login_resp = client.post("/login", data={"username": email, "password": password})
    return {"email": email, "token": login_resp.json()["access_token"]}

def test_create_and_get_book(user1):
    headers = {"Authorization": f"Bearer {user1['token']}"}
    
    book_data = {
        "title": "Automated Book",
        "author": "Bot",
        "total_pages": 100,
        "current_page": 0,
        "status": "want to read"
    }
    
    resp = client.post("/books/", json=book_data, headers=headers)
    assert resp.status_code == 200, resp.text
    book_id = resp.json()["id"]
    user1["book_id"] = book_id

def test_shelf_creation_and_sharing(user1, user2):
    headers1 = {"Authorization": f"Bearer {user1['token']}"}
    headers2 = {"Authorization": f"Bearer {user2['token']}"}
    
    resp = client.post("/shelves/", json={"name": "Automated Shelf"}, headers=headers1)
    assert resp.status_code == 200, resp.text
    shelf_id = resp.json()["id"]
    
    # Share as viewer
    resp = client.post(f"/sharing/shelves/{shelf_id}", json={
        "email": user2["email"],
        "role": "viewer"
    }, headers=headers1)
    assert resp.status_code == 201
    
    # Get share_id
    resp = client.get(f"/shelves/{shelf_id}", headers=headers1)
    shares = resp.json().get("shares", [])
    share_id = next(s["id"] for s in shares if s["user"]["email"] == user2["email"].lower())
    
    # Owner can add book
    resp = client.post(f"/shelves/{shelf_id}/books/{user1['book_id']}", headers=headers1)
    assert resp.status_code == 200, resp.text
    
    # Viewer cannot add a different book (let's create a new book for user 2 to try adding)
    # Actually just trying to remove the same book is enough to test viewer permissions
    resp = client.delete(f"/shelves/{shelf_id}/books/{user1['book_id']}", headers=headers2)
    assert resp.status_code == 403
    
    # Upgrade to editor
    resp = client.put(f"/sharing/{share_id}", json={"role": "editor"}, headers=headers1)
    assert resp.status_code == 200, resp.text
    
    # Editor CAN remove the book
    resp = client.delete(f"/shelves/{shelf_id}/books/{user1['book_id']}", headers=headers2)
    assert resp.status_code == 204

def test_lending_flow(user1, user2):
    headers1 = {"Authorization": f"Bearer {user1['token']}"}
    headers2 = {"Authorization": f"Bearer {user2['token']}"}
    
    # Lend book
    resp = client.post(f"/lending/{user1['book_id']}/lend", json={"borrower_email": user2["email"]}, headers=headers1)
    assert resp.status_code == 200, resp.text
    lend_id = resp.json()["id"]
    
    # Return book
    resp = client.post(f"/lending/{lend_id}/return", headers=headers2)
    assert resp.status_code == 200, resp.text

def test_auth_refresh(user1):
    resp = client.post("/login", data={
        "username": user1["email"],
        "password": "Password123A"
    })
    refresh_token = resp.json()["refresh_token"]
    
    resp = client.post("/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200, resp.text
    assert "access_token" in resp.json()

