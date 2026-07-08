import streamlit as st
import json
import os

# ---------------------------------
# GET USER DATA PATHS
# ---------------------------------
def get_history_file(username):
    """
    Returns path to scan_history.json for a specific user.
    Example: data/users/vyom/scan_history.json
    """
    user_dir = f"data/users/{username}"
    os.makedirs(user_dir, exist_ok=True)
    return f"{user_dir}/scan_history.json"

# ---------------------------------
# LOAD HISTORY
# ---------------------------------
def load_history(username):
    """Loads scan history entries safely from the individual user's data folder."""
    history_file = get_history_file(username)
    if not os.path.exists(history_file):
        return []
    try:
        with open(history_file, "r") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except:
        return []

# ---------------------------------
# SAVE HISTORY
# ---------------------------------
def save_history_item(username, item_data):
    """Appends a new scan or BMI event safely to the specific user's log."""
    history_file = get_history_file(username)
    history = load_history(username)
    history.append(item_data)
    with open(history_file, "w") as file:
        json.dump(history, file, indent=4)
def save_history(item_data):
    """
    A fallback function for pages still calling save_history(data) 
    without passing a username explicitly.
    """
    username = st.session_state.get("username", "default")
    save_history_item(username, item_data)