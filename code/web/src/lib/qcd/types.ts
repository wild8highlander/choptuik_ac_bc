/**
 * types.ts — Shared TypeScript types for the Choptuik–QCD bridge web app.
 *
 * These types are designed to round-trip the JSON output of the Python
 * `qcd_bridge_engine.run_all` pipeline (see qcd_bridge_engine.py).
 */

export type Language = "en" | "ru";

export type ReportFormat = "txt" | "csv" | "md" | "pdf" | "html" | "docx" | "json";

/** User-configurable parameters for a custom run. */
export interface QCDConfig {
  mode: "verify_all" | "verify_section" | "custom";
  sections: number[];
  kappa_values: number[];
  N_values: number[];
  kappa_T_custom: number;
  N_custom: number;
  n_flavors: number;
  seed: number;
  language: Language;
  report_formats: ReportFormat[];
}

export const DEFAULT_CONFIG: QCDConfig = {
  mode: "custom",
  sections: [1, 2, 3, 4, 5, 6, 7, 8, 9],
  kappa_values: [0.0, 0.3, 0.7, 1.0, 1.5, 2.0, 2.62, 3.0, 4.0, 5.0, 8.45, 12.0, 20.0],
  N_values: [10, 28, 50, 100, 200, 500, 1000, 2000, 5000],
  kappa_T_custom: 8.45,
  N_custom: 28,
  n_flavors: 6,
  seed: 42,
  language: "en",
  report_formats: ["txt", "csv", "md", "pdf", "html", "docx", "json"],
};

/** Result shape returned by the Python engine (mirrors QCDBridgeResult). */
export interface QCDResult {
  config: QCDConfig;
  sections_run: number[];
  results: Record<string, unknown>;
  logs: string[];
  timestamp: string;
  elapsed_s: number;
}

/** Single kappa_T sweep row. */
export interface SweepRow {
  kappa_T: number;
  BF_GUE_Poisson: number;
  BF_class: string;
  lambda_min: number;
  lambda_max: number;
  lambda_mean: number;
  lambda_std: number;
  n_eigs: number;
  elapsed_s: number;
  BF: number;
  log_BF: number;
  n_spacings: number;
  mean_s: number;
  std_s: number;
}

/** Single N-scaling row. */
export interface NScalingRow {
  N: number;
  lambda_mean: number;
  lambda_std: number;
  abs_mean: number;
  theoretical_1_over_sqrt_N: number;
  ratio_abs_mean_to_theory: number;
}

/** Tau relaxation dynamics result. */
export interface TauRelaxResult {
  theta_0: number;
  tau_relax_s: number;
  tau_relax_theory_s: number;
  Lambda_QCD_eV: number;
  t_values_s: number[];
  theta_t_values: number[];
  theta_at_1_tau: number;
  theta_at_5_tau: number;
  suppression_factor_at_1_tau: number;
}

/** Cabibbo coincidence result. */
export interface CabibboResult {
  b_Ch: number;
  c_theta_framework: number;
  sin_2theta_C_predicted: number;
  theta_C_predicted_rad: number;
  sin_theta_C_predicted: number;
  sin2_theta_C_measured: number;
  theta_C_measured_rad: number;
  sin_theta_C_measured: number;
  deviation_rad: number;
  deviation_pct: number;
  coincidence_quality: "good" | "weak";
}

/** Single step in the CP 8-step solution chain. */
export interface CPChainStep {
  step: number;
  statement: string;
  evidence: string;
  section: string;
}

export interface CPChainResult {
  steps: CPChainStep[];
  total_steps: number;
  final_result: string;
  new_fields_introduced: number;
  new_scales_introduced: number;
  new_symmetries_introduced: number;
  falsification_tests: string[];
}

/** Jet wake bridge result. */
export interface JetWakeResult {
  delta_C: number;
  Lambda_QCD_GeV: number;
  chi_eff_GeV4: number;
  chi_eff_eV4: number;
  bridge_formula: string;
  jet_wake_amplitude_ratio: number;
  topological_sector_count: number;
  kappa_T_coupling: number;
}
