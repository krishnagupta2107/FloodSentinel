"""
Unit and integration tests for FloodSentinel Risk Fusion and Prioritization Module.
"""

import pytest
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
from src.floodsentinel.risk.risk_fusion import RiskFusionEngine
from src.floodsentinel.risk.risk_ranker import rank_sites, to_dataframe


class TestBlockageNormalization:
    def test_normal_percentage(self):
        engine = RiskFusionEngine()
        assert engine.normalize_blockage(0.0) == 0.0
        assert engine.normalize_blockage(50.0) == 0.5
        assert engine.normalize_blockage(100.0) == 1.0

    def test_clamping(self):
        engine = RiskFusionEngine()
        assert engine.normalize_blockage(-10.0) == 0.0
        assert engine.normalize_blockage(150.0) == 1.0

    def test_none_and_nan(self):
        engine = RiskFusionEngine()
        assert engine.normalize_blockage(None) == 0.0
        assert engine.normalize_blockage(float("nan")) == 0.0

    def test_invalid_type(self):
        engine = RiskFusionEngine()
        with pytest.raises(ValueError):
            engine.normalize_blockage("invalid_text")


class TestOverflowCalculation:
    def test_weighted_combination(self):
        weights = FusionWeights(overflow_15min_weight=0.65, overflow_30min_weight=0.35)
        engine = RiskFusionEngine(weights=weights)
        score = engine.compute_overflow_score(p15=0.80, p30=0.60)
        expected = 0.65 * 0.80 + 0.35 * 0.60
        assert pytest.approx(score, rel=1e-4) == expected

    def test_single_horizon(self):
        engine = RiskFusionEngine()
        assert engine.compute_overflow_score(p15=0.75, p30=None) == 0.75
        assert engine.compute_overflow_score(p15=None, p30=0.45) == 0.45
        assert engine.compute_overflow_score(p15=None, p30=None) == 0.0

    def test_invalid_probabilities(self):
        engine = RiskFusionEngine()
        with pytest.raises(ValueError):
            engine.compute_overflow_score(p15=1.5, p30=0.5)
        with pytest.raises(ValueError):
            engine.compute_overflow_score(p15=0.5, p30=-0.1)


class TestRainfallNormalization:
    def test_monotonic_scaling(self):
        normalizer = RainfallNormalizer()
        s0 = normalizer.normalize(0.0)
        s1 = normalizer.normalize(50.0)
        s2 = normalizer.normalize(200.0)
        s3 = normalizer.normalize(500.0)
        s4 = normalizer.normalize(3000.0)

        assert s0 == 0.0
        assert 0.0 < s1 < s2 < s3 < s4 <= 1.0
        assert s4 == 1.0

    def test_edge_cases(self):
        normalizer = RainfallNormalizer()
        assert normalizer.normalize(None) == 0.0
        assert normalizer.normalize(-20.0) == 0.0
        assert normalizer.normalize(float("nan")) == 0.0

    def test_invalid_input(self):
        normalizer = RainfallNormalizer()
        with pytest.raises(ValueError):
            normalizer.normalize("bad_input")


class TestWeightsAndThresholds:
    def test_weights_validation(self):
        with pytest.raises(ValueError):
            FusionWeights(blockage_weight=-0.1)
        with pytest.raises(ValueError):
            FusionWeights(overflow_15min_weight=0.5, overflow_30min_weight=0.2)

    def test_dynamic_normalization(self):
        weights = FusionWeights(
            blockage_weight=0.4,
            overflow_weight=0.4,
            rainfall_weight=0.2,
            vulnerability_weight=0.2,
        )
        # Without vulnerability
        w_no_vuln = weights.normalized_weights(has_vulnerability=False)
        assert pytest.approx(sum(w_no_vuln.values()), rel=1e-5) == 1.0
        assert "vulnerability" not in w_no_vuln
        assert w_no_vuln["blockage"] == 0.4

        # With vulnerability
        w_vuln = weights.normalized_weights(has_vulnerability=True)
        assert pytest.approx(sum(w_vuln.values()), rel=1e-5) == 1.0
        assert "vulnerability" in w_vuln
        assert pytest.approx(w_vuln["blockage"], rel=1e-4) == 0.4 / 1.2

    def test_risk_levels(self):
        thresholds = RiskThresholds(low_cutoff=0.30, medium_cutoff=0.60, high_cutoff=0.80)
        assert thresholds.get_level(0.15) == RiskLevel.LOW
        assert thresholds.get_level(0.45) == RiskLevel.MEDIUM
        assert thresholds.get_level(0.70) == RiskLevel.HIGH
        assert thresholds.get_level(0.95) == RiskLevel.CRITICAL


class TestSiteEvaluationAndRanking:
    def test_full_evaluation(self):
        engine = RiskFusionEngine()
        site_data = {
            "site_id": "TEST_001",
            "image_name": "test.jpg",
            "occlusion_percentage": 50.0,
            "overflow_probability_15min": 0.80,
            "overflow_probability_30min": 0.60,
            "rainfall_prediction_mm": 120.0,
            "vulnerability_score": None,
        }
        res = engine.evaluate_site(site_data)
        assert isinstance(res, SiteRiskResult)
        assert 0.0 <= res.risk_score <= 1.0
        assert res.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert not res.vulnerability_available
        assert res.vulnerability_score is None
        assert len(res.explanation) > 0
        assert "blockage" in res.factor_breakdown

    def test_ranking_order(self):
        engine = RiskFusionEngine()
        records = [
            {"site_id": "LOW_SITE", "occlusion_percentage": 5.0, "overflow_probability_15min": 0.05, "rainfall_prediction_mm": 10.0},
            {"site_id": "CRITICAL_SITE", "occlusion_percentage": 90.0, "overflow_probability_15min": 0.95, "rainfall_prediction_mm": 400.0},
            {"site_id": "MEDIUM_SITE", "occlusion_percentage": 40.0, "overflow_probability_15min": 0.40, "rainfall_prediction_mm": 80.0},
        ]
        ranked = rank_sites(records, engine=engine)
        assert len(ranked) == 3
        assert ranked[0].site_id == "CRITICAL_SITE"
        assert ranked[0].rank == 1
        assert ranked[1].site_id == "MEDIUM_SITE"
        assert ranked[1].rank == 2
        assert ranked[2].site_id == "LOW_SITE"
        assert ranked[2].rank == 3
        assert ranked[0].risk_score > ranked[1].risk_score > ranked[2].risk_score

    def test_dataframe_conversion(self):
        records = [
            {"site_id": "S1", "occlusion_percentage": 20.0, "overflow_probability_15min": 0.1, "rainfall_prediction_mm": 15.0},
            {"site_id": "S2", "occlusion_percentage": 80.0, "overflow_probability_15min": 0.9, "rainfall_prediction_mm": 200.0},
        ]
        ranked = rank_sites(records)
        df = to_dataframe(ranked)
        assert len(df) == 2
        assert list(df["rank"]) == [1, 2]
        assert "risk_score" in df.columns
        assert "dominant_risk_factor" in df.columns


class TestModelArtifactsIntegration:
    def test_real_overflow_predictor(self):
        pred = OverflowPredictor()
        telemetry = {
            "water_level_cm": 85.0,
            "rise_rate_cm_per_15min": 6.0,
            "rainfall_mm_per_hr": 25.0,
            "cumulative_rain_6hr_mm": 50.0,
            "cumulative_rain_24hr_mm": 100.0,
            "pipe_diameter_mm": 600.0,
            "pipe_slope": 0.02,
            "elevation_m": 10.0,
            "month": 7,
            "pipe_material": "Concrete",
        }
        p15, p30 = pred.predict_proba(telemetry)
        assert 0.0 <= p15 <= 1.0
        assert 0.0 <= p30 <= 1.0

    def test_end_to_end_fusion_with_telemetry(self):
        overflow_pred = OverflowPredictor()
        engine = RiskFusionEngine(overflow_predictor=overflow_pred)
        site_data = {
            "site_id": "SENSOR_SITE_01",
            "occlusion_percentage": 35.0,
            "rainfall_prediction_mm": 150.0,
            "metadata": {
                "telemetry": {
                    "water_level_cm": 80.0,
                    "rise_rate_cm_per_15min": 4.0,
                    "rainfall_mm_per_hr": 15.0,
                    "cumulative_rain_6hr_mm": 30.0,
                    "cumulative_rain_24hr_mm": 60.0,
                    "pipe_diameter_mm": 600.0,
                    "pipe_slope": 0.015,
                    "elevation_m": 12.0,
                    "month": 6,
                    "pipe_material": "Cast Iron",
                }
            },
        }
        res = engine.evaluate_site(site_data)
        assert res.overflow_score > 0.0
        assert 0.0 <= res.risk_score <= 1.0
