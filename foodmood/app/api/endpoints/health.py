from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.core.config import get_settings
from app.utils.cache import cache_stats

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse, summary="Service health check")
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version="1.0.0",
        mock_mode=settings.mock_mode,
        model=settings.openrouter_model,
    )


@router.get("/cache/stats", summary="Cache statistics (dev only)")
async def get_cache_stats() -> dict:
    return cache_stats()
