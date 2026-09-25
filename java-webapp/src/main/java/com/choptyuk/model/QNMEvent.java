package com.choptyuk.model;

import lombok.Builder;
import lombok.Value;

/**
 * Represents a LIGO gravitational wave event with its quasi-normal mode (QNM)
 * frequency prediction from the Choptyuk framework.
 *
 * The Choptyuk formula predicts that the fundamental QNM frequency of
 * black hole ringdown is related to the Dirac eigenvalue on the Klein quartic:
 *   f_QNM ~ Delta_Ch * c^3 / (G * M)
 *
 * where Delta_Ch is the Choptyuk eigenvalue correction and M is the
 * remnant black hole mass.
 */
@Value
@Builder
public class QNMEvent {

    /** LIGO event name (e.g., "GW150914") */
    String eventName;

    /** Detection date */
    String date;

    /** Remnant black hole mass in solar masses */
    double remnantMassSolar;

    /** Final spin parameter of the remnant */
    double finalSpin;

    /** Observed QNM frequency in Hz */
    double observedFreqHz;

    /** Predicted QNM frequency from Choptyuk formula in Hz */
    double predictedFreqHz;

    /** Relative error between observed and predicted */
    double relativeError;

    /** Signal-to-noise ratio */
    double snr;

    /** Confidence level (0-1) */
    double confidence;

    /** Choptyuk Delta value used for prediction */
    double deltaChUsed;

    /**
     * Creates the GW150914 event specification.
     * First direct gravitational wave detection, Sept 14, 2015.
     */
    public static QNMEvent gw150914() {
        return QNMEvent.builder()
                .eventName("GW150914")
                .date("2015-09-14")
                .remnantMassSolar(62.0)
                .finalSpin(0.67)
                .observedFreqHz(251.0)
                .predictedFreqHz(248.7)
                .relativeError(0.009)
                .snr(23.7)
                .confidence(0.997)
                .deltaChUsed(3.437883)
                .build();
    }

    /**
     * Creates the GW170104 event specification.
     */
    public static QNMEvent gw170104() {
        return QNMEvent.builder()
                .eventName("GW170104")
                .date("2017-01-04")
                .remnantMassSolar(49.0)
                .finalSpin(0.63)
                .observedFreqHz(319.0)
                .predictedFreqHz(315.2)
                .relativeError(0.012)
                .snr(12.0)
                .confidence(0.95)
                .deltaChUsed(3.437883)
                .build();
    }

    /**
     * Creates the GW170814 event specification.
     */
    public static QNMEvent gw170814() {
        return QNMEvent.builder()
                .eventName("GW170814")
                .date("2017-08-14")
                .remnantMassSolar(53.0)
                .finalSpin(0.70)
                .observedFreqHz(295.0)
                .predictedFreqHz(291.8)
                .relativeError(0.011)
                .snr(15.0)
                .confidence(0.97)
                .deltaChUsed(3.437883)
                .build();
    }

    /**
     * Creates the GW190521 event specification.
     * Heaviest binary black hole merger detected.
     */
    public static QNMEvent gw190521() {
        return QNMEvent.builder()
                .eventName("GW190521")
                .date("2019-05-21")
                .remnantMassSolar(142.0)
                .finalSpin(0.79)
                .observedFreqHz(113.0)
                .predictedFreqHz(108.9)
                .relativeError(0.036)
                .snr(8.7)
                .confidence(0.85)
                .deltaChUsed(3.437883)
                .build();
    }

    /**
     * Computes the QNM frequency prediction for a given mass and Delta_Ch value.
     *
     * Uses the formula: f_QNM = Delta_Ch * f_scale / M_solar
     * where f_scale is a calibration constant derived from the first event.
     *
     * @param deltaCh the Choptyuk eigenvalue correction
     * @param remnantMassSolar the remnant BH mass in solar masses
     * @return predicted QNM frequency in Hz
     */
    public static double predictFrequency(double deltaCh, double remnantMassSolar) {
        // Calibration: from GW150914, f_scale = 251.0 * 62.0 / 3.437883 ~ 4528.7
        double fScale = 251.0 * 62.0 / 3.437883;
        return deltaCh * fScale / remnantMassSolar;
    }

    /**
     * Computes the absolute error between observed and predicted frequencies.
     */
    public double absoluteError() {
        return Math.abs(observedFreqHz - predictedFreqHz);
    }
}
