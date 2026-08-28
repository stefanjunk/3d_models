#!/usr/bin/env python3
"""Create a hash-bound multi-material slicer-preflight report."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.2"
PROCESS = Path("/opt/AnycubicSlicerNext/share/resources/profiles/Anycubic/process/0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle.json")
JOBS = {
    "tpu-gauge": {
        "slicer": "validation/slicer-anycubic-tpu-gauge-run-003.json",
        "gcode": "validation/gcode-tpu-gauge-run-003.json",
        "package": "validation/fdm-3mf-pen-gauge-final.json",
        "material": "TPU",
    },
    "petg-kit": {
        "slicer": "validation/slicer-anycubic-petg-kit-run-003.json",
        "gcode": "validation/gcode-petg-kit-run-003.json",
        "package": "validation/fdm-3mf-petg-kit-final.json",
        "material": "PETG",
    },
    "tpu-kit": {
        "slicer": "validation/slicer-anycubic-tpu-kit-run-003.json",
        "gcode": "validation/gcode-tpu-kit-run-003.json",
        "package": "validation/fdm-3mf-tpu-kit-final.json",
        "material": "TPU",
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
    checks = [check("supports-disabled", str(process.get("enable_support")) == "0" and str(process.get("enforce_support_layers")) == "0", "Exact process profile disables generated supports", {"process_sha256": sha256(PROCESS)})]
    metrics = {}
    inputs = [record(PROCESS)]
    for job, spec in JOBS.items():
        slicer_path, gcode_path, package_path = (ROOT / spec[key] for key in ["slicer", "gcode", "package"])
        slicer = json.loads(slicer_path.read_text())
        gcode_report = json.loads(gcode_path.read_text())
        package = json.loads(package_path.read_text())
        inputs.extend([record(slicer_path), record(gcode_path), record(package_path)])
        output = next(item for item in slicer["outputs"] if item["relative_path"].endswith(".gcode"))
        output_path = Path(output["path"])
        native_warning = slicer["native_result"]["sliced_plates"][0]["warning_message"]
        gm = gcode_report["metrics"]
        filament_name = next(profile["name"] for profile in slicer["slicer"]["profiles"] if profile["type"] == "filament")
        checks.extend([
            check(f"{job}:package", package["status"] == "PASS", f"{job} 3MF package passes strict validation"),
            check(f"{job}:slice", slicer["status"] == "PASS" and slicer["native_result"]["return_code"] == 0, f"{job} native slice succeeds"),
            check(f"{job}:native-warning", native_warning == "", f"{job} has no native slicer warning", {"warning": native_warning}),
            check(f"{job}:gcode", gcode_report["status"] == "PASS", f"{job} G-code policy passes"),
            check(f"{job}:preserved", output_path.is_file() and sha256(output_path) == output["sha256"], f"{job} exact G-code is preserved", {"sha256": output["sha256"], "size_bytes": output["size_bytes"]}),
            check(f"{job}:single-tool", gm["tools_seen"] == [0] and gm["tool_changes"] == 0, f"{job} uses one tool with no tool changes"),
            check(f"{job}:parser-warnings", not gm["warnings"], f"{job} parser reports no warnings"),
            check(f"{job}:material-profile", spec["material"] in filament_name, f"{job} uses the declared {spec['material']} filament profile", {"profile": filament_name}),
        ])
        density = 1.27 if spec["material"] == "PETG" else 1.21
        metrics[job] = {
            "material": spec["material"],
            "layers": gm["layers_from_comments"],
            "estimate_seconds": gm["slicer_metadata_time_s"],
            "extruded_volume_mm3": gm["extruded_volume_mm3"],
            "density_conversion_g": gm["extruded_volume_mm3"] / 1000 * density,
            "peak_flow_mm3_s": gm["peak_flow_mm3_s"],
            "gcode_path": str(output_path.relative_to(ROOT)),
            "gcode_sha256": output["sha256"],
        }
        inputs.append(record(output_path))
    report = {
        "schema_version": "1.0", "tool": "MM-ORG-034-multi-material-slicer-preflight", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft",
        "inputs": inputs, "checks": checks, "metrics": metrics,
        "limitations": [
            "Density conversions are planning estimates, not scale measurements.",
            "Headless slicing does not replace the human final layer, seam, support, and tool preview.",
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
