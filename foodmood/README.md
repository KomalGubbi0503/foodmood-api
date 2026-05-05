# 🥑 FoodMood – AI Meal Processing & Recommendation API

> **Evaluation submission by Komal | SRH Heidelberg – M.Sc. Data Science**

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [AI Model Choice](#ai-model-choice)
4. [Nutrition Data Approach](#nutrition-data-approach)
5. [Caching & Optimisation](#caching--optimisation)
6. [API Reference](#api-reference)
7. [Project Structure](#project-structure)
8. [Running Tests](#running-tests)
9. [Trade-offs & Future Work](#trade-offs--future-work)

---

## Quick Start

### 1. Clone and set up

```bash
git clone https://github.com/<your-username>/foodmood-api.git
cd foodmood-api

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env
# create .env and add your OpenRouter API key
# Free key at: https://openrouter.ai  (no credit card required)
```

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

API docs available at: **http://localhost:8000/docs**

### 4. No API key? Use mock mode

```bash
MOCK_MODE=true uvicorn app.main:app --reload
```

Or per-request: set `"mock": true` in any `POST /parse-meal` body.

---

## Architecture

```
POST /parse-meal
      │
      ▼
  Cache lookup (TTLCache)
      │ miss
      ▼
  LLM Service (OpenRouter → Mistral-7B-Instruct)
      │
      ▼
  Build FoodItem list + aggregate macros
      │
      ▼
  Personalisation (rule-based, if user_profile provided)
      │
      ▼
  Store in cache → Return MealParseResponse
```

**Layer responsibilities:**

| Layer | File | Responsibility |
|-------|------|---------------|
| API | `app/api/endpoints/` | HTTP routing, request validation, error wrapping |
| Service | `app/services/meal_service.py` | Orchestration: cache → AI → personalisation |
| LLM | `app/services/llm_service.py` | OpenRouter HTTP call, prompt engineering, mock mode |
| Personalisation | `app/services/personalisation_service.py` | Rule-based goal/diet feedback |
| Cache | `app/utils/cache.py` | TTL + LRU in-memory cache |
| Models | `app/models/schemas.py` | Pydantic request/response schemas |
| Config | `app/core/config.py` | Settings from `.env` via pydantic-settings |
| Data | `data/nutrition_data.py` | Internal nutrition reference dataset |

---

## AI Model Choice

**Model:** `meta-llama/llama-3-8b-instruct` via **OpenRouter**

**Why OpenRouter?**
- Single unified API for 100+ open-source and commercial models
- Free tier available — no billing setup needed to evaluate this project
- Allows swapping models with one config change (`OPENROUTER_MODEL` in `.env`)

**Why meta-llama/llama-3-8b-instruct?**
- Available on OpenRouter's free tier
- excellent reasoning-following for structured JSON output
- 3–5 second response time — fast enough for a web API
- Open-source weights (Apache 2.0) — aligns with open-source requirement

**Alternative models** (just change `OPENROUTER_MODEL` in `.env`):
- `google/gemma-2-9b-it` — Google open-source, similar quality
- `Mistral-7B-Instruct` — opensource model, Strong instruction-following for structured JSON output
- `openai/gpt-4o-mini` — best accuracy, costs ~$0.15/1M tokens

**Prompt design:**
- System prompt establishes expert nutritionist persona
- User prompt requests strict JSON schema (structured output)
- Temperature = 0.2 for deterministic, consistent results
- Max tokens = 800 — sufficient for 5–8 food items, avoids waste

---

## Nutrition Data Approach

**Choice: Internal curated dataset** (with USDA as optional enrichment)

**Why not USDA FoodData Central as primary?**

| Factor | Internal Dataset | USDA API |
|--------|-----------------|----------|
| Latency | 0 ms | ~200–500 ms extra |
| Availability | Always | Requires API key + internet |
| Rate limits | None | 3,600 req/hour (free tier) |
| Setup complexity | Zero | API key registration |
| Coverage | ~50 common foods | 1M+ foods |

**Decision:** The LLM already estimates macros well for common meals. The internal dataset (`data/nutrition_data.py`) covers the 50 most frequently eaten foods with USDA-sourced values per 100g.

**USDA integration path:** Set `USDA_API_KEY` in `.env`. The architecture is ready for a `usda_service.py` that fetches exact values as a fallback/enrichment layer — a straightforward extension with more development time.

---

## Caching & Optimisation

### Strategy: TTL + LRU in-process cache

```python
# app/utils/cache.py
_cache: TTLCache = TTLCache(maxsize=256, ttl=3600)  
```

**Cache key:** MD5 hash of the lowercased, stripped meal description.
This means `"2 Eggs, Avocado"` and `"2 eggs, avocado"` hit the same cache entry.

**Why this approach?**
- Zero infrastructure — no Redis/Memcached needed
- Identical meal descriptions (very common in production) skip the LLM entirely
- Configurable TTL via `CACHE_TTL_SECONDS` in `.env`

**Additional optimisations:**
1. **Mock mode** — `MOCK_MODE=true` or `"mock": true` per-request skips all AI calls
2. **Low temperature (0.2)** — reduces tokens wasted on creative variation
3. **Max tokens = 800** — hard cap prevents runaway costs
4. **Async HTTP** — `httpx.AsyncClient` for non-blocking LLM calls

**Production path:** Replace `cachetools.TTLCache` with Redis for persistence across restarts and horizontal scaling.

---

## API Reference

### `POST /parse-meal`

Parse a free-text meal description.

**Request:**
```json
{
  "meal_description": "2 eggs, 1 slice whole wheat bread, avocado",
  "mock": false,
  "user_profile": {
    "goal": "lose",
    "diet_type": "high-protein",
    "daily_calorie_target": 1800
  }
}
```

**Response:**
```json
{
  "meal_description": "2 eggs, 1 slice whole wheat bread, avocado",
  "food_items": [
    { "name": "egg", "quantity": "2 units", "calories": 155, "protein_g": 13.0, "carbs_g": 1.1, "fat_g": 11.0 },
    { "name": "whole wheat bread", "quantity": "1 slice", "calories": 69, "protein_g": 2.5, "carbs_g": 12.9, "fat_g": 1.0 },
    { "name": "avocado", "quantity": "0.5 medium", "calories": 120, "protein_g": 1.5, "carbs_g": 6.8, "fat_g": 11.0 }
  ],
  "total_macros": { "calories": 344.0, "protein_g": 17.0, "carbs_g": 20.8, "fat_g": 23.0 },
  "ai_feedback": "Well-balanced breakfast with healthy fats from avocado, quality protein from eggs, and complex carbs from whole wheat bread.",
  "personalised": {
    "adjusted_feedback": "Good calorie control at 344 kcal — well suited for your weight-loss goal.",
    "suggestions": ["Increase protein with an extra egg or Greek yogurt to preserve muscle while in a deficit."],
    "goal_alignment": "good"
  },
  "cache_hit": false,
  "mock": false
}
```

---

### `POST /recommendations`

Get meal recommendations for a goal + diet combination.

**Request:**
```json
{ "goal": "lose", "diet_type": "low-carb" }
```

---

### `GET /health`

Service health check — returns model name and mock mode status.

### `GET /cache/stats`

Cache size, maxsize, and TTL for monitoring.

---

## Project Structure

```
foodmood/
├── app/
│   ├── main.py                          # FastAPI app factory
│   ├── api/
│   │   ├── router.py                    # Combines all routers
│   │   └── endpoints/
│   │       ├── meal.py                  # POST /parse-meal
│   │       ├── recommendations.py       # POST /recommendations
│   │       └── health.py               # GET /health, /cache/stats
│   ├── core/
│   │   └── config.py                   # Settings (pydantic-settings + .env)
│   ├── models/
│   │   └── schemas.py                  # All Pydantic request/response models
│   ├── services/
│   │   ├── meal_service.py             # Orchestration layer
│   │   ├── llm_service.py              # OpenRouter/Mistral integration
│   │   └── personalisation_service.py  # Rule-based personalisation
│   └── utils/
│       └── cache.py                    # TTLCache wrapper
├── data/
│   └── nutrition_data.py               # Internal nutrition reference (50 foods)
├── tests/
│   └── test_api.py                     # 11 test cases (all use mock mode)
├── .env.example                        # Environment variable template
├── requirements.txt
└── README.md
```

---

## Running Tests

```bash
# All tests run with mock=True — no API key or internet needed
pytest tests/ -v
```

Expected output: **11 tests passing**

---

## Trade-offs & Future Work

### What I prioritised
- **Working system end-to-end** over feature completeness
- **Developer experience** — mock mode makes the project runnable without any API key
- **Clean architecture** — clear separation of concerns for easy extension
- **Practical caching** — eliminates the most common redundant AI calls

### What I would improve with more time

| Improvement | Why |
|-------------|-----|
| Redis cache | Persist across restarts, support horizontal scaling |
| USDA API integration | Exact nutritional values for 1M+ foods |
| Async test suite | `pytest-asyncio` for true async test coverage |
| Authentication | JWT-based user auth to personalise at account level |
| Database (SQLite/Postgres) | Store meal history per user for trend analysis |
| Streaming responses | Stream AI feedback token-by-token for better UX |
| Product scanner endpoint | Barcode → Open Food Facts API → parse-meal pipeline |
| Rate limiting | `slowapi` middleware to prevent abuse |
| Docker + docker-compose | One-command deployment |
| CI/CD | GitHub Actions for automated testing on every PR |

---

## Notes for the Reviewer

- **Mock mode first:** Run with `MOCK_MODE=true` to see the full system working without any API key. All tests also use mock mode.
- **OpenRouter is free:** The actual AI integration works with a free OpenRouter account — no credit card. Key takes ~30 seconds to create at openrouter.ai.
- **Model is configurable:** Change `OPENROUTER_MODEL` in `.env` to use GPT-4o, Gemini, Llama-3, or any other OpenRouter-supported model without changing a single line of code.
- **Nutrition data choice:** I chose an internal dataset for zero-dependency operation, and explicitly documented the USDA path. In a production system I would use USDA as an enrichment layer after the LLM extracts food items.
