#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
REPORT_PATHS = [
    "validation/parametric-source-report-run-003.json",
    "validation/mesh-generation-report.json",
    "validation/interface-report.json",
    "reports/optimization-comparison.json",
    "validation/fdm-mesh-rack.json",
    "validation/fdm-mesh-mouth-coupon.json",
    "validation/fdm-3mf-gemstage-six-run-003.json",
    "validation/slicer-anycubic-next-run-003.json",
    "validation/current-approvals-through-slicer.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict:
    try:
        display = str(path.relative_to(ROOT))
    except ValueError:
        display = str(path)
    return {"path": display, "sha256": sha256(path), "size_bytes": path.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def main() -> None:
    loaded = {path: json.loads((ROOT / path).read_text()) for path in REPORT_PATHS}
    checks = [check(f"report:{path}", report["status"] == "PASS", f"{path} reports PASS") for path, report in loaded.items()]
    slicer = loaded["validation/slicer-anycubic-next-run-003.json"]
    gcode_name, gcode_report = next(iter(slicer["gcode_reports"].items()))
    gcode_output = next(item for item in slicer["outputs"] if item["relative_path"].endswith(".gcode"))
    native_output = next(item for item in slicer["outputs"] if item["relative_path"] == "result.json")
    gcode = Path(gcode_output["path"])
    native = Path(native_output["path"])
    metrics = gcode_report["metrics"]
    process_profile = Path("/opt/AnycubicSlicerNext/share/resources/profiles/Anycubic/process/0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle.json")
    process = json.loads(process_profile.read_text())
    checks.extend([
        check("gcode-preserved", gcode.is_file() and sha256(gcode) == gcode_output["sha256"], "Exact G-code is preserved with the adapter-recorded hash", {"sha256": gcode_output["sha256"], "size_bytes": gcode_output["size_bytes"]}),
        check("native-result-preserved", native.is_file() and sha256(native) == native_output["sha256"], "Native result.json is preserved with the adapter-recorded hash"),
        check("layer-consistency", metrics["layers_from_comments"] == metrics["layers_declared"] == 480, "Layer markers and declared layer count agree at 480"),
        check("single-tool", metrics["tools_seen"] == [0] and metrics["tool_changes"] == 0, "The plate uses one tool with no tool changes"),
        check("no-gcode-warnings", not metrics["warnings"], "G-code analysis reports no warnings"),
        check("native-success", slicer["native_result"]["return_code"] == 0 and not slicer["native_result"]["sliced_plates"][0]["warning_message"], "Native slicer result is successful and warning-free"),
        check("supports-disabled", str(process.get("enable_support")) == "0" and str(process.get("enforce_support_layers")) == "0", "Exact process profile disables generated supports", {"process_profile_sha256": sha256(process_profile)}),
        check("bed-margin", loaded["validation/fdm-3mf-gemstage-six-run-003.json"]["metrics"]["objects"][0]["bounds_mm"][0][:2] == [20.0, 20.0], "Rack build item retains the corrected 20 mm bed margin"),
        check("physical-deferred", True, "Real tray fit, loaded spill resistance, one-hand removal, cycles and appearance remain human-controlled"),
    ])
    estimated_mass_g = metrics["extruded_volume_mm3"] / 1000 * 1.24
    report = {
        "schema_version": "1.0", "tool": "MM-ORG-033-finalize-digital-print-candidate", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft",
        "inputs": [record(ROOT / path) for path in REPORT_PATHS] + [record(gcode), record(native), record(process_profile)],
        "checks": checks,
        "metrics": {
            "digital_print_candidate": True, "physical_validation": "DEFERRED", "commercial_release": "BLOCKED",
            "gcode_relative_path": str(gcode.relative_to(ROOT)), "gcode_sha256": gcode_output["sha256"],
            "layers": metrics["layers_from_comments"], "slicer_estimate_seconds": metrics["slicer_metadata_time_s"],
            "extruded_volume_mm3": metrics["extruded_volume_mm3"], "estimated_pla_mass_g_at_1p24": estimated_mass_g,
            "tool_changes": metrics["tool_changes"], "support_generation": "disabled_by_exact_process_profile",
        },
        "limitations": [
            "Headless slice evidence does not replace final layer/seam preview or the human-run print.",
            "The mass is a density conversion from analyzed extrusion volume, not a scale measurement.",
            "Adult stationary craft use only; no child, transport or spill-proof claim.",
            "No printer upload or print-start action was performed.",
        ],
        "required_capabilities": [],
    }
    target = ROOT / "validation/print-candidate-report.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": report["status"], "metrics": report["metrics"]}, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
