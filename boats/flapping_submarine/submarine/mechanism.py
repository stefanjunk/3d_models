"""Kinematics of the slotted-rocker tail drive.

Motor shaft axis = X at (y=0, z=0).  Rocker pivot axis is parallel to X at
(y=0, z=+offset).  The crank pin rotates in the YZ plane around the shaft;
the pin carries a mushroom head sliding inside a straight radial slot of the
rocker.  Everything is computed in the YZ plane.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .config import SubmarineConfig


@dataclass(frozen=True)
class RockerSolution:
    pivot_z: float
    pin_r_min: float  # min distance pivot -> crank pin
    pin_r_max: float
    slot_r_start: float
    slot_r_end: float
    sweep_deg: float  # total fin sweep (peak-to-peak) of the rocker
    tip_sweep_mm: float


def solve_rocker(cfg: SubmarineConfig) -> RockerSolution:
    r = cfg.crank_r
    d = cfg.rocker_offset_z
    if d <= r:
        raise ValueError("rocker pivot must lie outside the crank circle")
    r_min = d - r
    r_max = d + r
    margin = cfg.crank_pin_d / 2 + 1.0
    slot_start = r_min - margin
    slot_end = r_max + margin
    # rocker swing: tangent from the pivot to the crank circle
    half_swing = math.degrees(math.asin(r / d))
    sweep = 2 * half_swing
    tip_sweep = 2 * cfg.rocker_arm_tip_r * math.sin(math.radians(half_swing))
    return RockerSolution(
        pivot_z=d,
        pin_r_min=r_min,
        pin_r_max=r_max,
        slot_r_start=slot_start,
        slot_r_end=slot_end,
        sweep_deg=sweep,
        tip_sweep_mm=tip_sweep,
    )


def validate_rocker(cfg: SubmarineConfig) -> list[str]:
    """Return a list of problems (empty = ok)."""
    problems: list[str] = []
    sol = solve_rocker(cfg)
    if sol.sweep_deg < 15.0:
        problems.append(
            f"fin sweep too small: {sol.sweep_deg:.1f} deg (< 15)"
        )
    if sol.slot_r_start < cfg.crank_pin_d / 2 + 2.0:
        problems.append("slot start too close to the pivot (weak hub)")
    slot_len = sol.slot_r_end - sol.slot_r_start
    if slot_len < 2 * cfg.crank_r + cfg.crank_pin_d:
        problems.append("slot too short for crank excursion")
    # fin tip must stay below hull top at full sweep
    tip_z_min = -sol.tip_sweep_mm / 2 - 5.0
    if tip_z_min > -cfg.capsule_od / 4:
        problems.append("fin tip sweep suspiciously small vs hull size")
    return problems
