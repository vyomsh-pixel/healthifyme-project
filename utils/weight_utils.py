import json
import os

FILE = "data/weight_history.json"


def load_weight_history():
    if not os.path.exists(FILE):
        return []

    with open(FILE, "r") as f:
        return json.load(f)


def save_weight_entry(entry):
    history = load_weight_history()
    history.append(entry)

    with open(FILE, "w") as f:
        json.dump(history, f, indent=4)