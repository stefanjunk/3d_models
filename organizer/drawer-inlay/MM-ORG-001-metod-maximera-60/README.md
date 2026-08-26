# MM-ORG-001 — METOD/MAXIMERA 60 DRAFT

The reactivated `0.1.0-requirements` concept is approved. Geometry revision `0.1.0-draft.1` is a digitally validated **DRAFT**, not a print candidate or commercial release.

## Current result

- Assembled nominal envelope: `512 × 491 × 50 mm`.
- Manufacturing: exact `3 × 3` grid, nine modules; largest DRAFT mesh extent including tabs is about `180.667 × 173.667 mm`, within the `216 × 216 mm` safe bed.
- Functional layout: one full-depth tool lane, removable eight-slot comb, exactly `3 × 6 = 18` hardware bins.
- Connections: one planar-jigsaw mating location per necessary seam segment, twelve total. The generated value is `0.45 mm` clearance per side; `0.30`, `0.45` and `0.60 mm` coupons exist because fit is unresolved.
- Surface: plain. The approved `MM-WM-001-R1` mark is intentionally absent until final geometry and watermark approval.

The main assembly package is `output/DRAFT/DRAFT-MM-ORG-001-v0.1.0-draft.1-common-220-assembly.3mf`. It contains exactly nine positioned module objects plus the comb. It is an assembly/reference package, not a pre-sliced build plate.

## Toolchain and provenance

The source is a controlled fork of `../DRAFT-schubladen-organizer-R1.6-parametric-surfaces/schubladen-organizer`, rebuilt for the system envelope rather than scaled. Manifold3D 3.5.1 generates the meshes; Python/Trimesh and the shared FDM validation skill audit them; the 3MF packager is deterministic. The local `node_modules` symlink only reuses the already-installed R1.6 dependency tree; a portable checkout can install the pinned dependency from `package.json` after explicit dependency/network approval.

```bash
npm run build
node src/optimization_study.mjs
npm run package
npm run validate
blender -b --python src/render_blender.py
```

## Gate state

The aggregate DRAFT gate has `37 PASS` and `3 REVIEW_REQUIRED`: exact slicer preflight, connector/comb physical fit, and real-drawer/loaded-use evidence. Do not upload/start a printer, force connectors, print all nine modules, add the watermark, claim IKEA compatibility, or release these files until the relevant gates pass.

Next action: follow `print-and-test-plan.md`, beginning with the connector sweep—not a full module.
