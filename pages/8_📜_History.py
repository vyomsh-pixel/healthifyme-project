import streamlit as st

# Auth Gate for sub-pages
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please log in on the main page first!")
    st.stop()

from utils.history_utils import load_history

# Grab the active user session context
username = st.session_state["username"]

# Load only this specific user's scan history logs
history = load_history(username)

bmi_history = [
    item for item in history
    if item.get("type") == "BMI"
] if history else []

skin_history = [
    item for item in history
    if item.get("type") == "Skin Scan"
] if history else []

food_history = [
    item for item in history
    if item.get("type") == "Food Scan"
] if history else []

st.title("📜 Your Scan History")
st.write("Review your recorded measurements, food logs, and dermatological evaluations.")

tab1, tab2, tab3 = st.tabs([
    "📏 BMI History",
    "🧴 Skin Scans",
    "🍎 Food Scans"
])

with tab1:
    if not bmi_history:
        st.info("No BMI history recorded yet for this account.")
    else:
        for item in reversed(bmi_history):
            with st.container(border=True):
                st.write(f"### ⚖️ BMI: {item.get('bmi', 'N/A')} ({item.get('category', 'Unknown')})")
                st.write(f"Weight: {item.get('weight')} kg | Height: {item.get('height')} cm")
                st.caption(f"Recorded on: {item.get('timestamp', 'N/A')}")

with tab2:
    if not skin_history:
        st.info("No skin scans found yet for this account.")
    else:
        for item in reversed(skin_history):
            with st.container(border=True):
                st.markdown(item.get("result", "No details available."))
                st.caption(f"Scanned on: {item.get('timestamp', 'N/A')}")

with tab3:
    if not food_history:
        st.info("No food scans found yet for this account.")
    else:
        for item in reversed(food_history):
            with st.container(border=True):
                st.markdown(item.get("result", "No details available."))
                st.caption(f"Scanned on: {item.get('timestamp', 'N/A')}")