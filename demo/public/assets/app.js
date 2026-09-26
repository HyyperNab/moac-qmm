/* ═════════════════════════════════════════════════════════════════
   MOAC QMM — Custom Drug Delivery Protocol · demo client
   talks to the REAL kernel running serverless at /api/*
   ═════════════════════════════════════════════════════════════════ */

"use strict";

const PRESETS = {
  edge: {
    desc: "<strong>Esomeprazole 40mg OD</strong> (a PPI) in the original edge-case patient: CYP2C19 *17/*17 ultra-rapid metabolizer, H. pylori in biofilm mode, dysbiotic microbiome, hypoalbuminemia (3.2 g/dL), chronic toxin load, sleep-deprived, catabolic. Watch the engine expose why a standard PPI dose underperforms here.",
    telemetry: {
      genetics: { "CYP2C19": "*17/*17", "CYP3A4": "*1/*1", "CYP2D6": "*1/*1",
                 "HLA-B": "Negative", "SLCO1B1": "*1/*1", "VKORC1": "*1/*1" },
      primary_drug: "Esomeprazole", primary_drug_class: "PPI", route: "oral",
      drug_params: { name: "Esomeprazole", dose: 40, interval: 24,
                     therapeutic_min: 0.5, therapeutic_max: 5.0,
                     renal_fraction: 0.2, hepatic_extraction: 0.8,
                     protein_bound: 0.95, vd: 0.25,
                     cyp_pathway: ["CYP2C19", "CYP3A4"], kd: 0.8 },
      drug_stack: [
        { name: "Esomeprazole", protein_bound: 0.95, cyp_pathway: ["CYP2C19", "CYP3A4"] },
        { name: "Clarithromycin", protein_bound: 0.70, cyp_pathway: ["CYP3A4"] },
        { name: "Magnesium_Bisglycinate", protein_bound: 0.10, cyp_pathway: [] },
        { name: "Alginate", protein_bound: 0.05, cyp_pathway: [] }
      ],
      k12: 0.15, k21: 0.10, v_central: 0.15, v_peripheral: 0.10,
      age: 52, biological_age: 61, methylation_pace: 1.17, telomere_kb: 6.2,
      gfr: 72, hepatic_flow: 1100, albumin: 3.2,
      organ_states: { gut: 0.4, liver: 0.65, kidney: 0.7, heart: 0.85, lung: 0.75, brain: 0.9 },
      current_ph: 3.5, spasm_prob: 0.3,
      spo2: 94.0, tissue_po2: 28.0,
      hrv_rmssd: 18.0, cortisol_nadir: 12.0, cortisol_8am: 28.0, dhea_s: 85.0,
      pathogen_name: "Helicobacter pylori",
      pathogen_k: 0.3, immune_v: 1.2, biofilm: false,
      exposure_hours: 18, th1_th2_ratio: 1.5,
      pathogen_strategy: "BIOFILM_FORTIFY",
      microbiome_diversity: 2.1, pathobionts: ["Enterococcus faecalis"],
      ppi_exposure_weeks: 8,
      nutrients: { glutamine: 0.3, zinc: 4.0, vitamin_c: 60.0,
                   vitamin_a: 700.0, arginine: 2.0, n3_index: 4.0 },
      mtor_activity: 0.3, ampk_activity: 0.8,
      hour: 22.0,
      total_sleep_hours: 5.5, n3_percentage: 8.0,
      rem_percentage: 15.0, sleep_efficiency: 0.72, awakenings: 5,
      toxins: { lead: 3.2, mercury: 2.0, alcohol_chronic: 45.0 }
    }
  },
  healthy: {
    desc: "<strong>Esomeprazole 40mg OD</strong> in a physiologically stable reference patient: normal-genotype, no toxins, adequate sleep and substrates, planktonic pathogen under immune control. The protocol survives — see what a clean pass looks like.",
    telemetry: {
      genetics: { "CYP2C19": "*1/*1" },
      primary_drug: "Esomeprazole", primary_drug_class: "PPI", route: "oral",
      drug_params: { dose: 40, kd: 0.8, protein_bound: 0.95, vd: 0.25,
                     cyp_pathway: ["CYP2C19"], renal_fraction: 0.2,
                     hepatic_extraction: 0.8, therapeutic_min: 0.5 },
      drug_stack: [ { name: "Esomeprazole", protein_bound: 0.95, cyp_pathway: ["CYP2C19"] } ],
      gfr: 90, hepatic_flow: 1500, albumin: 4.0, current_ph: 5.0,
      spo2: 98, tissue_po2: 40, hrv_rmssd: 50, hour: 8.0,
      pathogen_name: "H. pylori", pathogen_k: 0.1, immune_v: 2.0,
      exposure_hours: 2, pathogen_strategy: "PLANKTONIC_FAST",
      age: 35, biological_age: 35, telomere_kb: 10.0,
      cortisol_8am: 15, cortisol_nadir: 3, dhea_s: 200,
      total_sleep_hours: 8, n3_percentage: 18,
      mtor_activity: 0.6, ampk_activity: 0.4,
      microbiome_diversity: 3.5, pathobionts: [],
      nutrients: { glutamine: 0.5, zinc: 8, vitamin_c: 75,
                   vitamin_a: 900, arginine: 4, n3_index: 8 },
      organ_states: { gut: 1, liver: 1, kidney: 1, heart: 1, lung: 1, brain: 1 }
    }
  },
  valproate: {
    desc: "<strong>Valproate 500mg OD</strong> (an antiepileptic, ~92% protein-bound, mainly hepatic elimination via CYP2C9/CYP2C19 and glucuronidation) in a hypoalbuminemic (3.2 g/dL), alcohol-exposed, catabolic 52-year-old. Watch the free-fraction and exposure findings — the classic valproate traps.",
    telemetry: {
      genetics: { "CYP2C19": "*17/*17", "CYP3A4": "*1/*1", "CYP2D6": "*1/*1",
                 "CYP2C9": "*1/*2", "HLA-B": "Negative",
                 "SLCO1B1": "*1/*1", "VKORC1": "*1/*1" },
      primary_drug: "Valproate", primary_drug_class: "Antiepileptic", route: "oral",
      drug_params: { name: "Valproate", dose: 500, interval: 24,
                     therapeutic_min: 50, therapeutic_max: 100,
                     renal_fraction: 0.05, hepatic_extraction: 0.9,
                     protein_bound: 0.92, vd: 0.15,
                     cyp_pathway: ["CYP2C9", "CYP2C19"], kd: 1.2 },
      drug_stack: [
        { name: "Valproate", protein_bound: 0.92, cyp_pathway: ["CYP2C9", "CYP2C19"] },
        { name: "Magnesium_Bisglycinate", protein_bound: 0.10, cyp_pathway: [] }
      ],
      k12: 0.15, k21: 0.10, v_central: 0.15, v_peripheral: 0.10,
      age: 52, biological_age: 61, methylation_pace: 1.17, telomere_kb: 6.2,
      gfr: 72, hepatic_flow: 1100, albumin: 3.2,
      organ_states: { gut: 0.4, liver: 0.65, kidney: 0.7, heart: 0.85, lung: 0.75, brain: 0.9 },
      current_ph: 6.5, spasm_prob: 0.3,
      spo2: 94, tissue_po2: 28,
      hrv_rmssd: 18, cortisol_nadir: 12, cortisol_8am: 28, dhea_s: 85,
      pathogen_name: "None", pathogen_k: 0.0, immune_v: 1.0, biofilm: false,
      exposure_hours: 0, th1_th2_ratio: 1.0, pathogen_strategy: "PLANKTONIC_FAST",
      microbiome_diversity: 2.1, pathobionts: [], ppi_exposure_weeks: 0,
      nutrients: { glutamine: 0.3, zinc: 4, vitamin_c: 60,
                   vitamin_a: 700, arginine: 2, n3_index: 4 },
      mtor_activity: 0.3, ampk_activity: 0.8, hour: 22,
      total_sleep_hours: 5.5, n3_percentage: 8, rem_percentage: 15,
      sleep_efficiency: 0.72, awakenings: 5,
      toxins: { lead: 3.2, mercury: 2, alcohol_chronic: 45 }
    }
  }
};

/* ── demo state ──────────────────────────────────────────── */
let mode = "edge";

const $ = (id) => document.getElementById(id);
const fmt = (v, d = 3) => (typeof v === "number" ? v.toFixed(d) : String(v));
const pct = (v, d = 1) => (100 * v).toFixed(d) + "%";

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function currentTelemetry() {
  let telemetry;
  if (mode === "custom") {
    try {
      telemetry = JSON.parse($("customJson").value);
      $("jsonError").classList.add("hidden");
    } catch (err) {
      $("jsonError").textContent = "Invalid JSON: " + err.message;
      $("jsonError").classList.remove("hidden");
      return null;
    }
  } else {
    telemetry = JSON.parse(JSON.stringify(PRESETS[mode].telemetry));
  }
  telemetry.use_neural_pk = $("tNeural").checked;
  telemetry.use_bayesian_calibration = $("tCalib").checked;
  telemetry.use_adaptive_payoff = $("tAdapt").checked;
  telemetry.use_rl_optimizer = $("tRL").checked;
  telemetry.strict_receptor_gate = $("tStrict").checked;
  return telemetry;
}

function setMode(next) {
  mode = next;
  document.querySelectorAll(".preset-btn").forEach(b =>
    b.classList.toggle("active", b.dataset.preset === next)
  );
  const isCustom = next === "custom";
  $("customJsonWrap").classList.toggle("hidden", !isCustom);
  $("presetDesc").classList.toggle("hidden", isCustom);
  if (isCustom) {
    $("customJson").value = JSON.stringify(PRESETS.valproate.telemetry, null, 2);
    $("presetDesc").classList.add("hidden");
  } else {
    $("presetDesc").innerHTML = PRESETS[next].desc;
  }
}

/* ── API ─────────────────────────────────────────────────── */
async function api(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data.detail;
    let msg = `HTTP ${res.status}`;
    if (Array.isArray(detail)) {
      msg = detail.map(d => `${(d.loc || []).join(".")}: ${d.msg}`).join("\n");
    } else if (detail) {
      msg = typeof detail === "string" ? detail : JSON.stringify(detail);
    }
    throw new Error(msg);
  }
  return data;
}

/* ── clinical interpretation ──────────────────────────────── */
const ABORT_MAP = [
  ["CLEARANCE-KILL", "Kidney function below the safe floor",
   "The simulation refuses this protocol: with a GFR under 30 mL/min, renally-cleared drugs accumulate to toxic levels in this profile. Renal dose adjustment — or a drug with a non-renal elimination path — is required before the protocol can pass."],
  ["DDI-KILL", "Protein-binding conflict in the drug stack",
   "Two or more highly albumin-bound drugs in this stack displace each other; the simulated unbound fraction explodes, which behaves like an unplanned overdose. Separate the competing drugs or replace one with a less protein-bound alternative."],
  ["CYTOKINE-STORM", "Immune overdrive",
   "The simulated inflammatory loop crossed storm thresholds (IL-6 and TNF-α both critical). The engine stops here: drug action on top of an uncontrolled inflammatory cascade is not interpretable in this model."],
  ["TOXIN-KILL", "Background toxin overload",
   "A background toxin (lead, mercury or alcohol) reached twice its toxic threshold. The engine stops before simulating drug action on top of an acute toxic load."],
  ["CROSSTALK-KILL", "Multi-organ failure trajectory",
   "Two or more organs fell below the failure line and the degradation graph cascades. In this simulated state no drug protocol is evaluated — the multi-organ failure itself dominates."],
  ["HPA-KILL", "Adrenal insufficiency",
   "Morning cortisol is below the survival floor in this profile. Stress-dose steroid support is simulated as required before any other therapy reasoning is meaningful."],
  ["NTI-KILL", "Narrow-therapeutic-index breach",
   "A narrow-index drug (warfarin/digoxin type) crossed out of its safe range in the simulation. These drugs have almost no margin — the engine treats a breach as a hard stop."],
  ["HYPOXIA-KILL", "Oxygenation below survival threshold",
   "SpO2 fell below the floor at which the liver's CYP450 enzymes can clear drugs at all. Every hepatically cleared drug accumulates unbound in this state."],
  ["QUANTUM-RECEPTOR", "Target engagement below the strict gate",
   "With the strict receptor gate enabled, the Monte-Carlo simulation aborted: the probability of therapeutic receptor engagement stayed under 50% of runs. Increase the dose, remove a competitor, or switch class — or disable the strict gate to record this as a warning instead of an abort."],
  ["ANTI-PERSONA-ESCAPE", "Pathogen adaptation cascade",
   "Three or more resistance escape vectors activated simultaneously (efflux pumps, persisters, target mutation, biofilm). The simulated pathogen is winning the evolutionary race against this drug — the protocol needs a fundamentally different strategy, not a higher dose."],
  ["GAME-THEORY-KILL", "Pathogen plays a dominant strategy",
   "In the game-theory matrix, the pathogen's current strategy dominates the chosen treatment: no dosing of this agent wins. Switch to the minimax-optimal strategy shown in the metrics."],
];

function finding(severity, title, text) {
  const icon = { critical: "⛔", warning: "⚠", note: "◆", good: "✓" }[severity];
  return `<div class="finding ${severity}"><div class="finding-icon">${icon}</div>` +
    `<div class="finding-body"><div class="finding-title">${title}</div>` +
    `<div class="finding-text">${text}</div></div></div>`;
}

function renderInterpretation(r, telemetry) {
  const findings = [];
  const drug = escapeHtml(telemetry.primary_drug || "the drug");
  const dp = telemetry.drug_params || {};

  if (r.error) {
    const err = String(r.error);
    const hit = ABORT_MAP.find(m => err.includes(m[0]));
    if (hit) {
      findings.push(finding("critical", hit[1], hit[2]));
    } else {
      findings.push(finding("critical", "The simulation aborted",
        `The kernel stopped this protocol: <strong>${escapeHtml(err)}</strong>. The named constraint must be resolved in the patient profile or the drug protocol before the simulation can complete.`));
    }
    findings.push(finding("note", "How to read this",
      "An abort is a result, not a crash: the engine refuses to average past a hard biological limit. Adjust the offending field in the JSON (left panel) and re-run — the phase-by-phase numbers are in the raw JSON below."));
    $("findings").innerHTML = findings.join("");
    return;
  }

  /* 1 — metabolism */
  if (r.pk_modifier !== undefined) {
    if (r.pk_modifier < 0.9) {
      findings.push(finding("warning", "Genetics cut the drug exposure",
        `The simulated PK modifier is <strong>${fmt(r.pk_modifier, 2)}</strong> — the genetics in this profile (ultra-rapid CYP2C19) reduce ${drug}'s expected exposure to roughly ${pct(r.pk_modifier, 0)} of standard. Standard dosing under-treats; a dose increase or a metabolism-independent alternative is the classic lever.`));
    } else if (r.pk_modifier > 1.5) {
      findings.push(finding("warning", "Slow metabolism accumulates the drug",
        `The simulated PK modifier is <strong>${fmt(r.pk_modifier, 2)}</strong> — poor-metabolizer genetics. Expect roughly ${fmt(r.pk_modifier, 1)}× normal exposure per dose; accumulation and dose reduction are the concerns.`));
    } else {
      findings.push(finding("good", "Standard metabolism assumed",
        `The simulated PK modifier is <strong>${fmt(r.pk_modifier, 2)}</strong> — no loss- or gain-of-function alleles in the pathways this model tracks for ${drug}.`));
    }
  }

  /* 2 — free fraction */
  if (r.clearance) {
    const bound = typeof dp.protein_bound === "number" ? dp.protein_bound : 0.9;
    const expectedFree = 1 - bound;
    const actualFree = r.clearance.free_fraction;
    if (actualFree > expectedFree * 1.6) {
      findings.push(finding("warning", "Low albumin amplifies the active dose",
        `With albumin at <strong>${fmt(telemetry.albumin, 1)} g/dL</strong>, the unbound (active) fraction of ${drug} rises from ~${pct(expectedFree, 1)} at normal albumin to <strong>${pct(actualFree, 1)}</strong> — about <strong>${fmt(actualFree / expectedFree, 1)}×</strong> more active drug per total dose. For a highly protein-bound drug this is the classic toxicity trap: the total level looks normal while the free level does not.`));
    }
  }

  /* 3 — exposure & dosing */
  if (r.pk_window && r.clearance) {
    const sub = r.pk_window.fraction_subtherapeutic;
    const supra = r.pk_window.fraction_supratherapeutic || 0;
    if (sub > 0.3) {
      findings.push(finding("critical", "The dosing interval cannot hold the window",
        `The simulated concentration spends <strong>${pct(sub, 0)}</strong> of the dosing interval below the therapeutic floor — the simulated half-life is only <strong>${fmt(r.clearance.t_half, 2)} h</strong> against a ${dp.interval || 24}-hour interval. Therapeutically this reads as: the dose works briefly, then fades for hours. Levers: divide the daily dose (BD/TDS), shorten the interval, or use a longer-acting formulation — then re-check the toxicity margin.`));
    }
    if (supra > 0.1) {
      findings.push(finding("warning", "Supra-therapeutic peaks",
        `The simulated curve spends <strong>${pct(supra, 0)}</strong> of the interval above the therapeutic ceiling — peak-related toxicity (for ${drug}: dose-related CNS/GI effects in real pharmacology) would be expected in this profile.`));
    }
    if (sub <= 0.3 && supra <= 0.1) {
      findings.push(finding("good", "Exposure stays inside the window",
        `Only ${pct(sub, 0)} of the interval falls below the floor and ${pct(supra, 0)} above the ceiling — this simulated dose/interval combination holds the therapeutic window for ${drug}.`));
    }
  }

  /* 4 — target engagement */
  if (r.receptor_occupancy) {
    const occ = r.receptor_occupancy;
    if (occ.p_therapeutic_effect < 0.5) {
      findings.push(finding("warning", "Target engagement is insufficient at this concentration",
        `Monte-Carlo receptor simulation: mean occupancy <strong>${pct(occ.mean_occupancy, 1)}</strong> against a therapeutic threshold of ${pct(occ.therapeutic_threshold, 0)} — the probability of a therapeutic effect is ~<strong>${pct(occ.p_therapeutic_effect, 1)}</strong>. In plain terms: at this simulated dose and affinity (Kd ${fmt(dp.kd, 2)}), the drug does not occupy enough of its target, in essentially any of the simulated runs. Levers: raise the dose, lower Kd (different molecule), or remove the competitor.`));
    }
  }

  /* 5 — systemic resilience */
  if (r.allostatic_load !== undefined && r.allostatic_load > 3) {
    findings.push(finding("warning", "Catabolic dominance (HPA axis)",
      `The allostatic load is <strong>${fmt(r.allostatic_load, 1)}</strong> (normal ≈ 1) — cortisol dominates DHEA by a wide margin in this profile. Clinically-styled reading: tissue repair, immune competence and drug tolerance are all suppressed; addressing the adrenal state is a precondition for the rest of therapy to work.`));
  }

  /* 6 — healing capacity */
  if (r.restitution !== undefined) {
    if (r.restitution < 0.05) {
      const drivers = [];
      if ((telemetry.current_ph || 0) < 4) drivers.push("gastric pH below the restitution floor");
      if (telemetry.mtor_activity / Math.max(0.01, telemetry.ampk_activity || 1) < 0.5) drivers.push("demolition-mode tissue signaling (mTOR ≪ AMPK)");
      if ((telemetry.total_sleep_hours || 8) * (telemetry.sleep_efficiency || 1) * ((telemetry.n3_percentage || 15) / 100) < 1.5) drivers.push("deep-sleep debt (N3 < 1.5h)");
      findings.push(finding("critical", "Healing capacity is effectively zero",
        `The composite restitution score is <strong>${fmt(r.restitution, 3)}</strong>. ${drivers.length ? "Main drivers in this profile: " + drivers.join("; ") + "." : ""} Any mucosal recovery target is unreachable until these are corrected.`));
    } else if (r.restitution < 0.3) {
      findings.push(finding("warning", "Limited healing capacity",
        `The composite restitution score is <strong>${fmt(r.restitution, 3)}</strong> — healing is possible but slow in this profile.`));
    } else {
      findings.push(finding("good", "Healing capacity is intact",
        `The composite restitution score is <strong>${fmt(r.restitution, 3)}</strong> — substrate supply, tissue mode and hormonal background support recovery in this profile.`));
    }
  }

  /* 7 — inflammation */
  if (r.cytokine && r.cytokine["IL-6"] > 40) {
    const lagging = r.cytokine["IL-10"] < 0.1 * r.cytokine["IL-6"];
    findings.push(finding("warning", "Inflammatory burden is high",
      `Simulated IL-6 is <strong>${fmt(r.cytokine["IL-6"], 1)} pg/mL</strong> with TNF-α at ${fmt(r.cytokine["TNF-α"], 1)}${lagging ? " — and the counter-regulatory IL-10 response is lagging behind" : ""}. An inflammatory load of this size reshapes drug distribution and hepatic capacity on its own.`));
  }

  /* 8 — infection / resistance (only if a pathogen is in play) */
  const pathogenActive = telemetry.pathogen_k > 0 ||
    !["", "none", "unknown"].includes(String(telemetry.pathogen_name || "").toLowerCase());
  if (pathogenActive && r.escape_vectors) {
    const n = Object.values(r.escape_vectors).filter(Boolean).length;
    if (n > 0) {
      findings.push(finding("warning", "Pathogen is adapting to exposure",
        `${n}/5 resistance escape vectors are active in the simulation (efflux, persisters, target mutation, biofilm, enzymatic degradation). The longer the exposure profile stays marginal, the more of these switch on — and they do not switch back.`));
    }
    if (r.minimax && r.minimax.minimax_treatment) {
      findings.push(finding("note", "Game-theoretic strategy note",
        `Against the simulated pathogen there is no stable pure-strategy treatment (0 pure Nash equilibria). The minimax-optimal play is <strong>${escapeHtml(r.minimax.minimax_treatment)}</strong> — the strategy that limits the pathogen's best case${r.rl_recommendation ? `; the Q-learning agent recommends ${escapeHtml(r.rl_recommendation)} for this exact state` : ""}.`));
    }
  }

  /* 9 — ML PK estimate */
  if (r.neural_pk) {
    const heur = r.neural_pk.heuristic ? "heuristic mode (untrained), low confidence" : `confidence ${pct(r.neural_pk.confidence, 0)}`;
    findings.push(finding("note", "Machine-learning PK cross-check",
      `The neural PK estimator (${heur}) suggests clearance ${fmt(r.neural_pk.clearance_rate, 3)}, t½ ${fmt(r.neural_pk.t_half, 2)} h, Vd ${fmt(r.neural_pk.vd, 3)} — use it as a second opinion against the analytical model above, not as a replacement.`));
  }

  /* 10 — NTI results */
  if (r.nti_warfarin) {
    findings.push(finding(r.nti_warfarin.inr_in_range ? "good" : "warning", "Warfarin NTI check",
      `Simulated INR is ${r.nti_warfarin.inr_in_range ? "inside" : "outside"} the target range; genotype-adjusted recommended dose factor: <strong>${fmt(r.nti_warfarin.recommended_dose_factor, 2)}</strong> of standard.`));
  }
  if (r.nti_digoxin) {
    findings.push(finding(r.nti_digoxin.level_in_range ? "good" : "warning", "Digoxin NTI check",
      `Simulated digoxin level is ${r.nti_digoxin.level_in_range ? "inside" : "outside"} the therapeutic range${r.nti_digoxin.renal_adjustment_needed ? " — and renal adjustment is flagged (GFR < 60)" : ""}.`));
  }

  /* 11 — bottom line */
  findings.push(finding(findings.some(f => f.includes("critical")) ? "warning" : "good",
    "Bottom line",
    `The protocol <strong>${r.error ? "aborted" : "survived all 25 biological checks"}</strong> in this simulated patient. Every flag above is a lever: dose, interval, albumin, timing, competitor drugs — change one field in the JSON and re-run to see the system respond. Remember: these are outputs of an unverified research model, not dosing guidance.`));

  $("findings").innerHTML = findings.join("");
}

/* ── rendering ───────────────────────────────────────────── */
function metric(label, value, cls = "", sub = "") {
  return `<div class="metric"><div class="metric-label">${label}</div>` +
    `<div class="metric-value ${cls}">${value}</div>` +
    (sub ? `<div class="metric-sub">${sub}</div>` : "") + `</div>`;
}

function renderMetrics(r, telemetry) {
  const m = [];
  m.push(metric("PK modifier", fmt(r.pk_modifier, 2), r.pk_modifier < 1 ? "magenta" : "cyan",
    r.pk_modifier < 1 ? "ultra-rapid metabolizer" : "normal metabolizer"));
  if (r.neural_pk) {
    m.push(metric("Neural clearance", fmt(r.neural_pk.clearance_rate, 3), "magenta",
      `confidence ${pct(r.neural_pk.confidence, 0)}`));
  }
  if (r.clearance) {
    m.push(metric("Clearance", fmt(r.clearance.clearance_rate, 3), "cyan",
      `renal ${fmt(r.clearance.renal_component, 2)} + hepatic ${fmt(r.clearance.hepatic_component, 2)}`));
    m.push(metric("Half-life", fmt(r.clearance.t_half, 2) + "h"));
    m.push(metric("Free fraction", fmt(r.clearance.free_fraction, 3), "amber",
      "unbound, active part"));
    m.push(metric("Vd adjusted", fmt(r.clearance.vd_adjusted, 2)));
  }
  if (r.cyp_derate !== undefined) {
    m.push(metric("CYP derate", fmt(r.cyp_derate, 3), r.cyp_derate < 0.8 ? "amber" : "",
      "hypoxia × toxins"));
  }
  if (r.chrono_efficacy !== undefined) {
    m.push(metric("Chrono efficacy", fmt(r.chrono_efficacy, 2),
      r.chrono_efficacy < 1 ? "amber" : "green"));
  }
  if (r.allostatic_load !== undefined) {
    m.push(metric("Allostatic load", fmt(r.allostatic_load, 2),
      r.allostatic_load > 3 ? "red" : "", "normal = 1.0"));
  }
  if (r.cytokine) {
    m.push(metric("IL-6 / TNF-α",
      `${fmt(r.cytokine["IL-6"], 1)} / ${fmt(r.cytokine["TNF-α"], 1)}`,
      r.cytokine["IL-6"] > 80 ? "red" : "green", "pg/mL"));
  }
  if (r.restitution !== undefined) {
    m.push(metric("Restitution", fmt(r.restitution, 3),
      r.restitution < 0.05 ? "red" : r.restitution < 0.3 ? "amber" : "green",
      "composite healing capacity"));
  }
  if (r.receptor_occupancy) {
    m.push(metric("Receptor occupancy", pct(r.receptor_occupancy.mean_occupancy, 1), "cyan",
      `P(therapeutic) ${pct(r.receptor_occupancy.p_therapeutic_effect, 1)}`));
  }
  if (r.pk_window) {
    m.push(metric("Subtherapeutic", pct(r.pk_window.fraction_subtherapeutic, 0),
      r.pk_window.subtherapeutic ? "red" : "green", "share of interval"));
  }
  if (pathogenActive(telemetry) && r.escape_vectors) {
    const n = Object.values(r.escape_vectors).filter(Boolean).length;
    m.push(metric("Escape vectors", `${n}/5`, n >= 3 ? "red" : n > 0 ? "amber" : "green",
      "pathogen adaptation"));
  }
  if (r.minimax) m.push(metric("Minimax strategy", escapeHtml(r.minimax.minimax_treatment), "cyan"));
  if (r.nash_equilibria) m.push(metric("Pure Nash", String(r.nash_equilibria.length), "magenta",
    "0 = no stable pure strategy"));
  if (r.rl_recommendation) m.push(metric("RL recommends", escapeHtml(r.rl_recommendation), "green",
    "pre-trained Q-agent"));
  if (r.nti_warfarin) m.push(metric("Warfarin dose factor", fmt(r.nti_warfarin.recommended_dose_factor, 2),
    r.nti_warfarin.inr_in_range ? "green" : "amber", "genotype-adjusted"));
  if (r.nti_digoxin) m.push(metric("Digoxin in range", r.nti_digoxin.level_in_range ? "yes" : "no",
    r.nti_digoxin.level_in_range ? "green" : "amber"));
  if (r.lagom_stack_size !== undefined) {
    m.push(metric("Lagom stack", String(r.lagom_stack_size), "", "poly-pharmacy budget"));
  }
  if (r.surviving_priors) {
    m.push(metric("Surviving priors", `${Object.keys(r.surviving_priors).length}/10`,
      Object.keys(r.surviving_priors).length < 10 ? "amber" : "green", "assumption ledger"));
  }
  $("metrics").innerHTML = m.join("");
}

function pathogenActive(telemetry) {
  return telemetry.pathogen_k > 0 ||
    !["", "none", "unknown"].includes(String(telemetry.pathogen_name || "").toLowerCase());
}

function renderRx(rx) {
  const grid = $("rxGrid");
  if (!rx || Object.keys(rx).length === 0) {
    grid.innerHTML = `<div class="rx-empty">✓ No corrections required — the profile is already stable across every dimension the optimizer checks.</div>`;
    return;
  }
  grid.innerHTML = Object.entries(rx).map(([cat, d]) => {
    let body = "";
    for (const [k, v] of Object.entries(d || {})) {
      if (Array.isArray(v)) {
        body += `<ul>${v.map(i => `<li>${escapeHtml(i)}</li>`).join("")}</ul>`;
      } else if (typeof v === "object" && v !== null) {
        body += `<div class="rx-line"><b>${escapeHtml(k)}:</b> ${escapeHtml(JSON.stringify(v))}</div>`;
      } else {
        body += `<div class="rx-line"><b>${escapeHtml(k)}:</b> ${escapeHtml(v)}</div>`;
      }
    }
    return `<div class="rx-card"><h4>${escapeHtml(cat)}</h4>${body}</div>`;
  }).join("");
}

function renderStatus(r) {
  const banner = $("statusBanner");
  if (r.error) {
    banner.className = "status-banner status-abort";
    banner.innerHTML = `⚠ SYSTEM ABORT — ${escapeHtml(r.error)}`;
  } else {
    banner.className = "status-banner status-ok";
    banner.innerHTML = `✓ COLLISION COMPLETE — RAGNAR HASH <span class="hash">${r.hash}</span>`;
  }
}

/* ── run ─────────────────────────────────────────────────── */
async function run() {
  const telemetry = currentTelemetry();
  if (telemetry === null) return;

  const seed = Number($("seedInput").value) >>> 0;
  const btn = $("runBtn");
  const status = $("runStatus");

  btn.disabled = true;
  status.classList.remove("hidden", "err");
  status.textContent = "◇ colliding 25 biological checks…";

  try {
    const [result, rx] = await Promise.all([
      api("/api/simulate", { telemetry, seed }),
      api("/api/optimize", { telemetry }),
    ]);

    $("resultsEmpty").classList.add("hidden");
    $("resultsBody").classList.remove("hidden");
    renderStatus(result);
    renderInterpretation(result, telemetry);
    $("metricsWrap").classList.toggle("hidden", !!result.error);
    if (!result.error) renderMetrics(result, telemetry);
    renderRx(rx);
    $("rawJson").textContent = JSON.stringify(result, null, 2);
    status.textContent = "✓ done — interpretation first, numbers below";
  } catch (err) {
    status.classList.add("err");
    status.textContent = "✗ " + err.message;
  } finally {
    btn.disabled = false;
  }
}

/* ── wire up ──────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  setMode("edge");
  document.querySelectorAll(".preset-btn").forEach(b =>
    b.addEventListener("click", () => setMode(b.dataset.preset))
  );
  $("runBtn").addEventListener("click", run);

  fetch("/api/health")
    .then(r => r.json())
    .then(h => { document.title = `MOAC QMM v${h.version} — Custom Drug Delivery Protocol`; })
    .catch(() => {});
});
