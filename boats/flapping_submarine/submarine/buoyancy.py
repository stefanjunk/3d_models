"""Buoyancy, mass and ballast planning.

All volumes in mm^3, masses in grams, densities in g/cm^3.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .config import SubmarineConfig


def piston_area_mm2(cfg: SubmarineConfig) -> float:
    return math.pi / 4 * cfg.bladder_rod_d ** 2


def bladder_range_g(cfg: SubmarineConfig) -> float:
    """Adjustable displacement range of the bladder in grams of water."""
    return piston_area_mm2(cfg) * cfg.bladder_travel / 1000.0 * cfg.rho_water


def keel_capacity_g(cfg: SubmarineConfig) -> float:
    v = (
        (cfg.keel_l - 2 * cfg.keel_wall - 2)
        * (cfg.keel_w - 2 * cfg.keel_wall - 2)
        * (cfg.keel_h - cfg.keel_wall - 2)
    )
    return v / 1000.0 * cfg.rho_shot_fill


def ballast_box_capacity_g(cfg: SubmarineConfig) -> float:
    v = (
        (cfg.ballast_box_l - 4)
        * (cfg.ballast_box_w - 4)
        * (cfg.ballast_box_h - 3)
    )
    return v / 1000.0 * cfg.rho_coin_fill


@dataclass
class BuoyancyReport:
    displacement_ml: float
    displacement_mid_bladder_ml: float
    print_mass_g: float
    fixed_mass_g: float
    dry_mass_g: float
    required_ballast_g: float
    keel_ballast_g: float
    box_ballast_g: float
    bladder_range_g: float
    submerged_fraction_no_ballast: float

    def to_dict(self) -> dict:
        return {k: round(v, 2) for k, v in self.__dict__.items()}


def compute_buoyancy(
    cfg: SubmarineConfig,
    envelope_mm3: dict[str, float],
    part_mass_mm3: dict[str, float],
) -> BuoyancyReport:
    """envelope_mm3: closed outer volumes of buoyant modules (nose, segments, capsule).
    part_mass_mm3: material volumes of every printed part."""
    v_env = sum(envelope_mm3.values())
    piston_mid = piston_area_mm2(cfg) * cfg.bladder_travel / 2
    v_mid = v_env + piston_mid
    displacement_ml = v_env / 1000.0
    displacement_mid = v_mid / 1000.0

    print_mass = sum(part_mass_mm3.values()) / 1000.0 * cfg.rho_print
    fixed = cfg.motor_mass_g + cfg.battery_mass_g + cfg.misc_mass_g
    dry = print_mass + fixed

    submerged_no_ballast = dry / (v_mid / 1000.0 * cfg.rho_water)
    target_mass = v_mid / 1000.0 * cfg.rho_water * cfg.target_submergence
    required = max(0.0, target_mass - dry)

    keel_cap = keel_capacity_g(cfg)
    box_cap = ballast_box_capacity_g(cfg)
    keel = min(required, keel_cap)
    box = required - keel

    return BuoyancyReport(
        displacement_ml=displacement_ml,
        displacement_mid_bladder_ml=displacement_mid,
        print_mass_g=print_mass,
        fixed_mass_g=fixed,
        dry_mass_g=dry,
        required_ballast_g=required,
        keel_ballast_g=keel,
        box_ballast_g=box,
        bladder_range_g=bladder_range_g(cfg),
        submerged_fraction_no_ballast=submerged_no_ballast,
    )
