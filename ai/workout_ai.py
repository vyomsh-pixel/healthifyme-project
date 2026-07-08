import os
import ast
import random

from google import genai
from dotenv import load_dotenv

from utils.progress_utils import load_stats

# ---------------- LOAD ENV ----------------

load_dotenv()

# ---------------- GEMINI CLIENT ----------------

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# ---------------- WORKOUT GENERATOR ----------------

def generate_workout(
    goal,
    level,
    location,
    duration,
    rest,
    username=None
):

    # Load stats inside function with username scope
    # Falls back to empty dict if no username provided
    stats = load_stats()

    prompt = f"""
    Generate a workout plan.

    Goal: {goal}
    Experience Level: {level}
    Workout Location: {location}
    Workout Duration: {duration} minutes

    User Stats:
    - Streak: {stats.get("streak", 0)}
    - Total Workouts: {stats.get("total_workouts", 0)}
    - Fitness Level: {stats.get("level", "Beginner")}

    IMPORTANT:
    - Return ONLY a valid Python list
    - Do NOT add markdown
    - Do NOT add explanations
    - Give ONLY exercise names

    Example:

    [
      {{
        "name": "Push Ups"
      }},
      {{
        "name": "Squats"
      }}
    ]

    Generate 7-8 exercises.
    """

    try:

        # ---------------- AI RESPONSE ----------------

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        # ---------------- CLEAN RESPONSE ----------------

        text = text.replace("```python", "")
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        # ---------------- SAFE PARSING ----------------

        workout = ast.literal_eval(text)

        # ---------------- DYNAMIC DURATION SYSTEM ----------------

        total_seconds = duration * 60

        used_time = 0

        final_workout = []

        for exercise in workout:

            # Random exercise duration between 60-90 sec
            exercise_time = random.randint(60, 90)

            # Use user-selected rest
            rest_time = rest

            # Stop if duration exceeded
            if used_time + exercise_time + rest_time > total_seconds:
                break

            # Random calories
            calories = round(random.uniform(8, 20), 1)

            # Exercise name
            name = exercise.get("name", "Exercise")

            # Final formatted workout
            final_workout.append({
                "name": name,
                "time": exercise_time,
                "cal": calories,
                "rest": rest_time,
                "youtube": f"https://www.youtube.com/results?search_query={name.replace(' ', '+')}+exercise"
            })

            used_time += exercise_time + rest_time

        # ---------------- FALLBACK IF EMPTY ----------------

        if len(final_workout) == 0:
            final_workout.append({
                "name": "Jumping Jacks",
                "time": 60,
                "cal": 15,
                "rest": rest,
                "youtube": "https://www.youtube.com/results?search_query=Jumping+Jacks+exercise"
            })

        return final_workout

    except Exception as e:

        print("Workout Generation Error:", e)

        return [
            {
                "name": "Jumping Jacks",
                "time": 60,
                "cal": 15,
                "rest": rest,
                "youtube": "https://www.youtube.com/results?search_query=Jumping+Jacks+exercise"
            }
        ]