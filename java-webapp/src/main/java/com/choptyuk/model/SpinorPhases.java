package com.choptyuk.model;

import lombok.Builder;
import lombok.Value;
import java.util.ArrayList;
import java.util.List;

/**
 * Represents the three spinor phases delta_A, delta_B, delta_C and provides
 * enumeration of all 64 spinor structures (2^6 combinations).
 *
 * The spinor phases are determined by the geometry of the Klein quartic:
 *   delta_A = pi/2  (from the A-twist, order 2)
 *   delta_B = pi/3  (from the B-twist, order 3)
 *   delta_C = pi/7  (from the C-twist, order 7)
 *
 * The 64 = 2^6 spinor structures arise from the 6-dimensional spinor space
 * at genus g=3: dim H^0(C, K^{1/2}) has 2^3 real degrees of freedom,
 * giving 2^6 = 64 possible sign combinations.
 */
@Value
@Builder
public class SpinorPhases {

    /** Spinor phase delta_A = pi/2 */
    double deltaA;

    /** Spinor phase delta_B = pi/3 */
    double deltaB;

    /** Spinor phase delta_C = pi/7 */
    double deltaC;

    /** Number of spinor structures (64 = 2^6) */
    int numStructures;

    /** List of all 64 spinor structure sign combinations */
    List<SpinorStructure> structures;

    /**
     * Represents a single spinor structure as a 6-tuple of signs (+1/-1).
     */
    @Value
    @Builder
    public static class SpinorStructure {
        int s1;
        int s2;
        int s3;
        int s4;
        int s5;
        int s6;

        /** Compute the total phase contribution for this structure */
        public double totalPhase(double dA, double dB, double dC) {
            return s1 * dA + s2 * dB + s3 * dC + s4 * dA + s5 * dB + s6 * dC;
        }

        /** Index of this structure (0-63) */
        public int index() {
            return ((s1 + 1) / 2) * 32 + ((s2 + 1) / 2) * 16 +
                   ((s3 + 1) / 2) * 8 + ((s4 + 1) / 2) * 4 +
                   ((s5 + 1) / 2) * 2 + ((s6 + 1) / 2);
        }

        @Override
        public String toString() {
            return String.format("[%d,%d,%d,%d,%d,%d]", s1, s2, s3, s4, s5, s6);
        }
    }

    /**
     * Factory method creating canonical spinor phases.
     */
    public static SpinorPhases canonical() {
        double dA = Math.PI / 2.0;
        double dB = Math.PI / 3.0;
        double dC = Math.PI / 7.0;

        List<SpinorStructure> structures = enumerateStructures();

        return SpinorPhases.builder()
                .deltaA(dA)
                .deltaB(dB)
                .deltaC(dC)
                .numStructures(64)
                .structures(structures)
                .build();
    }

    /**
     * Creates spinor phases with custom values.
     */
    public static SpinorPhases of(double deltaA, double deltaB, double deltaC) {
        List<SpinorStructure> structures = enumerateStructures();
        return SpinorPhases.builder()
                .deltaA(deltaA)
                .deltaB(deltaB)
                .deltaC(deltaC)
                .numStructures(64)
                .structures(structures)
                .build();
    }

    /**
     * Enumerates all 64 spinor structures (2^6 sign combinations).
     */
    private static List<SpinorStructure> enumerateStructures() {
        List<SpinorStructure> result = new ArrayList<>(64);
        for (int i = 0; i < 64; i++) {
            int s1 = ((i >> 5) & 1) == 0 ? -1 : 1;
            int s2 = ((i >> 4) & 1) == 0 ? -1 : 1;
            int s3 = ((i >> 3) & 1) == 0 ? -1 : 1;
            int s4 = ((i >> 2) & 1) == 0 ? -1 : 1;
            int s5 = ((i >> 1) & 1) == 0 ? -1 : 1;
            int s6 = (i & 1) == 0 ? -1 : 1;
            result.add(SpinorStructure.builder()
                    .s1(s1).s2(s2).s3(s3).s4(s4).s5(s5).s6(s6)
                    .build());
        }
        return result;
    }

    /**
     * Computes all 64 total phase values for the current spinor phases.
     */
    public List<Double> allTotalPhases() {
        List<Double> phases = new ArrayList<>(64);
        for (SpinorStructure s : structures) {
            phases.add(s.totalPhase(deltaA, deltaB, deltaC));
        }
        return phases;
    }

    /**
     * Computes the effective phase for a-C correction: delta_eff = delta_C^5 / 22.
     */
    public double effectivePhaseAC() {
        return Math.pow(deltaC, 5) / 22.0;
    }

    /**
     * Computes the second-order correction: delta_C^2 / 2.
     */
    public double secondOrderCorrection() {
        return Math.pow(deltaC, 2) / 2.0;
    }

    /**
     * Computes the fourth-order correction: delta_C^4 / 8.
     */
    public double fourthOrderCorrection() {
        return Math.pow(deltaC, 4) / 8.0;
    }

    /**
     * Computes the sixth-order correction: delta_C^6 / 2.
     */
    public double sixthOrderCorrection() {
        return Math.pow(deltaC, 6) / 2.0;
    }
}
