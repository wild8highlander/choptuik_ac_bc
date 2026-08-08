# Dirac Operator

The **Dirac operator** on the Klein quartic curve is the central analytical object that links the curve's geometry to the Choptuik critical exponent and the spinor-phase corrections. Its spectral properties determine the correction terms \(\delta_k\) in the spinor phases and appear directly in the critical exponent formula.

## Construction

Let \(\Sigma = \mathcal{K}\) be the Klein quartic equipped with its unique Poincaré-type metric \(g\) compatible with the \(\mathrm{PSL}(2,7)\) symmetry. The canonical bundle \(K_\Sigma\) provides a spin structure via the identification

\[
S = K_\Sigma^{1/2} \oplus K_\Sigma^{-1/2},
\]

where \(S\) is the spinor bundle of rank 2. The **Dirac operator** is the first-order elliptic operator

\[
D : \Gamma(S) \to \Gamma(S), \qquad D = \begin{pmatrix} 0 & \bar{\partial}^* \\ \bar{\partial} & 0 \end{pmatrix},
\]

where \(\bar{\partial} : \Gamma(K_\Sigma^{1/2}) \to \Gamma(K_\Sigma^{1/2} \otimes \bar{K}_\Sigma)\) is the Dolbeault operator and \(\bar{\partial}^*\) is its formal adjoint.

## Spectral Theory

The Dirac operator \(D\) is formally self-adjoint and has discrete real spectrum \(\{\lambda_n\}_{n \in \mathbb{Z}}\) with \(\lambda_n \to \pm\infty\) as \(|n| \to \infty\). The key spectral quantities are:

### Kernel

The **index theorem** for the Dirac operator on a genus-\(g\) curve gives

\[
\mathrm{index}(D) = \int_\Sigma \hat{A}(\Sigma) \, \mathrm{ch}(S) = 0,
\]

since \(\hat{A}\) is trivial in dimension 2. Combined with the self-adjointness, this implies

\[
\ker(D) = 0.
\]

The Dirac operator on the Klein quartic has **trivial kernel**—there are no harmonic spinors. ✓

### Spectral Gap

The **spectral gap** is the smallest positive eigenvalue:

\[
\lambda_1 = \min\{\lambda > 0 : \lambda \in \mathrm{spec}(D)\}.
\]

For the Klein quartic, the spectral gap is determined by the geometry:

\[
\lambda_1 = \sqrt{6} \approx 2.4494897\ldots
\]

This value is related to the first non-trivial eigenvalue of the Laplace–Beltrami operator \(\Delta\) on \(\Sigma\) via the Lichnerowicz formula \(D^2 = \Delta + \kappa/4\), where \(\kappa\) is the scalar curvature.

### Eigenvalue Asymptotics

The eigenvalues of \(D\) satisfy the **Weyl asymptotic law**:

\[
N(\lambda) \sim \frac{\mathrm{Area}(\Sigma)}{4\pi} \lambda^2, \qquad \lambda \to \infty,
\]

where \(N(\lambda) = \#\{n : |\lambda_n| \leq \lambda\}\) is the eigenvalue counting function.

## Connection to the Choptuik Formula

The Choptuik critical exponent \(\gamma\) is expressed as a spectral invariant of the Dirac operator:

\[
\gamma = \frac{1}{2} + \frac{1}{4\pi} \arctan\!\left(\frac{\lambda_1^2 - 3}{2\lambda_1}\right).
\]

Substituting \(\lambda_1 = \sqrt{6}\) yields the closed-form expression given in the [Choptuik Formula](choptyuk-formula.md) page. This formula is the central result of the Choptuik AC/BC framework, connecting the spectral geometry of the Klein quartic to the scaling behavior of scalar field collapse.

## Group Action on the Spectrum

The automorphism group \(\mathrm{PSL}(2,7)\) acts on the eigenspaces of \(D\) by unitary transformations, decomposing the spectrum into **irreducible representations**. The eigenspace for \(\lambda_n\) carries an irreducible representation of dimension:

\[
d_n = \begin{cases} 1 & \text{if } n \equiv 0 \pmod{7}, \\ 6 & \text{if } n \not\equiv 0 \pmod{7}. \end{cases}
\]

This 1-6 splitting reflects the two irreducible representations of \(\mathrm{PSL}(2,7)\) that appear in the spinor representation.

!!! warning "Numerical Computation"
    The Dirac operator is discretized using a spectral method based on the automorphism-invariant basis of \(L^2(\Sigma)\). The computed eigenvalues converge exponentially fast with the truncation order, but care must be taken to avoid spectral pollution (spurious eigenvalues) when using finite-dimensional approximations. The package uses a validated enclosure method to guarantee that reported eigenvalues are correct to the stated precision.

!!! example "Computing the Spectrum"
    ```python
    from choptuik_ac_bc.dirac_operator import compute_spectrum

    eigenvalues = compute_spectrum(n_modes=20, precision=50)
    print(f"λ_1 = {eigenvalues[0]}")   # First positive eigenvalue
    print(f"λ_1 / √6 = {eigenvalues[0] / 6**0.5}")  # Should be ≈ 1.0
    ```
    See the [Dirac Operator API](../api/dirac-operator.md) for full documentation.
