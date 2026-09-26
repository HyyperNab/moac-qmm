"""Engine integration tests — the full tensor collision."""

from __future__ import annotations

from typing import Any

import pytest

from moac_qmm import QMMEngine, __version__
from moac_qmm.types import PatientTelemetry


class TestQMMEngine:
    def test_healthy_patient_completes(self, healthy_telemetry: dict[str, Any]) -> None:
        engine = QMMEngine(healthy_telemetry, seed=42)
        result = engine.execute()
        assert "error" not in result
        assert "hash" in result

    def test_edge_case_aborts(self, edge_case_telemetry: dict[str, Any]) -> None:
        engine = QMMEngine(edge_case_telemetry, seed=42)
        result = engine.execute()
        assert "error" in result
        assert "CLEARANCE-KILL" in result["error"]

    def test_edge_case_abort_includes_events(self, edge_case_telemetry: dict[str, Any]) -> None:
        engine = QMMEngine(edge_case_telemetry, seed=42)
        result = engine.execute()
        assert isinstance(result.get("events"), list)
        assert len(result["events"]) >= 3

    def test_raise_on_abort_flag(self, edge_case_telemetry: dict[str, Any]) -> None:
        from moac_qmm.exceptions import StrataRejection

        engine = QMMEngine(edge_case_telemetry, seed=42)
        with pytest.raises(StrataRejection):
            engine.execute(raise_on_abort=True)

    def test_returns_version(self, healthy_telemetry: dict[str, Any]) -> None:
        engine = QMMEngine(healthy_telemetry, seed=42)
        assert engine.execute()["version"] == __version__

    def test_restitution_is_float(self, healthy_telemetry: dict[str, Any]) -> None:
        result = QMMEngine(healthy_telemetry, seed=42).execute()
        assert isinstance(result["restitution"], float)
        assert 0.0 <= result["restitution"] <= 1.0

    def test_deterministic_with_same_seed(self, healthy_telemetry: dict[str, Any]) -> None:
        r1 = QMMEngine(healthy_telemetry, seed=123).execute()
        r2 = QMMEngine(healthy_telemetry, seed=123).execute()
        assert r1["hash"] == r2["hash"]
        assert r1["compiled_state"] == r2["compiled_state"]

    def test_events_have_25_phases(self, healthy_telemetry: dict[str, Any]) -> None:
        result = QMMEngine(healthy_telemetry, seed=42).execute()
        assert len(result["events"]) == 25

    def test_accepts_validated_model(self, healthy_telemetry: dict[str, Any]) -> None:
        model = PatientTelemetry(**healthy_telemetry)
        result = QMMEngine(model, seed=42).execute()
        assert "hash" in result

    def test_deep_learning_optional(self, healthy_telemetry: dict[str, Any]) -> None:
        telemetry = dict(healthy_telemetry)
        telemetry.update(
            {
                "use_neural_pk": True,
                "use_bayesian_calibration": True,
                "use_adaptive_payoff": True,
                "use_rl_optimizer": True,
            }
        )
        result = QMMEngine(telemetry, seed=42).execute()
        assert "hash" in result
        assert "neural_pk" in result
        assert "rl_recommendation" in result
        assert "calibration" in result

    def test_rl_pretrained_not_zero_table(self, healthy_telemetry: dict[str, Any]) -> None:
        """D-08 fix: RL recommendations come from a pre-trained Q-table."""
        telemetry = dict(healthy_telemetry)
        telemetry["use_rl_optimizer"] = True
        result = QMMEngine(telemetry, seed=42).execute()
        assert result["rl_summary"]["episodes_trained"] >= 200
        assert result["rl_summary"]["q_table_nonzero"] > 0

    def test_nti_warfarin_check_runs(self, healthy_telemetry: dict[str, Any]) -> None:
        telemetry = dict(healthy_telemetry)
        telemetry["primary_drug"] = "Warfarin"
        telemetry["primary_drug_class"] = "Anticoagulant"
        telemetry["inr"] = 2.5
        result = QMMEngine(telemetry, seed=42).execute()
        assert "nti_warfarin" in result
        assert result["nti_warfarin"]["inr_in_range"] is True

    def test_outcome_tracker_injectable(self, healthy_telemetry: dict[str, Any]) -> None:
        from moac_qmm.deep_learning import OutcomeTracker

        tracker = OutcomeTracker()
        QMMEngine(healthy_telemetry, seed=42, outcome_tracker=tracker).execute()
        assert len(tracker.predictions) == 1  # D-14: exactly one log per run

    def test_strict_receptor_gate_aborts(self, healthy_telemetry: dict[str, Any]) -> None:
        telemetry = dict(healthy_telemetry)
        telemetry["strict_receptor_gate"] = True
        result = QMMEngine(telemetry, seed=42).execute()
        assert "error" in result
        assert "QUANTUM-RECEPTOR" in result["error"]
