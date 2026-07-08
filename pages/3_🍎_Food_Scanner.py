import streamlit as st

# Auth Gate for sub-pages
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please log in on the main page first!")
    st.stop()

from PIL import Image
from google import genai
import os
import json
from dotenv import load_dotenv
from utils.history_utils import load_history, save_history_item
from ai.context import load_profile
from datetime import datetime
from utils.nutrition_utils import add_nutrition

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

.glass-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 24px;
    margin-bottom: 20px;
}

.section-title {
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 18px;
    color: white;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #f97316, #ea580c);
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
    background: linear-gradient(90deg, #ea580c, #c2410c);
}

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 18px;
}

.stInfo { border-radius: 14px; }
.stSuccess { border-radius: 14px; }
img { border-radius: 18px; }

</style>
""", unsafe_allow_html=True)

# -------------------------
# LOAD ENV + PROFILE
# -------------------------

load_dotenv()

username = st.session_state["username"]
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
<div class="hero-title">🍎 AI Food Scanner</div>
<div class="hero-subtitle">
Upload your meal image and receive AI-powered nutrition analysis,
calorie estimation, macro breakdown, and personalized health advice
based on your fitness goals.
</div>
</div>
""", unsafe_allow_html=True)

# -------------------------
# PROFILE INFO BANNER
# -------------------------

if profile and profile.get('name'):
    st.info(
        f"👤 Personalized for: **{profile.get('name')}** "
        f"🎯 Goal: **{profile.get('goal', 'General Fitness')}** "
        f"🏃 Activity Level: **{profile.get('activity_level', 'Moderate')}**"
    )
else:
    st.warning("⚠️ Profile metrics not configured yet. Go to the Profile page to sync personalized AI recommendations.")

# -------------------------
# UPLOAD + PREVIEW LAYOUT
# -------------------------

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="section-title">📤 Upload Food Image</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Food Image", type=["jpg", "jpeg", "png"])
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-title">🖼️ Preview</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Food Image", use_container_width=True)
    else:
        st.info("Upload a food image to preview it here.")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# ANALYZE BUTTON + RESULTS
# -------------------------

if uploaded_file is not None:

    image = Image.open(uploaded_file)

    if st.button("🚀 Analyze Food"):

        with st.spinner("AI is analyzing your meal..."):

            prompt = f"""
            Analyze this food image.

            Return ONLY valid JSON with no markdown, no explanations, just the JSON object:

            {{
             "food_name": "",
             "calories": 0,
             "protein": 0,
             "carbs": 0,
             "fat": 0,
             "advice": ""
            }}

            User Goal: {profile.get('goal', 'General Fitness')}
            User Age: {profile.get('age', 'Unknown')}
            User Gender: {profile.get('gender', 'Unknown')}
            Activity Level: {profile.get('activity_level', 'Moderate')}
            """

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[image, prompt]
            )

        # -------------------------
        # DISPLAY RESULTS
        # -------------------------

        st.markdown('<div class="section-title">📊 AI Nutrition Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        try:
            raw_text = response.text.strip()

            # Strip markdown code fences if Gemini wraps in them
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text.replace("```", "").strip()

            result = json.loads(raw_text)

            food_name = result.get("food_name", "Unknown Food")
            calories  = int(result.get("calories", 0))
            protein   = int(result.get("protein", 0))
            carbs     = int(result.get("carbs", 0))
            fat       = int(result.get("fat", 0))
            advice    = result.get("advice", "")

            # Metric cards
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("🔥 Calories", calories)
            with c2: st.metric("💪 Protein",  f"{protein} g")
            with c3: st.metric("🥖 Carbs",    f"{carbs} g")
            with c4: st.metric("🧈 Fat",      f"{fat} g")

            st.markdown("---")
            st.subheader("🍽 Food Detected")
            st.write(food_name)

            if advice:
                st.info(advice)

            # Save to nutrition tracker and history
            add_nutrition(username, calories, protein)

            save_history_item(username, {
                "type":      "Food Scan",
                "food_name": food_name,
                "calories":  calories,
                "protein":   protein,
                "carbs":     carbs,
                "fat":       fat,
                "result":    raw_text,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            st.success("Food analysis completed and added to today's nutrition!")

        except Exception as e:

            # Fallback: show raw text if JSON parsing fails
            st.write(response.text)

            save_history_item(username, {
                "type":      "Food Scan",
                "result":    response.text,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            st.warning("Nutrition values could not be extracted automatically.")
            st.caption(f"Debug: {e}")

        st.markdown('</div>', unsafe_allow_html=True)