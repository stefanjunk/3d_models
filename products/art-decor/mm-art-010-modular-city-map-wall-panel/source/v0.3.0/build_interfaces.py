#!/usr/bin/env python3
"""Build shared permanent-assembly parts and the four-clearance coupon."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cadquery as cq
from cadquery import exporters

from interface_geometry import (
    PARAMS,
    anchor_head,
    connector_receiver,
    geometric_strain_percent,
    lower_standoff,
    seam_connector,
    socket_receiver,
    upper_hanger,
)


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[1]
EXPORT = PRODUCT / "exports" / "v0.3.0" / "interfaces"
COUPON = PRODUCT / "coupons" / "v0.3.0"
VALIDATION = PRODUCT / "validation" / "v0.3.0" / "interfaces"


def export_shape(shape: cq.Workplane | cq.Compound, stem: Path) -> list[Path]:
    stem.parent.mkdir(parents=True, exist_ok=True)
    outputs = []
    for suffix in (".step", ".stl"):
        path = stem.with_suffix(suffix)
        exporters.export(shape, str(path), tolerance=0.02, angularTolerance=0.08)
        outputs.append(path)
    return outputs


def translated_shapes_for_coupon(clearance: float, row: int) -> list[cq.Shape]:
    """Loose production-orientation parts laid out as one support-free build."""
    y0 = row * 34.0
    shapes: list[cq.Shape] = []
    left = connector_receiver("left", clearance).translate((25.0, y0 + 10.0, 0))
    right = connector_receiver("right", clearance).translate((70.0, y0 + 10.0, 0))
    connector = seam_connector().translate((115.0, y0 + 10.0, 0))
    socket = socket_receiver(clearance).translate((150.0, y0 + 10.0, 0))
    anchor = anchor_head().translate((181.0, y0 + 10.0, 0))
    for item in (left, right, connector, socket, anchor):
        shapes.extend(item.vals())
    return shapes


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    EXPORT.mkdir(parents=True, exist_ok=True)
    COUPON.mkdir(parents=True, exist_ok=True)
    VALIDATION.mkdir(parents=True, exist_ok=True)

    outputs: list[Path] = []
    outputs += export_shape(seam_connector(), EXPORT / "seam-connector-c025")
    outputs += export_shape(anchor_head(), EXPORT / "socket-test-anchor")
    outputs += export_shape(lower_standoff(), EXPORT / "lower-standoff-18mm")
    outputs += export_shape(upper_hanger(), EXPORT / "upper-hanger-18mm")

    coupon_solids: list[cq.Shape] = []
    clearances = PARAMS["connector"]["coupon_clearance_per_side"]
    for row, clearance in enumerate(clearances):
        tag = f"c{int(round(clearance * 100)):02d}"
        outputs += export_shape(
            connector_receiver("left", clearance), COUPON / f"connector-receiver-left-{tag}"
        )
        outputs += export_shape(
            connector_receiver("right", clearance), COUPON / f"connector-receiver-right-{tag}"
        )
        outputs += export_shape(socket_receiver(clearance), COUPON / f"socket-receiver-{tag}")
        coupon_solids.extend(translated_shapes_for_coupon(clearance, row))

    coupon = cq.Compound.makeCompound(coupon_solids)
    outputs += export_shape(coupon, COUPON / "interface-coupon-all-clearances")

    connector_p = PARAMS["connector"]
    socket_p = PARAMS["socket_anchor"]
    report = {
        "schema_version": "1.0",
        "revision": "0.3.0",
        "status": "DIGITAL_PASS_PHYSICAL_NOT_RUN",
        "formula": "epsilon_percent = 100 * 1.5 * t * delta / L^2",
        "connector": {
            "arm_thickness_mm": connector_p["arm_thickness_in_plane"],
            "nominal_deflection_mm": connector_p["barb_nominal_deflection_per_arm"],
            "free_length_mm": connector_p["arm_free_length"],
            "geometric_surface_strain_percent": geometric_strain_percent(
                connector_p["arm_thickness_in_plane"],
                connector_p["barb_nominal_deflection_per_arm"],
                connector_p["arm_free_length"],
            ),
        },
        "socket_detent": {
            "arm_thickness_mm": socket_p["detent_arm_thickness_in_plane"],
            "nominal_deflection_mm": socket_p["detent_nominal_deflection"],
            "free_length_mm": socket_p["detent_arm_length"],
            "geometric_surface_strain_percent": geometric_strain_percent(
                socket_p["detent_arm_thickness_in_plane"],
                socket_p["detent_nominal_deflection"],
                socket_p["detent_arm_length"],
            ),
        },
        "material_allowable": None,
        "claim_boundary": "Geometry-only beam estimate; not a material strength, life, retention-force or wall-load claim.",
        "coupon_clearances_per_side_mm": clearances,
        "provisional_product_clearance_per_side_mm": connector_p[
            "selected_provisional_clearance_per_side"
        ],
        "physical_acceptance": [
            "Print with exact production filament, 0.4 mm nozzle and selected process profile.",
            "Select the smallest clearance that fully inserts once without crack or visible whitening.",
            "Confirm both connector barbs and socket detent seat completely.",
            "Record insertion observation and destructive pull result; no universal force rating is inferred.",
        ],
    }
    report_path = VALIDATION / "interface-calculation.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    outputs.append(report_path)

    manifest = {
        "schema_version": "1.0",
        "revision": "0.3.0",
        "generator": str(Path(__file__).relative_to(PRODUCT)),
        "parameter_source": str((HERE / "interface-parameters.json").relative_to(PRODUCT)),
        "artifacts": [
            {
                "path": str(path.relative_to(PRODUCT)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in sorted(set(outputs))
        ],
    }
    manifest_path = VALIDATION / "interface-build-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "artifacts": len(outputs), "manifest": str(manifest_path)}))


if __name__ == "__main__":
    main()
