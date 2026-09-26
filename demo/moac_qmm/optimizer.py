"""Stable homeostasis vector optimizer — reverse-engineers the stable state."""

from __future__ import annotations

from typing import Any

from moac_qmm.constants import (
    CRITICAL_PH_THRESHOLD,
    HRV_VAGAL_FLOOR,
    MICROBIOME_DIVERSITY_FLOOR,
    MTOR_AUTOPHAGY_THRESHOLD,
)
from moac_qmm.models.nutrients import NutrientSubstrateMatrix
from moac_qmm.types import PatientTelemetry


class StableHomeostasisOptimizer:
    """Reverse-engineers the telemetry values needed to pass all phases.

    Given a patient, this module outputs a prescription: the exact
    physiological targets required to reach stable homeostasis across
    all dimensions.
    """

    @staticmethod
    def calculate_optimal_vector(
        telemetry: dict[str, Any] | PatientTelemetry,
    ) -> dict[str, Any]:
        """Compute the prescription set for the given telemetry."""
        if not isinstance(telemetry, PatientTelemetry):
            telemetry = PatientTelemetry(**telemetry)

        t = telemetry
        prescriptions: dict[str, Any] = {}

        # 1. Genomic dosing
        if "*17" in t.genetics.get("CYP2C19", ""):
            prescriptions["ppi_dose"] = {
                "current": "40mg OD",
                "required": "80-120mg BD before breakfast + dinner",
                "alternative": "Rabeprazole 20mg BD (CYP2C19-independent metabolism)",
            }

        # 2. Renal
        if t.gfr < 60:
            prescriptions["renal"] = {
                "current_gfr": t.gfr,
                "target": ">60",
                "intervention": "Hydration, nephrotoxin avoidance, ACEi if proteinuric",
            }

        # 3. Albumin
        if t.albumin < 3.5:
            prescriptions["albumin"] = {
                "current": t.albumin,
                "target": ">3.5 g/dL",
                "intervention": "High biological value protein 1.5 g/kg/day",
            }

        # 4. pH
        if t.current_ph < CRITICAL_PH_THRESHOLD:
            prescriptions["ph"] = {
                "current": t.current_ph,
                "target": f">{CRITICAL_PH_THRESHOLD}",
                "interventions": [
                    "PPI 30-60 min before breakfast (not nighttime)",
                    "Sodium alginate nocturnally",
                    "Stop eating 3h before bed",
                    "Elevate head of bed 15-20°",
                ],
            }

        # 5. Hypoxia
        if t.spo2 < 95:
            prescriptions["hypoxia"] = {
                "current": f"{t.spo2}%",
                "target": ">95%",
                "intervention": "O2 supplementation + treat underlying cause",
            }

        # 6. Vagal
        if t.hrv_rmssd < HRV_VAGAL_FLOOR:
            prescriptions["vagal"] = {
                "current_rmssd": t.hrv_rmssd,
                "target": ">30ms",
                "interventions": [
                    "Paced breathing 4-6 breaths/min",
                    "Cold exposure",
                    "Magnesium glycinate 400mg nocturnally",
                    "Reduce caffeine + chronic stress",
                ],
            }

        # 7. Nutrients
        deficient: dict[str, Any] = {}
        for nutrient, level in t.nutrients.items():
            if nutrient in NutrientSubstrateMatrix.REQUIRED_SUBSTRATES:
                req = NutrientSubstrateMatrix.REQUIRED_SUBSTRATES[nutrient]
                if level < req * 0.7:
                    deficient[nutrient] = {"current": level, "required": req}
        if deficient:
            prescriptions["nutrients"] = deficient

        # 8. Sleep
        if t.total_sleep_hours < 7 or t.n3_percentage < 12:
            prescriptions["sleep"] = {
                "current": f"{t.total_sleep_hours}h, {t.n3_percentage}% N3",
                "target": ">7h, >15% N3",
                "interventions": [
                    "Consistent sleep/wake times",
                    "Room temp 18-20°C",
                    "No screens 90 min before bed",
                    "Glycine 3g before bed",
                    "Avoid alcohol (fragments N3)",
                ],
            }

        # 9. HPA
        if t.cortisol_8am > 20 or t.dhea_s < 100:
            prescriptions["hpa"] = {
                "current": f"Cortisol={t.cortisol_8am}, DHEA={t.dhea_s}",
                "target": "Cortisol 10-20, DHEA >150",
                "interventions": [
                    "Ashwagandha KSM-66 600mg/day",
                    "Phosphatidylserine 600mg",
                    "DHEA 25-50mg/day if <100",
                ],
            }

        # 10. Tissue mode
        if t.mtor_activity / max(0.01, t.ampk_activity) < MTOR_AUTOPHAGY_THRESHOLD:
            prescriptions["tissue_mode"] = {
                "current": "DEMOLITION (mTOR << AMPK)",
                "target": f"BUILDING (mTOR/AMPK > {MTOR_AUTOPHAGY_THRESHOLD})",
                "interventions": [
                    "Leucine 3g with meals",
                    "Resistance training",
                    "Protein 1.6 g/kg/day",
                ],
            }

        # 11. Toxins
        if t.toxins:
            prescriptions["detox"] = {
                "toxins": t.toxins,
                "interventions": [
                    "NAC 600mg 2x/day",
                    "Chlorella/spirulina",
                    "Sauna",
                    "Eliminate source",
                ],
            }

        # 12. Microbiome
        if t.microbiome_diversity < MICROBIOME_DIVERSITY_FLOOR:
            prescriptions["microbiome"] = {
                "current": t.microbiome_diversity,
                "target": f">{MICROBIOME_DIVERSITY_FLOOR}",
                "interventions": [
                    "30+ plant species/week",
                    "Fermented foods",
                    "L. rhamnosus GG + S. boulardii",
                ],
            }

        # 13. Chrono
        if t.hour > 10 or t.hour < 5:
            prescriptions["chrono"] = {
                "current": f"Hour {t.hour}",
                "target": "6-9 AM",
            }

        return prescriptions


__all__ = ["StableHomeostasisOptimizer"]
