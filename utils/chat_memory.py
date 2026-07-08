import json
import os

# -------------------------
# GET USER CHAT FILE PATH
# -------------------------
def get_chat_file(username):
    """
    Returns the path to chat history JSON for a specific user.
    Example: data/users/vyom/chat_history.json
    """
    user_dir = f"data/users/{username}"
    os.makedirs(user_dir, exist_ok=True)
    return f"{user_dir}/chat_history.json"

# -------------------------
# LOAD CHAT
# -------------------------
def load_chat(username):
    """
    Loads chat history for the given user.
    Returns a list of messages, or empty list if none found.
    """
    chat_file = get_chat_file(username)

    if os.path.exists(chat_file):
        try:
            with open(chat_file, "r") as file:
                return json.load(file)
        except:
            return []
    return []

# -------------------------
# SAVE CHAT
# -------------------------
def save_chat(username, messages):
    """
    Saves chat history for the given user.
    """
    chat_file = get_chat_file(username)

    with open(chat_file, "w") as file:
        json.dump(messages, file, indent=4)