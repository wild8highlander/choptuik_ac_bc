# The theory behind the seven experiments

This note states, without proofs, the mathematical background that the
experiments of the DSI laboratory stand on. Proofs and full statements
live in [`theorems.md`](theorems.md); the numerical evidence lives in the
committed verdicts [`../results/`](../results/).

## 1. The framework: spinor corrections b-C and a-C

The parent repository verifies two spinor corrections on the Klein
quartic curve: the first-order Berry-type correction b-C and the
second-order braking correction a-C. Both are built on the *septinial
phase* δ_C = π/7, which produces the dimensionless framework constant

```text
b_Ch = 1 − cos(2π/7) = 0.37651019814126640,
```

and the Choptuik-side universal curve Δ_Ch(δ) = λ_D2 + δ²/2 − δ⁵/22 with
λ_D2 = 3.338. The DSI laboratory ("dynamics of invariants") tests what
happens when the framework's inputs are *derived* rather than assumed:
experiment 2 asks whether the last empirical input, c_K3 = 0.0401775…,
is forced by arithmetic; experiments 3 and 6 audit and extend the
algebraic tower that is supposed to generate it.

## 2. The Klein quartic and PSL(2,7)

The Klein quartic X: x³y + y³z + z³x = 0 is the genus-3 curve with the
largest possible automorphism group: |Aut(X)| = 84·(3−1) = 168, and
PSL(2,7) ≅ GL(3,2) acts on it. Its {7,3} tiling is a self-dual map with

```text
V = 56 triangular faces,  E = 84 edges,  F = 24 heptagons,
7F = 3V = 2E = |PSL(2,7)| = 168,   V − E + F = 2 − 2·3 = −4.
```

Experiment 6 builds this census *explicitly*: the vertices, edges and
faces are the coset spaces of G = GL(3,2) by the stabilizers of a point,
an edge and a heptagon, and the valence identity is a theorem about
group orders, not an observation. The Klein graph (the 1-skeleton {3,7})
has degree 3 and girth 7 — it is the Tutte–Coxeter graph's dense cousin
and the combinatorial spine of the whole package.

## 3. The Kunz tree and the Kunz defect F

The Cuntz/Kunz tree encodes the two-generator relations of the
framework's noncommutative data. Truncating the infinite binary tree at
depth k and taking the two level-raising shifts S₁, S₂ gives n = 2^(k+1)
− 1 partial isometries whose ranges split depth ≥ 1 without overlap.
The *Kunz defect* of a pair (X₁, X₂) is the Frobenius-norm functional

```text
F(X₁,X₂) = ‖X₁*X₁ − I‖² + ‖X₂*X₂ − I‖² + ‖X₁*X₂‖²
           + ‖X₁X₁* + X₂X₂* − I‖²,
```

the per-generator ratio e = F/n is the quantity the framework wants to
push to zero. The sharp trace theorem forbids it: **F ≥ 5n/7 for every
n**, so e ≥ 5/7 for scalars, and the partial-isometry theorems A/B/C of
experiment 7 pin the whole landscape: e ≥ 1 on the class, F = n + 2·rank
(I−P−Q) exactly under coverage, F = 2n for unitaries. The trimmed tree
attains F = n + 2 exactly — the almost-extremal pair of the class — and
the weighted-tree formula shows no weighting does better. The sofic
√ε-law (defect → 0 along amplifications with error ε) is **refuted** by
the data of experiment 1: the observed defect does not fall with ε.

## 4. DSI-4 and the denominator 224

The last empirical input of the framework is the K3-closure value

```text
c_K3 = 0.04017757639214903   (measured, audit 2026-09),
```

and the DSI-4 observation is that the exact rational

```text
c_K3 = 3³/(2²·|PSL(2,7)|) = 27/672 = 9/224 = 0.040178571428571…
```

deviates from it by +0.0025 % — three orders of magnitude tighter than
every structural alternative (b_Ch(22) +0.82 %, braking RG +0.45 %,
1/25 −0.44 %). Experiment 2 shows 9/224 is a convergent of the continued
fraction of the measured value (rank #1 exclusivity for q ≤ 2000);
experiment 6 proves the census-uniqueness lemma — among 7-smooth
denominators in the census budget, 9/224 is the *only* fraction that
close — and the degeneracy theorem: on the Hurwitz tower the two
structural readings of DSI-4 coincide only at g = 3, the Klein quartic
itself.

## 5. The Hurwitz tower and finding D1

Hurwitz surfaces carry automorphisms of order 84(g−1). The tower the
package uses is

```text
g = 3   PSL(2,7)    (2,3,7)    |G| = 168
g = 7   PSL(2,8)    (2,3,9)    |G| = 504   (Fricke–Macbeath)
g = 14  PSL(2,13)   (2,3,13)   |G| = 1092
g = 17  (2,3,8) triplet        |G| = 1344
```

Experiment 3 audits the repository row and **finds D1**: the stored
genus-14 row (g = 14, n = 11) is impossible, because 84·13 = 1092 is not
divisible by 11 — there is no element of order 11. The corrected group
is PSL(2,13), and the framework curve evaluates to Δ_Ch(π/13) = 3.3672.
The finding is a correction *produced by* the package and is kept in the
committed verdicts as an honest negative about the previous row.

## 6. QNM overtones and the QCD bridge

Experiment 4 assembles the QNM catalogue of ten events and extracts a
falsifiable law from the GW150914 overtone ladder:

```text
|Δf_n| / f_n = const = 8.3857e-5,
```

with overtone detectability 0.84σ at Cosmic Explorer. Experiment 5 tests
the QCD bridge on the framework's own operator: the work formula
θ_eff = δ_C · N·⟨λ⟩ · S_GUE requires centering ⟨λ⟩ — finding **E1**:
tr(Q_K3 ⊕ M_F) = 32 must be read after centering — after which the
|⟨λ⟩| scaling follows 1/√N with slope −0.99, and the κ_T-sweep gives
BF(GUE) up to 1165 against the Poisson null.

## 7. What is proved, what is verified, what is open

The package keeps the honesty discipline of the monographs: every
claim carries a status label (proved / verified numerically / refuted /
open) and an address in the claim ledger,
[`claim_ledger.md`](claim_ledger.md). The one-sentence version: the
census arithmetic, the ladder and the convergent facts are *proved*;
theorems A/B/C are *proved and verified* (analytically, and numerically
to 5.9e-16); the sofic law is *refuted*; the DSI-4 formula, the b₂
pattern on higher Hurwitz surfaces and the QCD T-violation model remain
*hypotheses* — labeled as such everywhere they appear.
