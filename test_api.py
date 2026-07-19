import requests

print("Registering...")
resp = requests.post("http://localhost:8001/api/auth/register", json={
    "username": "test_ai", "display_name": "AI", "password": "password123"
})
if resp.status_code == 409:
    print("Already registered, logging in...")
    resp = requests.post("http://localhost:8001/api/auth/login", json={
        "username": "test_ai", "password": "password123"
    })
    
print("Response:", resp.json())
token = resp.json().get("token")

if token:
    print("Testing chat endpoint...")
    chat_resp = requests.post(
        "http://localhost:8001/api/chat",
        json={"message": "I feel tired and want to eat something healthy."},
        headers={"Authorization": f"Bearer {token}"}
    )
    print("Chat Response:", chat_resp.json())

    print("Testing meal plan generation...")
    meal_resp = requests.post(
        "http://localhost:8001/api/meal-plans",
        json={
            "goal": "Weight loss",
            "diet_type": "Vegetarian",
            "budget": 500,
            "meals_per_day": 3,
            "extra_instructions": "Low carb"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    print("Meal Plan Response:", meal_resp.json())
