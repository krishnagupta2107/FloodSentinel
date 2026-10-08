"""
Unified multi-modal risk fusion and site prioritization endpoint.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status

from api.schemas.api_models import (
    RankAlertsRequest,
    RankAlertsResponse,
    SiteRankOutput,
)
from api.dependencies import (
    get_overflow_predictor,
    get_rainfall_predictor,
    get_fusion_engine,
)
from src.floodsentinel.risk.schemas import FusionWeights, SiteInput
from src.floodsentinel.risk.risk_ranker import rank_sites

router = APIRouter(tags=["Risk Fusion & Prioritization"])


@router.post(
    "/alerts/rank",
    response_model=RankAlertsResponse,
    summary="Rank and prioritize drainage sites using multi-modal risk fusion",
    description=(
        "Synthesizes CCTV visual blockage, sensor telemetry overflow probabilities, regional rainfall forecasts, "
        "and optional site vulnerability into calibrated 0.0-1.0 risk scores. Sorts sites in descending order of urgency (Rank 1 = Critical)."
    ),
)
def rank_alerts(request: RankAlertsRequest) -> RankAlertsResponse:
    if not request.sites:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one site record must be supplied in 'sites'.",
        )

    # Convert custom weights if supplied
    weights = None
    if request.weights:
        try:
            weights = FusionWeights(
                blockage_weight=request.weights.blockage_weight,
                overflow_weight=request.weights.overflow_weight,
                rainfall_weight=request.weights.rainfall_weight,
                vulnerability_weight=request.weights.vulnerability_weight,
                overflow_15min_weight=request.weights.overflow_15min_weight,
                overflow_30min_weight=request.weights.overflow_30min_weight,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid fusion weights configuration: {e}",
            )

    engine = get_fusion_engine(weights=weights)
    overflow_pred = get_overflow_predictor()
    rainfall_pred = get_rainfall_predictor()

    site_inputs: List[SiteInput] = []

    for site_req in request.sites:
        p15 = site_req.overflow_probability_15min
        p30 = site_req.overflow_probability_30min

        # If raw overflow telemetry is provided, evaluate directly
        if (p15 is None or p30 is None) and site_req.overflow is not None:
            try:
                tel_dict = site_req.overflow.model_dump()
                eval_p15, eval_p30 = overflow_pred.predict_proba(tel_dict)
                p15 = p15 if p15 is not None else eval_p15
                p30 = p30 if p30 is not None else eval_p30
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Failed to evaluate overflow telemetry for site '{site_req.site_id}': {e}",
                )

        rain_mm = site_req.rainfall_prediction_mm
        # If raw rainfall lookback is provided, evaluate directly
        if rain_mm is None and site_req.rainfall is not None:
            try:
                rain_res = rainfall_pred.predict(
                    previous_12_months=site_req.rainfall.rainfall_lags,
                    subdivision=site_req.rainfall.subdivision,
                    target_month=site_req.rainfall.target_month,
                )
                rain_mm = rain_res["average_prediction_mm"]
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Failed to evaluate rainfall forecast for site '{site_req.site_id}': {e}",
                )

        site_inputs.append(
            SiteInput(
                site_id=site_req.site_id,
                image_name=site_req.image_name,
                occlusion_percentage=site_req.occlusion_percentage,
                overflow_probability_15min=p15,
                overflow_probability_30min=p30,
                rainfall_prediction_mm=rain_mm,
                vulnerability_score=site_req.vulnerability_score,
                metadata=site_req.metadata,
            )
        )

    try:
        ranked_results = rank_sites(site_inputs, engine=engine)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    output_list: List[SiteRankOutput] = []
    for r in ranked_results:
        output_list.append(
            SiteRankOutput(
                rank=r.rank,
                site_id=r.site_id,
                risk_score=r.risk_score,
                risk_level=r.risk_level.value,
                image_name=r.image_name,
                occlusion_percentage=r.raw_inputs.get("occlusion_percentage"),
                blockage_score=r.blockage_score,
                overflow_probability_15min=r.raw_inputs.get("overflow_probability_15min"),
                overflow_probability_30min=r.raw_inputs.get("overflow_probability_30min"),
                overflow_score=r.overflow_score,
                rainfall_prediction_mm=r.raw_inputs.get("rainfall_prediction_mm"),
                rainfall_score=r.rainfall_score,
                vulnerability_score=r.vulnerability_score,
                vulnerability_available=r.vulnerability_available,
                dominant_risk_factor=r.dominant_risk_factor,
                explanation=r.explanation,
                factor_breakdown=r.factor_breakdown,
            )
        )

    return RankAlertsResponse(
        total_sites=len(output_list),
        ranked_sites=output_list,
    )
