package com.choptyuk.model;

import lombok.Builder;
import lombok.Value;
import java.util.Map;

/**
 * Configuration for custom hypothesis testing.
 *
 * Allows the user to specify alternative values for any parameter in the
 * Choptyuk formula and test whether the resulting predictions agree with
 * observations better or worse than the canonical hypothesis.
 */
@Value
@Builder
public class HypothesisConfig {

    /** Name/label for this hypothesis */
    String name;

    /** Custom delta_A phase (canonical: pi/2) */
    double deltaA;

    /** Custom delta_B phase (canonical: pi/3) */
    double deltaB;

    /** Custom delta_C phase (canonical: pi/7) */
    double deltaC;

    /** Custom lambda_1 eigenvalue (canonical: 3.838) */
    double lambda1;

    /** Custom scalar curvature R (canonical: -2) */
    double scalarCurvature;

    /** Custom genus (canonical: 3) */
    int genus;

    /** Custom PSL(2,7) order (canonical: 168) */
    int pslOrder;

    /** Custom observed Delta value (canonical: 3.443) */
    double deltaObserved;

    /** Maximum correction order to include */
    int maxOrder;

    /** Additional custom parameters */
    Map<String, Double> customParameters;

    /**
     * Creates the canonical (default) hypothesis.
     */
    public static HypothesisConfig canonical() {
        return HypothesisConfig.builder()
                .name("Canonical Choptyuk")
                .deltaA(Math.PI / 2.0)
                .deltaB(Math.PI / 3.0)
                .deltaC(Math.PI / 7.0)
                .lambda1(3.838)
                .scalarCurvature(-2.0)
                .genus(3)
                .pslOrder(168)
                .deltaObserved(3.443)
                .maxOrder(6)
                .customParameters(Map.of())
                .build();
    }

    /**
     * Creates a perturbed hypothesis by modifying one parameter.
     *
     * @param paramName the parameter to perturb
     * @param perturbation the relative perturbation factor (e.g., 0.01 for 1%)
     * @return the perturbed hypothesis
     */
    public HypothesisConfig perturb(String paramName, double perturbation) {
        switch (paramName) {
            case "deltaA":
                return HypothesisConfig.builder().name(name + " + dA*" + perturbation)
                        .deltaA(deltaA * (1 + perturbation)).deltaB(deltaB).deltaC(deltaC)
                        .lambda1(lambda1).scalarCurvature(scalarCurvature).genus(genus)
                        .pslOrder(pslOrder).deltaObserved(deltaObserved).maxOrder(maxOrder)
                        .customParameters(customParameters).build();
            case "deltaB":
                return HypothesisConfig.builder().name(name + " + dB*" + perturbation)
                        .deltaA(deltaA).deltaB(deltaB * (1 + perturbation)).deltaC(deltaC)
                        .lambda1(lambda1).scalarCurvature(scalarCurvature).genus(genus)
                        .pslOrder(pslOrder).deltaObserved(deltaObserved).maxOrder(maxOrder)
                        .customParameters(customParameters).build();
            case "deltaC":
                return HypothesisConfig.builder().name(name + " + dC*" + perturbation)
                        .deltaA(deltaA).deltaB(deltaB).deltaC(deltaC * (1 + perturbation))
                        .lambda1(lambda1).scalarCurvature(scalarCurvature).genus(genus)
                        .pslOrder(pslOrder).deltaObserved(deltaObserved).maxOrder(maxOrder)
                        .customParameters(customParameters).build();
            case "lambda1":
                return HypothesisConfig.builder().name(name + " + l1*" + perturbation)
                        .deltaA(deltaA).deltaB(deltaB).deltaC(deltaC)
                        .lambda1(lambda1 * (1 + perturbation)).scalarCurvature(scalarCurvature).genus(genus)
                        .pslOrder(pslOrder).deltaObserved(deltaObserved).maxOrder(maxOrder)
                        .customParameters(customParameters).build();
            case "scalarCurvature":
                return HypothesisConfig.builder().name(name + " + R*" + perturbation)
                        .deltaA(deltaA).deltaB(deltaB).deltaC(deltaC)
                        .lambda1(lambda1).scalarCurvature(scalarCurvature * (1 + perturbation)).genus(genus)
                        .pslOrder(pslOrder).deltaObserved(deltaObserved).maxOrder(maxOrder)
                        .customParameters(customParameters).build();
            default:
                return this;
        }
    }

    /**
     * Evaluates the Choptyuk formula for this hypothesis configuration.
     */
    public double evaluateChoptyuk() {
        double lambdaD2Triv = lambda1 + scalarCurvature / 4.0;
        double result = lambdaD2Triv;

        if (maxOrder >= 2) result += Math.pow(deltaC, 2) / 2.0;
        if (maxOrder >= 4) result += Math.pow(deltaC, 4) / 8.0;
        if (maxOrder >= 5) result -= Math.pow(deltaC, 5) / 22.0;
        if (maxOrder >= 6) result += Math.pow(deltaC, 6) / 2.0;

        return result;
    }

    /**
     * Computes the deviation from the observed value.
     */
    public double deviation() {
        return evaluateChoptyuk() - deltaObserved;
    }

    /**
     * Computes the relative deviation.
     */
    public double relativeDeviation() {
        return Math.abs(deviation()) / deltaObserved;
    }
}
