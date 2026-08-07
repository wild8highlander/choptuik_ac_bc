"""Custom hypothesis testing framework for spinor correction research.

Allows users to define arbitrary configurations for testing variations
of the Choptyuk formula with custom parameters, group structures, and
correction formulas.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class HypothesisConfig:
    """Configuration for a custom hypothesis test.

    Attributes:
        name: Hypothesis name/identifier.
        description: Human-readable description.
        custom_delta_C: Custom spinor phase (None = use pi/7).
        custom_lambda_D2: Custom Dirac eigenvalue (None = use 3.338).
        custom_k_struct: Custom structural constant (None = use 22).
        custom_c4: Custom 3rd-order coefficient (None = use 1/8).
        custom_c6: Custom 4th-order coefficient (None = use 1/2).
        custom_group_order: Custom group order (None = use 168).
        custom_genus: Custom genus (None = use 3).
        custom_correction_fn: Optional custom correction function.
    """
    name: str
    description: str = ""
    custom_delta_C: float | None = None
    custom_lambda_D2: float | None = None
    custom_k_struct: int | None = None
    custom_c4: float | None = None
    custom_c6: float | None = None
    custom_group_order: int | None = None
    custom_genus: int | None = None
    custom_correction_fn: Callable | None = None


@dataclass
class HypothesisResult:
    """Result of a hypothesis test.

    Attributes:
        name: Hypothesis name.
        delta_C: Spinor phase used.
        lambda_D2: Dirac eigenvalue used.
        delta_bc: b-C corrected value.
        delta_ch_base: Base Choptyuk value.
        delta_ch_full: Full Choptyuk value.
        deviation: Percentage deviation from observed.
        passed: Whether deviation is within tolerance.
    """
    name: str
    delta_C: float
    lambda_D2: float
    delta_bc: float
    delta_ch_base: float
    delta_ch_full: float
    deviation: float
    passed: bool


class HypothesisTester:
    """Framework for testing custom hypotheses about spinor corrections.

    Supports:
    - Parameter sweeps (vary one parameter over a range)
    - Custom correction formulas
    - Group structure variations
    - Multi-hypothesis comparison
    """

    def __init__(self, delta_obs: float = 3.443, b_ch_obs: float = 0.377,
                 tolerance: float = 1.0):
        self.delta_obs = delta_obs
        self.b_ch_obs = b_ch_obs
        self.tolerance = tolerance  # percent
        logger.info(f"Hypothesis tester: Δ_obs={delta_obs}, tolerance={tolerance}%")

    def test_hypothesis(self, config: HypothesisConfig) -> HypothesisResult:
        """Test a single hypothesis configuration.

        Args:
            config: HypothesisConfig with custom parameters.

        Returns:
            HypothesisResult with computed values and pass/fail.
        """
        dC = config.custom_delta_C if config.custom_delta_C is not None else np.pi / 7
        lam_D2 = config.custom_lambda_D2 if config.custom_lambda_D2 is not None else 3.338
        k = config.custom_k_struct if config.custom_k_struct is not None else 22
        c4 = config.custom_c4 if config.custom_c4 is not None else 0.125
        c6 = config.custom_c6 if config.custom_c6 is not None else 0.5

        # b-C correction
        delta_bc = lam_D2 + dC**2 / 2

        # a-C correction
        delta_eff = dC**5 / k

        # Base Choptyuk
        delta_ch_base = delta_bc - delta_eff

        # Custom correction if provided
        if config.custom_correction_fn is not None:
            delta_ch_full = config.custom_correction_fn(dC, lam_D2, k)
        else:
            delta_ch_full = delta_ch_base + c4 * dC**4 + c6 * dC**6

        deviation = abs(delta_ch_full - self.delta_obs) / self.delta_obs * 100
        passed = deviation <= self.tolerance

        result = HypothesisResult(
            name=config.name, delta_C=dC, lambda_D2=lam_D2,
            delta_bc=delta_bc, delta_ch_base=delta_ch_base,
            delta_ch_full=delta_ch_full, deviation=deviation, passed=passed,
        )
        logger.info(
            f"Hypothesis '{config.name}': Δ_Ch={delta_ch_full:.6f}, "
            f"deviation={deviation:.3f}%, {'PASS' if passed else 'FAIL'}"
        )
        return result

    def parameter_sweep(self, param_name: str, values: list[float],
                         base_config: HypothesisConfig | None = None) -> list[HypothesisResult]:
        """Sweep a single parameter over a range of values.

        Args:
            param_name: Parameter to vary ('delta_C', 'lambda_D2', 'k_struct', etc.)
            values: List of values to test.
            base_config: Base configuration (default parameters used if None).

        Returns:
            List of HypothesisResult for each value.
        """
        results = []
        for val in values:
            config = base_config or HypothesisConfig(name="sweep")
            config.name = f"sweep_{param_name}={val:.4f}"
            config.description = f"Parameter sweep: {param_name} = {val}"

            if param_name == "delta_C":
                config.custom_delta_C = val
            elif param_name == "lambda_D2":
                config.custom_lambda_D2 = val
            elif param_name == "k_struct":
                config.custom_k_struct = int(val)
            elif param_name == "c4":
                config.custom_c4 = val
            elif param_name == "c6":
                config.custom_c6 = val
            else:
                logger.warning(f"Unknown parameter: {param_name}")
                continue

            results.append(self.test_hypothesis(config))

        return results

    def compare_hypotheses(self, configs: list[HypothesisConfig]) -> list[HypothesisResult]:
        """Compare multiple hypotheses side by side.

        Args:
            configs: List of HypothesisConfig to test.

        Returns:
            List of HypothesisResult sorted by deviation.
        """
        results = [self.test_hypothesis(c) for c in configs]
        results.sort(key=lambda r: r.deviation)
        for i, r in enumerate(results):
            logger.info(f"  Rank {i+1}: '{r.name}' deviation={r.deviation:.3f}%")
        return results
