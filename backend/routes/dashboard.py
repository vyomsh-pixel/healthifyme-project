from fastapi import APIRouter

from utils.history_utils import load_history
from utils.meal_utils import load_meal_history

router = APIRouter()


def calculate_health_score(bmi_records, food_records, skin_records, meal_history):
    """Same scoring logic as the original Streamlit dashboard."""
    score = 0

    latest_bmi = bmi_records[-1] if bmi_records else None
    if latest_bmi:
        bmi_value = latest_bmi.get("bmi", 0)
        try:
            bmi_value = float(bmi_value)
            if 18.5 <= bmi_value <= 24.9:
                score += 40
            else:
                score += 20
        except (TypeError, ValueError):
            score += 20

    score += min(len(food_records) * 5, 30)
    score += min(len(skin_records) * 5, 30)
    score = min(score, 100)

    adjusted_score = score + (len(meal_history) * 5)

    return score, adjusted_score


@router.get("")
def get_dashboard():
    history = load_history()
    meal_history = load_meal_history()

    bmi_records = [item for item in history if item.get("type") == "BMI"]
    food_records = [item for item in history if item.get("type") == "Food Scan"]
    skin_records = [item for item in history if item.get("type") == "Skin Scan"]

    latest_bmi = bmi_records[-1] if bmi_records else None
    latest_food = food_records[-1] if food_records else None
    latest_skin = skin_records[-1] if skin_records else None
    latest_meal = meal_history[-1] if meal_history else None

    health_score, adjusted_score = calculate_health_score(
        bmi_records, food_records, skin_records, meal_history
    )

    recent_activity = list(reversed(history[-5:])) if history else []

    return {
        "has_data": len(history) > 0,
        "counts": {
            "bmi_records": len(bmi_records),
            "food_scans": len(food_records),
            "skin_scans": len(skin_records),
            "meal_plans": len(meal_history),
        },
        "health_score": health_score,
        "adjusted_score": adjusted_score,
        "latest_bmi": latest_bmi,
        "latest_food": latest_food,
        "latest_skin": latest_skin,
        "latest_meal": latest_meal,
        "recent_activity": recent_activity,
    }