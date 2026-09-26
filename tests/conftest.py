"""Shared fixtures for the MOAC QMM test suite."""

from __future__ import annotations

from typing import Any

import pytest

from moac_qmm import QMMEngine


@pytest.fixture
def healthy_telemetry() -> dict[str, Any]:
    """A healthy patient with no SPOF triggers."""
    return {
        "genetics": {"CYP2C19": "*1/*1"},
        "primary_drug": "Esomeprazole",
        "primary_drug_class": "PPI",
        "drug_params": {
            "dose": 40,
            "kd": 0.8,
            "protein_bound": 0.95,
            "vd": 0.25,
            "cyp_pathway": ["CYP2C19"],
            "renal_fraction": 0.2,
            "hepatic_extraction": 0.8,
            "therapeutic_min": 0.5,
        },
        "drug_stack": [
            {"name": "Esomeprazole", "protein_bound": 0.95, "cyp_pathway": ["CYP2C19"]},
        ],
        "gfr": 90,
        "albumin": 4.0,
        "current_ph": 5.0,
        "spo2": 98,
        "hrv_rmssd": 50,
        "hour": 8.0,
        "pathogen_name": "H. pylori",
        "pathogen_k": 0.1,
        "immune_v": 2.0,
        "exposure_hours": 2,
        "pathogen_strategy": "PLANKTONIC_FAST",
        "age": 35,
        "biological_age": 35,
        "telomere_kb": 10.0,
        "cortisol_8am": 15,
        "cortisol_nadir": 3,
        "dhea_s": 200,
        "total_sleep_hours": 8,
        "n3_percentage": 18,
        "mtor_activity": 0.6,
        "ampk_activity": 0.4,
        "microbiome_diversity": 3.5,
        "pathobionts": [],
        "nutrients": {
            "glutamine": 0.5,
            "zinc": 8,
            "vitamin_c": 75,
            "vitamin_a": 900,
            "arginine": 4,
            "n3_index": 8,
        },
        "organ_states": {
            "gut": 1,
            "liver": 1,
            "kidney": 1,
            "heart": 1,
            "lung": 1,
            "brain": 1,
        },
    }


@pytest.fixture
def edge_case_telemetry(healthy_telemetry: dict[str, Any]) -> dict[str, Any]:
    """A critically compromised patient."""
    telemetry = dict(healthy_telemetry)
    telemetry.update(
        {
            "genetics": {"CYP2C19": "*17/*17"},
            "gfr": 25,
            "albumin": 2.0,
            "current_ph": 2.0,
            "spo2": 88,
            "hrv_rmssd": 10,
            "hour": 23,
            "pathogen_k": 0.8,
            "immune_v": 0.3,
            "exposure_hours": 48,
            "pathogen_strategy": "BIOFILM_FORTIFY",
            "age": 65,
            "biological_age": 75,
            "telomere_kb": 3.0,
            "cortisol_8am": 35,
            "dhea_s": 40,
            "total_sleep_hours": 4,
            "n3_percentage": 3,
            "mtor_activity": 0.2,
            "ampk_activity": 0.9,
            "toxins": {"lead": 8, "mercury": 6, "alcohol_chronic": 60},
        }
    )
    return telemetry


@pytest.fixture
def engine(healthy_telemetry: dict[str, Any]) -> QMMEngine:
    """A ready-to-run engine on the healthy profile."""
    return QMMEngine(healthy_telemetry, seed=42)
