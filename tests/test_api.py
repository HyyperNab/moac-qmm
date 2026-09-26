"""API layer tests (skipped when fastapi is not installed)."""

from __future__ import annotations

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from moac_qmm.api import app  # noqa: E402
from moac_qmm.types import PatientTelemetry  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def telemetry_payload() -> dict[str, object]:
    model = PatientTelemetry(
        primary_drug="Esomeprazole",
        primary_drug_class="PPI",
        gfr=90,
        current_ph=5.0,
        drug_params={"dose": 40, "kd": 0.8, "therapeutic_min": 0.5},
        drug_stack=[{"name": "Esomeprazole", "protein_bound": 0.95, "cyp_pathway": ["CYP2C19"]}],
        nutrients={
            "glutamine": 0.5,
            "zinc": 8,
            "vitamin_c": 75,
            "vitamin_a": 900,
            "arginine": 4,
            "n3_index": 8,
        },
        genetics={"CYP2C19": "*1/*1"},
    )
    return model.model_dump()


class TestMoacQmmApi:
    def test_healthz(self, client: TestClient) -> None:
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_readyz_reports_version(self, client: TestClient) -> None:
        response = client.get("/readyz")
        assert response.status_code == 200
        assert "version" in response.json()

    def test_version_endpoint(self, client: TestClient) -> None:
        from moac_qmm import __version__

        assert client.get("/version").json()["version"] == __version__

    def test_simulate_healthy(self, client: TestClient, telemetry_payload: dict) -> None:
        response = client.post("/v1/simulate", json={"telemetry": telemetry_payload, "seed": 42})
        assert response.status_code == 200
        body = response.json()
        assert "hash" in body
        assert len(body["events"]) == 25

    def test_simulate_deterministic(self, client: TestClient, telemetry_payload: dict) -> None:
        r1 = client.post("/v1/simulate", json={"telemetry": telemetry_payload, "seed": 42})
        r2 = client.post("/v1/simulate", json={"telemetry": telemetry_payload, "seed": 42})
        assert r1.json()["hash"] == r2.json()["hash"]

    def test_simulate_invalid_telemetry_422(self, client: TestClient) -> None:
        response = client.post("/v1/simulate", json={"telemetry": {"age": 999}})
        assert response.status_code == 422

    def test_simulate_edge_case_returns_error_field(
        self, client: TestClient, telemetry_payload: dict
    ) -> None:
        telemetry_payload["gfr"] = 25
        response = client.post("/v1/simulate", json={"telemetry": telemetry_payload})
        assert response.status_code == 200  # kernel aborts are results, not HTTP errors
        assert "error" in response.json()

    def test_optimize(self, client: TestClient, telemetry_payload: dict) -> None:
        telemetry_payload["gfr"] = 50
        response = client.post("/v1/optimize", json={"telemetry": telemetry_payload})
        assert response.status_code == 200
        assert "renal" in response.json()

    def test_predict(self, client: TestClient) -> None:
        response = client.post("/v1/predict", json={"features": {"age": 50, "gfr": 60}})
        assert response.status_code == 200
        assert "clearance_rate" in response.json()
