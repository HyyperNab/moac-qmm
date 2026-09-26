# Evidence Register — Per-Constant Provenance

**Ground Truth or Silence.** The v28 kernel artifact shipped biophysical
constants *without citations*. We refuse to fabricate references, so every
constant is registered in `src/moac_qmm/evidence.py` with an honest
provenance tier. A test (`tests/test_constants_evidence.py`) enforces that
the register and `constants.py` never drift apart.

## Tiers

| Tier | Meaning |
|------|---------|
| `VERIFIED_PRIMARY` | Verified against a peer-reviewed primary source with DOI. **Currently none.** |
| `SECONDARY_REVIEW_UNVERIFIED` | Claimed origin that was *not* verified against the source. Approximate. |
| `HEURISTIC_KERNEL` | Modelling assumption authored into the kernel. No citation exists. |
| `STRUCTURAL` | Internal game-theory / architecture constant. No clinical claim. |

## Register

| Constant | Tier | Note |
|----------|------|------|
| `ALLELE_FREQUENCIES` | SECONDARY_REVIEW_UNVERIFIED | Claimed 1000 Genomes / PharmGKB; NOT verified. Varies by ancestry. |
| `CRITICAL_PH_THRESHOLD` | HEURISTIC_KERNEL | Minimal gastric pH for epithelial restitution. |
| `DIC_ENTROPY_TRIPWIRE` | HEURISTIC_KERNEL | Waterhouse-Friderichsen 3-sigma threshold. |
| `IL6_STORM_THRESHOLD` / `TNF_ALPHA_LETHAL` | HEURISTIC_KERNEL | Cytokine storm onset / necrosis risk (pg/mL). |
| `HRV_VAGAL_FLOOR` | HEURISTIC_KERNEL | RMSSD parasympathetic collapse floor (ms). |
| `MTOR_AUTOPHAGY_THRESHOLD` | HEURISTIC_KERNEL | mTOR/AMPK demolition-mode ratio. |
| `MICROBIOME_DIVERSITY_FLOOR` | HEURISTIC_KERNEL | Shannon diversity floor. |
| `CHRONO_PPI_OPTIMAL_WINDOW` | HEURISTIC_KERNEL | PPI efficacy window (06:00-09:00). |
| `PROTEIN_BINDING_CRITICAL` | HEURISTIC_KERNEL | Albumin displacement lethality threshold. |
| `RECEPTOR_OCCUPANCY_THRESHOLD` | HEURISTIC_KERNEL | Receptor occupancy for therapeutic effect. |
| `N3_SLEEP_MINIMUM_HOURS` / `GLYMPHATIC_CLEARANCE_RATE` | HEURISTIC_KERNEL | Deep-sleep minimum / glymphatic fraction. |
| `CORTISOL_AWAKENING_PEAK` / `DHEA_NORMAL` | HEURISTIC_KERNEL | Endocrine reference values. |
| `NTI_WARFARIN_INR_TARGET` / `NTI_DIGOXIN_THERAPEUTIC` | HEURISTIC_KERNEL | NTI therapeutic targets. |
| `LEAD_TOXIC_THRESHOLD` / `MERCURY_TOXIC_THRESHOLD` / `ALCOHOL_CYP2E1_INDUCTION` | HEURISTIC_KERNEL | Toxicity thresholds. |
| `ALBUMIN_NORMAL` / `GFR_NORMAL` / `HEPATIC_FLOW_NORMAL` | HEURISTIC_KERNEL | Organ reference values. Textbook-plausible, unverified. |
| `HYPOXIA_CYP450_FLOOR` | HEURISTIC_KERNEL | CYP450 oxygen-starvation floor. |
| `VOLTAGE_ANCHOR_MG` | HEURISTIC_KERNEL | v28 parity constant; not used in computation. |
| `LAGOM_NBE_MINIMUM` / `SPO2_NOMINAL` | STRUCTURAL | Internal model constants. |

## Policy

1. No constant may be promoted to `VERIFIED_PRIMARY` without a DOI-attached
   verification note in the same PR.
2. Clinical-adjacent use of any `HEURISTIC_KERNEL` constant is forbidden —
   the kernel is a qualitative simulation, not a dosing tool.
3. New constants require a register entry in the same PR (the integrity test
   enforces this).
