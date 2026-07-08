import streamlit as st
# Auth Gate for sub-pages
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please log in on the main page first!")
    st.stop()

# Import our user-scoped signature saving function
from utils.history_utils import save_history_item
from datetime import datetime

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Health.io | BMI Calculator",
    page_icon="💪",
    layout="wide"
)

# Grab the active user session context
username = st.session_state["username"]

# -----------------------------------
# CUSTOM CSS
# -----------------------------------
st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

h1, h2, h3 {
    color: white;
}

.stNumberInput label {
    color: #D1D5DB !important;
    font-size: 16px;
    font-weight: 600;
}

.stButton button {
    width: 100%;
    background: linear-gradient(90deg, #4F46E5, #7C3AED);
    color: white;
    border-radius: 12px;
    height: 3rem;
    border: none;
    font-size: 16px;
    font-weight: 600;
    transition: 0.3s;
}

.stButton button:hover {
    transform: scale(1.02);
    background: linear-gradient(90deg, #4338CA, #6D28D9);
}

.metric-card {
    background: #161B22;
    padding: 25px;
    border-radius: 20px;
    border: 1px solid #2A2F3A;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.25);
}

.bmi-value {
    font-size: 48px;
    font-weight: 700;
    color: #8B5CF6;
}

.bmi-label {
    font-size: 18px;
    color: #9CA3AF;
}

.tip-box {
    background-color: #111827;
    padding: 18px;
    border-radius: 15px;
    border-left: 5px solid #8B5CF6;
    margin-top: 20px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# HEADER
# -----------------------------------
st.markdown("""
<h1 style='text-align:center;'>💪 AI BMI Calculator</h1>
<p style='text-align:center; color: #9CA3AF; font-size:18px;'>
Track your body metrics and understand your health better.
</p>
""", unsafe_allow_html=True)

st.write("")

# -----------------------------------
# MAIN LAYOUT
# -----------------------------------
col1, col2 = st.columns([1, 1])

# -----------------------------------
# INPUT SECTION
# -----------------------------------
with col1:

    st.markdown("### Enter Your Details")

    weight = st.number_input(
        "Weight (kg)",
        min_value=1.0,
        max_value=300.0,
        step=0.5,
        value=70.0
    )

    height = st.number_input(
        "Height (meters)",
        min_value=0.5,
        max_value=2.5,
        step=0.01,
        value=1.70
    )

    calculate = st.button("Calculate BMI")

# -----------------------------------
# RESULT SECTION
# -----------------------------------
with col2:

    st.markdown("### Your Results")

    if calculate:

        bmi = weight / (height ** 2)
        bmi = round(bmi, 2)

        # BMI CATEGORY
        if bmi < 18.5:
            category = "Underweight"
            color = "#FBBF24"
            tip = "Increase calorie intake and focus on nutritious meals."
        
        elif bmi < 25:
            category = "Normal Weight"
            color = "#10B981"
            tip = "Great job! Maintain your healthy lifestyle."

        elif bmi < 30:
            category = "Overweight"
            color = "#F97316"
            tip = "Focus on regular workouts and balanced nutrition."

        else:
            category = "Obese"
            color = "#EF4444"
            tip = "Consider a structured fitness and nutrition plan."

        # RESULT CARD
        st.markdown(f"""
        <div class="metric-card">
            <div class="bmi-label">Your BMI</div>
            <div class="bmi-value">{bmi}</div>
            <div style="font-size:20px; font-weight:600; color:{color};">
                {category}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # PROGRESS BAR
        progress = min(bmi / 40, 1.0)
        st.progress(progress)

        # HEALTH TIP
        st.markdown(f"""
        <div class="tip-box">
            <h4 style="color:white;">💡 AI Health Tip</h4>
            <p style="color:#D1D5DB;">
                {tip}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # USER-SCOPED SAVE LOG EXECUTIONS
        save_history_item(username, {
            "type": "BMI",
            "weight": weight,
            "height": height,
            "bmi": bmi,
            "category": category,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.success("Measurement recorded successfully!")

# -----------------------------------
# BMI REFERENCE SECTION
# -----------------------------------
st.write("")
st.markdown("## BMI Reference Guide")

ref1, ref2, ref3, ref4 = st.columns(4)

with ref1:
    st.info("🔹 Underweight\n\nBMI < 18.5")

with ref2:
    st.success("🟢 Normal\n\nBMI 18.5 - 24.9")

with ref3:
    st.warning("🟠 Overweight\n\nBMI 25 - 29.9")

with ref4:
    st.error("🔴 Obese\n\nBMI 30+")