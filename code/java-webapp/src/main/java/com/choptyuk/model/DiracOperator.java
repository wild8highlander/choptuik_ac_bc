package com.choptyuk.model;

import lombok.Builder;
import lombok.Value;
import java.util.List;
import java.util.Map;

/**
 * Represents the Dirac operator on the Klein quartic and computes eigenvalues
 * using the Lichnerowicz formula.
 *
 * The Lichnerowicz formula relates the Dirac operator squared to the
 * Laplacian plus scalar curvature:
 *   D^2 = Delta + (R/4)
 *
 * For the trivial spinor bundle on the Klein quartic:
 *   lambda_D^2_triv = lambda_1 + R/4 = 3.838 + (-2)/4 = 3.838 - 0.5 = 3.338
 *
 * This is the base eigenvalue used in all Choptyuk corrections.
 */
@Value
@Builder
public class DiracOperator {

    /** First positive Laplacian eigenvalue on the Klein quartic */
    double lambda1;

    /** Scalar curvature R = -2 */
    double scalarCurvature;

    /** Dirac squared eigenvalue for the trivial spinor bundle */
    double lambdaD2Trivial;

    /** List of computed eigenvalues */
    List<Double> eigenvalues;

    /** Map of spectral invariants */
    Map<String, Double> spectralInvariants;

    /**
     * Factory method creating the canonical Dirac operator on the Klein quartic.
     */
    public static DiracOperator canonical() {
        double lambda1 = 3.838;
        double R = -2.0;
        double lambdaD2Triv = lambda1 + R / 4.0;

        return DiracOperator.builder()
                .lambda1(lambda1)
                .scalarCurvature(R)
                .lambdaD2Trivial(lambdaD2Triv)
                .eigenvalues(computeEigenvalueSpectrum(lambdaD2Triv))
                .spectralInvariants(Map.of(
                        "lambda1", lambda1,
                        "R", R,
                        "R_over_4", R / 4.0,
                        "lambdaD2Trivial", lambdaD2Triv,
                        "lambdaDTrivial", Math.sqrt(lambdaD2Triv),
                        "etaInvariant", 0.0,  // eta-invariant for trivial spin structure
                        "indexDirac", 0.0      // index of D on Klein quartic
                ))
                .build();
    }

    /**
     * Creates a Dirac operator with custom parameters.
     */
    public static DiracOperator of(double lambda1, double scalarCurvature) {
        double lambdaD2Triv = lambda1 + scalarCurvature / 4.0;
        return DiracOperator.builder()
                .lambda1(lambda1)
                .scalarCurvature(scalarCurvature)
                .lambdaD2Trivial(lambdaD2Triv)
                .eigenvalues(computeEigenvalueSpectrum(lambdaD2Triv))
                .spectralInvariants(Map.of(
                        "lambda1", lambda1,
                        "R", scalarCurvature,
                        "R_over_4", scalarCurvature / 4.0,
                        "lambdaD2Trivial", lambdaD2Triv,
                        "lambdaDTrivial", Math.sqrt(Math.max(0, lambdaD2Triv)),
                        "etaInvariant", 0.0,
                        "indexDirac", 0.0
                ))
                .build();
    }

    /**
     * Computes the Dirac eigenvalue spectrum up to a reasonable cutoff.
     * The eigenvalues are lambda_k = sqrt(lambda_D^2_triv + k * gap)
     * where gap is the Weyl law spacing.
     */
    private static List<Double> computeEigenvalueSpectrum(double lambdaD2Triv) {
        List<Double> spectrum = new java.util.ArrayList<>();
        spectrum.add(0.0);  // zero mode
        spectrum.add(Math.sqrt(Math.max(0, lambdaD2Triv)));

        // Add higher eigenvalues following Weyl law
        double weylGap = lambdaD2Triv / 3.0;  // approximate gap for genus 3
        for (int k = 1; k <= 20; k++) {
            double lambdaK2 = lambdaD2Triv + k * weylGap;
            spectrum.add(Math.sqrt(lambdaK2));
        }
        return spectrum;
    }

    /**
     * Applies the Lichnerowicz formula: D^2 = Delta + R/4.
     *
     * @param laplacianEigenvalue the Laplacian eigenvalue
     * @return the corresponding Dirac squared eigenvalue
     */
    public double lichnerowicz(double laplacianEigenvalue) {
        return laplacianEigenvalue + scalarCurvature / 4.0;
    }

    /**
     * Verifies the Lichnerowicz formula consistency for the trivial spinor.
     *
     * @return true if lambda_D^2_triv = lambda_1 + R/4
     */
    public boolean verifyLichnerowicz() {
        double expected = lambda1 + scalarCurvature / 4.0;
        return Math.abs(lambdaD2Trivial - expected) < 1e-10;
    }

    /**
     * Computes the spectral action Tr(f(D)) for a given test function f.
     * Uses the heat kernel expansion.
     */
    public double spectralAction(double t) {
        // Heat trace: Tr(exp(-t D^2)) ~ (4*pi*t)^(-3) * Area * (1 + t*R/6 + ...)
        double area = 4.0 * Math.PI * 3;  // genus 3
        double a0 = area;
        double a2 = area * scalarCurvature / 6.0;
        double a4 = area * (scalarCurvature * scalarCurvature / 30.0 + 1.0 / 30.0);  // simplified

        double heatTrace = a0 * Math.pow(4.0 * Math.PI * t, -3.0) +
                           a2 * Math.pow(4.0 * Math.PI * t, -2.0) +
                           a4 * Math.pow(4.0 * Math.PI * t, -1.0);
        return heatTrace;
    }
}
