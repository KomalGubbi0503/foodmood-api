
#Rule-based personalisation engine.

from app.models.schemas import Macros, UserProfile, PersonalisedFeedback, GoalType, DietType
from typing import Literal


def generate_personalised_feedback(
    macros: Macros, profile: UserProfile
) -> PersonalisedFeedback:
    suggestions: list[str] = []
    feedback_parts: list[str] = []

    total_cal = macros.calories or 1  # guard div-by-zero
    protein_pct = (macros.protein_g * 4) / total_cal * 100
    carb_pct = (macros.carbs_g * 4) / total_cal * 100
    fat_pct = (macros.fat_g * 9) / total_cal * 100

    # Goal-based feedback
    if profile.goal == GoalType.lose:
        if total_cal > 600:
            feedback_parts.append(
                f"At {total_cal:.0f} kcal this meal is on the higher side for a weight-loss goal."
            )
            suggestions.append("Consider reducing portion size or swapping to a lower-calorie protein source.")
        else:
            feedback_parts.append(
                f"Good calorie control at {total_cal:.0f} kcal — well suited for your weight-loss goal."
            )
        if protein_pct < 25:
            suggestions.append("Increase protein (e.g., add an extra egg or some Greek yogurt) to preserve muscle while in a deficit.")

    elif profile.goal == GoalType.gain:
        if total_cal < 500:
            feedback_parts.append(
                f"At {total_cal:.0f} kcal this meal may not support your muscle-gain goal."
            )
            suggestions.append("Add a calorie-dense food like nuts, nut butter, or an extra portion of complex carbs.")
        else:
            feedback_parts.append(
                f"Solid {total_cal:.0f} kcal meal that supports your muscle-gain goal."
            )
        if protein_pct < 30:
            suggestions.append("Aim for at least 30 g of protein per meal to maximise muscle protein synthesis.")

    else:  # maintain
        feedback_parts.append(
            f"This {total_cal:.0f} kcal meal fits a balanced maintenance approach."
        )

    # Diet-type feedback
    if profile.diet_type == DietType.low_carb:
        if carb_pct > 30:
            feedback_parts.append(
                f"Carbs are {carb_pct:.0f}% of calories — higher than typical for low-carb."
            )
            suggestions.append("Replace bread or starchy items with leafy greens or cauliflower to lower carbs.")
        else:
            feedback_parts.append("Carbohydrate ratio aligns with your low-carb preference.")

    elif profile.diet_type == DietType.high_protein:
        if protein_pct < 30:
            feedback_parts.append(
                f"Protein is only {protein_pct:.0f}% of calories — below high-protein target."
            )
            suggestions.append("Add a protein-rich food (chicken breast, tuna, or cottage cheese) to boost protein ratio.")
        else:
            feedback_parts.append(f"Great protein ratio at {protein_pct:.0f}% of total calories.")

    elif profile.diet_type == DietType.keto:
        if carb_pct > 10:
            feedback_parts.append(
                f"Carbs at {carb_pct:.0f}% of calories may break ketosis (target <10%)."
            )
            suggestions.append("Remove bread and replace with avocado or extra eggs to stay in ketosis.")

    elif profile.diet_type == DietType.vegan:
        feedback_parts.append("Ensure you're meeting B12 and iron needs through fortified foods or supplementation.")

    # Daily target check 
    if profile.daily_calorie_target:
        proportion = total_cal / profile.daily_calorie_target * 100
        feedback_parts.append(
            f"This meal accounts for {proportion:.0f}% of your {profile.daily_calorie_target} kcal daily target."
        )

    #  Goal alignment score
    alignment = _score_alignment(macros, profile, protein_pct, carb_pct)

    # Deduplicate suggestions and cap at 2
    unique_suggestions = list(dict.fromkeys(suggestions))[:2]
    if not unique_suggestions:
        unique_suggestions = ["Keep it up — this meal fits your nutritional profile well."]

    return PersonalisedFeedback(
        adjusted_feedback=" ".join(feedback_parts),
        suggestions=unique_suggestions,
        goal_alignment=alignment,
    )


def _score_alignment(
    macros: Macros, profile: UserProfile, protein_pct: float, carb_pct: float
) -> Literal["good", "moderate", "poor"]:
    score = 0

    if profile.goal == GoalType.lose:
        if macros.calories <= 500: score += 2
        elif macros.calories <= 700: score += 1
        if protein_pct >= 25: score += 1

    elif profile.goal == GoalType.gain:
        if macros.calories >= 600: score += 2
        elif macros.calories >= 400: score += 1
        if protein_pct >= 25: score += 1

    else:
        score = 2  # maintenance is flexible

    if profile.diet_type == DietType.low_carb and carb_pct <= 30: score += 1
    if profile.diet_type == DietType.high_protein and protein_pct >= 30: score += 1
    if profile.diet_type == DietType.keto and carb_pct <= 10: score += 1

    if score >= 3: return "good"
    if score >= 1: return "moderate"
    return "poor"
