import json
import pytest
from backend import ai_services
from backend.ai_services import MealPlanResult


def test_food_text_offline_heuristic_fallback(monkeypatch):
    # Ensure Gemini client returns None to simulate offline / unavailable state
    monkeypatch.setattr(ai_services, "_get_client", lambda: None)

    res = ai_services.analyze_food_text("2 roti with 1 katori dal and salad")
    assert res is not None
    assert res["is_offline_estimate"] is True
    assert res["source"] == "offline_estimate"
    assert res["calories"] > 0
    assert res["protein_g"] > 0
    assert "food_name" in res


def test_skin_image_offline_strict_no_fabrication(monkeypatch):
    monkeypatch.setattr(ai_services, "_get_client", lambda: None)

    res = ai_services.analyze_skin_image("dummy_base64_data")
    assert res is not None
    assert res["status"] == "unavailable"
    assert res["is_offline_fallback"] is True
    # Crucial medical safety requirement: never fabricate dermatological concerns
    assert res["concerns"] == []
    assert "unavailable" in res["summary"].lower()


def test_meal_plan_offline_fallback_schema_valid(monkeypatch):
    monkeypatch.setattr(ai_services, "_get_client", lambda: None)

    plan_json = ai_services.generate_ai_meal_plan("Fitness", "Vegetarian", 250, 4, None, None)
    assert plan_json is not None
    # Validate it parses according to Pydantic schema
    validated = MealPlanResult.model_validate_json(plan_json)
    assert validated.daily_total_calories > 0
    assert len(validated.meals) >= 3


def test_workout_offline_fallback(monkeypatch):
    monkeypatch.setattr(ai_services, "_get_client", lambda: None)

    exercises = ai_services.generate_ai_workout("Fitness", "Beginner", "Home", 30, 30, 70.0)
    assert exercises is not None
    assert len(exercises) >= 3
    for ex in exercises:
        assert "name" in ex
        assert "seconds" in ex
        assert "estimated_calories" in ex
