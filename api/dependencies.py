"""
Dependency management and singleton ML model instances for FastAPI.
"""

from typing import Dict, Optional
import logging

from src.floodsentinel.models.rainfall_predictor import RainfallPredictor
from src.floodsentinel.risk.overflow_predictor import OverflowPredictor
from src.floodsentinel.risk.rainfall_normalizer import RainfallNormalizer
from src.floodsentinel.risk.risk_fusion import RiskFusionEngine
from src.floodsentinel.risk.schemas import FusionWeights

logger = logging.getLogger("floodsentinel.api")

# Singleton cache
_rainfall_predictor: Optional[RainfallPredictor] = None
_overflow_predictor: Optional[OverflowPredictor] = None
_rainfall_normalizer: Optional[RainfallNormalizer] = None
_fusion_engine: Optional[RiskFusionEngine] = None


def get_rainfall_predictor() -> RainfallPredictor:
    """Returns the singleton instance of RainfallPredictor."""
    global _rainfall_predictor
    if _rainfall_predictor is None:
        logger.info("Initializing RainfallPredictor singleton...")
        _rainfall_predictor = RainfallPredictor()
    return _rainfall_predictor


def get_overflow_predictor() -> OverflowPredictor:
    """Returns the singleton instance of OverflowPredictor."""
    global _overflow_predictor
    if _overflow_predictor is None:
        logger.info("Initializing OverflowPredictor singleton...")
        _overflow_predictor = OverflowPredictor()
    return _overflow_predictor


def get_rainfall_normalizer() -> RainfallNormalizer:
    """Returns the singleton instance of RainfallNormalizer."""
    global _rainfall_normalizer
    if _rainfall_normalizer is None:
        logger.info("Initializing RainfallNormalizer singleton...")
        _rainfall_normalizer = RainfallNormalizer()
    return _rainfall_normalizer


def get_fusion_engine(weights: Optional[FusionWeights] = None) -> RiskFusionEngine:
    """Returns a RiskFusionEngine instance with injected predictors."""
    overflow_pred = get_overflow_predictor()
    rain_norm = get_rainfall_normalizer()
    return RiskFusionEngine(
        weights=weights or FusionWeights(),
        rainfall_normalizer=rain_norm,
        overflow_predictor=overflow_pred,
    )


def check_models_health() -> Dict[str, bool]:
    """Checks the readiness of all core ML models."""
    status = {"rainfall": False, "overflow": False, "fusion": False}
    try:
        get_rainfall_predictor()
        status["rainfall"] = True
    except Exception as e:
        logger.error("RainfallPredictor health check failed: %s", e)

    try:
        get_overflow_predictor()
        status["overflow"] = True
    except Exception as e:
        logger.error("OverflowPredictor health check failed: %s", e)

    if status["overflow"]:
        status["fusion"] = True

    return status
