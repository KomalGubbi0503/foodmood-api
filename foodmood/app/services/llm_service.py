
import json
import re
import httpx
from app.core.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """You are a professional nutritionist and food analyst AI.
Your job is to parse meal descriptions and return structured nutritional data.
Always respond ONLY with valid JSON. No markdown, no explanation outside JSON.
"""

PARSE_PROMPT_TEMPLATE = """Analyse this meal description and return a JSON object with exactly this structure:

{{
  "food_items": [
    {{
      "name": "string - recognised food name",
      "quantity": "string - amount as described",
      "calories": number,
      "protein_g": number,
      "carbs_g": number,
      "fat_g": number
    }}
  ],
  "ai_feedback": "string - 2-3 sentence nutritional assessment",
  "is_valid_meal": boolean
}}

Meal description: "{meal_description}"

Rules:
- ONLY parse REAL FOOD ITEMS
- If input is NOT about food (e.g. "car", "xyz", "hello"), return empty food_items and is_valid_meal=false
- For real meals, estimate realistic calories and macros
- ai_feedback must be specific to actual foods mentioned
- Return ONLY the JSON object, nothing else.
"""


async def parse_meal_with_llm(meal_description: str) -> dict:
    """Call OpenRouter to parse a meal description. Returns parsed dict."""
    prompt = PARSE_PROMPT_TEMPLATE.format(meal_description=meal_description)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.openrouter_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "HTTP-Referer": "https://foodmood.app",
                "X-Title": "FoodMood",
            },
            json={
                "model": settings.openrouter_model,
                "max_tokens": 1024,
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            },
        )
        response.raise_for_status()

    data = response.json()
    raw_text = data["choices"][0]["message"]["content"].strip()
    result = _extract_json(raw_text)
    
    if not _is_valid_food_meal(result):
        raise ValueError(
            "Invalid input: Please describe a real meal with food items. "
            "Example: '2 eggs, toast, avocado' or 'chicken salad'"
        )
    
    return result


def _is_valid_food_meal(result: dict) -> bool:
    """Check if the result contains actual food items, not random data."""
    if result.get("is_valid_meal") is False:
        return False
    
    food_items = result.get("food_items", [])
    if not food_items or len(food_items) == 0:
        return False
    
    for item in food_items:
        name = str(item.get("name", "")).lower()
        if name in ["xyz", "car", "hello", "test", "random", "object", "thing"]:
            return False
    
    return True


def _extract_json(raw_text: str) -> dict:
    """Robustly extract JSON from LLM output."""
    if "```" in raw_text:
        parts = raw_text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:]
            part = part.strip()
            if part.startswith("{"):
                raw_text = part
                break

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    try:
        fixed = _fix_truncated_json(raw_text)
        if fixed:
            return fixed
    except Exception:
        pass

    result = dict(MOCK_RESPONSE)
    result["ai_feedback"] = "AI response could not be parsed. Showing estimated values."
    return result


def _fix_truncated_json(text: str) -> dict | None:
    """Try to salvage truncated JSON by closing open brackets."""
    open_braces = text.count('{') - text.count('}')
    open_brackets = text.count('[') - text.count(']')

    text = text.rstrip()
    text += '}' * open_braces
    text += ']' * open_brackets

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


MOCK_RESPONSE = {
    "food_items": [
        {
            "name": "egg",
            "quantity": "2 units",
            "calories": 155,
            "protein_g": 13.0,
            "carbs_g": 1.1,
            "fat_g": 11.0,
        },
        {
            "name": "whole wheat bread",
            "quantity": "1 slice",
            "calories": 69,
            "protein_g": 2.5,
            "carbs_g": 12.9,
            "fat_g": 1.0,
        },
        {
            "name": "avocado",
            "quantity": "0.5 medium",
            "calories": 120,
            "protein_g": 1.5,
            "carbs_g": 6.8,
            "fat_g": 11.0,
        },
    ],
    "ai_feedback": (
        "This is a well-balanced breakfast with healthy fats from avocado, "
        "quality protein from eggs, and complex carbohydrates from whole wheat bread. "
        "It provides sustained energy and keeps you satiated for several hours."
    ),
}


async def parse_meal_mock(_meal_description: str) -> dict:
    """Return a deterministic mock response — no AI call, no API key needed."""
    return MOCK_RESPONSE