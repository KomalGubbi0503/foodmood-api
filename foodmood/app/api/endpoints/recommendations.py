from fastapi import APIRouter
from app.models.schemas import RecommendationRequest, RecommendationResponse, GoalType, DietType

router = APIRouter()

# Rule-based meal recommendations per goal + diet combination
MEAL_LIBRARY: dict[tuple, list[str]] = {
    (GoalType.lose, DietType.low_carb): [
        "Grilled chicken salad with olive oil dressing",
        "Baked salmon with steamed broccoli",
        "Egg omelette with spinach and feta",
    ],
    (GoalType.lose, DietType.balanced): [
        "Grilled chicken with quinoa and roasted vegetables",
        "Greek yogurt with berries and a handful of almonds",
        "Lentil soup with a small whole-grain roll",
    ],
    (GoalType.lose, DietType.high_protein): [
        "Tuna and cottage cheese lettuce wraps",
        "Protein smoothie with whey, spinach, and banana",
        "Chicken breast with steamed broccoli",
    ],
    (GoalType.gain, DietType.balanced): [
        "Chicken and brown rice bowl with avocado",
        "Peanut butter oats with banana and milk",
        "Beef stir-fry with noodles and mixed vegetables",
    ],
    (GoalType.gain, DietType.high_protein): [
        "Steak with sweet potato and Greek yogurt",
        "Salmon with quinoa and a side of cottage cheese",
        "Egg white omelette with oats and nut butter",
    ],
    (GoalType.maintain, DietType.balanced): [
        "Mediterranean grain bowl with chickpeas and feta",
        "Whole-grain toast with avocado and poached egg",
        "Stir-fried tofu with brown rice and vegetables",
    ],
    (GoalType.maintain, DietType.vegetarian): [
        "Lentil dahl with basmati rice",
        "Chickpea and spinach curry",
        "Quinoa salad with roasted bell peppers and halloumi",
    ],
    (GoalType.maintain, DietType.vegan): [
        "Tofu scramble with sautéed vegetables and toast",
        "Black bean tacos with salsa and guacamole",
        "Smoothie bowl with blueberries, oats, and almond butter",
    ],
}

TIPS_LIBRARY: dict[GoalType, list[str]] = {
    GoalType.lose: [
        "Eat slowly — it takes ~20 minutes for satiety signals to reach the brain.",
        "Prioritise protein at every meal to reduce hunger and preserve muscle.",
        "Drink a glass of water before meals to reduce total intake.",
    ],
    GoalType.gain: [
        "Aim for a calorie surplus of 250–500 kcal/day for lean muscle gain.",
        "Eat within 30 minutes post-workout to maximise protein synthesis.",
        "Don't skip carbohydrates — they fuel your workouts and spare protein.",
    ],
    GoalType.maintain: [
        "Track meals occasionally to stay aware without obsessing.",
        "Vary your protein sources to get a full amino acid profile.",
        "Include colourful vegetables at each meal for micronutrient variety.",
    ],
}


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    summary="Get meal recommendations based on user goal and diet type",
)
async def get_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    key = (request.goal, request.diet_type)
    # Fallback to balanced if specific combination not found
    meals = MEAL_LIBRARY.get(key) or MEAL_LIBRARY.get((request.goal, DietType.balanced), [
        "Consult a nutritionist for a personalised meal plan."
    ])

    tips = TIPS_LIBRARY.get(request.goal, [])

    return RecommendationResponse(
        goal=request.goal,
        diet_type=request.diet_type,
        recommended_meals=meals[:3],
        tips=tips[:3],
    )
