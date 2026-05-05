from fastapi import APIRouter
from app.api.endpoints import meal, recommendations, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(meal.router, tags=["Meal Parsing"])
api_router.include_router(recommendations.router, tags=["Recommendations"])
