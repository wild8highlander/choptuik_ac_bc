package com.choptyuk.model;

import lombok.Builder;
import lombok.Value;

/**
 * Einstein GR QNM frequency correction from spinorial braking.
 * ω^corr = ω · (1 - δ_eff/π²) where δ_eff = (π/7)⁵/22.
 * Correction factor ≈ 0.999916, shift ≈ 8.4×10⁻⁵ of QNM frequency.
 */
@Value
@Builder
public class EinsteinQNMCorrection {
    double deltaEff;          // (π/7)⁵/22
    double qnmCorrection;     // δ_eff/π²
    double qnmFactor;         // 1 - δ_eff/π² ≈ 0.999916
    double correctionPct;     // correction in percent

    public static EinsteinQNMCorrection canonical() {
        double deltaC = Math.PI / 7.0;
        double deltaEff = Math.pow(deltaC, 5) / 22.0;
        double qnmCorrection = deltaEff / (Math.PI * Math.PI);
        double qnmFactor = 1.0 - qnmCorrection;
        return EinsteinQNMCorrection.builder()
            .deltaEff(deltaEff)
            .qnmCorrection(qnmCorrection)
            .qnmFactor(qnmFactor)
            .correctionPct(qnmCorrection * 100.0)
            .build();
    }

    public double correctedFrequency(double omega) {
        return omega * qnmFactor;
    }
}
