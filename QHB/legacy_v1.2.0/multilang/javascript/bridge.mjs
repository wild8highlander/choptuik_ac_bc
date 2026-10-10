// bridge.mjs — the Quark-Hawking Bridge twin (JavaScript, self-test).
// Recomputes the closed-form core from the CODATA constants, prints the
// validation block, exits.  Nothing is downloaded, nothing is fitted.
const pi = Math.PI;

// --- Part A: CODATA ----------------------------------------------------------
const G = 6.67430e-11, c = 299792458.0, h = 6.62607015e-34;
const hbar = h / (2 * pi), kB = 1.380649e-23;
const MeV_J = 1.602176634e-13;
const T_CMB = 2.72548;
const T_QCD = 155.16 * MeV_J / kB;

// --- Part B: the septinial family and the three corrections -------------------
const delta_C = pi / 7;
const b_Ch = 1 - Math.cos(2 * pi / 7);
const bC = pi ** 2 / 98, aC = pi ** 5 / 369754;
const bB = pi ** 2 / 18, aB = pi ** 5 / 5346;
const PAGE = 1 - Math.pow(2, -1.5);

// --- closed forms -------------------------------------------------------------
const M_QCD = hbar * c ** 3 / (8 * pi * G * kB * T_QCD);
const M_CMB = hbar * c ** 3 / (8 * pi * G * kB * T_CMB);
const T_H_1e12 = hbar * c ** 3 / (8 * pi * G * 1e12 * kB);
const growth = Math.sqrt(1.5);

function residual(alpha, x) {
  const f = (u) => (u < 1e-300) ? x : -Math.expm1(-x * u) / u;
  const fp = f(1 - alpha), fm = f(1 + alpha);
  return (fp - fm) / (fp + fm);
}

// --- committed C1 constants (verbatim from campaigns/reference/c1_verdict) ----
const DELTA0 = 0.523004556028;
const B2 = -5.49670294e-2;
const GAP_QUAD = DELTA0 + B2 * 0.2 ** 2;   // the quadratic law at beta = 0.2

const rows = [
  ["delta_C = pi/7", delta_C, "0.44879895051282761"],
  ["b_Ch = 1-cos(2pi/7)", b_Ch, "0.37651019814126640"],
  ["bC = pi^2/98", bC, "0.10071024899070774"],
  ["aC = pi^5/369754", aC, "0.0008276304915843546"],
  ["bB = pi^2/18", bB, "0.54831135561607551"],
  ["aB = pi^5/5346", aB, "0.057242739391186152"],
  ["Page fraction", PAGE, "0.64644660940672620"],
  ["M_QCD [kg]", M_QCD, "6.814006e+10"],
  ["M_CMB [kg]", M_CMB, "4.501595e+22"],
  ["T_H(1e12 kg) [K]", T_H_1e12, "1.226901e+11"],
  ["r_Wu(0.9, 100)", residual(0.9, 100), "0.899995686821"],
  ["Gascheau growth sqrt(3/2)", growth, "1.22474487139158905"],
  ["gap law Delta_F(0.2)", GAP_QUAD, "0.520805874852"],
  ["vortex Lagrange 3/(2pi)", 3 / (2 * pi), "0.477464829275686"],
];

let pass = 0;
for (const [name, val, ref] of rows) {
  const refv = parseFloat(ref);
  const rel = Math.abs(val - refv) / Math.abs(refv);
  const ok = rel < 1e-6;
  if (ok) pass++;
  console.log(`${name.padEnd(30)} = ${val.toPrecision(12).padEnd(20)} ` +
              `${ok ? "PASS" : "FAIL"} (rel ${rel.toExponential(2)})`);
}
console.log(`${pass}/${rows.length} checks PASS (qhb twin, JavaScript)`);
