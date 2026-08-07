package com.choptyuk;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Main entry point for the Choptyuk Spinor Monograph verification and simulation application.
 *
 * <p>Author: Ishak Khamzatovich Isaev (Исаев Исхак Хамзатович)
 * <br>Email: aslan08_05@mail.ru
 * <br>GitHub: https://github.com/wild8highlander
 * <br>Repository: https://github.com/wild8highlander/choptuik_ac_bc
 *
 * <p>This application provides tools for verifying and simulating spinor corrections
 * b-C and a-C on the Klein quartic curve, including:
 * <ul>
 *   <li>Klein curve invariant verification (genus 3, PSL(2,7) order 168)</li>
 *   <li>Spinor phase enumeration (64 structures from delta_A, delta_B, delta_C)</li>
 *   <li>Dirac operator eigenvalue computation via Lichnerowicz formula</li>
 *   <li>Choptyuk formula evaluation (b-C, a-C, unified)</li>
 *   <li>LIGO QNM prediction comparison</li>
 *   <li>Multi-format report generation and publication-quality plots</li>
 * </ul>
 */
@SpringBootApplication
public class ChoptyukApplication {

    public static void main(String[] args) {
        SpringApplication.run(ChoptyukApplication.class, args);
    }
}
