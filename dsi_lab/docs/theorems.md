# The theorem layer of the DSI laboratory

Status labels: **[proved]** — exact proof; **[proved + verified]** —
proof plus machine-precision numerical check with fixed seeds; **[refuted]**
— the statement is *false* and the package keeps the falsifying data.
Lean 4 counterparts: exact stratum in `lean4/DSILab.lean` (sorry-free);
theorems A/B/C anchored by axioms documented with the verifying
experiment.

---

## T1 — the sharp trace theorem **[proved + verified]**

For every n and every pair X₁, X₂ ∈ M_n(C),

```text
F(X₁,X₂) ≥ 5n/7,      e = F/n ≥ 5/7,
```

where F is the Kunz defect. The equality case is the scalar pair
X₁ = X₂ = √(4/7)·I, which is *not* a partial isometry (singular value
√(4/7) ≠ 1). Numerical check: L-BFGS minimization with restarts at
n = 7..12 lands on the floor with gap ≤ 5.92e-8
(`results/exp1_sh3.json`, `theorem_big_n.minimization`); the exact
rational minimum of the scaled-permutation family 7t² − 8t + 3 at
t = 4/7 is verified in Lean (`scaled_permutation_minimum`).

## T2 — the Kunz-tree identity **[proved + verified]**

For the depth-k trimmed Kunz tree (n = 2^(k+1) − 1 nodes, shifts S₁, S₂
with disjoint ranges on depth ≥ 1):

```text
F(S₁, S₂) = n + 2   exactly,     e = 1 + 2/n → 1.
```

Proof sketch: `I − S₁S₁* − S₂S₂*` has rank 1 (only the root survives), and
theorem T4 below turns rank 1 into the +2. Verified to |err| ≤ 5.7e-14
for k = 2..10 (`exp1_sh3.json`, `tree.truncation`; `exp7_e1_threshold.json`,
`theorem_B.tree`). Lean: the arithmetic layer of T4.

## T3 — the weighted-tree formula **[proved + verified]**

For the weighted tree Xᵢ = cᵢ·Sᵢ:

```text
F = (n−1)·[(c₁²−1)² + (c₂²−1)²] + n + 2,
```

minimized at c₁ = c₂ = 1: **no weighting improves the trimming**, and no
weighted tree reaches 5/7. Verified to 1e-9 for k = 2..7 at several
weights (`exp1_sh3.json`, `tree.weighted`). At c² = 4/7, k = 3 the value
is exactly 549/49 — proved in Lean (`weighted_tree_549_49`).

## T4 — theorem A (the threshold) **[proved + verified]**

For partial isometries X₁, X₂ ∈ M_n (all nonzero singular values equal 1):

```text
F(X₁,X₂) ≥ n,      i.e.  e ≥ 1.
```

*Proof (5 lines).* For partial isometries P = X₁X₁*, Q = X₂X₂* are
projections, p = rank P, q = rank Q, r = tr(PQ), and the audited identity
F = G(P,Q) = 3n − 2p − 2q + 3r holds. Dimension gives
max(0, p+q−n) ≤ r ≤ min(p,q). If p+q ≥ n: F − n = 3r − 2(p+q−n) ≥
3(p+q−n) − 2(p+q−n) = p+q−n ≥ 0; if p+q ≤ n: F − n = 2(n−p−q) + 3r ≥ 0. ∎

Equality ⟺ P·Q = 0 and p + q = n (complementary projections). Numerical
check: the identity F = 3n − 2p − 2q + 3r holds to 5.9e-16 over 24 000
random pairs, and **zero** threshold violations among them
(`exp7_e1_threshold.json`, `theorem_A`). Lean: `theorem_A_threshold`
(axiom-anchored), corollary D derived from it.

## T5 — theorem B (exact coverage arithmetic) **[proved + verified]**

If X₁ = P, X₂ = Q are projections with P + Q ≤ I, then

```text
F = n + 2·rank(I − P − Q)   exactly.
```

In particular the trimmed Kunz tree covers everything except the root:
rank(I − P − Q) = 1 and F = n + 2. Verified on random disjoint
projections (max |err| = 2.3e-13) and on the tree k = 2..10
(`exp7_e1_threshold.json`, `theorem_B`). Lean: arithmetic stratum.

## T6 — theorem C (unitary pairs) **[proved + verified]**

If X₁, X₂ are unitary, then

```text
F = 2n  exactly   (e = 2);
```

the defect comes entirely from the overlap term ‖X₁*X₂‖² = n. Permutation
models are the special case the framework uses. Verified: max
|F − 2n| = 2.8e-14 over unitary and permutation pairs
(`exp7_e1_threshold.json`, `theorem_C`).

## T7 — corollary D (class closure) **[proved]**

inf e over carrier-isometric pairs = 1; the value 5/7 is unreachable in
the class, hence the Ш.3(iii) bridge (sofic amplifications driving the
defect to zero) is impossible for isometric transports: η ≡ 1 > 0. This
upgrades the Ш1–Ш4 chain: Ш2 holds class-wide. Lean: `corollary_D_class_closure`
(derived from T4, sorry-free).

## T8 — the sofic √ε-law is refuted **[refuted]**

The conjecture "natural transports of sofic data with error ε drive
e → 0 like C·ε^(1/2)" is **false** in the tested class: random
permutations with fixed-point share ε, transported as c·P with the
optimal c, keep the defect flat (the Hamming scan of `exp1_sh3.json`,
`hamming`). The data is kept as an honest negative.

## T9 — the census lemma (valence identity) **[proved]**

For the {7,3} tiling of the Klein quartic built as coset spaces of
G = GL(3,2) ≅ PSL(2,7):

```text
V = 56,  E = 84,  F = 24,   7F = 3V = 2E = |G| = 168,   V − E + F = −4.
```

The element census (1, 21, 56, 42, 48 by order) and the Sylow numbers
n₂ = 21, n₃ = 28, n₇ = 8 are verified in the explicit enumeration
(`exp6_census_224.json`, `census`). Lean: `census_valence_identity`,
`census_euler` (sorry-free).

## T10 — the uniqueness lemma for 9/224 **[proved + verified]**

Among fractions p/q with q ≤ 5000, p ≤ 32 whose denominator is 7-smooth
within the census budget (v₂ ≤ 6, v₃ ≤ 1, v₇ ≤ 1), the fraction 9/224 is
the **only** one within 0.1 % (and a fortiori 0.01 %) of the measured
c_K3; among the convergents of the continued fraction of c_K3, only
1/24 and 9/224 pass the census filter (`exp6_census_224.json`,
`census_filter`). Lean: the CF layer (`cf_9_224_*`, `cK3_eq_cf`).

## T11 — the degeneracy theorem for the genus family **[proved]**

On the Hurwitz tower the two structural readings of DSI-4,

```text
branch I  : c_I(g)  = 27/(4|G|) = 9/(4V)            ~ (g−1)⁻¹
branch II : c_II(g) = (N−1)/(F·N),  N = 14(g−1)      ~ (g−1)⁻¹·(1−1/N),
```

coincide **only at g = 3** (the Klein quartic), while the framework's
branch III c_III(g) = b_Ch(b₂(g)) ~ (g−1)⁻² separates already at g = 7.
Consequence: a single DSI-amplitude measurement on any higher Hurwitz
surface discriminates the mechanisms (`exp6_census_224.json`, `genus`).

## T12 — finding D1 (the Hurwitz row) **[proved, correction]**

The repository row (g = 14, n = 11) is impossible: 84·13 = 1092 is not
divisible by 11, so no order-11 automorphism exists. The correct genus-14
Hurwitz group is PSL(2,13) of signature (2,3,13); the corrected tower
passes all three checks (84(g−1) = |G|, n | |G|, 1/2 + 1/3 + 1/n < 1) and
the framework curve gives Δ_Ch(π/13) = 3.3672 (`exp3_hurwitz.json`).

## T13 — the falsifiable overtone law **[verified, falsifiable]**

From the committed QNM catalogue: |Δf_n|/f_n = const = 8.3857e-5 across
the GW150914 overtone ladder, with overtone detectability 0.84σ at
Cosmic Explorer. This is a *prediction* of the framework, structured so
that a single null result kills it (`exp4_qnm.json`, `overtones`).

## T14 — finding E1 (the QCD centering) **[verified, correction]**

The trace tr(Q_K3 ⊕ M_F) = 32 exists only after centering ⟨λ⟩; on the
centered tower |⟨λ⟩| scales as 1/√N with slope −0.99, and the κ_T-sweep
gives BF(GUE) up to 1165 against Poisson (`exp5_qcd.json`, `nscaling`,
`kappa_sweep`). The honest caveat: V_T remains a constructive model of
T-violation, not a derivation.

## Open problems carried by the package

1. **Ш.3(iii) without isometries** — whether *non*-isometric transports
   can beat the floor is untouched by T4–T7; the class closure says only
   that the isometric route is dead.
2. **DSI-4 derivation** — the +0.0025 % match of 9/224 is an observation
   with a uniqueness lemma, not a derivation from the DSI
   renormalization.
3. **b₂ on higher Hurwitz surfaces** — the pattern 2b+2 is a structural
   hypothesis of the framework (labeled as such in experiment 3).
