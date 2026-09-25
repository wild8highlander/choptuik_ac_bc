package com.choptyuk.model;

import lombok.Builder;
import lombok.Value;

/**
 * K3 surface as a 4D spin manifold with Betti numbers and Hodge decomposition.
 * b₂ = 22 = h^(1,1) + 2h^(2,0) = 20 + 2.
 * Dirac index Â(K3) = 2, holonomy Sp(1) ≅ SU(2).
 */
@Value
@Builder
public class K3Surface {
    int b0;        // 1
    int b1;        // 0
    int b2;        // 22
    int b3;        // 0
    int b4;        // 1
    int hodge11;   // 20
    int hodge20;   // 1
    int diracIndex; // 2
    int b2Plus;    // 3 (for Seiberg-Witten)

    public static K3Surface canonical() {
        return K3Surface.builder()
            .b0(1).b1(0).b2(22).b3(0).b4(1)
            .hodge11(20).hodge20(1)
            .diracIndex(2).b2Plus(3)
            .build();
    }

    public boolean verifyB2Decomposition() {
        return b2 == hodge11 + 2 * hodge20;
    }

    public boolean isSeibergWittenCompatible() {
        return b2Plus > 1;
    }

    public double b2OverDiracIndex() {
        return (double) b2 / diracIndex;
    }
}
