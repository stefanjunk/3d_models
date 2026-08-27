from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .common import check, report, sha256_file
from .gcode import analyze as analyze_gcode


SUPPORTED_INPUTS = {".3mf", ".obj", ".stl"}
VERSION_PATTERN = re.compile(r"AnycubicSlicerNext-([^:\s]+):")
LOG_PREFIX = re.compile(r"^\[[^\]]+\]\s+\[[^\]]+\]\s+\[[^\]]+\]\s+")
WRAPPER_EXEC_PATTERN = re.compile(r"^\s*exec\s+(['\"]?)(/[^\s'\"]*AnycubicSlicerNext)\1(?:\s|$)", re.M)


def _resolve_executable(value: str) -> Path | None:
    candidate = Path(value)
    if candidate.is_absolute() or candidate.parent != Path("."):
        return candidate.resolve() if candidate.is_file() and os.access(candidate, os.X_OK) else None
    resolved = shutil.which(value)
    return Path(resolved).resolve() if resolved else None


def _resolve_runtime_binary(launcher: Path) -> Path:
    if launcher.stat().st_size > 65536:
        return launcher
    try:
        match = WRAPPER_EXEC_PATTERN.search(launcher.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return launcher
    if not match:
        return launcher
    candidate = Path(match.group(2))
    return candidate.resolve() if candidate.is_file() and os.access(candidate, os.X_OK) else launcher


def _profile_identity(path: Path, expected_type: str) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, f"profile not found: {path}"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"invalid JSON profile {path}: {exc}"
    if not isinstance(payload, dict):
        return None, f"profile root must be an object: {path}"
    actual_type = payload.get("type")
    if actual_type != expected_type:
        return None, f"expected {expected_type!r} profile, found {actual_type!r}: {path}"
    return {
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
        "type": actual_type,
        "name": payload.get("name"),
        "inherits": payload.get("inherits"),
    }, None


def _diagnostic_text(value: str | bytes | None) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


def _stable_diagnostics(stdout: str | bytes | None, stderr: str | bytes | None) -> list[str]:
    lines: list[str] = []
    for raw in (_diagnostic_text(stdout) + "\n" + _diagnostic_text(stderr)).splitlines():
        line = LOG_PREFIX.sub("", raw).strip()
        if line and line != "Initializing StaticPrintConfigs":
            lines.append(line)
    return lines[-20:]


def _native_result(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, "Anycubic Slicer Next did not write result.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"invalid Anycubic result.json: {exc}"
    if not isinstance(payload, dict):
        return None, "Anycubic result.json root is not an object"
    plates = []
    for plate in payload.get("sliced_plates", []):
        if isinstance(plate, dict):
            plates.append({
                "id": plate.get("id"),
                "triangle_count": plate.get("triangle_count"),
                "warning_message": plate.get("warning_message"),
            })
    stable = {
        "return_code": payload.get("return_code"),
        "error_string": payload.get("error_string"),
        "plate_index": payload.get("plate_index"),
        "sliced_plates": plates,
    }
    return stable, None


def _output_rows(output_dir: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(item for item in output_dir.rglob("*") if item.is_file()):
        rows.append({
            "path": str(path.resolve()),
            "relative_path": path.relative_to(output_dir).as_posix(),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        })
    return rows


def slice_anycubic_next(
    source: Path,
    output_dir: Path,
    *,
    machine_profile: Path | None = None,
    process_profile: Path | None = None,
    filament_profiles: list[Path] | None = None,
    executable: str = "AnycubicSlicerNext",
    plate: int = 0,
    timeout_s: int = 600,
    profile: str = "release",
) -> dict[str, Any]:
    filament_profiles = filament_profiles or []
    checks = []
    inputs = [source]
    resolved_executable = _resolve_executable(executable)

    checks.append(check(
        "slicer-executable",
        "PASS" if resolved_executable else "NOT_RUN",
        f"Anycubic Slicer Next executable: {resolved_executable}" if resolved_executable else f"Anycubic Slicer Next executable not found: {executable}",
    ))
    checks.append(check(
        "source-file",
        "PASS" if source.is_file() else "FAIL",
        f"Slicer input: {source}" if source.is_file() else f"Slicer input not found: {source}",
    ))
    checks.append(check(
        "source-format",
        "PASS" if source.suffix.lower() in SUPPORTED_INPUTS else "FAIL",
        f"Supported slicer input format: {source.suffix.lower()}" if source.suffix.lower() in SUPPORTED_INPUTS else f"Unsupported slicer input format: {source.suffix or '<none>'}",
    ))
    checks.append(check(
        "fresh-output-directory",
        "PASS" if not output_dir.exists() else "FAIL",
        f"Output directory is new: {output_dir}" if not output_dir.exists() else f"Refusing existing output directory: {output_dir}",
    ))
    checks.append(check(
        "plate-index",
        "PASS" if plate >= 0 else "FAIL",
        f"Slice plate selector: {plate}" if plate >= 0 else "Plate selector must be non-negative: {plate}",
    ))
    checks.append(check(
        "timeout",
        "PASS" if timeout_s > 0 else "FAIL",
        f"Slicer timeout: {timeout_s} s" if timeout_s > 0 else "Slicer timeout must be positive",
    ))

    supplied_profiles = machine_profile is not None or process_profile is not None or bool(filament_profiles)
    requires_profiles = source.suffix.lower() != ".3mf"
    complete_profiles = machine_profile is not None and process_profile is not None and bool(filament_profiles)
    profiles_ok = complete_profiles if requires_profiles or supplied_profiles else True
    checks.append(check(
        "profile-set",
        "PASS" if profiles_ok else "FAIL",
        "Exact machine, process, and filament profiles supplied" if complete_profiles else (
            "Using profiles embedded in the 3MF project" if profiles_ok else "Mesh slicing requires machine, process, and at least one filament profile"
        ),
    ))

    profile_rows: list[dict[str, Any]] = []
    for path, expected_type in [
        (machine_profile, "machine"),
        (process_profile, "process"),
        *[(item, "filament") for item in filament_profiles],
    ]:
        if path is None:
            continue
        inputs.append(path)
        identity, error = _profile_identity(path, expected_type)
        checks.append(check(
            f"profile:{expected_type}:{len(profile_rows) + 1}",
            "FAIL" if error else "PASS",
            error or f"Loaded {expected_type} profile: {identity['name']}",
        ))
        if identity:
            profile_rows.append(identity)

    runtime_executable = _resolve_runtime_binary(resolved_executable) if resolved_executable else None
    if resolved_executable:
        inputs.append(resolved_executable)
    if runtime_executable and runtime_executable != resolved_executable:
        inputs.append(runtime_executable)
    if any(item["status"] in {"FAIL", "NOT_RUN"} for item in checks):
        result = report("slice-anycubic-next", checks, inputs=inputs, profile=profile)
        result["slicer"] = {"name": "Anycubic Slicer Next", "version": None, "profiles": profile_rows}
        result["outputs"] = []
        return result

    assert resolved_executable is not None
    with tempfile.TemporaryDirectory(prefix="fdm-anycubic-next-") as temporary:
        temporary_root = Path(temporary)
        isolated_datadir = temporary_root / "datadir"
        environment = os.environ.copy()
        environment.update({
            "XDG_CONFIG_HOME": str(temporary_root / "config"),
            "XDG_CACHE_HOME": str(temporary_root / "cache"),
            "XDG_DATA_HOME": str(temporary_root / "data"),
        })
        try:
            probe = subprocess.run(
                [str(resolved_executable), "--datadir", str(isolated_datadir), "--help"],
                capture_output=True,
                text=True,
                timeout=min(timeout_s, 30),
                check=False,
                env=environment,
                cwd=temporary_root,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            checks.append(check("slicer-version", "NOT_RUN", f"Could not probe Anycubic Slicer Next: {exc}"))
            result = report("slice-anycubic-next", checks, inputs=inputs, profile=profile)
            result["slicer"] = {"name": "Anycubic Slicer Next", "version": None, "profiles": profile_rows}
            result["outputs"] = []
            return result

        probe_text = probe.stdout + "\n" + probe.stderr
        version_match = VERSION_PATTERN.search(probe_text)
        slicer_version = version_match.group(1) if version_match else None
        checks.append(check(
            "slicer-version",
            "PASS" if probe.returncode == 0 and slicer_version else "NOT_RUN",
            f"Anycubic Slicer Next version {slicer_version}" if slicer_version else "Anycubic Slicer Next version could not be determined",
        ))
        if not slicer_version:
            result = report("slice-anycubic-next", checks, inputs=inputs, profile=profile)
            result["slicer"] = {"name": "Anycubic Slicer Next", "version": None, "profiles": profile_rows}
            result["outputs"] = []
            return result

        output_dir.mkdir(parents=True, exist_ok=False)
        command = [str(resolved_executable), "--datadir", str(isolated_datadir)]
        if complete_profiles:
            command.extend(["--load-settings", f"{process_profile};{machine_profile}"])
            command.extend(["--load-filaments", ";".join(str(item) for item in filament_profiles)])
            # This is a boolean switch in tested builds. Supplying "1" is parsed as an input file.
            command.append("--load-defaultfila")
        if source.suffix.lower() != ".3mf":
            command.extend(["--ensure-on-bed", "--arrange", "1"])
        command.extend(["--slice", str(plate), "--outputdir", str(output_dir), str(source)])

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
                env=environment,
                cwd=temporary_root,
            )
            process_error = None
        except subprocess.TimeoutExpired as exc:
            completed = None
            process_error = f"Anycubic Slicer Next timed out after {timeout_s} s"
            diagnostics = _stable_diagnostics(exc.stdout, exc.stderr)
        except OSError as exc:
            completed = None
            process_error = f"Anycubic Slicer Next could not be executed: {exc}"
            diagnostics = []

    if completed is not None:
        diagnostics = _stable_diagnostics(completed.stdout, completed.stderr)
        checks.append(check(
            "slicer-process",
            "PASS" if completed.returncode == 0 else "FAIL",
            f"Anycubic Slicer Next exited with code {completed.returncode}",
            metrics={"return_code": completed.returncode},
        ))
    else:
        checks.append(check("slicer-process", "FAIL", process_error or "Anycubic Slicer Next failed"))

    native, native_error = _native_result(output_dir / "result.json")
    native_ok = native is not None and native.get("return_code") == 0
    checks.append(check(
        "slicer-native-result",
        "PASS" if native_ok else "FAIL",
        "Anycubic result.json reports success" if native_ok else (native_error or f"Anycubic result.json return_code={native.get('return_code') if native else None}"),
    ))

    gcode_files = sorted(output_dir.rglob("*.gcode"))
    checks.append(check(
        "gcode-output",
        "PASS" if gcode_files and all(path.stat().st_size > 0 for path in gcode_files) else "FAIL",
        f"Generated {len(gcode_files)} non-empty G-code file(s)" if gcode_files else "No G-code output was generated",
    ))
    gcode_reports: dict[str, Any] = {}
    for index, gcode in enumerate(gcode_files, start=1):
        analysis = analyze_gcode(gcode, profile=profile)
        relative = gcode.relative_to(output_dir).as_posix()
        gcode_reports[relative] = {
            "status": analysis["status"],
            "metrics": analysis["metrics"],
            "checks": analysis["checks"],
        }
        checks.append(check(
            f"gcode-analysis:{index}",
            analysis["status"],
            f"G-code analysis for {relative}: {analysis['status']}",
        ))
        for detail in analysis["checks"]:
            if detail["status"] != "PASS":
                checks.append(check(
                    f"gcode-detail:{index}:{detail['id']}",
                    detail["status"],
                    f"{relative}: {detail['message']}",
                    required=detail.get("required", True),
                    metrics=detail.get("metrics", {}),
                ))

    result = report(
        "slice-anycubic-next",
        checks,
        inputs=inputs,
        profile=profile,
        metrics={"gcode_files": len(gcode_files)},
        limitations=[
            "Anycubic Slicer Next embeds a wall-clock timestamp and may vary path segmentation or ordering between same-scope runs; neither raw nor normalized byte identity is guaranteed.",
            "Do not normalize or rewrite manufacturing G-code in place; retain each exact hash, compare approved metric tolerances, and use separate path diffs only as regression diagnostics.",
            "Headless slicing does not replace final layer/tool/color preview or physical validation.",
            "This adapter only performs local export; it implements no printer upload or print-start action.",
        ],
    )
    stable_command = ["<AnycubicSlicerNext>", "--datadir", "<isolated-datadir>", *command[3:]]
    result["slicer"] = {
        "name": "Anycubic Slicer Next",
        "version": slicer_version,
        "executable": str(resolved_executable),
        "runtime_executable": str(runtime_executable),
        "profiles": profile_rows,
        "plate": plate,
        "invocation": stable_command,
    }
    result["native_result"] = native
    result["outputs"] = _output_rows(output_dir)
    result["gcode_reports"] = gcode_reports
    if diagnostics and result["status"] != "PASS":
        result["diagnostics"] = diagnostics
    return result
