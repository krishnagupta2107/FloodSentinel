"""
Sensor-based overflow prediction wrapper.
Loads the trained 15-minute and 30-minute XGBoost overflow onset models.
"""

import os
import joblib
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)

MODEL_15MIN_PATH = os.path.join(BASE_DIR, "models", "xgboost_overflow_15min.pkl")
MODEL_30MIN_PATH = os.path.join(BASE_DIR, "models", "xgboost_overflow_30min.pkl")
PIPE_ENCODER_PATH = os.path.join(BASE_DIR, "models", "pipe_material_encoder.pkl")
FEATURE_COLUMNS_PATH = os.path.join(BASE_DIR, "models", "feature_columns.pkl")


class OverflowPredictor:
    """
    Interface for the underground sensor telemetry XGBoost overflow models.
    Produces predicted overflow onset probabilities for 15-min and 30-min horizons.
    """

    NUMERIC_FEATURES = [
        "water_level_cm",
        "rise_rate_cm_per_15min",
        "rainfall_mm_per_hr",
        "cumulative_rain_6hr_mm",
        "cumulative_rain_24hr_mm",
        "pipe_diameter_mm",
        "pipe_slope",
        "elevation_m",
        "month",
    ]

    def __init__(
        self,
        model_15min_path: str = MODEL_15MIN_PATH,
        model_30min_path: str = MODEL_30MIN_PATH,
        pipe_encoder_path: str = PIPE_ENCODER_PATH,
        feature_columns_path: str = FEATURE_COLUMNS_PATH,
    ):
        self.model_15min = joblib.load(model_15min_path)
        self.model_30min = joblib.load(model_30min_path)
        self.pipe_encoder = joblib.load(pipe_encoder_path)

        if os.path.exists(feature_columns_path):
            self.feature_columns = joblib.load(feature_columns_path)
        else:
            self.feature_columns = self.NUMERIC_FEATURES + [
                "pipe_material_Cast Iron",
                "pipe_material_Concrete",
                "pipe_material_PVC",
            ]

    def _build_feature_vector(self, telemetry: Dict[str, Any]) -> np.ndarray:
        """
        Extracts and aligns features into the exact 12-dimensional vector expected by XGBoost.
        """
        numeric_vals = []
        for feat in self.NUMERIC_FEATURES:
            val = telemetry.get(feat, 0.0)
            try:
                numeric_vals.append(float(val))
            except (ValueError, TypeError):
                numeric_vals.append(0.0)

        numeric_arr = np.array(numeric_vals, dtype=float).reshape(1, -1)

        # Encode pipe material
        pipe_mat = str(telemetry.get("pipe_material", "Concrete"))
        pipe_input = pd.DataFrame([{"pipe_material": pipe_mat}])
        try:
            pipe_encoded = self.pipe_encoder.transform(pipe_input)
        except Exception:
            # Fallback if unknown
            pipe_encoded = np.zeros((1, 3))

        feature_matrix = np.hstack([numeric_arr, pipe_encoded])
        return feature_matrix

    def predict_proba(
        self, telemetry: Dict[str, Any]
    ) -> Tuple[float, float]:
        """
        Returns (prob_15min, prob_30min) for a single sensor telemetry reading.
        """
        X = self._build_feature_vector(telemetry)
        p15 = float(self.model_15min.predict_proba(X)[0, 1])
        p30 = float(self.model_30min.predict_proba(X)[0, 1])
        return (np.clip(p15, 0.0, 1.0), np.clip(p30, 0.0, 1.0))

    def predict_batch(
        self, records: List[Dict[str, Any]]
    ) -> List[Tuple[float, float]]:
        """
        Batch prediction for multiple telemetry readings.
        """
        if not records:
            return []
        matrices = [self._build_feature_vector(rec) for rec in records]
        X = np.vstack(matrices)
        p15_all = self.model_15min.predict_proba(X)[:, 1]
        p30_all = self.model_30min.predict_proba(X)[:, 1]
        return [
            (float(np.clip(p15, 0.0, 1.0)), float(np.clip(p30, 0.0, 1.0)))
            for p15, p30 in zip(p15_all, p30_all)
        ]
