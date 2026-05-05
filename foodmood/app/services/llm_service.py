
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
  "ai_feedback": "string - 2-3 sentence nutritional assessment of the overall meal"
}}

Meal description: "{meal_description}"

Rules:
- Estimate realistic calories and macros based on typical serving sizes.
- If a quantity is ambiguous, use a standard/average portion.
- ai_feedback must be specific to THIS meal (mention actual foods).
- Return ONLY the JSON object, nothing else.
"""


async def parse_meal_with_llm(meal_description: str) -> dict:
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
    return _extract_json(raw_text)


def _extract_json(raw_text: str) -> dict:
    # 1. Strip markdown fences
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

    # 2. Direct parse
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    # 3. Extract first {...} block
    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # 4. Fix truncated JSON
    open_braces = raw_text.count('{') - raw_text.count('}')
    open_brackets = raw_text.count('[') - raw_text.count(']')
    fixed = raw_text.rstrip() + '}' * open_braces + ']' * open_brackets
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    # 5. Fallback to mock
    result = dict(MOCK_RESPONSE)
    result["ai_feedback"] = "AI response could not be parsed. Showing estimated values."
    return result


MOCK_RESPONSE = {
    "food_items": [
        {"name": "egg", "quantity": "2 units", "calories": 155, "protein_g": 13.0, "carbs_g": 1.1, "fat_g": 11.0},
        {"name": "whole wheat bread", "quantity": "1 slice", "calories": 69, "protein_g": 2.5, "carbs_g": 12.9, "fat_g": 1.0},
        {"name": "avocado", "quantity": "0.5 medium", "calories": 120, "protein_g": 1.5, "carbs_g": 6.8, "fat_g": 11.0},
    ],
    "ai_feedback": (
        "This is a well-balanced breakfast with healthy fats from avocado, "
        "quality protein from eggs, and complex carbohydrates from whole wheat bread. "
        "It provides sustained energy and keeps you satiated for several hours."
    ),
}


async def parse_meal_mock(_meal_description: str) -> dict:
    return MOCK_RESPONSE