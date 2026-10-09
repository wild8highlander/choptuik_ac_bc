// ============================================================
// Simulation Engine — Parameter Sweeps & Convergence Analysis
// Runs client-side for real-time interactivity
// ============================================================

import type { SimulationParams, SweepResult, ConvergenceData } from "./types";
import { computeFull, deltaBC, deltaAC, choptyukBase, choptyukFull, spinorDeltaA, spinorDeltaB, diracTrivial } from "./compute";

/** Default simulation parameters matching the Klein curve */
export const DEFAULT_PARAMS: SimulationParams = {
  delta_C: Math.PI / 7,
  lambda_1: 3.838,
  k_struct: 0,
  c4: 1.0,
  c6: 1.0,
  genus: 3,
  R: -2,
  b_Ch: 0.376510,
};

/** Sweep a single parameter over a range, computing all invariants */
export function sweepParameter(
  paramName: keyof SimulationParams,
  min: number,
  max: number,
  steps: number,
  baseParams: SimulationParams = DEFAULT_PARAMS
): SweepResult {
  const values: number[] = [];
  const dBC_arr: number[] = [];
  const dAC_arr: number[] = [];
  const chArr: number[] = [];
  const obsArr: number[] = [];

  const deltaA = spinorDeltaA();
  const deltaB = spinorDeltaB();

  for (let i = 0; i <= steps; i++) {
    const t = min + (max - min) * (i / steps);
    values.push(t);

    const params = { ...baseParams, [paramName]: t };
    const lTriv = diracTrivial(params.genus, params.R);
    const dBC_val = deltaBC(lTriv, deltaA, deltaB, params.delta_C);
    const dAC_val = deltaAC(params.delta_C, params.R);
    const chBase = choptyukBase(dBC_val, dAC_val, params.R, params.genus);
    const chFull = choptyukFull(chBase, params.b_Ch, deltaA);

    dBC_arr.push(dBC_val);
    dAC_arr.push(dAC_val);
    chArr.push(chFull);
    obsArr.push(3.443); // reference observed value
  }

  return {
    parameter: paramName,
    values,
    delta_bC: dBC_arr,
    delta_aC: dAC_arr,
    Delta_Ch: chArr,
    observed: obsArr,
  };
}

/** Sweep delta_C from 0.1 to 1.5 */
export function sweepDeltaC(baseParams?: SimulationParams): SweepResult {
  return sweepParameter("delta_C", 0.1, 1.5, 100, baseParams);
}

/** Sweep lambda_1 from 2.0 to 6.0 */
export function sweepLambda1(baseParams?: SimulationParams): SweepResult {
  return sweepParameter("lambda_1", 2.0, 6.0, 100, baseParams);
}

/** Sweep genus from 2 to 7 */
export function sweepGenus(baseParams?: SimulationParams): SweepResult {
  return sweepParameter("genus", 2, 7, 50, baseParams);
}

/** Sweep R from -5 to -0.1 */
export function sweepR(baseParams?: SimulationParams): SweepResult {
  return sweepParameter("R", -5, -0.1, 100, baseParams);
}

/** Sweep b_Ch from 0 to 1 */
export function sweepBCh(baseParams?: SimulationParams): SweepResult {
  return sweepParameter("b_Ch", 0, 1, 100, baseParams);
}

/** Compute convergence of the Choptyuk series */
export function computeConvergence(
  params: SimulationParams = DEFAULT_PARAMS,
  maxTerms: number = 50
): ConvergenceData {
  const terms: number[] = [];
  const partialSums: number[] = [];
  let sum = 0;
  const deltaA = spinorDeltaA();

  for (let n = 1; n <= maxTerms; n++) {
    // Choptyuk series: Δ_Ch = Σ (-1)^(n+1) · b_Ch^n · sin(n·δ_A) / n²
    const term = ((-1) ** (n + 1)) * (params.b_Ch ** n) * Math.sin(n * deltaA) / (n * n);
    sum += term;
    terms.push(n);
    partialSums.push(sum + params.lambda_1); // offset by base eigenvalue
  }

  const limit = partialSums[partialSums.length - 1];
  const convergenceRate = partialSums.length > 10
    ? Math.abs(partialSums[partialSums.length - 1] - partialSums[partialSums.length - 11]) / 10
    : 0;

  return {
    terms,
    partialSums,
    limit,
    convergenceRate,
  };
}

/** Multi-parameter sweep: vary two parameters simultaneously */
export function sweep2D(
  param1: keyof SimulationParams,
  min1: number,
  max1: number,
  steps1: number,
  param2: keyof SimulationParams,
  min2: number,
  max2: number,
  steps2: number,
  baseParams: SimulationParams = DEFAULT_PARAMS
): { x: number[]; y: number[]; z: number[][] } {
  const x: number[] = [];
  const y: number[] = [];
  const z: number[][] = [];

  const deltaA = spinorDeltaA();
  const deltaB = spinorDeltaB();

  for (let i = 0; i <= steps1; i++) {
    x.push(min1 + (max1 - min1) * (i / steps1));
  }
  for (let j = 0; j <= steps2; j++) {
    y.push(min2 + (max2 - min2) * (j / steps2));
  }

  for (let i = 0; i <= steps1; i++) {
    const row: number[] = [];
    for (let j = 0; j <= steps2; j++) {
      const params = {
        ...baseParams,
        [param1]: x[i],
        [param2]: y[j],
      };
      const result = computeFull(params);
      row.push(result.chFull);
    }
    z.push(row);
  }

  return { x, y, z };
}

/** Run full computation with current params */
export function computeCurrent(params: SimulationParams) {
  return computeFull(params);
}
