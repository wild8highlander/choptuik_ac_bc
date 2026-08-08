// ============================================================
// TypeScript types for Choptyuk Spinor Monograph
// ============================================================

/** Klein quartic curve parameters */
export interface KleinCurveParams {
  genus: number;        // g = 3
  automorphismOrder: number; // |PSL(2,7)| = 168
  lambda1: number;      // first eigenvalue ≈ 3.838
  R: number;            // R = -2
  curvature: number;    // scalar curvature
}

/** Spinor phase parameters */
export interface SpinorPhases {
  delta_A: number;  // π/2
  delta_B: number;  // π/3
  delta_C: number;  // π/7
}

/** Dirac operator data */
export interface DiracData {
  lambda_D2_triv: number;  // 3.338 - trivial connection
  delta_bC: number;        // 3.438710 - b-C correction
  delta_aC: number;        // 0.000828 - a-C effective correction
}

/** Choptyuk invariant data */
export interface ChoptyukData {
  Delta_Ch_base: number;  // 3.437883
  Delta_Ch_full: number;  // 3.447040
  b_Ch: number;           // 0.376510
  observed_Delta: number; // 3.443
  deviation: number;      // |observed - computed|
}

/** Single spinor structure among 64 */
export interface SpinorStructure {
  index: number;          // 0-63
  phase_A: number;        // phase contribution from A
  phase_B: number;        // phase contribution from B
  phase_C: number;        // phase contribution from C
  delta_total: number;    // total correction
  is_stable: boolean;     // stability flag
  symmetry_class: string; // e.g. "C2", "C3", "C7", "D4", "S3"
  eigenvalue: number;     // associated eigenvalue
}

/** Riemann surface data */
export interface RiemannSurface {
  name: string;           // "Bolza", "Bring", "Macbeath"
  genus: number;
  automorphismOrder: number;
  lambda1: number;
  delta_bC: number;
  delta_aC: number;
  Delta_Ch: number;
  curvature: number;
}

/** LIGO/Virgo gravitational wave event */
export interface GWEvent {
  name: string;           // e.g. "GW150914"
  date: string;
  masses: [number, number]; // [m1, m2] in solar masses
  finalMass: number;
  spin: number;           // final dimensionless spin
  qnmFrequency: number;   // predicted QNM frequency (Hz)
  qnmDamping: number;     // predicted QNM damping time (ms)
  chirpMass: number;      // chirp mass
  snr: number;            // signal-to-noise ratio
}

/** Hypothesis test result */
export interface HypothesisTest {
  name: string;
  computed: number;
  reference: number;
  tolerance: number;
  deviation: number;
  relativeError: number;
  passed: boolean;
}

/** Simulation parameters for interactive sweep */
export interface SimulationParams {
  delta_C: number;       // spinor phase C ∈ [0.1, 1.5]
  lambda_1: number;      // first eigenvalue ∈ [2.0, 6.0]
  k_struct: number;      // structure index ∈ [0, 63]
  c4: number;            // c4 coefficient ∈ [0, 2]
  c6: number;            // c6 coefficient ∈ [0, 2]
  genus: number;         // genus ∈ [2, 5]
  R: number;             // scalar curvature ∈ [-5, 0]
  b_Ch: number;          // Choptyuk parameter ∈ [0, 1]
}

/** Sweep result for parameter sweep visualization */
export interface SweepResult {
  parameter: string;
  values: number[];
  delta_bC: number[];
  delta_aC: number[];
  Delta_Ch: number[];
  observed: number[];
}

/** Convergence data for series analysis */
export interface ConvergenceData {
  terms: number[];
  partialSums: number[];
  limit: number;
  convergenceRate: number;
}

/** Verification entry */
export interface VerificationEntry {
  id: string;
  description: string;
  computed: number;
  expected: number;
  tolerance: number;
  passed: boolean;
  relativeError: number;
  deviation: number;
}

/** K3 Surface data */
export interface K3SurfaceData {
  b0: number;     // 1
  b1: number;     // 0
  b2: number;     // 22
  b3: number;     // 0
  b4: number;     // 1
  hodge11: number; // 20
  hodge20: number; // 1
  diracIndex: number; // 2
  b2Plus: number; // 3
  b2DecompositionValid: boolean;
  swCompatible: boolean;
}

/** Tyukovsky equation data */
export interface TyukovskyData {
  delta0: number;
  deltaC: number;
  deltaCorrected: number;
  echoPeriod: number;
  echoShiftPct: number;
  freeParameters: number;
}

/** Einstein GR QNM correction */
export interface EinsteinQNMData {
  deltaEff: number;
  qnmCorrection: number;
  qnmFactor: number;
  correctionPct: number;
}

/** Enhanced verification results */
export interface EnhancedVerificationResult {
  k3Surface: K3SurfaceData;
  tyukovsky: TyukovskyData;
  einsteinQNM: EinsteinQNMData;
  imaginaryCorrection: number;
  kahlerCorrection: number;
  b2Uniqueness: Record<string, {deviationPct: number; compatible: boolean}>;
  spinStructureDistribution: {total: number; even: number; odd: number; goodPct: number};
}

/** Report format */
export type ReportFormat = "json" | "html" | "csv" | "txt" | "md";
