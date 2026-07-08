import json
import os
from datetime import datetime


def nutrition_path(username):
    return f"data/users/{username}/nutrition.json"


def load_nutrition(username):

    path = nutrition_path(username)

    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return json.load(f)


def save_nutrition(username, data):

    path = nutrition_path(username)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def add_nutrition(username, calories, protein):

    today = datetime.now().strftime("%Y-%m-%d")

    data = load_nutrition(username)

    if today not in data:
        data[today] = {
            "calories": 0,
            "protein": 0
        }

    data[today]["calories"] += calories
    data[today]["protein"] += protein

    save_nutrition(username, data)


def get_today_nutrition(username):

    today = datetime.now().strftime("%Y-%m-%d")

    data = load_nutrition(username)

    if today not in data:
        return 0, 0

    return (
        data[today]["calories"],
        data[today]["protein"]
    )