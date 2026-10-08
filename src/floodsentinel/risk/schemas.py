"""
Risk data schemas, thresholds, weights, and data containers.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskThresholds:
    """Configurable risk level boundaries."""
    low_cutoff: float = 0.30
    medium_cutoff: float = 0.60
    high_cutoff: float = 0.80

    def get_level(self, score: float) -> RiskLevel:
        if score < self.low_cutoff:
            return RiskLevel.LOW
        elif score < self.medium_cutoff:
            return RiskLevel.MEDIUM
        elif score < self.high_cutoff:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL


@dataclass
class FusionWeights:
    """
    Configurable weights for risk fusion.
    
    Default weights:
      - blockage_weight: 0.35 (visual drainage obstruction)
      - overflow_weight: 0.45 (sensor telemetry overflow probability)
      - rainfall_weight: 0.20 (forecasted rainfall intensity/volume)
      - vulnerability_weight: 0.00 (optional physical/population vulnerability)
      
    For the overflow sub-model:
      - overflow_15min_weight: 0.65 (immediate 15-minute lead time)
      - overflow_30min_weight: 0.35 (extended 30-minute lead time)
    """
    blockage_weight: float = 0.35
    overflow_weight: float = 0.45
    rainfall_weight: float = 0.20
    vulnerability_weight: float = 0.00
    overflow_15min_weight: float = 0.65
    overflow_30min_weight: float = 0.35

    def __post_init__(self):
        self.validate()

    def validate(self):
        for name, w in [
            ("blockage_weight", self.blockage_weight),
            ("overflow_weight", self.overflow_weight),
            ("rainfall_weight", self.rainfall_weight),
            ("vulnerability_weight", self.vulnerability_weight),
            ("overflow_15min_weight", self.overflow_15min_weight),
            ("overflow_30min_weight", self.overflow_30min_weight),
        ]:
            if w < 0.0:
                raise ValueError(f"Weight {name} cannot be negative (got {w})")

        overflow_sub_sum = self.overflow_15min_weight + self.overflow_30min_weight
        if not (0.99 <= overflow_sub_sum <= 1.01):
            raise ValueError(
                f"Overflow sub-weights must sum to 1.0 (got {overflow_sub_sum})"
            )

    def normalized_weights(self, has_vulnerability: bool = False) -> Dict[str, float]:
        """
        Dynamically normalizes active weights so their sum is exactly 1.0.
        """
        raw_weights = {
            "blockage": self.blockage_weight,
            "overflow": self.overflow_weight,
            "rainfall": self.rainfall_weight,
        }
        if has_vulnerability and self.vulnerability_weight > 0.0:
            raw_weights["vulnerability"] = self.vulnerability_weight

        total = sum(raw_weights.values())
        if total <= 0:
            raise ValueError("Sum of active weights must be positive.")

        return {k: v / total for k, v in raw_weights.items()}


@dataclass
class SiteInput:
    """
    Common data contract for site risk evaluation.
    """
    site_id: str
    image_name: Optional[str] = None
    occlusion_percentage: Optional[float] = None
    overflow_probability_15min: Optional[float] = None
    overflow_probability_30min: Optional[float] = None
    rainfall_prediction_mm: Optional[float] = None
    vulnerability_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SiteInput":
        return cls(
            site_id=str(data.get("site_id", "UNKNOWN")),
            image_name=data.get("image_name"),
            occlusion_percentage=data.get("occlusion_percentage"),
            overflow_probability_15min=data.get("overflow_probability_15min"),
            overflow_probability_30min=data.get("overflow_probability_30min"),
            rainfall_prediction_mm=data.get("rainfall_prediction_mm"),
            vulnerability_score=data.get("vulnerability_score"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SiteRiskResult:
    """
    Comprehensive risk scoring and explanation for a drainage site.
    """
    site_id: str
    risk_score: float
    risk_level: RiskLevel
    rank: int = 0
    image_name: Optional[str] = None
    blockage_score: float = 0.0
    overflow_score: float = 0.0
    rainfall_score: float = 0.0
    vulnerability_score: Optional[float] = None
    vulnerability_available: bool = False
    dominant_risk_factor: str = ""
    explanation: str = ""
    factor_breakdown: Dict[str, Any] = field(default_factory=dict)
    raw_inputs: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "site_id": self.site_id,
            "risk_score": round(self.risk_score, 4),
            "risk_level": self.risk_level.value,
            "image_name": self.image_name,
            "blockage_score": round(self.blockage_score, 4),
            "overflow_score": round(self.overflow_score, 4),
            "rainfall_score": round(self.rainfall_score, 4),
            "vulnerability_score": (
                round(self.vulnerability_score, 4)
                if self.vulnerability_score is not None
                else None
            ),
            "vulnerability_available": self.vulnerability_available,
            "dominant_risk_factor": self.dominant_risk_factor,
            "explanation": self.explanation,
            "factor_breakdown": self.factor_breakdown,
            "raw_inputs": self.raw_inputs,
        }
