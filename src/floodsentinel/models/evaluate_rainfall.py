import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from src.floodsentinel.models.rainfall_predictor import (
    RainfallPredictor
)


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)

TEST_DATA = os.path.join(
    BASE_DIR,
    "rainfall_test.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "evaluation"
)


def calculate_metrics(actual, predicted):

    return {
        "MAE_mm": mean_absolute_error(
            actual,
            predicted
        ),

        "RMSE_mm": np.sqrt(
            mean_squared_error(
                actual,
                predicted
            )
        ),

        "R2": r2_score(
            actual,
            predicted
        )
    }


def main():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    print("Loading test data...")

    test = pd.read_csv(
        TEST_DATA
    )

    test["TARGET_DATE"] = pd.to_datetime(
        test["TARGET_DATE"]
    )

    print("Loading RainfallPredictor...")

    predictor = RainfallPredictor()

    actual = []
    xgb_predictions = []
    lstm_predictions = []
    average_predictions = []

    subdivisions = []
    target_dates = []

    print()
    print(
        f"Evaluating {len(test)} test samples..."
    )
    print()

    for index, row in test.iterrows():

        lag_values = [
            float(
                row[f"LAG_{i}"]
            )
            for i in range(12, 0, -1)
        ]

        subdivision = row[
            "SUBDIVISION"
        ]

        target_date = row[
            "TARGET_DATE"
        ]

        target_month = int(
            target_date.month
        )

        result = predictor.predict(
            lag_values,
            subdivision,
            target_month
        )

        actual.append(
            float(
                row[
                    "TARGET_RAINFALL"
                ]
            )
        )

        xgb_predictions.append(
            result[
                "xgboost_prediction_mm"
            ]
        )

        lstm_predictions.append(
            result[
                "lstm_prediction_mm"
            ]
        )

        average_predictions.append(
            result[
                "average_prediction_mm"
            ]
        )

        subdivisions.append(
            subdivision
        )

        target_dates.append(
            target_date
        )

        if (
            index + 1
        ) % 1000 == 0:

            print(
                f"Processed "
                f"{index + 1}/"
                f"{len(test)} samples..."
            )

    actual = np.asarray(
        actual,
        dtype=float
    )

    xgb_predictions = np.asarray(
        xgb_predictions,
        dtype=float
    )

    lstm_predictions = np.asarray(
        lstm_predictions,
        dtype=float
    )

    average_predictions = np.asarray(
        average_predictions,
        dtype=float
    )

    # =====================================================
    # METRICS
    # =====================================================

    xgb_result = calculate_metrics(
        actual,
        xgb_predictions
    )

    lstm_result = calculate_metrics(
        actual,
        lstm_predictions
    )

    average_result = calculate_metrics(
        actual,
        average_predictions
    )

    results = pd.DataFrame([
        {
            "Model": "XGBoost",
            **xgb_result
        },
        {
            "Model": "LSTM",
            **lstm_result
        },
        {
            "Model": "XGBoost + LSTM Average",
            **average_result
        }
    ])

    # =====================================================
    # SAVE METRICS
    # =====================================================

    metrics_path = os.path.join(
        OUTPUT_DIR,
        "rainfall_model_metrics.csv"
    )

    results.to_csv(
        metrics_path,
        index=False
    )

    # =====================================================
    # SAVE PREDICTIONS
    # =====================================================

    predictions = pd.DataFrame({

        "SUBDIVISION":
            subdivisions,

        "TARGET_DATE":
            target_dates,

        "ACTUAL_RAINFALL_MM":
            actual,

        "XGBOOST_PREDICTION_MM":
            xgb_predictions,

        "LSTM_PREDICTION_MM":
            lstm_predictions,

        "AVERAGE_PREDICTION_MM":
            average_predictions
    })

    predictions_path = os.path.join(
        OUTPUT_DIR,
        "rainfall_predictions.csv"
    )

    predictions.to_csv(
        predictions_path,
        index=False
    )

    # =====================================================
    # PLOT
    # =====================================================

    sample = min(
        500,
        len(test)
    )

    plt.figure(
        figsize=(12, 6)
    )

    plt.plot(
        actual[:sample],
        label="Actual"
    )

    plt.plot(
        xgb_predictions[:sample],
        label="XGBoost"
    )

    plt.plot(
        lstm_predictions[:sample],
        label="LSTM"
    )

    plt.plot(
        average_predictions[:sample],
        label="XGBoost + LSTM"
    )

    plt.title(
        "Rainfall Forecasting Evaluation"
    )

    plt.xlabel(
        "Test Samples"
    )

    plt.ylabel(
        "Rainfall (mm)"
    )

    plt.legend()

    plt.tight_layout()

    plot_path = os.path.join(
        OUTPUT_DIR,
        "rainfall_prediction_comparison.png"
    )

    plt.savefig(
        plot_path,
        dpi=150
    )

    plt.close()

    # =====================================================
    # PRINT RESULTS
    # =====================================================

    print()
    print("=" * 70)
    print("FINAL RAINFALL MODEL EVALUATION")
    print("=" * 70)

    print()

    print(
        f"XGBoost              | "
        f"MAE: {xgb_result['MAE_mm']:.4f} | "
        f"RMSE: {xgb_result['RMSE_mm']:.4f} | "
        f"R2: {xgb_result['R2']:.4f}"
    )

    print(
        f"LSTM                 | "
        f"MAE: {lstm_result['MAE_mm']:.4f} | "
        f"RMSE: {lstm_result['RMSE_mm']:.4f} | "
        f"R2: {lstm_result['R2']:.4f}"
    )

    print(
        f"XGB + LSTM Average   | "
        f"MAE: {average_result['MAE_mm']:.4f} | "
        f"RMSE: {average_result['RMSE_mm']:.4f} | "
        f"R2: {average_result['R2']:.4f}"
    )

    print()

    print(
        "Metrics saved:",
        metrics_path
    )

    print(
        "Predictions saved:",
        predictions_path
    )

    print(
        "Plot saved:",
        plot_path
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
