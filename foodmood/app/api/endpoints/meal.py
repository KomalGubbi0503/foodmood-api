from fastapi import APIRouter, HTTPException
from app.models.schemas import MealParseRequest, MealParseResponse
from app.services.meal_service import process_meal

router = APIRouter()


@router.post(
    "/parse-meal",
    response_model=MealParseResponse,
    summary="Parse a free-text meal description",
    description=(
        "Accepts a natural-language meal description and returns structured food items, "
        "calorie and macro estimates, AI-generated feedback, and optional personalised "
        "suggestions based on the user's goal and diet type."
    ),
)
async def parse_meal(request: MealParseRequest) -> MealParseResponse:
    if not request.meal_description.strip():
        raise HTTPException(status_code=422, detail="meal_description cannot be empty.")
    try:
        return await process_meal(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        # Surface LLM/network errors clearly without leaking internals
        raise HTTPException(
            status_code=502,
            detail=f"AI service error: {str(exc)}. Try enabling mock=true for testing.",
        )
