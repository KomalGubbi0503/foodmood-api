from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title="FoodMood API",
        description=(
            "AI-powered meal parsing and nutrition recommendation service.\n\n"
            "## Quick start\n"
            "1. `POST /parse-meal` with a free-text meal description\n"
            "2. Add `user_profile` to get personalised feedback\n"
            "3. Use `mock: true` during development to skip AI calls\n\n"
            "## LLM\n"
            f"Running **{settings.openrouter_model}** via [OpenRouter](https://openrouter.ai)"
        ),
        version="1.0.0",
        contact={"name": "FoodMood Engineering", "email": "eng@foodmood.app"},
    )

    # Allow local development frontend / Swagger UI
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    return app


app = create_app()
