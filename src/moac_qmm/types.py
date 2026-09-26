"""Validated input schema for MOAC QMM.

Pydantic-validated patient telemetry — SPOF #29 annihilated:
no more unvalidated dict inputs that silently fail.

All fields carry defaults for a physiologically plausible reference
profile. Edge cases override these. Note that ``current_ph`` defaults to
fasting gastric pH (2.0): with the default telemetry the composite
restitution is zero by design — the module models gastric epithelial
restitution, not systemic physiology.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PatientTelemetry(BaseModel):
    """Validated patient telemetry for the QMM engine."""

    model_config = ConfigDict(extra="allow")  # forward compatibility

    # ── Genomic ──
    genetics: dict[str, str] = Field(
        default_factory=lambda: {"CYP2C19": "*1/*1", "CYP3A4": "*1/*1"}
    )

    # ── Demographics ──
    age: int = Field(45, ge=0, le=120)
    biological_age: int = Field(45, ge=0, le=120)
    methylation_pace: float = Field(1.0, ge=0.5, le=2.0)
    telomere_kb: float = Field(10.0, ge=1.0, le=20.0)

    # ── Organ function ──
    gfr: float = Field(90.0, ge=0, le=200)
    hepatic_flow: float = Field(1500.0, ge=0, le=3000)
    albumin: float = Field(4.0, ge=1.0, le=6.0)

    # ── Organ crosstalk states (0=failure, 1=optimal) ──
    organ_states: dict[str, float] = Field(
        default_factory=lambda: {
            "gut": 1.0,
            "liver": 1.0,
            "kidney": 1.0,
            "heart": 1.0,
            "lung": 1.0,
            "brain": 1.0,
        }
    )

    # ── Drug ──
    primary_drug: str = "Esomeprazole"
    primary_drug_class: str = "PPI"
    route: str = "oral"
    drug_params: dict[str, Any] = Field(default_factory=dict)
    drug_stack: list[dict[str, Any]] = Field(default_factory=list)

    # ── PK micro-constants (2-compartment) ──
    k12: float = Field(0.15, ge=0, le=1.0)
    k21: float = Field(0.10, ge=0, le=1.0)
    v_central: float = Field(0.15, ge=0.01, le=5.0)
    v_peripheral: float = Field(0.10, ge=0.01, le=5.0)

    # ── Physiological ──
    current_ph: float = Field(2.0, ge=0, le=14)  # fasting gastric pH
    spasm_prob: float = Field(0.5, ge=0, le=1)
    spo2: float = Field(98.0, ge=0, le=100)
    tissue_po2: float = Field(40.0, ge=0, le=150)
    hrv_rmssd: float = Field(40.0, ge=0, le=200)
    cortisol_nadir: float = Field(5.0, ge=0, le=50)
    cortisol_8am: float = Field(15.0, ge=0, le=60)
    dhea_s: float = Field(200.0, ge=0, le=1000)

    # ── Infectiology ──
    pathogen_name: str = "Unknown"
    pathogen_k: float = Field(0.0, ge=0, le=10)
    immune_v: float = Field(1.0, ge=0, le=10)
    biofilm: bool = False
    exposure_hours: float = Field(0.0, ge=0, le=720)
    th1_th2_ratio: float = Field(1.0, ge=0, le=10)
    pathogen_strategy: str = "PLANKTONIC_FAST"

    # ── Microbiome ──
    microbiome_diversity: float = Field(3.5, ge=0, le=6)
    pathobionts: list[str] = Field(default_factory=list)
    ppi_exposure_weeks: float = Field(0.0, ge=0, le=520)

    # ── Nutrients ──
    nutrients: dict[str, float] = Field(default_factory=dict)

    # ── Cellular ──
    mtor_activity: float = Field(0.5, ge=0, le=2)
    ampk_activity: float = Field(0.5, ge=0, le=2)

    # ── Chrono ──
    hour: float = Field(8.0, ge=0, le=24)

    # ── Metabolic ──
    metabolic_reserve: float = Field(1.0, ge=0, le=2)
    entropy_estimate: float = Field(0.1, ge=0, le=1)

    # ── Sleep ──
    total_sleep_hours: float = Field(7.0, ge=0, le=14)
    n3_percentage: float = Field(15.0, ge=0, le=40)
    rem_percentage: float = Field(22.0, ge=0, le=40)
    sleep_efficiency: float = Field(0.85, ge=0, le=1)
    awakenings: int = Field(2, ge=0, le=30)

    # ── Toxins ──
    toxins: dict[str, float] = Field(default_factory=dict)

    # ── Quantum receptor ──
    n_receptors: int = Field(10_000, ge=100, le=1_000_000)
    n_simulations: int = Field(1000, ge=10, le=100_000)
    spare_receptors: float = Field(0.1, ge=0, le=0.5)
    allosteric_alpha: float = Field(1.0, ge=0.1, le=10)
    competitor_conc: float = Field(0.0, ge=0, le=100)
    competitor_kd: float = Field(1.0, ge=0.01, le=100)

    # ── Strict gates ──
    strict_receptor_gate: bool = False  # SPOF #37: v28 kill-switch is opt-in

    # ── Electrolytes ──
    potassium: float = Field(4.0, ge=1, le=8)

    # ── NTI monitoring (used when Warfarin/Digoxin in stack) ──
    inr: float = Field(2.5, ge=0, le=10)
    vitamin_k_intake: float = Field(100.0, ge=0, le=1000)
    digoxin_level: float = Field(1.0, ge=0, le=10)

    # ── Deep learning ──
    use_neural_pk: bool = False
    use_bayesian_calibration: bool = False
    use_adaptive_payoff: bool = False
    use_rl_optimizer: bool = False

    @field_validator("organ_states")
    @classmethod
    def _validate_organ_states(cls, v: dict[str, float]) -> dict[str, float]:
        for organ, state in v.items():
            if not 0.0 <= state <= 1.0:
                msg = f"organ_states[{organ!r}]={state} outside [0, 1]"
                raise ValueError(msg)
        return v


__all__ = ["PatientTelemetry"]
