"""
Risk Fusion Engine.
Synthesizes visual blockage severity, sensor overflow probabilities,
meteorological rainfall forecasts, and optional site vulnerability into
a unified, calibrated 0.0 to 1.0 flood risk score.
"""

from typing import Any, Dict, Optional, Union
import numpy as np

from src.floodsentinel.risk.schemas import (
    FusionWeights,
    RiskLevel,
    RiskThresholds,
    SiteInput,
    SiteRiskResult,
)
from src.floodsentinel.risk.rainfall_normalizer import RainfallNormalizer
from src.floodsentinel.risk.overflow_predictor import OverflowPredictor


class RiskFusionEngine:
    """
    Core engine responsible for computing unified risk scores, risk levels,
    factor contribution breakdowns, and human-readable explanations.
    """

    def __init__(
        self,
        weights: Optional[FusionWeights] = None,
        thresholds: Optional[RiskThresholds] = None,
        rainfall_normalizer: Optional[RainfallNormalizer] = None,
        overflow_predictor: Optional[OverflowPredictor] = None,
    ):
        self.weights = weights or FusionWeights()
        self.thresholds = thresholds or RiskThresholds()
        self.rainfall_normalizer = rainfall_normalizer or RainfallNormalizer()
        self.overflow_predictor = overflow_predictor

    def normalize_blockage(self, occlusion_percentage: Optional[float]) -> float:
        """
        Normalizes CCTV grate occlusion percentage (0-100%) to [0.0, 1.0].
        """
        if occlusion_percentage is None:
            return 0.0
        try:
            val = float(occlusion_percentage)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid occlusion percentage: {occlusion_percentage}")

        if np.isnan(val) or val <= 0.0:
            return 0.0
        return float(np.clip(val / 100.0, 0.0, 1.0))

    def compute_overflow_score(
        self,
        p15: Optional[float],
        p30: Optional[float],
    ) -> float:
        """
        Computes the combined overflow risk score from 15-min and 30-min probabilities.
        """
        if p15 is None and p30 is None:
            return 0.0

        p15_val = float(p15) if p15 is not None else None
        p30_val = float(p30) if p30 is not None else None

        if p15_val is not None and (p15_val < 0.0 or p15_val > 1.0 or np.isnan(p15_val)):
            raise ValueError(f"p15 must be in [0.0, 1.0], got {p15_val}")
        if p30_val is not None and (p30_val < 0.0 or p30_val > 1.0 or np.isnan(p30_val)):
            raise ValueError(f"p30 must be in [0.0, 1.0], got {p30_val}")

        if p15_val is not None and p30_val is not None:
            score = (
                self.weights.overflow_15min_weight * p15_val
                + self.weights.overflow_30min_weight * p30_val
            )
        elif p15_val is not None:
            score = p15_val
        else:
            score = p30_val

        return float(np.clip(score, 0.0, 1.0))

    def compute_rainfall_score(self, rainfall_mm: Optional[float]) -> float:
        """
        Transforms forecasted rainfall in mm to a normalized risk score [0.0, 1.0].
        """
        return self.rainfall_normalizer.normalize(rainfall_mm)

    def normalize_vulnerability(self, vulnerability: Optional[float]) -> Optional[float]:
        """
        Validates and clamps optional vulnerability score to [0.0, 1.0].
        """
        if vulnerability is None:
            return None
        try:
            val = float(vulnerability)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid vulnerability score: {vulnerability}")

        if np.isnan(val):
            return None
        return float(np.clip(val, 0.0, 1.0))

    def _generate_explanation(
        self,
        site_id: str,
        risk_score: float,
        risk_level: RiskLevel,
        dominant_factor: str,
        scores: Dict[str, float],
        weights: Dict[str, float],
        raw_inputs: Dict[str, Any],
    ) -> str:
        """
        Generates an intuitive, actionable natural-language summary.
        """
        parts = [
            f"Site {site_id} is evaluated at {risk_level.value} risk (Score: {risk_score:.2f}).",
            f"Primary risk driver: {dominant_factor}.",
        ]

        # Specific context clues
        evidence = []
        occ = raw_inputs.get("occlusion_percentage")
        if occ is not None and occ > 0:
            evidence.append(f"Visual grate occlusion: {occ:.1f}%")

        p15 = raw_inputs.get("overflow_probability_15min")
        p30 = raw_inputs.get("overflow_probability_30min")
        if p15 is not None or p30 is not None:
            p15_str = f"{p15*100:.0f}%" if p15 is not None else "N/A"
            p30_str = f"{p30*100:.0f}%" if p30 is not None else "N/A"
            evidence.append(f"Sensor overflow probability: 15min={p15_str}, 30min={p30_str}")

        rain = raw_inputs.get("rainfall_prediction_mm")
        if rain is not None:
            evidence.append(f"Forecasted rainfall: {rain:.1f} mm")

        if evidence:
            parts.append("Key signals: " + "; ".join(evidence) + ".")

        return " ".join(parts)

    def evaluate_site(
        self,
        site_data: Union[SiteInput, Dict[str, Any]],
    ) -> SiteRiskResult:
        """
        Evaluates a single drainage site and returns its fused risk profile.
        """
        if isinstance(site_data, dict):
            site_input = SiteInput.from_dict(site_data)
        else:
            site_input = site_data

        # If telemetry metadata is provided and probabilities are not, use overflow predictor
        p15 = site_input.overflow_probability_15min
        p30 = site_input.overflow_probability_30min
        if (p15 is None or p30 is None) and "telemetry" in site_input.metadata and self.overflow_predictor:
            tel_p15, tel_p30 = self.overflow_predictor.predict_proba(site_input.metadata["telemetry"])
            p15 = p15 if p15 is not None else tel_p15
            p30 = p30 if p30 is not None else tel_p30

        # Compute individual scores
        blockage_score = self.normalize_blockage(site_input.occlusion_percentage)
        overflow_score = self.compute_overflow_score(p15, p30)
        rainfall_score = self.compute_rainfall_score(site_input.rainfall_prediction_mm)
        vulnerability_score = self.normalize_vulnerability(site_input.vulnerability_score)
        has_vulnerability = vulnerability_score is not None

        # Normalized active weights
        active_weights = self.weights.normalized_weights(has_vulnerability=has_vulnerability)

        scores = {
            "blockage": blockage_score,
            "overflow": overflow_score,
            "rainfall": rainfall_score,
        }
        if has_vulnerability:
            scores["vulnerability"] = vulnerability_score

        # Weighted risk calculation
        risk_score = sum(active_weights[k] * scores[k] for k in active_weights)
        risk_score = float(np.clip(risk_score, 0.0, 1.0))
        risk_level = self.thresholds.get_level(risk_score)

        # Factor contributions & dominant factor determination
        contributions = {
            k: active_weights[k] * scores[k] for k in active_weights
        }
        max_contrib_key = max(contributions, key=lambda k: contributions[k])

        factor_labels = {
            "blockage": "CCTV Grate Blockage Severity",
            "overflow": "Underground Sensor Overflow Probability",
            "rainfall": "Forecasted Rainfall Intensity",
            "vulnerability": "Site Physical & Urban Vulnerability",
        }
        dominant_factor = factor_labels.get(max_contrib_key, max_contrib_key.capitalize())

        raw_inputs = {
            "occlusion_percentage": site_input.occlusion_percentage,
            "overflow_probability_15min": p15,
            "overflow_probability_30min": p30,
            "rainfall_prediction_mm": site_input.rainfall_prediction_mm,
            "vulnerability_score": site_input.vulnerability_score,
        }

        explanation = self._generate_explanation(
            site_id=site_input.site_id,
            risk_score=risk_score,
            risk_level=risk_level,
            dominant_factor=dominant_factor,
            scores=scores,
            weights=active_weights,
            raw_inputs=raw_inputs,
        )

        factor_breakdown = {
            k: {
                "raw_score": round(scores[k], 4),
                "weight": round(active_weights[k], 4),
                "weighted_contribution": round(contributions[k], 4),
                "percentage_share": (
                    round((contributions[k] / risk_score) * 100.0, 1)
                    if risk_score > 0
                    else 0.0
                ),
            }
            for k in active_weights
        }

        return SiteRiskResult(
            site_id=site_input.site_id,
            risk_score=risk_score,
            risk_level=risk_level,
            image_name=site_input.image_name,
            blockage_score=blockage_score,
            overflow_score=overflow_score,
            rainfall_score=rainfall_score,
            vulnerability_score=vulnerability_score,
            vulnerability_available=has_vulnerability,
            dominant_risk_factor=dominant_factor,
            explanation=explanation,
            factor_breakdown=factor_breakdown,
            raw_inputs=raw_inputs,
        )
