"""
API schemas package.
"""

from api.schemas.api_models import (
    HealthResponse,
    ModelReadiness,
    RainfallPredictRequest,
    RainfallPredictResponse,
    OverflowTelemetryInput,
    OverflowPredictResponse,
    FusionWeightsInput,
    SiteAlertInput,
    RankAlertsRequest,
    RankAlertsResponse,
    SiteRankOutput,
    DemoRiskResponse,
)

__all__ = [
    "HealthResponse",
    "ModelReadiness",
    "RainfallPredictRequest",
    "RainfallPredictResponse",
    "OverflowTelemetryInput",
    "OverflowPredictResponse",
    "FusionWeightsInput",
    "SiteAlertInput",
    "RankAlertsRequest",
    "RankAlertsResponse",
    "SiteRankOutput",
    "DemoRiskResponse",
]
