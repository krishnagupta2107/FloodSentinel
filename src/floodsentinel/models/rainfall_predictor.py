import os
import joblib
import numpy as np
from xgboost import XGBRegressor
from tensorflow.keras.models import load_model


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)


# =========================================================
# MODEL PATHS
# =========================================================

XGB_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "rainfall_xgboost.json"
)

LSTM_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "rainfall_lstm.keras"
)


# XGBoost subdivision encoder
XGB_SUBDIVISION_ENCODER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "subdivision_encoder.pkl"
)


# Subdivision-aware LSTM files
LSTM_INPUT_SCALER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "rainfall_lstm_subdivision_input_scaler.pkl"
)

LSTM_TARGET_SCALER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "rainfall_lstm_subdivision_target_scaler.pkl"
)

LSTM_SUBDIVISION_ENCODER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "rainfall_lstm_subdivision_encoder.pkl"
)


class RainfallPredictor:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        # -------------------------------------------------
        # Load XGBoost
        # -------------------------------------------------

        self.xgb_model = XGBRegressor()

        self.xgb_model.load_model(
            XGB_MODEL_PATH
        )

        # -------------------------------------------------
        # Load XGBoost subdivision encoder
        # -------------------------------------------------

        self.xgb_subdivision_encoder = joblib.load(
            XGB_SUBDIVISION_ENCODER_PATH
        )

        # -------------------------------------------------
        # Load subdivision-aware LSTM
        # -------------------------------------------------

        self.lstm_model = load_model(
            LSTM_MODEL_PATH
        )

        # -------------------------------------------------
        # LSTM input scaler
        #
        # IMPORTANT:
        # This scaler was trained on 12 rainfall values.
        # It must NOT receive the 3-feature sequence.
        # -------------------------------------------------

        self.lstm_input_scaler = joblib.load(
            LSTM_INPUT_SCALER_PATH
        )

        # -------------------------------------------------
        # LSTM target scaler
        # -------------------------------------------------

        self.lstm_target_scaler = joblib.load(
            LSTM_TARGET_SCALER_PATH
        )

        # -------------------------------------------------
        # LSTM subdivision encoder
        # -------------------------------------------------

        self.lstm_subdivision_encoder = joblib.load(
            LSTM_SUBDIVISION_ENCODER_PATH
        )

    # =====================================================
    # VALIDATION
    # =====================================================

    @staticmethod
    def _validate_rainfall_input(
        previous_12_months
    ):

        values = np.asarray(
            previous_12_months,
            dtype=float
        ).reshape(-1)

        if len(values) != 12:
            raise ValueError(
                "Exactly 12 previous months are required."
            )

        if not np.all(
            np.isfinite(values)
        ):
            raise ValueError(
                "Rainfall values must contain only "
                "finite numbers."
            )

        return values

    @staticmethod
    def _validate_target_month(
        target_month
    ):

        target_month = int(
            target_month
        )

        if target_month < 1 or target_month > 12:
            raise ValueError(
                "target_month must be between 1 and 12."
            )

        return target_month

    # =====================================================
    # MONTH FEATURES
    # =====================================================

    @staticmethod
    def _month_features(month):

        month = int(month)

        angle = (
            2.0
            * np.pi
            * month
            / 12.0
        )

        return (
            np.sin(angle),
            np.cos(angle)
        )

    # =====================================================
    # PREVIOUS MONTH NUMBERS
    # =====================================================

    @staticmethod
    def _previous_months(
        target_month
    ):

        months = []

        for lag in range(12, 0, -1):

            month = (
                (target_month - lag - 1)
                % 12
            ) + 1

            months.append(month)

        return months

    # =====================================================
    # XGBOOST SUBDIVISION ENCODING
    # =====================================================

    def _encode_xgb_subdivision(
        self,
        subdivision
    ):

        try:

            return (
                self.xgb_subdivision_encoder
                .transform([subdivision])[0]
            )

        except ValueError:

            raise ValueError(
                f"Unknown subdivision: {subdivision}"
            )

    # =====================================================
    # LSTM SUBDIVISION ENCODING
    # =====================================================

    def _encode_lstm_subdivision(
        self,
        subdivision
    ):

        try:

            return (
                self.lstm_subdivision_encoder
                .transform([subdivision])[0]
            )

        except ValueError:

            raise ValueError(
                f"Unknown subdivision: {subdivision}"
            )

    # =====================================================
    # XGBOOST FEATURES
    # =====================================================

    def _build_xgboost_features(
        self,
        previous_12_months,
        subdivision,
        target_month
    ):

        values = self._validate_rainfall_input(
            previous_12_months
        )

        target_month = self._validate_target_month(
            target_month
        )

        subdivision_encoded = (
            self._encode_xgb_subdivision(
                subdivision
            )
        )

        # -------------------------------------------------
        # LAG FEATURES
        #
        # values:
        # LAG_12 ... LAG_1
        # -------------------------------------------------

        lag_features = {}

        for index, value in enumerate(values):

            lag = 12 - index

            lag_features[
                f"LAG_{lag}"
            ] = value

        # -------------------------------------------------
        # Rolling features
        # -------------------------------------------------

        rolling_3 = np.mean(
            values[-3:]
        )

        rolling_6 = np.mean(
            values[-6:]
        )

        rolling_12 = np.mean(
            values
        )

        # -------------------------------------------------
        # Recent changes
        # -------------------------------------------------

        lag_1 = values[-1]
        lag_2 = values[-2]
        lag_4 = values[-4]

        recent_change = (
            lag_1 - lag_2
        )

        recent_3_change = (
            lag_1 - lag_4
        )

        # -------------------------------------------------
        # Seasonal features
        # -------------------------------------------------

        month_sin, month_cos = (
            self._month_features(
                target_month
            )
        )

        # -------------------------------------------------
        # Complete feature dictionary
        # -------------------------------------------------

        features = {

            **lag_features,

            "ROLLING_3": rolling_3,
            "ROLLING_6": rolling_6,
            "ROLLING_12": rolling_12,

            "RECENT_CHANGE": recent_change,
            "RECENT_3_CHANGE": recent_3_change,

            "SAME_MONTH_LAST_YEAR": values[0],

            "MONTH_SIN": month_sin,
            "MONTH_COS": month_cos,

            "MONTH": target_month,

            "SUBDIVISION_ENCODED":
                subdivision_encoded
        }

        return features

    # =====================================================
    # XGBOOST PREDICTION
    # =====================================================

    def predict_xgboost(
        self,
        previous_12_months,
        subdivision,
        target_month
    ):

        features = self._build_xgboost_features(
            previous_12_months,
            subdivision,
            target_month
        )

        booster = (
            self.xgb_model.get_booster()
        )

        model_feature_names = (
            booster.feature_names
        )

        if model_feature_names is not None:

            missing_features = [
                name
                for name in model_feature_names
                if name not in features
            ]

            if missing_features:

                raise RuntimeError(
                    "XGBoost model expects missing "
                    f"features: {missing_features}"
                )

            feature_vector = [
                features[name]
                for name in model_feature_names
            ]

        else:

            feature_vector = []

            for lag in range(12, 0, -1):

                feature_vector.append(
                    features[
                        f"LAG_{lag}"
                    ]
                )

            feature_vector.extend([
                features["ROLLING_3"],
                features["ROLLING_6"],
                features["ROLLING_12"],
                features["RECENT_CHANGE"],
                features["RECENT_3_CHANGE"],
                features["SAME_MONTH_LAST_YEAR"],
                features["MONTH_SIN"],
                features["MONTH_COS"],
                features["MONTH"],
                features["SUBDIVISION_ENCODED"]
            ])

        feature_array = np.asarray(
            feature_vector,
            dtype=float
        ).reshape(1, -1)

        prediction = (
            self.xgb_model.predict(
                feature_array
            )[0]
        )

        return max(
            0.0,
            float(prediction)
        )

    # =====================================================
    # LSTM SEQUENCE
    # =====================================================

    def _build_lstm_sequence(
        self,
        previous_12_months,
        target_month
    ):

        values = self._validate_rainfall_input(
            previous_12_months
        )

        target_month = self._validate_target_month(
            target_month
        )

        # -------------------------------------------------
        # STEP 1
        #
        # Scale the 12 rainfall values.
        #
        # The saved scaler expects exactly 12 features.
        # -------------------------------------------------

        rainfall_matrix = values.reshape(
            1,
            12
        )

        scaled_rainfall = (
            self.lstm_input_scaler.transform(
                rainfall_matrix
            )
        )

        scaled_rainfall = (
            scaled_rainfall.reshape(12)
        )

        # -------------------------------------------------
        # STEP 2
        #
        # Determine calendar month for each lag.
        # -------------------------------------------------

        sequence_months = (
            self._previous_months(
                target_month
            )
        )

        # -------------------------------------------------
        # STEP 3
        #
        # Build:
        #
        # rainfall + month_sin + month_cos
        #
        # Shape = (12, 3)
        # -------------------------------------------------

        sequence = []

        for rainfall, month in zip(
            scaled_rainfall,
            sequence_months
        ):

            month_sin, month_cos = (
                self._month_features(
                    month
                )
            )

            sequence.append([
                rainfall,
                month_sin,
                month_cos
            ])

        return np.asarray(
            sequence,
            dtype=np.float32
        )

    # =====================================================
    # LSTM PREDICTION
    # =====================================================

    def predict_lstm(
        self,
        previous_12_months,
        subdivision,
        target_month
    ):

        # -------------------------------------------------
        # Build sequence
        # -------------------------------------------------

        sequence = (
            self._build_lstm_sequence(
                previous_12_months,
                target_month
            )
        )

        # -------------------------------------------------
        # Add batch dimension
        #
        # (12, 3)
        # ->
        # (1, 12, 3)
        # -------------------------------------------------

        rainfall_sequence = (
            sequence.reshape(
                1,
                12,
                3
            )
        )

        # -------------------------------------------------
        # Encode subdivision
        # -------------------------------------------------

        subdivision_encoded = (
            self._encode_lstm_subdivision(
                subdivision
            )
        )

        subdivision_input = np.asarray(
            [subdivision_encoded],
            dtype=np.int32
        )

        # -------------------------------------------------
        # Predict
        # -------------------------------------------------

        prediction_scaled = (
            self.lstm_model.predict(
                [
                    rainfall_sequence,
                    subdivision_input
                ],
                verbose=0
            )
        )

        # -------------------------------------------------
        # Convert back to rainfall mm
        # -------------------------------------------------

        prediction = (
            self.lstm_target_scaler
            .inverse_transform(
                np.asarray(
                    prediction_scaled
                ).reshape(-1, 1)
            )[0][0]
        )

        return max(
            0.0,
            float(prediction)
        )

    # =====================================================
    # COMBINED PREDICTION
    # =====================================================

    def predict(
        self,
        previous_12_months,
        subdivision,
        target_month
    ):

        xgb_prediction = (
            self.predict_xgboost(
                previous_12_months,
                subdivision,
                target_month
            )
        )

        lstm_prediction = (
            self.predict_lstm(
                previous_12_months,
                subdivision,
                target_month
            )
        )

        average_prediction = (
            xgb_prediction
            + lstm_prediction
        ) / 2.0

        return {

            "subdivision": subdivision,

            "target_month": int(
                target_month
            ),

            "xgboost_prediction_mm": round(
                xgb_prediction,
                2
            ),

            "lstm_prediction_mm": round(
                lstm_prediction,
                2
            ),

            "average_prediction_mm": round(
                average_prediction,
                2
            )
        }