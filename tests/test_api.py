"""
API test suite for FloodSentinel FastAPI backend using TestClient.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestHealthEndpoints:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "FloodSentinel API"
        assert data["status"] == "running"
        assert "/docs" in data["documentation"]

    def test_health_endpoint(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["ok", "degraded"]
        assert "models" in data
        assert isinstance(data["models"]["rainfall"], bool)
        assert isinstance(data["models"]["overflow"], bool)
        assert isinstance(data["models"]["fusion"], bool)


class TestRainfallPredictEndpoint:
    @pytest.fixture
    def valid_rainfall_payload(self):
        return {
            "subdivision": "ANDAMAN & NICOBAR ISLANDS",
            "target_month": 1,
            "rainfall_lags": [10.0, 20.0, 15.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0],
        }

    def test_valid_rainfall_prediction(self, valid_rainfall_payload):
        response = client.post("/api/risk/predict", json=valid_rainfall_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["subdivision"] == "ANDAMAN & NICOBAR ISLANDS"
        assert data["target_month"] == 1
        assert data["xgboost_prediction_mm"] >= 0.0
        assert data["lstm_prediction_mm"] >= 0.0
        assert data["average_prediction_mm"] >= 0.0

    def test_invalid_sequence_length(self, valid_rainfall_payload):
        valid_rainfall_payload["rainfall_lags"] = [10.0, 20.0, 30.0]  # Only 3 values instead of 12
        response = client.post("/api/risk/predict", json=valid_rainfall_payload)
        assert response.status_code == 422
        data = response.json()
        assert "Validation Error" in str(data) or "error" in str(data)

    def test_invalid_month(self, valid_rainfall_payload):
        valid_rainfall_payload["target_month"] = 13  # Invalid month
        response = client.post("/api/risk/predict", json=valid_rainfall_payload)
        assert response.status_code == 422

    def test_unknown_subdivision(self, valid_rainfall_payload):
        valid_rainfall_payload["subdivision"] = "UNKNOWN_SUBDIVISION_XYZ"
        response = client.post("/api/risk/predict", json=valid_rainfall_payload)
        assert response.status_code == 422
        data = response.json()
        assert "Unknown subdivision" in str(data.get("detail", ""))


class TestOverflowPredictEndpoint:
    @pytest.fixture
    def valid_overflow_payload(self):
        return {
            "water_level_cm": 85.0,
            "rise_rate_cm_per_15min": 6.0,
            "rainfall_mm_per_hr": 25.0,
            "cumulative_rain_6hr_mm": 50.0,
            "cumulative_rain_24hr_mm": 100.0,
            "pipe_diameter_mm": 600.0,
            "pipe_material": "Concrete",
            "pipe_slope": 0.02,
            "elevation_m": 10.0,
            "month": 7,
        }

    def test_valid_overflow_prediction(self, valid_overflow_payload):
        response = client.post("/api/risk/overflow", json=valid_overflow_payload)
        assert response.status_code == 200
        data = response.json()
        assert 0.0 <= data["overflow_probability_15min"] <= 1.0
        assert 0.0 <= data["overflow_probability_30min"] <= 1.0
        assert 0.0 <= data["overflow_score"] <= 1.0

    def test_invalid_pipe_material(self, valid_overflow_payload):
        valid_overflow_payload["pipe_material"] = "Unobtainium"
        response = client.post("/api/risk/overflow", json=valid_overflow_payload)
        assert response.status_code == 422

    def test_invalid_negative_water_level(self, valid_overflow_payload):
        valid_overflow_payload["water_level_cm"] = -5.0
        response = client.post("/api/risk/overflow", json=valid_overflow_payload)
        assert response.status_code == 422


class TestAlertsRankEndpoint:
    def test_valid_multi_site_ranking(self):
        payload = {
            "sites": [
                {
                    "site_id": "SITE_LOW",
                    "occlusion_percentage": 5.0,
                    "overflow_probability_15min": 0.05,
                    "overflow_probability_30min": 0.08,
                    "rainfall_prediction_mm": 10.0,
                },
                {
                    "site_id": "SITE_CRITICAL",
                    "occlusion_percentage": 85.0,
                    "overflow_probability_15min": 0.90,
                    "overflow_probability_30min": 0.95,
                    "rainfall_prediction_mm": 350.0,
                },
                {
                    "site_id": "SITE_MEDIUM",
                    "occlusion_percentage": 40.0,
                    "overflow_probability_15min": 0.40,
                    "overflow_probability_30min": 0.50,
                    "rainfall_prediction_mm": 120.0,
                },
            ],
            "weights": {
                "blockage_weight": 0.35,
                "overflow_weight": 0.45,
                "rainfall_weight": 0.20,
                "vulnerability_weight": 0.00,
                "overflow_15min_weight": 0.65,
                "overflow_30min_weight": 0.35,
            },
        }
        response = client.post("/api/alerts/rank", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_sites"] == 3
        ranked = data["ranked_sites"]
        assert len(ranked) == 3

        # Check descending sort and rank assignment
        assert ranked[0]["rank"] == 1
        assert ranked[0]["site_id"] == "SITE_CRITICAL"
        assert ranked[1]["rank"] == 2
        assert ranked[1]["site_id"] == "SITE_MEDIUM"
        assert ranked[2]["rank"] == 3
        assert ranked[2]["site_id"] == "SITE_LOW"
        assert ranked[0]["risk_score"] > ranked[1]["risk_score"] > ranked[2]["risk_score"]

    def test_dynamic_telemetry_and_rainfall_evaluation(self):
        payload = {
            "sites": [
                {
                    "site_id": "SITE_DYNAMIC",
                    "occlusion_percentage": 30.0,
                    "overflow": {
                        "water_level_cm": 80.0,
                        "rise_rate_cm_per_15min": 5.0,
                        "rainfall_mm_per_hr": 20.0,
                        "cumulative_rain_6hr_mm": 40.0,
                        "cumulative_rain_24hr_mm": 80.0,
                        "pipe_diameter_mm": 600.0,
                        "pipe_material": "Concrete",
                        "pipe_slope": 0.015,
                        "elevation_m": 12.0,
                        "month": 6,
                    },
                    "rainfall": {
                        "subdivision": "ANDAMAN & NICOBAR ISLANDS",
                        "target_month": 6,
                        "rainfall_lags": [10, 20, 15, 30, 40, 50, 60, 70, 80, 90, 100, 110],
                    },
                }
            ]
        }
        response = client.post("/api/alerts/rank", json=payload)
        assert response.status_code == 200
        data = response.json()
        site = data["ranked_sites"][0]
        assert site["site_id"] == "SITE_DYNAMIC"
        assert site["overflow_probability_15min"] is not None
        assert site["rainfall_prediction_mm"] is not None
        assert 0.0 <= site["risk_score"] <= 1.0

    def test_empty_sites_list(self):
        response = client.post("/api/alerts/rank", json={"sites": []})
        assert response.status_code == 422


class TestDemoEndpoint:
    def test_demo_endpoint(self):
        response = client.get("/api/demo/risk")
        assert response.status_code == 200
        data = response.json()
        assert data["is_demo_data"] is True
        assert "DEMO DATA NOTICE" in data["notice"]
        assert data["total_sites"] > 0
        assert len(data["ranked_sites"]) == data["total_sites"]
        assert data["ranked_sites"][0]["rank"] == 1
