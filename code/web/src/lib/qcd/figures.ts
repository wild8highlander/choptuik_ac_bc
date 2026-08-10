/**
 * figures.ts — Build Plotly figures for each of the 9 sections.
 *
 * Each builder is a pure function: input is the live preview config, output is
 * a `PlotlyFigure` ready to hand to <PlotlyChart />. Builders also return a
 * list of stat tiles to render next to the chart.
 */

import {
  KAPPA_T_BESTFIT,
  KAPPA_T_PHYSICAL_LOWER,
  PALETTE,
} from "./constants";
import {
  cabibboCoincidence,
  cpSolutionChain,
  jetWakeBridge,
  kappaTPhysicalEstimate,
  kappaTSweep,
  nScalingTest,
  ochiEigenvalues,
  section1Stats,
  tauRelaxDynamics,
} from "./compute";
import { gueSpacingPdf, poissonSpacingPdf } from "./linalg";
import type { PlotlyFigure } from "@/components/qcd/PlotlyChart";
import type { QCDConfig } from "./types";

export interface StatTile {
  label: string;       // i18n key under "stats.*"
  value: string;
  hint?: string;
  tone?: "default" | "good" | "warn" | "bad";
}

export interface SectionFigure {
  figure: PlotlyFigure;
  stats: StatTile[];
  table?: { columns: string[]; rows: (string | number)[][] };
}

const TEXT_COLOR = PALETTE.primary;
const BG_PAPER = "rgba(255,255,255,0.85)";

function baseLayout(title: string, sceneLabels?: { x?: string; y?: string; z?: string }): Record<string, unknown> {
  const scene = sceneLabels
    ? {
        xaxis: { title: { text: sceneLabels.x ?? "x" }, gridcolor: PALETTE.grid, backgroundcolor: BG_PAPER },
        yaxis: { title: { text: sceneLabels.y ?? "y" }, gridcolor: PALETTE.grid, backgroundcolor: BG_PAPER },
        zaxis: { title: { text: sceneLabels.z ?? "z" }, gridcolor: PALETTE.grid, backgroundcolor: BG_PAPER },
        camera: { eye: { x: 1.5, y: 1.5, z: 0.8 } },
      }
    : undefined;
  return {
    title: { text: title, font: { color: TEXT_COLOR, size: 14 } },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: { family: "Inter, system-ui, sans-serif", size: 12, color: PALETTE.ink },
    margin: { l: 60, r: 30, t: 60, b: 50 },
    legend: { orientation: "h", y: -0.15 },
    scene,
  };
}

// ─── Section 1: O_chi matrix + eigenvalues ──────────────────────────────────
export function figureSection1(cfg: QCDConfig): SectionFigure {
  const stats = section1Stats(cfg.kappa_T_custom, cfg.n_flavors, cfg.seed);
  const n = stats.N;
  const M = stats.matrix;
  // Heatmap is row-major; Plotly expects nested arrays [row][col].
  const z: number[][] = [];
  for (let i = 0; i < n; i++) {
    const row: number[] = [];
    for (let j = 0; j < n; j++) row.push(M[i * n + j]);
    z.push(row);
  }
  const eigs = stats.eigenvalues;

  const figure: PlotlyFigure = {
    data: [
      {
        type: "heatmap",
        z,
        colorscale: [
          [0, "#1E293B"],
          [0.5, PALETTE.bg],
          [1, PALETTE.accent],
        ],
        showscale: true,
        colorbar: { title: { text: "O_chi[i,j]" }, thickness: 12 },
        hovertemplate: "i=%{y}, j=%{x}, v=%{z:.3f}<extra></extra>",
      },
    ],
    layout: baseLayout("O_chi matrix (28×28) — K3 ⊕ M_F + κ_T·V_T", undefined),
  };

  // Side chart: eigenvalue spectrum as a 3D bar ribbon.
  const scatter: PlotlyFigure = {
    data: [
      {
        type: "scatter3d",
        mode: "markers+lines",
        x: eigs.map((_, i) => i),
        y: eigs,
        z: eigs.map(() => 0),
        marker: { size: 4, color: eigs, colorscale: "Viridis", showscale: false },
        line: { color: PALETTE.accent, width: 2 },
        name: "λ_i",
      },
      {
        type: "scatter3d",
        mode: "markers",
        x: eigs.map((_, i) => i),
        y: eigs.map(() => 0),
        z: eigs,
        marker: { size: 3, color: PALETTE.accent2 },
        name: "λ_i (proj.)",
      },
    ],
    layout: baseLayout("O_chi eigenvalue spectrum (3D ribbon)", {
      x: "index i",
      y: "λ_i",
      z: "mirror",
    }),
  };

  return {
    figure: { data: figure.data.concat(scatter.data), layout: figure.layout },
    stats: [
      { label: "stats.shape", value: `[${stats.operator_shape[0]} × ${stats.operator_shape[1]}]` },
      { label: "stats.trace", value: stats.trace.toFixed(4) },
      { label: "stats.lambdaMin", value: stats.lambda_min.toFixed(4), tone: "bad" },
      { label: "stats.lambdaMax", value: stats.lambda_max.toFixed(4) },
      { label: "stats.lambdaMean", value: stats.lambda_mean.toFixed(4) },
      { label: "stats.lambdaStd", value: stats.lambda_std.toFixed(4) },
    ],
  };
}

// ─── Section 2: kappa_T sweep 3D scatter ────────────────────────────────────
export function figureSection2(cfg: QCDConfig): SectionFigure {
  const rows = kappaTSweep(cfg.kappa_values, cfg.seed);
  const x = rows.map((r) => r.kappa_T);
  const y = rows.map((r) => r.BF_GUE_Poisson);
  const z = rows.map((r) => r.lambda_mean);
  const color = rows.map((r) => r.BF_class);

  // Class → numeric color
  const classToColor: Record<string, string> = {
    negative: PALETTE.muted,
    weak: PALETTE.warning,
    positive: PALETTE.accent2,
    strong: PALETTE.accent,
    decisive: PALETTE.danger,
  };
  const colors = color.map((c) => classToColor[c] ?? PALETTE.muted);

  const figure: PlotlyFigure = {
    data: [
      {
        type: "scatter3d",
        mode: "markers+lines",
        x,
        y,
        z,
        marker: { size: 7, color: colors, line: { color: PALETTE.primary, width: 0.5 } },
        line: { color: PALETTE.accent, width: 2, dash: "dot" },
        text: rows.map((r) => `κ_T=${r.kappa_T}<br>BF=${r.BF_GUE_Poisson.toFixed(2)}<br>${r.BF_class}`),
        hovertemplate: "%{text}<extra></extra>",
        name: "sweep",
      },
      // Markers for the 95% CL lower and best-fit
      {
        type: "scatter3d",
        mode: "markers",
        x: [KAPPA_T_PHYSICAL_LOWER, KAPPA_T_BESTFIT],
        y: [
          rows.find((r) => Math.abs(r.kappa_T - KAPPA_T_PHYSICAL_LOWER) < 0.01)?.BF_GUE_Poisson ?? 99,
          rows.find((r) => Math.abs(r.kappa_T - KAPPA_T_BESTFIT) < 0.01)?.BF_GUE_Poisson ?? 510,
        ],
        z: [
          rows.find((r) => Math.abs(r.kappa_T - KAPPA_T_PHYSICAL_LOWER) < 0.01)?.lambda_mean ?? 0,
          rows.find((r) => Math.abs(r.kappa_T - KAPPA_T_BESTFIT) < 0.01)?.lambda_mean ?? 0,
        ],
        marker: { size: 12, color: [PALETTE.warning, PALETTE.danger], symbol: "diamond" },
        name: "lattice anchors",
      },
    ],
    layout: baseLayout("κ_T sweep — 3D scatter (κ_T, BF, ⟨λ⟩)", {
      x: "κ_T",
      y: "BF(GUE/Poisson)",
      z: "⟨λ⟩",
    }),
  };

  const table = {
    columns: ["table.kappa", "table.bf", "stats.class", "stats.lambdaMean"],
    rows: rows.map((r) => [
      r.kappa_T.toFixed(2),
      r.BF_GUE_Poisson.toFixed(2),
      r.BF_class,
      r.lambda_mean.toFixed(4),
    ]),
  };

  return {
    figure,
    stats: [
      { label: "stats.bf", value: `${Math.min(...y).toFixed(2)} – ${Math.max(...y).toFixed(2)}` },
      { label: "stats.class", value: rows[rows.length - 1]?.BF_class ?? "—" },
      { label: "stats.lambdaMean", value: `${z[0].toFixed(3)} → ${z[z.length - 1].toFixed(3)}` },
      { label: "stats.elapsed", value: `${rows.reduce((s, r) => s + r.elapsed_s, 0).toFixed(3)} s` },
    ],
    table,
  };
}

// ─── Section 3: spectral staircase vs Wigner semicircle ─────────────────────
export function figureSection3(cfg: QCDConfig): SectionFigure {
  const eigs = ochiEigenvalues(KAPPA_T_BESTFIT, cfg.n_flavors, cfg.seed);
  const sorted = [...eigs].sort((a, b) => a - b);
  const staircase = sorted.map((_, i) => (i + 1) / sorted.length);
  // Wigner semicircle (radius R = 2σ√N; σ_λ from data).
  const meanL = sorted.reduce((s, x) => s + x, 0) / sorted.length;
  const R = (sorted[sorted.length - 1] - sorted[0]) / 2;
  const xs: number[] = [];
  const semi: number[] = [];
  for (let i = 0; i <= 60; i++) {
    const x = meanL - R + (2 * R * i) / 60;
    xs.push(x);
    const v = R * R - (x - meanL) * (x - meanL);
    semi.push(v > 0 ? (2 / (Math.PI * R * R)) * Math.sqrt(v) : 0);
  }

  // Folded spacing pdf overlay.
  const eigsForSpacing = eigs;
  const sGrid = Array.from({ length: 60 }, (_, i) => (i / 60) * 4);
  const guePdf = sGrid.map((s) => gueSpacingPdf(s));
  const poiPdf = sGrid.map((s) => poissonSpacingPdf(s));

  const figure: PlotlyFigure = {
    data: [
      {
        type: "scatter3d",
        mode: "lines+markers",
        x: sorted,
        y: staircase,
        z: sorted.map(() => 0),
        marker: { size: 4, color: PALETTE.accent },
        line: { color: PALETTE.accent, width: 3 },
        name: "N(λ) staircase",
      },
      {
        type: "scatter3d",
        mode: "lines",
        x: xs,
        y: semi,
        z: xs.map(() => 0.3),
        marker: { size: 2, color: PALETTE.accent2 },
        line: { color: PALETTE.accent2, width: 3, dash: "dash" },
        name: "Wigner semicircle",
      },
      {
        type: "scatter3d",
        mode: "lines",
        x: sGrid,
        y: guePdf,
        z: sGrid.map(() => 0.6),
        marker: { size: 2, color: PALETTE.danger },
        line: { color: PALETTE.danger, width: 2 },
        name: "GUE P(s)",
      },
      {
        type: "scatter3d",
        mode: "lines",
        x: sGrid,
        y: poiPdf,
        z: sGrid.map(() => 0.6),
        marker: { size: 2, color: PALETTE.muted },
        line: { color: PALETTE.muted, width: 2, dash: "dot" },
        name: "Poisson P(s)",
      },
    ],
    layout: baseLayout("Spectral staircase + Wigner semicircle + spacing PDF", {
      x: "λ / s",
      y: "N(λ) / ρ(s)",
      z: "layer",
    }),
  };

  return {
    figure,
    stats: [
      { label: "stats.lambdaMin", value: sorted[0].toFixed(4) },
      { label: "stats.lambdaMax", value: sorted[sorted.length - 1].toFixed(4) },
      { label: "stats.lambdaMean", value: meanL.toFixed(4) },
      { label: "stats.lambdaStd", value: (R / Math.SQRT2).toFixed(4), hint: "≈ R/√2" },
    ],
  };
}

// ─── Section 4: N-scaling 1/√N ──────────────────────────────────────────────
export function figureSection4(cfg: QCDConfig): SectionFigure {
  const rows = nScalingTest(cfg.N_values, cfg.kappa_T_custom, cfg.seed);
  const N = rows.map((r) => r.N);
  const absMean = rows.map((r) => r.abs_mean);
  const theory = rows.map((r) => r.theoretical_1_over_sqrt_N);

  const figure: PlotlyFigure = {
    data: [
      {
        type: "scatter3d",
        mode: "markers+lines",
        x: N,
        y: absMean,
        z: N.map(() => 0),
        marker: { size: 7, color: PALETTE.accent },
        line: { color: PALETTE.accent, width: 2 },
        name: "|⟨λ⟩| measured",
      },
      {
        type: "scatter3d",
        mode: "lines",
        x: N,
        y: theory,
        z: N.map(() => 0.1),
        marker: { size: 4, color: PALETTE.accent2 },
        line: { color: PALETTE.accent2, width: 3, dash: "dash" },
        name: "1/√N (theory)",
      },
      // Vertical bars for visual depth
      {
        type: "bar3d",
        x: N,
        y: N.map(() => 0),
        z: absMean,
        // @ts-expect-error bar3d needs width param shape
        width: N.map(() => 4),
        marker: { color: PALETTE.accent, opacity: 0.3 },
        name: "depth",
      },
    ],
    layout: Object.assign(baseLayout("1/√N scaling: |⟨λ⟩| vs N", {
      x: "N",
      y: "|⟨λ⟩|",
      z: "layer",
    }), { scene: { xaxis: { type: "log" }, yaxis: { type: "log" } } }),
  };

  return {
    figure,
    stats: [
      { label: "stats.N", value: `${N[0]} → ${N[N.length - 1]}` },
      { label: "stats.absMean", value: `${absMean[0].toExponential(2)} → ${absMean[absMean.length - 1].toExponential(2)}` },
      { label: "stats.theory", value: `${theory[0].toExponential(2)} → ${theory[theory.length - 1].toExponential(2)}` },
      { label: "stats.ratio", value: `${rows[rows.length - 1].ratio_abs_mean_to_theory.toFixed(2)}`, hint: "@ N_max" },
    ],
    table: {
      columns: ["table.N", "table.lambdaMean", "table.absMean", "table.theory"],
      rows: rows.map((r) => [
        r.N,
        r.lambda_mean.toExponential(3),
        r.abs_mean.toExponential(3),
        r.theoretical_1_over_sqrt_N.toExponential(3),
      ]),
    },
  };
}

// ─── Section 5: tau_relax dynamics ──────────────────────────────────────────
export function figureSection5(_cfg: QCDConfig): SectionFigure {
  const r = tauRelaxDynamics();
  const figure: PlotlyFigure = {
    data: [
      {
        type: "scatter3d",
        mode: "lines+markers",
        x: r.t_values_s.map((t) => Math.log10(t)),
        y: r.theta_t_values.map((th) => th),
        z: r.t_values_s.map(() => 0),
        marker: { size: 4, color: PALETTE.accent },
        line: { color: PALETTE.accent, width: 3 },
        name: "θ(t) = θ_0 · exp(-t/τ)",
      },
      // Marker plane at θ(τ) and θ(5τ)
      {
        type: "scatter3d",
        mode: "markers",
        x: [Math.log10(r.tau_relax_s), Math.log10(5 * r.tau_relax_s)],
        y: [r.theta_at_1_tau, r.theta_at_5_tau],
        z: [0.1, 0.1],
        marker: { size: 10, color: [PALETTE.warning, PALETTE.danger], symbol: "diamond" },
        name: "θ(τ), θ(5τ)",
      },
    ],
    layout: baseLayout("τ_relax decay: θ(t) = θ_0·exp(-t/τ_relax)", {
      x: "log₁₀(t / s)",
      y: "θ(t)",
      z: "layer",
    }),
  };

  return {
    figure,
    stats: [
      { label: "stats.tauRelax", value: r.tau_relax_s.toExponential(2) },
      { label: "stats.tauTheory", value: r.tau_relax_theory_s.toExponential(2) },
      { label: "stats.theta0", value: r.theta_0.toExponential(2) },
      { label: "stats.thetaAt1Tau", value: r.theta_at_1_tau.toExponential(2), tone: "warn" },
      { label: "stats.thetaAt5Tau", value: r.theta_at_5_tau.toExponential(2), tone: "good" },
    ],
  };
}

// ─── Section 6: kappa_T physical estimate ───────────────────────────────────
export function figureSection6(cfg: QCDConfig): SectionFigure {
  const kpe = kappaTPhysicalEstimate();
  // Sweep for the surface
  const sweep = kappaTSweep(cfg.kappa_values, cfg.seed);
  const kappas = sweep.map((r) => r.kappa_T);
  const bfs = sweep.map((r) => r.BF_GUE_Poisson);
  // For a 3D ribbon: add a synthetic dimension "BF strength band"
  const z = sweep.map((r) => r.lambda_std);

  const figure: PlotlyFigure = {
    data: [
      {
        type: "scatter3d",
        mode: "markers+lines",
        x: kappas,
        y: bfs,
        z,
        marker: {
          size: 8,
          color: bfs,
          colorscale: [
            [0, PALETTE.muted],
            [0.2, PALETTE.warning],
            [0.5, PALETTE.accent2],
            [0.8, PALETTE.accent],
            [1, PALETTE.danger],
          ],
          showscale: true,
          colorbar: { title: "BF", thickness: 10 },
        },
        line: { color: PALETTE.primary, width: 2 },
        name: "lattice sweep",
      },
      // Vertical drop-lines at 2.62 and 8.45
      {
        type: "scatter3d",
        mode: "markers",
        x: [kpe.kappa_T_lower_95CL, kpe.kappa_T_best_fit],
        y: [kpe.BF_at_lower, kpe.BF_at_best_fit],
        z: [0, 0],
        marker: { size: 14, color: [PALETTE.warning, PALETTE.success], symbol: "diamond" },
        name: "95% CL / best-fit",
      },
    ],
    layout: baseLayout("κ_T physical estimate — lattice confidence region", {
      x: "κ_T",
      y: "BF(GUE/Poisson)",
      z: "σ_λ",
    }),
  };

  return {
    figure,
    stats: [
      { label: "stats.kappaLower", value: kpe.kappa_T_lower_95CL.toFixed(2), tone: "warn" },
      { label: "stats.kappaBest", value: kpe.kappa_T_best_fit.toFixed(2), tone: "good" },
      { label: "stats.bfAtLower", value: kpe.BF_at_lower.toFixed(1) },
      { label: "stats.bfAtBest", value: kpe.BF_at_best_fit.toFixed(1), tone: "good" },
      { label: "stats.class", value: kpe.BF_class_at_best_fit },
    ],
  };
}

// ─── Section 7: Cabibbo angle coincidence ───────────────────────────────────
export function figureSection7(_cfg: QCDConfig): SectionFigure {
  const cab = cabibboCoincidence();
  // 3D bar chart: predicted vs measured θ_C, b_Ch, c_theta, etc.
  const labels = ["b_Ch", "c_θ", "sin(2θ_C)", "θ_C pred", "θ_C meas", "dev %"];
  const pred = [cab.b_Ch, cab.c_theta_framework, cab.sin_2theta_C_predicted, cab.theta_C_predicted_rad, cab.theta_C_measured_rad, cab.deviation_pct];
  const figure: PlotlyFigure = {
    data: [
      {
        type: "bar3d",
        x: labels,
        y: labels.map(() => "value"),
        z: pred,
        // @ts-expect-error bar3d width param
        width: labels.map(() => 0.4),
        marker: {
          color: pred,
          colorscale: [
            [0, PALETTE.accent2],
            [0.5, PALETTE.accent],
            [1, PALETTE.danger],
          ],
          showscale: false,
        },
        name: "Cabibbo",
      },
    ],
    layout: baseLayout("Cabibbo: framework prediction vs measurement", {
      x: "quantity",
      y: "",
      z: "value",
    }),
  };

  return {
    figure,
    stats: [
      { label: "stats.thetaCpred", value: cab.theta_C_predicted_rad.toFixed(4) },
      { label: "stats.thetaCmeas", value: cab.theta_C_measured_rad.toFixed(4) },
      { label: "stats.deviationPct", value: `${cab.deviation_pct.toFixed(2)} %`, tone: cab.coincidence_quality === "good" ? "good" : "warn" },
      { label: "stats.coincidence", value: cab.coincidence_quality, tone: cab.coincidence_quality === "good" ? "good" : "warn" },
    ],
  };
}

// ─── Section 8: CP 8-step chain (3D bars) ───────────────────────────────────
export function figureSection8(_cfg: QCDConfig): SectionFigure {
  const chain = cpSolutionChain();
  // Each step gets a bar; height = step number; color by step
  const steps = chain.steps;
  const xs = steps.map((s) => s.step);
  const ys = steps.map(() => "chain");
  const zs = steps.map((s) => s.step);
  const texts = steps.map((s) => `§${s.section}: ${s.statement}`);

  const figure: PlotlyFigure = {
    data: [
      {
        type: "bar3d",
        x: xs,
        y: ys,
        z: zs,
        // @ts-expect-error bar3d width param
        width: steps.map(() => 0.6),
        text: texts,
        hovertemplate: "%{text}<extra></extra>",
        marker: {
          color: xs,
          colorscale: [
            [0, PALETTE.accent2],
            [0.5, PALETTE.accent],
            [1, PALETTE.danger],
          ],
          showscale: false,
        },
        name: "CP step",
      },
    ],
    layout: baseLayout("CP 8-step solution chain → θ̄ = 0", {
      x: "step",
      y: "",
      z: "step #",
    }),
  };

  const table = {
    columns: ["table.step", "table.statement", "table.evidence", "table.section"],
    rows: steps.map((s) => [s.step, s.statement, s.evidence, s.section]),
  };

  return {
    figure,
    stats: [
      { label: "stats.totalSteps", value: String(chain.total_steps) },
      { label: "stats.finalResult", value: chain.final_result, tone: "good" },
      { label: "stats.class", value: "0 new fields", tone: "good" },
    ],
    table,
  };
}

// ─── Section 9: jet wake bridge ─────────────────────────────────────────────
export function figureSection9(_cfg: QCDConfig): SectionFigure {
  const jwb = jetWakeBridge();
  // Surface: chi_eff(Lambda, delta) = delta * Lambda^4
  const N = 25;
  const lambdas: number[] = [];
  const deltas: number[] = [];
  for (let i = 0; i < N; i++) lambdas.push(0.05 + (0.5 * i) / (N - 1));
  for (let i = 0; i < N; i++) deltas.push((Math.PI / 14) + (Math.PI / 4 - Math.PI / 14) * (i / (N - 1)));
  const z: number[][] = [];
  for (let i = 0; i < N; i++) {
    const row: number[] = [];
    for (let j = 0; j < N; j++) {
      row.push(deltas[i] * Math.pow(lambdas[j], 4));
    }
    z.push(row);
  }

  const figure: PlotlyFigure = {
    data: [
      {
        type: "surface",
        x: lambdas,
        y: deltas,
        z,
        colorscale: [
          [0, PALETTE.accent2],
          [0.5, PALETTE.accent],
          [1, PALETTE.primary],
        ],
        showscale: true,
        colorbar: { title: "χ_eff", thickness: 10 },
        name: "χ_eff(Λ, δ)",
      },
      {
        type: "scatter3d",
        mode: "markers",
        x: [jwb.Lambda_QCD_GeV],
        y: [jwb.delta_C],
        z: [jwb.chi_eff_GeV4],
        marker: { size: 12, color: PALETTE.danger, symbol: "diamond" },
        name: "physical point",
      },
    ],
    layout: baseLayout("Jet wake bridge: χ_eff = δ_C · Λ_QCD⁴ surface", {
      x: "Λ_QCD [GeV]",
      y: "δ_C",
      z: "χ_eff [GeV⁴]",
    }),
  };

  return {
    figure,
    stats: [
      { label: "stats.deltaC", value: jwb.delta_C.toFixed(4) },
      { label: "stats.chiEff", value: jwb.chi_eff_GeV4.toExponential(3) },
      { label: "stats.chiEffEv", value: jwb.chi_eff_eV4.toExponential(3) },
      { label: "stats.kappaCoupling", value: jwb.kappa_T_coupling.toFixed(2) },
      { label: "stats.bridge", value: jwb.bridge_formula },
    ],
  };
}

const BUILDERS: Record<number, (cfg: QCDConfig) => SectionFigure> = {
  1: figureSection1,
  2: figureSection2,
  3: figureSection3,
  4: figureSection4,
  5: figureSection5,
  6: figureSection6,
  7: figureSection7,
  8: figureSection8,
  9: figureSection9,
};

export function buildSectionFigure(sectionId: number, cfg: QCDConfig): SectionFigure {
  const fn = BUILDERS[sectionId];
  if (!fn) {
    return {
      figure: { data: [], layout: baseLayout("Unknown section") },
      stats: [],
    };
  }
  return fn(cfg);
}
