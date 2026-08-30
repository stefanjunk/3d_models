"""Generate process-matched DRAFT fit coupons for 0.1.0-parametric.3."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import component_parameters as P
from build_component_rover import box, cyl, cut_many, fuse, slot_xy, slot_xz_through_y

OUT_ROOT = HERE / "coupons" / f"v{P.CANDIDATE}"
STEP_DIR = OUT_ROOT / "master-step"
MESH_DIR = OUT_ROOT / "validation-mesh"
REPORT = ROOT / "validation" / f"v{P.CANDIDATE}" / "coupon-build-report.json"


def motor_bracket_coupon() -> cq.Shape:
    shape = box(-22, 22, -8, 8, 0, 7)
    cutters = [
        slot_xy(x, 0.0, P.MOTOR_BRACKET_AXIAL_SLOT_MM, P.M3_SLOT_WIDTH_MM, "y", -1, 8)
        for x in (-P.MOTOR_BRACKET_BASE_PITCH_MM, 0.0, P.MOTOR_BRACKET_BASE_PITCH_MM)
    ]
    return cut_many(shape, cutters)


def battery_width_coupon() -> cq.Shape:
    half_y = P.BATTERY_INNER_MM[1] / 2.0 + P.BATTERY_WALL_MM
    return fuse(
        [
            box(0, 14, -half_y, half_y, 0, P.BATTERY_FLOOR_MM),
            box(0, 14, -half_y, -half_y + P.BATTERY_WALL_MM, 0, 30),
            box(0, 14, half_y - P.BATTERY_WALL_MM, half_y, 0, 30),
        ]
    )


def camera_width_coupon() -> cq.Shape:
    positives = [
        box(0, 16, -13.5, 13.5, 0, 3),
        box(0, 16, -13.5, -10.5, 0, 24),
        box(0, 16, 10.5, 13.5, 0, 24),
    ]
    shape = fuse(positives)
    slot = slot_xz_through_y(
        8.0,
        12.0,
        P.CAMERA_MOUNT_SLOT_LENGTH_MM,
        P.CAMERA_MOUNT_HOLE_MM_PROVISIONAL,
        -15,
        15,
    )
    return shape.cut(slot)


def driver_footprint_coupon() -> cq.Shape:
    shape = box(0, 72, 0, 58, 0, 3)
    cutters = [
        slot_xy(8.0, 7.06, 8.0, P.M3_SLOT_WIDTH_MM, "x", -1, 4),
        slot_xy(15.62, 50.24, 8.0, P.M3_SLOT_WIDTH_MM, "x", -1, 4),
    ]
    for x in (32.0, 62.0):
        for y in (5.0, 53.0):
            cutters.append(slot_xy(x, y, 10.0, 3.2, "x", -1, 4))
    return cut_many(shape, cutters)


def tx800_footprint_coupon() -> cq.Shape:
    shape = box(-17, 17, -17, 17, 0, 3)
    cutters = [
        cyl((x, y, -1), (x, y, 4), P.M3_CLEARANCE_MM / 2.0)
        for x in (-10.0, 10.0)
        for y in (-10.0, 10.0)
    ]
    return cut_many(shape, cutters)


def xt60_panel_coupon() -> cq.Shape:
    shape = box(-25, 25, -16, 16, 0, 4)
    cut_x, cut_y = P.XT60_PANEL_CUTOUT_MM_PROVISIONAL
    cutters = [box(-cut_x / 2, cut_x / 2, -cut_y / 2, cut_y / 2, -1, 5)]
    for x in (-P.XT60_MOUNT_PITCH_MM_PROVISIONAL / 2.0, P.XT60_MOUNT_PITCH_MM_PROVISIONAL / 2.0):
        cutters.append(cyl((x, 0, -1), (x, 0, 5), 1.4))
    return cut_many(shape, cutters)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    STEP_DIR.mkdir(parents=True, exist_ok=True)
    MESH_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    coupons = {
        "motor-bracket-slot": (motor_bracket_coupon(), "Pololu 1995 three-hole base and axial slot travel"),
        "battery-width": (battery_width_coupon(), "Gens ace 44 mm width plus 1 mm nominal clearance per side"),
        "camera-width": (camera_width_coupon(), "RunCam 19 mm width plus side-screw slot"),
        "driver-footprint": (driver_footprint_coupon(), "Pololu 2507 diagonal two-hole relation and restraint slots"),
        "tx800-footprint": (tx800_footprint_coupon(), "SpeedyBee TX800 20 x 20 mm M3 pattern"),
        "xt60-panel": (xt60_panel_coupon(), "AMASS XT60E-M provisional panel cutout and mounting pitch"),
    }
    rows = []
    status = "PASS"
    for name, (shape, purpose) in coupons.items():
        if not shape.isValid() or len(shape.Solids()) != 1 or shape.Volume() <= 0:
            status = "FAIL"
        bb = shape.BoundingBox()
        oriented = shape.translate((-bb.xmin, -bb.ymin, -bb.zmin))
        step = STEP_DIR / f"DRAFT-{name}-coupon.step"
        stl = MESH_DIR / f"DRAFT-{name}-coupon.stl"
        cq.exporters.export(shape, str(step), exportType="STEP")
        cq.exporters.export(
            oriented,
            str(stl),
            exportType="STL",
            tolerance=P.STL_LINEAR_TOLERANCE_MM,
            angularTolerance=P.STL_ANGULAR_TOLERANCE_RAD,
        )
        rows.append(
            {
                "name": name,
                "purpose": purpose,
                "status": "PASS" if shape.isValid() and len(shape.Solids()) == 1 and shape.Volume() > 0 else "FAIL",
                "bounds_mm": [bb.xlen, bb.ylen, bb.zlen],
                "volume_mm3": shape.Volume(),
                "step": {"path": str(step.relative_to(ROOT)), "sha256": sha256(step), "size_bytes": step.stat().st_size},
                "mesh": {"path": str(stl.relative_to(ROOT)), "sha256": sha256(stl), "size_bytes": stl.stat().st_size},
            }
        )
    report = {
        "schema_version": "1.0",
        "tool": "MM-TOY-003 fit coupon builder",
        "tool_version": "0.1.0",
        "candidate": P.CANDIDATE,
        "status": status,
        "inputs": [
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
            for path in (
                Path(__file__).resolve(),
                HERE / "component_parameters.py",
                HERE / "build_component_rover.py",
            )
        ],
        "coupons": rows,
        "use_rule": "Print in the same material, nozzle, layer height, line width, orientation and dimensional compensation planned for the corresponding full part; record pass/fail against the delivered component.",
        "limitations": [
            "Coupon geometry remains manufacturer-derived until a delivered component is identified and measured.",
            "A coupon PASS qualifies only the tested printer/material/profile and does not approve the complete rover or powered operation.",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "coupons": len(rows)}, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
