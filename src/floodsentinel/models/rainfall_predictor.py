import os

import joblib
import numpy as np
from tensorflow.keras.models import load_model
from xgboost import XGBRegressor

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

XGB_MODEL_PATH = os.path.join(BASE_DIR, "models", "rainfall_xgboost.json")

LSTM_MODEL_PATH = os.path.join(BASE_DIR, "models", "rainfall_lstm.keras")

LSTM_INPUT_SCALER_PATH = os.path.join(
    BASE_DIR, "models", "rainfall_lstm_input_scaler.pkl"
)

LSTM_TARGET_SCALER_PATH = os.path.join(BASE_DIR, "models", "rainfall_lstm_scaler.pkl")

SUBDIVISION_ENCODER_PATH = os.path.join(BASE_DIR, "models", "subdivision_encoder.pkl")


class RainfallPredictor:

    def __init__(self):
        self.xgb_model = XGBRegressor()
        self.xgb_model.load_model(XGB_MODEL_PATH)

        self.lstm_model = load_model(LSTM_MODEL_PATH)

        self.input_scaler = joblib.load(LSTM_INPUT_SCALER_PATH)

        self.target_scaler = joblib.load(LSTM_TARGET_SCALER_PATH)

        self.subdivision_encoder = joblib.load(SUBDIVISION_ENCODER_PATH)

    def predict_xgboost(self, previous_12_months, subdivision, target_month):
        values = np.array(previous_12_months).reshape(1, -1)

        if values.shape[1] != 12:
            raise ValueError("Exactly 12 previous months are required.")

        try:
            subdivision_encoded = self.subdivision_encoder.transform([subdivision])[0]
        except ValueError:
            raise ValueError(f"Unknown subdivision: {subdivision}")

        features = np.column_stack([values, [[target_month, subdivision_encoded]]])

        prediction = self.xgb_model.predict(features)[0]

        return max(0.0, float(prediction))

    def predict_lstm(self, previous_12_months):
        values = np.array(previous_12_months).reshape(1, -1)

        if values.shape[1] != 12:
            raise ValueError("Exactly 12 previous months are required.")

        scaled = self.input_scaler.transform(values)

        sequence = scaled.reshape(1, 12, 1)

        prediction_scaled = self.lstm_model.predict(sequence, verbose=0)

        prediction = self.target_scaler.inverse_transform(prediction_scaled)[0][0]

        return max(0.0, float(prediction))

    def predict(self, previous_12_months, subdivision, target_month):
        xgb_prediction = self.predict_xgboost(
            previous_12_months, subdivision, target_month
        )

        lstm_prediction = self.predict_lstm(previous_12_months)

        return {
            "subdivision": subdivision,
            "target_month": target_month,
            "xgboost_prediction_mm": round(xgb_prediction, 2),
            "lstm_prediction_mm": round(lstm_prediction, 2),
            "average_prediction_mm": round((xgb_prediction + lstm_prediction) / 2, 2),
        }
