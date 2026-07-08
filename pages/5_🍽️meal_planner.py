import streamlit as st
# Auth Gate for sub-pages
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please log in on the main page first!")
    st.stop()

import json
import os
from datetime import datetime

from ai.meal_ai import generate_meal_plan
from ai.chatbot import get_ai_response
from ai.prompts import build_health_prompt
from ai.context import load_profile

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="AI Meal Planner",
    page_icon="🍽️",
    layout="wide"
)

username = st.session_state["username"]

# -----------------------------------
# CUSTOM UI
# -----------------------------------

st.markdown("""
<style>

.main {
    background: linear-gradient(to bottom right, #0f172a, #111827);
    color: white;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1300px;
}

.hero-box {
    background: linear-gradient(135deg, #1e293b, #111827);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 35px;
    border-radius: 24px;
    margin-bottom: 30px;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    color: white;
    margin-bottom: 10px;
}

.hero-subtitle {
    font-size: 17px;
    color: #cbd5e1;
    line-height: 1.7;
}

.glass-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 24px;
    border-radius: 22px;
    margin-bottom: 20px;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #22c55e, #16a34a);
    color: white;
    border: none;
    padding: 14px;
    border-radius: 14px;
    font-weight: 700;
    font-size: 16px;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.02);
    background: linear-gradient(90deg, #16a34a, #15803d);
}

.stDownloadButton > button {
    width: 100%;
    background: linear-gradient(90deg, #3b82f6, #2563eb);
    color: white;
    border: none;
    padding: 12px;
    border-radius: 14px;
    font-weight: 700;
}

.stSelectbox label,
.stSlider label,
.stNumberInput label {
    font-weight: 600 !important;
    color: white !important;
}

.chat-header {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 10px;
    color: white;
}

.streamlit-expanderHeader {
    font-size: 16px;
    font-weight: 700;
}

.section-title {
    font-size: 30px;
    font-weight: 800;
    margin-bottom: 20px;
    color: white;
}

.stSuccess {
    border-radius: 12px;
}

/* Extra instructions textarea */
.stTextArea label {
    color: white !important;
    font-weight: 600 !important;
}

.stTextArea textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 14px !important;
    color: #e2e8f0 !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
}

.stTextArea textarea::placeholder {
    color: #475569 !important;
}

.stTextArea textarea:focus {
    border-color: #22c55e !important;
    box-shadow: 0 0 0 2px rgba(34,197,94,0.15) !important;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# HERO SECTION
# -----------------------------------

st.markdown("""
<div class="hero-box">
<div class="hero-title">🍽️ AI Meal Planner</div>
<div class="hero-subtitle">
Create personalized AI-powered meal plans based on your goals,
budget, diet preferences, and lifestyle. Track meals, save plans,
and chat with your intelligent nutrition assistant.
</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------
# LOAD PROFILE + PATHS
# -----------------------------------
profile = load_profile(username)

user_dir = f"data/users/{username}"
os.makedirs(user_dir, exist_ok=True)
MEAL_HISTORY_PATH = f"{user_dir}/meal_history.json"

# -----------------------------------
# HELPERS
# -----------------------------------

def load_meal_history():
    if not os.path.exists(MEAL_HISTORY_PATH):
        return []
    try:
        with open(MEAL_HISTORY_PATH, "r") as file:
            return json.load(file)
    except:
        return []

def save_meal_plan(data):
    history = load_meal_history()
    history.append(data)
    with open(MEAL_HISTORY_PATH, "w") as file:
        json.dump(history, file, indent=4)

# -----------------------------------
# SESSION STATE
# -----------------------------------

if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = ""

if "meal_chat" not in st.session_state:
    st.session_state.meal_chat = []

# -----------------------------------
# INPUT SECTION
# -----------------------------------

st.markdown('<div class="section-title">⚙️ Meal Preferences</div>', unsafe_allow_html=True)

with st.container():

    col1, col2 = st.columns(2)

    with col1:

        

        goal = st.selectbox(
            "🎯 Goal",
            ["Fat Loss", "Muscle Gain", "Maintenance"]
        )

        diet_type = st.selectbox(
            "🥗 Diet Type",
            ["Vegetarian", "Non-Vegetarian", "Eggetarian"]
        )

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:

        

        budget = st.number_input(
            "💰 Budget Per Day (₹)",
            min_value=30,
            value=50
        )

        meals = st.slider(
            "🍱 Meals Per Day",
            3,
            6,
            4
        )

        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# EXTRA INSTRUCTIONS PANEL
# -----------------------------------

st.markdown('<div class="section-title">💬 Anything else to tell the AI?</div>', unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

extra_instructions = st.text_area(
    "Extra Instructions",
    placeholder="e.g. I hate mushrooms · I work night shifts so I eat late · I want a high-protein breakfast · avoid spicy food · I only have 10 minutes to cook · I'm lactose intolerant...",
    height=130,
    label_visibility="collapsed"
)

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# GENERATE BUTTON
# -----------------------------------

if st.button("✨ Generate AI Meal Plan"):

    with st.spinner("Generating your personalized meal plan..."):

        meal_plan = generate_meal_plan(
            goal=goal,
            diet_type=diet_type,
            budget=budget,
            meals=meals,
            profile=profile,
            extra_instructions=extra_instructions
        )

        st.session_state.meal_plan = meal_plan

    st.success("Meal Plan Generated Successfully!")

# -----------------------------------
# DISPLAY MEAL PLAN
# -----------------------------------

if st.session_state.meal_plan:

    st.markdown('<div class="section-title">📋 Your AI Meal Plan</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(st.session_state.meal_plan)
    st.markdown('</div>', unsafe_allow_html=True)

    btn1, btn2 = st.columns(2)

    with btn1:

        if st.button("💾 Save Meal Plan"):

            save_data = {
                "timestamp": str(datetime.now()),
                "goal": goal,
                "diet_type": diet_type,
                "budget": budget,
                "extra_instructions": extra_instructions,
                "meal_plan": st.session_state.meal_plan
            }

            save_meal_plan(save_data)
            st.success("Meal Plan Saved!")

    with btn2:

        st.download_button(
            label="⬇️ Download Meal Plan",
            data=st.session_state.meal_plan,
            file_name="meal_plan.txt",
            mime="text/plain"
        )

# -----------------------------------
# CHATBOT SECTION
# -----------------------------------

st.divider()

st.markdown('<div class="chat-header">🤖 AI Nutrition Assistant</div>', unsafe_allow_html=True)
st.caption("Ask anything about diet, calories, protein, nutrition, or your meal plan.")

for msg in st.session_state.meal_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about diet, calories, protein, meals...")

if user_input:

    st.session_state.meal_chat.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    combined_context = f"""
    Current Meal Plan:
    {st.session_state.meal_plan}

    User Question:
    {user_input}
    """

    prompt = build_health_prompt(combined_context, profile=profile)

    with st.chat_message("assistant"):
        with st.spinner("AI Nutrition Assistant is thinking..."):
            response = get_ai_response(prompt)
            st.markdown(response)

    st.session_state.meal_chat.append({"role": "assistant", "content": response})

# -----------------------------------
# SAVED MEAL PLANS
# -----------------------------------

st.divider()

st.markdown('<div class="section-title">📚 Saved Meal Plans</div>', unsafe_allow_html=True)

history = load_meal_history()

if history:

    for item in reversed(history):

        label = f"{item.get('goal','?')} · {item.get('diet_type','?')} · {item.get('timestamp','?')}"

        with st.expander(label):

            if item.get("extra_instructions"):
                st.caption(f"📝 User note: {item['extra_instructions']}")

            st.markdown(item["meal_plan"])

else:
    st.info("No saved meal plans yet.")