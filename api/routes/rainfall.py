"""
Meteorological rainfall prediction endpoint.
"""

from fastapi import APIRouter, HTTPException, status
from api.schemas.api_models import RainfallPredictRequest, RainfallPredictResponse
from api.dependencies import get_rainfall_predictor

router = APIRouter(tags=["Rainfall Forecasting"])


@router.post(
    "/risk/predict",
    response_model=RainfallPredictResponse,
    summary="Predict next-month rainfall using XGBoost + LSTM ensemble",
    description=(
        "Forecasts next-month rainfall volume (in millimeters) based on a 12-month historical rainfall sequence, "
        "meteorological subdivision, and target calendar month. Uses real XGBoost and subdivision-aware LSTM models."
    ),
)
def predict_rainfall(request: RainfallPredictRequest) -> RainfallPredictResponse:
    predictor = get_rainfall_predictor()

    try:
        result = predictor.predict(
            previous_12_months=request.rainfall_lags,
            subdivision=request.subdivision,
            target_month=request.target_month,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute rainfall forecasting model.",
        )

    return RainfallPredictResponse(
        subdivision=result["subdivision"],
        target_month=result["target_month"],
        xgboost_prediction_mm=result["xgboost_prediction_mm"],
        lstm_prediction_mm=result["lstm_prediction_mm"],
        average_prediction_mm=result["average_prediction_mm"],
    )
