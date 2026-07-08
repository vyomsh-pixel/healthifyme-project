import streamlit as st
# Auth Gate for sub-pages
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please log in on the main page first!")
    st.stop()

from PIL import Image
from google import genai
from dotenv import load_dotenv
# Explicitly grab user-scoped data engines
from utils.history_utils import load_history, save_history_item
from ai.context import load_profile
import os
import json
from datetime import datetime

# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(
    page_title="Health.io",
    page_icon="💪",
    layout="wide"
)

# -------------------------
# CUSTOM UI
# -------------------------

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
    max-width: 1300px;
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
    padding: 24px;
    margin-bottom: 20px;
}

/* SECTION TITLES */

.section-title {
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 18px;
    color: white;
}

/* BUTTON */

.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #8b5cf6, #7c3aed);
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
    background: linear-gradient(90deg, #7c3aed, #6d28d9);
}

/* FILE UPLOADER */

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 18px;
}

/* INFO BOX */

.stInfo {
    border-radius: 14px;
}

/* SUCCESS */

.stSuccess {
    border-radius: 14px;
}

/* IMAGE */

img {
    border-radius: 18px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# LOAD ENV VARIABLES
# -------------------------

load_dotenv()

# Grab the active user session context
username = st.session_state["username"]

# Load profile data safely using your new backend file handler
profile = load_profile(username)

# -------------------------
# GEMINI CLIENT
# -------------------------

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -------------------------
# HERO SECTION
# -------------------------

st.markdown("""
<div class="hero-box">

<div class="hero-title">
🧴 AI Skin Scan
</div>

<div class="hero-subtitle">
Upload your face image and receive AI-powered skincare analysis,
skin issue detection, personalized skincare suggestions,
nutrition advice, and wellness recommendations instantly.
</div>

</div>
""", unsafe_allow_html=True)

# -------------------------
# PROFILE INFO
# -------------------------

if profile and profile.get('name'):
    st.info(
        f"""
        👤 Personalized for: **{profile.get('name')}** 🎯 Goal: **{profile.get('goal', 'General Fitness')}** 🏃 Activity Level: **{profile.get('activity_level', 'Moderate')}**
        """
    )
else:
    st.warning("⚠️ Profile metrics not configured yet. Go to the Profile page to sync personalized AI recommendations.")

# -------------------------
# MAIN LAYOUT
# -------------------------

col1, col2 = st.columns([1, 1])

# -------------------------
# LEFT SECTION
# -------------------------

with col1:

    st.markdown(
        '<div class="section-title">📤 Upload Face Image</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Face Image",
        type=["jpg", "jpeg", "png"]
    )

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# RIGHT SECTION
# -------------------------

with col2:

    st.markdown(
        '<div class="section-title">🖼️ Preview</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    if uploaded_file is not None:

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Uploaded Face Image",
            use_container_width=True
        )

    else:

        st.info("Upload an image to preview it here.")

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# PROCESS IMAGE
# -------------------------

if uploaded_file is not None:

    image = Image.open(uploaded_file)

    if st.button("✨ Analyze Skin"):

        with st.spinner("AI is scanning your skin..."):

            prompt = f"""
            Analyze this face image.

            Detect possible:
            - acne
            - pimples
            - oily skin
            - dryness
            - dark circles
            - pigmentation
            - redness

            Then provide:

            1. Skin issues detected
            2. Skincare tips
            3. Home remedies
            4. Product suggestions

            Rules:
            - Use short bullet points
            - Use simple English
            - Keep answers concise
            - Avoid long paragraphs
            - give answer in 1 line

            User Profile:
            Name: {profile.get('name', 'User')}
            Age: {profile.get('age', 'Unknown')}
            Gender: {profile.get('gender', 'Unknown')}
            Goal: {profile.get('goal', 'General Fitness')}
            Activity Level: {profile.get('activity_level', 'Moderate')}

            Give personalized nutrition advice based on the user's health goal.

            Keep the response clean and well formatted.
            """

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    image,
                    prompt
                ]
            )

            st.markdown(
                '<div class="section-title">✨ AI Skin Analysis</div>',
                unsafe_allow_html=True
            )

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)

            st.write(response.text)

            st.markdown('</div>', unsafe_allow_html=True)

            # -------------------------
            # USER-SCOPED SAVE HISTORY
            # -------------------------
            save_history_item(username, {
                "type": "Skin Scan",
                "result": response.text,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            st.success("Skin analysis completed successfully!")