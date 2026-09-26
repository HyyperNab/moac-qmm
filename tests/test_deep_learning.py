"""Deep learning layer unit tests."""

from __future__ import annotations

import numpy as np
import pytest

from moac_qmm.deep_learning import (
    AdaptivePayoffMatrix,
    BayesianCalibration,
    NeuralPKPredictor,
    OutcomeTracker,
    ReinforcementLearningOptimizer,
)


class TestNeuralPKPredictor:
    def test_untrained_returns_heuristic(self) -> None:
        predictor = NeuralPKPredictor()
        result = predictor.predict({"age": 50, "gfr": 60})
        assert "clearance_rate" in result
        assert result.get("heuristic") is True

    def test_heuristic_clearance_formula(self) -> None:
        predictor = NeuralPKPredictor()
        result = predictor.predict({"gfr": 90, "albumin": 4.0, "cyp2c19_activity": 1.0})
        assert result["clearance_rate"] == pytest.approx(0.8)

    def test_train_and_predict(self) -> None:
        predictor = NeuralPKPredictor(hidden_size=16, learning_rate=0.01, seed=42)
        rng = np.random.default_rng(42)
        X = rng.random((100, 10)) * np.array([80, 80, 120, 5, 2000, 1, 1, 100, 100, 1])
        y = rng.random((100, 3)) * np.array([2, 10, 1])
        predictor.train(X, y, epochs=50)
        assert predictor.is_trained
        result = predictor.predict(
            {
                "age": 50,
                "bio_age": 55,
                "gfr": 60,
                "albumin": 3.5,
                "hepatic_flow": 1200,
                "cyp2c19_activity": 0.5,
                "cyp3a4_activity": 0.8,
                "spo2": 95,
                "body_weight": 70,
                "sex": 0,
            }
        )
        assert "clearance_rate" in result
        assert "confidence" in result
        assert "clearance_rate_uncertainty" in result
        assert "heuristic" not in result

    def test_training_rejects_bad_shapes(self) -> None:
        predictor = NeuralPKPredictor()
        with pytest.raises(ValueError):
            predictor.train(np.zeros((10, 4)), np.zeros((10, 3)))

    def test_deterministic_with_same_seed(self) -> None:
        def run() -> dict[str, float]:
            p = NeuralPKPredictor(hidden_size=8, seed=99)
            rng = np.random.default_rng(5)
            p.train(rng.random((40, 10)), rng.random((40, 3)), epochs=10)
            return p.predict({"age": 50}, n_mc_samples=20)

        assert run()["clearance_rate"] == pytest.approx(run()["clearance_rate"])

    def test_json_roundtrip(self, tmp_path) -> None:  # SPOF #38: JSON, not pickle
        path = tmp_path / "model.json"
        source = NeuralPKPredictor(hidden_size=8, seed=3)
        rng = np.random.default_rng(1)
        source.train(rng.random((30, 10)), rng.random((30, 3)), epochs=5)
        source.save(path)

        loaded = NeuralPKPredictor(hidden_size=8, seed=4)
        loaded.load(path)
        assert loaded.is_trained
        assert np.allclose(loaded.W1, source.W1)
        assert np.allclose(loaded.W3, source.W3)
        assert np.allclose(loaded.feature_mean, source.feature_mean)
        assert loaded.predict({"age": 50}, n_mc_samples=1)["clearance_rate"] is not None


class TestBayesianCalibration:
    def test_binary_calibration_converges_to_success(self) -> None:
        cal = BayesianCalibration()
        for _ in range(10):
            cal.calibrate_binary("test_condition", 0.8, True)
        for _ in range(2):
            cal.calibrate_binary("test_condition", 0.8, False)
        mean, unc = cal.get_confidence("test_condition")
        assert 0.5 < mean < 1.0
        assert unc > 0

    def test_continuous_calibration(self) -> None:
        cal = BayesianCalibration()
        for val in [1.0, 1.1, 0.9, 1.05, 0.95]:
            cal.calibrate_continuous("clearance", 1.0, val)
        mean, unc = cal.get_confidence("clearance")
        assert 0.8 < mean < 1.2
        assert unc > 0

    def test_uninformed_prior(self) -> None:
        mean, unc = BayesianCalibration().get_confidence("unknown")
        assert (mean, unc) == (0.5, 0.5)

    def test_summary_counts(self) -> None:
        cal = BayesianCalibration()
        cal.calibrate_binary("cond", 0.7, True)
        cal.calibrate_continuous("param", 1.0, 1.1)
        summary = cal.summary()
        assert summary["total_observations"] == 2
        assert summary["binary_conditions"] == 1
        assert summary["continuous_parameters"] == 1

    def test_credible_interval_respects_confidence(self) -> None:
        from moac_qmm.deep_learning import BetaDistribution

        beta = BetaDistribution(alpha=50, beta=50)
        ci95 = beta.credible_interval(0.95)
        ci80 = beta.credible_interval(0.80)
        assert (ci95[1] - ci95[0]) > (ci80[1] - ci80[0])  # D-09 fix


class TestAdaptivePayoffMatrix:
    def test_initial_payoffs_match_v28(self) -> None:
        apm = AdaptivePayoffMatrix()
        p, t = apm.get_payoff("PLANKTONIC_FAST", "PHAGE_THERAPY")
        assert (p, t) == (1.0, 9.0)

    def test_update_increases_treatment_payoff_on_success(self) -> None:
        apm = AdaptivePayoffMatrix()
        _, old_t = apm.get_payoff("BIOFILM_FORTIFY", "BACTERICIDAL_HIGH")
        apm.update_from_outcome("BIOFILM_FORTIFY", "BACTERICIDAL_HIGH", True)
        _, new_t = apm.get_payoff("BIOFILM_FORTIFY", "BACTERICIDAL_HIGH")
        assert new_t > old_t

    def test_update_decreases_treatment_payoff_on_failure(self) -> None:
        apm = AdaptivePayoffMatrix()
        _, old_t = apm.get_payoff("BIOFILM_FORTIFY", "BACTERICIDAL_HIGH")
        apm.update_from_outcome("BIOFILM_FORTIFY", "BACTERICIDAL_HIGH", False)
        _, new_t = apm.get_payoff("BIOFILM_FORTIFY", "BACTERICIDAL_HIGH")
        assert new_t < old_t

    def test_learned_equilibria_survive_float_noise(self) -> None:
        # D-10 fix: tolerant comparison after learning updates
        apm = AdaptivePayoffMatrix()
        for _ in range(3):
            apm.update_from_outcome("PLANKTONIC_FAST", "PHAGE_THERAPY", True)
        assert isinstance(apm.find_nash_equilibria(), list)

    def test_minimax_returns_treatment(self) -> None:
        result = AdaptivePayoffMatrix().calc_minimax()
        assert "minimax_treatment" in result


class TestReinforcementLearningOptimizer:
    def test_q_table_starts_zero(self) -> None:
        rl = ReinforcementLearningOptimizer()
        assert rl.Q.max() == 0

    def test_training_updates_q(self) -> None:
        rl = ReinforcementLearningOptimizer().with_seed(42)
        payoff = np.array([[[2, 8], [6, 4], [3, 7], [1, 9], [4, 6]]] * 5)
        rl.train(payoff, episodes=50, max_steps=10)
        assert rl.Q.max() > 0

    def test_epsilon_decays_during_training(self) -> None:
        # D-11 fix: decay was a no-op in the draft
        rl = ReinforcementLearningOptimizer().with_seed(1)
        payoff = np.array([[[2, 8], [6, 4], [3, 7], [1, 9], [4, 6]]] * 5)
        rl.train(payoff, episodes=50, max_steps=10)
        assert rl.epsilon < 1.0

    def test_recommend_treatment_in_range(self) -> None:
        rl = ReinforcementLearningOptimizer().with_seed(1)
        action = rl.recommend_treatment(0, immune_high=True, biofilm=False, subtherapeutic=False)
        assert 0 <= action < 5

    def test_deterministic_with_seed(self) -> None:
        def max_q(seed: int) -> float:
            rl = ReinforcementLearningOptimizer().with_seed(seed)
            payoff = np.array([[[2, 8], [6, 4], [3, 7], [1, 9], [4, 6]]] * 5)
            rl.train(payoff, episodes=20, max_steps=10)
            return float(rl.Q.max())

        assert max_q(7) == pytest.approx(max_q(7))


class TestOutcomeTracker:
    def test_log_and_resolve(self) -> None:
        tracker = OutcomeTracker()
        tracker.log_prediction("pred1", {"restitution": 0.5})
        tracker.log_outcome("pred1", {"restitution": 0.6})
        metrics = tracker.get_accuracy_metrics()
        assert metrics["n_resolved"] == 1
        assert metrics["mean_relative_error"] == pytest.approx(0.1 / 0.6, rel=1e-3)

    def test_unresolved_has_no_metrics(self) -> None:
        tracker = OutcomeTracker()
        tracker.log_prediction("pred1", {"restitution": 0.5})
        assert tracker.get_accuracy_metrics()["n_resolved"] == 0

    def test_json_persistence_roundtrip(self, tmp_path) -> None:
        path = tmp_path / "outcomes.json"
        tracker = OutcomeTracker()
        tracker.log_prediction("p1", {"restitution": 0.4})
        tracker.save(path)

        restored = OutcomeTracker()
        restored.load(path)
        assert len(restored.predictions) == 1
        assert restored.predictions[0]["id"] == "p1"

    def test_jsonl_streaming_log(self, tmp_path) -> None:
        path = tmp_path / "stream.jsonl"
        tracker = OutcomeTracker(log_path=path)
        tracker.log_prediction("a", {"x": 1})
        tracker.log_prediction("b", {"x": 2})
        content = path.read_text(encoding="utf-8").strip().splitlines()
        assert len(content) == 2
