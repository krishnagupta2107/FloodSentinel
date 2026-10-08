"""
Site ranking and prioritization module.
Evaluates a collection of drainage monitoring sites, calculates fused risk scores,
ranks them descending by severity, and produces tabular summaries.
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd

from src.floodsentinel.risk.schemas import SiteInput, SiteRiskResult
from src.floodsentinel.risk.risk_fusion import RiskFusionEngine


def rank_sites(
    records: List[Union[SiteInput, Dict[str, Any]]],
    engine: Optional[RiskFusionEngine] = None,
) -> List[SiteRiskResult]:
    """
    Evaluates each site record, assigns unified risk scores, sorts sites in descending
    order of risk severity (rank 1 = highest risk), and assigns ranks.
    """
    if not records:
        return []

    evaluator = engine or RiskFusionEngine()

    evaluated_sites: List[SiteRiskResult] = [
        evaluator.evaluate_site(rec) for rec in records
    ]

    # Sort descending by risk_score, with tie-breakers on overflow_score, then blockage_score
    evaluated_sites.sort(
        key=lambda s: (s.risk_score, s.overflow_score, s.blockage_score),
        reverse=True,
    )

    # Assign 1-indexed ranks
    for idx, site in enumerate(evaluated_sites, start=1):
        site.rank = idx

    return evaluated_sites


def to_dataframe(results: List[SiteRiskResult]) -> pd.DataFrame:
    """
    Converts a list of SiteRiskResult objects into a flattened pandas DataFrame.
    """
    rows = []
    for r in results:
        rows.append({
            "rank": r.rank,
            "site_id": r.site_id,
            "risk_score": r.risk_score,
            "risk_level": r.risk_level.value,
            "image_name": r.image_name,
            "occlusion_percentage": r.raw_inputs.get("occlusion_percentage"),
            "blockage_score": r.blockage_score,
            "overflow_probability_15min": r.raw_inputs.get("overflow_probability_15min"),
            "overflow_probability_30min": r.raw_inputs.get("overflow_probability_30min"),
            "overflow_score": r.overflow_score,
            "rainfall_prediction_mm": r.raw_inputs.get("rainfall_prediction_mm"),
            "rainfall_score": r.rainfall_score,
            "vulnerability_score": r.vulnerability_score,
            "dominant_risk_factor": r.dominant_risk_factor,
            "explanation": r.explanation,
        })
    return pd.DataFrame(rows)
