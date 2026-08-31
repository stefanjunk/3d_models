# MM-ART-011 terrain-build failure trace — revision 0.3.0

This is the owning raw project trace for two corrected digital failures. It is not a promoted general rule and contains no physical evidence.

## Buffered contour created a loose terrain island

- Expected: each selected open terrain contour becomes one protected through-slot while each half remains one connected panel body.
- Initial Rhenish-right result: two watertight disconnected components. The secondary component measured 147.8090088371 mm³ and 504 triangles.
- Observation: one selected buffered open contour polygon contained one interior ring. Subtracting that ring-shaped cutter enclosed a terrain island even though the source path was nominally open.
- Correction: reject every candidate aperture polygon with any interior ring before Boolean subtraction; retain the existing safe-region, spacing and area checks.
- Final result: Harz left/right and Rhenish left/right each contain exactly one connected watertight composite component; no orphan cleanup was needed. Six Harz and seven Rhenish open light paths remain.
- Evidence: `harz/harz-build-report.json`, `rhenish/rhenish-build-report.json`, and `source/v0.3.0/build_terrain.py`.

## Vertex tangent to a horizontal color plane created null faces

- Expected: four layer-only band solids remain watertight after STL welding and 3MF packaging.
- Initial Rhenish-right 3MF result: object 3 contained repeated-index triangles `[6592, 6592, 6593]` and `[6592, 20114, 6592]`; its welded mesh was not watertight.
- A post-export degenerate-face cleanup fixed that isolated Rhenish body but opened a Harz-right Chocolate Brown band, so generic post-export cleanup was rejected.
- Direct measurement found manufacturing vertices within 0.0001 mm of the selected planes: 72 across Harz and 141 across Rhenish. Five Harz vertices lay numerically exactly at Z=4.2 mm.
- Correction: before heightfield construction, move only vertices within 0.0001 mm of a color plane to plane + 0.001 mm. The measured maximum displacement is 0.0010995865 mm; the 4.2/4.8/6.0 mm and 7.6/7.8/8.2 mm color planes remain unchanged and aligned to 0.20 mm layers.
- Final result: all sixteen color STL bodies are watertight; all four standard 3MF packages validate with four watertight material objects and no warnings; all four unchanged composite hashes pass exact Anycubic slicing.
- Evidence: `harz/harz-build-report.json`, `rhenish/rhenish-build-report.json`, the four `*-3mf-validation.json` reports and the four `slice-*-composite-r1.json` reports.

## Scope limits

- Digital-only evidence on two 600 × 400 mm terrain pilots, Manifold3D, Trimesh, binary STL, standard 3MF and Anycubic Slicer Next 1.3.9.4.
- Target process: Anycubic Kobra 3 Max Combo, 0.4 mm nozzle, 0.20 mm Standard profile, PLA Matte candidate; exact unit, firmware, nozzle material/wear, spool identity, batch and conditioning are unknown.
- No physical coupon, seam assembly, lighting test or full print has been run.
