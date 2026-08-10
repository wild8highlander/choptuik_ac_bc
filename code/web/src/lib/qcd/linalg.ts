/**
 * linalg.ts — Minimal numeric linear algebra used by the client-side preview.
 *
 * We avoid a heavy dependency (numeric.js / ml-matrix) by implementing:
 *   • mulberry32 PRNG + Box–Muller Gaussian
 *   • Symmetric eigen-decomposition via the Jacobi rotation algorithm
 *   • Sort + basic array stats
 *
 * These mirror numpy.linalg.eigvalsh closely enough for live slider previews;
 * the canonical values come from the Python engine (NumPy LAPACK) via /api/run.
 */

/** Mulberry32 — small, fast, seedable PRNG (matches numpy default_rng only approximately). */
export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Standard-normal sample via Box–Muller using a provided uniform generator. */
export function gaussian(rng: () => number): number {
  let u = 0;
  let v = 0;
  while (u === 0) u = rng();
  while (v === 0) v = rng();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

/** Fill an n×n matrix with i.i.d. standard-normal entries (row-major Float64Array). */
export function randnMatrix(n: number, rng: () => number): Float64Array {
  const m = new Float64Array(n * n);
  for (let i = 0; i < m.length; i++) m[i] = gaussian(rng);
  return m;
}

/** Compute A + Aᵀ (in place) and return the symmetric matrix. */
export function symmetrize(M: Float64Array, n: number): Float64Array {
  const out = new Float64Array(n * n);
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      out[i * n + j] = 0.5 * (M[i * n + j] + M[j * n + i]);
    }
  }
  return out;
}

/**
 * Jacobi eigenvalue algorithm for symmetric matrices.
 * Returns sorted (ascending) eigenvalues. O(n³) per sweep, ~10 sweeps for n≤64.
 *
 * Reference: Numerical Recipes §11.1 (Jacinth rotation variant).
 */
export function eigvalshSym(M: Float64Array, n: number, maxSweeps = 100): number[] {
  // Work on a copy.
  const a = Float64Array.from(M);
  const off = new Float64Array(n);
  // Use cyclic Jacobi: iterate over upper-triangle pairs.
  for (let sweep = 0; sweep < maxSweeps; sweep++) {
    // off-diagonal sum of squares
    let sum = 0;
    for (let p = 0; p < n - 1; p++) {
      for (let q = p + 1; q < n; q++) {
        sum += a[p * n + q] * a[p * n + q];
      }
    }
    if (sum < 1e-30) break;

    // threshold for this sweep (only first 3 sweeps)
    const thresh = sweep < 3 ? 0.2 * sum / (n * n) : 0;

    for (let p = 0; p < n - 1; p++) {
      for (let q = p + 1; q < n; q++) {
        const apq = a[p * n + q];
        const g = 100 * Math.abs(apq);
        const app = a[p * n + p];
        const aqq = a[q * n + q];

        if (sweep > 3 && Math.abs(app) + g === Math.abs(app) && Math.abs(aqq) + g === Math.abs(aqq)) {
          a[p * n + q] = 0;
        } else if (Math.abs(apq) > thresh) {
          let theta = (aqq - app) / (2 * apq);
          let t: number;
          if (Math.abs(theta) > 1e15) {
            t = 0.5 / theta;
          } else {
            t = Math.sign(theta) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
          }
          const c = 1 / Math.sqrt(t * t + 1);
          const s = t * c;
          const tau = s / (1 + c);

          a[p * n + p] = app - t * apq;
          a[q * n + q] = aqq + t * apq;
          a[p * n + q] = 0;
          a[q * n + p] = 0;

          for (let i = 0; i < n; i++) {
            if (i !== p && i !== q) {
              const aip = a[i * n + p];
              const aiq = a[i * n + q];
              a[i * n + p] = aip - s * (aiq + tau * aip);
              a[p * n + i] = a[i * n + p];
              a[i * n + q] = aiq + s * (aip - tau * aiq);
              a[q * n + i] = a[i * n + q];
            }
          }
        }
      }
    }
  }

  const eigs = new Array(n);
  for (let i = 0; i < n; i++) eigs[i] = a[i * n + i];
  eigs.sort((a, b) => a - b);
  return eigs;
}

/** Convenience: build a symmetric GUE-like matrix and return its eigenvalues. */
export function gueEigenvalues(n: number, rng: () => number, scale = 1): number[] {
  const M = randnMatrix(n, rng);
  const S = symmetrize(M, n);
  // Match Python: V_T = 0.5*(G+Gᵀ)/sqrt(n), then O += kappa_T*V_T.
  const norm = 1 / Math.sqrt(n);
  for (let i = 0; i < S.length; i++) S[i] *= norm * scale;
  return eigvalshSym(S, n);
}

export function mean(xs: number[]): number {
  if (!xs.length) return 0;
  let s = 0;
  for (const x of xs) s += x;
  return s / xs.length;
}

export function std(xs: number[]): number {
  if (xs.length < 2) return 0;
  const m = mean(xs);
  let s = 0;
  for (const x of xs) s += (x - m) * (x - m);
  return Math.sqrt(s / (xs.length - 1));
}

/** Atas folded ratio: s_i = (λ_{i+1} − λ_i) / ⟨λ_{i+1} − λ_i⟩. */
export function foldedSpacings(eigs: number[]): number[] {
  const sorted = [...eigs].sort((a, b) => a - b);
  const s: number[] = [];
  for (let i = 0; i < sorted.length - 1; i++) s.push(sorted[i + 1] - sorted[i]);
  const m = mean(s);
  return m > 0 ? s.map((x) => x / m) : s;
}

/** GUE (β=2) Wigner surmise: P(s) = (32/π²)·s²·exp(−4s²/π). */
export function gueSpacingPdf(s: number): number {
  return (32 / (Math.PI * Math.PI)) * s * s * Math.exp((-4 * s * s) / Math.PI);
}

/** Poisson spacing: P(s) = exp(−s). */
export function poissonSpacingPdf(s: number): number {
  return Math.exp(-s);
}

/** Kass–Raftery BF classification. */
export function classifyBF(bf: number): string {
  if (bf < 1) return "negative";
  if (bf < 3) return "weak";
  if (bf < 20) return "positive";
  if (bf < 150) return "strong";
  return "decisive";
}
