# FLUENT — two actual 3D routes, one recommendation

**Recommend the parametric bundled-petal version, Run 003.**
The local Step1X comparison is retained as silhouette inspiration; its
ragged rib surfaces and four components make it unsuitable as the current
production exterior.

[Actual model hero](runs/003/fluent-hero.png) ·
[Back](runs/003/fluent-back.png) ·
[Side](runs/003/fluent-side.png) ·
[3D GLB](runs/003/fluent-visual.glb) ·
[Blender scene](runs/003/fluent-parametric-study.blend)

## What exists

- Editable geometric source: source/build_petals.py, source/petal_envelope.py,
  source/build_fluent.py, parameters.json.
- A true curved, ribbed 3D shell and subordinate visual foot, not a raster
  illusion. Total bounding dimensions approximately 93.21 × 87.12 × 240 mm.
- Cubic station profiles for belly/waist/centerline/twist; 12 rounded ribs;
  separate asymmetric petal tips. Explicit radial shell closure, no liquid reservoir.
- Purchased vial Ø50 × H64 mm and fibre reed Ø5 × 200 mm remain hidden reference
  objects in the Blender scene, excluded from the visual GLB/OBJ.
- An immutable 400000-triangle Step1X raw proposal plus registered 240 mm
  visual derivative, approximately 104.02 × 101.87 × 240 mm.

GLB coordinates use metres. The single-shell inspection OBJ is in millimetres.
There is no STEP/B-Rep claim, STL print candidate, slicer 3MF or G-code.

## Rebuild and edit

From this directory, with the existing Blender 5.2 executable:

```sh
blender --background --factory-startup -t 12 --python source/build_petals.py -- --out runs/next-unused --views hero,back,side --samples 24 --resolution 1000
```

Always choose a new output directory. Never overwrite a prior run.
Edit a copy of parameters.json and pass --params /absolute/path/to/copy.json.
Height, width/depth factors, rib count/depth, twist and station profiles are
independently editable. Purchased dimensions do not scale with the exterior.
The nominal width/depth parameters are profile factors, not exact final
bounding-box constraints; rely on measured export dimensions.

For the selected petal method, crown_asymmetry_fraction controls tip-height
offset; optional petal_split_fraction controls the root height (default 0.55,
tested 0.50–0.60). crown_valley_fraction belongs only to the old radial-cut-rim
generator and has no effect on the selected petal crown.

Do not scale the radial shell value or future calibrated fits with the object.
The 2.4 mm radial offset is not a measured minimum normal wall thickness.

## Validation boundary

The preflight remains CONCEPT_ONLY / C3 / R0 / K2 / Lane E. This phase is a
user-directed visual form study within the existing product, lifecycle P0;
it is not P2 and does not bypass concept/production approval.

Shared mesh audits and reduced-mesh parameter sweeps are retained. A strict
self-intersection check is NOT_RUN because the shared auditor has no certified
backend configured. Walls, crown strength, slicer supports, finish, stability,
service/holder/retention geometry, oil compatibility and scent remain open.
The foot is a visual placeholder, not an engineered coupling.

Curvature reports are numerical diagnostics, not G2/Class-A certification.
The earlier sparse-rail report contains resampling artifacts; use the later
dense-petal-rail diagnostic for the selected method, with physical/visual
review still required.

See VISUAL-REVIEW.md, reconstruction-brief.yaml, validation-project.json and
learning-trace.md. Only the visual-method comparison is complete.

## Evidence and retention

R1 hero remains the primary style reference. Step1X's isolated plate is a
separate input, generated via the built-in image tool; exact prompts are in
step1x/input-prompt*.txt. No model render was AI-enhanced.

Step1X source/runtime/input/output hashes and the container-path mapping are
in step1x/run-001 and step1x/CONTAINER-EXECUTION.md. No package was installed,
service restarted, printer uploaded to or print started.

Intermediate Run 001 and sweep OBJ binaries remain locally recoverable but
are not added to Git. Their parameters, source/evidence and retained renders
allow regeneration. Selected models and images use product-local Git LFS.

Commercial rights, identity regularization and final marking remain separate
main/release tasks. This product feature phase is merge-ready after push,
not integrated into main and not released.
