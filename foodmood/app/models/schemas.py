from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum


# ── Enums ──────────────────────────────────────────────────────────────────

class GoalType(str, Enum):
    lose = "lose"
    maintain = "maintain"
    gain = "gain"


class DietType(str, Enum):
    balanced = "balanced"
    low_carb = "low-carb"
    high_protein = "high-protein"
    vegetarian = "vegetarian"
    vegan = "vegan"
    keto = "keto"


# ── Sub-models ─────────────────────────────────────────────────────────────

class FoodItem(BaseModel):
    name: str = Field(..., description="Recognised food item name")
    quantity: str = Field(..., description="Amount as described, e.g. '2 units', '150g'")
    calories: float = Field(..., ge=0, description="Estimated kcal for this item")
    protein_g: float = Field(..., ge=0)
    carbs_g: float = Field(..., ge=0)
    fat_g: float = Field(..., ge=0)


class Macros(BaseModel):
    calories: float = Field(..., ge=0, description="Total kcal")
    protein_g: float = Field(..., ge=0)
    carbs_g: float = Field(..., ge=0)
    fat_g: float = Field(..., ge=0)


class UserProfile(BaseModel):
    goal: GoalType = Field(..., description="User's nutritional goal")
    diet_type: DietType = Field(DietType.balanced, description="Preferred diet style")
    # Optional personalisation extras
    daily_calorie_target: Optional[int] = Field(None, ge=500, le=6000)
    name: Optional[str] = None


# ── Request models ─────────────────────────────────────────────────────────

class MealParseRequest(BaseModel):
    meal_description: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Free-text description of the meal",
        examples=["2 eggs, 1 slice whole wheat bread, avocado"],
    )
    user_profile: Optional[UserProfile] = Field(
        None,
        description="If provided, personalised feedback is included in the response",
    )
    mock: bool = Field(
        False,
        description="Force mock mode for this request (dev/testing without using AI credits)",
    )


class RecommendationRequest(BaseModel):
    goal: GoalType
    diet_type: DietType = DietType.balanced
    current_macros: Optional[Macros] = None
    meal_context: Optional[str] = Field(None, description="Optional meal description for context")


# ── Response models ────────────────────────────────────────────────────────

class PersonalisedFeedback(BaseModel):
    adjusted_feedback: str
    suggestions: list[str] = Field(..., min_length=1, max_length=2)
    goal_alignment: Literal["good", "moderate", "poor"]


class MealParseResponse(BaseModel):
    meal_description: str
    food_items: list[FoodItem]
    total_macros: Macros
    ai_feedback: str
    personalised: Optional[PersonalisedFeedback] = None
    cache_hit: bool = Field(False, description="True if this response was served from cache")
    mock: bool = Field(False, description="True if AI call was mocked")


class RecommendationResponse(BaseModel):
    goal: GoalType
    diet_type: DietType
    recommended_meals: list[str]
    tips: list[str]


class HealthResponse(BaseModel):
    status: str
    version: str
    mock_mode: bool
    model: str
