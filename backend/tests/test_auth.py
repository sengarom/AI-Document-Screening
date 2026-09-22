from fastapi.testclient import TestClient
from app.main import app

def test_login_user_success():
    app.dependency_overrides.clear()
    client = TestClient(app)
    response = client.post("/api/auth/login", json={"email": "user@example.com", "password": "User@123"})
    assert response.status_code == 200
    assert response.json() == {"message": "Logged in successfully"}
    assert "session_id" in response.cookies

def test_login_admin_success():
    app.dependency_overrides.clear()
    client = TestClient(app)
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "Admin@123"})
    assert response.status_code == 200
    assert response.json() == {"message": "Logged in successfully"}
    assert "session_id" in response.cookies

def test_login_invalid_password():
    app.dependency_overrides.clear()
    client = TestClient(app)
    response = client.post("/api/auth/login", json={"email": "user@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "session_id" not in response.cookies

def test_me_after_login():
    app.dependency_overrides.clear()
    client = TestClient(app)
    client.post("/api/auth/login", json={"email": "user@example.com", "password": "User@123"})
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["role"] == "USER"

def test_logout():
    app.dependency_overrides.clear()
    client = TestClient(app)
    client.post("/api/auth/login", json={"email": "user@example.com", "password": "User@123"})
    # Logout
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    # Try me
    response2 = client.get("/api/auth/me")
    assert response2.status_code == 401

def test_protected_endpoint_rejects_unauthenticated():
    app.dependency_overrides.clear()
    client = TestClient(app)
    # Don't login
    response = client.get("/api/auth/me")
    assert response.status_code == 401
