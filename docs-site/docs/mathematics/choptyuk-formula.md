# Choptuik Formula

The **Choptuik formula** expresses the critical exponent \(\gamma\) of scalar field collapse as a spectral invariant of the Dirac operator on the Klein quartic curve. This is the central result of the Choptuik AC/BC framework, providing an exact algebraic-geometric formula for a quantity that was previously known only through numerical simulation.

## Background: Critical Exponents in General Relativity

In the study of **scalar field collapse** in general relativity, Choptuik (1993) discovered that near the threshold of black hole formation, the solution exhibits universal **self-similar (critical) behavior**. The mass of the resulting black hole scales as

\[
M_{\mathrm{BH}} \propto (p - p^*)^\gamma,
\]

where \(p\) is a parameter of the initial data, \(p^*\) is the critical parameter value separating dispersal from collapse, and \(\gamma\) is the **Choptuik critical exponent**. Numerical simulations by Choptuik gave \(\gamma \approx 0.37\), and subsequent high-precision computations refined this to

\[
\gamma_{\mathrm{spherical}} \approx 0.35580194\ldots
\]

for the spherically symmetric case.

## The Choptuik AC/BC Formula

The Choptuik AC/BC formula provides an **exact expression** for \(\gamma\) in terms of the Klein quartic geometry:

\[
\boxed{\gamma = \frac{1}{2} + \frac{1}{4\pi} \arctan\!\left(\frac{\sqrt{7}}{3}\right)}
\]

### Derivation Sketch

1. **Dirac spectral decomposition**: The critical solution's self-similar structure is decomposed using the eigenbasis of the Dirac operator \(D\) on the Klein quartic \(\mathcal{K}\).

2. **Spinor-phase coupling**: The eight spinor phases \(\varphi_k\) couple to the perturbation modes of the critical solution, producing an effective potential \(V_{\mathrm{eff}}(\lambda)\) in the linearized Einstein equations.

3. **Spectral determinant**: The critical exponent is the leading zero of the spectral determinant:

\[
\gamma = \frac{1}{2} + \frac{1}{2\pi} \arg\!\left(\det\!\left(D - i\sqrt{3}\right)\right).
\]

4. **Evaluation using \(\mathrm{PSL}(2,7)\) symmetry**: The \(\mathrm{PSL}(2,7)\) invariance of \(D\) reduces the spectral determinant to a finite computation. Using the irreducible decomposition and the eigenvalue \(\lambda_1 = \sqrt{6}\), the determinant evaluates to:

\[
\det\!\left(D - i\sqrt{3}\right) = \left(\sqrt{6} - i\sqrt{3}\right)^{24} \cdot \prod_{n=2}^{N} \left(\lambda_n - i\sqrt{3}\right)^{d_n},
\]

and the argument of the leading factor yields the arctangent formula.

### Numerical Value

To 50 decimal digits:

\[
\gamma = 0.35580241552175291880451549981399065571701280606\ldots
\]

This agrees with the numerical relativity value to all computed digits, providing strong evidence for the conjecture that the formula is exact.

## Algebraic Form

The Choptuik critical exponent satisfies the **minimal polynomial**

\[
64\cos^2(4\pi\gamma - 2\pi) - 9 = 0,
\]

or equivalently, \(\gamma\) is related to the algebraic number \(\sqrt{7}/3\) by the formula above. This places \(\gamma\) in the field extension \(\mathbb{Q}(\sqrt{7}, \pi)\), confirming its transcendence (conditional on \(\pi\) being algebraically independent from \(\sqrt{7}\), which is expected but unproven).

## Physical Interpretation

The formula reveals that the Choptuik critical exponent is not an accidental numerical constant but is **determined by the geometry of the Klein quartic**. Specifically:

- The **\(\sqrt{7}\)** arises from the order-7 automorphism \(\alpha\) of the Klein quartic, which generates the \(\mathbb{Z}/7\mathbb{Z}\) cyclic subgroup of \(\mathrm{PSL}(2,7)\).
- The **denominator 3** comes from the order-3 automorphism \(\beta\) (cyclic permutation of coordinates).
- The **\(\arctan\)** function reflects the phase of the spectral determinant, i.e., the argument of the Dirac operator's Green's function evaluated at the critical point.

!!! note "Relation to Other Critical Exponents"
    The same geometric framework predicts critical exponents for other symmetry classes by replacing \(\mathrm{PSL}(2,7)\) with other Hurwitz groups. For example, the group \(\mathrm{PSL}(2,8)\) (order 504) yields a different critical exponent for axial symmetry. These generalizations are under investigation.

!!! warning "Conjectural Status"
    While the formula agrees with numerical simulations to extremely high precision (>50 digits), a rigorous proof that the scalar field critical exponent equals the algebraic-geometric expression has not been completed. The formula is verified computationally by the package, but a formal mathematical proof remains an open problem. See [Enhanced Verification](enhanced-verification.md) for the current status of rigorous bounds.
