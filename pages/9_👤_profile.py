import streamlit as st

# Auth Gate for sub-pages
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please log in on the main page first!")
    st.stop()

import json
import os
# Import your clean user-scoped context handlers
from ai.context import load_profile, save_profile

# ---------------------------------
# PAGE CONFIG
# ---------------------------------

st.set_page_config(
    page_title="Profile",
    page_icon="👤",
    layout="centered"
)

# ---------------------------------
# CUSTOM UI
# ---------------------------------

st.markdown("""
<style>

/* MAIN */

.main {
    background: linear-gradient(to bottom right, #0f172a, #111827);
    color: white;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 850px;
}

/* HERO */

.hero-box {
    background: linear-gradient(135deg, #1e293b, #111827);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 35px;
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

/* GLASS CARD */

.glass-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 28px;
    margin-bottom: 20px;
}

/* SECTION TITLE */

.section-title {
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 20px;
    color: white;
}

/* INPUT LABELS */

.stTextInput label,
.stNumberInput label,
.stSelectbox label {
    color: white !important;
    font-weight: 600 !important;
}

/* BUTTON */

.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #22c55e, #16a34a);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 14px;
    font-size: 16px;
    font-weight: 700;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.02);
    background: linear-gradient(90deg, #16a34a, #15803d);
}

/* SUCCESS */

.stSuccess {
    border-radius: 14px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------
# LOAD EXISTING DATA (User-Scoped)
# ---------------------------------
username = st.session_state["username"]
profile = load_profile(username)

# Helper lists for handling selectbox indexes correctly on refresh
gender_options = ["Male", "Female", "Other"]
activity_options = ["Low", "Moderate", "High"]
goal_options = ["Weight Loss", "Muscle Gain", "Maintenance", "General Fitness"]
diet_options = ["None", "Vegetarian", "Vegan", "Non-Vegetarian", "Eggitarian"]

# Safely find the previously saved selection, defaulting to index 0 if not found
gender_idx = gender_options.index(profile.get("gender")) if profile.get("gender") in gender_options else 0
activity_idx = activity_options.index(profile.get("activity_level")) if profile.get("activity_level") in activity_options else 0
goal_idx = goal_options.index(profile.get("goal")) if profile.get("goal") in goal_options else 0
diet_idx = diet_options.index(profile.get("diet_preference")) if profile.get("diet_preference") in diet_options else 0

# ---------------------------------
# HERO SECTION
# ---------------------------------

st.markdown("""
<div class="hero-box">

<div class="hero-title">
👤 User Profile
</div>

<div class="hero-subtitle">
Personalize your AI health and wellness experience.
Your profile helps the AI generate smarter workouts,
meal plans, recovery suggestions, and recommendations.
</div>

</div>
""", unsafe_allow_html=True)

# ---------------------------------
# PROFILE SECTION
# ---------------------------------





bio = st.text_area(
    "✍️ BIO",
    value=profile.get("bio", ""),
    placeholder="Tell us a little about yourself — your fitness journey, goals, or motivation...",
    height=120
)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------
# FITNESS DETAILS SECTION
# ---------------------------------

st.markdown(
    '<div class="section-title">💪 Fitness Details</div>',
    unsafe_allow_html=True
)



# ---------------------------------
# ROW 1
# ---------------------------------

col1, col2 = st.columns(2)

with col1:
    name = st.text_input(
        "👤 Name",
        value=profile.get("name", "")
    )

with col2:
    age = st.number_input(
        "🎂 Age",
        min_value=1,
        max_value=100,
        value=int(profile.get("age", 18))
    )

# ---------------------------------
# ROW 2
# ---------------------------------

col3, col4 = st.columns(2)

with col3:
    gender = st.selectbox(
        "⚧ Gender",
        gender_options,
        index=gender_idx
    )

with col4:
    activity_level = st.selectbox(
        "🏃 Activity Level",
        activity_options,
        index=activity_idx
    )

# ---------------------------------
# ROW 3
# ---------------------------------

col5, col6 = st.columns(2)

with col5:
    height = st.number_input(
        "📏 Height (cm)",
        min_value=50,
        max_value=250,
        value=int(profile.get("height", 170))
    )

with col6:
    weight = st.number_input(
        "⚖️ Weight (kg)",
        min_value=20,
        max_value=300,
        value=int(profile.get("weight", 70))
    )

# ---------------------------------
# ROW 4
# ---------------------------------

goal = st.selectbox(
    "🎯 Fitness Goal",
    goal_options,
    index=goal_idx
)

diet_preference = st.selectbox(
    "🥗 Dietary Preference",
    diet_options,
    index=diet_idx
)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------
# SAVE BUTTON
# ---------------------------------

if st.button("💾 Save Profile"):

    profile_data = {
        "name": name,
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "goal": goal,
        "activity_level": activity_level,
        "diet_preference": diet_preference,
        "bio": bio
    }

    

    # Save to your structured user directory: data/users/{username}/profile.json
    save_profile(username, profile_data)

    st.success("✅ Changes saved successfully!")
    