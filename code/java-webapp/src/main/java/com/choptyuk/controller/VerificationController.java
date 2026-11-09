package com.choptyuk.controller;

import com.choptyuk.model.HypothesisConfig;
import com.choptyuk.service.SimulationService;
import com.choptyuk.service.VerificationService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * REST API controller for verification and simulation endpoints.
 *
 * Endpoints:
 *   POST /api/verify           - Run full verification with optional custom parameters
 *   POST /api/simulate         - Run simulation with parameter sweep
 *   POST /api/hypothesis       - Test a custom hypothesis
 */
@RestController
@RequestMapping("/api")
@Slf4j
public class VerificationController {

    private final VerificationService verificationService;
    private final SimulationService simulationService;

    public VerificationController(VerificationService verificationService, SimulationService simulationService) {
        this.verificationService = verificationService;
        this.simulationService = simulationService;
    }

    /**
     * Run full verification with canonical or custom parameters.
     *
     * Request body (optional):
     *   deltaA, deltaB, deltaC, lambda1, scalarCurvature, deltaObserved
     */
    @PostMapping("/verify")
    public ResponseEntity<VerificationService.VerificationResult> verify(
            @RequestBody(required = false) Map<String, Double> params) {

        log.info("POST /api/verify with params: {}", params);

        VerificationService.VerificationResult result;
        if (params != null && !params.isEmpty()) {
            double deltaA = params.getOrDefault("deltaA", Math.PI / 2.0);
            double deltaB = params.getOrDefault("deltaB", Math.PI / 3.0);
            double deltaC = params.getOrDefault("deltaC", Math.PI / 7.0);
            double lambda1 = params.getOrDefault("lambda1", 3.838);
            double R = params.getOrDefault("scalarCurvature", -2.0);
            double deltaObs = params.getOrDefault("deltaObserved", 3.443);
            result = verificationService.verifyAll(deltaA, deltaB, deltaC, lambda1, R, deltaObs);
        } else {
            result = verificationService.verifyAll();
        }

        return ResponseEntity.ok(result);
    }

    /**
     * Run simulation with parameter sweep configuration.
     *
     * Request body (optional):
     *   deltaCMin, deltaCMax, lambda1Min, lambda1Max,
     *   curvatureMin, curvatureMax, numPoints, maxOrder
     */
    @PostMapping("/simulate")
    public ResponseEntity<SimulationService.SimulationResult> simulate(
            @RequestBody(required = false) Map<String, Object> params) {

        log.info("POST /api/simulate with params: {}", params);

        double dCMin = getDouble(params, "deltaCMin", 0.5);
        double dCMax = getDouble(params, "deltaCMax", 1.5);
        double l1Min = getDouble(params, "lambda1Min", 3.0);
        double l1Max = getDouble(params, "lambda1Max", 5.0);
        double rMin = getDouble(params, "curvatureMin", -4.0);
        double rMax = getDouble(params, "curvatureMax", 0.0);
        int numPts = getInt(params, "numPoints", 100);
        int maxOrd = getInt(params, "maxOrder", 8);

        SimulationService.SimulationResult result = simulationService.simulate(
                dCMin, dCMax, l1Min, l1Max, rMin, rMax, numPts, maxOrd);

        return ResponseEntity.ok(result);
    }

    /**
     * Test a custom hypothesis.
     *
     * Request body:
     *   name, deltaA, deltaB, deltaC, lambda1, scalarCurvature, genus, pslOrder, deltaObserved, maxOrder
     */
    @PostMapping("/hypothesis")
    public ResponseEntity<Map<String, Object>> hypothesis(
            @RequestBody Map<String, Object> params) {

        log.info("POST /api/hypothesis with params: {}", params);

        HypothesisConfig config = HypothesisConfig.builder()
                .name(getString(params, "name", "Custom Hypothesis"))
                .deltaA(getDouble(params, "deltaA", Math.PI / 2.0))
                .deltaB(getDouble(params, "deltaB", Math.PI / 3.0))
                .deltaC(getDouble(params, "deltaC", Math.PI / 7.0))
                .lambda1(getDouble(params, "lambda1", 3.838))
                .scalarCurvature(getDouble(params, "scalarCurvature", -2.0))
                .genus(getInt(params, "genus", 3))
                .pslOrder(getInt(params, "pslOrder", 168))
                .deltaObserved(getDouble(params, "deltaObserved", 3.443))
                .maxOrder(getInt(params, "maxOrder", 6))
                .customParameters(Map.of())
                .build();

        Map<String, Object> result = Map.of(
                "hypothesis", config,
                "choptyukValue", config.evaluateChoptyuk(),
                "deviation", config.deviation(),
                "relativeDeviation", config.relativeDeviation(),
                "lambdaD2Trivial", config.getLambda1() + config.getScalarCurvature() / 4.0
        );

        return ResponseEntity.ok(result);
    }

    private double getDouble(Map<String, Object> params, String key, double defaultValue) {
        if (params == null || !params.containsKey(key)) return defaultValue;
        Object val = params.get(key);
        if (val instanceof Number) return ((Number) val).doubleValue();
        return defaultValue;
    }

    private int getInt(Map<String, Object> params, String key, int defaultValue) {
        if (params == null || !params.containsKey(key)) return defaultValue;
        Object val = params.get(key);
        if (val instanceof Number) return ((Number) val).intValue();
        return defaultValue;
    }

    private String getString(Map<String, Object> params, String key, String defaultValue) {
        if (params == null || !params.containsKey(key)) return defaultValue;
        Object val = params.get(key);
        return val != null ? val.toString() : defaultValue;
    }
}
