"""
Rainfall to risk normalization module.
Transforms forecasted rainfall volume (in millimeters) into a bounded,
statistically calibrated risk score in [0.0, 1.0].
"""

import os
from typing import Optional, Union, Sequence
import numpy as np
import pandas as pd


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)
DEFAULT_HISTORICAL_DATA = os.path.join(BASE_DIR, "rainfall_monthly.csv")


class RainfallNormalizer:
    """
    Normalizes forecasted rainfall (mm) into a continuous risk score [0.0, 1.0]
    using the historical empirical distribution from the dataset.
    """

    def __init__(
        self,
        historical_csv_path: Optional[str] = DEFAULT_HISTORICAL_DATA,
        historical_values: Optional[Sequence[float]] = None,
    ):
        self.quantiles = None
        self.quantile_values = None
        self._load_distribution(historical_csv_path, historical_values)

    def _load_distribution(
        self,
        historical_csv_path: Optional[str],
        historical_values: Optional[Sequence[float]],
    ):
        data = None
        if historical_values is not None and len(historical_values) > 0:
            data = np.asarray(historical_values, dtype=float)
        elif historical_csv_path and os.path.exists(historical_csv_path):
            try:
                df = pd.read_csv(historical_csv_path)
                if "RAINFALL" in df.columns:
                    data = df["RAINFALL"].dropna().values
                elif "TARGET_RAINFALL" in df.columns:
                    data = df["TARGET_RAINFALL"].dropna().values
            except Exception:
                data = None

        if data is not None and len(data) > 0:
            # Precompute 1000 quantiles from 0.0 to 1.0 for fast O(log N) lookup
            self.quantiles = np.linspace(0.0, 1.0, 1001)
            self.quantile_values = np.quantile(data, self.quantiles)
        else:
            # Fallback calibrated to India Meteorological Department (IMD) monthly rainfall distribution:
            # 0mm -> 0.0, 40mm (median) -> 0.50, 160mm (75th) -> 0.75, 350mm (90th) -> 0.90, 600mm -> 0.98
            self.quantiles = np.array([0.0, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1.0])
            self.quantile_values = np.array([0.0, 0.2, 5.0, 41.4, 166.4, 335.9, 450.8, 831.7, 2362.8])

    def normalize(self, rainfall_mm: Union[float, int, None]) -> float:
        """
        Converts rainfall mm to a normalized risk score between 0.0 and 1.0.
        """
        if rainfall_mm is None:
            return 0.0

        try:
            val = float(rainfall_mm)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid rainfall input: {rainfall_mm}")

        if np.isnan(val) or val <= 0.0:
            return 0.0

        if val >= self.quantile_values[-1]:
            return 1.0

        # Empirical CDF interpolation
        score = np.interp(val, self.quantile_values, self.quantiles)
        return float(np.clip(score, 0.0, 1.0))

    def __call__(self, rainfall_mm: Union[float, int, None]) -> float:
        return self.normalize(rainfall_mm)
