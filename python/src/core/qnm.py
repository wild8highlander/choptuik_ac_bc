"""LIGO/Virgo quasi-normal mode predictions from the Choptyuk formula.

The spinor corrections predict a frequency shift for black hole QNMs:
  delta_f = f_QNM / 14 * (a/M)^2

where a/M is the dimensionless spin parameter. This shift is compared
against detector sensitivity for current and future gravitational wave
observatories.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BHEvent:
    """A gravitational wave detection event.

    Attributes:
        name: Event designation (e.g., GW150914).
        mass_solar: Total mass in solar masses.
        spin: Dimensionless spin parameter a/M.
        f_qnm: Quasi-normal mode frequency in Hz.
        sigma: Measurement uncertainty in Hz.
    """
    name: str
    mass_solar: float
    spin: float
    f_qnm: float
    sigma: float


# Reference events
GW150914 = BHEvent("GW150914", 62.0, 0.67, 251.0, 5.5)
GW170104 = BHEvent("GW170104", 48.7, 0.65, 314.0, 25.0)
GW170814 = BHEvent("GW170814", 53.4, 0.70, 286.0, 30.0)
GW190521 = BHEvent("GW190521", 142.0, 0.72, 110.0, 10.0)

DEFAULT_EVENTS = [GW150914, GW170104, GW170814, GW190521]

# Future detectors
DEFAULT_DETECTORS = [
    {"name": "LIGO O3", "sigma_hz": 5.5},
    {"name": "LIGO A+ (2024-26)", "sigma_hz": 2.8},
    {"name": "Einstein Telescope (2030+)", "sigma_hz": 0.5},
    {"name": "Cosmic Explorer (2035+)", "sigma_hz": 0.1},
]


class QNMPredictor:
    """QNM frequency shift predictions for gravitational wave events.

    Attributes:
        events: List of BHEvent objects.
        detectors: List of future detector specifications.
        G: Gravitational constant.
        c: Speed of light.
        M_sun: Solar mass in kg.
    """

    def __init__(self, events: list[BHEvent] | None = None,
                 detectors: list[dict] | None = None,
                 G: float = 6.674e-11, c: float = 3e8,
                 M_sun: float = 1.989e30):
        self.events = events or DEFAULT_EVENTS
        self.detectors = detectors or DEFAULT_DETECTORS
        self.G = G
        self.c = c
        self.M_sun = M_sun
        logger.info(f"QNM predictor initialized with {len(self.events)} events")

    def predict_shift(self, event: BHEvent, scaling: float = 14.0) -> dict:
        """Predict QNM frequency shift for a single event.

        Args:
            event: BHEvent with observed parameters.
            scaling: Scaling factor (default 14 from Choptyuk formula).

        Returns:
            Dict with event name, predicted shift, and SNR.
        """
        delta_f = event.f_qnm / scaling * event.spin**2
        snr = delta_f / event.sigma
        result = {
            "name": event.name,
            "mass_solar": event.mass_solar,
            "spin": event.spin,
            "f_qnm": event.f_qnm,
            "delta_f": delta_f,
            "sigma": event.sigma,
            "snr": snr,
        }
        logger.info(f"QNM {event.name}: Δf={delta_f:.2f} Hz, SNR={snr:.2f}")
        return result

    def predict_all(self, scaling: float = 14.0) -> list[dict]:
        """Predict QNM shifts for all events.

        Returns:
            List of prediction dicts.
        """
        return [self.predict_shift(e, scaling) for e in self.events]

    def detectability(self, event_name: str = "GW150914",
                       scaling: float = 14.0) -> list[dict]:
        """Compute detectability for a given event across all future detectors.

        Args:
            event_name: Which event to analyze.
            scaling: QNM scaling factor.

        Returns:
            List of dicts with detector name, sigma, and SNR.
        """
        event = next((e for e in self.events if e.name == event_name), self.events[0])
        delta_f = event.f_qnm / scaling * event.spin**2

        results = []
        for det in self.detectors:
            snr = delta_f / det["sigma_hz"]
            results.append({
                "detector": det["name"],
                "sigma_hz": det["sigma_hz"],
                "snr": snr,
                "detectable": snr >= 1.0,
            })
            logger.info(f"{det['name']}: σ={det['sigma_hz']} Hz, SNR={snr:.2f}")

        return results

    def as_dict(self) -> dict:
        """Serialize QNM predictor state."""
        return {
            "n_events": len(self.events),
            "n_detectors": len(self.detectors),
            "events": [{"name": e.name, "M": e.mass_solar, "a": e.spin,
                         "f": e.f_qnm, "sigma": e.sigma} for e in self.events],
        }
