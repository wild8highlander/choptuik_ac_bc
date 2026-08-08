package com.choptyuk.model;

import lombok.Builder;
import lombok.Value;

/**
 * Adaptation of spinorial corrections to Tyukovsky equations.
 * Corrected critical exponent: δ_corr = δ₀ + δ_C²/2 - δ_C⁵/22
 * Zero free parameters — all determined by Klein curve data.
 */
@Value
@Builder
public class TyukovskyEquation {
    double deltaC;      // π/7
    double delta0;      // uncorrected critical exponent
    double deltaCorrected;
    double echoPeriod;
    double echoShiftPct;
    int freeParameters;

    public static TyukovskyEquation canonical() {
        return of(Math.PI / 7.0, 0.36);
    }

    public static TyukovskyEquation of(double deltaC, double delta0) {
        double deltaCorr = delta0 + Math.pow(deltaC, 2) / 2.0 - Math.pow(deltaC, 5) / 22.0;
        double echoPeriod = 1.0 / deltaCorr;
        double echoShiftPct = (echoPeriod - 1.0 / delta0) / (1.0 / delta0) * 100.0;
        return TyukovskyEquation.builder()
            .deltaC(deltaC)
            .delta0(delta0)
            .deltaCorrected(deltaCorr)
            .echoPeriod(echoPeriod)
            .echoShiftPct(echoShiftPct)
            .freeParameters(0)
            .build();
    }
}
