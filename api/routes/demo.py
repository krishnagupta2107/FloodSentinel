"""
Demonstration endpoint illustrating multi-modal risk fusion.
Clearly labelled as synthetic demonstration data.
"""

import os
import pandas as pd
from fastapi import APIRouter

from api.schemas.api_models import DemoRiskResponse, SiteRankOutput
from api.dependencies import (
    get_overflow_predictor,
    get_rainfall_predictor,
    get_fusion_engine,
)
from api.config import settings
from src.floodsentinel.risk.schemas import SiteInput
from src.floodsentinel.risk.risk_ranker import rank_sites

router = APIRouter(tags=["Demonstration"])

OCCLUSION_CSV = os.path.join(settings.base_dir, "runs", "detect", "occlusion_results.csv")


@router.get(
    "/demo/risk",
    response_model=DemoRiskResponse,
    summary="Get sample ranked risk prioritization for 10 demonstration catch basins",
    description=(
        "Executes multi-modal risk fusion on sample CCTV test images paired with synthetic sensor telemetry scenarios. "
        "Explicitly marked as demonstration data."
    ),
)
def get_demo_risk() -> DemoRiskResponse:
    overflow_pred = get_overflow_predictor()
    rainfall_pred = get_rainfall_predictor()
    engine = get_fusion_engine()

    # Load sample CCTV occlusion records from runs/detect/occlusion_results.csv if available
    sample_images = []
    if os.path.exists(OCCLUSION_CSV):
        occlusion_df = pd.read_csv(OCCLUSION_CSV)
        sample_images = occlusion_df.head(10).to_dict(orient="records")

    sample_rainfall_lookback = [12.0, 18.5, 45.0, 120.0, 310.0, 480.0, 520.0, 450.0, 280.0, 110.0, 35.0, 15.0]
    subdivision = "ANDAMAN & NICOBAR ISLANDS"
    rain_result = rainfall_pred.predict(
        previous_12_months=sample_rainfall_lookback,
        subdivision=subdivision,
        target_month=6,
    )
    predicted_rain_mm = rain_result["average_prediction_mm"]

    telemetry_scenarios = [
        {"water_level_cm": 92.0, "rise_rate_cm_per_15min": 8.5, "rainfall_mm_per_hr": 35.0,
         "cumulative_rain_6hr_mm": 70.0, "cumulative_rain_24hr_mm": 150.0, "pipe_diameter_mm": 600.0,
         "pipe_slope": 0.015, "elevation_m": 12.0, "month": 6, "pipe_material": "Concrete"},
        {"water_level_cm": 75.0, "rise_rate_cm_per_15min": 5.0, "rainfall_mm_per_hr": 22.0,
         "cumulative_rain_6hr_mm": 45.0, "cumulative_rain_24hr_mm": 90.0, "pipe_diameter_mm": 800.0,
         "pipe_slope": 0.02, "elevation_m": 15.0, "month": 6, "pipe_material": "Cast Iron"},
        {"water_level_cm": 50.0, "rise_rate_cm_per_15min": 2.0, "rainfall_mm_per_hr": 10.0,
         "cumulative_rain_6hr_mm": 20.0, "cumulative_rain_24hr_mm": 40.0, "pipe_diameter_mm": 600.0,
         "pipe_slope": 0.01, "elevation_m": 18.0, "month": 6, "pipe_material": "PVC"},
        {"water_level_cm": 20.0, "rise_rate_cm_per_15min": 0.0, "rainfall_mm_per_hr": 0.0,
         "cumulative_rain_6hr_mm": 0.0, "cumulative_rain_24hr_mm": 0.0, "pipe_diameter_mm": 600.0,
         "pipe_slope": 0.02, "elevation_m": 22.0, "month": 6, "pipe_material": "Concrete"},
    ]

    site_inputs = []
    for idx, row in enumerate(sample_images):
        site_id = f"SITE_CATCH_{idx+1:03d}"
        tel = telemetry_scenarios[idx % len(telemetry_scenarios)]
        p15, p30 = overflow_pred.predict_proba(tel)
        site_rain = round(predicted_rain_mm * (0.85 + 0.03 * idx), 1)

        site_inputs.append(
            SiteInput(
                site_id=site_id,
                image_name=row.get("image_name"),
                occlusion_percentage=float(row.get("occlusion_percentage", 0.0)),
                overflow_probability_15min=p15,
                overflow_probability_30min=p30,
                rainfall_prediction_mm=site_rain,
                vulnerability_score=None,
                metadata={"subdivision": subdivision, "telemetry": tel},
            )
        )

    ranked_results = rank_sites(site_inputs, engine=engine)

    outputs = [
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
        for r in ranked_results
    ]

    return DemoRiskResponse(
        is_demo_data=True,
        notice=(
            "DEMO DATA NOTICE: The underlying ML models (YOLO, XGBoost, LSTM) are real and fully trained. "
            "However, the catch basin site IDs and sensor-to-camera bindings in this demonstration are synthetic scenarios. "
            "Production usage requires mapping real IoT telemetry streams to specific municipal GIS sites."
        ),
        total_sites=len(outputs),
        ranked_sites=outputs,
    )
