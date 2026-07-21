"""Request models used to validate every value entering the API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    display_name: str = Field(min_length=2, max_length=60)
    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=1, max_length=128)


class ProfileRequest(BaseModel):
    age: int | None = Field(default=None, ge=13, le=120)
    gender: str | None = Field(default=None, max_length=40)
    height_cm: float | None = Field(default=None, ge=80, le=250)
    weight_kg: float | None = Field(default=None, ge=20, le=400)
    goal: str | None = Field(default=None, max_length=80)
    activity_level: str | None = Field(default=None, max_length=80)
    diet_preference: str | None = Field(default=None, max_length=80)
    bio: str | None = Field(default=None, max_length=500)


class BMIRequest(BaseModel):
    weight_kg: float = Field(ge=20, le=400)
    height_cm: float = Field(ge=80, le=250)


class FoodLogRequest(BaseModel):
    food_name: str = Field(min_length=2, max_length=120)
    calories: int = Field(ge=0, le=10_000)
    protein_g: float = Field(ge=0, le=1_000)
    carbs_g: float = Field(ge=0, le=1_000)
    fat_g: float = Field(ge=0, le=1_000)
    note: str | None = Field(default=None, max_length=600)


class SkinLogRequest(BaseModel):
    summary: str = Field(min_length=2, max_length=4_000)
    concerns: list[str] = Field(default_factory=list, max_length=8)


class MealPlanRequest(BaseModel):
    goal: str = Field(min_length=2, max_length=80)
    diet_type: str = Field(min_length=2, max_length=80)
    budget: float | None = Field(default=None, ge=0, le=100_000)
    meals_per_day: int = Field(ge=2, le=6)
    extra_instructions: str | None = Field(default=None, max_length=600)


class WorkoutRequest(BaseModel):
    goal: Literal["Fat Loss", "Muscle Gain", "Fitness"]
    level: Literal["Beginner", "Intermediate", "Advanced"]
    location: Literal["Home", "Gym"]
    duration_minutes: int = Field(ge=15, le=120)
    rest_seconds: int = Field(ge=10, le=120)
    weight_kg: float = Field(ge=20, le=400)


class WorkoutCompleteRequest(BaseModel):
    total_calories: float = Field(ge=0, le=5_000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1_500)

    @field_validator("message")
    @classmethod
    def normalise_message(cls, value: str) -> str:
        return " ".join(value.split())


class CheckinRequest(BaseModel):
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    steps: int | None = Field(default=None, ge=0, le=100_000)
    water_glasses: int | None = Field(default=None, ge=0, le=30)
    mood: int | None = Field(default=None, ge=1, le=5)
    energy: int | None = Field(default=None, ge=1, le=5)
    soreness: int | None = Field(default=None, ge=1, le=5)
    note: str | None = Field(default=None, max_length=500)


class FoodAnalysisRequest(BaseModel):
    image: str | None = Field(default=None, description="Base64 encoded image string, optionally prefixed with data URI scheme")
    text: str | None = Field(default=None, min_length=2, max_length=1500, description="Text description of the food eaten")

    @field_validator('text')
    @classmethod
    def check_at_least_one(cls, v, info):
        image = info.data.get('image')
        if not v and not image:
            raise ValueError("You must provide either an image or a text description.")
        if v and image:
            raise ValueError("You cannot provide both an image and a text description.")
        return v

class ImageUploadRequest(BaseModel):
    image: str = Field(description="Base64 encoded image string, optionally prefixed with data URI scheme")
