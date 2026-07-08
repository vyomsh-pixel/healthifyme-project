import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_meal_plan(goal, diet_type, budget, meals, profile, extra_instructions=""):

    prompt = f"""
    Create a personalized Indian meal plan.

    User Information:
    Goal: {goal}
    Diet Type: {diet_type}
    Budget per day: {budget}
    Meals Per Day: {meals}

    User Profile:
    Age: {profile.get('age')}
    Gender: {profile.get('gender')}
    Weight: {profile.get('weight')}
    Height: {profile.get('height')}
    Activity Level: {profile.get('activity_level')}

    Requirements:
    - Make the meal plan practical
    = table with columns: Meal, Dish, Calories, Protein Sources,time of day
    - Use Indian foods
    - Mention calories roughly
    - Mention protein sources
    - Include breakfast, lunch, dinner, snacks
    - Keep formatting clean and simple
    - Avoid long paragraphs, use bullet 
    - dont give any fitness advice or health advice only meal plan
    - dont give user profile summary or meal plan summary, only meal plan
    - dont give any tips or suggestions, only meal plan
    {f"Special instructions from the user (must follow these): {extra_instructions}" if extra_instructions.strip() else ""}
    """

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        return f"Error: {e}"