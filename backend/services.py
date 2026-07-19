"""Deterministic, explainable wellness helpers used when an AI provider is absent.

Health.io deliberately treats generated material as general wellness guidance,
not a diagnosis.  The deterministic paths make demos dependable and transparent.
"""

from __future__ import annotations

from typing import Any

from backend.ai_services import generate_wellness_chat_reply, generate_ai_meal_plan, generate_ai_workout


def bmi_result(weight_kg: float, height_cm: float) -> dict[str, Any]:
    bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)
    if bmi < 18.5:
        category, guidance = "Below recommended range", "Focus on regular, nourishing meals and discuss persistent weight changes with a clinician."
    elif bmi < 25:
        category, guidance = "Within the usual range", "Keep supporting your routine with balanced meals, movement, sleep, and check-ins."
    elif bmi < 30:
        category, guidance = "Above recommended range", "Small, sustainable nutrition and activity habits are more useful than quick fixes."
    else:
        category, guidance = "Higher range", "Consider speaking with a qualified clinician for advice tailored to your health history."
    return {"bmi": bmi, "category": category, "guidance": guidance, "weight_kg": weight_kg, "height_cm": height_cm}


def make_meal_plan(goal: str, diet_type: str, budget: float | None, meals: int, note: str | None, profile: dict[str, Any] | None = None) -> str:
    # Try AI generation first
    ai_plan = generate_ai_meal_plan(goal, diet_type, budget, meals, note, profile)
    if ai_plan:
        return ai_plan

    breakfast = "Vegetable poha with curd" if diet_type.lower() != "non-vegetarian" else "Egg bhurji with whole-wheat roti"
    protein = "dal, paneer, curd, or soy" if diet_type.lower() != "non-vegetarian" else "dal plus eggs, chicken, or fish"
    budget_text = f"Aim to stay near Rs. {budget:.0f} per day." if budget else "Use seasonal produce and pantry staples to keep costs predictable."
    return "\n".join([
        f"## {goal} meal plan ({diet_type})",
        "This is general meal-planning guidance, not medical nutrition therapy.",
        "",
        f"- Breakfast: {breakfast} + one fruit.",
        f"- Lunch: Rice or 2 rotis, a bowl of dal, seasonal sabzi, salad, and {protein}.",
        "- Snack: Roasted chana or fruit with buttermilk/tea.",
        f"- Dinner: 2 rotis or millet, mixed vegetables, and a protein serving from {protein}.",
        f"- {budget_text}",
        f"- Plan {meals} eating occasions; adjust portions to hunger, activity, and professional advice.",
        *( [f"- Your note: {note}"] if note else []),
    ])


EXERCISES: dict[str, list[tuple[str, str]]] = {
    "Home": [
        ("Bodyweight squat", "Keep knees tracking over toes; use a chair for support if needed."),
        ("Incline push-up", "Use a stable elevated surface and keep your body in one line."),
        ("Glute bridge", "Pause briefly at the top without arching your lower back."),
        ("Reverse lunge", "Hold a wall or chair for balance as needed."),
        ("Dead bug", "Move slowly and keep the lower back gently braced."),
        ("March in place", "Keep the pace conversational, not breathless."),
    ],
    "Gym": [
        ("Goblet squat", "Choose a controlled load you can move with stable form."),
        ("Seated row", "Pull elbows back without shrugging your shoulders."),
        ("Machine chest press", "Use a pain-free range and keep wrists neutral."),
        ("Romanian deadlift", "Hinge at the hips; stop if you feel sharp back pain."),
        ("Lat pulldown", "Pull toward the upper chest and avoid swinging."),
        ("Incline walk", "Use a pace that lets you speak in short sentences."),
    ],
}


def make_workout(location: str, level: str, duration: int, rest: int, weight_kg: float) -> list[dict[str, Any]]:
    # Try AI generation first
    ai_workout = generate_ai_workout(goal="General Fitness", level=level, location=location, duration=duration, rest=rest, weight_kg=weight_kg)
    if ai_workout:
        return ai_workout

    count = 4 if level == "Beginner" else 5 if level == "Intermediate" else 6
    seconds = max(35, min(75, int((duration * 60 - rest * count) / count)))
    intensity = {"Beginner": "2 rounds", "Intermediate": "3 rounds", "Advanced": "3-4 rounds"}[level]
    exercises = []
    for name, cue in EXERCISES[location][:count]:
        calories = round(5.5 * weight_kg * (seconds / 3600), 1)
        exercises.append({
            "name": name, "seconds": seconds, "rest_seconds": rest,
            "estimated_calories": calories, "sets": intensity, "form_cue": cue,
            "video_search": f"https://www.youtube.com/results?search_query={name.replace(' ', '+')}+proper+form",
        })
    return exercises


def wellness_chat_reply(message: str, profile: dict[str, Any] | None = None, recent_history: list[dict[str, Any]] | None = None) -> str:
    lower = message.lower()
    if any(term in lower for term in ("chest pain", "can\'t breathe", "suicide", "self harm", "fainting", "severe")):
        return "I can’t assess an emergency. Please seek urgent local medical help now, or contact a trusted person nearby."
    
    # Try AI generation first
    ai_reply = generate_wellness_chat_reply(message, profile, recent_history or [])
    if ai_reply:
        return ai_reply

    goal = (profile or {}).get("goal") or "your routine"
    return (
        f"For {goal}, start with one small, repeatable action today: a balanced meal, a short walk, or a planned workout. "
        "I can give general wellness information, but I can’t diagnose conditions or replace a qualified clinician. "
        "What is the specific goal or habit you want to work on?"
    )
