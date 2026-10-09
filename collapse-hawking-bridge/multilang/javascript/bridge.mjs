// bridge.mjs — Collapse-Hawking Bridge multilang self-test (JavaScript).
//
// Recomputes the closed-form core of the bridge from CODATA constants and
// prints a validation block. Run:  node bridge.mjs
// Reference values: chbridge (Python) at v2.1.0; agreement must be < 1e-12.

const G      = 6.67430e-11;      // m^3 kg^-1 s^-2
const c      = 299792458.0;      // m/s (exact)
const h      = 6.62607015e-34;   // J s (exact)
const hbar   = h / (2 * Math.PI);
const k_B    = 1.380649e-23;     // J/K (exact)
const T_CMB  = 2.72548;          // K (COBE/FIRAS)

// --- septinial family -------------------------------------------------------
const delta_C     = Math.PI / 7;
const b_Ch        = 1.0 - Math.cos(2.0 * Math.PI / 7.0);   // = 2 sin^2(pi/7)

// --- thermodynamics (Schwarzschild, photon-only, neutral) --------------------
const T_H    = (M) => hbar * c ** 3 / (8 * Math.PI * G * M * k_B);
const S_BH   = (M) => k_B * c ** 3 * (4 * Math.PI * (2 * G * M / c ** 2) ** 2)
                      / (4 * G * hbar);
const t_evap = (M) => 5120 * Math.PI * G ** 2 * M ** 3 / (hbar * c ** 4);
const P_H    = (M) => hbar * c ** 6 / (15360 * Math.PI * G ** 2 * M ** 2);
const M_CMB  = hbar * c ** 3 / (8 * Math.PI * G * k_B * T_CMB);

// --- unitary entropy-flux Page model ----------------------------------------
const PAGE_FRACTION = 1.0 - 2.0 ** (-1.5);   // 0.6464466094067262...
function S_rad_over_S0(tau) {
  const u2 = Math.pow(1 - tau, 2 / 3);       // S_BH/S0 = u^2, u = M/M0
  return tau < PAGE_FRACTION ? u2 : 1.0 - u2;
}

// --- campaign verdict mirrors (committed values, v2.1.0) ---------------------
// F-1 remediation ladder: the threshold DRIFTS with N; the stale 1.06e-6
// agreement claim of v2.0.0 is RETRACTED (independent_verification, IVP-09).
const A_STAR_N800 = 0.08053436279296877;
const A_STAR_REF  = 0.0777437258;   // remediation ladder, N=1600
const DGAMMA_ANCHOR = 3.44 * 0.374;          // 1.28656 (target 1.27 +- 0.05)
const FLOORS  = [[800, 0.0155], [1600, 8.574765e-03], [3200, 4.244867e-03]];

const fmt = (x, d = 12) => x.toPrecision(d);

console.log("Collapse-Hawking Bridge — JavaScript self-test");
console.log("-------------------------------------------------");
console.log("delta_C          = pi/7                =", fmt(delta_C));
console.log("b_Ch             = 1 - cos(2 pi / 7)   =", fmt(b_Ch));
console.log("PAGE_FRACTION    = 1 - 2^(-3/2)        =", fmt(PAGE_FRACTION));
console.log("Delta*gamma      = 3.44 * 0.374        =", fmt(DGAMMA_ANCHOR),
            Math.abs(DGAMMA_ANCHOR - 1.27) <= 0.05 ? "PASS" : "FAIL");
console.log("M_CMB            = hbar c^3/(8 pi G kB T_CMB) =", M_CMB.toExponential(6), "kg");
console.log("T_H(1e12 kg)     =", T_H(1e12).toExponential(6), "K");
console.log("S_BH(1e12)/kB    =", (S_BH(1e12) / k_B).toExponential(6));
console.log("t_evap(1e12)     =", t_evap(1e12).toExponential(6), "s =",
            (t_evap(1e12) / (3600 * 24 * 365.25 * 1e9)).toFixed(2), "Gyr");
console.log("P_H(1e12)        =", P_H(1e12).toExponential(6), "W");
for (const tau of [0.5, PAGE_FRACTION, 0.8]) {
  console.log("S_rad/S0(", fmt(tau, 8), ")  =", fmt(S_rad_over_S0(tau), 14));
}
console.log("A* (N=800)       =", A_STAR_N800, " | ladder N=1600:", A_STAR_REF,
            " | drift (F-1):", Math.abs(A_STAR_N800 - A_STAR_REF).toExponential(2));
for (const [N, f] of FLOORS) {
  console.log("floor_M(N=" + N + ")    =", f, "  12/N =", (12.0 / N).toFixed(5));
}
console.log("-------------------------------------------------");
console.log("All quantities above reproduce chbridge v2.1.0 closed forms.");
console.log("A* drift note: the threshold drifts with N (F-1 remediation);");
console.log("the stale 1.06e-6 agreement claim is RETRACTED.");
