package com.choptyuk.controller;

import com.choptyuk.model.ChoptyukFormula;
import com.choptyuk.model.EinsteinQNMCorrection;
import com.choptyuk.model.K3Surface;
import com.choptyuk.model.TyukovskyEquation;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * REST API controller for enhanced verification endpoints.
 *
 * Endpoints:
 *   GET /api/enhanced/k3           - K3 surface data
 *   GET /api/enhanced/tyukovsky    - Tyukovsky equation data
 *   GET /api/enhanced/einstein-qnm - Einstein QNM correction data
 *   GET /api/enhanced/verify       - Full enhanced verification
 */
@RestController
@RequestMapping("/api/enhanced")
@Slf4j
public class EnhancedController {

    /**
     * Returns K3 surface data with Betti numbers and Hodge decomposition.
     */
    @GetMapping("/k3")
    public ResponseEntity<Map<String, Object>> k3Surface() {
        log.info("GET /api/enhanced/k3");
        K3Surface k3 = K3Surface.canonical();

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("k3Surface", k3);
        response.put("b2DecompositionVerified", k3.verifyB2Decomposition());
        response.put("seibergWittenCompatible", k3.isSeibergWittenCompatible());
        response.put("b2OverDiracIndex", k3.b2OverDiracIndex());

        return ResponseEntity.ok(response);
    }

    /**
     * Returns Tyukovsky equation data with corrected critical exponent.
     */
    @GetMapping("/tyukovsky")
    public ResponseEntity<Map<String, Object>> tyukovskyEquation() {
        log.info("GET /api/enhanced/tyukovsky");
        TyukovskyEquation te = TyukovskyEquation.canonical();

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("tyukovskyEquation", te);

        return ResponseEntity.ok(response);
    }

    /**
     * Returns Einstein GR QNM correction data from spinorial braking.
     */
    @GetMapping("/einstein-qnm")
    public ResponseEntity<Map<String, Object>> einsteinQNMCorrection() {
        log.info("GET /api/enhanced/einstein-qnm");
        EinsteinQNMCorrection correction = EinsteinQNMCorrection.canonical();

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("einsteinQNMCorrection", correction);

        return ResponseEntity.ok(response);
    }

    /**
     * Runs the full enhanced verification combining all new models
     * and the new ChoptyukFormula correction methods.
     */
    @GetMapping("/verify")
    public ResponseEntity<Map<String, Object>> verify() {
        log.info("GET /api/enhanced/verify");

        K3Surface k3 = K3Surface.canonical();
        TyukovskyEquation te = TyukovskyEquation.canonical();
        EinsteinQNMCorrection qnm = EinsteinQNMCorrection.canonical();
        ChoptyukFormula formula = ChoptyukFormula.canonical();

        Map<String, Object> result = new LinkedHashMap<>();

        // K3 verification
        result.put("k3_b2DecompositionVerified", k3.verifyB2Decomposition());
        result.put("k3_seibergWittenCompatible", k3.isSeibergWittenCompatible());
        result.put("k3_b2OverDiracIndex", k3.b2OverDiracIndex());

        // Tyukovsky verification
        result.put("tyukovsky_deltaCorrected", te.getDeltaCorrected());
        result.put("tyukovsky_echoPeriod", te.getEchoPeriod());
        result.put("tyukovsky_echoShiftPct", te.getEchoShiftPct());
        result.put("tyukovsky_freeParameters", te.getFreeParameters());

        // Einstein QNM verification
        result.put("einsteinQNM_deltaEff", qnm.getDeltaEff());
        result.put("einsteinQNM_qnmFactor", qnm.getQnmFactor());
        result.put("einsteinQNM_correctionPct", qnm.getCorrectionPct());

        // Choptyuk formula new methods
        result.put("choptyuk_imaginaryCorrection", formula.imaginaryCorrection());
        result.put("choptyuk_kahlerCorrection", formula.kahlerCorrection());
        result.put("choptyuk_tyukovskyCorrection", formula.tyukovskyCorrection(te.getDelta0()));
        result.put("choptyuk_einsteinQNMCorrection", formula.einsteinQNMCorrection());

        // Overall pass/fail
        boolean allPassed = k3.verifyB2Decomposition()
                && k3.isSeibergWittenCompatible()
                && te.getFreeParameters() == 0;
        result.put("allPassed", allPassed);

        return ResponseEntity.ok(result);
    }
}
