package com.choptyuk.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Application configuration with all customizable parameters for the
 * Choptyuk Spinor Monograph verification and simulation.
 *
 * All parameters can be overridden via application.properties or
 * environment variables (CHOPTYUK_* prefix).
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "choptyuk")
public class AppConfig {

    /** Spinor phase delta_A (canonical: pi/2 = 1.570796) */
    private double deltaA = Math.PI / 2.0;

    /** Spinor phase delta_B (canonical: pi/3 = 1.047198) */
    private double deltaB = Math.PI / 3.0;

    /** Spinor phase delta_C (canonical: pi/7 = 0.448799) */
    private double deltaC = Math.PI / 7.0;

    /** First Laplacian eigenvalue lambda_1 on Klein quartic (canonical: 3.838) */
    private double lambda1 = 3.838;

    /** Scalar curvature R (canonical: -2) */
    private double scalarCurvature = -2.0;

    /** Genus of the Klein curve (canonical: 3) */
    private int genus = 3;

    /** PSL(2,7) automorphism group order (canonical: 168) */
    private int pslOrder = 168;

    /** Observed Delta value from LIGO data (canonical: 3.443) */
    private double deltaObserved = 3.443;

    /** Maximum correction order in Choptyuk formula (canonical: 6) */
    private int maxCorrectionOrder = 6;

    /** Default tolerance for verification checks */
    private double verificationTolerance = 1e-4;

    /** Number of points for parameter sweeps */
    private int sweepPoints = 100;

    /** Plot width in pixels */
    private int plotWidth = 1200;

    /** Plot height in pixels */
    private int plotHeight = 800;

    /** Plot DPI */
    private int plotDpi = 600;

    /** Reports output directory */
    private String reportDir = "reports";

    /** Plots output directory */
    private String plotDir = "plots";

    /** Whether to run verification on startup */
    private boolean verifyOnStartup = false;

    /** QNM frequency scale calibration constant */
    private double qnmScaleCalibration = 251.0 * 62.0 / 3.437883;

    /** b_Ch constant: 1 - cos(2*pi/7) */
    private double bCh = 1.0 - Math.cos(2.0 * Math.PI / 7.0);

    /**
     * Computes the Dirac squared trivial eigenvalue from current parameters.
     */
    public double getLambdaD2Trivial() {
        return lambda1 + scalarCurvature / 4.0;
    }

    /**
     * Computes the b-C correction value.
     */
    public double getDeltaBC() {
        return getLambdaD2Trivial() + Math.pow(deltaC, 2) / 2.0;
    }

    /**
     * Computes the Choptyuk base formula value.
     */
    public double getDeltaChBase() {
        return getLambdaD2Trivial() + Math.pow(deltaC, 2) / 2.0 - Math.pow(deltaC, 5) / 22.0;
    }
}
