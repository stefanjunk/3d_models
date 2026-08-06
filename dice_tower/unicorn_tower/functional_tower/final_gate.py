#!/usr/bin/env python3
"""Aggregate all final digital gates into one machine-readable verdict."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

params=load("parameters.json")
mesh=load("reports/functional_unicorn_dice_tower.mesh.json")
functional=load("reports/functional_validation.json")
self_intersection=load("reports/functional_unicorn_dice_tower.self_intersection.json")
path_check=load("reports/die_path_clearance.json")
fdm=load("reports/functional_unicorn_dice_tower.fdm.json")
fdm_assessment=load("reports/fdm_assessment.json")
previews=load("reports/preview_inspection.json")
source=(ROOT/params["source"]["path"]).resolve()
final=ROOT/"exports/functional_unicorn_dice_tower.stl"
required=[
 "README.md","parameters.json","prepare_source.py","functional_tower.scad",
 "generated_parameters.scad","validate_die_path.scad","validate_function.py",
 "check_self_intersections.py","render_previews.py","actual_preview_geometry.scad",
 "exports/functional_unicorn_dice_tower.stl",
 "previews/functional_unicorn_dice_tower_isometric.png",
 "previews/functional_unicorn_dice_tower_front_minus_y.png",
 "previews/functional_unicorn_dice_tower_back_plus_y.png",
 "previews/functional_unicorn_dice_tower_cutaway_verified_path.png",
]
missing=[p for p in required if not (ROOT/p).is_file()]
checks={
 "source_sha256_unchanged":sha(source)==params["source"]["sha256"],
 "final_sha256_matches_functional_report":sha(final)==functional["actual_final_sha256"],
 "shared_mesh_validation":bool(mesh["passed"]),
 "functional_validation":bool(functional["passed"]),
 "self_intersection_indicator":bool(self_intersection["passed"]),
 "die_path_clearance":bool(path_check["passed"]),
 "shared_fdm_hard_checks":bool(fdm["passed"]),
 "manual_fdm_assessment":bool(fdm_assessment["passed"]),
 "preview_inspection":bool(previews["passed"]),
 "z_min_zero":abs(float(mesh["bounds_xyz_mm"][0][2]))<=1e-6,
 "one_connected_body":int(mesh["body_count"])==1,
 "required_files_present":not missing,
 "no_final_path_collision_artifact":not (ROOT/"diagnostics/final_die_path_collision.stl").exists(),
}
passed=all(checks.values())
summary={
 "verdict":"PASS" if passed else "FAIL",
 "scope":"Digital model, mesh, prescribed 22 mm path, and configured FDM geometry gates. Not physical manufacturing approval.",
 "actual_final_stl":str(final),
 "actual_final_sha256":sha(final),
 "original_source_sha256":sha(source),
 "checks":checks,
 "missing_files":missing,
 "measured_extents_xyz_mm":mesh["extents_xyz_mm"],
 "measured_volume_mm3":mesh["volume_mm3"],
 "supported_die_mm":params["functional_geometry"]["supported_die_max_mm"],
 "remaining_caveats":[
  "No slicer executable was available for layer-preview validation.",
  "A physical PLA test with real 22 mm dice is required before manufacturing approval.",
  "The path result is geometric and does not simulate bounce, rotation, or jamming."
 ],
 "passed":passed,
}
(ROOT/"reports/final_validation_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
print(json.dumps(summary,indent=2))
raise SystemExit(0 if passed else 2)
