"""Preflight acceptance checks before slicing/printing."""

from __future__ import annotations

from dataclasses import dataclass, field

from .buoyancy import BuoyancyReport, ballast_box_capacity_g, keel_capacity_g
from .config import SubmarineConfig


class PreflightError(RuntimeError):
    pass


@dataclass
class PartCheck:
    name: str
    bbox: tuple[float, float, float]
    watertight_expected: bool
    watertight_actual: bool | None = None
    print_note: str = ""


def run_preflight(
    cfg: SubmarineConfig,
    buoyancy: BuoyancyReport,
    mechanism_problems: list[str],
    part_checks: list[PartCheck],
) -> dict:
    problems: list[str] = []
    checks: dict = {}

    checks["wall_vs_nozzle"] = cfg.wall >= 3 * cfg.nozzle
    if not checks["wall_vs_nozzle"]:
        problems.append(f"wall {cfg.wall} too thin for watertight prints (< 3 x nozzle)")

    checks["hinge_clearance"] = cfg.hinge_clearance >= 0.15
    if not checks["hinge_clearance"]:
        problems.append("hinge clearance below 0.15 mm (print-in-place joints may fuse)")

    checks["mechanism"] = not mechanism_problems
    problems.extend(mechanism_problems)

    bed = cfg.print_bed
    bed_problems = []
    for pc in part_checks:
        dims = sorted(pc.bbox, reverse=True)
        if dims[0] > bed[0] or dims[1] > bed[1] or dims[2] > bed[2]:
            bed_problems.append(f"{pc.name}: {pc.bbox} exceeds bed {bed}")
    checks["bed_fit"] = not bed_problems
    problems.extend(bed_problems)

    for pc in part_checks:
        if pc.watertight_expected and pc.watertight_actual is False:
            problems.append(f"{pc.name}: mesh not watertight (hull leak)")
    checks["watertight_meshes"] = not any(
        pc.watertight_expected and pc.watertight_actual is False for pc in part_checks
    )

    capacity = keel_capacity_g(cfg) + ballast_box_capacity_g(cfg)
    checks["ballast_capacity"] = buoyancy.required_ballast_g <= capacity * 1.05
    if not checks["ballast_capacity"]:
        problems.append(
            f"required ballast {buoyancy.required_ballast_g:.0f} g exceeds "
            f"keel+box capacity {capacity:.0f} g"
        )

    checks["floats_at_all"] = buoyancy.dry_mass_g < buoyancy.displacement_mid_bladder_ml
    if not checks["floats_at_all"]:
        problems.append("dry mass exceeds displacement; submarine cannot float")

    checks["bladder_range"] = buoyancy.bladder_range_g >= 4.0
    if not checks["bladder_range"]:
        problems.append(
            f"bladder trim range {buoyancy.bladder_range_g:.1f} g too small (< 4 g)"
        )

    report = {
        "pass": not problems,
        "checks": checks,
        "problems": problems,
    }
    if problems:
        raise PreflightError("; ".join(problems))
    return report
