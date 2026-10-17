"""
Demo script for FloodSentinel Unified Risk Fusion and Site Prioritization.
Synthesizes:
1. CCTV visual blockage occlusion (from YOLOv8 detection & occlusion estimation)
2. Underground sensor overflow probability (from XGBoost 15min/30min onset models)
3. Regional rainfall forecast (from XGBoost + LSTM RainfallPredictor)
4. Optional site vulnerability metadata

Saves ranked results to evaluation/fused_risk_rankings.csv.
"""

import os
import sys
import pandas as pd
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.floodsentinel.risk import (
    RiskFusionEngine,
    FusionWeights,
    OverflowPredictor,
    RainfallNormalizer,
    rank_sites,
    to_dataframe,
)
from src.floodsentinel.models.rainfall_predictor import RainfallPredictor
OCCLUSION_CSV = os.path.join(BASE_DIR, "runs", "detect", "occlusion_results.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "evaluation")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "fused_risk_rankings.csv")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 80)
    print("   FLOODSENTINEL UNIFIED MULTI-MODAL RISK FUSION & PRIORITIZATION DEMO")
    print("=" * 80)

    # 1. Initialize Real Model Artifacts
    print("\n[1/4] Initializing real model artifacts...")
    overflow_pred = OverflowPredictor()
    rainfall_pred = RainfallPredictor()
    normalizer = RainfallNormalizer()
    engine = RiskFusionEngine(
        weights=FusionWeights(
            blockage_weight=0.35,
            overflow_weight=0.45,
            rainfall_weight=0.20,
            vulnerability_weight=0.00,
        ),
        rainfall_normalizer=normalizer,
        overflow_predictor=overflow_pred,
    )
    print("  -> Loaded XGBoost Overflow models (15-min & 30-min)")
    print("  -> Loaded XGBoost & LSTM Rainfall forecasting models")
    print("  -> Loaded Empirical Historical Rainfall Normalizer")

    # 2. Prepare Sample Multi-Modal Site Inputs
    print("\n[2/4] Constructing multi-modal monitoring site records...")
    # Load sample CCTV occlusion records from runs/detect/occlusion_results.csv
    occlusion_df = pd.read_csv(OCCLUSION_CSV)
    sample_images = occlusion_df.head(10).to_dict(orient="records")

    # Example meteorological rainfall lookback (12 historical months)
    sample_rainfall_lookback = [12.0, 18.5, 45.0, 120.0, 310.0, 480.0, 520.0, 450.0, 280.0, 110.0, 35.0, 15.0]
    subdivision = "ANDAMAN & NICOBAR ISLANDS"
    
    # Compute real rainfall forecast
    rain_result = rainfall_pred.predict(
        previous_12_months=sample_rainfall_lookback,
        subdivision=subdivision,
        target_month=6,  # Monsoon onset month
    )
    predicted_rain_mm = rain_result["average_prediction_mm"]
    print(f"  -> Evaluated regional rainfall forecast: {predicted_rain_mm:.1f} mm")

    # Realistic simulated sensor telemetry conditions for urban drainage catchments
    telemetry_scenarios = [
        # Critical surge scenario
        {"water_level_cm": 92.0, "rise_rate_cm_per_15min": 8.5, "rainfall_mm_per_hr": 35.0,
         "cumulative_rain_6hr_mm": 70.0, "cumulative_rain_24hr_mm": 150.0, "pipe_diameter_mm": 600.0,
         "pipe_slope": 0.015, "elevation_m": 12.0, "month": 6, "pipe_material": "Concrete"},
        # High rising level scenario
        {"water_level_cm": 75.0, "rise_rate_cm_per_15min": 5.0, "rainfall_mm_per_hr": 22.0,
         "cumulative_rain_6hr_mm": 45.0, "cumulative_rain_24hr_mm": 90.0, "pipe_diameter_mm": 800.0,
         "pipe_slope": 0.02, "elevation_m": 15.0, "month": 6, "pipe_material": "Cast Iron"},
        # Moderate flow scenario
        {"water_level_cm": 50.0, "rise_rate_cm_per_15min": 2.0, "rainfall_mm_per_hr": 10.0,
         "cumulative_rain_6hr_mm": 20.0, "cumulative_rain_24hr_mm": 40.0, "pipe_diameter_mm": 600.0,
         "pipe_slope": 0.01, "elevation_m": 18.0, "month": 6, "pipe_material": "PVC"},
        # Normal dry scenario
        {"water_level_cm": 20.0, "rise_rate_cm_per_15min": 0.0, "rainfall_mm_per_hr": 0.0,
         "cumulative_rain_6hr_mm": 0.0, "cumulative_rain_24hr_mm": 0.0, "pipe_diameter_mm": 600.0,
         "pipe_slope": 0.02, "elevation_m": 22.0, "month": 6, "pipe_material": "Concrete"},
    ]

    site_records = []
    for idx, row in enumerate(sample_images):
        site_id = f"SITE_CATCH_{idx+1:03d}"
        tel = telemetry_scenarios[idx % len(telemetry_scenarios)]
        p15, p30 = overflow_pred.predict_proba(tel)
        
        # Vary rainfall slightly per catchment topography
        site_rain = round(predicted_rain_mm * (0.85 + 0.03 * idx), 1)

        site_records.append({
            "site_id": site_id,
            "image_name": row["image_name"],
            "occlusion_percentage": float(row["occlusion_percentage"]),
            "overflow_probability_15min": p15,
            "overflow_probability_30min": p30,
            "rainfall_prediction_mm": site_rain,
            "vulnerability_score": None,  # Explicitly marked unavailable
            "metadata": {"subdivision": subdivision, "telemetry": tel},
        })

    # 3. Execute Site Ranking and Prioritization
    print("\n[3/4] Running multi-criteria risk fusion and ranking...")
    ranked_results = rank_sites(site_records, engine=engine)

    # 4. Save and Output Results
    df_results = to_dataframe(ranked_results)
    df_results.to_csv(OUTPUT_CSV, index=False)
    print(f"  -> Saved ranked results to: {OUTPUT_CSV}")

    print("\n" + "=" * 105)
    print(f"{'Rank':<5} | {'Site ID':<15} | {'Risk Score':<11} | {'Level':<9} | {'Blockage':<9} | {'Overflow':<9} | {'Rainfall':<9} | {'Dominant Factor'}")
    print("-" * 105)
    for r in ranked_results:
        print(
            f"{r.rank:<5} | "
            f"{r.site_id:<15} | "
            f"{r.risk_score:<11.4f} | "
            f"{r.risk_level.value:<9} | "
            f"{r.blockage_score:<9.4f} | "
            f"{r.overflow_score:<9.4f} | "
            f"{r.rainfall_score:<9.4f} | "
            f"{r.dominant_risk_factor}"
        )
    print("=" * 105)

    print("\nExample Detailed Explanation for Top Priority Site:")
    top_site = ranked_results[0]
    print(f"[{top_site.site_id}] Rank #{top_site.rank} ({top_site.risk_level.value}):")
    print(f"  {top_site.explanation}")
    print("  Factor breakdown:")
    for k, v in top_site.factor_breakdown.items():
        print(f"    - {k:<12}: raw={v['raw_score']:.3f}, weight={v['weight']:.2f}, contribution={v['weighted_contribution']:.4f} ({v['percentage_share']}%)")


if __name__ == "__main__":
    main()
