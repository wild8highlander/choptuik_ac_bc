package com.choptyuk.service;

import com.choptyuk.model.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.*;

/**
 * Orchestrates the full verification of the Choptyuk monograph claims.
 */
@Service
@Slf4j
public class VerificationService {

    public record VerificationCheck(
            String name,
            boolean passed,
            double expected,
            double actual,
            double tolerance,
            String message
    ) {}

    public record VerificationResult(
            Instant timestamp,
            boolean allPassed,
            int totalChecks,
            int passedChecks,
            int failedChecks,
            List<VerificationCheck> checks,
            KleinCurve kleinCurve,
            SpinorPhases spinorPhases,
            DiracOperator diracOperator,
            ChoptyukFormula choptyukFormula,
            List<SurfaceSpec> surfaces,
            List<QNMEvent> qnmEvents,
            Map<String, Object> summary
    ) {}

    private static final double DEFAULT_TOLERANCE = 1e-4;

    public VerificationResult verifyAll() {
        return verifyAll(Math.PI / 2.0, Math.PI / 3.0, Math.PI / 7.0, 3.838, -2.0, 3.443);
    }

    public VerificationResult verifyAll(double deltaA, double deltaB, double deltaC,
                                         double lambda1, double scalarCurvature, double deltaObserved) {
        log.info("Starting full verification with deltaA={}, deltaB={}, deltaC={}, lambda1={}, R={}, deltaObs={}",
                deltaA, deltaB, deltaC, lambda1, scalarCurvature, deltaObserved);

        List<VerificationCheck> checks = new ArrayList<>();

        KleinCurve klein = KleinCurve.canonical();
        checks.addAll(verifyKleinCurve(klein));

        SpinorPhases phases = SpinorPhases.of(deltaA, deltaB, deltaC);
        checks.addAll(verifySpinorPhases(phases));

        DiracOperator dirac = DiracOperator.of(lambda1, scalarCurvature);
        checks.addAll(verifyDiracOperator(dirac));

        ChoptyukFormula formula = ChoptyukFormula.of(dirac.getLambdaD2Trivial(), deltaC, deltaObserved);
        checks.addAll(verifyChoptyukFormula(formula));

        checks.add(verifyBChConstant());

        List<SurfaceSpec> surfaces = List.of(SurfaceSpec.bolza(), SurfaceSpec.bring(), SurfaceSpec.macbeath());
        checks.addAll(verifySurfaces(surfaces));

        List<QNMEvent> qnmEvents = List.of(
                QNMEvent.gw150914(), QNMEvent.gw170104(),
                QNMEvent.gw170814(), QNMEvent.gw190521()
        );
        checks.addAll(verifyQNMPredictions(qnmEvents));

        int passed = (int) checks.stream().filter(VerificationCheck::passed).count();
        int failed = checks.size() - passed;
        boolean allPassed = failed == 0;

        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("allPassed", allPassed);
        summary.put("totalChecks", checks.size());
        summary.put("passedChecks", passed);
        summary.put("failedChecks", failed);
        summary.put("deltaChBase", formula.getDeltaChBase());
        summary.put("deltaChHigher", formula.getDeltaChHigher());
        summary.put("deltaObserved", deltaObserved);
        summary.put("deviationBase", formula.getDeviationBase());
        summary.put("deviationHigher", formula.getDeviationHigher());
        summary.put("relativeErrorBase", formula.relativeErrorBase());
        summary.put("relativeErrorHigher", formula.relativeErrorHigher());

        log.info("Verification complete: {}/{} checks passed", passed, checks.size());

        return new VerificationResult(Instant.now(), allPassed, checks.size(), passed, failed,
                checks, klein, phases, dirac, formula, surfaces, qnmEvents, summary);
    }

    private List<VerificationCheck> verifyKleinCurve(KleinCurve klein) {
        List<VerificationCheck> checks = new ArrayList<>();
        checks.add(makeCheckDouble("Klein genus", 3.0, klein.getGenus(), 0, "Genus must be 3"));
        checks.add(makeCheckDouble("PSL(2,7) order", 168.0, klein.getPslOrder(), 0, "Automorphism group order must be 168"));
        checks.add(makeCheckDouble("Klein lambda_1", 3.838, klein.getLambda1(), DEFAULT_TOLERANCE, "First Laplacian eigenvalue"));
        checks.add(makeCheckDouble("Klein R", -2.0, klein.getScalarCurvature(), DEFAULT_TOLERANCE, "Scalar curvature must be -2"));
        checks.add(makeCheckDouble("Klein area", 4 * Math.PI * 3, klein.getArea(), DEFAULT_TOLERANCE, "Area = 4*pi*genus"));
        checks.add(makeCheckDouble("Klein Euler char", -4.0, klein.getEulerCharacteristic(), 0, "Euler characteristic = 2 - 2g = -4"));
        checks.add(makeCheckBoolean("PSL(2,7) relation", true, klein.verifyPsl27Relation(), "Generators satisfy a^2=b^3=c^7=abc=1"));
        checks.add(makeCheckBoolean("Hurwitz curve", true, klein.isHurwitzCurve(), "Klein curve attains Hurwitz bound 84(g-1)=168"));
        return checks;
    }

    private List<VerificationCheck> verifySpinorPhases(SpinorPhases phases) {
        List<VerificationCheck> checks = new ArrayList<>();
        checks.add(makeCheckDouble("delta_A = pi/2", Math.PI / 2, phases.getDeltaA(), DEFAULT_TOLERANCE, "Spinor phase delta_A"));
        checks.add(makeCheckDouble("delta_B = pi/3", Math.PI / 3, phases.getDeltaB(), DEFAULT_TOLERANCE, "Spinor phase delta_B"));
        checks.add(makeCheckDouble("delta_C = pi/7", Math.PI / 7, phases.getDeltaC(), DEFAULT_TOLERANCE, "Spinor phase delta_C"));
        checks.add(makeCheckDouble("64 spinor structures", 64.0, phases.getNumStructures(), 0, "2^6 = 64 spinor structures"));
        checks.add(makeCheckDouble("Structure count", 64.0, phases.getStructures().size(), 0, "Enumerated structures count"));

        List<Double> allPhases = phases.allTotalPhases();
        long distinctCount = allPhases.stream().distinct().count();
        checks.add(makeCheckDouble("Distinct phase count", 64.0, distinctCount, 0, "All 64 structures should produce distinct total phases"));
        return checks;
    }

    private List<VerificationCheck> verifyDiracOperator(DiracOperator dirac) {
        List<VerificationCheck> checks = new ArrayList<>();
        checks.add(makeCheckBoolean("Lichnerowicz formula", true, dirac.verifyLichnerowicz(), "D^2 = Delta + R/4"));
        checks.add(makeCheckDouble("lambda_D^2_trivial", 3.338, dirac.getLambdaD2Trivial(), DEFAULT_TOLERANCE, "Dirac trivial eigenvalue = 3.838 + (-2)/4 = 3.338"));
        checks.add(makeCheckDouble("lambda_D_trivial", Math.sqrt(3.338), Math.sqrt(dirac.getLambdaD2Trivial()), DEFAULT_TOLERANCE, "Dirac trivial eigenvalue (sqrt)"));
        return checks;
    }

    private List<VerificationCheck> verifyChoptyukFormula(ChoptyukFormula formula) {
        List<VerificationCheck> checks = new ArrayList<>();
        double deltaC = formula.getDeltaC();

        double expectedBC = 3.338 + Math.pow(deltaC, 2) / 2.0;
        checks.add(makeCheckDouble("b-C correction", expectedBC, formula.getDeltaBC(), DEFAULT_TOLERANCE, "Delta_bC = lambda_D^2_triv + delta_C^2/2"));

        double expectedEffAC = Math.pow(deltaC, 5) / 22.0;
        checks.add(makeCheckDouble("a-C effective phase", expectedEffAC, formula.getDeltaEffAC(), DEFAULT_TOLERANCE * 10, "delta_eff = delta_C^5/22 ~ 0.000828"));

        double expectedBase = 3.338 + Math.pow(deltaC, 2) / 2.0 - Math.pow(deltaC, 5) / 22.0;
        checks.add(makeCheckDouble("Choptyuk base", expectedBase, formula.getDeltaChBase(), DEFAULT_TOLERANCE, "Delta_Ch = lambda_D^2_triv + delta_C^2/2 - delta_C^5/22"));

        double expectedHigher = expectedBase + Math.pow(deltaC, 4) / 8.0 + Math.pow(deltaC, 6) / 2.0;
        checks.add(makeCheckDouble("Choptyuk higher order", expectedHigher, formula.getDeltaChHigher(), DEFAULT_TOLERANCE, "Delta_Ch^+ = Delta_Ch + delta_C^4/8 + delta_C^6/2"));

        checks.add(makeCheckDouble("Deviation from observed", formula.getDeltaChBase() - formula.getDeltaObserved(),
                formula.getDeviationBase(), DEFAULT_TOLERANCE, "Delta_Ch - Delta_obs"));

        return checks;
    }

    private VerificationCheck verifyBChConstant() {
        double expected = 1.0 - Math.cos(2.0 * Math.PI / 7.0);
        return makeCheckDouble("b_Ch constant", 0.376510, expected, 1e-4, "b_Ch = 1 - cos(2*pi/7) ~ 0.376510");
    }

    private List<VerificationCheck> verifySurfaces(List<SurfaceSpec> surfaces) {
        List<VerificationCheck> checks = new ArrayList<>();
        checks.add(makeCheckDouble("Bolza genus", 2.0, surfaces.get(0).getGenus(), 0, "Bolza surface genus"));
        checks.add(makeCheckDouble("Bolza |Aut|", 48.0, surfaces.get(0).getAutomorphismOrder(), 0, "Bolza automorphism order"));
        checks.add(makeCheckDouble("Bring genus", 4.0, surfaces.get(1).getGenus(), 0, "Bring curve genus"));
        checks.add(makeCheckDouble("Bring |Aut|", 120.0, surfaces.get(1).getAutomorphismOrder(), 0, "Bring automorphism order"));
        checks.add(makeCheckDouble("Macbeath genus", 7.0, surfaces.get(2).getGenus(), 0, "Macbeath surface genus"));
        checks.add(makeCheckDouble("Macbeath |Aut|", 504.0, surfaces.get(2).getAutomorphismOrder(), 0, "Macbeath automorphism order"));
        checks.add(makeCheckBoolean("Macbeath Hurwitz", true, surfaces.get(2).isHurwitzCurve(), "Macbeath is Hurwitz curve"));
        return checks;
    }

    private List<VerificationCheck> verifyQNMPredictions(List<QNMEvent> events) {
        List<VerificationCheck> checks = new ArrayList<>();
        for (QNMEvent event : events) {
            String name = event.getEventName();
            boolean errorOk = event.getRelativeError() < 0.05;
            checks.add(makeCheckBoolean(name + " error < 5%", true, errorOk, name + ": QNM prediction within 5% of observation"));
            checks.add(makeCheckBoolean(name + " SNR > 5", true, event.getSnr() > 5, name + ": Signal-to-noise ratio > 5"));
        }
        return checks;
    }

    private VerificationCheck makeCheckDouble(String name, double expected, double actual, double tolerance, String message) {
        boolean passed = Math.abs(expected - actual) <= Math.max(tolerance, Math.abs(expected) * tolerance + 1e-10);
        return new VerificationCheck(name, passed, expected, actual, tolerance, message);
    }

    private VerificationCheck makeCheckBoolean(String name, boolean expected, boolean actual, String message) {
        boolean passed = expected == actual;
        return new VerificationCheck(name, passed, expected ? 1.0 : 0.0, actual ? 1.0 : 0.0, 0, message);
    }
}
