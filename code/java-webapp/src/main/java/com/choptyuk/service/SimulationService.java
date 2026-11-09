package com.choptyuk.service;

import com.choptyuk.model.ChoptyukFormula;
import com.choptyuk.model.HypothesisConfig;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.*;

/**
 * Provides simulation capabilities for the Choptyuk framework:
 * parameter sweeps, convergence analysis, and sensitivity studies.
 */
@Service
@Slf4j
public class SimulationService {

    /**
     * Result of a parameter sweep simulation.
     */
    public record SweepResult(
            String parameterName,
            double minValue,
            double maxValue,
            int numPoints,
            List<Double> parameterValues,
            List<Double> deltaChValues,
            List<Double> deviations,
            double optimalValue,
            double optimalDeltaCh,
            double minDeviation
    ) {}

    /**
     * Convergence analysis result.
     */
    public record ConvergenceResult(
            List<Integer> orders,
            List<Double> deltaValues,
            List<Double> differences,
            boolean converged,
            double convergenceRate,
            double limitEstimate
    ) {}

    /**
     * Sensitivity analysis result.
     */
    public record SensitivityResult(
            Map<String, Double> sensitivities,
            Map<String, Double> relativeSensitivities,
            String mostSensitiveParameter,
            double maxSensitivity
    ) {}

    /**
     * Full simulation result.
     */
    public record SimulationResult(
            Instant timestamp,
            SweepResult deltaCSweep,
            SweepResult lambda1Sweep,
            SweepResult curvatureSweep,
            ConvergenceResult convergence,
            SensitivityResult sensitivity,
            Map<String, Object> metadata
    ) {}

    private static final int DEFAULT_SWEEP_POINTS = 100;

    /**
     * Runs a complete simulation with default parameters.
     */
    public SimulationResult simulate() {
        return simulate(0.5, 1.5, 3.0, 5.0, -4.0, 0.0, DEFAULT_SWEEP_POINTS, 8);
    }

    /**
     * Runs a complete simulation with custom ranges.
     */
    public SimulationResult simulate(double deltaCMin, double deltaCMax,
                                      double lambda1Min, double lambda1Max,
                                      double curvatureMin, double curvatureMax,
                                      int numPoints, int maxOrder) {
        log.info("Running simulation: {} points, max order {}", numPoints, maxOrder);

        SweepResult deltaCSweep = sweepDeltaC(deltaCMin, deltaCMax, numPoints);
        SweepResult lambda1Sweep = sweepLambda1(lambda1Min, lambda1Max, numPoints);
        SweepResult curvatureSweep = sweepCurvature(curvatureMin, curvatureMax, numPoints);
        ConvergenceResult convergence = analyzeConvergence(maxOrder);
        SensitivityResult sensitivity = analyzeSensitivity();

        Map<String, Object> metadata = new LinkedHashMap<>();
        metadata.put("numPoints", numPoints);
        metadata.put("maxOrder", maxOrder);
        metadata.put("deltaCRange", List.of(deltaCMin, deltaCMax));
        metadata.put("lambda1Range", List.of(lambda1Min, lambda1Max));
        metadata.put("curvatureRange", List.of(curvatureMin, curvatureMax));

        return new SimulationResult(
                Instant.now(),
                deltaCSweep, lambda1Sweep, curvatureSweep,
                convergence, sensitivity, metadata
        );
    }

    /**
     * Sweeps delta_C from min to max and computes Delta_Ch for each value.
     */
    public SweepResult sweepDeltaC(double min, double max, int numPoints) {
        List<Double> paramValues = new ArrayList<>(numPoints);
        List<Double> deltaChValues = new ArrayList<>(numPoints);
        List<Double> deviations = new ArrayList<>(numPoints);

        double step = (max - min) / (numPoints - 1);
        double minDev = Double.MAX_VALUE;
        double optVal = min;
        double optDelta = 0;

        for (int i = 0; i < numPoints; i++) {
            double dC = min + i * step;
            ChoptyukFormula f = ChoptyukFormula.of(3.338, dC, 3.443);
            double deltaCh = f.getDeltaChBase();
            double dev = Math.abs(deltaCh - 3.443);

            paramValues.add(dC);
            deltaChValues.add(deltaCh);
            deviations.add(dev);

            if (dev < minDev) {
                minDev = dev;
                optVal = dC;
                optDelta = deltaCh;
            }
        }

        return new SweepResult("delta_C", min, max, numPoints,
                paramValues, deltaChValues, deviations, optVal, optDelta, minDev);
    }

    /**
     * Sweeps lambda_1 from min to max.
     */
    public SweepResult sweepLambda1(double min, double max, int numPoints) {
        List<Double> paramValues = new ArrayList<>(numPoints);
        List<Double> deltaChValues = new ArrayList<>(numPoints);
        List<Double> deviations = new ArrayList<>(numPoints);

        double step = (max - min) / (numPoints - 1);
        double minDev = Double.MAX_VALUE;
        double optVal = min;
        double optDelta = 0;
        double dC = Math.PI / 7.0;

        for (int i = 0; i < numPoints; i++) {
            double l1 = min + i * step;
            double lambdaD2 = l1 + (-2.0) / 4.0;
            ChoptyukFormula f = ChoptyukFormula.of(lambdaD2, dC, 3.443);
            double deltaCh = f.getDeltaChBase();
            double dev = Math.abs(deltaCh - 3.443);

            paramValues.add(l1);
            deltaChValues.add(deltaCh);
            deviations.add(dev);

            if (dev < minDev) {
                minDev = dev;
                optVal = l1;
                optDelta = deltaCh;
            }
        }

        return new SweepResult("lambda_1", min, max, numPoints,
                paramValues, deltaChValues, deviations, optVal, optDelta, minDev);
    }

    /**
     * Sweeps scalar curvature from min to max.
     */
    public SweepResult sweepCurvature(double min, double max, int numPoints) {
        List<Double> paramValues = new ArrayList<>(numPoints);
        List<Double> deltaChValues = new ArrayList<>(numPoints);
        List<Double> deviations = new ArrayList<>(numPoints);

        double step = (max - min) / (numPoints - 1);
        double minDev = Double.MAX_VALUE;
        double optVal = min;
        double optDelta = 0;
        double dC = Math.PI / 7.0;

        for (int i = 0; i < numPoints; i++) {
            double R = min + i * step;
            double lambdaD2 = 3.838 + R / 4.0;
            ChoptyukFormula f = ChoptyukFormula.of(lambdaD2, dC, 3.443);
            double deltaCh = f.getDeltaChBase();
            double dev = Math.abs(deltaCh - 3.443);

            paramValues.add(R);
            deltaChValues.add(deltaCh);
            deviations.add(dev);

            if (dev < minDev) {
                minDev = dev;
                optVal = R;
                optDelta = deltaCh;
            }
        }

        return new SweepResult("scalarCurvature", min, max, numPoints,
                paramValues, deltaChValues, deviations, optVal, optDelta, minDev);
    }

    /**
     * Analyzes the convergence of the Choptyuk formula as order increases.
     */
    public ConvergenceResult analyzeConvergence(int maxOrder) {
        List<Integer> orders = new ArrayList<>();
        List<Double> deltaValues = new ArrayList<>();
        List<Double> differences = new ArrayList<>();

        ChoptyukFormula formula = ChoptyukFormula.canonical();
        double prev = formula.evaluateToOrder(0);

        for (int n = 1; n <= maxOrder; n++) {
            double current = formula.evaluateToOrder(n);
            orders.add(n);
            deltaValues.add(current);
            differences.add(Math.abs(current - prev));
            prev = current;
        }

        // Estimate convergence rate from last differences
        double rate = 0;
        if (differences.size() >= 2) {
            double d1 = differences.get(differences.size() - 2);
            double d2 = differences.get(differences.size() - 1);
            if (d1 > 1e-15) {
                rate = d2 / d1;
            }
        }

        boolean converged = differences.stream()
                .skip(Math.max(0, differences.size() - 3))
                .allMatch(d -> d < 1e-6);

        return new ConvergenceResult(orders, deltaValues, differences,
                converged, rate, prev);
    }

    /**
     * Performs sensitivity analysis for all parameters.
     */
    public SensitivityResult analyzeSensitivity() {
        double eps = 1e-6;
        ChoptyukFormula base = ChoptyukFormula.canonical();
        double baseVal = base.getDeltaChBase();

        Map<String, Double> sensitivities = new LinkedHashMap<>();
        Map<String, Double> relativeSensitivities = new LinkedHashMap<>();

        // Sensitivity to lambda_D^2_trivial
        ChoptyukFormula fLam = ChoptyukFormula.of(base.getLambdaD2Trivial() + eps, base.getDeltaC(), base.getDeltaObserved());
        double sLam = (fLam.getDeltaChBase() - baseVal) / eps;
        sensitivities.put("lambdaD2Trivial", sLam);
        relativeSensitivities.put("lambdaD2Trivial", Math.abs(sLam * base.getLambdaD2Trivial() / baseVal));

        // Sensitivity to delta_C
        ChoptyukFormula fDC = ChoptyukFormula.of(base.getLambdaD2Trivial(), base.getDeltaC() + eps, base.getDeltaObserved());
        double sDC = (fDC.getDeltaChBase() - baseVal) / eps;
        sensitivities.put("deltaC", sDC);
        relativeSensitivities.put("deltaC", Math.abs(sDC * base.getDeltaC() / baseVal));

        // Sensitivity to delta_observed (trivial: deviation = Delta_Ch - delta_obs)
        sensitivities.put("deltaObserved", -1.0);
        relativeSensitivities.put("deltaObserved", base.getDeltaObserved() / baseVal);

        String mostSensitive = relativeSensitivities.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse("unknown");
        double maxSens = relativeSensitivities.getOrDefault(mostSensitive, 0.0);

        return new SensitivityResult(sensitivities, relativeSensitivities, mostSensitive, maxSens);
    }
}
