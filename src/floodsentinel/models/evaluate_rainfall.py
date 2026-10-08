import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from xgboost import XGBRegressor
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)

TEST_DATA = os.path.join(BASE_DIR, "rainfall_test.csv")

XGB_MODEL = os.path.join(
    BASE_DIR, "models", "rainfall_xgboost.json"
)

LSTM_MODEL = os.path.join(
    BASE_DIR, "models", "rainfall_lstm.keras"
)

ENCODER = os.path.join(
    BASE_DIR, "models", "subdivision_encoder.pkl"
)

INPUT_SCALER = os.path.join(
    BASE_DIR, "models", "rainfall_lstm_input_scaler.pkl"
)

TARGET_SCALER = os.path.join(
    BASE_DIR, "models", "rainfall_lstm_scaler.pkl"
)

OUTPUT_DIR = os.path.join(BASE_DIR, "evaluation")


def metrics(actual, predicted):
    return {
        "MAE_mm": mean_absolute_error(actual, predicted),
        "RMSE_mm": np.sqrt(
            mean_squared_error(actual, predicted)
        ),
        "R2": r2_score(actual, predicted)
    }


def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading test data...")

    test = pd.read_csv(TEST_DATA)
    test["TARGET_DATE"] = pd.to_datetime(test["TARGET_DATE"])

    lag_cols = [
        f"LAG_{i}" for i in range(12, 0, -1)
    ]

    actual = test["TARGET_RAINFALL"].values

    # =========================
    # XGBoost
    # =========================

    print("Evaluating XGBoost...")

    encoder = joblib.load(ENCODER)

    test["MONTH"] = test["TARGET_DATE"].dt.month

    test["SUBDIVISION_ENCODED"] = encoder.transform(
        test["SUBDIVISION"]
    )

    xgb = XGBRegressor()
    xgb.load_model(XGB_MODEL)

    xgb_features = lag_cols + [
        "MONTH",
        "SUBDIVISION_ENCODED"
    ]

    xgb_pred = xgb.predict(
        test[xgb_features]
    )

    xgb_pred = np.maximum(xgb_pred, 0)

    xgb_result = metrics(actual, xgb_pred)

    # =========================
    # LSTM
    # =========================

    print("Evaluating LSTM...")

    input_scaler = joblib.load(INPUT_SCALER)
    target_scaler = joblib.load(TARGET_SCALER)

    lstm = load_model(LSTM_MODEL)

    lstm_input = test[lag_cols].values

    lstm_input = input_scaler.transform(
        lstm_input
    )

    lstm_input = lstm_input.reshape(
        -1, 12, 1
    )

    lstm_pred_scaled = lstm.predict(
        lstm_input,
        verbose=0
    )

    lstm_pred = target_scaler.inverse_transform(
        lstm_pred_scaled
    ).ravel()

    lstm_pred = np.maximum(lstm_pred, 0)

    lstm_result = metrics(actual, lstm_pred)

    # =========================
    # Save metrics
    # =========================

    results = pd.DataFrame([
        {
            "Model": "XGBoost",
            **xgb_result
        },
        {
            "Model": "LSTM",
            **lstm_result
        }
    ])

    results.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "rainfall_model_metrics.csv"
        ),
        index=False
    )

    # =========================
    # Save predictions
    # =========================

    predictions = pd.DataFrame({
        "SUBDIVISION": test["SUBDIVISION"],
        "TARGET_DATE": test["TARGET_DATE"],
        "ACTUAL_RAINFALL_MM": actual,
        "XGBOOST_PREDICTION_MM": xgb_pred,
        "LSTM_PREDICTION_MM": lstm_pred,
        "AVERAGE_PREDICTION_MM":
            (xgb_pred + lstm_pred) / 2
    })

    predictions.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "rainfall_predictions.csv"
        ),
        index=False
    )

    # =========================
    # Comparison plot
    # =========================

    sample = min(500, len(test))

    plt.figure(figsize=(12, 6))

    plt.plot(
        actual[:sample],
        label="Actual"
    )

    plt.plot(
        xgb_pred[:sample],
        label="XGBoost"
    )

    plt.plot(
        lstm_pred[:sample],
        label="LSTM"
    )

    plt.title(
        "Rainfall Forecasting Evaluation"
    )

    plt.xlabel("Test Samples")
    plt.ylabel("Rainfall (mm)")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "rainfall_prediction_comparison.png"
        ),
        dpi=150
    )

    plt.close()

    # =========================
    # Print results
    # =========================

    print("\n================================")
    print("   RAINFALL MODEL EVALUATION")
    print("================================")

    print("\nXGBoost")
    print(f"MAE  : {xgb_result['MAE_mm']:.4f} mm")
    print(f"RMSE : {xgb_result['RMSE_mm']:.4f} mm")
    print(f"R2   : {xgb_result['R2']:.4f}")

    print("\nLSTM")
    print(f"MAE  : {lstm_result['MAE_mm']:.4f} mm")
    print(f"RMSE : {lstm_result['RMSE_mm']:.4f} mm")
    print(f"R2   : {lstm_result['R2']:.4f}")

    better = (
        "XGBoost"
        if xgb_result["MAE_mm"] < lstm_result["MAE_mm"]
        else "LSTM"
    )

    print(f"\nBetter model by MAE: {better}")

    print("\nSaved evaluation files:")
    print("evaluation/rainfall_model_metrics.csv")
    print("evaluation/rainfall_predictions.csv")
    print("evaluation/rainfall_prediction_comparison.png")


if __name__ == "__main__":
    main()
