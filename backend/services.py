"""Deterministic, explainable wellness helpers used when an AI provider is absent.

Health.io deliberately treats generated material as general wellness guidance,
not a diagnosis.  The deterministic paths make demos dependable and transparent.
"""

from __future__ import annotations

from typing import Any

from backend.ai_services import generate_wellness_chat_reply, generate_ai_meal_plan, generate_ai_workout


def bmi_result(weight_kg: float, height_cm: float) -> dict[str, Any]:
    bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)
    if bmi < 16:
        category, guidance = "Well below recommended range", "This BMI is significantly low. If this number seems unexpected, double-check your height and weight inputs for typos. Otherwise, please speak with a clinician."
    elif bmi < 18.5:
        category, guidance = "Below recommended range", "Focus on regular, nourishing meals and discuss persistent weight changes with a clinician."
    elif bmi < 25:
        category, guidance = "Within the usual range", "Keep supporting your routine with balanced meals, movement, sleep, and check-ins."
    elif bmi < 30:
        category, guidance = "Above recommended range", "Small, sustainable nutrition and activity habits are more useful than quick fixes."
    else:
        category, guidance = "Higher range", "Consider speaking with a qualified clinician for advice tailored to your health history."
    return {"bmi": bmi, "category": category, "guidance": guidance, "weight_kg": weight_kg, "height_cm": height_cm}


def make_meal_plan(goal: str, diet_type: str, budget: float | None, meals: int, note: str | None, profile: dict[str, Any] | None = None) -> str:
    return generate_ai_meal_plan(goal, diet_type, budget, meals, note, profile)


def make_workout(location: str, level: str, duration: int, rest: int, weight_kg: float, goal: str = "Fitness") -> list[dict[str, Any]]:
    return generate_ai_workout(goal=goal, level=level, location=location, duration=duration, rest=rest, weight_kg=weight_kg)


def wellness_chat_reply(message: str, profile: dict[str, Any] | None = None, recent_history: list[dict[str, Any]] | None = None) -> str:
    lower = message.lower()
    if any(term in lower for term in ("chest pain", "can't breathe", "suicide", "self harm", "fainting", "severe")):
        return "I can’t assess an emergency. Please seek urgent local medical help now, or contact a trusted person nearby."
    return generate_wellness_chat_reply(message, profile, recent_history or [])
