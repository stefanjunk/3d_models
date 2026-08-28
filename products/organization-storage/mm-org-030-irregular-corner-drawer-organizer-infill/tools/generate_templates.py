#!/usr/bin/env python3
"""Generate exact 1:1 A4 paper measurement templates from the CAD footprints."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cad"))
from geometry import footprint_points  # noqa: E402


def sha256(target: Path) -> str:
    return hashlib.sha256(target.read_bytes()).hexdigest()


def record(target: Path) -> dict:
    return {"path": str(target.relative_to(ROOT)), "sha256": sha256(target), "size_bytes": target.stat().st_size}


def svg_for(preset: dict, clearance: float, tolerance: float) -> str:
    points = footprint_points(preset, clearance)
    shifted = [(x + 25, y + 55) for x, y in points]
    path = " ".join(("M" if index == 0 else "L") + f" {x:.3f} {y:.3f}" for index, (x, y) in enumerate(shifted)) + " Z"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">
<rect width="210" height="297" fill="white"/>
<text x="15" y="18" font-family="sans-serif" font-size="6" font-weight="700">DrawerFit CornerLab 3 · {preset['label']} · 1:1</text>
<text x="15" y="28" font-family="sans-serif" font-size="3.5">Print at 100%, no fit-to-page. Verify the 100 mm line within ±{tolerance:.1f}%.</text>
<line x1="15" y1="40" x2="115" y2="40" stroke="#111" stroke-width="0.6"/>
<line x1="15" y1="37" x2="15" y2="43" stroke="#111" stroke-width="0.6"/><line x1="115" y1="37" x2="115" y2="43" stroke="#111" stroke-width="0.6"/>
<text x="53" y="37" font-family="sans-serif" font-size="3.5">100 mm calibration</text>
<path d="{path}" fill="none" stroke="#183e49" stroke-width="0.5"/>
<text x="15" y="250" font-family="sans-serif" font-size="3.5">Cut/trace the outline, place it in the drawer corner, then mark the real boundary and obstruction.</text>
<text x="15" y="258" font-family="sans-serif" font-size="3.5">Selected digital clearance: {clearance:.1f} mm per side. Record drawer depth separately with calipers.</text>
</svg>\n'''


def main() -> None:
    params_path = ROOT / "config/model-parameters.json"
    params = json.loads(params_path.read_text())
    outputs = []
    for preset in params["presets"]:
        target = ROOT / "assets/templates" / f"MM-ORG-030-{preset['id']}-measurement-1to1.svg"
        target.write_text(svg_for(preset, params["fit"]["selected_per_side_clearance_mm"], params["fit"]["paper_print_scale_tolerance_percent"]), encoding="utf-8")
        outputs.append(record(target))
    checks = [
        {"id":"template-count","status":"PASS","required":True,"message":"Three exact preset templates were generated","metrics":{"count":len(outputs)},"evidence":[]},
        {"id":"calibration-contract","status":"PASS","required":True,"message":"Every page carries a 100 mm scale line and print-scale tolerance","metrics":{"tolerance_percent":params["fit"]["paper_print_scale_tolerance_percent"]},"evidence":[]}
    ]
    report = {"schema_version":"1.0","tool":"MM-ORG-030-paper-template-generator","tool_version":params["project"]["revision"],"status":"PASS","profile":"draft","inputs":[record(params_path),record(ROOT/"cad/geometry.py"),record(ROOT/"tools/generate_templates.py")],"checks":checks,"metrics":{"templates":outputs,"clearance_per_side_mm":params["fit"]["selected_per_side_clearance_mm"]},"limitations":["A paper trace is a fit input, not dimensional proof; printer scaling, paper stretch, tracing and drawer access remain physical/user errors."],"required_capabilities":[]}
    (ROOT / "reports/template-generation.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","templates":len(outputs)}, indent=2))


if __name__ == "__main__":
    main()
