import streamlit as st

# Auth Gate
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please log in on the main page first!")
    st.stop()

from ai.workout_ai import generate_workout
from utils.timer_utils import (
    init_timer, start_timer,
    pause_timer, resume_timer, update_timer
)
from utils.workout_utils import save_workout, save_completed_workout
from utils.progress_utils import load_stats, update_stats

# ── PAGE CONFIG ────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Workout Planner",
    page_icon="🏋️",
    layout="wide"
)

username = st.session_state["username"]

# ── STYLES ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: #080c14 !important;
    font-family: 'DM Sans', sans-serif;
    color: #e2e8f0;
}

.block-container {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 1380px !important;
}

/* ── HEADER ── */
.page-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding: 2.5rem 0 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 2.5rem;
}
.page-header-left h1 {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -1px;
    color: #fff;
    line-height: 1;
}
.page-header-left p {
    color: #64748b;
    font-size: 0.95rem;
    margin-top: 0.5rem;
    font-weight: 400;
}
.badge-pill {
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
    color: white;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.3rem 0.9rem;
    border-radius: 999px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ── STAT CARDS ── */
.stat-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}
.stat-card {
    background: #0d1420;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #06b6d4, #3b82f6);
}
.stat-card .label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #475569;
    margin-bottom: 0.5rem;
}
.stat-card .value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #f8fafc;
    line-height: 1;
}
.stat-card .unit {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 0.25rem;
    font-weight: 400;
}

/* ── SECTION LABEL ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #06b6d4;
    margin-bottom: 0.75rem;
}
.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: #f1f5f9;
    margin-bottom: 1.25rem;
}

/* ── PANEL ── */
.panel {
    background: #0d1420;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 1.75rem;
    margin-bottom: 1.25rem;
}

/* ── EXERCISE CARD ── */
.ex-card {
    background: linear-gradient(135deg, #0f1f35 0%, #0d1420 100%);
    border: 1px solid rgba(6,182,212,0.2);
    border-radius: 16px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1rem;
}
.ex-name {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #fff;
    margin-bottom: 0.75rem;
}
.ex-meta {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
}
.ex-meta-item {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
}
.ex-meta-item .m-label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #475569;
    font-weight: 600;
}
.ex-meta-item .m-val {
    font-size: 1.05rem;
    font-weight: 600;
    color: #e2e8f0;
}

/* ── EXERCISE LIST ── */
.ex-list-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.9rem;
}
.ex-list-item:last-child { border-bottom: none; }
.ex-list-item .ex-num {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 800;
    color: #475569;
    width: 1.5rem;
    text-align: right;
}
.ex-list-item .ex-name-sm {
    flex: 1;
    font-weight: 500;
    color: #cbd5e1;
}
.ex-list-item.done .ex-name-sm { color: #475569; text-decoration: line-through; }
.ex-list-item.current .ex-name-sm { color: #06b6d4; font-weight: 700; }
.ex-list-item .ex-dur {
    font-size: 0.78rem;
    color: #475569;
    font-weight: 500;
}
.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.dot-done { background: #22c55e; }
.dot-current { background: #06b6d4; animation: pulse 1.5s infinite; }
.dot-pending { background: #1e293b; border: 1px solid #334155; }
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.75); }
}

/* ── TIMER ── */
.timer-ring-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.5rem 0;
}
.timer-number {
    font-family: 'Syne', sans-serif;
    font-size: 5rem;
    font-weight: 800;
    color: #06b6d4;
    line-height: 1;
    letter-spacing: -2px;
}
.timer-label {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #475569;
    margin-top: 0.4rem;
}
.timer-rest .timer-number { color: #f59e0b; }

/* ── PROGRESS BAR ── */
.prog-wrap {
    background: #1e293b;
    border-radius: 999px;
    height: 6px;
    overflow: hidden;
    margin: 0.5rem 0 1rem;
}
.prog-fill {
    height: 100%;
    background: linear-gradient(90deg, #06b6d4, #3b82f6);
    border-radius: 999px;
    transition: width 0.4s ease;
}

/* ── BUTTONS ── */
.stButton > button {
    background: #0d1420 !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 0.65rem 1.2rem !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    width: 100% !important;
    transition: all 0.2s !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: #131e30 !important;
    border-color: #06b6d4 !important;
    color: #06b6d4 !important;
    transform: translateY(-1px) !important;
}

/* Primary generate button */
div[data-testid="stButton"]:first-of-type > button {
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.85rem !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
}

/* ── SELECTBOX / SLIDER ── */
.stSelectbox label, .stSlider label {
    color: #64748b !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
.stSelectbox > div > div {
    background: #0d1420 !important;
    border-color: rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
}

/* ── CALORIE BANNER ── */
.cal-banner {
    background: linear-gradient(135deg, #0f2b1f 0%, #0d1420 100%);
    border: 1px solid rgba(34,197,94,0.2);
    border-radius: 16px;
    padding: 1.2rem 1.75rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}
.cal-banner .cb-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #22c55e;
    font-weight: 600;
    margin-bottom: 0.2rem;
}
.cal-banner .cb-val {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #22c55e;
}
.cal-banner .cb-note {
    font-size: 0.78rem;
    color: #475569;
    max-width: 200px;
    text-align: right;
    line-height: 1.5;
}

/* ── COMPLETE SCREEN ── */
.complete-hero {
    text-align: center;
    padding: 3rem 2rem;
}
.complete-hero h2 {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: #22c55e;
    margin-bottom: 0.5rem;
}
.complete-hero p {
    color: #64748b;
    font-size: 1rem;
}

/* streamlit overrides */
[data-testid="metric-container"] { display: none; }
div.stSuccess, div.stWarning, div.stInfo {
    border-radius: 12px !important;
    font-size: 0.88rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── CALORIE CALCULATION (MET-based) ────────────────────────────
# MET values per exercise type
MET_MAP = {
    "jumping jacks": 8.0, "burpees": 10.0, "mountain climbers": 9.0,
    "high knees": 8.5, "squat jumps": 9.5, "push ups": 6.0,
    "pull ups": 8.0, "dips": 6.0, "plank": 4.0, "sit ups": 5.0,
    "crunches": 5.0, "leg raises": 4.5, "lunges": 6.0, "squats": 6.0,
    "deadlifts": 6.0, "rows": 6.0, "shoulder press": 5.5,
    "bicep curls": 4.5, "tricep extensions": 4.5, "lat pulldown": 6.0,
    "chest press": 5.5, "jump rope": 11.0, "box jumps": 10.0,
    "bear crawls": 8.0, "inchworms": 5.5, "glute bridges": 4.0,
}
DEFAULT_MET = 6.5  # fallback for unknown exercises

def get_met(exercise_name: str) -> float:
    name_lower = exercise_name.lower()
    for key, met in MET_MAP.items():
        if key in name_lower:
            return met
    return DEFAULT_MET

def calc_calories(exercise_name: str, duration_seconds: int, weight_kg: float = 70.0) -> float:
    """
    Calories = MET × weight(kg) × time(hours)
    Uses user weight from profile if available, else 70 kg default.
    """
    met = get_met(exercise_name)
    hours = duration_seconds / 3600
    return round(met * weight_kg * hours, 1)

# ── LOAD STATS ─────────────────────────────────────────────────
stats = load_stats()

# ── SESSION STATE DEFAULTS ─────────────────────────────────────
defaults = {
    "i": 0, "cal": 0.0, "workout": [],
    "exercise_done": False, "workout_started": False,
    "mode": "exercise", "rest_done": False,
    "workout_complete": False,
    "calories_logged": set(),   # track which exercise indices already counted
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HEADER ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
  <div class="page-header-left">
    <h1>🏋️ Workout Planner</h1>
    <p>AI-generated sessions tailored to your goals and fitness level</p>
  </div>
  <span class="badge-pill">AI Powered</span>
</div>
""", unsafe_allow_html=True)

# ── STAT CARDS ─────────────────────────────────────────────────
total_cal = st.session_state.cal
streak    = stats.get("streak", 0)
total_wo  = stats.get("total_workouts", 0)
lvl       = stats.get("level", "Beginner")
n_ex      = len(st.session_state.workout)

st.markdown(f"""
<div class="stat-row">
  <div class="stat-card">
    <div class="label">🔥 Streak</div>
    <div class="value">{streak}</div>
    <div class="unit">days in a row</div>
  </div>
  <div class="stat-card">
    <div class="label">💪 Total Workouts</div>
    <div class="value">{total_wo}</div>
    <div class="unit">sessions completed</div>
  </div>
  <div class="stat-card">
    <div class="label">⚡ Fitness Level</div>
    <div class="value" style="font-size:1.4rem;padding-top:0.3rem">{lvl}</div>
    <div class="unit">current tier</div>
  </div>
  <div class="stat-card">
    <div class="label">🔥 Calories Burned</div>
    <div class="value">{total_cal:.1f}</div>
    <div class="unit">kcal this session</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TIMER INIT ─────────────────────────────────────────────────
init_timer()

# ── PREFERENCES ────────────────────────────────────────────────
st.markdown('<div class="section-label">Configuration</div>', unsafe_allow_html=True)
st.markdown('<div class="section-heading">⚙️ Workout Preferences</div>', unsafe_allow_html=True)

with st.container():
    
    c1, c2, c3 = st.columns(3)
    with c1:
        goal     = st.selectbox("🎯 Goal",       ["Fat Loss", "Muscle Gain", "Fitness"])
        level    = st.selectbox("📈 Experience", ["Beginner", "Intermediate", "Advanced"])
    with c2:
        location = st.selectbox("📍 Location",   ["Home", "Gym"])
        duration = st.slider("⏱ Duration (min)", 20, 120, 45)
    with c3:
        rest     = st.slider("😴 Rest (sec)", 10, 60, 30)
        weight_kg = st.number_input("⚖️ Your Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5,
                                     help="Used for accurate calorie calculation (MET formula)")
    st.markdown('</div>', unsafe_allow_html=True)

# ── GENERATE BUTTON ────────────────────────────────────────────
if st.button("✨ Generate AI Workout"):
    with st.spinner("Building your personalized workout..."):
        raw = generate_workout(goal, level, location, duration, rest)

    # Inject accurate calories into each exercise using MET formula
    for ex in raw:
        ex["cal"] = calc_calories(ex["name"], ex["time"], weight_kg)

    st.session_state.workout          = raw
    st.session_state.i                = 0
    st.session_state.cal              = 0.0
    st.session_state.calories_logged  = set()
    st.session_state.exercise_done    = False
    st.session_state.rest_done        = False
    st.session_state.mode             = "exercise"
    st.session_state.workout_started  = False
    st.session_state.workout_complete = False
    st.session_state.timer_running    = False
    st.session_state.timer_paused     = False
    st.session_state.remaining_time   = 0

    save_workout(st.session_state.workout, 0)
    st.rerun()

# ── WORKOUT SESSION ─────────────────────────────────────────────
if st.session_state.workout:

    workout = st.session_state.workout
    i       = st.session_state.i

    # ── COMPLETE SCREEN ─────────────────────────────────────────
    if st.session_state.workout_complete:

        update_stats()
        st.balloons()

        total = st.session_state.cal
        st.markdown(f"""
        <div class="panel complete-hero">
          <h2>🏆 Workout Complete!</h2>
          <p>Outstanding effort — here's your session summary</p>
          <div style="margin-top:2rem">
            <div class="label" style="color:#22c55e;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em">Total Calories Burned</div>
            <div style="font-family:'Syne',sans-serif;font-size:4rem;font-weight:800;color:#22c55e;line-height:1">{total:.1f}</div>
            <div style="color:#64748b;font-size:0.85rem;margin-top:0.25rem">kcal · MET-calculated for your body weight</div>
          </div>
          <div style="display:flex;gap:2rem;justify-content:center;margin-top:2rem">
            <div>
              <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:#f1f5f9">{len(workout)}</div>
              <div style="color:#64748b;font-size:0.8rem">Exercises</div>
            </div>
            <div>
              <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:#f1f5f9">{duration}</div>
              <div style="color:#64748b;font-size:0.8rem">Minutes</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💾 Save Workout"):
            try:
                save_completed_workout(workout, st.session_state.cal, duration, goal)
            except TypeError:
                save_completed_workout(workout, st.session_state.cal)
            st.success("Workout saved successfully ✅")

        st.stop()

    # ── SAFETY CHECK ────────────────────────────────────────────
    if i >= len(workout):
        st.success("Workout Completed ✅")
        st.stop()

    ex = workout[i]

    # ── LAYOUT: LEFT = SESSION, RIGHT = PLAN ────────────────────
    left, right = st.columns([3, 2], gap="large")

    with right:
        st.markdown('<div class="section-label">Session Plan</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">📋 Today\'s Exercises</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel" style="padding:1.25rem 1.5rem">', unsafe_allow_html=True)

        for n, w in enumerate(workout):
            if n < i:
                dot = '<span class="status-dot dot-done"></span>'
                cls = "done"
            elif n == i:
                dot = '<span class="status-dot dot-current"></span>'
                cls = "current"
            else:
                dot = '<span class="status-dot dot-pending"></span>'
                cls = ""

            cal_label = f"{w['cal']:.1f} kcal"
            st.markdown(f"""
            <div class="ex-list-item {cls}">
              {dot}
              <span class="ex-num">{n+1}</span>
              <span class="ex-name-sm">{w['name']}</span>
              <span class="ex-dur">{w['time']}s · {cal_label}</span>
            </div>
            """, unsafe_allow_html=True)

        total_plan_cal = sum(w["cal"] for w in workout)
        st.markdown(f"""
        <div style="margin-top:1rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.06);
                    display:flex;justify-content:space-between;align-items:center">
          <span style="color:#475569;font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em">Session Total</span>
          <span style="font-family:'Syne',sans-serif;font-weight:800;color:#22c55e;font-size:1.1rem">{total_plan_cal:.1f} kcal</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Progress
        pct = i / len(workout)
        pct_w = int(pct * 100)
        st.markdown(f"""
        <div style="margin-top:0.5rem">
          <div style="display:flex;justify-content:space-between;margin-bottom:0.4rem">
            <span style="color:#475569;font-size:0.75rem;font-weight:600">PROGRESS</span>
            <span style="color:#06b6d4;font-size:0.75rem;font-weight:700">{i}/{len(workout)} done</span>
          </div>
          <div class="prog-wrap"><div class="prog-fill" style="width:{pct_w}%"></div></div>
        </div>
        """, unsafe_allow_html=True)

    with left:
        st.markdown('<div class="section-label">Current Exercise</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-heading">Exercise {i+1} of {len(workout)}</div>', unsafe_allow_html=True)

        # Current exercise card
        mode_is_rest = st.session_state.mode == "rest"
        if not mode_is_rest:
            st.markdown(f"""
            <div class="ex-card">
              <div class="ex-name">{ex['name']}</div>
              <div class="ex-meta">
                <div class="ex-meta-item">
                  <span class="m-label">Duration</span>
                  <span class="m-val">⏱ {ex['time']} sec</span>
                </div>
                <div class="ex-meta-item">
                  <span class="m-label">Calories</span>
                  <span class="m-val">🔥 {ex['cal']:.1f} kcal</span>
                </div>
                <div class="ex-meta-item">
                  <span class="m-label">Rest after</span>
                  <span class="m-val">😴 {rest} sec</span>
                </div>
              </div>
              <div style="margin-top:1rem">
                <a href="{ex['youtube']}" target="_blank"
                   style="color:#06b6d4;font-size:0.85rem;font-weight:600;text-decoration:none">
                  ▶ Watch Tutorial →
                </a>
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ex-card" style="border-color:rgba(245,158,11,0.25);background:linear-gradient(135deg,#1f1a0f,#0d1420)">
              <div class="ex-name" style="color:#f59e0b">😴 Rest Period</div>
              <div class="ex-meta">
                <div class="ex-meta-item">
                  <span class="m-label">Rest Duration</span>
                  <span class="m-val" style="color:#f59e0b">⏱ {rest} sec</span>
                </div>
                <div class="ex-meta-item">
                  <span class="m-label">Up Next</span>
                  <span class="m-val">{workout[i+1]['name'] if i+1 < len(workout) else 'Finish 🎉'}</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Calorie burned so far
        st.markdown(f"""
        <div class="cal-banner">
          <div>
            <div class="cb-label">🔥 Burned This Session</div>
            <div class="cb-val">{st.session_state.cal:.1f} <span style="font-size:1rem;color:#16a34a">kcal</span></div>
          </div>
          <div class="cb-note">Calculated using MET × body weight × time</div>
        </div>
        """, unsafe_allow_html=True)

        # ── TIMER PANEL ─────────────────────────────────────────
        st.markdown('<div class="panel">', unsafe_allow_html=True)

        if not st.session_state.timer_running:
            if st.session_state.mode == "exercise":
                if st.button("▶ Start Exercise"):
                    st.session_state.workout_started = True
                    st.session_state.exercise_done   = False
                    start_timer(ex["time"], "Exercise")
                    st.rerun()
            else:
                if st.button("▶ Start Rest"):
                    st.session_state.rest_done = False
                    start_timer(rest, "Rest")
                    st.rerun()

        if st.session_state.timer_running:
            remaining  = st.session_state.remaining_time
            total_time = ex["time"] if st.session_state.mode == "exercise" else rest
            progress   = max(0, (total_time - remaining) / total_time)
            prog_w     = int(progress * 100)
            timer_cls  = "timer-rest" if mode_is_rest else ""
            color      = "#f59e0b" if mode_is_rest else "#06b6d4"

            st.markdown(f"""
            <div class="timer-ring-wrap {timer_cls}">
              <div class="timer-number" style="color:{color}">{remaining}</div>
              <div class="timer-label">{st.session_state.timer_type} · {remaining}s remaining</div>
            </div>
            <div class="prog-wrap">
              <div class="prog-fill" style="width:{prog_w}%;background:{'#f59e0b' if mode_is_rest else 'linear-gradient(90deg,#06b6d4,#3b82f6)'}"></div>
            </div>
            """, unsafe_allow_html=True)

            tc1, tc2 = st.columns(2)
            with tc1:
                if st.button("⏸ Pause"):
                    pause_timer()
            with tc2:
                if st.button("▶ Resume"):
                    resume_timer()

            if st.session_state.timer_paused:
                st.warning("⏸ Timer paused")
            else:
                st.info("▶ Timer running")

        st.markdown('</div>', unsafe_allow_html=True)

        # ── CONTROLS ────────────────────────────────────────────
        st.markdown('<div class="section-label" style="margin-top:1rem">Navigation</div>', unsafe_allow_html=True)

        nc1, nc2, nc3, nc4 = st.columns(4)

        def reset_timer():
            st.session_state.timer_running   = False
            st.session_state.timer_paused    = False
            st.session_state.remaining_time  = 0
            st.session_state.exercise_done   = False
            st.session_state.rest_done       = False
            st.session_state.mode            = "exercise"
            st.session_state.workout_started = False

        with nc1:
            if st.button("⬅ Prev"):
                if i > 0:
                    reset_timer()
                    st.session_state.i -= 1
                    st.rerun()

        with nc2:
            if st.button("➡ Skip"):
                if i < len(workout) - 1:
                    reset_timer()
                    st.session_state.i += 1
                    st.rerun()

        with nc3:
            if st.button("🔄 Redo"):
                st.session_state.exercise_done   = False
                st.session_state.mode            = "exercise"
                st.session_state.workout_started = True
                start_timer(ex["time"], "Exercise")
                st.rerun()

        with nc4:
            if st.button("🛑 End"):
                reset_timer()
                try:
                    save_completed_workout(workout, st.session_state.cal, duration, goal)
                except TypeError:
                    save_completed_workout(workout, st.session_state.cal)
                st.session_state.workout_complete = True
                st.rerun()

    # ── TIMER COMPLETE LOGIC ────────────────────────────────────
    if (
        st.session_state.workout_started
        and not st.session_state.timer_running
        and st.session_state.remaining_time == 0
    ):
        if (
            st.session_state.mode == "exercise"
            and not st.session_state.exercise_done
        ):
            # Only count calories once per exercise index
            if i not in st.session_state.calories_logged:
                st.session_state.cal += ex["cal"]
                st.session_state.calories_logged.add(i)

            st.session_state.exercise_done = True
            st.session_state.mode          = "rest"
            st.session_state.rest_done     = False
            start_timer(rest, "Rest")
            st.rerun()

        elif (
            st.session_state.mode == "rest"
            and not st.session_state.rest_done
        ):
            st.session_state.rest_done = True

            if i < len(workout) - 1:
                reset_timer()
                st.session_state.i += 1
                st.rerun()
            else:
                st.session_state.workout_complete = True
                st.rerun()

    update_timer()