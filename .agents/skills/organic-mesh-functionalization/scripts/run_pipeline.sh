#!/usr/bin/env bash
set -euo pipefail

SOURCE=${1:?usage: run_pipeline.sh SOURCE CONFIG ROI RESULT}
CONFIG=${2:?usage: run_pipeline.sh SOURCE CONFIG ROI RESULT}
ROI=${3:?usage: run_pipeline.sh SOURCE CONFIG ROI RESULT}
RESULT=${4:?usage: run_pipeline.sh SOURCE CONFIG ROI RESULT}

mkdir -p reports
python scripts/inspect_mesh.py "$SOURCE" --json reports/source.json
blender --background --python scripts/blender_functionalize.py -- "$CONFIG"
python scripts/inspect_mesh.py "$RESULT" --json reports/result.json --require-watertight
python scripts/validate_edit.py "$SOURCE" "$RESULT" --roi "$ROI" --json reports/edit-validation.json
