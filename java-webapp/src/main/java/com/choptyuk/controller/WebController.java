package com.choptyuk.controller;

import com.choptyuk.model.*;
import com.choptyuk.service.PlotService;
import com.choptyuk.service.ReportService;
import com.choptyuk.service.SimulationService;
import com.choptyuk.service.VerificationService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;

/**
 * Web UI controller serving Thymeleaf templates.
 *
 * Pages:
 *   GET /           - Dashboard with overview and quick verify
 *   GET /verify     - Verification page with detailed results
 *   GET /simulate   - Simulation page with parameter sweep controls
 *   GET /hypothesis - Custom hypothesis testing page
 *   GET /reports    - Reports listing and download page
 */
@Controller
@Slf4j
public class WebController {

    private final VerificationService verificationService;
    private final SimulationService simulationService;
    private final ReportService reportService;

    public WebController(VerificationService verificationService,
                         SimulationService simulationService,
                         ReportService reportService) {
        this.verificationService = verificationService;
        this.simulationService = simulationService;
        this.reportService = reportService;
    }

    @GetMapping("/")
    public String dashboard(Model model) {
        log.info("GET / - Dashboard");

        // Run quick verification for dashboard
        VerificationService.VerificationResult result = verificationService.verifyAll();

        model.addAttribute("title", "Choptyuk Spinor Monograph");
        model.addAttribute("subtitle", "Verification & Simulation");
        model.addAttribute("allPassed", result.allPassed());
        model.addAttribute("passedChecks", result.passedChecks());
        model.addAttribute("totalChecks", result.totalChecks());
        model.addAttribute("deltaChBase", result.choptyukFormula().getDeltaChBase());
        model.addAttribute("deltaChHigher", result.choptyukFormula().getDeltaChHigher());
        model.addAttribute("deltaObserved", result.choptyukFormula().getDeltaObserved());
        model.addAttribute("deviationBase", result.choptyukFormula().getDeviationBase());
        model.addAttribute("relativeErrorBase", result.choptyukFormula().relativeErrorBase());
        model.addAttribute("bCh", result.choptyukFormula().getBCh());

        // Klein curve info
        model.addAttribute("genus", result.kleinCurve().getGenus());
        model.addAttribute("pslOrder", result.kleinCurve().getPslOrder());
        model.addAttribute("lambda1", result.kleinCurve().getLambda1());

        // Spinor phases
        model.addAttribute("deltaA", result.spinorPhases().getDeltaA());
        model.addAttribute("deltaB", result.spinorPhases().getDeltaB());
        model.addAttribute("deltaC", result.spinorPhases().getDeltaC());
        model.addAttribute("numStructures", result.spinorPhases().getNumStructures());

        return "dashboard";
    }

    @GetMapping("/verify")
    public String verify(Model model,
                         @RequestParam(required = false) Double deltaA,
                         @RequestParam(required = false) Double deltaB,
                         @RequestParam(required = false) Double deltaC,
                         @RequestParam(required = false) Double lambda1,
                         @RequestParam(required = false) Double scalarCurvature,
                         @RequestParam(required = false) Double deltaObserved) {
        log.info("GET /verify - Verification page");

        double dA = deltaA != null ? deltaA : Math.PI / 2.0;
        double dB = deltaB != null ? deltaB : Math.PI / 3.0;
        double dC = deltaC != null ? deltaC : Math.PI / 7.0;
        double l1 = lambda1 != null ? lambda1 : 3.838;
        double R = scalarCurvature != null ? scalarCurvature : -2.0;
        double dObs = deltaObserved != null ? deltaObserved : 3.443;

        VerificationService.VerificationResult result = verificationService.verifyAll(dA, dB, dC, l1, R, dObs);

        model.addAttribute("title", "Verification Results");
        model.addAttribute("result", result);
        model.addAttribute("checks", result.checks());
        model.addAttribute("surfaces", result.surfaces());
        model.addAttribute("qnmEvents", result.qnmEvents());

        // Input parameters for form
        model.addAttribute("inputDeltaA", dA);
        model.addAttribute("inputDeltaB", dB);
        model.addAttribute("inputDeltaC", dC);
        model.addAttribute("inputLambda1", l1);
        model.addAttribute("inputR", R);
        model.addAttribute("inputDeltaObs", dObs);

        return "verify";
    }

    @GetMapping("/simulate")
    public String simulate(Model model) {
        log.info("GET /simulate - Simulation page");

        SimulationService.SimulationResult result = simulationService.simulate();

        model.addAttribute("title", "Simulation & Parameter Sweep");
        model.addAttribute("result", result);
        model.addAttribute("deltaCSweep", result.deltaCSweep());
        model.addAttribute("lambda1Sweep", result.lambda1Sweep());
        model.addAttribute("convergence", result.convergence());
        model.addAttribute("sensitivity", result.sensitivity());

        return "simulate";
    }

    @GetMapping("/hypothesis")
    public String hypothesis(Model model) {
        log.info("GET /hypothesis - Hypothesis testing page");

        HypothesisConfig canonical = HypothesisConfig.canonical();

        model.addAttribute("title", "Custom Hypothesis Testing");
        model.addAttribute("canonical", canonical);
        model.addAttribute("canonicalDeltaCh", canonical.evaluateChoptyuk());
        model.addAttribute("canonicalDeviation", canonical.deviation());

        return "hypothesis";
    }

    @GetMapping("/reports")
    public String reports(Model model) {
        log.info("GET /reports - Reports page");

        model.addAttribute("title", "Reports & Downloads");
        model.addAttribute("formats", List.of("JSON", "HTML", "CSV", "TXT", "MD", "DOCX", "PDF"));
        model.addAttribute("existingReports", reportService.listReports());

        return "reports";
    }
}
