import requests
import json
import base64

BASE_URL = "http://localhost:8001/api"
session = requests.Session()
token = None

def get_headers():
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def test_endpoint(name, method, url, **kwargs):
    print(f"\n--- Testing {name} ---")
    try:
        if 'headers' not in kwargs:
            kwargs['headers'] = get_headers()
        res = session.request(method, f"{BASE_URL}{url}", **kwargs)
        print(f"Status: {res.status_code}")
        if res.status_code >= 400:
            print("Error:", res.text)
        return res
    except Exception as e:
        print(f"Exception: {e}")
        return None

# 1. Auth
import time
username = f"testuser_{int(time.time())}"
res = test_endpoint("Register", "POST", "/auth/register", json={"display_name": "Test User", "username": username, "password": "Password123!"})
if res and res.status_code == 201:
    token = res.json().get("token")
    print("Registered and got token.")

# 2. Profile
test_endpoint("Get Profile (empty)", "GET", "/me")
test_endpoint("Update Profile", "PUT", "/profile", json={"age": 30, "gender": "Male", "height_cm": 180, "weight_kg": 75.5, "goal": "Fitness", "activity_level": "Moderate", "diet_preference": "Vegetarian", "bio": "Testing API"})
test_endpoint("Get Profile (updated)", "GET", "/me")

# 3. Records
test_endpoint("Add BMI", "POST", "/records/bmi", json={"weight_kg": 75.5, "height_cm": 180.0})
test_endpoint("Add Food Log", "POST", "/records/food", json={"food_name": "Apple", "calories": 95, "protein_g": 0.5, "carbs_g": 25.0, "fat_g": 0.3, "note": "Snack"})
test_endpoint("Add Skin Log", "POST", "/records/skin", json={"summary": "Skin looks clear.", "concerns": ["Acne / pimples"]})
test_endpoint("Get Records", "GET", "/records")

# 4. Checkin
test_endpoint("Today Checkin", "PUT", "/checkins/today", json={"sleep_hours": 7.5, "steps": 8000, "water_glasses": 8, "mood": 4, "energy": 4, "soreness": 2, "note": "Good day"})

# 5. Dashboard
test_endpoint("Dashboard", "GET", "/dashboard")

# 6. Chat
test_endpoint("Chat send", "POST", "/chat", json={"message": "Hello, how can I improve my sleep?"})
test_endpoint("Chat history", "GET", "/chat")
test_endpoint("Chat clear", "DELETE", "/chat")

# 7. Meal Plans
res = test_endpoint("Generate Meal Plan", "POST", "/meal-plans", json={"goal": "Fitness", "diet_type": "Vegetarian", "budget": 1000, "meals_per_day": 3, "extra_instructions": "Low sodium"})
test_endpoint("Get Meal Plans", "GET", "/meal-plans")

# 8. Workouts
res = test_endpoint("Generate Workout", "POST", "/workouts/generate", json={"goal": "Fitness", "level": "Beginner", "location": "Home", "duration_minutes": 30, "rest_seconds": 30, "weight_kg": 75.5})
if res and res.status_code == 200:
    workout_id = res.json().get("workout", {}).get("id")
    if workout_id:
        test_endpoint("Complete Workout", "POST", f"/workouts/{workout_id}/complete", json={"total_calories": 250.0})
test_endpoint("Get Workouts", "GET", "/workouts")

# 9. Vision Endpoints (using a tiny 1x1 base64 JPEG)
tiny_jpg = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAQGBAAAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAA/AFQf/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAhAAAAAAAAAAAAAAAAAAAAAA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAxAAAAAAAAAAAAAAAAAAAAAA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPwB//9k="
# Gemini will likely return an error about the image being too small or uninformative, but it should hit the API.
test_endpoint("Analyze Food (Dummy)", "POST", "/analyze-food", json={"image": tiny_jpg})
test_endpoint("Analyze Skin (Dummy)", "POST", "/analyze-skin", json={"image": tiny_jpg})

print("\n--- Tests Complete ---")
