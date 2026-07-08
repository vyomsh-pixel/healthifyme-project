import streamlit as st

# Auth Gate for sub-pages
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please log in on the main page first!")
    st.stop()

import json
import os
from datetime import datetime

# CRITICAL FIX: Explicitly pull load_history from utils.history_utils
from utils.history_utils import load_history
from utils.nutrition_utils import (
    get_today_nutrition,
    add_nutrition
)

import plotly.graph_objects as go

username = st.session_state["username"]
today_calories, today_protein = get_today_nutrition(username)
st.write(f"Welcome back, **{username}**! Here's your personalized health overview.")
# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

# Grab the active user session context
username = st.session_state["username"]

# ---------------------------------
# USER-SCOPED DATA PATHS
# ---------------------------------
user_dir = f"data/users/{username}"
os.makedirs(user_dir, exist_ok=True)
MEAL_HISTORY_PATH = f"{user_dir}/meal_history.json"

# ---------------------------------
# LOAD SCOPED MEAL HISTORY
# ---------------------------------
def load_user_meal_history():
    if not os.path.exists(MEAL_HISTORY_PATH):
        return []
    try:
        with open(MEAL_HISTORY_PATH, "r") as file:
            return json.load(file)
    except:
        return []

# Load only this specific user's metrics
history = load_history(username)
meal_history = load_user_meal_history()

# ---------------------------------
# CUSTOM CSS
# ---------------------------------
st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

.dashboard-card {
    padding: 20px;
    border-radius: 15px;
    background-color: #1E1E1E;
    border: 1px solid #2E2E2E;
    margin-bottom: 15px;
}

.big-font {
    font-size: 22px;
    font-weight: bold;
}

.small-font {
    font-size: 14px;
    color: #B0B0B0;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------
# TITLE
# ---------------------------------
st.title("📊 AI Health Dashboard")
st.write(f"Welcome back, **{username}**! Here's your personalized health overview.")

# ---------------------------------
# DAILY NUTRITION TRACKER
# ---------------------------------

st.subheader("🎯 Daily Nutrition")

daily_calorie_goal = 2200
daily_protein_goal = 140

col1, col2 = st.columns(2)

with col1:

    calorie_remaining = max(
        daily_calorie_goal - today_calories,
        0
    )

    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Consumed", "Remaining"],
                values=[
                    today_calories,
                    calorie_remaining
                ],
                hole=0.7
            )
        ]
    )

    fig.update_layout(
        title=f"🔥 Calories ({today_calories}/{daily_calorie_goal})",
        height=300
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    protein_remaining = max(
        daily_protein_goal - today_protein,
        0
    )

    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Consumed", "Remaining"],
                values=[
                    today_protein,
                    protein_remaining
                ],
                hole=0.7
            )
        ]
    )

    fig.update_layout(
        title=f"💪 Protein ({today_protein}/{daily_protein_goal}g)",
        height=300
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------------------------
# FILTER DATA
# ---------------------------------
bmi_records = [item for item in history if item.get("type") == "BMI"]
food_records = [item for item in history if item.get("type") == "Food Scan"]
skin_records = [item for item in history if item.get("type") == "Skin Scan"]

# ---------------------------------
# LATEST RECORDS
# ---------------------------------
latest_bmi = bmi_records[-1] if bmi_records else None
latest_food = food_records[-1] if food_records else None
latest_skin = skin_records[-1] if skin_records else None

# ---------------------------------
# HEALTH SCORE CALCULATION
# ---------------------------------
health_score = 0
score_breakdown = {}

# --- BMI: Gradient scoring (max 30 pts) ---
if latest_bmi:
    try:
        bmi_value = float(latest_bmi.get("bmi", 0))
        if 18.5 <= bmi_value <= 24.9:
            bmi_score = 30
        elif 17.0 <= bmi_value < 18.5 or 25.0 < bmi_value <= 27.5:
            bmi_score = 20
        elif 15.0 <= bmi_value < 17.0 or 27.5 < bmi_value <= 30.0:
            bmi_score = 10
        else:
            bmi_score = 5
    except (ValueError, TypeError):
        bmi_score = 0
    health_score += bmi_score
    score_breakdown["BMI"] = bmi_score

# --- Calorie Goal Adherence (max 25 pts) ---
calorie_score = 0
if today_calories > 0:
    calorie_ratio = today_calories / daily_calorie_goal
    if 0.85 <= calorie_ratio <= 1.10:
        calorie_score = 25      # Hit the goal
    elif 0.70 <= calorie_ratio < 0.85:
        calorie_score = 16      # Slightly under
    elif 1.10 < calorie_ratio <= 1.25:
        calorie_score = 12      # Slightly over
    elif calorie_ratio > 1.25:
        calorie_score = 5       # Significantly over
    else:
        calorie_score = 3       # Very low intake
health_score += calorie_score
score_breakdown["Calorie Goal"] = calorie_score

# --- Protein Goal Adherence (max 20 pts) ---
protein_score = 0
if today_protein > 0:
    protein_ratio = today_protein / daily_protein_goal
    if protein_ratio >= 0.90:
        protein_score = 20      # Hit protein goal
    elif protein_ratio >= 0.70:
        protein_score = 13
    elif protein_ratio >= 0.50:
        protein_score = 7
    else:
        protein_score = 3
health_score += protein_score
score_breakdown["Protein Goal"] = protein_score

# --- Skin Scan Engagement (max 10 pts) ---
skin_score = min(len(skin_records) * 2, 10)
health_score += skin_score
score_breakdown["Skin Scans"] = skin_score

# --- Meal Planning Engagement (max 15 pts) ---
meal_score = min(len(meal_history) * 5, 15)
health_score += meal_score
score_breakdown["Meal Plans"] = meal_score

health_score = min(health_score, 100)
# ---------------------------------
# LATEST MEAL PLAN DISPLAY
# ---------------------------------
st.subheader("🍽️ Latest Meal Plan")

if meal_history:
    latest_meal = meal_history[-1]
    st.info(
        f"""
        Goal: {latest_meal.get('goal', 'N/A')}
        
        Diet Type: {latest_meal.get('diet_type', 'N/A')}
        
        Budget: ₹{latest_meal.get('budget', 'N/A')}
        """
    )

    with st.expander("View Meal Plan"):
        st.markdown(latest_meal.get("meal_plan", "No plan content available."))
else:
    st.warning("No meal plans generated yet.")

# ---------------------------------
# TOP METRICS
# ---------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="BMI Records",
        value=len(bmi_records)
    )

with col2:
    st.metric(
        label="Food Scans",
        value=len(food_records)
    )

with col3:
    st.metric(
        label="Skin Scans",
        value=len(skin_records)
    )

with col4:
    st.metric(
        label="Health Score",
        value=f"{health_score}/100"
    )

with col5:
    st.metric(
        label="Meal Plans",
        value=len(meal_history)
    )

# ---------------------------------
# HEALTH SCORE SECTION
# ---------------------------------
st.subheader("🏆 Health Score")

st.progress(health_score / 100)
st.metric("Overall Score", f"{health_score}/100")

with st.expander("📊 Score Breakdown"):
    for category, pts in score_breakdown.items():
        st.write(f"**{category}**: {pts} pts")

if health_score >= 80:
    st.success("Excellent health activity! You're on track.")
elif health_score >= 50:
    st.warning("Good progress. Keep going!")
else:
    st.error("Log your meals and track nutrition consistently for a better score.")
# ---------------------------------
# LATEST BMI
# ---------------------------------
st.subheader("📏 Latest BMI")

if latest_bmi:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="big-font">
                BMI: {latest_bmi.get("bmi")}
            </div>
            <div class="small-font">
                Category: {latest_bmi.get("category")}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="big-font">
                Recorded On
            </div>
            <div class="small-font">
                {latest_bmi.get("timestamp")}
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No BMI records found.")

# ---------------------------------
# LATEST FOOD SCAN
# ---------------------------------
st.subheader("🍔 Latest Food Scan")

if latest_food:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="small-font">
            {latest_food.get("result")}
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No food scans found.")

# ---------------------------------
# LATEST SKIN SCAN
# ---------------------------------
st.subheader("🧴 Latest Skin Scan")

if latest_skin:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="small-font">
            {latest_skin.get("result")}
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No skin scans found.")

# ---------------------------------
# RECENT ACTIVITY
# ---------------------------------
st.subheader("🕒 Recent Activity")

if history:
    recent_history = history[-5:]
    recent_history.reverse()

    for item in recent_history:
        record_type = item.get("type", "Unknown")
        timestamp = item.get("timestamp", "Unknown Time")

        with st.expander(f"{record_type} • {timestamp}"):
            for key, value in item.items():
                if key != "type":
                    st.write(f"**{key.capitalize()}**: {value}")
else:
    st.info("No recent application activity logged yet.")

# ---------------------------------
# FOOTER
# ---------------------------------
st.divider()
st.caption("AI Health App • Dashboard")