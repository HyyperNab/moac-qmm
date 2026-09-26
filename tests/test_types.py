"""Contract tests for the validated telemetry schema."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from moac_qmm.types import PatientTelemetry


class TestPatientTelemetry:
    def test_defaults_construct_valid_model(self) -> None:
        model = PatientTelemetry()
        assert model.age == 45
        assert model.gfr == 90.0
        assert model.genetics["CYP2C19"] == "*1/*1"

    def test_rejects_out_of_range_age(self) -> None:
        with pytest.raises(ValidationError):
            PatientTelemetry(age=200)

    def test_rejects_out_of_range_gfr(self) -> None:
        with pytest.raises(ValidationError):
            PatientTelemetry(gfr=999)

    def test_rejects_invalid_organ_state(self) -> None:
        with pytest.raises(ValidationError):
            PatientTelemetry(organ_states={"gut": 1.7})

    def test_allows_extra_fields(self) -> None:
        model = PatientTelemetry(future_field_xyz=123)  # type: ignore[call-arg]
        assert model.model_dump().get("future_field_xyz") == 123

    def test_rejects_wrong_type(self) -> None:
        with pytest.raises(ValidationError):
            PatientTelemetry(age="fifty")  # type: ignore[arg-type]

    def test_healthy_fixture_roundtrip(self, healthy_telemetry: dict[str, Any]) -> None:
        model = PatientTelemetry(**healthy_telemetry)
        assert model.primary_drug == "Esomeprazole"

    def test_nti_fields_have_defaults(self) -> None:
        model = PatientTelemetry()
        assert model.inr == 2.5
        assert model.digoxin_level == 1.0
        assert model.vitamin_k_intake == 100.0

    def test_strict_receptor_gate_defaults_off(self) -> None:
        assert PatientTelemetry().strict_receptor_gate is False
