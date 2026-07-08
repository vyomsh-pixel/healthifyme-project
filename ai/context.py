import json
import os

# -------------------------
# GET USER DATA PATHS
# -------------------------
def get_profile_file(username):
    """
    Returns path to profile.json for a specific user.
    Example: data/users/vyom/profile.json
    """
    user_dir = f"data/users/{username}"
    os.makedirs(user_dir, exist_ok=True)
    return f"{user_dir}/profile.json"

def get_history_file(username):
    """
    Returns path to history.json for a specific user.
    Example: data/users/vyom/history.json
    """
    user_dir = f"data/users/{username}"
    os.makedirs(user_dir, exist_ok=True)
    return f"{user_dir}/history.json"

# -------------------------
# PROFILE
# -------------------------
def load_profile(username):
    """
    Loads profile data for the given user.
    Returns dict, or empty dict if no profile yet.
    """
    profile_file = get_profile_file(username)

    if os.path.exists(profile_file):
        with open(profile_file, "r") as file:
            return json.load(file)

    return {}

def save_profile(username, profile_data):
    """
    Saves profile data for the given user.
    """
    profile_file = get_profile_file(username)

    with open(profile_file, "w") as file:
        json.dump(profile_data, file, indent=4)

# -------------------------
# HISTORY
# -------------------------
def load_history(username):
    """
    Loads health history for the given user.
    Returns list, or empty list if no history yet.
    """
    history_file = get_history_file(username)

    if os.path.exists(history_file):
        with open(history_file, "r") as file:
            return json.load(file)

    return []

def save_history(username, history_data):
    """
    Saves health history for the given user.
    """
    history_file = get_history_file(username)

    with open(history_file, "w") as file:
        json.dump(history_data, file, indent=4)