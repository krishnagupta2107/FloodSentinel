"""
Underground sensor telemetry overflow prediction endpoint.
"""

from fastapi import APIRouter, HTTPException, status
from api.schemas.api_models import OverflowTelemetryInput, OverflowPredictResponse
from api.dependencies import get_overflow_predictor, get_fusion_engine

router = APIRouter(tags=["Overflow Prediction"])


@router.post(
    "/risk/overflow",
    response_model=OverflowPredictResponse,
    summary="Predict drain overflow onset probability from sensor telemetry",
    description=(
        "Evaluates real-time underground catch basin telemetry (water level, rise rate, pipe specs, cumulative rain) "
        "using trained XGBoost classifiers to predict 15-minute and 30-minute overflow onset probabilities."
    ),
)
def predict_overflow(telemetry: OverflowTelemetryInput) -> OverflowPredictResponse:
    overflow_pred = get_overflow_predictor()
    engine = get_fusion_engine()

    try:
        telemetry_dict = telemetry.model_dump()
        p15, p30 = overflow_pred.predict_proba(telemetry_dict)
        overflow_score = engine.compute_overflow_score(p15, p30)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute overflow onset prediction models.",
        )

    return OverflowPredictResponse(
        overflow_probability_15min=round(p15, 4),
        overflow_probability_30min=round(p30, 4),
        overflow_score=round(overflow_score, 4),
    )
