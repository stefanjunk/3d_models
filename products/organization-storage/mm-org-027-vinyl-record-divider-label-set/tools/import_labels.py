#!/usr/bin/env python3
"""Validate a customer CSV label batch and emit hash-bound normalized JSON."""
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path) -> dict:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def parse_rows(csv_path: Path, parameters: dict) -> list[dict]:
    batch = parameters["batch"]
    cap = parameters["label_cap"]
    rows = []
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["label", "tab_position"]:
            raise ValueError("CSV header must be exactly: label,tab_position")
        for index, row in enumerate(reader, 1):
            label = normalize_text(row["label"], batch["allowed_characters"], batch["maximum_characters_after_transliteration"])
            position = row["tab_position"].strip().lower()
            if position not in batch["allowed_tab_positions"]:
                raise ValueError(f"row {index}: unsupported tab_position {position!r}")
            data = layout(label, cap["width_mm"] - 2.0 * cap["text_margin_x_mm"], cap["text_height_mm"], cap["maximum_pixel_pitch_mm"], cap["minimum_pixel_width_mm"])
            rows.append({"index": index, "source_label": row["label"], "normalized_label": label, "tab_position": position, "slot_center_x_mm": cap["tab_offsets_x_mm"][position], "layout": data})
    if not rows or len(rows) > batch["maximum_labels"]:
        raise ValueError(f"CSV must contain 1 to {batch['maximum_labels']} labels")
    if len({item["normalized_label"] for item in rows}) != len(rows):
        raise ValueError("normalized labels must be unique")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, default=ROOT / "config/model-parameters.json")
    parser.add_argument("--csv", type=Path, default=ROOT / "config/labels.csv")
    parser.add_argument("--json-out", type=Path, default=ROOT / "config/label-batch.json")
    parser.add_argument("--report-out", type=Path, default=ROOT / "reports/csv-import.json")
    args = parser.parse_args()
    parameters = json.loads(args.parameters.read_text(encoding="utf-8"))
    rows = parse_rows(args.csv, parameters)
    batch = {"schema_version": "1.0", "project": parameters["project"]["id"], "revision": parameters["project"]["revision"], "font_id": FONT_ID, "source_csv": record(args.csv), "labels": rows}
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(batch, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checks = [
        {"id": "label-count", "status": "PASS", "required": True, "message": f"Imported {len(rows)} unique labels", "metrics": {"count": len(rows)}, "evidence": []},
        {"id": "font-identity", "status": "PASS", "required": True, "message": "All labels use the repository-owned glyph source", "metrics": {"font_id": FONT_ID}, "evidence": []},
        {"id": "minimum-pixel", "status": "PASS", "required": True, "message": "Every normalized label meets the configured minimum pixel width", "metrics": {"minimum_mm": min(item["layout"]["pixel_width_mm"] for item in rows)}, "evidence": []},
        {"id": "tab-positions", "status": "PASS", "required": True, "message": "Every tab position is in the declared left/center/right set", "metrics": {}, "evidence": []}
    ]
    report = {"schema_version": "1.0", "tool": "MM-ORG-027-csv-label-import", "tool_version": parameters["project"]["revision"], "status": "PASS", "profile": "draft", "inputs": [record(args.parameters), record(args.csv), record(ROOT / "cad/gridfont.py")], "checks": checks, "metrics": {"font_id": FONT_ID, "labels": rows, "batch_json_sha256": sha256(args.json_out)}, "limitations": ["Customer text still requires an exact proof and rights/content review before manufacture."], "required_capabilities": []}
    args.report_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "labels": len(rows), "json": str(args.json_out), "report": str(args.report_out)}, indent=2))


if __name__ == "__main__":
    main()
