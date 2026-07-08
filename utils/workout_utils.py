import json
import os

from datetime import datetime

# ---------------- FILE PATHS ----------------

FILE = "data/workout_history.json"
COMPLETED_FILE = "data/completed_workouts.json"


# ---------------- SAVE GENERATED WORKOUT ----------------

def save_workout(workout, calories):

    os.makedirs("data", exist_ok=True)

    data = {
        "time": str(datetime.now()),
        "calories": calories,
        "workout": workout
    }

    try:
        with open(FILE, "r") as f:
            history = json.load(f)
    except:
        history = []

    history.append(data)

    with open(FILE, "w") as f:
        json.dump(history, f, indent=4)


# ---------------- SAVE COMPLETED WORKOUT ----------------

def save_completed_workout(workout, calories, duration=0, goal="Workout"):

    # Always ensure data/ folder exists before writing
    os.makedirs("data", exist_ok=True)

    data = {
        "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "goal": goal,
        "duration": duration,
        "total_calories": calories,
        "exercise_count": len(workout),
        "workout": workout
    }

    try:
        with open(COMPLETED_FILE, "r") as f:
            history = json.load(f)
    except:
        history = []

    history.append(data)

    with open(COMPLETED_FILE, "w") as f:
        json.dump(history, f, indent=4)


# ---------------- LOAD COMPLETED WORKOUTS ----------------

def load_completed_workouts():

    if not os.path.exists(COMPLETED_FILE):
        return []

    try:
        with open(COMPLETED_FILE, "r") as f:
            return json.load(f)
    except:
        return []


# ---------------- DELETE SINGLE WORKOUT ----------------

def delete_completed_workout(index):
    """index = global position in the flat completed_workouts list"""

    workouts = load_completed_workouts()

    if 0 <= index < len(workouts):
        workouts.pop(index)

    os.makedirs("data", exist_ok=True)

    with open(COMPLETED_FILE, "w") as f:
        json.dump(workouts, f, indent=4)


# ---------------- DELETE ALL WORKOUTS ----------------

def delete_all_completed_workouts():

    os.makedirs("data", exist_ok=True)

    with open(COMPLETED_FILE, "w") as f:
        json.dump([], f, indent=4)