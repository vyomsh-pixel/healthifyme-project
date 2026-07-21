import os
import json
import random
from typing import Any

from google import genai
from google.genai import types
import base64
# Lazy client — only created on first call so load_dotenv() has already run by then
_client = None

def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
        try:
            _client = genai.Client(api_key=api_key)
        except Exception as e:
            print(f"Gemini client init error: {e}")
            return None
    return _client


def generate_wellness_chat_reply(message: str, profile: dict[str, Any] | None, recent_history: list[dict[str, Any]]) -> str | None:
    """Generate a chat reply using Gemini, returning None if the API is unavailable."""
    client = _get_client()
    if not client:
        return None
        
    p = profile or {}
    
    # Format history for prompt
    history_text = "No recent activity."
    if recent_history:
        history_items = []
        for item in recent_history:
            kind = item.get("type", "Activity")
            date = item.get("created_at", "").split("T")[0]
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

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini API Error (Chat): {e}")
        return None


def generate_ai_meal_plan(goal: str, diet_type: str, budget: float | None, meals: int, extra_instructions: str | None, profile: dict[str, Any] | None) -> str | None:
    """Generate a meal plan using Gemini, returning None if the API is unavailable."""
    client = _get_client()
    if not client:
        return None
        
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
    - Use a markdown list or simple table format
    - Use mostly Indian foods or easily available ingredients
    - Mention calories roughly
    - Mention protein sources
    - Include exactly {meals} meals (e.g. breakfast, lunch, dinner, snacks)
    - Keep formatting clean and simple
    - Avoid long paragraphs, use bullets
    - DO NOT give any fitness advice or health advice, ONLY the meal plan
    - DO NOT give user profile summary, ONLY the meal plan
    
    {f"Special instructions from the user (must follow these): {extra_instructions}" if extra_instructions else ""}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini API Error (Meal): {e}")
        return None


def generate_ai_workout(goal: str, level: str, location: str, duration: int, rest: int, weight_kg: float) -> list[dict[str, Any]] | None:
    """Generate a workout using Gemini, returning None if the API is unavailable."""
    client = _get_client()
    if not client:
        return None
        
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

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        text = response.text.strip()
        text = text.replace("```python", "").replace("```json", "").replace("```", "").strip()
        
        workout_list = json.loads(text)
        
        # Dynamic duration and calorie system
        total_seconds = duration * 60
        used_time = 0
        final_workout = []
        
        # Base calorie burn rate (approx 5.5 METs for general resistance/circuit training)
        # Calories = MET * weight_kg * (time_in_hours)
        
        for exercise in workout_list:
            # Calculate time per exercise based on level
            exercise_time = 45 if level == "Beginner" else 60 if level == "Intermediate" else 75
            
            if used_time + exercise_time + rest > total_seconds:
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
            
        if not final_workout:
            return None
            
        return final_workout
        
    except Exception as e:
        print(f"Gemini API Error (Workout): {e}")
        return None


def analyze_food_text(text: str) -> dict[str, Any] | None:
    """Analyze a food description and return estimated nutritional info."""
    client = _get_client()
    if not client:
        return None
        
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
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        output = response.text.strip()
        output = output.replace("```json", "").replace("```python", "").replace("```", "").strip()
        
        return json.loads(output)
    except Exception as e:
        print(f"Gemini API Error (Food Text Analysis): {e}")
        return None


def analyze_food_image(base64_image: str) -> dict[str, Any] | None:
    """Analyze a food image and return estimated nutritional info."""
    client = _get_client()
    if not client:
        return None
        
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
        # Strip potential data URI prefix e.g., "data:image/jpeg;base64,"
        if "," in base64_image:
            base64_image = base64_image.split(",")[1]
            
        image_bytes = base64.b64decode(base64_image)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            ]
        )
        
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
        
    except Exception as e:
        print(f"Gemini API Error (Food Image): {e}")
        return None


def analyze_skin_image(base64_image: str) -> dict[str, Any] | None:
    """Analyze a skin image and return concerns and summary."""
    client = _get_client()
    if not client:
        return None
        
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
        if "," in base64_image:
            base64_image = base64_image.split(",")[1]
            
        image_bytes = base64.b64decode(base64_image)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            ]
        )
        
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
        
    except Exception as e:
        print(f"Gemini API Error (Skin Image): {e}")
        return None
