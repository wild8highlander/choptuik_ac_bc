/**
 * compute.ts — JavaScript port of qcd_bridge_engine.py.
 *
 * Every function mirrors a section of the Python engine so the live preview in
 * the browser matches the canonical Python output (within PRNG/numerical noise).
 * Author: Ishak Khamzatovich Isaev (ORCID 0009-0003-7299-0701).
 */

import {
  DELTA_C,
  HBAR_EV_S,
  KAPPA_T_BESTFIT,
  KAPPA_T_PHYSICAL_LOWER,
  K_STRUCT,
  N_HILBERT,
  SIN2_THETA_CABIBBO,
  TAU_RELAX_S,
} from "./constants";
import {
  classifyBF,
  eigvalshSym,
  foldedSpacings,
  gaussian,
  gueSpacingPdf,
  mean,
  mulberry32,
  poissonSpacingPdf,
  randnMatrix,
  std,
  symmetrize,
} from "./linalg";
import type {
  CabibboResult,
  CPChainResult,
  JetWakeResult,
  NScalingRow,
  SweepRow,
  TauRelaxResult,
} from "./types";

// ─── 1. K3 intersection form: E8 ⊕ E8 ⊕ U ⊕ U ⊕ U  (22×22) ─────────────────
const E8_CARTAN: number[][] = [
  [ 2, -1,  0,  0,  0,  0,  0,  0],
  [-1,  2, -1,  0,  0,  0,  0,  0],
  [ 0, -1,  2, -1,  0,  0,  0,  0],
  [ 0,  0, -1,  2, -1,  0,  0,  0],
  [ 0,  0,  0, -1,  2, -1,  0, -1],
  [ 0,  0,  0,  0, -1,  2, -1,  0],
  [ 0,  0,  0,  0,  0, -1,  2,  0],
  [ 0,  0,  0,  0, -1,  0,  0,  2],
];

const HYPERBOLIC_PLANE: number[][] = [[0, 1], [1, 0]];

/** 22×22 intersection form on H²(K3, Z) = E8 ⊕ E8 ⊕ U ⊕ U ⊕ U. */
export function K3IntersectionForm(): Float64Array {
  const blocks = [E8_CARTAN, E8_CARTAN, HYPERBOLIC_PLANE, HYPERBOLIC_PLANE, HYPERBOLIC_PLANE];
  const n = blocks.reduce((s, b) => s + b.length, 0);
  const Q = new Float64Array(n * n);
  let i = 0;
  for (const b of blocks) {
    const m = b.length;
    for (let r = 0; r < m; r++) {
      for (let c = 0; c < m; c++) {
        Q[(i + r) * n + (i + c)] = b[r][c];
      }
    }
    i += m;
  }
  return Q;
}

// ─── 2. O_chi operator:  Q_K3 ⊕ M_F + kappa_T * V_T  (28×28 by default) ─────
const YUKAWA_ALL = [2.2e-3, 4.7e-3, 1.28e-1, 1.27, 4.18, 173.0];

/** Build O_chi = block_diag(Q_K3, M_F) + kappa_T * V_T. */
export function buildOchi(kappaT: number, nFlavors = 6, seed = 42): { O: Float64Array; n: number } {
  const Q = K3IntersectionForm();      // 22×22
  const nf = Math.max(1, Math.min(6, nFlavors));
  const yuk = YUKAWA_ALL.slice(0, nf);
  const n = K_STRUCT + nf;
  const O = new Float64Array(n * n);
  // Block-diagonal: Q in the top-left.
  for (let r = 0; r < K_STRUCT; r++) {
    for (let c = 0; c < K_STRUCT; c++) {
      O[r * n + c] = Q[r * K_STRUCT + c];
    }
  }
  // M_F = diag(log(y/y0) * 0.1) in the bottom-right.
  for (let i = 0; i < nf; i++) {
    O[(K_STRUCT + i) * n + (K_STRUCT + i)] = Math.log(yuk[i] / yuk[0]) * 0.1;
  }
  // GUE-like real symmetric perturbation, scaled by kappa_T.
  const rng = mulberry32(seed);
  const G = randnMatrix(n, rng);
  const V = symmetrize(G, n);
  const norm = 1 / Math.sqrt(n);
  for (let i = 0; i < O.length; i++) O[i] += kappaT * V[i] * norm;
  return { O, n };
}

// ─── 3. Bayes factor GUE/Poisson from folded spacing histogram ──────────────
export function bayesFactorGuePoisson(eigs: number[], nBins = 20): {
  bf: number;
  stats: { BF: number; log_BF: number; n_spacings: number; mean_s: number; std_s: number };
} {
  const s = foldedSpacings(eigs).filter((x) => x > 1e-9);
  if (s.length < 5) {
    return { bf: 1, stats: { BF: 1, log_BF: 0, n_spacings: s.length, mean_s: mean(s), std_s: 0 } };
  }
  // Histogram on [0, 4] (matches Python).
  const lo = 0;
  const hi = 4;
  const dx = (hi - lo) / nBins;
  const counts = new Array(nBins).fill(0);
  for (const x of s) {
    let idx = Math.floor((x - lo) / dx);
    if (idx < 0) idx = 0;
    if (idx >= nBins) idx = nBins - 1;
    counts[idx]++;
  }
  // Normalize to density (mass / binWidth / total).
  const total = s.length;
  const dens = counts.map((c) => c / (total * dx));
  const centers = counts.map((_, i) => lo + (i + 0.5) * dx);
  const eps = 1e-12;
  let lGue = 0;
  let lPoi = 0;
  for (let i = 0; i < nBins; i++) {
    lGue += dens[i] * Math.log(gueSpacingPdf(centers[i]) + eps);
    lPoi += dens[i] * Math.log(poissonSpacingPdf(centers[i]) + eps);
  }
  const logBF = lGue - lPoi;
  const bf = Math.exp(logBF);
  return {
    bf,
    stats: { BF: bf, log_BF: logBF, n_spacings: s.length, mean_s: mean(s), std_s: std(s) },
  };
}

// ─── 4. kappa_T sweep ────────────────────────────────────────────────────────
export function kappaTSweep(kappas: number[], seed = 42): SweepRow[] {
  const rows: SweepRow[] = [];
  for (const k of kappas) {
    const t0 = performance.now();
    const { O, n } = buildOchi(k, 6, seed);
    const eigs = eigvalshSym(O, n);
    const { bf, stats } = bayesFactorGuePoisson(eigs);
    const lambdaMin = eigs[0];
    const lambdaMax = eigs[eigs.length - 1];
    const lambdaMean = mean(eigs);
    const lambdaStd = std(eigs);
    rows.push({
      kappa_T: k,
      BF_GUE_Poisson: bf,
      BF_class: classifyBF(bf),
      lambda_min: lambdaMin,
      lambda_max: lambdaMax,
      lambda_mean: lambdaMean,
      lambda_std: lambdaStd,
      n_eigs: eigs.length,
      elapsed_s: (performance.now() - t0) / 1000,
      BF: bf,
      log_BF: stats.log_BF,
      n_spacings: stats.n_spacings,
      mean_s: stats.mean_s,
      std_s: stats.std_s,
    });
  }
  return rows;
}

// ─── 5. N-scaling: <λ> -> 0 as 1/sqrt(N) ─────────────────────────────────────
export function nScalingTest(Ns: number[], kappaT = KAPPA_T_BESTFIT, seed = 42): NScalingRow[] {
  const rng = mulberry32(seed);
  const rows: NScalingRow[] = [];
  for (const N of Ns) {
    // Build an N×N GUE: H = (G+G†)/sqrt(2N) — but Python uses complex GUE.
    // For a real symmetric preview we use a GOE-like matrix scaled to the same σ.
    // The qualitative 1/sqrt(N) decay is preserved.
    const G = randnMatrix(N, rng);
    const H = symmetrize(G, N);
    const norm = 1 / Math.sqrt(2 * N);
    for (let i = 0; i < H.length; i++) H[i] *= norm;
    const eigs = eigvalshSym(H, N);
    const lambdaMean = mean(eigs);
    const lambdaStd = std(eigs);
    const absMean = Math.abs(lambdaMean);
    const theory = 1 / Math.sqrt(N);
    rows.push({
      N,
      lambda_mean: lambdaMean,
      lambda_std: lambdaStd,
      abs_mean: absMean,
      theoretical_1_over_sqrt_N: theory,
      ratio_abs_mean_to_theory: theory > 0 ? absMean / theory : 0,
    });
  }
  return rows;
}

// ─── 6. tau_relax dynamics ───────────────────────────────────────────────────
export function tauRelaxDynamics(theta0 = 1e-19): TauRelaxResult {
  const tau = TAU_RELAX_S;
  const lambdaQcdEv = 200e6;
  const tauTheory = HBAR_EV_S / lambdaQcdEv;
  const times: number[] = [];
  const thetaT: number[] = [];
  // 60 log-spaced points from 1e-45 to 1e-38 s (matches Python).
  const lo = Math.log10(1e-45);
  const hi = Math.log10(1e-38);
  const n = 60;
  for (let i = 0; i < n; i++) {
    const t = Math.pow(10, lo + ((hi - lo) * i) / (n - 1));
    times.push(t);
    thetaT.push(theta0 * Math.exp(-t / tau));
  }
  return {
    theta_0: theta0,
    tau_relax_s: tau,
    tau_relax_theory_s: tauTheory,
    Lambda_QCD_eV: lambdaQcdEv,
    t_values_s: times,
    theta_t_values: thetaT,
    theta_at_1_tau: theta0 * Math.exp(-1),
    theta_at_5_tau: theta0 * Math.exp(-5),
    suppression_factor_at_1_tau: Math.exp(-1),
  };
}

// ─── 7. kappa_T physical estimate from lattice Dirac data ───────────────────
export function kappaTPhysicalEstimate() {
  return {
    kappa_T_lower_95CL: KAPPA_T_PHYSICAL_LOWER,
    kappa_T_best_fit: KAPPA_T_BESTFIT,
    lattice_data_source: "Borsányi et al. arXiv:1512.04954 (extrapolated)",
    BF_at_lower: 99.0,
    BF_at_best_fit: 510.0,
    BF_class_at_lower: classifyBF(99.0),
    BF_class_at_best_fit: classifyBF(510.0),
    physical_kappa_in_GUE_regime: true,
    GUE_threshold_kappa: 1.5,
  };
}

// ─── 8. Cabibbo angle coincidence ────────────────────────────────────────────
export function cabibboCoincidence(): CabibboResult {
  const bCh = 1 - Math.cos((2 * Math.PI) / 7);
  const cTheta = bCh / 4;
  const sin2tC = 2 * Math.sqrt(cTheta);
  const thetaCpred = 0.5 * Math.asin(Math.min(1, sin2tC));
  const sinThetaCpred = Math.sin(thetaCpred);
  const sin2Meas = SIN2_THETA_CABIBBO;
  const sinThetaCmeas = Math.sqrt(sin2Meas);
  const thetaCmeas = Math.asin(sinThetaCmeas);
  const devRad = thetaCpred - thetaCmeas;
  const devPct = (Math.abs(devRad) / thetaCmeas) * 100;
  return {
    b_Ch: bCh,
    c_theta_framework: cTheta,
    sin_2theta_C_predicted: sin2tC,
    theta_C_predicted_rad: thetaCpred,
    sin_theta_C_predicted: sinThetaCpred,
    sin2_theta_C_measured: sin2Meas,
    theta_C_measured_rad: thetaCmeas,
    sin_theta_C_measured: sinThetaCmeas,
    deviation_rad: devRad,
    deviation_pct: devPct,
    coincidence_quality: devPct < 15 ? "good" : "weak",
  };
}

// ─── 9. CP 8-step solution chain ─────────────────────────────────────────────
export function cpSolutionChain(): CPChainResult {
  const steps = [
    { step: 1, statement: "O_chi = Q_hat (structural role)",
      evidence: "O_chi occupies the same epistemic niche as the topological charge operator",
      section: "§3" },
    { step: 2, statement: "O_chi = Q_K3 ⊕ M_F + kappa_T * V_T at N=28",
      evidence: "22 K3 topological sectors ⊕ 6 quark flavors",
      section: "§5.6" },
    { step: 3, statement: "GUE class at kappa_T > 2.62 (95% CL), BF >= 99",
      evidence: "Bayes factor classification: strong at lower bound, decisive at best-fit",
      section: "§5.7, §6.4" },
    { step: 4, statement: "GUE spectral symmetry => <lambda> = 0",
      evidence: "Wigner semicircle is symmetric; all odd spectral moments vanish",
      section: "§6.5" },
    { step: 5, statement: "Work formula: theta_bar = delta_C * N * <lambda> * S_GUE",
      evidence: "Derived from path integral over topological sectors",
      section: "§6" },
    { step: 6, statement: "theta_bar = 0 exactly in continuum GUE regime",
      evidence: "Follows directly from steps 4 and 5",
      section: "§6" },
    { step: 7, statement: "Finite-N artifact ~ 1/sqrt(N) vanishes as N -> infinity",
      evidence: "Monte Carlo verification across N = 10..10000",
      section: "§6.6" },
    { step: 8, statement: "Dynamic relaxation tau_relax ~ 5e-41 s",
      evidence: "Damps CKM-induced residual theta_0 ~ 1e-19",
      section: "§6.7" },
  ];
  return {
    steps,
    total_steps: steps.length,
    final_result: "theta_bar = 0 exactly",
    new_fields_introduced: 0,
    new_scales_introduced: 0,
    new_symmetries_introduced: 0,
    falsification_tests: [
      "Direct lattice measurement of F(theta) - F(0) via Giusti-Rossi-Testa method",
      "Derivation of work formula from PSL(2,7) algebraic geometry",
    ],
  };
}

// ─── 10. Jet wake bridge (NR <-> QCD) ────────────────────────────────────────
export function jetWakeBridge(): JetWakeResult {
  const lambdaQcdGeV = 0.2;
  const chiEffGeV4 = DELTA_C * Math.pow(lambdaQcdGeV, 4);
  const chiEffEv4 = chiEffGeV4 * 1e36;
  return {
    delta_C: DELTA_C,
    Lambda_QCD_GeV: lambdaQcdGeV,
    chi_eff_GeV4: chiEffGeV4,
    chi_eff_eV4: chiEffEv4,
    bridge_formula: "chi_eff = delta_C * Lambda_QCD^4",
    jet_wake_amplitude_ratio: DELTA_C / Math.PI,
    topological_sector_count: 22,
    kappa_T_coupling: KAPPA_T_BESTFIT,
  };
}

// ─── Convenience: O_chi eigenvalues (used by section 1 + section 3) ──────────
export function ochiEigenvalues(kappaT: number, nFlavors: number, seed: number): number[] {
  const { O, n } = buildOchi(kappaT, nFlavors, seed);
  return eigvalshSym(O, n);
}

/** Section 1 helper returning operator stats. */
export function section1Stats(kappaT: number, nFlavors: number, seed: number) {
  const { O, n } = buildOchi(kappaT, nFlavors, seed);
  const eigs = eigvalshSym(O, n);
  let trace = 0;
  for (let i = 0; i < n; i++) trace += O[i * n + i];
  return {
    operator_shape: [n, n],
    eigenvalues: eigs,
    lambda_min: eigs[0],
    lambda_max: eigs[eigs.length - 1],
    lambda_mean: mean(eigs),
    lambda_std: std(eigs),
    trace,
    kappa_T: kappaT,
    N: n,
    matrix: O,
  };
}

export const N_HILBERT_VALUE = N_HILBERT;
export const K_STRUCT_VALUE = K_STRUCT;
