#!/usr/bin/env python3
"""Create the hash-bound digital print-candidate report for MM-ORG-027."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
REPORT_PATHS = [
    "validation/parametric-source-report.json",
    "validation/mesh-generation-report.json",
    "validation/interface-report.json",
    "reports/csv-import.json",
    "reports/live-batch-preview.json",
    "reports/nesting-layout.json",
    "validation/optimization-report.json",
    "validation/fdm-mesh-smooth-carrier-print-six.json",
    "validation/fdm-mesh-label-cap-01-a-e.json",
    "validation/fdm-mesh-label-cap-02-f-j.json",
    "validation/fdm-mesh-label-cap-03-k-o.json",
    "validation/fdm-mesh-label-cap-04-p-t.json",
    "validation/fdm-mesh-label-cap-05-u-z.json",
    "validation/fdm-mesh-label-cap-06-jazz.json",
    "validation/fdm-mesh-cap-slot-gauge.json",
    "validation/fdm-mesh-carrier-fit-key.json",
    "validation/fdm-3mf-selected.json",
    "validation/slicer-selected-020.json",
    "validation/approvals-through-slicer.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {
        "id": check_id,
        "status": "PASS" if passed else "FAIL",
        "required": True,
        "message": message,
        "metrics": metrics or {},
        "evidence": [],
    }


def main() -> None:
    paths = [ROOT / item for item in REPORT_PATHS]
    loaded = {item: json.loads((ROOT / item).read_text(encoding="utf-8")) for item in REPORT_PATHS}
    checks = [check(f"report:{item}", report.get("status") == "PASS", f"{item} reports PASS") for item, report in loaded.items()]

    slicer = loaded["validation/slicer-selected-020.json"]
    gcode_reports = list(slicer.get("gcode_reports", {}).values())
    gcode = gcode_reports[0] if len(gcode_reports) == 1 else {}
    gcode_metrics = gcode.get("metrics", {})
    native_warnings = [
        item.get("warning_message", "")
        for item in slicer.get("native_result", {}).get("sliced_plates", [])
        if item.get("warning_message", "").strip()
    ]
    interface_metrics = loaded["validation/interface-report.json"]["metrics"]
    interfaces = interface_metrics["interfaces"]
    caps = [interfaces[f"label-cap-{index:02d}-{slug}"] for index, slug in enumerate(["a-e", "f-j", "k-o", "p-t", "u-z", "jazz"], 1)]
    csv_metrics = loaded["reports/csv-import.json"]["metrics"]
    proof_metrics = loaded["reports/live-batch-preview.json"]["metrics"]
    nesting_metrics = loaded["reports/nesting-layout.json"]["metrics"]
    optimization = loaded["validation/optimization-report.json"]["metrics"]

    checks.extend([
        check("gcode-report", len(gcode_reports) == 1 and gcode.get("status") == "PASS", "Exactly one temporary G-code analysis reports PASS"),
        check("expected-height", gcode_metrics.get("layers_from_comments") == 12, "2.4 mm maximum part height slices as twelve layers at 0.20 mm"),
        check("native-slicer-warnings", not native_warnings and not gcode_metrics.get("warnings", []), "Selected exact slice contains no native or parser warnings", {"native_warnings": native_warnings, "parser_warnings": gcode_metrics.get("warnings", [])}),
        check("one-tool", gcode_metrics.get("tools_seen") == [0] and gcode_metrics.get("tool_changes") == 0, "Selected build uses one tool and no tool changes"),
        check("selected-protected-contact", interfaces["smooth-carrier"].get("record_contact_surface") == "continuous" and not interfaces["smooth-carrier"].get("windowed"), "Manufacturing carrier retains the continuous protected sleeve-facing surface"),
        check("carrier-envelope", interfaces["smooth-carrier"].get("outer_dimensions_mm") == [230.0, 35.0, 1.6], "Carrier remains within the 235 × 105 × 5 mm single-part legacy envelope"),
        check("nominal-fit", all(cap.get("slot_width_mm") == 1.9 for cap in caps) and interfaces["carrier-fit-key"].get("thickness_mm") == 1.6, "All caps retain 0.30 mm total nominal clearance over the 1.60 mm carrier"),
        check("coupon-bracket", interfaces["cap-slot-gauge"].get("candidate_slot_widths_mm") == [1.8, 1.9, 2.0] and interfaces["carrier-fit-key"].get("thickness_mm") == 1.6, "Coupon brackets the nominal cap slot and exactly reproduces carrier thickness"),
        check("csv-batch", len(csv_metrics.get("labels", [])) == 6 and csv_metrics.get("labels") == interface_metrics.get("labels"), "CSV import and CAD retain the same six normalized labels and tab positions"),
        check("font-identity", csv_metrics.get("font_id") == proof_metrics.get("font_id") == interface_metrics.get("font_record", {}).get("font_id") == "MM-GRID-5X7-v1", "CSV import, exact proof and CAD retain repository-owned glyph identity"),
        check("exact-label-proof", proof_metrics.get("labels") == [item.get("normalized_label") for item in csv_metrics.get("labels", [])], "Exact SVG proof and imported batch retain identical normalized labels"),
        check("printable-pixels", proof_metrics.get("minimum_pixel_width_mm", 0) >= 0.8 and min(cap.get("layout", {}).get("pixel_width_mm", 0) for cap in caps) >= 0.8, "Exact proof and CAD exceed the 0.8 mm minimum glyph-pixel width"),
        check("protected-text-backing", min(cap.get("minimum_backing_mm", 0) for cap in caps) >= 1.8 - 1e-9 and min(cap.get("text_to_slot_margin_mm", 0) for cap in caps) >= 2.0, "Every cap retains at least 1.8 mm backing and 2.0 mm text-to-slot margin"),
        check("nested-build", nesting_metrics.get("object_count") == 14 and loaded["reports/nesting-layout.json"]["checks"][0].get("metrics", {}).get("collisions") == [], "Six carriers, six caps and two coupons form a collision-free fourteen-object build"),
        check("optimization-selection", optimization.get("selected_variant") == "smooth-020" and optimization.get("feasible_variants") == 1 and optimization.get("pareto_variants") == ["smooth-020"], "Smooth 0.20 mm is the sole feasible Pareto variant"),
        check("physical-gates-deferred", True, "Fit, snag, flatness, legibility, corner-lift and cycle tests remain user-owned"),
    ])
    output = {
        "schema_version": "1.0",
        "tool": "MM-ORG-027-finalize-digital-candidate",
        "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "draft",
        "inputs": [record(path) for path in paths],
        "checks": checks,
        "metrics": {
            "labels": 6,
            "unique_selected_meshes": 9,
            "selected_objects": 14,
            "layers": gcode_metrics.get("layers_from_comments"),
            "slicer_estimate_seconds": gcode_metrics.get("slicer_metadata_time_s"),
            "extruded_volume_mm3": gcode_metrics.get("extruded_volume_mm3"),
            "positive_extrusion_mm": gcode_metrics.get("positive_extrusion_total_mm"),
            "peak_flow_mm3_s": gcode_metrics.get("peak_flow_mm3_s"),
            "tools_seen": gcode_metrics.get("tools_seen", []),
            "font_id": proof_metrics.get("font_id"),
            "selected_variant": optimization.get("selected_variant"),
            "geometric_reduction_vs_legacy_percent": optimization.get("geometric_reduction_vs_legacy_percent"),
            "physical_validation": "DEFERRED",
            "release_state": "DRAFT_DIGITAL_PRINT_CANDIDATE",
        },
        "limitations": [
            "The nominal 1.9 mm cap slot is a digital candidate; print the included coupon pair before the full set.",
            "Use only between protective outer sleeves; this is not archival protection and must not contact bare records.",
            "The exact SVG proves CAD/source identity, not printed contrast, customer approval or content rights.",
            "Headless slicing does not replace final layer preview or a physical print.",
            "Snagging, edge feel, corner lift, racking, label retention, 250 carrier cycles and 500 retrieval cycles remain untested.",
            "Commercial release and customer-specific label approval remain separate human gates.",
            "No G-code was retained and no printer upload or print-start action was performed.",
        ],
        "required_capabilities": [],
    }
    path = ROOT / "validation/print-candidate-report.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "output": str(path), "metrics": output["metrics"]}, indent=2))
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
