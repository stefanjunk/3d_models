#!/usr/bin/env python3
"""Review Anycubic multicolor G-code without changing the manufacturing file."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter-report", type=Path, required=True)
    parser.add_argument("--gcode", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-tools", default="0,1,2,3")
    parser.add_argument("--expected-tool-changes", type=int, default=3)
    args = parser.parse_args()

    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing report: {args.output}")
    adapter = json.loads(args.adapter_report.read_text(encoding="utf-8"))
    lines = args.gcode.read_text(encoding="utf-8", errors="replace").splitlines()
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

    expected_tools = {int(item) for item in args.expected_tools.split(",") if item.strip()}
    canonical_count = len(canonical_z)
    unique_z_count = len(set(canonical_z))
    declared = next(iter(declared_header)) if len(declared_header) == 1 else None
    native_result = adapter.get("native_result", {})
    checks = {
        "native_slicer_success": native_result.get("return_code") == 0,
        "gcode_nonempty": args.gcode.is_file() and args.gcode.stat().st_size > 0,
        "canonical_layer_markers_match_header": declared is not None and canonical_count == declared,
        "canonical_layer_z_values_unique": canonical_count == unique_z_count,
        "header_and_summary_agree": declared_header == declared_summary and len(declared_header) == 1,
        "expected_tools_seen": tools == expected_tools,
        "expected_tool_changes": tool_changes == args.expected_tool_changes,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "schema_version": "1.0",
        "status": status,
        "scope": "MM-ART-010 Anycubic project-3MF import and four-volume routing regression",
        "inputs": {
            "adapter_report": {"path": str(args.adapter_report.resolve()), "sha256": sha256(args.adapter_report)},
            "gcode": {"path": str(args.gcode.resolve()), "bytes": args.gcode.stat().st_size, "sha256": sha256(args.gcode)},
        },
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
            "known_false_failure": "The generic analyzer adds canonical ';LAYER_CHANGE' markers and supplemental '; layer #' comments, reporting 42 instead of the 23 executable layers.",
        },
        "limitations": [
            "This regression establishes target-slicer import, non-empty G-code, canonical layer consistency and four tool routes; it does not approve ACE slot identity, purge sufficiency or appearance.",
            "The exact G-code is evidence only and was neither normalized nor rewritten.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
