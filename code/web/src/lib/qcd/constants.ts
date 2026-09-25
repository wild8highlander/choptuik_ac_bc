/**
 * constants.ts — Physical constants for the Choptuik–QCD bridge.
 *
 * Mirrors qcd_bridge_engine.py (Task 1-5, by Ishak Khamzatovich Isaev).
 * All values are the monograph reference values and MUST match the Python engine
 * so that client-side previews and Python-backed runs agree.
 */

export const DELTA_C = Math.PI / 7;                  // Choptuik critical exponent ≈ 0.4488
export const DELTA_A = Math.PI / 2;                  // Spinor phase A
export const DELTA_B = Math.PI / 3;                  // Spinor phase B
export const LAMBDA_D2_TRIV = 3.338;                 // Trivial Dirac eigenvalue (Lichnerowicz)
export const K_STRUCT = 22;                          // b_2(K3) — second Betti number
export const N_HILBERT = 28;                         // 22 K3 + 6 N_f
export const KAPPA_T_PHYSICAL_LOWER = 2.62;          // 95% CL lattice lower bound
export const KAPPA_T_BESTFIT = 8.45;                 // best-fit lattice value
export const TAU_RELAX_S = 5.0e-41;                  // dynamic relaxation timescale (s)
export const HBAR_EV_S = 6.582119569e-16;            // hbar in eV·s
export const SIN2_THETA_CABIBBO = 0.051;             // sin^2(theta_C) measured
export const THETA_CABIBBO = Math.asin(Math.sqrt(SIN2_THETA_CABIBBO));

/** Default kappa_T sweep grid — must match Python default. */
export const DEFAULT_KAPPAS: number[] = [
  0.0, 0.3, 0.7, 1.0, 1.5, 2.0, 2.62, 3.0, 4.0, 5.0, 8.45, 12.0, 20.0,
];

/** Default N values for the 1/sqrt(N) scaling test. */
export const DEFAULT_N_VALUES: number[] = [
  10, 28, 50, 100, 200, 500, 1000, 2000, 5000,
];

/** Business Cool palette (mandated by task spec). */
export const PALETTE = {
  primary: "#243447",
  accent: "#4C6EF5",
  accent2: "#3AAFA9",
  bg: "#F8FAFC",
  ink: "#0F172A",
  muted: "#64748B",
  grid: "#E2E8F0",
  danger: "#E11D48",
  success: "#10B981",
  warning: "#F59E0B",
} as const;

/** Categorical color cycle for multi-series plots. */
export const COLOR_CYCLE: string[] = [
  PALETTE.accent,
  PALETTE.accent2,
  "#F59E0B",
  "#E11D48",
  "#8B5CF6",
  "#10B981",
  PALETTE.primary,
  "#EC4899",
];

/** Author information used across footer + About page. */
export const AUTHOR = {
  name: "Ishak Khamzatovich Isaev",
  orcid: "0009-0003-7299-0701",
  orcidUrl: "https://orcid.org/0009-0003-7299-0701",
  github: "https://github.com/wild8highlander/choptuik_ac_bc",
  monographEn: "choptyuk_qcd_bridge_en.docx",
  monographRu: "choptyuk_qcd_bridge_ru.docx",
  license: "Isaev Proprietary",
} as const;

/** Section metadata (id matches the Python engine 1..9). */
export interface SectionMeta {
  id: number;
  key: string;
  shortKey: string;     // short identifier used in figure file names
  icon: string;         // lucide icon name
  color: string;        // tailwind text color class for the icon chip
}

export const SECTIONS: SectionMeta[] = [
  { id: 1, key: "section_1_ochi",             shortKey: "s1", icon: "Grid3x3",      color: "text-blue-600"    },
  { id: 2, key: "section_2_rmt_sweep",        shortKey: "s2", icon: "Activity",     color: "text-emerald-600" },
  { id: 3, key: "section_3_staircase",        shortKey: "s3", icon: "BarChart3",    color: "text-amber-600"   },
  { id: 4, key: "section_4_N_scaling",        shortKey: "s4", icon: "TrendingDown", color: "text-rose-600"    },
  { id: 5, key: "section_5_tau_relax",        shortKey: "s5", icon: "Timer",        color: "text-purple-600"  },
  { id: 6, key: "section_6_kappa_T_physical", shortKey: "s6", icon: "Target",       color: "text-teal-600"    },
  { id: 7, key: "section_7_cabibbo",          shortKey: "s7", icon: "Compass",      color: "text-orange-600"  },
  { id: 8, key: "section_8_cp_chain",         shortKey: "s8", icon: "Link2",        color: "text-indigo-600"  },
  { id: 9, key: "section_9_jet_wake",         shortKey: "s9", icon: "Waves",        color: "text-cyan-600"    },
];
