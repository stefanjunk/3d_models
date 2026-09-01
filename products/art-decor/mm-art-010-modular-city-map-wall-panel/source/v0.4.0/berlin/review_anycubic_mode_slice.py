#!/usr/bin/env python3
"""Review one exact Anycubic mode slice without modifying manufacturing G-code."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter-report", type=Path, required=True)
    parser.add_argument("--gcode", type=Path, required=True)
    parser.add_argument("--project-3mf", type=Path, required=True)
    parser.add_argument("--mode", choices=("boundary-crop", "context-outline"), required=True)
    parser.add_argument("--half", choices=("left", "right"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-tools", default="0,1,2,3")
    parser.add_argument("--expected-tool-changes", type=int, default=3)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing report: {args.output}")
    required = [args.adapter_report, args.gcode, args.project_3mf]
    missing = [str(path) for path in required if not path.is_file() or path.stat().st_size == 0]
    if missing:
        raise SystemExit(f"missing or empty input(s): {missing}")

    adapter = json.loads(args.adapter_report.read_text())
    lines = args.gcode.read_text(errors="replace").splitlines()
    declared_header = {
        int(match.group(1))
        for line in lines
        if (match := re.search(r"total layer number:\s*(\d+)", line, re.IGNORECASE))
    }
    declared_summary = {
        int(match.group(1))
        for line in lines
        if (match := re.search(r"total layers count\s*=\s*(\d+)", line, re.IGNORECASE))
    }
    canonical_z = []
    supplemental_layer_comments = 0
    tools = {0}
    tool_changes = 0
    current_tool = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.upper() == ";LAYER_CHANGE":
            z_value = None
            for candidate in lines[index + 1 : index + 8]:
                if candidate.startswith(";Z:"):
                    z_value = float(candidate[3:])
                    break
            canonical_z.append(z_value)
        elif stripped.upper().startswith("; LAYER "):
            supplemental_layer_comments += 1
        command = stripped.split(";", 1)[0].strip().upper()
        if re.fullmatch(r"T\d+", command):
            next_tool = int(command[1:])
            tools.add(next_tool)
            if next_tool != current_tool:
                tool_changes += 1
                current_tool = next_tool

    expected_tools = {int(value) for value in args.expected_tools.split(",") if value.strip()}
    canonical_count = len(canonical_z)
    unique_z_count = len(set(canonical_z))
    declared = next(iter(declared_header)) if len(declared_header) == 1 else None
    native_result = adapter.get("native_result", {})
    checks = {
        "native_slicer_success": native_result.get("return_code") == 0,
        "project_hash_matches_adapter_source": any(
            item.get("sha256") == sha256(args.project_3mf) for item in adapter.get("inputs", [])
        ),
        "gcode_hash_registered_by_adapter": any(
            output.get("sha256") == sha256(args.gcode) for output in adapter.get("outputs", [])
        ),
        "canonical_layer_markers_match_header": declared is not None and canonical_count == declared,
        "canonical_layer_z_values_unique": canonical_count == unique_z_count,
        "header_and_summary_agree": declared_header == declared_summary and len(declared_header) == 1,
        "expected_tools_seen": tools == expected_tools,
        "expected_tool_changes": tool_changes == args.expected_tool_changes,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    input_hashes = {
        "project_3mf": sha256(args.project_3mf),
        "adapter_report": sha256(args.adapter_report),
        "gcode": sha256(args.gcode),
    }
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.4.0",
        "mode": args.mode,
        "half": args.half,
        "status": status,
        "scope": "native Anycubic project-3MF import, executable layer consistency and four-volume tool routing",
        "inputs": {
            "project_3mf": {"path": str(args.project_3mf.resolve()), "sha256": input_hashes["project_3mf"]},
            "adapter_report": {"path": str(args.adapter_report.resolve()), "sha256": input_hashes["adapter_report"]},
            "gcode": {"path": str(args.gcode.resolve()), "bytes": args.gcode.stat().st_size, "sha256": input_hashes["gcode"]},
        },
        "input_hashes": input_hashes,
        "checks": checks,
        "metrics": {
            "declared_header_layers": sorted(declared_header),
            "declared_summary_layers": sorted(declared_summary),
            "canonical_layer_change_markers": canonical_count,
            "canonical_unique_z_values": unique_z_count,
            "supplemental_layer_comments": supplemental_layer_comments,
            "tools_seen": sorted(tools),
            "tool_changes": tool_changes,
        },
        "adapter_observation": {
            "status": adapter.get("status"),
            "generic_analyzer_layer_count": adapter.get("metrics", {}).get("layer_count"),
            "interpretation": "Only the canonical executable markers and native result are used here; supplemental comments are reported separately and the G-code is unchanged.",
        },
        "limitations": [
            "This digital review does not approve physical ACE slot identity, purge sufficiency, seam appearance or print quality.",
            "Final color/tool and wipe-tower inspection remains a human GUI gate.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": status, "report": str(args.output), "metrics": report["metrics"]}))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
