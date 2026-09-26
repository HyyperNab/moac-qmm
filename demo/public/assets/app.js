/* ═════════════════════════════════════════════════════════════════
   MOAC QMM — live demo client
   talks to the REAL kernel running serverless at /api/*
   ═════════════════════════════════════════════════════════════════ */

"use strict";

const PHASES = [
  ["Genomic collision", "CYP450 genotype → PK modifier. *17/*17 ultra-rapid metabolizers get 35% PPI efficacy; rare genotypes thin the evidence base."],
  ["Neural PK prediction", "MC-Dropout MLP predicts clearance/t½/Vd with epistemic uncertainty; heuristic fallback when untrained."],
  ["Renal/hepatic clearance", "GFR + hepatic flow + albumin + age → total clearance, free fraction, adjusted Vd. GFR < 30 → CLEARANCE-KILL."],
  ["Exogenous toxin load", "Lead derates CYP450 synthesis, mercury drains glutathione, chronic alcohol induces CYP2E1. 2× toxic threshold → TOXIN-KILL."],
  ["Hypoxia tensor", "SpO2 below the CYP450 floor → drug clearance collapses (HYPOXIA-KILL). Tissue pO2 drives HIF-1α and anaerobic pathogen shift."],
  ["HPA axis", "Circadian cortisol cosine, allostatic load (cortisol/DHEA), anabolic/catabolic ratio. Adrenal insufficiency → HPA-KILL."],
  ["Organ crosstalk", "8-edge degradation graph: gut→liver→brain, kidney↔heart. Two organs below 0.3 → multi-organ CROSSTALK-KILL."],
  ["Drug-drug interactions", "CYP450 competition detection + albumin displacement war. Displacement > 90% → free fraction explosion → DDI-KILL."],
  ["Chronopharmacology", "PPI dosed outside 06:00–09:00 loses ~70% efficacy; cortisol phase modulates immune function."],
  ["Microbiome", "Shannon diversity floor; pathobionts (E. faecalis on levodopa, Eggerthella on digoxin) collapse bioavailability to 20%."],
  ["Epigenetic + tissue mode", "Methylation pace → biological age → repair velocity. mTOR/AMPK ratio picks BUILDING vs DEMOLITION mode."],
  ["Sleep architecture", "N3 hours → GH pulse, glymphatic clearance (0.2 when N3 < 1.5h), immune consolidation, fragmentation penalty."],
  ["Cytokine dynamics", "6h ODE integration of IL-6/TNF-α/IL-1β/IL-10 with vagal and cortisol modulation. IL-6 > 80 ∧ TNF-α > 50 → CYTOKINE-STORM."],
  ["Vagal tone & spasm", "RMSSD below 20ms → vagal collapse, spasm amplification, cholinergic anti-inflammatory pathway offline."],
  ["Nutrient substrate", "Liebig's Law of the Minimum: the scarcest of glutamine/zinc/vitC/vitA/arginine/omega-3 caps restitution."],
  ["Composite restitution", "(1−spasm) × substrates × repair × telomere × HIF × GH → single restitution fraction. pH < 4 → zero."],
  ["Quantum receptor", "Binomial Monte Carlo over 10k receptors: occupancy is a probability, not a certainty. Competitive + allosteric modelling."],
  ["Multi-compartment PK", "2-compartment ODE (k10/k12/k21) over 72h with 3 doses → therapeutic window classification."],
  ["Narrow therapeutic index", "Warfarin (VKORC1 + CYP2C9 genotype, INR gate) and digoxin (level, K+, renal) precision checks → NTI-KILL on breach."],
  ["Anti-persona + game theory", "5 escape vectors (efflux, persisters, mutation, biofilm QS, β-lactamase); 3+ active → ESCAPE cascade. Nash/minimax on 5×5 payoffs."],
  ["RL treatment optimizer", "Q-learning agent pre-trained 200 episodes against the active payoff matrix before recommending."],
  ["Bayesian calibration", "Beta-Bernoulli + Gaussian conjugate calibrators narrow intervals as outcomes arrive."],
  ["Lagom throttle", "Friction budget: massive stacks with low entropy get purged to 3."],
  ["Ragnar compilation", "All surviving dimensions compiled into one state string → SHA-256 → the deterministic seal."],
  ["Outcome tracking", "Exactly one prediction logged per run under the seal id — stateless here, injectable in the library."],
];

const SPOFS = [
  ["1", "Static PK modifier"], ["2", "No Vd tensor"], ["3", "No protein-binding DDI"],
  ["4", "Single-shot execution"], ["5", "No organ perfusion"], ["6", "No hypoxia model"],
  ["7", "No microbiome"], ["8", "No nutrient substrates"], ["9", "Trivial anti-persona"],
  ["10", "No chronopharmacology"], ["11", "No epigenetic age"], ["12", "No endocrine model"],
  ["13", "No autophagy toggle"], ["14", "No cytokine model"], ["15", "No vagal tone"],
  ["16", "Receptor determinism"], ["17", "No HPA axis"], ["18", "No organ crosstalk"],
  ["19", "No sleep architecture"], ["20", "No exogenous toxins"], ["21", "No NTI engine"],
  ["22", "Single-compartment PK"], ["23", "Uniform Bayesian priors"], ["24", "Hardcoded PK params"],
  ["25", "No model calibration"], ["26", "Static game payoffs"], ["27", "No outcome learning"],
  ["28", "No feedback loop"], ["29", "Unvalidated inputs"],
  ["30", "Draft never built — 21 missing models"], ["31", "Wildcard imports"],
  ["32", "Global RNG state"], ["33", "print() in library code"], ["34", "Silent persistence"],
  ["35", "Scattered version strings"], ["36", "Hardcoded /var log path"],
  ["37", "Theatrical kill-switch broke healthy profiles"], ["38", "pickle RCE vector"],
  ["39", "No machine-to-machine surface"], ["40", "Non-existent build backend"],
  ["41", "Epsilon decay was a no-op"], ["42", "RL recommended from zero table"],
  ["43", "Double outcome logging"], ["44", "Warfarin ran on CYP2C19"],
  ["45", "Credible interval ignored confidence"], ["46", "Float-equality Nash detection"],
  ["47", "Bare % crashed lazy logging"], ["48", "No provenance discipline"],
  ["49", "No frozen API contract"],
];

const PRESETS = {
  edge: {
    desc: "The original v28 demonstration profile: CYP2C19 *17/*17 ultra-rapid metabolizer, H. pylori in biofilm mode, dysbiotic microbiome, chronic toxin load, sleep-deprived, catabolic — with the full learning layer enabled.",
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
    desc: "A physiologically stable reference: normal-genotype PPI patient, no toxins, adequate sleep and substrates, planktonic pathogen under immune control. Watch the engine find the one dimension that still bites — catabolic cortisol rhythm.",
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
  }
};

/* ── static section builders ─────────────────────────────── */
function buildPhaseMap() {
  const grid = document.getElementById("phaseGrid");
  grid.innerHTML = PHASES.map((p, i) =>
    `<div class="phase-cell" data-tip="${p[1].replace(/"/g, "&quot;")}"><b>${String(i + 1).padStart(2, "0")}</b>${p[0]}</div>`
  ).join("");
}

function buildSpofGrid() {
  const grid = document.getElementById("spofGrid");
  grid.innerHTML = SPOFS.map(s =>
    `<div class="spof-chip"><b>#${s[0]}</b>${s[1]}</div>`
  ).join("");
}

/* ── demo state ──────────────────────────────────────────── */
let mode = "edge";

const $ = (id) => document.getElementById(id);

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
    $("customJson").value = JSON.stringify(PRESETS.edge.telemetry, null, 2);
  } else {
    $("presetDesc").textContent = PRESETS[next].desc;
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

/* ── rendering ───────────────────────────────────────────── */
const fmt = (v, d = 3) =>
  typeof v === "number" ? v.toFixed(d) : String(v);
const pct = (v, d = 1) => (100 * v).toFixed(d) + "%";

function metric(label, value, cls = "", sub = "") {
  return `<div class="metric"><div class="metric-label">${label}</div>` +
    `<div class="metric-value ${cls}">${value}</div>` +
    (sub ? `<div class="metric-sub">${sub}</div>` : "") + `</div>`;
}

function renderMetrics(r) {
  const m = [];
  m.push(metric("PK modifier", fmt(r.pk_modifier, 2), r.pk_modifier < 1 ? "magenta" : "cyan",
    r.pk_modifier < 1 ? "ultra-rapid metabolizer" : "normal metabolizer"));
  if (r.clearance) {
    m.push(metric("Clearance", fmt(r.clearance.clearance_rate, 3), "cyan",
      `renal ${fmt(r.clearance.renal_component, 2)} + hepatic ${fmt(r.clearance.hepatic_component, 2)}`));
    m.push(metric("Half-life", fmt(r.clearance.t_half, 2) + "h"));
    m.push(metric("Free fraction", fmt(r.clearance.free_fraction, 3), "amber",
      "albumin-bound displacement"));
    m.push(metric("Vd adjusted", fmt(r.clearance.vd_adjusted, 2)));
  }
  if (r.neural_pk) {
    m.push(metric("Neural clearance", fmt(r.neural_pk.clearance_rate, 3), "magenta",
      `confidence ${pct(r.neural_pk.confidence, 0)}`));
  }
  m.push(metric("CYP derate", fmt(r.cyp_derate, 3), r.cyp_derate < 0.8 ? "amber" : "",
    "hypoxia × toxins"));
  m.push(metric("Chrono efficacy", fmt(r.chrono_efficacy, 2), r.chrono_efficacy < 1 ? "amber" : "green"));
  m.push(metric("Allostatic load", fmt(r.allostatic_load, 2), r.allostatic_load > 3 ? "red" : "",
    "cortisol/DHEA, normal = 1.0"));
  if (r.cytokine) {
    m.push(metric("IL-6 / TNF-α",
      `${fmt(r.cytokine["IL-6"], 1)} / ${fmt(r.cytokine["TNF-α"], 1)}`,
      r.cytokine["IL-6"] > 80 ? "red" : "green", "pg/mL"));
  }
  m.push(metric("Restitution", fmt(r.restitution, 3),
    r.restitution === 0 ? "red" : r.restitution < 0.3 ? "amber" : "green",
    "composite healing capacity"));
  if (r.receptor_occupancy) {
    m.push(metric("Receptor occupancy", pct(r.receptor_occupancy.mean_occupancy, 1), "cyan",
      `P(therapeutic) ${pct(r.receptor_occupancy.p_therapeutic_effect, 1)}`));
  }
  if (r.pk_window) {
    m.push(metric("Subtherapeutic", pct(r.pk_window.fraction_subtherapeutic, 0),
      r.pk_window.subtherapeutic ? "red" : "green", "2-compartment curve"));
  }
  if (r.escape_vectors) {
    const n = Object.values(r.escape_vectors).filter(Boolean).length;
    m.push(metric("Escape vectors", `${n}/5`, n >= 3 ? "red" : n > 0 ? "amber" : "green",
      "pathogen adaptation"));
  }
  if (r.minimax) m.push(metric("Minimax strategy", r.minimax.minimax_treatment, "cyan"));
  if (r.nash_equilibria) m.push(metric("Pure Nash", String(r.nash_equilibria.length), "magenta",
    "zero = no stable deterministic treatment"));
  if (r.rl_recommendation) m.push(metric("RL recommends", r.rl_recommendation, "green", "pre-trained Q-agent"));
  if (r.lagom_stack_size !== undefined) m.push(metric("Lagom stack", String(r.lagom_stack_size), "", "friction budget"));
  if (r.surviving_priors) m.push(metric("Surviving priors", `${Object.keys(r.surviving_priors).length}/10`,
    Object.keys(r.surviving_priors).length < 10 ? "amber" : "green", "SPOF ledger"));
  $("metrics").innerHTML = m.join("");
}

function renderTrace(events) {
  const trace = $("phaseTrace");
  trace.innerHTML = (events || []).map(ev => {
    const title = ev.title || PHASES[ev.phase - 1]?.[0] || `Phase ${ev.phase}`;
    const preview = (ev.lines && ev.lines[0]) || "";
    const lines = (ev.lines || []).map(l => `<div>${l}</div>`).join("");
    return `<details class="trace-item"><summary>` +
      `<span class="trace-num">${String(ev.phase).padStart(2, "0")}</span>` +
      `<span class="trace-title">${title}</span>` +
      `<span class="trace-preview">${preview}</span></summary>` +
      `<div class="trace-lines">${lines}</div></details>`;
  }).join("");
  $("phaseCount").textContent = `(${events ? events.length : 0} phases)`;
}

function renderRx(rx) {
  const grid = $("rxGrid");
  if (!rx || Object.keys(rx).length === 0) {
    grid.innerHTML = `<div class="rx-empty">✓ No prescriptions required — telemetry already stable across all dimensions.</div>`;
    return;
  }
  grid.innerHTML = Object.entries(rx).map(([cat, d]) => {
    let body = "";
    for (const [k, v] of Object.entries(d || {})) {
      if (Array.isArray(v)) {
        body += `<ul>${v.map(i => `<li>${i}</li>`).join("")}</ul>`;
      } else if (typeof v === "object" && v !== null) {
        body += `<div class="rx-line"><b>${k}:</b> ${JSON.stringify(v)}</div>`;
      } else {
        body += `<div class="rx-line"><b>${k}:</b> ${v}</div>`;
      }
    }
    return `<div class="rx-card"><h4>${cat}</h4>${body}</div>`;
  }).join("");
}

function renderStatus(r) {
  const banner = $("statusBanner");
  if (r.error) {
    banner.className = "status-banner status-abort";
    banner.innerHTML = `⚠ SYSTEM ABORT — ${escapeHtml(r.error)}` +
      `<small>Tensor matrix shattered. The kernel refused to average its way past reality.` +
      ` ${r.version ? "Kernel " + r.version + "." : ""}</small>`;
  } else {
    banner.className = "status-banner status-ok";
    banner.innerHTML = `✓ COLLISION COMPLETE — RAGNAR HASH <span class="hash">${r.hash}</span>` +
      `<small>Kernel ${r.version}. Same telemetry + seed ${$("seedInput").value} → same hash, always.</small>`;
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
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
  status.textContent = "◇ colliding 29 dimensions…";

  try {
    const t0 = performance.now();
    const [result, rx] = await Promise.all([
      api("/api/simulate", { telemetry, seed }),
      api("/api/optimize", { telemetry }),
    ]);
    const ms = Math.round(performance.now() - t0);

    $("resultsEmpty").classList.add("hidden");
    $("resultsBody").classList.remove("hidden");
    renderStatus(result);
    renderMetrics(result);
    renderTrace(result.events);
    renderRx(rx);
    $("rawJson").textContent = JSON.stringify(result, null, 2);
    status.textContent = `✓ ${ms} ms round-trip — real kernel, serverless`;
  } catch (err) {
    status.classList.add("err");
    status.textContent = "✗ " + err.message;
  } finally {
    btn.disabled = false;
  }
}

/* ── wire up ──────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  buildPhaseMap();
  buildSpofGrid();
  setMode("edge");
  document.querySelectorAll(".preset-btn").forEach(b =>
    b.addEventListener("click", () => setMode(b.dataset.preset))
  );
  $("runBtn").addEventListener("click", run);

  // health probe for the footer link
  fetch("/api/health")
    .then(r => r.json())
    .then(h => { document.title += ` — v${h.version}`; })
    .catch(() => {});
});
