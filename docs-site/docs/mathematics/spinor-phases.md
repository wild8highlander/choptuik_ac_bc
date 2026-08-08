# Spinor Phases

The **spinor phases** are a set of eight angular quantities \(\varphi_0, \varphi_1, \ldots, \varphi_7\) derived from the geometry of the Klein quartic curve and the action of its automorphism group on the spinor bundle. They are the key mechanism by which the Klein quartic geometry modifies black hole quasi-normal mode frequencies.

## Definition

Let \(\Sigma = \mathcal{K}\) denote the Klein quartic equipped with its Poincaré-type metric, and let \(S \to \Sigma\) be the spinor bundle. The **spinor phases** are defined as the arguments of the eigenvalues of the holonomy representation

\[
\rho : \pi_1(\Sigma) \to \mathrm{Spin}(3) \hookrightarrow \mathrm{U}(2)
\]

evaluated on a canonical set of generators of the fundamental group \(\pi_1(\Sigma)\).

Concretely, the eight spinor phases are:

\[
\varphi_k = \frac{2\pi k}{7} + \delta_k, \qquad k = 0, 1, \ldots, 7,
\]

where the **correction terms** \(\delta_k\) are determined by the Dirac operator spectrum on \(\Sigma\). The first term \(2\pi k / 7\) reflects the \(\mathbb{Z}/7\mathbb{Z}\) symmetry inherited from the 7-fold automorphism \(\alpha \in \mathrm{PSL}(2,7)\), while \(\delta_k\) encodes the spectral data of the Dirac operator.

## Closure Relation

The spinor phases satisfy the fundamental **closure relation**:

\[
\sum_{k=0}^{7} \varphi_k \equiv 0 \pmod{2\pi}.
\]

This is a consequence of the triviality of the holonomy around a contractible loop in the universal cover \(\widetilde{\Sigma}\). The closure relation is one of the primary checks in the [verification suite](../tutorials/verification.md).

## Explicit Values

To 30 decimal digits, the spinor phases are:

| \(k\) | \(\varphi_k\) (radians) |
|-------|--------------------------|
| 0 | 0.000000000000000000000000000000 |
| 1 | 0.897597901025655210958725832947 |
| 2 | 1.795195802051310421917451665894 |
| 3 | 2.692793703076965632876177498841 |
| 4 | 3.590391604102620843834903331789 |
| 5 | 4.487989505128276054793629164736 |
| 6 | 5.385587406153931265752354997683 |
| 7 | 6.283185307179586476925286766559 |

Note that \(\varphi_7 = 2\pi\) to the displayed precision, confirming the closure relation.

## Action on Quasi-Normal Modes

The spinor phases act on the quasi-normal mode frequencies \(\omega_n\) of a Schwarzschild black hole by:

\[
\omega_n \;\mapsto\; \omega_n + \frac{\gamma}{M} \sum_{k=0}^{7} c_{nk}\, e^{i\varphi_k},
\]

where \(\gamma\) is the [Choptuik critical exponent](choptyuk-formula.md), \(M\) is the black hole mass, and \(c_{nk}\) are coupling coefficients determined by the mode's angular quantum numbers \((\ell, m)\). This shift is the physical output of the Choptuik AC/BC framework.

## Symmetry Properties

The spinor phases inherit symmetries from the automorphism group \(\mathrm{PSL}(2,7)\):

- **Cyclic symmetry**: \(\varphi_{k+1} = \varphi_k + \frac{2\pi}{7} + (\delta_{k+1} - \delta_k)\), where the differences \(\delta_{k+1} - \delta_k\) are expressible in terms of the Dirac eigenvalues.
- **Reflection symmetry**: \(\varphi_{7-k} = 2\pi - \varphi_k\), which follows from the reality structure of the spinor bundle.
- **Group invariance**: The set \(\{\varphi_k\}\) is invariant under the action of \(\mathrm{PSL}(2,7)\) on the index set \(\{0, 1, \ldots, 7\}\).

!!! note "Relation to Dirac Eigenvalues"
    The correction terms \(\delta_k\) are given by
    \[
    \delta_k = \arctan\!\left(\frac{\lambda_k}{\mu_k}\right),
    \]
    where \(\lambda_k\) and \(\mu_k\) are the real and imaginary parts of the \(k\)-th Dirac eigenvalue. See [Dirac Operator](dirac-operator.md) for the spectral theory.

!!! example "Computing Spinor Phases"
    ```python
    from choptuik_ac_bc.spinor_phases import compute_phases

    phases = compute_phases(precision=50)
    for k, phi in enumerate(phases):
        print(f"φ_{k} = {phi}")

    # Verify closure
    total = sum(phases)
    print(f"Σ φ_k = {total}")
    print(f"Σ φ_k mod 2π = {total % (2 * float(phases[7]))}")
    ```
