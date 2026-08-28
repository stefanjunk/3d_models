# Draft final model result — MM-ORG-034 / 0.1.0-draft.2

## Outcome

FlexDock is complete as a **DRAFT digital print candidate**. Parametric CAD, STEP masters, manufacturing STLs, PETG/TPU 3MF packages, strict topology/package audits, the current approval chain, and three exact Anycubic G-code runs pass. Physical compatibility and commercial release remain blocked.

## Product set

- PETG modular cover clips: S 1.8 mm, M 2.6 mm, and L 3.4 mm nominal gaps.
- Common replaceable TPU loop insert: 10.8 mm relaxed bore, 1.8 mm radial wall, and a compliant snap socket.
- One-piece all-TPU variant: 2.8 mm nominal cover gap with opposed contact ribs.
- TPU pen gauge: 9 / 12 / 15 mm reference bores.
- Every final manufacturing mesh is one watertight, winding-consistent, positive-volume component with zero boundary, non-manifold, degenerate, and duplicate faces.
- The initial centered all-TPU loop was rejected after a native floating-cantilever warning; draft.2 grounds that loop at one side and slices warning-free.

Preview: `renders/MM-ORG-034-digital-candidate.png`.

## Exact slicer evidence

- Anycubic Slicer Next 1.3.9.4; Kobra 3 Max 0.4 mm machine and 0.20 mm Standard process profiles.
- Exact bundled Anycubic PETG and Anycubic TPU filament profiles; supports disabled.
- TPU gauge: 20 layers, 397 s, density-converted 1.67 g, G-code `00ae4f07da8aad160449474e7504cd3fa19417c18c0777e31fe561b7d00dd9c0`.
- PETG S/M/L kit: 150 layers, 1,968 s, density-converted 12.22 g, G-code `1b4f8be2f225bb3f40cff580602aa755eb5cce98f607c43d64a150b5a4a77360`.
- TPU loop/all-TPU kit: 150 layers, 1,784 s, density-converted 6.49 g, G-code `82e1f0e6c3af59ab87f62624894673bfd4bc3f9d597fbe5f15aae22a4ac1353e`.
- All final native results are successful and warning-free; parser reports use one tool, zero tool changes, and no warnings.
- No printer upload or print start occurred.

## Deliverables

- Source: `cad/build.py`, `cad/summarize_slices.py`, `cad/finalize_candidate.py`, and `config/model-parameters.json`.
- Neutral masters: `exports/master/`.
- Material-separated STLs: `exports/manufacturing/petg/` and `exports/manufacturing/tpu/`.
- First-print gauge: `exports/coupons/DRAFT-MM-ORG-034-tpu-pen-gauge-0.1.0-draft.2.stl`.
- Final packages: `exports/3mf/*0.1.0-draft.2.3mf`.
- Exact retained manufacturing runs: the three `slicer-runs/*run-003/` directories.
- Aggregate evidence: `validation/validation-summary.json` after project validation.

## User print sequence

1. Print the TPU gauge and test the actual pen.
2. Print the PETG S/M/L plate; choose the smallest size that seats without cover damage or bowing.
3. Print the TPU kit, then snap the replaceable loop over the chosen PETG rail; or test the one-piece all-TPU variant.
4. Complete `tests/physical-test-plan.md` before making a compatibility, durability, or sale claim.

## Remaining limits

The intended 9–16 mm pen range, cover gaps, TPU snap behavior, fatigue, surface marking, bag snag/drop handling, and appearance are not digitally provable. Filament hardness/brand/color/batch/drying, extrusion compensation, and cover construction can materially change results. No universal-fit or safety-retention claim is authorized.
