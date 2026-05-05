
#Meal parsing orchestration service.




from app.core.config import get_settings
from app.models.schemas import FoodItem, Macros, MealParseResponse, MealParseRequest
from app.services.llm_service import parse_meal_with_llm, parse_meal_mock
from app.utils.cache import get_cached, set_cached

settings = get_settings()


async def process_meal(request: MealParseRequest) -> MealParseResponse:
    use_mock = request.mock or settings.mock_mode

    # Cache lookup
    cache_key = request.meal_description
    cached = get_cached(cache_key)
    if cached and not use_mock:
        # Rebuild response from cached dict
        resp = MealParseResponse(**cached)
        resp.cache_hit = True
        return resp

    # AI call (or mock)
    if use_mock:
        raw = await parse_meal_mock(request.meal_description)
    else:
        raw = await parse_meal_with_llm(request.meal_description)

    #Build FoodItem list
    food_items: list[FoodItem] = []
    for item in raw.get("food_items", []):
        food_items.append(
            FoodItem(
                name=item["name"],
                quantity=item.get("quantity", "1 serving"),
                calories=float(item.get("calories", 0)),
                protein_g=float(item.get("protein_g", 0)),
                carbs_g=float(item.get("carbs_g", 0)),
                fat_g=float(item.get("fat_g", 0)),
            )
        )

    #  Aggregate totals
    total_macros = Macros(
        calories=round(sum(f.calories for f in food_items), 1),
        protein_g=round(sum(f.protein_g for f in food_items), 1),
        carbs_g=round(sum(f.carbs_g for f in food_items), 1),
        fat_g=round(sum(f.fat_g for f in food_items), 1),
    )

    # Build response
    response = MealParseResponse(
        meal_description=request.meal_description,
        food_items=food_items,
        total_macros=total_macros,
        ai_feedback=raw.get("ai_feedback", ""),
        cache_hit=False,
        mock=use_mock,
    )

    # Personalisation
    if request.user_profile:
        from app.services.personalisation_service import generate_personalised_feedback
        response.personalised = generate_personalised_feedback(
            total_macros, request.user_profile
        )

    # Cache (only real AI results)
    if not use_mock:
        set_cached(cache_key, response.model_dump())

    return response
