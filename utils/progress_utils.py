import json
import os
import streamlit as st

def get_stats_file():
    username = st.session_state.get("username", "default")
    user_dir = f"data/users/{username}"
    os.makedirs(user_dir, exist_ok=True)
    return f"{user_dir}/stats.json"

def load_stats():
    stats_file = get_stats_file()
    if os.path.exists(stats_file):
        try:
            with open(stats_file, "r") as f:
                return json.load(f)
        except:
            pass
    return {"streak": 0, "total_workouts": 0}

def update_stats():
    stats_file = get_stats_file()
    stats = load_stats()
    stats["streak"] += 1
    stats["total_workouts"] += 1
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=4)