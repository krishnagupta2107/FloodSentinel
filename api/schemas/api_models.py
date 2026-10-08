"""
Pydantic API request and response models for FloodSentinel.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ModelReadiness(BaseModel):
    rainfall: bool = Field(..., description="Whether the rainfall predictor models are loaded")
    overflow: bool = Field(..., description="Whether the overflow predictor models are loaded")
    fusion: bool = Field(..., description="Whether the multi-modal fusion engine is ready")


class HealthResponse(BaseModel):
    status: str = Field("ok", description="Overall API service status")
    service: str = Field("FloodSentinel API", description="Service name")
    version: str = Field("1.0.0", description="API version")
    models: ModelReadiness = Field(..., description="Readiness status of underlying ML models")


class RainfallPredictRequest(BaseModel):
    subdivision: str = Field(
        ...,
        description="Meteorological subdivision name (e.g. 'ANDAMAN & NICOBAR ISLANDS')",
        examples=["ANDAMAN & NICOBAR ISLANDS"],
    )
    target_month: int = Field(
        ...,
        ge=1,
        le=12,
        description="Target calendar month for rainfall prediction (1 to 12)",
        examples=[1],
    )
    rainfall_lags: List[float] = Field(
        ...,
        description="Previous 12 months historical rainfall sequence in mm, ordered [LAG_12, ..., LAG_1]",
        examples=[[10.0, 20.0, 15.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0]],
    )

    @field_validator("rainfall_lags")
    @classmethod
    def validate_rainfall_lags(cls, v: List[float]) -> List[float]:
        if len(v) != 12:
            raise ValueError(f"Exactly 12 monthly rainfall values required, got {len(v)}")
        for i, val in enumerate(v):
            if val < 0.0:
                raise ValueError(f"Rainfall lag value at index {i} cannot be negative: {val}")
        return v


class RainfallPredictResponse(BaseModel):
    subdivision: str = Field(..., description="Subdivision name")
    target_month: int = Field(..., description="Target calendar month")
    xgboost_prediction_mm: float = Field(..., description="Predicted rainfall in mm from XGBoost model")
    lstm_prediction_mm: float = Field(..., description="Predicted rainfall in mm from LSTM model")
    average_prediction_mm: float = Field(..., description="Ensemble average predicted rainfall in mm")


class OverflowTelemetryInput(BaseModel):
    water_level_cm: float = Field(..., ge=0.0, description="Current water level measured in catch basin (cm)", examples=[85.0])
    rise_rate_cm_per_15min: float = Field(..., description="Rate of water level rise in cm per 15 minutes", examples=[6.0])
    rainfall_mm_per_hr: float = Field(..., ge=0.0, description="Current localized rainfall intensity (mm/hr)", examples=[25.0])
    cumulative_rain_6hr_mm: float = Field(..., ge=0.0, description="Cumulative rainfall over past 6 hours (mm)", examples=[50.0])
    cumulative_rain_24hr_mm: float = Field(..., ge=0.0, description="Cumulative rainfall over past 24 hours (mm)", examples=[100.0])
    pipe_diameter_mm: float = Field(..., gt=0.0, description="Outflow drain pipe diameter in mm", examples=[600.0])
    pipe_material: str = Field(..., description="Pipe material (Cast Iron, Concrete, PVC)", examples=["Concrete"])
    pipe_slope: float = Field(..., ge=0.0, description="Pipe hydraulic gradient/slope", examples=[0.02])
    elevation_m: float = Field(..., description="Site topographic elevation above sea level in meters", examples=[10.0])
    month: int = Field(..., ge=1, le=12, description="Current calendar month (1 to 12)", examples=[7])

    @field_validator("pipe_material")
    @classmethod
    def validate_pipe_material(cls, v: str) -> str:
        valid = {"cast iron", "concrete", "pvc"}
        cleaned = v.strip().lower()
        if cleaned not in valid:
            raise ValueError(f"Invalid pipe_material '{v}'. Must be one of: Cast Iron, Concrete, PVC")
        mapping = {"cast iron": "Cast Iron", "concrete": "Concrete", "pvc": "PVC"}
        return mapping[cleaned]


class OverflowPredictResponse(BaseModel):
    overflow_probability_15min: float = Field(..., ge=0.0, le=1.0, description="Probability of overflow onset in next 15 minutes")
    overflow_probability_30min: float = Field(..., ge=0.0, le=1.0, description="Probability of overflow onset in next 30 minutes")
    overflow_score: float = Field(..., ge=0.0, le=1.0, description="Weighted composite overflow risk score")


class FusionWeightsInput(BaseModel):
    blockage_weight: float = Field(0.35, ge=0.0, description="Weight for CCTV grate blockage score")
    overflow_weight: float = Field(0.45, ge=0.0, description="Weight for sensor telemetry overflow score")
    rainfall_weight: float = Field(0.20, ge=0.0, description="Weight for forecasted rainfall risk score")
    vulnerability_weight: float = Field(0.00, ge=0.0, description="Weight for site vulnerability score (optional)")
    overflow_15min_weight: float = Field(0.65, ge=0.0, description="Weight for 15-min overflow horizon")
    overflow_30min_weight: float = Field(0.35, ge=0.0, description="Weight for 30-min overflow horizon")


class SiteAlertInput(BaseModel):
    site_id: str = Field(..., description="Unique drainage site identifier", examples=["SITE_001"])
    image_name: Optional[str] = Field(None, description="Associated CCTV inspection image filename")
    occlusion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Grate blockage occlusion percentage (0.0 - 100.0%)")
    overflow: Optional[OverflowTelemetryInput] = Field(None, description="Raw underground sensor telemetry readings")
    overflow_probability_15min: Optional[float] = Field(None, ge=0.0, le=1.0, description="Precomputed 15-min overflow probability")
    overflow_probability_30min: Optional[float] = Field(None, ge=0.0, le=1.0, description="Precomputed 30-min overflow probability")
    rainfall: Optional[RainfallPredictRequest] = Field(None, description="Raw meteorological rainfall forecast request")
    rainfall_prediction_mm: Optional[float] = Field(None, ge=0.0, description="Precomputed rainfall forecast in mm")
    vulnerability_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Optional site vulnerability index (0.0 to 1.0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata for the site")


class RankAlertsRequest(BaseModel):
    sites: List[SiteAlertInput] = Field(..., min_length=1, description="List of drainage sites to evaluate and rank")
    weights: Optional[FusionWeightsInput] = Field(None, description="Optional custom weights for multi-modal fusion")


class SiteRankOutput(BaseModel):
    rank: int = Field(..., description="Priority rank (1 = highest urgency)")
    site_id: str = Field(..., description="Unique site identifier")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Unified composite risk score (0.0 to 1.0)")
    risk_level: str = Field(..., description="Risk category: LOW, MEDIUM, HIGH, CRITICAL")
    image_name: Optional[str] = Field(None, description="Associated CCTV image name")
    occlusion_percentage: Optional[float] = Field(None, description="Raw grate blockage percentage")
    blockage_score: float = Field(..., ge=0.0, le=1.0, description="Normalized blockage score")
    overflow_probability_15min: Optional[float] = Field(None, description="15-minute overflow probability")
    overflow_probability_30min: Optional[float] = Field(None, description="30-minute overflow probability")
    overflow_score: float = Field(..., ge=0.0, le=1.0, description="Composite overflow score")
    rainfall_prediction_mm: Optional[float] = Field(None, description="Forecasted rainfall volume in mm")
    rainfall_score: float = Field(..., ge=0.0, le=1.0, description="Normalized empirical rainfall score")
    vulnerability_score: Optional[float] = Field(None, description="Vulnerability score if available")
    vulnerability_available: bool = Field(False, description="Whether vulnerability data was supplied")
    dominant_risk_factor: str = Field(..., description="Primary risk driver")
    explanation: str = Field(..., description="Automated natural-language summary")
    factor_breakdown: Dict[str, Any] = Field(default_factory=dict, description="Detailed score and weight contributions")


class RankAlertsResponse(BaseModel):
    total_sites: int = Field(..., description="Total number of evaluated drainage sites")
    ranked_sites: List[SiteRankOutput] = Field(..., description="Ranked list of drainage sites in descending risk order")


class DemoRiskResponse(BaseModel):
    is_demo_data: bool = Field(True, description="Flag indicating data is synthetic demonstration data")
    notice: str = Field(..., description="Data provenance clarification notice")
    total_sites: int = Field(..., description="Total demo sites evaluated")
    ranked_sites: List[SiteRankOutput] = Field(..., description="Ranked demo sites")
