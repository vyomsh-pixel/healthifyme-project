import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import database

@pytest.fixture
def client():
    from backend.database import initialise_database
    initialise_database()
    with TestClient(app) as test_client:
        yield test_client

def test_google_auth_new_user(client):
    unique_sub = "google_test_sub_9999"
    email = "test_google_runner@example.com"
    resp = client.post("/api/auth/google", json={
        "google_id": unique_sub,
        "email": email,
        "display_name": "Google Test Runner"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["user"]["username"] == email
    assert data["user"]["display_name"] == "Google Test Runner"

    # Test login again with the same google_id returns existing user
    resp_again = client.post("/api/auth/google", json={
        "google_id": unique_sub,
        "email": email
    })
    assert resp_again.status_code == 200
    data_again = resp_again.json()
    assert data_again["user"]["id"] == data["user"]["id"]

def test_google_auth_missing_fields(client):
    resp = client.post("/api/auth/google", json={})
    assert resp.status_code == 400
