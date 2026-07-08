import json
import os

MEAL_HISTORY_PATH = "data/meal_history.json"


def load_meal_history():
    if not os.path.exists(MEAL_HISTORY_PATH):
        return []
    try:
        with open(MEAL_HISTORY_PATH, "r") as file:
            return json.load(file)
    except Exception:
        return []