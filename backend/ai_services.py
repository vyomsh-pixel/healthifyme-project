import os
import re
import json
import time
import base64
from typing import Any, List
from pydantic import BaseModel

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

# Lazy client — only created on first call so load_dotenv() has already run by then
_client = None


def _get_client():
    global _client
    if genai is None or types is None:
        return None
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
        try:
            http_opts = types.HttpOptions(timeout=15000)
            _client = genai.Client(api_key=api_key, http_options=http_opts)
        except Exception as e:
            print(f"Gemini client init error: {e}")
            return None
    return _client


# ---------------------------------------------------------------------------
# Offline Deterministic Food Database & Estimator
# ---------------------------------------------------------------------------

OFFLINE_FOOD_DB = {
    "roti": {"calories": 100, "protein_g": 3.0, "carbs_g": 20.0, "fat_g": 1.0},
    "chapati": {"calories": 100, "protein_g": 3.0, "carbs_g": 20.0, "fat_g": 1.0},
    "paratha": {"calories": 220, "protein_g": 4.0, "carbs_g": 28.0, "fat_g": 10.0},
    "rice": {"calories": 130, "protein_g": 2.5, "carbs_g": 28.0, "fat_g": 0.5},
    "chawal": {"calories": 130, "protein_g": 2.5, "carbs_g": 28.0, "fat_g": 0.5},
    "dal": {"calories": 120, "protein_g": 8.0, "carbs_g": 18.0, "fat_g": 2.5},
    "daal": {"calories": 120, "protein_g": 8.0, "carbs_g": 18.0, "fat_g": 2.5},
    "paneer": {"calories": 260, "protein_g": 18.0, "carbs_g": 4.0, "fat_g": 20.0},
    "egg": {"calories": 75, "protein_g": 6.0, "carbs_g": 0.6, "fat_g": 5.0},
    "eggs": {"calories": 150, "protein_g": 12.0, "carbs_g": 1.2, "fat_g": 10.0},
    "anda": {"calories": 75, "protein_g": 6.0, "carbs_g": 0.6, "fat_g": 5.0},
    "chicken": {"calories": 165, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6},
    "salad": {"calories": 50, "protein_g": 1.5, "carbs_g": 10.0, "fat_g": 0.5},
    "sabzi": {"calories": 90, "protein_g": 2.5, "carbs_g": 12.0, "fat_g": 4.0},
    "curd": {"calories": 100, "protein_g": 5.0, "carbs_g": 7.0, "fat_g": 5.0},
    "dahi": {"calories": 100, "protein_g": 5.0, "carbs_g": 7.0, "fat_g": 5.0},
    "yogurt": {"calories": 100, "protein_g": 5.0, "carbs_g": 7.0, "fat_g": 5.0},
    "milk": {"calories": 150, "protein_g": 8.0, "carbs_g": 12.0, "fat_g": 8.0},
    "idli": {"calories": 60, "protein_g": 2.0, "carbs_g": 12.0, "fat_g": 0.5},
    "dosa": {"calories": 160, "protein_g": 4.0, "carbs_g": 28.0, "fat_g": 4.0},
    "oats": {"calories": 150, "protein_g": 5.0, "carbs_g": 27.0, "fat_g": 3.0},
    "banana": {"calories": 90, "protein_g": 1.1, "carbs_g": 23.0, "fat_g": 0.3},
    "apple": {"calories": 80, "protein_g": 0.4, "carbs_g": 21.0, "fat_g": 0.3},
    "ghee": {"calories": 120, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 14.0},
    "butter": {"calories": 100, "protein_g": 0.1, "carbs_g": 0.0, "fat_g": 11.5},
    "fish": {"calories": 140, "protein_g": 22.0, "carbs_g": 0.0, "fat_g": 5.0},
    "khichdi": {"calories": 250, "protein_g": 8.0, "carbs_g": 45.0, "fat_g": 4.5},
}


def _estimate_food_offline(text: str) -> dict[str, Any]:
    lower = text.lower()
    matched = []
    tot_cal = 0
    tot_p = 0.0
    tot_c = 0.0
    tot_f = 0.0

    for key, val in OFFLINE_FOOD_DB.items():
        if re.search(r"\b" + re.escape(key) + r"\b", lower):
            matched.append(key)
            tot_cal += val["calories"]
            tot_p += val["protein_g"]
            tot_c += val["carbs_g"]
            tot_f += val["fat_g"]

    if not matched:
        tot_cal = 350
        tot_p = 12.0
        tot_c = 45.0
        tot_f = 10.0

    clean_name = text.strip()[:40] if text.strip() else "Meal"

    return {
        "food_name": clean_name,
        "calories": int(tot_cal),
        "protein_g": round(tot_p, 1),
        "carbs_g": round(tot_c, 1),
        "fat_g": round(tot_f, 1),
        "source": "offline_estimate",
        "is_offline_estimate": True,
    }


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

def generate_wellness_chat_reply(message: str, profile: dict[str, Any] | None, recent_history: list[dict[str, Any]]) -> str | None:
    """Generate a chat reply using Gemini, returning None if the API is unavailable."""
    client = _get_client()
    if not client:
        return "I am currently running in offline mode. For urgent health matters, please consult a healthcare professional."
        
    p = profile or {}
    
    # Format history for prompt
    history_text = "No recent activity."
    if recent_history:
        history_items = []
        for item in recent_history:
            kind = item.get("type", "Activity")
            date = str(item.get("created_at", ""))[:10]
            if kind == "FOOD":
                history_items.append(f"- {date}: Ate {item.get('food_name')} ({item.get('calories')} kcal)")
            elif kind == "BMI":
                history_items.append(f"- {date}: BMI check - {item.get('bmi')} ({item.get('category')})")
            elif kind == "SKIN":
                history_items.append(f"- {date}: Skin note - {', '.join(item.get('concerns', []))}")
            elif kind == "WORKOUT":
                history_items.append(f"- {date}: Workout completed ({item.get('total_calories')} kcal)")
        
        if history_items:
            history_text = "\n".join(history_items)

    prompt = f"""
    You are an AI Health Assistant for Health.io.
    You give general wellness information, but you CANNOT diagnose conditions or replace a qualified clinician.

    User Profile:
    Age: {p.get('age', 'Unknown')}
    Gender: {p.get('gender', 'Unknown')}
    Goal: {p.get('goal', 'General Fitness')}
    Activity Level: {p.get('activity_level', 'Unknown')}
    Diet Preference: {p.get('diet_preference', 'Unknown')}
    Bio/Notes: {p.get('bio', 'None')}

    Recent User Health Activity:
    {history_text}

    User Question:
    {message}

    Give:
    - personalized advice based on their profile and history
    - concise answers
    - practical suggestions
    - beginner-friendly explanations
    - use bullet points when possible
    
    Keep responses clean and readable. Do not use markdown headers (like # or ##) in standard chat replies, just bolding and bullets.
    """

    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini API Error (Chat attempt {attempt + 1}): {e}")
            time.sleep(0.5)

    return "AI chat is temporarily unreachable. Please refer to your saved activity history or check back in a few minutes."


# ---------------------------------------------------------------------------
# Meal Planning
# ---------------------------------------------------------------------------

class MealItem(BaseModel):
    name: str
    portion: str
    calories: int
    protein_g: int

class Meal(BaseModel):
    meal_type: str
    items: List[MealItem]
    total_calories: int
    total_protein_g: int

class MealPlanResult(BaseModel):
    plan_title: str
    daily_total_calories: int
    daily_total_protein_g: int
    meals: List[Meal]


def generate_ai_meal_plan(goal: str, diet_type: str, budget: float | None, meals: int, extra_instructions: str | None, profile: dict[str, Any] | None) -> str | None:
    """Generate a meal plan using Gemini, returning structured offline fallback if unavailable."""
    client = _get_client()
    if client:
        p = profile or {}
        prompt = f"""
        Create a personalized Indian meal plan.

        User Information:
        Goal: {goal}
        Diet Type: {diet_type}
        Budget per day: {f'Rs. {budget}' if budget else 'Not specified'}
        Meals Per Day: {meals}

        User Profile:
        Age: {p.get('age', 'Unknown')}
        Gender: {p.get('gender', 'Unknown')}
        Weight: {p.get('weight_kg', 'Unknown')} kg
        Height: {p.get('height_cm', 'Unknown')} cm
        Activity Level: {p.get('activity_level', 'Unknown')}

        Requirements:
        - Make the meal plan practical
        - Use mostly Indian foods or easily available ingredients
        - Include exactly {meals} meals (e.g. breakfast, lunch, dinner, snacks)
        - DO NOT give any fitness advice or health advice, ONLY the meal plan
        - DO NOT give user profile summary, ONLY the meal plan
        
        {f"Special instructions from the user (must follow these): {extra_instructions}" if extra_instructions else ""}
        """

        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=MealPlanResult,
                    ),
                )
                
                # Validate the JSON string returned by Gemini
                MealPlanResult.model_validate_json(response.text)
                return response.text
            except Exception as e:
                print(f"Gemini API Error (Meal, attempt {attempt + 1}): {e}")
                time.sleep(0.5)

    # Deterministic structured fallback plan
    fallback_plan = {
        "plan_title": f"Balanced Daily {diet_type} Plan (Offline Guide)",
        "daily_total_calories": 1850,
        "daily_total_protein_g": 72,
        "meals": [
            {
                "meal_type": "Breakfast",
                "items": [
                    {"name": "Poha or Vegetable Oats with peanuts", "portion": "1 medium bowl", "calories": 320, "protein_g": 9},
                    {"name": "Boiled eggs or sprout salad", "portion": "2 eggs / 1 cup sprouts", "calories": 150, "protein_g": 12}
                ],
                "total_calories": 470,
                "total_protein_g": 21
            },
            {
                "meal_type": "Lunch",
                "items": [
                    {"name": "Whole wheat rotis or brown rice", "portion": "2 rotis / 1 katori rice", "calories": 220, "protein_g": 6},
                    {"name": "Dal (moong or toor)", "portion": "1 large katori", "calories": 160, "protein_g": 10},
                    {"name": "Seasonal mixed vegetable sabzi", "portion": "1 katori", "calories": 110, "protein_g": 3},
                    {"name": "Cucumber and carrot curd salad", "portion": "1 small cup", "calories": 70, "protein_g": 4}
                ],
                "total_calories": 560,
                "total_protein_g": 23
            },
            {
                "meal_type": "Evening Snack",
                "items": [
                    {"name": "Roasted chana or green tea with almonds", "portion": "1 handful", "calories": 180, "protein_g": 7}
                ],
                "total_calories": 180,
                "total_protein_g": 7
            },
            {
                "meal_type": "Dinner",
                "items": [
                    {"name": "Grilled paneer or stir-fried greens & tofu", "portion": "150g", "calories": 380, "protein_g": 17},
                    {"name": "Warm dal soup or multigrain roti", "portion": "1 bowl", "calories": 260, "protein_g": 4}
                ],
                "total_calories": 640,
                "total_protein_g": 21
            }
        ]
    }
    return json.dumps(fallback_plan)


# ---------------------------------------------------------------------------
# Workout Generation
# ---------------------------------------------------------------------------

def generate_ai_workout(goal: str, level: str, location: str, duration: int, rest: int, weight_kg: float) -> list[dict[str, Any]] | None:
    """Generate a workout using Gemini, returning structured offline fallback if unavailable."""
    client = _get_client()
    workout_list = None
    
    if client:
        prompt = f"""
        Generate a workout plan.

        Goal: {goal}
        Experience Level: {level}
        Workout Location: {location}
        Workout Duration: {duration} minutes
        User Weight: {weight_kg} kg

        IMPORTANT:
        - Return ONLY a valid Python list of dictionaries
        - Do NOT add markdown formatting around the list (no ```python or ```json)
        - Do NOT add explanations
        - Give ONLY exercise names and a short form cue

        Example format:
        [
          {{
            "name": "Push Ups",
            "cue": "Keep body in a straight line"
          }},
          {{
            "name": "Bodyweight Squats",
            "cue": "Keep knees tracking over toes"
          }}
        ]

        Generate between 4 to 8 exercises depending on the level and duration.
        """

        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    )
                )
                text = response.text.strip().replace("```python", "").replace("```json", "").replace("```", "").strip()
                workout_list = json.loads(text)
                if isinstance(workout_list, list) and len(workout_list) > 0:
                    break
            except Exception as e:
                print(f"Gemini API Error (Workout attempt {attempt + 1}): {e}")
                time.sleep(0.5)

    if not workout_list:
        workout_list = [
            {"name": "Bodyweight Squats", "cue": "Keep chest tall, push knees out over toes"},
            {"name": "Push-Ups (or Incline Push-Ups)", "cue": "Maintain a firm plank position, elbows at 45 degrees"},
            {"name": "Glute Bridges", "cue": "Drive through heels, squeeze glutes at the top"},
            {"name": "Plank Hold", "cue": "Engage core, keep hips level with shoulders"},
            {"name": "Reverse Lunges", "cue": "Step back softly, lower back knee toward the floor"},
            {"name": "Bird Dogs", "cue": "Reach opposite arm and leg, maintain stable hips"}
        ]

    # Dynamic duration and calorie system
    total_seconds = duration * 60
    used_time = 0
    final_workout = []
    
    # Base calorie burn rate (approx 5.5 METs for resistance/circuit training)
    # Calories = MET * weight_kg * (time_in_hours)
    for exercise in workout_list:
        exercise_time = 45 if level == "Beginner" else 60 if level == "Intermediate" else 75
        if used_time + exercise_time + rest > total_seconds and len(final_workout) >= 3:
            break
            
        cal_burn = round(5.5 * weight_kg * (exercise_time / 3600), 1)
        name = exercise.get("name", "Exercise")
        cue = exercise.get("cue", "Maintain proper form")
        
        final_workout.append({
            "name": name, 
            "seconds": exercise_time, 
            "rest_seconds": rest,
            "estimated_calories": cal_burn, 
            "sets": "2-3 rounds", 
            "form_cue": cue,
            "video_search": f"https://www.youtube.com/results?search_query={name.replace(' ', '+')}+proper+form"
        })
        used_time += exercise_time + rest
        
    return final_workout


# ---------------------------------------------------------------------------
# Food Analysis
# ---------------------------------------------------------------------------

def analyze_food_text(text: str) -> dict[str, Any] | None:
    """Analyze a food description and return estimated nutritional info."""
    client = _get_client()
    if client:
        prompt = f"""
        Analyze this meal description: "{text}"
        Estimate the nutritional content.
        
        CRITICAL ANCHORS FOR YOUR ESTIMATION (USE THESE!):
        - 1 katori (standard Indian bowl) = ~150g of cooked dal, rice, or sabzi.
        - 1 spoonful = ~15g (tablespoon).
        - 1 teaspoonful = ~5g (teaspoon).
        - 1 fistful = ~30g.
        - 1 standard roti = ~30-40g.
        - 1 standard paratha = ~60-80g (depends on filling).
        - 1 standard cup = ~240ml.
        
        Return ONLY a raw JSON dictionary (no markdown, no formatting).
        Keys required:
        - "food_name": string (brief summarized name of the meal)
        - "calories": integer
        - "protein_g": float
        - "carbs_g": float
        - "fat_g": float
        """
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    )
                )
                output = response.text.strip().replace("```json", "").replace("```python", "").replace("```", "").strip()
                data = json.loads(output)
                if {"food_name", "calories", "protein_g", "carbs_g", "fat_g"}.issubset(data.keys()):
                    data["is_offline_estimate"] = False
                    data["source"] = "gemini_ai"
                    return data
            except Exception as e:
                print(f"Gemini API Error (Food Text Analysis attempt {attempt + 1}): {e}")
                time.sleep(0.5)

    return _estimate_food_offline(text)


def analyze_food_image(base64_image: str) -> dict[str, Any] | None:
    """Analyze a food image and return estimated nutritional info."""
    client = _get_client()
    if client:
        prompt = """
        Analyze this food image. Estimate the nutritional content per typical serving shown.
        Return ONLY a raw JSON dictionary (no markdown, no formatting).
        Keys required:
        - "food_name": string (brief name of the dish)
        - "calories": integer
        - "protein_g": float
        - "carbs_g": float
        - "fat_g": float
        """
        try:
            mime_type = "image/jpeg"
            clean_b64 = base64_image
            if "," in base64_image:
                header, clean_b64 = base64_image.split(",", 1)
                if header.startswith("data:"):
                    mime_type = header.split(";")[0].replace("data:", "")
                    
            image_bytes = base64.b64decode(clean_b64)
            
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[
                            prompt,
                            types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                        ],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                        )
                    )
                    text = response.text.strip().replace("```json", "").replace("```", "").strip()
                    data = json.loads(text)
                    if {"food_name", "calories", "protein_g", "carbs_g", "fat_g"}.issubset(data.keys()):
                        data["is_offline_estimate"] = False
                        data["source"] = "gemini_ai"
                        return data
                except Exception as e:
                    print(f"Gemini API Error (Food Image attempt {attempt + 1}): {e}")
                    time.sleep(0.5)
        except Exception as e:
            print(f"Failed decoding food image payload: {e}")

    return {
        "food_name": "Meal (Standard Serving)",
        "calories": 380,
        "protein_g": 12.0,
        "carbs_g": 48.0,
        "fat_g": 10.0,
        "source": "offline_estimate",
        "is_offline_estimate": True,
    }


# ---------------------------------------------------------------------------
# Skin Analysis (ZERO Synthetic Medical/Cosmetic Claims on Failure)
# ---------------------------------------------------------------------------

def analyze_skin_image(base64_image: str) -> dict[str, Any] | None:
    """Analyze a skin image and return concerns and summary.
    
    If Gemini is unavailable or errors, returns an explicit degraded state
    with zero fabricated dermatological conditions.
    """
    client = _get_client()
    if client:
        prompt = """
        Analyze this skin photo. Identify any visible cosmetic concerns. 
        IMPORTANT: You are a general wellness AI, NOT a doctor. Do not diagnose medical conditions. 
        Focus only on cosmetic features like: 'Acne / pimples', 'Dryness', 'Oiliness', 'Redness', 'Pigmentation', 'Dark circles'.
        Return ONLY a raw JSON dictionary (no markdown, no formatting).
        Keys required:
        - "concerns": list of strings (must only contain exact matches from the list above)
        - "summary": string (A brief, gentle observation of the skin condition, suggesting general, non-medical skincare tips like hydration, mild cleansing, or sunscreen. End with 'This is an AI observation, not a medical diagnosis.')
        """
        try:
            mime_type = "image/jpeg"
            clean_b64 = base64_image
            if "," in base64_image:
                header, clean_b64 = base64_image.split(",", 1)
                if header.startswith("data:"):
                    mime_type = header.split(";")[0].replace("data:", "")
                    
            image_bytes = base64.b64decode(clean_b64)
            
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[
                            prompt,
                            types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                        ],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                        )
                    )
                    text = response.text.strip().replace("```json", "").replace("```", "").strip()
                    data = json.loads(text)
                    if {"concerns", "summary"}.issubset(data.keys()):
                        data["status"] = "success"
                        data["is_offline_fallback"] = False
                        return data
                except Exception as e:
                    print(f"Gemini API Error (Skin Image attempt {attempt + 1}): {e}")
                    time.sleep(0.5)
        except Exception as e:
            print(f"Failed decoding skin image payload: {e}")

    # Explicit degraded state — strictly NO synthetic diagnoses or guesses
    return {
        "concerns": [],
        "summary": "AI image analysis is currently unavailable. Please log your observations and notes manually.",
        "status": "unavailable",
        "source": "offline_fallback",
        "is_offline_fallback": True,
    }
