"""MOAC QMM engine — the Strata-Oblivion tensor compiler.

29-dimensional tensor matrix that collides all biological variables
into a single deterministic homeostasis vector.

Production hardening vs. the v28 god-object and v29 draft:

- SPOF #30: the 20 model modules actually exist (the draft imported a
  ``models/`` package that was never written — the build was broken).
- SPOF #31: no wildcard imports; every dependency is explicit.
- SPOF #32: the global ``numpy.random`` state is replaced by an
  injected, seeded ``numpy.random.Generator`` — ``execute()`` is
  deterministic for a given (telemetry, seed) pair.
- SPOF #33: ``print()`` side-effects replaced by :mod:`logging` plus a
  structured ``events`` list in the result (library- and API-safe).
- SPOF #34: the outcome tracker is injectable; the engine never
  silently persists to the filesystem.
- SPOF #35: version strings derive from a single source
  (:mod:`moac_qmm._version`), not scattered literals.
- D-08: RL recommendations were drawn from an untrained zero Q-table;
  the engine now pre-trains the agent against the active payoff matrix.
- D-14: predictions were logged twice per run (phase-24 id and final
  seal); the engine logs exactly once, under the seal id.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

import numpy as np

from moac_qmm._version import __version__
from moac_qmm.constants import CRITICAL_PH_THRESHOLD
from moac_qmm.deep_learning import (
    AdaptivePayoffMatrix,
    BayesianCalibration,
    NeuralPKPredictor,
    OutcomeTracker,
    ReinforcementLearningOptimizer,
)
from moac_qmm.exceptions import (
    CytokineStormDetected,
    EdgeCaseCascade,
    HypoxiaCascade,
    NTIToxicityKill,
    NutrientDepletionKill,
    OrganCrosstalkFailure,
    PathogenDominanceNash,
    QuantumReceptorFailure,
    SleepDeprivationKill,
    StrataRejection,
    ToxinOverloadKill,
)
from moac_qmm.models import (
    AntiPersonaEscapeV2,
    AutophagyApoptosisToggle,
    ChronopharmacologyModulator,
    CytokineStormVector,
    DrugDrugInteractionTensor,
    EpigeneticAgeClock,
    ExogenousToxinLoad,
    HPAAxisModel,
    HypoxiaTensor,
    MicrobiomeMetabolizer,
    MultiCompartmentPK,
    NarrowTherapeuticIndexEngine,
    NutrientSubstrateMatrix,
    OrganCrosstalkTensor,
    PathogenGameTheory,
    QSenseGovernor,
    QuantumDrugReceptor,
    RenalHepaticClearance,
    SleepArchitectureTensor,
    SpofLedger,
    TimeSeriesPKSolver,
    VagalToneVoltage,
)
from moac_qmm.models.genomic import GenomicTensor
from moac_qmm.types import PatientTelemetry

logger = logging.getLogger(__name__)

_KERNEL_ABORTS: tuple[type[BaseException], ...] = (
    StrataRejection,
    EdgeCaseCascade,
    CytokineStormDetected,
    HypoxiaCascade,
    NutrientDepletionKill,
    OrganCrosstalkFailure,
    ToxinOverloadKill,
    SleepDeprivationKill,
    NTIToxicityKill,
    QuantumReceptorFailure,
    PathogenDominanceNash,
)

_CYTOKINE_STEPS = 6  # hours of ODE integration per run (v28 parity)
_RL_PRETRAIN_EPISODES = 200


class QMMEngine:
    """The master compiler. Collides all 29 dimensions into one vector.

    Usage::

        engine = QMMEngine(telemetry, seed=42)
        result = engine.execute()

    The result is a plain dict. Kernel aborts surface as
    ``{"error": ...}`` unless ``raise_on_abort=True``.
    """

    VERSION = __version__
    DIMENSIONS = 29

    def __init__(
        self,
        telemetry: dict[str, Any] | PatientTelemetry,
        *,
        seed: int = 42,
        outcome_tracker: OutcomeTracker | None = None,
    ) -> None:
        # Validate input (SPOF #29)
        if isinstance(telemetry, PatientTelemetry):
            self.t: PatientTelemetry = telemetry
        else:
            self.t = PatientTelemetry(**telemetry)

        # SPOF #32: injected, deterministic RNG
        self.seed = seed
        self.rng = np.random.default_rng(seed)

        t = self.t

        # ── Core models ──
        self.genome = GenomicTensor(t.genetics)
        self.allele_freq = self.genome.calc_population_prior()
        self.clearance = RenalHepaticClearance(t.gfr, t.hepatic_flow, t.albumin, t.biological_age)
        self.ddi = DrugDrugInteractionTensor()
        self.cytokine = CytokineStormVector()
        self.vagal = VagalToneVoltage(t.hrv_rmssd, t.cortisol_nadir)
        self.hypoxia = HypoxiaTensor(t.spo2, t.tissue_po2)
        self.microbiome = MicrobiomeMetabolizer(t.microbiome_diversity, t.pathobionts)
        self.nutrients = NutrientSubstrateMatrix(t.nutrients)
        self.chrono = ChronopharmacologyModulator(t.hour)
        self.epigenetic = EpigeneticAgeClock(t.age, t.methylation_pace)
        self.autophagy = AutophagyApoptosisToggle(t.mtor_activity, t.ampk_activity)
        self.anti_persona = AntiPersonaEscapeV2()
        self.pk_solver = TimeSeriesPKSolver()  # v27 parity
        self.multi_pk = MultiCompartmentPK()
        self.hpa = HPAAxisModel(t.cortisol_8am, t.cortisol_nadir, t.dhea_s, t.hour)
        self.organ_crosstalk = OrganCrosstalkTensor(t.organ_states)
        self.toxins = ExogenousToxinLoad(t.toxins)
        self.sleep = SleepArchitectureTensor(
            t.total_sleep_hours,
            t.n3_percentage,
            t.rem_percentage,
            t.sleep_efficiency,
            t.awakenings,
        )
        self.nti = NarrowTherapeuticIndexEngine()
        self.quantum_receptor = QuantumDrugReceptor(t.n_receptors, t.n_simulations, rng=self.rng)
        self.game_theory = PathogenGameTheory()
        self.qsense = QSenseGovernor()
        self.ledger = SpofLedger(allele_frequency=self.allele_freq)

        # ── Deep learning models (v29) ──
        self.neural_pk = NeuralPKPredictor(seed=seed) if t.use_neural_pk else None
        self.calibrator = BayesianCalibration() if t.use_bayesian_calibration else None
        self.adaptive_payoff = AdaptivePayoffMatrix() if t.use_adaptive_payoff else None
        self.rl_optimizer = (
            ReinforcementLearningOptimizer().with_seed(seed + 1) if t.use_rl_optimizer else None
        )
        # SPOF #34: injectable, never silently persistent
        self.outcome_tracker = outcome_tracker if outcome_tracker is not None else OutcomeTracker()

        self._drug_params = self._build_drug_params()

        # Structured phase events (SPOF #33)
        self._events: list[dict[str, Any]] = []

    def _build_drug_params(self) -> dict[str, Any]:
        """Merge default drug parameters with the provided ones."""
        defaults: dict[str, Any] = {
            "name": self.t.primary_drug,
            "dose": 40,
            "interval": 24,
            "therapeutic_min": 0.5,
            "therapeutic_max": 5.0,
            "renal_fraction": 0.3,
            "hepatic_extraction": 0.3,
            "protein_bound": 0.90,
            "vd": 0.25,
            "cyp_pathway": [],
            "kd": 0.5,
        }
        defaults.update(self.t.drug_params)
        return defaults

    def _phase(self, number: int, title: str) -> list[str]:
        lines: list[str] = []
        self._events.append({"phase": number, "title": title, "lines": lines})
        logger.info("PHASE %d: %s", number, title)
        return lines

    def execute(self, *, raise_on_abort: bool = False) -> dict[str, Any]:
        """Run the full 29-dimensional tensor collision."""
        results: dict[str, Any] = {}
        try:
            results.update(self._run_phases())
        except _KERNEL_ABORTS as exc:
            logger.critical("SYSTEM ABORT: %s", exc)
            if raise_on_abort:
                raise
            return {
                "error": str(exc),
                "version": self.VERSION,
                "events": self._events,
            }
        return results

    # ------------------------------------------------------------------
    def _run_phases(self) -> dict[str, Any]:
        t = self.t
        results: dict[str, Any] = {}

        # ── PHASE 1: Genomic ──
        lines = self._phase(1, "GENOMIC COLLISION")
        pk_mod = self.genome.calc_pharmacokinetic_modifier(t.primary_drug_class)
        lines.append(f"Allele frequency: {self.allele_freq:.4f} | PK modifier: {pk_mod}")
        results["pk_modifier"] = pk_mod

        # ── PHASE 2: Neural PK Prediction ──
        lines = self._phase(2, "NEURAL PK PREDICTION")
        if self.neural_pk is not None:
            neural_features = {
                "age": t.age,
                "bio_age": t.biological_age,
                "gfr": t.gfr,
                "albumin": t.albumin,
                "hepatic_flow": t.hepatic_flow,
                "cyp2c19_activity": pk_mod,
                "cyp3a4_activity": 1.0,
                "spo2": t.spo2,
                "body_weight": 70,
                "sex": 0,
            }
            neural_pred = self.neural_pk.predict(neural_features)
            lines.append(
                f"Neural PK: clearance={neural_pred['clearance_rate']:.3f}, "
                f"t½={neural_pred['t_half']:.2f}, Vd={neural_pred['vd']:.3f}"
            )
            lines.append(f"Confidence: {neural_pred['confidence']:.1%}")
            results["neural_pk"] = neural_pred
        else:
            lines.append("Neural PK disabled. Using analytical clearance model.")

        # ── PHASE 3: Clearance ──
        lines = self._phase(3, "RENAL/HEPATIC CLEARANCE")
        clearance_data = self.clearance.calc_total_clearance(self._drug_params)
        organ_risk = self.clearance.evaluate_organ_failure_risk()
        lines.append(
            f"Clearance: {clearance_data['clearance_rate']:.3f} | "
            f"t½: {clearance_data['t_half']:.2f}h"
        )
        lines.append(
            f"Free fraction: {clearance_data['free_fraction']:.3f} | "
            f"Vd: {clearance_data['vd_adjusted']:.2f}"
        )
        lines.append(f"Organ risk: {organ_risk}")
        if "KILL" in organ_risk:
            raise StrataRejection(organ_risk)
        results["clearance"] = clearance_data

        # ── PHASE 4: Toxins ──
        lines = self._phase(4, "EXOGENOUS TOXIN LOAD")
        toxin_derate = self.toxins.calc_toxin_cyp_derate()
        cyp2e1_ind = self.toxins.calc_cyp2e1_induction()
        gsh_frac = self.toxins.calc_glutathione_depletion()
        lines.append(
            f"Toxin CYP derate: {toxin_derate:.2f} | "
            f"CYP2E1: {cyp2e1_ind:.1f}x | GSH: {gsh_frac:.2f}"
        )
        results["toxin_derate"] = toxin_derate

        # ── PHASE 5: Hypoxia ──
        lines = self._phase(5, "HYPOXIA TENSOR")
        cyp_derate = self.hypoxia.calc_cyp450_derate()
        anaerobic_shift = self.hypoxia.calc_pathogen_anaerobic_shift()
        hif_boost = self.hypoxia.calc_hif1alpha_restitution_boost()
        combined_cyp = cyp_derate * toxin_derate
        lines.append(f"CYP derate: {cyp_derate:.2f} | Combined: {combined_cyp:.3f}")
        lines.append(f"Anaerobic shift: {anaerobic_shift:.1f}x | HIF-1α boost: {hif_boost:.1f}x")
        results["cyp_derate"] = combined_cyp

        # ── PHASE 6: HPA axis ──
        lines = self._phase(6, "HPA AXIS")
        adrenal = self.hpa.evaluate_adrenal_reserve()
        allostatic = self.hpa.calc_allostatic_load()
        anabolic_ratio = self.hpa.calc_anabolic_catabolic_ratio()
        current_cort = self.hpa.calc_circadian_cortisol()
        lines.append(
            f"Adrenal: {adrenal} | Cortisol: {current_cort:.1f} | Allostatic: {allostatic:.2f}"
        )
        lines.append(f"Anabolic/catabolic ratio: {anabolic_ratio:.2f}")
        if "KILL" in adrenal:
            raise StrataRejection(adrenal)
        results["allostatic_load"] = allostatic

        # ── PHASE 7: Organ crosstalk ──
        lines = self._phase(7, "ORGAN CROSSTALK")
        organ_adj = self.organ_crosstalk.calc_crosstalk_cascade()
        lines.append(f"Adjusted organs: {organ_adj}")
        results["organ_states"] = organ_adj

        # ── PHASE 8: DDI ──
        lines = self._phase(8, "DRUG-DRUG INTERACTIONS")
        ddi_warnings = self.ddi.check_interactions(t.drug_stack)
        lines.extend(ddi_warnings if ddi_warnings else ["No interactions detected."])
        results["ddi_warnings"] = ddi_warnings

        # ── PHASE 9: Chrono ──
        lines = self._phase(9, "CHRONOPHARMACOLOGY")
        chrono_eff = (
            self.chrono.calc_ppi_efficacy_window() if t.primary_drug_class == "PPI" else 1.0
        )
        immune_mod = self.chrono.calc_cortisol_immune_modulation()
        lines.append(f"Chrono efficacy: {chrono_eff:.2f} | Immune mod: {immune_mod:.2f}")
        results["chrono_efficacy"] = chrono_eff

        # ── PHASE 10: Microbiome ──
        lines = self._phase(10, "MICROBIOME")
        bioavail = self.microbiome.calc_bioavailability_modifier(t.primary_drug, t.route)
        ppi_shift = self.microbiome.calc_ppi_microbiome_shift(t.ppi_exposure_weeks)
        lines.append(f"Bioavailability mod: {bioavail:.2f}")
        results["bioavailability_modifier"] = bioavail
        results["ppi_microbiome_shift"] = ppi_shift

        # ── PHASE 11: Epigenetic + autophagy ──
        lines = self._phase(11, "EPIGENETIC & TISSUE MODE")
        repair_vel = self.epigenetic.calc_repair_velocity()
        telomere = self.epigenetic.calc_telomere_integrity(t.telomere_kb)
        tissue_mode, mtor_ratio = self.autophagy.evaluate_tissue_mode()
        lines.append(
            f"Bio age: {self.epigenetic.bio_age} | Repair vel: {repair_vel:.2f} | "
            f"Telomere: {telomere:.2f}"
        )
        lines.append(f"Tissue mode: {tissue_mode} (mTOR/AMPK={mtor_ratio:.2f})")
        if tissue_mode == "DEMOLITION":
            self.ledger.bayesian_update("linear_healing", False)

        # ── PHASE 12: Sleep ──
        lines = self._phase(12, "SLEEP ARCHITECTURE")
        gh_pulse = self.sleep.calc_gh_pulse()
        glymphatic = self.sleep.calc_glymphatic_clearance()
        immune_consol = self.sleep.calc_immune_consolidation()
        sleep_frag = self.sleep.calc_sleep_fragmentation_penalty()
        lines.append(
            f"N3: {self.sleep.calc_n3_hours():.1f}h | GH: {gh_pulse:.1f} | "
            f"Glymphatic: {glymphatic:.2f}"
        )

        # ── PHASE 13: Cytokine ──
        lines = self._phase(13, "CYTOKINE DYNAMICS")
        pathogen_k = t.pathogen_k * anaerobic_shift
        vagal_supp = self.vagal.calc_cholinergic_immune_suppression()
        immune_v = t.immune_v * immune_mod * vagal_supp * immune_consol * sleep_frag
        cytokine_state: dict[str, float] = {}
        for _ in range(_CYTOKINE_STEPS):
            cytokine_state = self.cytokine.step(
                pathogen_k,
                immune_v,
                hours=1.0,
                vagal_suppression=vagal_supp,
                cortisol_level=current_cort,
            )
        lines.append(
            f"IL-6={cytokine_state['IL-6']:.1f} | TNF-α={cytokine_state['TNF-α']:.1f} | "
            f"IL-10={cytokine_state['IL-10']:.1f}"
        )
        results["cytokine"] = cytokine_state

        # ── PHASE 14: Vagal + spasm ──
        lines = self._phase(14, "VAGAL TONE & SPASM")
        mod_spasm = self.vagal.modify_spasm_probability(t.spasm_prob)
        lines.append(f"Spasm: {t.spasm_prob:.2f} → {mod_spasm:.2f}")

        # ── PHASE 15: Nutrients ──
        lines = self._phase(15, "NUTRIENT SUBSTRATE")
        rest_capacity = self.nutrients.calc_restitution_capacity()
        lines.append(f"Restitution capacity: {rest_capacity:.2f}")

        # ── PHASE 16: Composite restitution ──
        lines = self._phase(16, "COMPOSITE RESTITUTION")
        if t.current_ph < CRITICAL_PH_THRESHOLD:
            restitution = 0.0
            self.ledger.bayesian_update("linear_healing", False)
            lines.append(f"pH={t.current_ph} < {CRITICAL_PH_THRESHOLD}. Restitution = 0.")
        else:
            restitution = (
                (1.0 - mod_spasm)
                * rest_capacity
                * repair_vel
                * telomere
                * hif_boost
                * min(1.0, gh_pulse / 2.0)
            )
            if tissue_mode == "DEMOLITION":
                restitution *= 0.1
            if allostatic > 3.0:
                restitution *= 0.5
            restitution = min(1.0, restitution)
            lines.append(f"Composite restitution: {restitution:.3f}")
        results["restitution"] = restitution

        # ── PHASE 17: Quantum receptor ──
        lines = self._phase(17, "QUANTUM RECEPTOR BINDING")
        eff_conc = float(self._drug_params.get("dose", 40)) * 0.001 * pk_mod * chrono_eff * bioavail
        receptor = self.quantum_receptor.calc_stochastic_occupancy(
            ligand_conc=eff_conc,
            kd=float(self._drug_params.get("kd", 0.5)),
            competitor_conc=t.competitor_conc,
            competitor_kd=t.competitor_kd,
            alpha=t.allosteric_alpha,
            spare_receptor_fraction=t.spare_receptors,
            strict=t.strict_receptor_gate,  # SPOF #37: opt-in kill-switch
        )
        lines.append(
            f"Occupancy: {receptor['mean_occupancy']:.1%} | "
            f"P(therapeutic): {receptor['p_therapeutic_effect']:.1%}"
        )
        results["receptor_occupancy"] = receptor

        # ── PHASE 18: Multi-compartment PK ──
        lines = self._phase(18, "MULTI-COMPARTMENT PK")
        k10 = (
            clearance_data["clearance_rate"]
            * combined_cyp
            * pk_mod
            * chrono_eff
            / clearance_data["vd_adjusted"]
        )
        pk_curve = self.multi_pk.solve_two_compartment(
            dose=float(self._drug_params.get("dose", 40)),
            bioavailability=bioavail,
            k10=k10,
            k12=t.k12,
            k21=t.k21,
            v_central=t.v_central,
            v_peripheral=t.v_peripheral,
            duration_hours=72,
            dosing_interval=float(self._drug_params.get("interval", 24)),
            num_doses=3,
        )
        pk_window = self.multi_pk.check_therapeutic_window(
            pk_curve,
            therapeutic_min=float(self._drug_params.get("therapeutic_min", 0.5)),
            therapeutic_max=(
                float(self._drug_params["therapeutic_max"])
                if self._drug_params.get("therapeutic_max") is not None
                else None
            ),
        )
        lines.append(f"Peak: {pk_window['peak']:.3f} | Trough: {pk_window['trough']:.3f}")
        lines.append(f"Subtherapeutic: {pk_window['fraction_subtherapeutic'] * 100:.0f}%")
        results["pk_window"] = pk_window
        is_subtherapeutic = bool(pk_window.get("subtherapeutic", False))

        # ── PHASE 19: NTI ──
        lines = self._phase(19, "NARROW THERAPEUTIC INDEX")
        nti_drugs = {"Warfarin", "Digoxin", "Lithium", "Phenytoin"}
        stack_names = {str(d["name"]) for d in t.drug_stack} | {t.primary_drug}
        detected = nti_drugs & stack_names
        if detected:
            lines.append(f"NTI drugs detected: {sorted(detected)}")
            if "Warfarin" in detected:
                warfarin = self.nti.check_warfarin(
                    vkorc1_genotype=self.genome.vkorc1,
                    cyp2c9_genotype=self.genome.cyp2c9,  # D-07 fix
                    vitamin_k_intake=t.vitamin_k_intake,
                    inr_current=t.inr,
                    interacting_drugs=[str(d["name"]) for d in t.drug_stack],
                )
                lines.append(f"Warfarin: INR in range={warfarin['inr_in_range']}")
                lines.append(f"Warfarin dose factor: {warfarin['recommended_dose_factor']:.2f}")
                results["nti_warfarin"] = warfarin
            if "Digoxin" in detected:
                digoxin = self.nti.check_digoxin(
                    digoxin_level=t.digoxin_level,
                    gfr=t.gfr,
                    potassium=t.potassium,
                    interacting_drugs=[str(d["name"]) for d in t.drug_stack],
                )
                lines.append(f"Digoxin: In range={digoxin['level_in_range']}")
                results["nti_digoxin"] = digoxin
        else:
            lines.append("No NTI drugs. Phase skipped.")

        # ── PHASE 20: Anti-persona + game theory ──
        lines = self._phase(20, "ANTI-PERSONA + GAME THEORY")
        escape = self.anti_persona.predict_escape_vectors(
            t.pathogen_name, t.primary_drug, t.exposure_hours, is_subtherapeutic
        )
        lines.append(f"Escape vectors: {sum(escape.values())}/5")

        if self.adaptive_payoff is not None:
            game: Any = self.adaptive_payoff
            lines.append(f"[ADAPTIVE] Learned payoff matrix ({game.n_updates} updates)")
        else:
            game = self.game_theory

        if hasattr(game, "find_nash_equilibria"):
            nash_list = game.find_nash_equilibria()
        elif hasattr(game, "find_nash_equilibrium"):
            nash_result = game.find_nash_equilibrium()
            nash_list = [nash_result] if isinstance(nash_result, dict) else list(nash_result)
        else:
            nash_list = []

        minimax = (
            game.calc_minimax()
            if hasattr(game, "calc_minimax")
            else (game.calc_minimax_strategy() if hasattr(game, "calc_minimax_strategy") else {})
        )
        mm_treatment = (
            minimax.get("minimax_treatment", "UNKNOWN") if isinstance(minimax, dict) else "UNKNOWN"
        )
        nash_count = len(nash_list) if isinstance(nash_list, list) else 0

        lines.append(f"Nash equilibria: {nash_count}")
        lines.append(f"Minimax treatment: {mm_treatment}")
        results["escape_vectors"] = escape
        results["nash_equilibria"] = nash_list
        results["minimax"] = minimax

        # ── PHASE 21: RL optimization ──
        lines = self._phase(21, "RL TREATMENT OPTIMIZATION")
        if self.rl_optimizer is not None:
            active_payoff = (
                self.adaptive_payoff.payoff_matrix
                if self.adaptive_payoff is not None
                else self.game_theory.PAYOFF_MATRIX
            )
            # D-08: pre-train instead of recommending from a zero table
            self.rl_optimizer.train(active_payoff, episodes=_RL_PRETRAIN_EPISODES)
            p_idx = (
                self.game_theory.PATHOGEN_STRATEGIES.index(t.pathogen_strategy)
                if t.pathogen_strategy in self.game_theory.PATHOGEN_STRATEGIES
                else 0
            )
            action = self.rl_optimizer.recommend_treatment(
                p_idx,
                immune_high=t.immune_v > 1.0,
                biofilm=t.biofilm,
                subtherapeutic=is_subtherapeutic,
            )
            treatment_name = self.game_theory.TREATMENT_STRATEGIES[action]
            lines.append(f"RL recommendation: {treatment_name} (action={action})")
            lines.append(
                f"RL episodes: {self.rl_optimizer.n_episodes} | ε={self.rl_optimizer.epsilon:.3f}"
            )
            results["rl_recommendation"] = treatment_name
            results["rl_summary"] = self.rl_optimizer.summary()
        else:
            lines.append("RL optimizer disabled.")

        # ── PHASE 22: Bayesian calibration ──
        lines = self._phase(22, "BAYESIAN CALIBRATION")
        if self.calibrator is not None:
            summary = self.calibrator.summary()
            lines.append(f"Observations: {summary['total_observations']}")
            lines.append(f"Binary conditions: {summary['binary_conditions']}")
            lines.append(f"Continuous params: {summary['continuous_parameters']}")
            results["calibration"] = summary
        else:
            lines.append("Calibration disabled.")

        # ── PHASE 23: Lagom throttle ──
        lines = self._phase(23, "LAGOM THROTTLE")
        stack_size = self.qsense.apply_lagom_throttle(len(t.drug_stack), t.entropy_estimate)
        lines.append(f"Optimal stack size: {stack_size}")
        results["lagom_stack_size"] = stack_size

        # ── PHASE 24: Ragnar compilation + crypto seal ──
        lines = self._phase(24, "RAGNAR COMPILATION")
        compiled = (
            f"v{self.VERSION}|PK:{pk_mod:.3f}|"
            f"CLR:{clearance_data['clearance_rate']:.3f}|"
            f"FF:{clearance_data['free_fraction']:.3f}|"
            f"Vd:{clearance_data['vd_adjusted']:.2f}|"
            f"t½:{clearance_data['t_half']:.1f}|CYP:{combined_cyp:.3f}|"
            f"CHRONO:{chrono_eff:.2f}|MICRO:{bioavail:.2f}|"
            f"EPI:{repair_vel:.2f}|TLM:{telomere:.2f}|MODE:{tissue_mode}|"
            f"HPA:{allostatic:.2f}|IL6:{cytokine_state['IL-6']:.1f}|"
            f"TNF:{cytokine_state['TNF-α']:.1f}|IL10:{cytokine_state['IL-10']:.1f}|"
            f"VAG:{self.vagal.vagal_integrity:.2f}|SPASM:{mod_spasm:.2f}|"
            f"NUTR:{rest_capacity:.2f}|REST:{restitution:.3f}|"
            f"GH:{gh_pulse:.1f}|GLYMPH:{glymphatic:.2f}|"
            f"QRECEPT:{receptor['mean_occupancy']:.2f}|"
            f"P_THER:{receptor['p_therapeutic_effect']:.2f}|"
            f"PK_SUB:{pk_window['fraction_subtherapeutic']:.2f}|"
            f"ESC:{sum(escape.values())}|STACK:{stack_size}|AF:{self.allele_freq:.4f}|"
            f"NEURAL:{1 if self.neural_pk is not None else 0}|"
            f"CALIB:{1 if self.calibrator is not None else 0}|"
            f"ADAPT:{1 if self.adaptive_payoff is not None else 0}|"
            f"RL:{1 if self.rl_optimizer is not None else 0}"
        )
        crypto_seal = hashlib.sha256(compiled.encode()).hexdigest()[:16]
        lines.append(f"COLLISION COMPLETE. RAGNAR HASH: {crypto_seal}")
        lines.append(compiled)

        results["hash"] = crypto_seal
        results["version"] = self.VERSION
        results["compiled_state"] = compiled
        results["surviving_priors"] = self.ledger.get_surviving_priors()
        results["events"] = self._events

        # ── PHASE 25: Outcome tracking (single log, D-14) ──
        lines = self._phase(25, "OUTCOME TRACKING")
        self.outcome_tracker.log_prediction(
            crypto_seal,
            {
                "restitution": restitution,
                "receptor_occupancy": receptor["mean_occupancy"],
                "pk_subtherapeutic": pk_window["fraction_subtherapeutic"],
                "escape_vectors": sum(escape.values()),
            },
        )
        lines.append(f"Logged prediction {crypto_seal} for outcome tracking.")

        return results


__all__ = ["QMMEngine"]
