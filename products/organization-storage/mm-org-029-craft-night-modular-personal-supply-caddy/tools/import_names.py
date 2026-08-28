#!/usr/bin/env python3
"""Validate a names CSV and emit a hash-bound normalized CraftOrbit batch."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cad"))
from gridfont import FONT_ID, layout, normalize_text  # noqa: E402


def sha256(target: Path) -> str:
    return hashlib.sha256(target.read_bytes()).hexdigest()


def record(target: Path) -> dict:
    return {"path": str(target.relative_to(ROOT)), "sha256": sha256(target), "size_bytes": target.stat().st_size}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, default=ROOT / "config/model-parameters.json")
    parser.add_argument("--csv", type=Path, default=ROOT / "config/names.csv")
    parser.add_argument("--json-out", type=Path, default=ROOT / "config/name-batch.json")
    parser.add_argument("--report-out", type=Path, default=ROOT / "reports/csv-import.json")
    args = parser.parse_args()
    parameters = json.loads(args.parameters.read_text(encoding="utf-8"))
    batch_p = parameters["batch"]
    plate_p = parameters["nameplate"]
    rows = []
    with args.csv.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["name"]:
            raise ValueError("CSV header must be exactly: name")
        for index, row in enumerate(reader, 1):
            name = normalize_text(row["name"], batch_p["allowed_characters"], batch_p["maximum_characters_after_transliteration"])
            glyph_layout = layout(name, plate_p["text_available_width_mm"], plate_p["text_height_mm"], plate_p["maximum_pixel_pitch_mm"], plate_p["minimum_pixel_width_mm"])
            rows.append({"index": index, "source_name": row["name"], "normalized_name": name, "layout": glyph_layout})
    if len(rows) != batch_p["maximum_names"] or len({row["normalized_name"] for row in rows}) != len(rows):
        raise ValueError("default batch must contain four unique names")
    batch = {"schema_version": "1.0", "project": parameters["project"]["id"], "revision": parameters["project"]["revision"], "font_id": FONT_ID, "source_csv": record(args.csv), "names": rows}
    args.json_out.write_text(json.dumps(batch, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checks = [
        {"id": "name-count", "status": "PASS", "required": True, "message": "Imported four unique participant names", "metrics": {"count": len(rows)}, "evidence": []},
        {"id": "font-identity", "status": "PASS", "required": True, "message": "All names use the repository-owned glyph source", "metrics": {"font_id": FONT_ID}, "evidence": []},
        {"id": "minimum-pixel", "status": "PASS", "required": True, "message": "Every name meets the configured printable pixel minimum", "metrics": {"minimum_mm": min(row["layout"]["pixel_width_mm"] for row in rows)}, "evidence": []}
    ]
    report = {"schema_version": "1.0", "tool": "MM-ORG-029-csv-name-import", "tool_version": parameters["project"]["revision"], "status": "PASS", "profile": "draft", "inputs": [record(args.parameters), record(args.csv), record(ROOT / "cad/gridfont.py")], "checks": checks, "metrics": {"font_id": FONT_ID, "names": rows, "batch_json_sha256": sha256(args.json_out)}, "limitations": ["Customer names still require exact proof and content approval before manufacture."], "required_capabilities": []}
    args.report_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "names": len(rows), "batch": str(args.json_out)}, indent=2))


if __name__ == "__main__":
    main()
