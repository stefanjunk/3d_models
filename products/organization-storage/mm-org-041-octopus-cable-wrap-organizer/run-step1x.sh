#!/usr/bin/env bash
# MM-ORG-041 — fresh Step1X-3D geometry run, run from the repository root.
# Prerequisite: organic/reference/octopus-preform-plate-001.png exists and
# evidence/imagegen-record.json records how it was made.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SKILL="$REPO_ROOT/.agents/skills/step1x-image-to-3d"
PROD="products/organization-storage/mm-org-041-octopus-cable-wrap-organizer"
PLATE="$PROD/organic/reference/octopus-preform-plate-001.png"
RUN_ID="${1:-}"

if [[ ! "$RUN_ID" =~ ^run-[0-9]{3}$ ]]; then
  echo "Usage: $0 run-NNN" >&2
  exit 2
fi

OUT="$PROD/organic/raw/step1x/$RUN_ID"
RUNTIME="$PROD/evidence/step1x-runtime-$RUN_ID.json"

test ! -e "$OUT" || { echo "BLOCKED: output already exists: $OUT"; exit 1; }

test -f "$PLATE" || { echo "BLOCKED: missing reference plate $PLATE"; exit 1; }
test -f "$PROD/evidence/imagegen-record.json" || { echo "BLOCKED: missing evidence/imagegen-record.json"; exit 1; }

# 1. readiness must be confirmed before every submission
python3 "$SKILL/scripts/step1x_client.py" status \
  --url http://127.0.0.1:7861 \
  --report "$PROD/reports/step1x-status-$RUN_ID.json"

# 2. freeze the live API contract
python3 "$SKILL/scripts/step1x_client.py" probe \
  --url http://127.0.0.1:7861 \
  --report "$PROD/reports/step1x-api-$RUN_ID.json"

# 3. capture the runtime for the commercial provenance chain
python3 "$SKILL/scripts/capture_step1x_runtime.py" \
  --repo /home/stefan/Projekte/Step1X-3D \
  --url http://127.0.0.1:7861 \
  --output "$RUNTIME"

# 4. generate one auditable untextured GLB (x symmetry for the radial body)
python3 "$SKILL/scripts/step1x_client.py" generate "$PLATE" \
  --output-dir "$OUT" \
  --runtime-profile "$RUNTIME" \
  --image-prompt-file "$PROD/organic/reference/imagegen-prompt.txt" \
  --input-record "$PROD/evidence/imagegen-record.json" \
  --guidance 7.5 --steps 50 --max-faces 400000 \
  --symmetry x --edge-type sharp

# 5. inspect without modifying the shape master
python3 "$SKILL/scripts/glb_to_print_mesh.py" inspect \
  "$OUT/geometry.raw.glb" \
  --report "$PROD/reports/step1x-geometry-intake-$RUN_ID.json"

echo "Done. Next: organic-mesh-functionalization for repair, millimetre scaling and the channel Boolean."
