import json
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import database, initialise_database
from backend.ai_services import _estimate_food_offline, generate_ai_meal_plan, generate_ai_workout


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SQLITE_DB_PATH", str(tmp_path / "test.sqlite3"))
    for env_key in ("DATABASE_URL", "SUPABASE_DB_URL", "POSTGRES_URL", "POSTGRES_PRISMA_URL", "GEMINI_API_KEY"):
        monkeypatch.delenv(env_key, raising=False)
    initialise_database()
    with TestClient(app) as test_client:
        yield test_client


def test_google_auth_new_user(client):
    unique_sub = "google_test_sub_9999"
    email = "test_google_runner@example.com"
    resp = client.post("/api/auth/google", json={
        "google_id": unique_sub,
        "email": email,
        "display_name": "Google Test Runner",
        "consent_accepted": True,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["user"]["username"] == email
    assert data["user"]["display_name"] == "Google Test Runner"

    # Test login again with the same google_id returns existing user
    resp_again = client.post("/api/auth/google", json={
        "google_id": unique_sub,
        "email": email,
    })
    assert resp_again.status_code == 200
    data_again = resp_again.json()
    assert data_again["user"]["id"] == data["user"]["id"]


def test_google_auth_missing_fields(client):
    resp = client.post("/api/auth/google", json={})
    assert resp.status_code == 400


def test_google_auth_rejects_forged_jwt(client):
    import base64
    header = base64.urlsafe_b64encode(b'{"alg":"none"}').decode().rstrip("=")
    payload = base64.urlsafe_b64encode(b'{"sub":"attacker","email":"victim@example.com"}').decode().rstrip("=")
    forged_token = f"{header}.{payload}.sig"
    resp = client.post("/api/auth/google", json={"idToken": forged_token})
    assert resp.status_code == 401


def test_account_export_and_delete(client):
    reg = client.post("/api/auth/register", json={
        "display_name": "Privacy User",
        "username": "privacy_user",
        "password": "Password1!",
        "consent_accepted": True,
    })
    assert reg.status_code == 201
    token = reg.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add profile, BMI record, checkin
    assert client.put("/api/profile", json={"age": 28, "goal": "Fitness"}, headers=headers).status_code == 200
    assert client.post("/api/records/bmi", json={"weight_kg": 70, "height_cm": 175}, headers=headers).status_code == 201
    assert client.put("/api/checkins/today?date=2026-10-11", json={"sleep_hours": 7.5, "water_glasses": 8}, headers=headers).status_code == 200

    # Verify date query param on checkins/today and dashboard
    checkin_resp = client.get("/api/checkins/today?date=2026-10-11", headers=headers)
    assert checkin_resp.status_code == 200
    assert checkin_resp.json()["checkin"]["sleep_hours"] == 7.5

    dash_resp = client.get("/api/dashboard?date=2026-10-11", headers=headers)
    assert dash_resp.status_code == 200
    assert dash_resp.json()["profile"]["age"] == 28

    # Export account data
    exp = client.get("/api/account/export", headers=headers)
    assert exp.status_code == 200
    exported = exp.json()
    assert exported["user"]["username"] == "privacy_user"
    assert exported["profile"]["age"] == 28
    assert len(exported["health_records"]) == 1
    assert len(exported["checkins"]) == 1
    assert "exported_at" in exported

    # Delete account
    del_resp = client.delete("/api/account", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json() == {"status": "deleted"}

    # Token should no longer authenticate
    assert client.get("/api/me", headers=headers).status_code == 401


def test_vegan_and_vegetarian_meal_fallback():
    vegan_json = generate_ai_meal_plan("Fat Loss", "Vegan", 250.0, 3, None, None)
    vegan_plan = json.loads(vegan_json)
    assert len(vegan_plan["meals"]) == 3
    vegan_text = vegan_json.lower()
    for forbidden in ("egg", "chicken", "fish", "meat", "paneer", "curd", "milk", "yogurt", "ghee", "butter", "chaas"):
        assert forbidden not in vegan_text

    veg_json = generate_ai_meal_plan("Muscle Gain", "Vegetarian", 300.0, 5, None, None)
    veg_plan = json.loads(veg_json)
    assert len(veg_plan["meals"]) == 5
    veg_text = veg_json.lower()
    for forbidden in ("egg", "chicken", "fish", "meat"):
        assert forbidden not in veg_text


def test_quantity_food_estimation():
    one_roti = _estimate_food_offline("1 roti")
    two_rotis = _estimate_food_offline("2 rotis")
    assert one_roti["calories"] == 100
    assert two_rotis["calories"] == 200
    assert two_rotis["protein_g"] == 6.0

    three_eggs = _estimate_food_offline("3 eggs")
    assert three_eggs["calories"] == 225
    assert three_eggs["protein_g"] == 18.0


def test_workout_fallback_location_and_calories():
    gym = generate_ai_workout("Muscle Gain", "Intermediate", "Gym", 30, 30, 70.0)
    home = generate_ai_workout("Fat Loss", "Beginner", "Home", 30, 30, 70.0)
    assert any("Goblet Squat" in ex["name"] or "Row" in ex["name"] for ex in gym)
    assert any("Bodyweight Squats" in ex["name"] for ex in home)
    # 5.5 * 70 * (60/3600) * 2.5 = 16.0 kcal for Intermediate 60s
    assert gym[0]["estimated_calories"] == round(5.5 * 70.0 * (60 / 3600) * 2.5, 1)


def test_rate_limiter_sqlite(client):
    headers = {"X-Forwarded-For": "203.0.113.42, 10.0.0.1"}
    for _ in range(5):
        r = client.post("/api/auth/login", json={"username": "nonexistent", "password": "wrong"}, headers=headers)
        assert r.status_code == 401
    r_blocked = client.post("/api/auth/login", json={"username": "nonexistent", "password": "wrong"}, headers=headers)
    assert r_blocked.status_code == 429

