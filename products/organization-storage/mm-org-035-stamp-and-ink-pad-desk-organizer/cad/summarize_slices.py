#!/usr/bin/env python3
"""Create the hash-bound MM-ORG-035 slicer-preflight report."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.2"
PROCESS = Path("/opt/AnycubicSlicerNext/share/resources/profiles/Anycubic/process/0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle.json")
JOBS = {
    "fit-coupons": {
        "slicer": "validation/slicer-anycubic-petg-coupons-run-002.json",
        "gcode": "validation/gcode-petg-coupons-run-002.json",
        "package": "validation/fdm-3mf-coupons-final.json",
    },
    "full-duo": {
        "slicer": "validation/slicer-anycubic-petg-full-run-002.json",
        "gcode": "validation/gcode-petg-full-run-002.json",
        "package": "validation/fdm-3mf-full-final.json",
    },
}


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
    process = json.loads(PROCESS.read_text())
    checks = [check(
        "supports-disabled",
        str(process.get("enable_support")) == "0" and str(process.get("enforce_support_layers")) == "0",
        "Exact process profile disables generated supports",
        {"process_sha256": sha256(PROCESS)},
    )]
    metrics: dict[str, dict] = {}
    inputs = [record(PROCESS)]
    for job, spec in JOBS.items():
        slicer_path, gcode_path, package_path = (ROOT / spec[key] for key in ["slicer", "gcode", "package"])
        slicer = json.loads(slicer_path.read_text())
        gcode_report = json.loads(gcode_path.read_text())
        package = json.loads(package_path.read_text())
        inputs.extend([record(slicer_path), record(gcode_path), record(package_path)])
        output = next(item for item in slicer["outputs"] if item["relative_path"].endswith(".gcode"))
        output_path = Path(output["path"])
        warnings = [plate.get("warning_message", "") for plate in slicer["native_result"]["sliced_plates"] if plate.get("warning_message")]
        gm = gcode_report["metrics"]
        filament_name = next(profile["name"] for profile in slicer["slicer"]["profiles"] if profile["type"] == "filament")
        checks.extend([
            check(f"{job}:package", package["status"] == "PASS", f"{job} 3MF package passes strict validation"),
            check(f"{job}:slice", slicer["status"] == "PASS" and slicer["native_result"]["return_code"] == 0, f"{job} native slice succeeds"),
            check(f"{job}:native-warning", not warnings, f"{job} has no native slicer warnings", {"warnings": warnings}),
            check(f"{job}:gcode", gcode_report["status"] == "PASS", f"{job} G-code policy passes"),
            check(f"{job}:preserved", output_path.is_file() and sha256(output_path) == output["sha256"], f"{job} exact G-code is preserved", {"sha256": output["sha256"], "size_bytes": output["size_bytes"]}),
            check(f"{job}:single-tool", gm["tools_seen"] == [0] and gm["tool_changes"] == 0, f"{job} uses one tool with no tool changes"),
            check(f"{job}:parser-warnings", not gm["warnings"], f"{job} parser reports no warnings"),
            check(f"{job}:material-profile", "PETG" in filament_name, f"{job} uses the declared PETG filament profile", {"profile": filament_name}),
        ])
        metrics[job] = {
            "material": "PETG",
            "layers": gm["layers_from_comments"],
            "estimate_seconds": gm["slicer_metadata_time_s"],
            "extruded_volume_mm3": gm["extruded_volume_mm3"],
            "density_conversion_g": gm["extruded_volume_mm3"] / 1000 * 1.27,
            "peak_flow_mm3_s": gm["peak_flow_mm3_s"],
            "gcode_path": str(output_path.relative_to(ROOT)),
            "gcode_sha256": output["sha256"],
        }
        inputs.append(record(output_path))
    report = {
        "schema_version": "1.0", "tool": "MM-ORG-035-anycubic-slicer-preflight", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft",
        "inputs": inputs, "checks": checks, "metrics": metrics,
        "limitations": [
            "Density conversions are planning estimates, not scale measurements.",
            "Headless slicing does not replace the human final layer, seam, support, and bed-placement preview.",
            "No printer upload or print-start action was performed.",
        ],
        "required_capabilities": [],
    }
    target = ROOT / "validation/slicer-preflight-report.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": report["status"], "metrics": metrics}, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
