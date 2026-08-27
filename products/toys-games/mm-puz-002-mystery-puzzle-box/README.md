# Mystery Puzzle Box — MM-PUZ-002 v1.2.0

This directory contains the first complete parametric and printable DRAFT model
for portfolio record `PORT-034`.  It preserves the approved 250 x 75 x 75 mm
question-mark exterior while implementing three independent direct latches.

The current status is **P2 Digital candidate**, not a qualified product.  The
source, B-Reps, meshes, multi-object 3MF, interfaces, watermark and procedural
texture are digitally checked.  Exact slicing and every physical mechanism,
spring, appearance, safety and commercial gate remain open.

Rebuild from the repository root:

```sh
python3 products/toys-games/mm-puz-002-mystery-puzzle-box/scripts/build.py
blender --background --python products/toys-games/mm-puz-002-mystery-puzzle-box/scripts/render_model.py
python3 .agents/skills/validate-printable-3d-projects/scripts/fdm_ci.py \
  validate-project products/toys-games/mm-puz-002-mystery-puzzle-box/validation-project.json --profile draft
```

Print one body, one lid, three sliders and three PETG return leaves.  Read
`print-profile-v1.2.0.json` and `test-plan.yaml` before treating any geometry as
manufacturing-ready.

