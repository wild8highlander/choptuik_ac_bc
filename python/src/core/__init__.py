"""Core mathematical computations for the Klein quartic curve and spinor corrections."""

from .choptyuk_formula import ChoptyukFormula
from .dirac_operator import DiracOperator
from .hypothesis import HypothesisTester
from .klein_curve import KleinCurve
from .qnm import QNMPredictor
from .spinor_phases import SpinorPhases
from .surfaces import BOLZA, BRING, MACBEATH, SurfaceSpec

__all__ = [
    "BOLZA",
    "BRING",
    "MACBEATH",
    "ChoptyukFormula",
    "DiracOperator",
    "HypothesisTester",
    "KleinCurve",
    "QNMPredictor",
    "SpinorPhases",
    "SurfaceSpec",
]
