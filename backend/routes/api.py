from __future__ import annotations

import json
import sqlite3
from datetime import UTC, date, datetime
from typing import Any, Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status

from backend.database import database
from backend.schemas import (
    BMIRequest, ChatRequest, CheckinRequest, FoodLogRequest, LoginRequest,
    MealPlanRequest, ProfileRequest, RegisterRequest, SkinLogRequest,
    WorkoutCompleteRequest, WorkoutRequest, ImageUploadRequest
)
from backend.security import hash_password, new_session_token, session_expiry, token_hash, verify_password
from backend.services import bmi_result, make_meal_plan, make_workout, wellness_chat_reply
from backend.ai_services import analyze_food_image, analyze_skin_image



router = APIRouter(prefix="/api", tags=["healthio"])
User = dict[str, Any]


def row_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


def require_user(authorization: Annotated[str | None, Header()] = None) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in is required.")
    with database() as connection:
        row = connection.execute(
            """
            SELECT users.id, users.username, users.display_name
            FROM sessions JOIN users ON users.id = sessions.user_id
            WHERE sessions.token_hash = ? AND sessions.expires_at > ?
            """,
            (token_hash(authorization.removeprefix("Bearer ")), datetime.now(UTC).isoformat()),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your session has expired. Please sign in again.")
    return dict(row)


CurrentUser = Annotated[User, Depends(require_user)]


def get_profile(connection: sqlite3.Connection, user_id: int) -> dict[str, Any]:
    row = connection.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    return row_dict(row) or {}


def get_records(connection: sqlite3.Connection, user_id: int, record_type: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    query = "SELECT id, record_type, payload, created_at FROM health_records WHERE user_id = ?"
    values: list[Any] = [user_id]
    if record_type:
        query += " AND record_type = ?"
        values.append(record_type)
    query += " ORDER BY created_at DESC LIMIT ?"
    values.append(limit)
    records = []
    for row in connection.execute(query, values).fetchall():
        records.append({"id": row["id"], "type": row["record_type"], "created_at": row["created_at"], **json.loads(row["payload"])})
    return records


def add_record(connection: sqlite3.Connection, user_id: int, record_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    cursor = connection.execute(
        "INSERT INTO health_records (user_id, record_type, payload) VALUES (?, ?, ?)",
        (user_id, record_type, json.dumps(payload)),
    )
    row = connection.execute("SELECT created_at FROM health_records WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return {"id": cursor.lastrowid, "type": record_type, "created_at": row["created_at"], **payload}


def session_response(connection: sqlite3.Connection, user: User) -> dict[str, Any]:
    token = new_session_token()
    connection.execute(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
        (token_hash(token), user["id"], session_expiry()),
    )
    return {"token": token, "user": {"id": user["id"], "username": user["username"], "display_name": user["display_name"]}}


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest) -> dict[str, Any]:
    with database() as connection:
        try:
            cursor = connection.execute(
                "INSERT INTO users (username, display_name, password_hash) VALUES (?, ?, ?)",
                (payload.username.strip(), payload.display_name.strip(), hash_password(payload.password)),
            )
        except sqlite3.IntegrityError as error:
            raise HTTPException(status_code=409, detail="That username is already in use.") from error
        return session_response(connection, {"id": cursor.lastrowid, "username": payload.username.strip(), "display_name": payload.display_name.strip()})


@router.post("/auth/login")
def login(payload: LoginRequest) -> dict[str, Any]:
    with database() as connection:
        row = connection.execute("SELECT * FROM users WHERE username = ?", (payload.username.strip(),)).fetchone()
        if not row or not verify_password(payload.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect username or password.")
        return session_response(connection, dict(row))


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: CurrentUser, authorization: Annotated[str | None, Header()] = None) -> Response:
    with database() as connection:
        connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash((authorization or "").removeprefix("Bearer ")),))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me")
def me(current_user: CurrentUser) -> dict[str, Any]:
    with database() as connection:
        return {"user": current_user, "profile": get_profile(connection, current_user["id"])}


@router.put("/profile")
def update_profile(payload: ProfileRequest, current_user: CurrentUser) -> dict[str, Any]:
    values = payload.model_dump()
    with database() as connection:
        connection.execute(
            """
            INSERT INTO profiles (user_id, age, gender, height_cm, weight_kg, goal, activity_level, diet_preference, bio, updated_at)
            VALUES (:user_id, :age, :gender, :height_cm, :weight_kg, :goal, :activity_level, :diet_preference, :bio, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
              age=excluded.age, gender=excluded.gender, height_cm=excluded.height_cm, weight_kg=excluded.weight_kg,
              goal=excluded.goal, activity_level=excluded.activity_level, diet_preference=excluded.diet_preference,
              bio=excluded.bio, updated_at=CURRENT_TIMESTAMP
            """,
            {"user_id": current_user["id"], **values},
        )
        return {"profile": get_profile(connection, current_user["id"])}


@router.get("/dashboard")
def dashboard(current_user: CurrentUser) -> dict[str, Any]:
    with database() as connection:
        records = get_records(connection, current_user["id"], limit=200)
        by_type = {kind: [record for record in records if record["type"] == kind] for kind in ("BMI", "FOOD", "SKIN")}
        meals = [dict(row) for row in connection.execute("SELECT * FROM meal_plans WHERE user_id = ? ORDER BY created_at DESC", (current_user["id"],)).fetchall()]
        workouts = [dict(row) for row in connection.execute("SELECT * FROM workouts WHERE user_id = ? AND completed_at IS NOT NULL ORDER BY completed_at DESC", (current_user["id"],)).fetchall()]
        today_food = [record for record in by_type["FOOD"] if record["created_at"].startswith(date.today().isoformat())]
        calories = sum(record.get("calories", 0) for record in today_food)
        protein = sum(record.get("protein_g", 0) for record in today_food)
        latest_bmi = by_type["BMI"][0] if by_type["BMI"] else None
        score = 0
        if latest_bmi:
            score += 30 if 18.5 <= latest_bmi["bmi"] < 25 else 15
        score += min(25, len(workouts) * 5)
        score += min(20, len(today_food) * 5)
        score += 15 if get_profile(connection, current_user["id"]) else 0
        score += min(10, len(meals) * 2)
        activity = sorted(
            [{"type": record["type"], "created_at": record["created_at"], "id": record["id"]} for record in records]
            + [{"type": "MEAL_PLAN", "created_at": meal["created_at"], "id": meal["id"]} for meal in meals]
            + [{"type": "WORKOUT", "created_at": workout["completed_at"], "id": workout["id"]} for workout in workouts],
            key=lambda item: item["created_at"], reverse=True,
        )[:6]
        return {
            "user": current_user, "profile": get_profile(connection, current_user["id"]), "health_score": min(score, 100),
            "counts": {"bmi_records": len(by_type["BMI"]), "food_logs": len(by_type["FOOD"]), "skin_logs": len(by_type["SKIN"]), "meal_plans": len(meals), "completed_workouts": len(workouts)},
            "today_nutrition": {"calories": calories, "protein_g": protein, "calorie_goal": 2200, "protein_goal": 140},
            "latest": {"bmi": latest_bmi, "food": by_type["FOOD"][0] if by_type["FOOD"] else None, "skin": by_type["SKIN"][0] if by_type["SKIN"] else None, "meal": meals[0] if meals else None},
            "recent_activity": activity,
        }


@router.post("/records/bmi", status_code=status.HTTP_201_CREATED)
def create_bmi(payload: BMIRequest, current_user: CurrentUser) -> dict[str, Any]:
    with database() as connection:
        return {"record": add_record(connection, current_user["id"], "BMI", bmi_result(payload.weight_kg, payload.height_cm))}


@router.post("/records/food", status_code=status.HTTP_201_CREATED)
def create_food_log(payload: FoodLogRequest, current_user: CurrentUser) -> dict[str, Any]:
    with database() as connection:
        return {"record": add_record(connection, current_user["id"], "FOOD", payload.model_dump())}


@router.post("/records/skin", status_code=status.HTTP_201_CREATED)
def create_skin_log(payload: SkinLogRequest, current_user: CurrentUser) -> dict[str, Any]:
    with database() as connection:
        return {"record": add_record(connection, current_user["id"], "SKIN", payload.model_dump())}


@router.get("/records")
def records(current_user: CurrentUser, record_type: str | None = None) -> dict[str, Any]:
    with database() as connection:
        return {"records": get_records(connection, current_user["id"], record_type=record_type)}


@router.post("/meal-plans", status_code=status.HTTP_201_CREATED)
def create_meal_plan(payload: MealPlanRequest, current_user: CurrentUser) -> dict[str, Any]:
    with database() as connection:
        profile = get_profile(connection, current_user["id"])
        plan = make_meal_plan(payload.goal, payload.diet_type, payload.budget, payload.meals_per_day, payload.extra_instructions, profile)
        cursor = connection.execute(
            "INSERT INTO meal_plans (user_id, goal, diet_type, budget, meals_per_day, extra_instructions, plan_text) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (current_user["id"], payload.goal, payload.diet_type, payload.budget, payload.meals_per_day, payload.extra_instructions, plan),
        )
        return {"meal_plan": dict(connection.execute("SELECT * FROM meal_plans WHERE id = ?", (cursor.lastrowid,)).fetchone())}


@router.get("/meal-plans")
def meal_plans(current_user: CurrentUser) -> dict[str, Any]:
    with database() as connection:
        rows = connection.execute("SELECT * FROM meal_plans WHERE user_id = ? ORDER BY created_at DESC", (current_user["id"],)).fetchall()
        return {"meal_plans": [dict(row) for row in rows]}


@router.post("/workouts/generate")
def generate_workout(payload: WorkoutRequest, current_user: CurrentUser) -> dict[str, Any]:
    exercises = make_workout(payload.location, payload.level, payload.duration_minutes, payload.rest_seconds, payload.weight_kg)
    with database() as connection:
        cursor = connection.execute(
            "INSERT INTO workouts (user_id, goal, level, location, duration_minutes, exercises) VALUES (?, ?, ?, ?, ?, ?)",
            (current_user["id"], payload.goal, payload.level, payload.location, payload.duration_minutes, json.dumps(exercises)),
        )
        row = dict(connection.execute("SELECT * FROM workouts WHERE id = ?", (cursor.lastrowid,)).fetchone())
        row["exercises"] = exercises
        return {"workout": row, "safety_note": "Stop if you feel sharp pain, dizziness, chest pain, or unusual breathlessness. Seek professional guidance for injuries or medical conditions."}


@router.post("/workouts/{workout_id}/complete")
def complete_workout(workout_id: int, payload: WorkoutCompleteRequest, current_user: CurrentUser) -> dict[str, Any]:
    with database() as connection:
        cursor = connection.execute(
            "UPDATE workouts SET total_calories = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?",
            (payload.total_calories, workout_id, current_user["id"]),
        )
        if not cursor.rowcount:
            raise HTTPException(status_code=404, detail="Workout not found.")
        return {"workout": dict(connection.execute("SELECT * FROM workouts WHERE id = ?", (workout_id,)).fetchone())}


@router.get("/workouts")
def workouts(current_user: CurrentUser) -> dict[str, Any]:
    with database() as connection:
        rows = connection.execute("SELECT * FROM workouts WHERE user_id = ? ORDER BY created_at DESC", (current_user["id"],)).fetchall()
        return {"workouts": [{**dict(row), "exercises": json.loads(row["exercises"])} for row in rows]}


@router.delete("/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, current_user: CurrentUser) -> Response:
    with database() as connection:
        cursor = connection.execute("DELETE FROM workouts WHERE id = ? AND user_id = ?", (workout_id, current_user["id"]))
        if not cursor.rowcount:
            raise HTTPException(status_code=404, detail="Workout not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/chat")
def chat_history(current_user: CurrentUser) -> dict[str, Any]:
    with database() as connection:
        rows = connection.execute("SELECT id, role, content, created_at FROM chat_messages WHERE user_id = ? ORDER BY id ASC", (current_user["id"],)).fetchall()
        return {"messages": [dict(row) for row in rows]}


@router.post("/chat")
def chat(payload: ChatRequest, current_user: CurrentUser) -> dict[str, Any]:
    with database() as connection:
        connection.execute("INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'user', ?)", (current_user["id"], payload.message))
        profile = get_profile(connection, current_user["id"])
        recent_history = get_records(connection, current_user["id"], limit=5)
        response = wellness_chat_reply(payload.message, profile, recent_history)
        cursor = connection.execute("INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'assistant', ?)", (current_user["id"], response))
        row = connection.execute("SELECT id, role, content, created_at FROM chat_messages WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return {"message": dict(row)}


@router.delete("/chat", status_code=status.HTTP_204_NO_CONTENT)
def clear_chat(current_user: CurrentUser) -> Response:
    with database() as connection:
        connection.execute("DELETE FROM chat_messages WHERE user_id = ?", (current_user["id"],))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/checkins/today")
def save_checkin(payload: CheckinRequest, current_user: CurrentUser) -> dict[str, Any]:
    with database() as connection:
        connection.execute(
            """
            INSERT INTO daily_checkins (user_id, checkin_date, sleep_hours, steps, water_glasses, mood, energy, soreness, note)
            VALUES (:user_id, :checkin_date, :sleep_hours, :steps, :water_glasses, :mood, :energy, :soreness, :note)
            ON CONFLICT(user_id, checkin_date) DO UPDATE SET sleep_hours=excluded.sleep_hours, steps=excluded.steps,
              water_glasses=excluded.water_glasses, mood=excluded.mood, energy=excluded.energy, soreness=excluded.soreness, note=excluded.note
            """,
            {"user_id": current_user["id"], "checkin_date": date.today().isoformat(), **payload.model_dump()},
        )
        row = connection.execute("SELECT * FROM daily_checkins WHERE user_id = ? AND checkin_date = ?", (current_user["id"], date.today().isoformat())).fetchone()
        return {"checkin": dict(row)}


@router.post("/analyze-food")
def analyze_food(payload: ImageUploadRequest, current_user: CurrentUser) -> dict[str, Any]:
    result = analyze_food_image(payload.image)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to analyze image with AI.")
    return result


@router.post("/analyze-skin")
def analyze_skin(payload: ImageUploadRequest, current_user: CurrentUser) -> dict[str, Any]:
    result = analyze_skin_image(payload.image)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to analyze image with AI.")
    return result
