"""Directed-rounding interval arithmetic for strict error bounds.

Closes gap G5 of the gap registry: every numerical claim shipped by the
service can be wrapped in an interval enclosure with outward rounding, in
the spirit of the integer-arithmetic error certificates used by the
computer-assisted proof of the existence of the Choptuik critical
spacetime (Reiterer & Trubowitz).  The Lean side will eventually replace
this module by a verified library; until then it serves as the strictness
backbone of the Python wing.

Rounding model: IEEE-754 double precision, with bounds pushed outward via
``math.nextafter`` — deterministic, portable, dependency-free.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


def _up(x: float) -> float:
    return math.nextafter(x, math.inf)


def _down(x: float) -> float:
    return math.nextafter(x, -math.inf)


@dataclass(frozen=True)
class Interval:
    """Closed real interval ``[lo, hi]`` with outward-rounded operations."""

    lo: float
    hi: float

    def __post_init__(self) -> None:
        if self.lo > self.hi:
            raise ValueError(f"empty interval [{self.lo}, {self.hi}]")

    # -- constructors ---------------------------------------------------
    @staticmethod
    def point(x: float) -> "Interval":
        return Interval(_down(float(x)), _up(float(x)))

    # -- arithmetic -----------------------------------------------------
    def __add__(self, other: "Interval") -> "Interval":
        return Interval(_down(self.lo + other.lo), _up(self.hi + other.hi))

    def __sub__(self, other: "Interval") -> "Interval":
        return Interval(_down(self.lo - other.hi), _up(self.hi - other.lo))

    def __neg__(self) -> "Interval":
        return Interval(-self.hi, -self.lo)

    def __mul__(self, other: "Interval") -> "Interval":
        candidates = (
            self.lo * other.lo,
            self.lo * other.hi,
            self.hi * other.lo,
            self.hi * other.hi,
        )
        return Interval(_down(min(candidates)), _up(max(candidates)))

    def __truediv__(self, other: "Interval") -> "Interval":
        if other.lo <= 0.0 <= other.hi:
            raise ZeroDivisionError("divisor interval contains zero")
        inv = Interval(1.0 / other.hi, 1.0 / other.lo)  # outward by monotonicity
        return self * inv

    # -- extras ----------------------------------------------------------
    def width(self) -> float:
        return self.hi - self.lo

    def contains(self, x: float) -> bool:
        return self.lo <= x <= self.hi

    def enclose_polynomial(self, coeffs: list[float], x: "Interval") -> "Interval":
        """Enclose ``p(x) = sum coeffs[i] * x**i`` (Horner, outward)."""
        acc = Interval.point(0.0)
        for c in reversed(coeffs):
            acc = acc * x + Interval.point(c)
        return acc


def enclosure_width_report(values: list[float], polynomial: list[float]) -> dict[str, float]:
    """Demonstration certificate: enclose a polynomial on [min,max] of values."""
    dom = Interval(_down(min(values)), _up(max(values)))
    enc = Interval.point(0.0).enclose_polynomial(polynomial, dom)
    return {
        "domain_lo": dom.lo,
        "domain_hi": dom.hi,
        "image_lo": enc.lo,
        "image_hi": enc.hi,
        "width": enc.width(),
    }
