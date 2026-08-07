package com.choptyuk.model;

import lombok.Builder;
import lombok.Value;
import java.util.Map;

/**
 * Implements the Choptyuk formula for spinor corrections on the Klein quartic.
 *
 * The Choptyuk formula computes the eigenvalue correction Delta from the
 * Dirac operator with spinor structure:
 *
 * <b>b-C correction (second order):</b>
 *   Delta_bC = lambda_D^2_triv + delta_C^2 / 2 = 3.338 + (pi/7)^2/2 = 3.438710
 *
 * <b>a-C correction (fifth order):</b>
 *   delta_eff = delta_C^5 / 22 = (pi/7)^5 / 22 ~ 0.000828
 *
 * <b>Choptyuk base formula:</b>
 *   Delta_Ch = lambda_D^2_triv + delta_C^2/2 - delta_C^5/22 = 3.437883
 *
 * <b>With higher orders:</b>
 *   Delta_Ch^+ = Delta_Ch + delta_C^4/8 + delta_C^6/2 = 3.447040
 *
 * <b>b_Ch constant:</b>
 *   b_Ch = 1 - cos(2*pi/7) = 0.376510
 *
 * <b>Observed value (LIGO):</b>
 *   Delta_obs = 3.443
 */
@Value
@Builder
public class ChoptyukFormula {

    /** Dirac squared eigenvalue for trivial spinor: 3.338 */
    double lambdaD2Trivial;

    /** Spinor phase delta_C = pi/7 */
    double deltaC;

    /** b-C correction: lambda_D^2_triv + delta_C^2/2 = 3.438710 */
    double deltaBC;

    /** a-C effective phase: delta_C^5/22 ~ 0.000828 */
    double deltaEffAC;

    /** Choptyuk base: lambda_D^2_triv + delta_C^2/2 - delta_C^5/22 = 3.437883 */
    double deltaChBase;

    /** Choptyuk with higher orders: + delta_C^4/8 + delta_C^6/2 = 3.447040 */
    double deltaChHigher;

    /** b_Ch constant: 1 - cos(2*pi/7) = 0.376510 */
    double bCh;

    /** Observed Delta from LIGO data */
    double deltaObserved;

    /** Deviation from observed */
    double deviationBase;

    /** Deviation of higher-order from observed */
    double deviationHigher;

    /** All computed values as a map */
    Map<String, Double> allValues;

    /**
     * Factory method creating the canonical Choptyuk formula with standard parameters.
     */
    public static ChoptyukFormula canonical() {
        return of(3.338, Math.PI / 7.0, 3.443);
    }

    /**
     * Creates a Choptyuk formula with custom parameters.
     *
     * @param lambdaD2Triv Dirac squared trivial eigenvalue
     * @param deltaC spinor phase delta_C
     * @param deltaObserved observed Delta value
     */
    public static ChoptyukFormula of(double lambdaD2Triv, double deltaC, double deltaObserved) {
        // b-C correction (second order)
        double deltaBC = lambdaD2Triv + Math.pow(deltaC, 2) / 2.0;

        // a-C effective phase (fifth order)
        double deltaEffAC = Math.pow(deltaC, 5) / 22.0;

        // Choptyuk base formula
        double deltaChBase = lambdaD2Triv + Math.pow(deltaC, 2) / 2.0 - Math.pow(deltaC, 5) / 22.0;

        // Choptyuk with higher-order corrections
        double deltaChHigher = deltaChBase + Math.pow(deltaC, 4) / 8.0 + Math.pow(deltaC, 6) / 2.0;

        // b_Ch constant
        double bCh = 1.0 - Math.cos(2.0 * Math.PI / 7.0);

        // Deviations from observed
        double devBase = deltaChBase - deltaObserved;
        double devHigher = deltaChHigher - deltaObserved;

        Map<String, Double> allValues = Map.ofEntries(
                Map.entry("lambdaD2Trivial", lambdaD2Triv),
                Map.entry("deltaC", deltaC),
                Map.entry("deltaC_squared", Math.pow(deltaC, 2)),
                Map.entry("deltaC_cubed", Math.pow(deltaC, 3)),
                Map.entry("deltaC_fourth", Math.pow(deltaC, 4)),
                Map.entry("deltaC_fifth", Math.pow(deltaC, 5)),
                Map.entry("deltaC_sixth", Math.pow(deltaC, 6)),
                Map.entry("secondOrderCorrection", Math.pow(deltaC, 2) / 2.0),
                Map.entry("fourthOrderCorrection", Math.pow(deltaC, 4) / 8.0),
                Map.entry("fifthOrderCorrection", Math.pow(deltaC, 5) / 22.0),
                Map.entry("sixthOrderCorrection", Math.pow(deltaC, 6) / 2.0),
                Map.entry("deltaBC", deltaBC),
                Map.entry("deltaEffAC", deltaEffAC),
                Map.entry("deltaChBase", deltaChBase),
                Map.entry("deltaChHigher", deltaChHigher),
                Map.entry("bCh", bCh),
                Map.entry("deltaObserved", deltaObserved),
                Map.entry("deviationBase", devBase),
                Map.entry("deviationHigher", devHigher),
                Map.entry("relativeDeviationBase", devBase / deltaObserved),
                Map.entry("relativeDeviationHigher", devHigher / deltaObserved)
        );

        return ChoptyukFormula.builder()
                .lambdaD2Trivial(lambdaD2Triv)
                .deltaC(deltaC)
                .deltaBC(deltaBC)
                .deltaEffAC(deltaEffAC)
                .deltaChBase(deltaChBase)
                .deltaChHigher(deltaChHigher)
                .bCh(bCh)
                .deltaObserved(deltaObserved)
                .deviationBase(devBase)
                .deviationHigher(devHigher)
                .allValues(allValues)
                .build();
    }

    /**
     * Evaluates the Choptyuk formula to a given order.
     *
     * @param order maximum order of delta_C corrections to include
     * @return the eigenvalue correction up to the specified order
     */
    public double evaluateToOrder(int order) {
        double result = lambdaD2Trivial;
        if (order >= 2) result += Math.pow(deltaC, 2) / 2.0;
        if (order >= 4) result += Math.pow(deltaC, 4) / 8.0;
        if (order >= 5) result -= Math.pow(deltaC, 5) / 22.0;
        if (order >= 6) result += Math.pow(deltaC, 6) / 2.0;
        return result;
    }

    /**
     * Computes the partial derivative d(Delta_Ch)/d(delta_C).
     */
    public double partialDeltaC() {
        return deltaC - 5.0 * Math.pow(deltaC, 4) / 22.0;
    }

    /**
     * Computes the sensitivity of Delta_Ch to changes in lambda_D^2_triv.
     */
    public double sensitivityLambdaD2() {
        return 1.0;  // Delta_Ch is linear in lambda_D^2_triv
    }

    /**
     * Computes the relative error |Delta_Ch - Delta_obs| / Delta_obs.
     */
    public double relativeErrorBase() {
        return Math.abs(deviationBase) / deltaObserved;
    }

    /**
     * Computes the relative error for the higher-order formula.
     */
    public double relativeErrorHigher() {
        return Math.abs(deviationHigher) / deltaObserved;
    }
}
