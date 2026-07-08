import streamlit as st

# Auth Gate
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please log in on the main page first!")
    st.stop()

from collections import defaultdict
from utils.workout_utils import (
    load_completed_workouts,
    delete_completed_workout,
    delete_all_completed_workouts
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Workout Analytics", page_icon="📊", layout="wide")

# ---------------- STYLES ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, .stApp {
    background: #080c14 !important;
    font-family: 'DM Sans', sans-serif;
    color: #e2e8f0;
}
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1300px !important; }

.page-header { padding: 2rem 0 1.75rem; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 2rem; }
.page-header h1 { font-family: 'Syne', sans-serif; font-size: 2.8rem; font-weight: 800; color: #fff; letter-spacing: -1px; line-height: 1; }
.page-header p { color: #64748b; font-size: 0.9rem; margin-top: 0.4rem; }

.summary-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }
.summary-card {
    background: #0d1420;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 1.3rem 1.5rem;
    position: relative; overflow: hidden;
}
.summary-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #06b6d4, #3b82f6);
}
.summary-card .sc-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #475569; margin-bottom: 0.4rem; }
.summary-card .sc-value { font-family: 'Syne', sans-serif; font-size: 1.9rem; font-weight: 800; color: #f8fafc; line-height: 1; }
.summary-card .sc-unit { font-size: 0.75rem; color: #64748b; margin-top: 0.2rem; }

.day-label {
    font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 800;
    color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em;
    margin: 1.75rem 0 0.75rem; padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}

.wo-card {
    background: #0d1420;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1rem;
}
.wo-card-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 1.25rem; }
.wo-goal { font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 800; color: #f1f5f9; }
.wo-time { font-size: 0.78rem; color: #475569; margin-top: 0.2rem; }

.wo-metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; margin-bottom: 1.25rem; }
.wo-metric { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 0.9rem 1rem; }
.wo-metric .wm-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #475569; margin-bottom: 0.3rem; }
.wo-metric .wm-val { font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 800; color: #e2e8f0; }

.ex-row {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.55rem 0; border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.85rem;
}
.ex-row:last-child { border-bottom: none; }
.ex-dot { width: 6px; height: 6px; border-radius: 50%; background: #22c55e; flex-shrink: 0; }
.ex-name-cell { flex: 1; color: #cbd5e1; font-weight: 500; }
.ex-stat { color: #475569; font-size: 0.78rem; }

.stButton > button {
    background: #0d1420 !important; color: #94a3b8 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important; padding: 0.5rem 1rem !important;
    font-size: 0.82rem !important; font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: #ef4444 !important; color: #ef4444 !important;
    background: rgba(239,68,68,0.05) !important;
}
[data-testid="metric-container"] { display: none !important; }
div.stSuccess, div.stInfo, div.stWarning { border-radius: 12px !important; font-size: 0.85rem !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD WORKOUTS ----------------
workouts = load_completed_workouts()

# ---------------- HEADER ----------------
st.markdown("""
<div class="page-header">
  <h1>📊 Workout Analytics</h1>
  <p>Your complete training history and performance overview</p>
</div>
""", unsafe_allow_html=True)

# ---------------- EMPTY STATE ----------------
if not workouts:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;background:#0d1420;border:1px solid rgba(255,255,255,0.07);border-radius:20px">
      <div style="font-size:3rem;margin-bottom:1rem">🏋️</div>
      <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;color:#f1f5f9;margin-bottom:0.5rem">No workouts yet</div>
      <div style="color:#64748b;font-size:0.9rem">Complete a session in the Workout Planner to see your analytics here.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ---------------- SUMMARY STATS ----------------
total_sessions  = len(workouts)
total_cal       = sum(w.get("total_calories", 0) for w in workouts)
total_exercises = sum(w.get("exercise_count", 0) for w in workouts)
total_minutes   = sum(w.get("duration", 0) for w in workouts)

st.markdown(f"""
<div class="summary-row">
  <div class="summary-card">
    <div class="sc-label">💪 Total Sessions</div>
    <div class="sc-value">{total_sessions}</div>
    <div class="sc-unit">workouts completed</div>
  </div>
  <div class="summary-card">
    <div class="sc-label">🔥 Total Calories</div>
    <div class="sc-value">{total_cal:.1f}</div>
    <div class="sc-unit">kcal burned overall</div>
  </div>
  <div class="summary-card">
    <div class="sc-label">⚡ Exercises Done</div>
    <div class="sc-value">{total_exercises}</div>
    <div class="sc-unit">individual exercises</div>
  </div>
  <div class="summary-card">
    <div class="sc-label">⏱ Total Time</div>
    <div class="sc-value">{total_minutes}</div>
    <div class="sc-unit">minutes trained</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------- DELETE ALL ----------------
_, btn_col = st.columns([6, 1])
with btn_col:
    if st.button("🗑 Delete All"):
        delete_all_completed_workouts()
        st.success("All workouts deleted.")
        st.rerun()

# ---------------- GROUP BY DATE ----------------
# Store GLOBAL index alongside each workout so delete targets the right entry
workouts_by_day = defaultdict(list)
for global_idx, workout in enumerate(workouts):
    date = workout.get("completed_at", "Unknown Date").split(" ")[0]
    workouts_by_day[date].append((global_idx, workout))

# ---------------- DISPLAY ----------------
for date, day_workouts in reversed(sorted(workouts_by_day.items())):

    st.markdown(f'<div class="day-label">📅 {date}</div>', unsafe_allow_html=True)

    for global_idx, workout in day_workouts:

        st.markdown('<div class="wo-card">', unsafe_allow_html=True)

        # Header row: goal + delete button
        hc1, hc2 = st.columns([5, 1])
        with hc1:
            goal = workout.get("goal", "Workout Session")
            completed_at = workout.get("completed_at", "N/A")
            st.markdown(f"""
            <div class="wo-card-header">
              <div>
                <div class="wo-goal">🎯 {goal}</div>
                <div class="wo-time">Completed at {completed_at}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        with hc2:
            # Use global_idx so the correct entry is deleted
            if st.button("❌ Delete", key=f"del_{global_idx}"):
                delete_completed_workout(global_idx)
                st.success("Workout deleted.")
                st.rerun()

        # Metrics
        cal      = workout.get("total_calories", 0)
        duration = workout.get("duration", 0)
        ex_count = workout.get("exercise_count", 0)
        st.markdown(f"""
        <div class="wo-metrics">
          <div class="wo-metric">
            <div class="wm-label">🔥 Calories</div>
            <div class="wm-val">{cal:.1f} <span style="font-size:0.8rem;color:#64748b">kcal</span></div>
          </div>
          <div class="wo-metric">
            <div class="wm-label">⏱ Duration</div>
            <div class="wm-val">{duration} <span style="font-size:0.8rem;color:#64748b">min</span></div>
          </div>
          <div class="wo-metric">
            <div class="wm-label">⚡ Exercises</div>
            <div class="wm-val">{ex_count}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Exercise breakdown
        exercises = workout.get("workout", [])
        if exercises:
            st.markdown('<div style="margin-top:0.25rem">', unsafe_allow_html=True)
            for ex in exercises:
                name     = ex.get("name", "Exercise")
                duration_ex = ex.get("time", 0)
                cal_ex   = ex.get("cal", 0)
                cal_str  = f"{cal_ex:.1f}" if isinstance(cal_ex, float) else str(cal_ex)
                st.markdown(f"""
                <div class="ex-row">
                  <span class="ex-dot"></span>
                  <span class="ex-name-cell">{name}</span>
                  <span class="ex-stat">{duration_ex}s</span>
                  <span class="ex-stat" style="color:#22c55e;font-weight:600">{cal_str} kcal</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#475569;font-size:0.85rem;padding:0.5rem 0">No exercise detail available.</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)