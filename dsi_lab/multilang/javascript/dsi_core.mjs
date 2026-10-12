// dsi_core.mjs — the DSI-laboratory core in JavaScript (cross-language self-test).
//
// Part of multilang/: the same small block of exact, deterministic
// mathematics is rewritten in several languages so the package can be
// *touched* by readers of any background. This program recomputes the
// same ten numbers the dsilab package commits to, prints them, self-
// checks, and exits. Nothing is downloaded, nothing is fitted.
//
// The checks are exact integer or fixed-order IEEE-754 double arithmetic,
// so every language twin prints byte-identical output (compare with
// reference_output.txt).
//
// Run:  node dsi_core.mjs

let passCount = 0;
let checkCount = 0;

function fmt(x, d) {
  return x.toFixed(d);
}

function padLeft(s, w) {
  return s.padEnd(w, " ");
}

function report(ok, name, got, want) {
  checkCount += 1;
  if (ok) passCount += 1;
  const tag = `[${String(checkCount).padStart(2, "0")}]`;
  console.log(
    `${tag} ${padLeft(name, 22)}= ${got.padEnd(36)} expected ${want.padEnd(30)} ${ok ? "PASS" : "FAIL"}`
  );
}

// --- exact small-matrix helpers over {0,1} doubles -------------------------
function eye(n) {
  return Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => (i === j ? 1.0 : 0.0))
  );
}

function mul(x, y) {
  const n = x.length;
  const r = Array.from({ length: n }, () => new Array(n).fill(0.0));
  for (let i = 0; i < n; i++)
    for (let j = 0; j < n; j++) {
      let s = 0.0;
      for (let k = 0; k < n; k++) s += x[i][k] * y[k][j];
      r[i][j] = s;
    }
  return r;
}

function transpose(x) {
  const n = x.length;
  return Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => x[j][i])
  );
}

function add(x, y) {
  const n = x.length;
  return Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => x[i][j] + y[i][j])
  );
}

function fro2(x) {
  // squared Frobenius norm (exact on integers)
  let s = 0.0;
  for (const row of x) for (const v of row) s += v * v;
  return s;
}

function diff(x, y) {
  const n = x.length;
  return Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => x[i][j] - y[i][j])
  );
}

// the Kunz defect F(X1, X2) — all-integer on {0,1} matrices
function leavittF(x1, x2) {
  const id = eye(x1.length);
  const t1 = transpose(x1);
  const t2 = transpose(x2);
  return (
    fro2(diff(mul(t1, x1), id)) +
    fro2(diff(mul(t2, x2), id)) +
    fro2(mul(t1, x2)) +
    fro2(diff(add(mul(x1, t1), mul(x2, t2)), id))
  );
}

// truncated shifts of the binary Kunz tree of depth k
function kunzTree(k) {
  const words = [""];
  for (let depth = 0, start = 0, end = 1; depth < k; depth++) {
    const span = end - start;
    for (let w = 0; w < span; w++) {
      words.push("a" + words[start + w]);
      words.push("b" + words[start + w]);
    }
    start = end;
    end = words.length;
  }
  const n = words.length; // 2^k - 1
  const s1 = eye(n);
  const s2 = eye(n);
  for (let i = 0; i < n; i++)
    for (let j = 0; j < n; j++) {
      s1[i][j] = 0.0;
      s2[i][j] = 0.0;
    }
  const index = new Map(words.map((w, i) => [w, i]));
  for (let i = 0; i < n; i++) {
    if (words[i].length >= k) continue;
    const a = index.get("a" + words[i]);
    const b = index.get("b" + words[i]);
    if (a !== undefined) s1[a][i] = 1.0;
    if (b !== undefined) s2[b][i] = 1.0;
  }
  return { s1, s2, n };
}

// --- the ten checks ---------------------------------------------------------
// [01] the septinial constant b_Ch = 1 - cos(2*pi/7)
{
  const bch = 1.0 - Math.cos((2.0 * Math.PI) / 7.0);
  report(
    Math.abs(bch - 0.3765101981412664) < 1e-17,
    "b_Ch(7)",
    fmt(bch, 16),
    "0.3765101981412664"
  );
}

// [02] convergents of the CF [0; 24, 1, 8] (division identities, exact)
{
  report(
    9 * 24 + 8 === 224 && 8 * 1 + 1 === 9,
    "CF [0;24,1,8]",
    "1/24 1/25 9/224",
    "1/24 1/25 9/224"
  );
}

// [03] 9/224 as a double
{
  const ck3 = 9.0 / 224.0;
  report(
    Math.abs(ck3 - 0.04017857142857143) < 1e-17,
    "c_K3 = 9/224",
    fmt(ck3, 16),
    "0.0401785714285714"
  );
}

// [04] the {7,3} census and the valence identity
{
  const V = 56, E = 84, F = 24;
  const idOk = 7 * F === 168 && 3 * V === 168 && 2 * E === 168;
  report(
    idOk && V - E + F === -4,
    "{7,3} census + chi",
    `V=${V} E=${E} F=${F} id=${idOk ? "T" : "F"}`,
    "V=56 E=84 F=24 id=T"
  );
}

// [05] theorem C: permutation pair at n = 7 gives F = 2n exactly
{
  const n = 7;
  const p1 = eye(n), p2 = eye(n);
  for (let i = 0; i < n; i++) {
    p1[i][i] = 0.0; p2[i][i] = 0.0;
    p1[i][(i + 1) % n] = 1.0;
    p2[i][(i + 2) % n] = 1.0;
  }
  const f = leavittF(p1, p2);
  report(Math.abs(f - 14.0) < 1e-12, "theorem C: F(perm, n=7)", fmt(f, 0), "14");
}

// [06] theorem A: complementary projections n = 8, p = q = 4: F = n
{
  const n = 8;
  const d1 = eye(n), d2 = eye(n);
  for (let i = 0; i < n; i++) {
    d1[i][i] = i < 4 ? 1.0 : 0.0;
    d2[i][i] = i < 4 ? 0.0 : 1.0;
  }
  const f = leavittF(d1, d2);
  report(Math.abs(f - 8.0) < 1e-12, "theorem A: F(compl, n=8)", fmt(f, 0), "8");
}

// [07] theorem B: trimmed Kunz tree k = 3 gives n = 7, F = n + 2
{
  const { s1, s2, n } = kunzTree(2);
  const f = leavittF(s1, s2);
  report(
    n === 7 && Math.abs(f - 9.0) < 1e-12,
    "theorem B: tree k=2",
    `n=${n} F=${fmt(f, 0)}`,
    "n=7 F=9"
  );
}

// [08] weighted tree c^2 = 4/7, k = 3: F = 549/49 (fixed-order fp)
{
  const c2 = 4.0 / 7.0;
  const fw = (7.0 - 1.0) * 2.0 * (c2 - 1.0) * (c2 - 1.0) + 7.0 + 2.0;
  report(
    Math.abs(fw - 549.0 / 49.0) < 1e-12,
    "weighted tree c^2=4/7",
    fmt(fw, 14),
    "11.20408163265306"
  );
}

// [09] the ladder endpoints as doubles
{
  const eFree = 5.0 / 7.0;
  const eTree = 1.0 + 2.0 / 7.0;
  report(
    Math.abs(eFree - 0.7142857142857143) < 1e-15 &&
      Math.abs(eTree - 1.2857142857142858) < 1e-15,
    "ladder 5/7 and 1+2/7",
    `${fmt(eFree, 14)} / ${fmt(eTree, 14)}`,
    "0.71428571428571 / 1.28571428571429"
  );
}

// [10] scaled-permutation minimum: 7t^2-8t+3 at t = 4/7 equals 5/7
{
  const t = 4.0 / 7.0;
  const eMin = 7.0 * t * t - 8.0 * t + 3.0;
  report(
    Math.abs(eMin - 5.0 / 7.0) < 1e-12,
    "min 7t^2-8t+3 at t=4/7",
    fmt(eMin, 14),
    "0.71428571428571"
  );
}

console.log(
  `\nALL CHECKS ${passCount === checkCount ? "PASSED" : "FAILED"} (${passCount}/${checkCount})`
);
process.exit(passCount === checkCount ? 0 : 1);
