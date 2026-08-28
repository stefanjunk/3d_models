"""Sparse, deterministic guide curves for the MM-BOAT-003 fish envelope.

The existing pressure hulls remain the immutable functional core.  These
curves define only an additive outer B-Rep fairing and its three shallow
crests.  The concept image is inspiration; dimensions here are authoritative.
"""

from __future__ import annotations

import bisect
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from .config import SubmarineConfig


@dataclass(frozen=True)
class NaturalCubicSpline:
    """One-dimensional natural cubic spline with analytic derivatives."""

    xs: tuple[float, ...]
    ys: tuple[float, ...]
    second_derivatives: tuple[float, ...]

    @classmethod
    def fit(cls, points: Iterable[tuple[float, float]]) -> "NaturalCubicSpline":
        rows = tuple((float(x), float(y)) for x, y in points)
        if len(rows) < 2:
            raise ValueError("a spline needs at least two points")
        xs = tuple(row[0] for row in rows)
        ys = tuple(row[1] for row in rows)
        if any(b <= a for a, b in zip(xs, xs[1:])):
            raise ValueError("spline x coordinates must be strictly increasing")
        n = len(xs)
        if n == 2:
            return cls(xs, ys, (0.0, 0.0))

        h = [xs[i + 1] - xs[i] for i in range(n - 1)]
        lower = [0.0] * (n - 2)
        diagonal = [0.0] * (n - 2)
        upper = [0.0] * (n - 2)
        rhs = [0.0] * (n - 2)
        for j, i in enumerate(range(1, n - 1)):
            lower[j] = h[i - 1]
            diagonal[j] = 2.0 * (h[i - 1] + h[i])
            upper[j] = h[i]
            rhs[j] = 6.0 * (
                (ys[i + 1] - ys[i]) / h[i]
                - (ys[i] - ys[i - 1]) / h[i - 1]
            )

        for i in range(1, n - 2):
            factor = lower[i] / diagonal[i - 1]
            diagonal[i] -= factor * upper[i - 1]
            rhs[i] -= factor * rhs[i - 1]

        interior = [0.0] * (n - 2)
        interior[-1] = rhs[-1] / diagonal[-1]
        for i in range(n - 4, -1, -1):
            interior[i] = (rhs[i] - upper[i] * interior[i + 1]) / diagonal[i]
        return cls(xs, ys, (0.0, *interior, 0.0))

    def _interval(self, x: float) -> tuple[int, float]:
        clamped = min(max(float(x), self.xs[0]), self.xs[-1])
        i = min(max(bisect.bisect_right(self.xs, clamped) - 1, 0), len(self.xs) - 2)
        return i, clamped

    def value(self, x: float) -> float:
        i, x = self._interval(x)
        x0, x1 = self.xs[i], self.xs[i + 1]
        y0, y1 = self.ys[i], self.ys[i + 1]
        m0, m1 = self.second_derivatives[i], self.second_derivatives[i + 1]
        h = x1 - x0
        a, b = (x1 - x) / h, (x - x0) / h
        return (
            a * y0
            + b * y1
            + ((a**3 - a) * m0 + (b**3 - b) * m1) * h * h / 6.0
        )

    def derivative(self, x: float) -> float:
        i, x = self._interval(x)
        x0, x1 = self.xs[i], self.xs[i + 1]
        y0, y1 = self.ys[i], self.ys[i + 1]
        m0, m1 = self.second_derivatives[i], self.second_derivatives[i + 1]
        h = x1 - x0
        a, b = (x1 - x) / h, (x - x0) / h
        return (y1 - y0) / h + h * (
            -(3.0 * a * a - 1.0) * m0 + (3.0 * b * b - 1.0) * m1
        ) / 6.0

    def second(self, x: float) -> float:
        i, x = self._interval(x)
        x0, x1 = self.xs[i], self.xs[i + 1]
        h = x1 - x0
        a, b = (x1 - x) / h, (x - x0) / h
        return a * self.second_derivatives[i] + b * self.second_derivatives[i + 1]


@dataclass(frozen=True)
class RegionProfile:
    name: str
    x0: float
    x1: float
    width: NaturalCubicSpline
    height: NaturalCubicSpline

    @classmethod
    def from_normalized(
        cls,
        name: str,
        x0: float,
        x1: float,
        rows: tuple[tuple[float, float, float], ...],
    ) -> "RegionProfile":
        stations = tuple((x0 + t * (x1 - x0), ry, rz) for t, ry, rz in rows)
        return cls(
            name=name,
            x0=x0,
            x1=x1,
            width=NaturalCubicSpline.fit((x, ry) for x, ry, _ in stations),
            height=NaturalCubicSpline.fit((x, rz) for x, _, rz in stations),
        )

    def radii(self, x: float) -> tuple[float, float]:
        return self.width.value(x), self.height.value(x)

    def sample(self, x0: float, x1: float, count: int) -> list[tuple[float, float, float]]:
        if count < 2:
            raise ValueError("profile sample count must be at least two")
        return [
            (x, *self.radii(x))
            for x in (x0 + i * (x1 - x0) / (count - 1) for i in range(count))
        ]


class FishEnvelopeProfile:
    """Authoritative side/top guide curves for the three hull regions."""

    def __init__(self, cfg: "SubmarineConfig") -> None:
        self.cfg = cfg
        self.nose = RegionProfile.from_normalized(
            "nose",
            -cfg.bladder_protrude,
            cfg.nose_length,
            cfg.fish_nose_profile,
        )
        self.chain = RegionProfile.from_normalized(
            "articulated-chain",
            cfg.nose_length,
            cfg.capsule_start_x,
            cfg.fish_chain_profile,
        )
        self.capsule = RegionProfile.from_normalized(
            "capsule",
            cfg.capsule_start_x + cfg.lug_len,
            cfg.capsule_end_x,
            cfg.fish_capsule_profile,
        )

    def nose_core_radius(self, x: float) -> float:
        tube_r = self.cfg.bladder_tube_od / 2.0 if x <= self.cfg.bladder_inner_len else 0.0
        if x <= 0.0:
            body_r = 0.0
        elif x < self.cfg.nose_dome:
            ratio = min(max(x / self.cfg.nose_dome, 0.0), 1.0)
            body_r = self.cfg.hull_od_front / 2.0 * (
                1.0 - math.sqrt(max(0.0, 1.0 - ratio * ratio))
            )
        else:
            body_r = self.cfg.hull_od_front / 2.0
        return max(tube_r, body_r)

    def core_radius(self, region: str, x: float) -> float:
        if region == "nose":
            return self.nose_core_radius(x)
        if region == "chain":
            return self.cfg.hull_od(x, self.cfg.nose_length, self.cfg.capsule_start_x) / 2.0
        if region == "capsule":
            return self.cfg.capsule_od / 2.0
        raise ValueError(f"unknown fish-envelope region: {region}")

    def radii(self, region: str, x: float) -> tuple[float, float]:
        profile = getattr(self, region)
        ry, rz = profile.radii(x)
        core = self.core_radius(region, x)
        return max(ry, core), max(rz, core)

    def sample(self, region: str, x0: float, x1: float, count: int) -> list[tuple[float, float, float]]:
        if count < 2:
            raise ValueError("fish-envelope sample count must be at least two")
        return [
            (x, *self.radii(region, x))
            for x in (x0 + i * (x1 - x0) / (count - 1) for i in range(count))
        ]

    def report_rows(self, samples_per_region: int = 41) -> list[dict[str, float | str]]:
        rows: list[dict[str, float | str]] = []
        for name, profile in (
            ("nose", self.nose),
            ("chain", self.chain),
            ("capsule", self.capsule),
        ):
            for i in range(samples_per_region):
                x = profile.x0 + i * (profile.x1 - profile.x0) / (samples_per_region - 1)
                ry, rz = self.radii(name, x)
                rows.append(
                    {
                        "region": name,
                        "x_mm": x,
                        "half_width_mm": ry,
                        "half_height_mm": rz,
                        "width_slope": profile.width.derivative(x),
                        "height_slope": profile.height.derivative(x),
                        "width_second": profile.width.second(x),
                        "height_second": profile.height.second(x),
                    }
                )
        return rows
