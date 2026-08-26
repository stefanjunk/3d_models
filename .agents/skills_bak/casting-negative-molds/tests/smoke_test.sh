#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="${TMPDIR:-/tmp}/casting-negative-molds-smoke"
rm -rf "$TMP"
mkdir -p "$TMP"

python -m py_compile \
  "$ROOT"/scripts/common/*.py \
  "$ROOT"/scripts/cadquery/*.py \
  "$ROOT"/scripts/blender/*.py \
  "$ROOT"/scripts/freecad/*.py

python -m pytest -q "$ROOT/tests"

python "$ROOT/scripts/common/mold_planner.py" \
  "$ROOT/assets/examples/roman-pillar.json" \
  --output "$TMP/roman-plan.md"

python "$ROOT/scripts/cadquery/block_mold.py" \
  --demo roman-pillar --height 40 --output-dir "$TMP/cadquery" \
  --stl-tolerance 0.15

python "$ROOT/scripts/cadquery/detail_coupon.py" \
  --output-dir "$TMP/coupon" --curved --width 80 --length 50 \
  --feature-widths 0.4,0.8,1.2 --feature-depths 0.2,0.4,0.6 \
  --stl-tolerance 0.10

python "$ROOT/scripts/common/mesh_preflight.py" \
  "$TMP/cadquery/mold_A.stl" --json "$TMP/cadquery/mold_A-report.json"

if command -v openscad >/dev/null 2>&1; then
  openscad -o "$TMP/openscad_A.stl" \
    -D 'part="A"' -D 'mode="hollow_block"' -D 'master_size=[32,32,48]' \
    "$ROOT/scripts/openscad/negative_mold.scad"
  python "$ROOT/scripts/common/mesh_preflight.py" \
    "$TMP/openscad_A.stl" --json "$TMP/openscad_A-report.json"
else
  echo "OpenSCAD not installed; OpenSCAD geometry smoke test skipped."
fi

echo "Smoke-test outputs: $TMP"
