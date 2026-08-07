package com.choptyuk.model;

import lombok.Builder;
import lombok.Value;
import java.util.Map;

/**
 * Represents a surface specification used in the Choptyuk framework.
 *
 * The three canonical surfaces are:
 * <ul>
 *   <li><b>Bolza surface</b>: Genus 2, maximal automorphism group GL(2,3) of order 48.
 *       The most symmetric genus-2 surface, defined over Q(sqrt(2)).</li>
 *   <li><b>Bring curve</b>: Genus 4, automorphism group S_5 of order 120.
 *       Defined by x^5 + y^5 + z^5 + w^5 + t^5 = 0, x+y+z+w+t = 0 in P^4.</li>
 *   <li><b>Macbeath surface</b>: Genus 7, Hurwitz curve with PSL(2,8) of order 504.
 *       Attains the Hurwitz bound 84(g-1) = 504.</li>
 * </ul>
 */
@Value
@Builder
public class SurfaceSpec {

    /** Name of the surface */
    String name;

    /** Genus of the surface */
    int genus;

    /** Order of the automorphism group */
    int automorphismOrder;

    /** Name of the automorphism group */
    String automorphismGroup;

    /** Scalar curvature */
    double scalarCurvature;

    /** Area = 4*pi*g */
    double area;

    /** First positive Laplacian eigenvalue (approximate) */
    double lambda1;

    /** Whether this is a Hurwitz curve (attains the Hurwitz bound) */
    boolean isHurwitzCurve;

    /** Additional invariants */
    Map<String, Double> invariants;

    /**
     * Creates the Bolza surface specification.
     * Genus 2, |Aut| = 48, GL(2,3).
     */
    public static SurfaceSpec bolza() {
        int g = 2;
        return SurfaceSpec.builder()
                .name("Bolza")
                .genus(g)
                .automorphismOrder(48)
                .automorphismGroup("GL(2,3)")
                .scalarCurvature(-2.0)
                .area(4.0 * Math.PI * g)
                .lambda1(3.832)  // approximate first eigenvalue
                .isHurwitzCurve(false)
                .invariants(Map.of(
                        "genus", (double) g,
                        "autOrder", 48.0,
                        "eulerCharacteristic", (double) (2 - 2 * g),
                        "firstBettiNumber", (double) (2 * g),
                        "hurwitzBound", (double) (84 * (g - 1)),
                        "autBoundRatio", 48.0 / (84 * (g - 1))
                ))
                .build();
    }

    /**
     * Creates the Bring curve specification.
     * Genus 4, |Aut| = 120, S_5.
     */
    public static SurfaceSpec bring() {
        int g = 4;
        return SurfaceSpec.builder()
                .name("Bring")
                .genus(g)
                .automorphismOrder(120)
                .automorphismGroup("S_5")
                .scalarCurvature(-2.0)
                .area(4.0 * Math.PI * g)
                .lambda1(3.840)  // approximate
                .isHurwitzCurve(false)
                .invariants(Map.of(
                        "genus", (double) g,
                        "autOrder", 120.0,
                        "eulerCharacteristic", (double) (2 - 2 * g),
                        "firstBettiNumber", (double) (2 * g),
                        "hurwitzBound", (double) (84 * (g - 1)),
                        "autBoundRatio", 120.0 / (84 * (g - 1))
                ))
                .build();
    }

    /**
     * Creates the Macbeath surface specification.
     * Genus 7, |Aut| = 504, PSL(2,8). Hurwitz curve.
     */
    public static SurfaceSpec macbeath() {
        int g = 7;
        return SurfaceSpec.builder()
                .name("Macbeath")
                .genus(g)
                .automorphismOrder(504)
                .automorphismGroup("PSL(2,8)")
                .scalarCurvature(-2.0)
                .area(4.0 * Math.PI * g)
                .lambda1(3.850)  // approximate
                .isHurwitzCurve(true)
                .invariants(Map.of(
                        "genus", (double) g,
                        "autOrder", 504.0,
                        "eulerCharacteristic", (double) (2 - 2 * g),
                        "firstBettiNumber", (double) (2 * g),
                        "hurwitzBound", (double) (84 * (g - 1)),
                        "autBoundRatio", 504.0 / (84 * (g - 1))
                ))
                .build();
    }

    /**
     * Computes the Dirac squared eigenvalue for the trivial spinor on this surface.
     */
    public double diracSquaredTrivial() {
        return lambda1 + scalarCurvature / 4.0;
    }

    /**
     * Computes the Hurwitz bound for this surface's genus.
     */
    public int hurwitzBound() {
        return 84 * (genus - 1);
    }
}
