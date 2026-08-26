from __future__ import annotations

import itertools
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from .common import ValidationInputError, check, load_data, report, resolve_path
from .gcode import analyze as analyze_gcode
from .geometry import compare as compare_meshes
from .interfaces import validate_contract
from .mesh import audit
from .threemf import validate as validate_3mf


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "case"


def _text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value


def generate_cases(parameters: dict[str, Any], explicit: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    names = sorted(parameters)
    defaults = {name: parameters[name]["default"] for name in names}
    rows: list[tuple[str, dict[str, Any]]] = [("default", dict(defaults))]
    for name in names:
        for bound in ("min", "max"):
            if bound in parameters[name]:
                values = dict(defaults)
                values[name] = parameters[name][bound]
                rows.append((f"{name}-{bound}", values))
    for first_index, first in enumerate(names):
        for second in names[first_index + 1 :]:
            if not all(key in parameters[first] and key in parameters[second] for key in ("min", "max")):
                continue
            for a_bound, b_bound in itertools.product(("min", "max"), repeat=2):
                values = dict(defaults)
                values[first] = parameters[first][a_bound]
                values[second] = parameters[second][b_bound]
                rows.append((f"{first}-{a_bound}__{second}-{b_bound}", values))
    for index, item in enumerate(explicit or []):
        values = dict(defaults)
        values.update(item.get("values", {}))
        rows.append((str(item.get("id", f"explicit-{index + 1}")), values))
    unique = []
    seen = set()
    for case_id, values in rows:
        signature = json.dumps(values, sort_keys=True, separators=(",", ":"))
        if signature in seen:
            continue
        seen.add(signature)
        unique.append({"id": _slug(case_id), "values": values})
    return unique


def run(manifest_path: Path, output_root: Path | None = None, profile: str = "release") -> dict[str, Any]:
    if not manifest_path.is_file():
        return report("run-sweep", [check("sweep-manifest", "FAIL", f"Manifest not found: {manifest_path}")], inputs=[manifest_path], profile=profile)
    try:
        data = load_data(manifest_path)
        if not isinstance(data, dict):
            raise ValidationInputError("sweep manifest root must be an object")
        command = data.get("command")
        if not isinstance(command, list) or not command or not all(isinstance(item, str) for item in command):
            raise ValidationInputError("command must be a non-empty array of strings")
        parameters = data.get("parameters", {})
        if not isinstance(parameters, dict):
            raise ValidationInputError("parameters must be an object")
        for name, spec in parameters.items():
            if not isinstance(spec, dict) or "default" not in spec:
                raise ValidationInputError(f"parameter {name} needs an object with default")
        cases = generate_cases(parameters, data.get("cases"))
        root = output_root or resolve_path(manifest_path.parent, data.get("output_root", "sweep-results"))
        if root.exists() and any(root.iterdir()):
            raise ValidationInputError(f"output root is not empty: {root}")
        root.mkdir(parents=True, exist_ok=True)
        environment_overrides = data.get("environment", {})
        if not isinstance(environment_overrides, dict) or not all(isinstance(key, str) and isinstance(value, str) for key, value in environment_overrides.items()):
            raise ValidationInputError("environment must be a string-to-string object")
    except Exception as exc:
        return report("run-sweep", [check("sweep-manifest", "FAIL", f"{type(exc).__name__}: {exc}")], inputs=[manifest_path], profile=profile)

    case_rows = []
    checks: list[dict[str, Any]] = []
    for case in cases:
        case_dir = root / case["id"]
        if case_dir.exists() and any(case_dir.iterdir()):
            checks.append(check(f"case:{case['id']}", "FAIL", f"Output directory is not empty: {case_dir}"))
            case_rows.append({"id": case["id"], "status": "FAIL", "reason": "non-empty output directory"})
            continue
        case_dir.mkdir(parents=True, exist_ok=True)
        values = {**case["values"], "workdir": str(case_dir.resolve())}
        try:
            rendered_command = [item.format_map(values) for item in command]
        except KeyError as exc:
            checks.append(check(f"case:{case['id']}", "FAIL", f"Unknown command placeholder: {exc}"))
            continue
        environment = os.environ.copy()
        environment.setdefault("PYTHONHASHSEED", "0")
        environment.update(environment_overrides)
        try:
            completed = subprocess.run(
                rendered_command,
                cwd=manifest_path.parent,
                text=True,
                capture_output=True,
                check=False,
                timeout=float(data.get("timeout_seconds", 300)),
                env=environment,
            )
            returncode = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as exc:
            returncode = 124
            stdout = _text(exc.stdout)
            stderr = _text(exc.stderr) + f"\nTimed out after {data.get('timeout_seconds', 300)} seconds"
        except OSError as exc:
            returncode = 127
            stdout = ""
            stderr = f"{type(exc).__name__}: {exc}"
        (case_dir / "command.json").write_text(json.dumps({"command": rendered_command, "values": case["values"]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (case_dir / "stdout.log").write_text(stdout, encoding="utf-8")
        (case_dir / "stderr.log").write_text(stderr, encoding="utf-8")
        validator_rows = []
        case_failed = returncode != 0
        for validator in data.get("validators", []):
            validator_type = validator.get("type")
            if validator_type == "mesh":
                artifact = resolve_path(case_dir, str(validator.get("path", "")))
                result = audit(artifact, validator.get("policy", {}), profile="release")
            elif validator_type == "mesh_compare":
                reference = resolve_path(case_dir, str(validator.get("reference", "")))
                candidate = resolve_path(case_dir, str(validator.get("candidate", "")))
                result = compare_meshes(reference, candidate, validator.get("policy", {}), profile="release")
            elif validator_type == "gcode":
                artifact = resolve_path(case_dir, str(validator.get("path", "")))
                result = analyze_gcode(artifact, validator.get("policy", {}), profile="release")
            elif validator_type == "3mf":
                artifact = resolve_path(case_dir, str(validator.get("path", "")))
                result = validate_3mf(artifact, validator.get("policy", {}), profile="release")
            elif validator_type == "interfaces":
                artifact = resolve_path(case_dir, str(validator.get("path", "")))
                result = validate_contract(artifact, profile="release")
            else:
                result = {"status": "NOT_RUN", "tool": str(validator_type), "checks": [], "message": f"Unsupported validator type {validator_type!r}"}
            validator_rows.append(result)
            if result["status"] != "PASS":
                case_failed = True
        status = "FAIL" if case_failed else "PASS"
        message = f"Command return code {returncode}; {len(validator_rows)} validator(s)"
        checks.append(check(f"case:{case['id']}", status, message, metrics={"returncode": returncode, "values": case["values"]}))
        case_rows.append({"id": case["id"], "status": status, "values": case["values"], "command": rendered_command, "returncode": returncode, "validators": validator_rows})
    return report(
        "run-sweep",
        checks,
        inputs=[manifest_path],
        profile=profile,
        metrics={"output_root": str(root.resolve()), "case_count": len(cases), "environment_overrides": environment_overrides, "cases": case_rows},
        limitations=[
            "The explicitly declared command executes local project code; review the manifest before running it.",
            "Pairwise cases hold all non-selected parameters at defaults and do not prove every higher-order interaction.",
            "The command inherits the caller environment plus recorded overrides; pin the project toolchain separately for reproducible releases.",
        ],
    )
