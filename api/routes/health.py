"""
Health check and model readiness endpoint.
"""

from fastapi import APIRouter
from api.schemas.api_models import HealthResponse, ModelReadiness
from api.dependencies import check_models_health
from api.config import settings

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health and ML model status",
    description="Returns the FloodSentinel API service status and the readiness of underlying ML model artifacts.",
)
def get_health() -> HealthResponse:
    model_status = check_models_health()
    all_ready = all(model_status.values())
    return HealthResponse(
        status="ok" if all_ready else "degraded",
        service=settings.app_name,
        version=settings.app_version,
        models=ModelReadiness(
            rainfall=model_status["rainfall"],
            overflow=model_status["overflow"],
            fusion=model_status["fusion"],
        ),
    )
