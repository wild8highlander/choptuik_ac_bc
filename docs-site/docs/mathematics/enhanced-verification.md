# Enhanced Verification

The **enhanced verification** system goes beyond the standard verification suite by providing **certified error bounds**, **cross-module consistency checks**, and **interval-arithmetic enclosures** for all computed quantities. This page describes the mathematical theory and implementation strategy behind these rigorous checks.

## Motivation

Standard floating-point verification confirms that computed values agree with theoretical predictions to the requested number of digits. However, this does not constitute a mathematical proof of equality—it only shows agreement within round-off tolerance. The enhanced verification system addresses this by:

1. **Enclosing all quantities in validated intervals** using interval arithmetic.
2. **Propagating error bounds** through every step of the computation.
3. **Cross-checking results** between independent algorithms to eliminate implementation-specific errors.

## Interval Arithmetic

The enhanced verification uses **interval arithmetic** (via the `mpmath.iv` module) to maintain rigorous error bounds throughout all computations. Every quantity is represented as a **validated interval** \([a, b]\) that is guaranteed to contain the true value.

### Example: Klein Quartic Automorphism Check

To verify that the automorphism group has order 168, we compute the order using two independent methods:

- **Method A**: Count the elements of \(\mathrm{PSL}(2,7)\) via the presentation \(\langle a, b \mid a^2 = b^3 = (ab)^7 = 1 \rangle\).
- **Method B**: Compute the degree of the quotient map \(\mathcal{K} \to \mathcal{K}/G\) for each subgroup \(G \leq \mathrm{PSL}(2,7)\) and use the Riemann–Hurwitz formula.

Both methods yield the interval \([168, 168]\), which is a **point interval**—a proof that the order is exactly 168.

## Certified Eigenvalue Enclosures

For the Dirac operator eigenvalues, the enhanced verification computes **validated enclosures** using a combination of:

1. **Temple–Lehmann–Goerisch method**: Provides lower bounds for eigenvalues using a posteriori error estimates from the Rayleigh–Ritz method.
2. **Lehmann–Goerisch bounds**: Gives upper bounds via complementary variational principles.
3. **Homotopy method**: Deforms the Dirac operator to a solvable reference operator and tracks eigenvalue trajectories with interval enclosures.

The result is a set of intervals \([\lambda_n^-, \lambda_n^+]\) such that

\[
\lambda_n \in [\lambda_n^-, \lambda_n^+] \qquad \text{with} \qquad \lambda_n^+ - \lambda_n^- < 10^{-p},
\]

where \(p\) is the working precision.

## Cross-Module Consistency

The enhanced verification checks that results from different modules are **mutually consistent**. For example:

| Check | Module A | Module B | Consistency Condition |
|-------|----------|----------|----------------------|
| Spinor phases ↔ Dirac eigenvalues | `spinor_phases` | `dirac_operator` | \(\delta_k = \arctan(\lambda_k / \mu_k)\) |
| Choptuik formula ↔ Dirac spectrum | `choptyuk_formula` | `dirac_operator` | \(\gamma = \frac{1}{2} + \frac{1}{4\pi}\arctan\!\left(\frac{\sqrt{7}}{3}\right)\) |
| K3 lattice ↔ Klein curve | `surfaces` | `klein_curve` | Pullback of intersection form matches |
| QNM corrections ↔ Spinor phases | `qnm` | `spinor_phases` | Frequency shifts match phase coupling |

Each consistency check is performed using interval arithmetic so that agreement is certified rather than merely observed.

## Verification Hierarchy

The enhanced verification system operates at three levels:

### Level 1 — Algebraic Checks
Purely algebraic verifications that can be performed exactly (e.g., group order, polynomial identities). These are **unconditionally rigorous**.

### Level 2 — Interval-Arithmetic Checks
Numerical computations with validated error bounds. These are rigorous **assuming correct implementation** of the interval arithmetic library.

### Level 3 — Cross-Module Checks
Consistency checks between independent implementations. These provide **strong circumstantial evidence** but are not formal proofs, since both implementations could share a common error.

!!! tip "Running Enhanced Verification"
    ```bash
    python -m choptuik_ac_bc.verify_enhanced --precision 50 --parallel 4
    ```
    At precision 50 with 4 parallel workers, the full enhanced suite typically completes in 2–5 minutes.

!!! warning "Formal Proof Status"
    As of v2.0.0, the enhanced verification provides Level 1 and Level 2 proofs for all core quantities (automorphism group, spinor-phase closure, spectral gap). A complete formal proof of the Choptuik formula (i.e., that the critical exponent of scalar field collapse equals the algebraic-geometric expression) remains an open problem. The enhanced verification certifies agreement to 200+ digits, which constitutes extremely strong numerical evidence but not a mathematical proof.
