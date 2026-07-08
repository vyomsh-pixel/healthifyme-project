import json
import os
from datetime import datetime

FILE_PATH = "data/history.json"


def load_history():
    if not os.path.exists(FILE_PATH):
        return []
    try:
        with open(FILE_PATH, "r") as file:
            return json.load(file)
    except Exception:
        return []


def save_history(new_data):
    os.makedirs("data", exist_ok=True)
    history = load_history()
    new_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append(new_data)
    with open(FILE_PATH, "w") as file:
        json.dump(history, file, indent=4)