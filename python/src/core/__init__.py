"""Core mathematical computations for the Klein quartic curve and spinor corrections."""

from .choptyuk_formula import ChoptyukFormula
from .dirac_operator import DiracOperator
from .enhanced_verification import CriticismResponse, K3Surface, KleinQuartic, QNMPredictor as EnhancedQNMPredictor, TyukovskyAdapter
from .hypothesis import HypothesisTester
from .klein_curve import KleinCurve
from .qcd_bridge_verification import (
    ChoptyukBridge,
    CPoddObservable,
    CPoddPredictions,
    FalsifiabilityTimeline,
    LatticeThetaDependence,
    MercuryParadox,
    MonteCarloUncertainty,
    PQAxiomWithResidual,
    WaveFunctionBridge,
)
from .qnm import QNMPredictor
from .spinor_phases import SpinorPhases
from .surfaces import BOLZA, BRING, MACBEATH, SurfaceSpec

__all__ = [
    "BOLZA",
    "BRING",
    "MACBEATH",
    "ChoptyukBridge",
    "ChoptyukFormula",
    "CPoddObservable",
    "CPoddPredictions",
    "CriticismResponse",
    "DiracOperator",
    "EnhancedQNMPredictor",
    "FalsifiabilityTimeline",
    "HypothesisTester",
    "K3Surface",
    "KleinCurve",
    "KleinQuartic",
    "LatticeThetaDependence",
    "MercuryParadox",
    "MonteCarloUncertainty",
    "PQAxiomWithResidual",
    "WaveFunctionBridge",
    "QNMPredictor",
    "SpinorPhases",
    "SurfaceSpec",
    "TyukovskyAdapter",
]
