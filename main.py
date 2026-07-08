import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="AI Health Assistant",
    page_icon="💪",
    layout="wide"
)

# -------------------------
# AUTH GATE
# -------------------------
if "username" not in st.session_state or not st.session_state["username"]:
    from auth import show_auth_page
    username = show_auth_page()
    if username:
        st.session_state["username"] = username
        st.rerun()
    st.stop()
# -------------------------
# USER IS LOGGED IN FROM HERE
# -------------------------
from auth import logout, get_current_user
from utils.chat_memory import load_chat, save_chat
from ai.chatbot import get_ai_response
from ai.context import load_profile, load_history
from ai.prompts import build_health_prompt

username = get_current_user()

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:

    st.title("💪 Health.io")
    st.write("Your personal AI health assistant for fitness, nutrition, skincare & more.")
    st.divider()
    st.caption(f"Logged in as: **{username}**")
    st.divider()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        save_chat(username, [])
        st.rerun()

    if st.button("🚪 Logout"):
        logout()

# -------------------------
# LOAD DATA (user-scoped)
# -------------------------
profile = load_profile(username)
history = load_history(username)

# -------------------------
# TITLE
# -------------------------
st.title("💪 AI Health Assistant")

# -------------------------
# WELCOME
# -------------------------
if profile and profile.get("name"):
    st.success(f"""
        Welcome back, {profile.get('name')} 👋
        Goal: {profile.get('goal', 'Not set yet')}
    """)
else:
    st.warning("👋 Welcome! Please complete your profile to get personalized health advice.")

# -------------------------
# LOAD CHAT MEMORY (user-scoped)
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = load_chat(username)

# -------------------------
# DISPLAY CHAT
# -------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------------
# CHAT INPUT
# -------------------------
user_input = st.chat_input("Ask anything about fitness, nutrition, skincare...")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})
    save_chat(username, st.session_state.messages)

    with st.chat_message("user"):
        st.markdown(user_input)

    final_prompt = build_health_prompt(user_input, profile, history)

    with st.spinner("Thinking..."):
        ai_response = get_ai_response(final_prompt)

    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    save_chat(username, st.session_state.messages)

    with st.chat_message("assistant"):
        st.markdown(ai_response)

# -------------------------
# CHAT EXPORT
# -------------------------
st.divider()

chat_text = ""
for message in st.session_state.messages:
    role = message["role"].upper()
    content = message["content"]
    chat_text += f"{role}:\n{content}\n\n"

st.download_button(
    label="📥 Download Chat",
    data=chat_text,
    file_name="health_chat.txt",
    mime="text/plain"
)