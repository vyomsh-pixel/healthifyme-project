import streamlit as st
import streamlit_authenticator as stauth
import yaml
import os
from yaml.loader import SafeLoader

# -------------------------
# USERS CONFIG FILE
# -------------------------
USERS_FILE = "data/users.yaml"

# -------------------------
# ENSURE FILE EXISTS
# -------------------------
def init_users_file():
    """Create users.yaml if it doesn't exist yet."""
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(USERS_FILE):
        default_config = {
            "credentials": {
                "usernames": {}
            },
            "cookie": {
                "name": "healthio_auth",
                "key": "healthio_secret_key_change_this",
                "expiry_days": 7
            }
        }
        with open(USERS_FILE, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False)

# -------------------------
# LOAD CONFIG
# -------------------------
def load_config():
    init_users_file()
    with open(USERS_FILE, "r") as f:
        return yaml.load(f, Loader=SafeLoader)

# -------------------------
# SAVE CONFIG
# -------------------------
def save_config(config):
    with open(USERS_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

# -------------------------
# REGISTER NEW USER
# -------------------------
def register_user(username, name, password):
    """
    Add a new user to users.yaml with a hashed password.
    Returns (True, "message") on success, (False, "error") on failure.
    """
    config = load_config()

    # Check if username already exists
    if username in config["credentials"]["usernames"]:
        return False, "Username already exists."

    # Modern, safe way to hash a single password string
    try:
        hashed_password = stauth.Hasher.hash(password)
    except AttributeError:
        # Fallback for slightly older versions
        hashed_password = stauth.Hasher([password]).generate()[0]

    # Add to config
    config["credentials"]["usernames"][username] = {
        "name": name,
        "password": hashed_password
    }
    
    save_config(config)

    # Create user data folder
    os.makedirs(f"data/users/{username}", exist_ok=True)

    return True, "Account created successfully!"

# -------------------------
# SETUP AUTHENTICATOR
# -------------------------
def get_authenticator():
    config = load_config()
    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"]
    )
    return authenticator, config

# -------------------------
# LOGIN / SIGNUP PAGE
# -------------------------
def show_auth_page():
    """
    Renders login + signup UI.
    Returns username if logged in, None otherwise.
    """
    st.title("💪 Health.io")
    st.markdown("Your personal AI health assistant.")
    st.divider()

    # Using a selectbox or radio button prevents Streamlit tabs from collapsing into a blank screen
    mode = st.radio("Choose an option:", ["Login", "Sign Up"], horizontal=True)

    # -------------------------
    # LOGIN MODE
    # -------------------------
    if mode == "Login":
        authenticator, config = get_authenticator()

        try:
            authenticator.login(location="main")
        except TypeError:
            authenticator.login()

        auth_status = st.session_state.get("authentication_status")
        username = st.session_state.get("username")

        if auth_status is False:
            st.error("Incorrect username or password.")
            return None

        if auth_status is None:
            st.info("Enter your credentials to continue.")
            return None

        if auth_status:
            st.session_state["authenticator"] = authenticator
            return username

    # -------------------------
    # SIGNUP MODE
    # -------------------------
    elif mode == "Sign Up":
        st.subheader("Create a New Account")

        new_name = st.text_input("Full Name", key="signup_name")
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Create Account", key="signup_btn"):
            if not new_name or not new_username or not new_password:
                st.error("All fields are required.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                success, message = register_user(new_username, new_name, new_password)
                if success:
                    st.success(message + " Toggle the option above to 'Login' to get started!")
                else:
                    st.error(message)

    return None
# -------------------------
# LOGOUT
# -------------------------
def logout():
    """Call this from sidebar to log out."""
    # Check if the authenticator exists in session state before calling logout
    if "authenticator" in st.session_state and st.session_state["authenticator"]:
        try:
            # Modern versions of streamlit-authenticator handle logout via the object
            st.session_state["authenticator"].logout(location="unrendered")
        except:
            pass
    
    # Clear out the session state completely to reset the app
    st.session_state.clear()
    st.rerun()
    # -------------------------
# GET CURRENT USER
# -------------------------
def get_current_user():
    """Returns username from session, or None if not logged in."""
    return st.session_state.get("username", None)