# Functional Unicorn Dice Tower

## Final status

**PASS — digital geometry and functional path gates passed.** The actual final
STL was reloaded from disk and passed mesh, underside, opening, baffle-fusion,
22 mm path, build-volume, and visual gates. This is not final manufacturing
approval: no slicer executable is installed in this environment and a physical
dice test is still required.

Final printable export:
`exports/functional_unicorn_dice_tower.stl`

## Method decision

This project uses a deliberate **mesh + parametric CSG hybrid**. Trimesh welds,
orients, scales, and records the imported artistic STL without modifying it.
OpenSCAD hollows the functional core, cuts rounded through-openings, and unions
three rounded baffles with controlled shell overlap. This is the smallest
sufficient method because the preserved exterior is an irregular artistic mesh
while the functional interior is dimension-controlled CSG. The final STL is the
printable mesh master; no STEP-equivalent B-Rep master is claimed.

## Source integrity and orientation

- Immutable input: `../polygonal.stl`
- Expected and final verified SHA-256:
  `fb642c430d34142095107f1f35327568c8f6cb25c6d5e5c4c226d38d68c831e3`
- Source long axis: Y.
- Applied transform: **+90 degrees about X**, then uniform 100 mm/source-unit
  scaling and translation to Z-min=0.
- Print up: **+Z**.
- Front: **-Y**, identified by the unicorn relief and projecting catch tray.
- Back: **+Y**, containing the upper loading inlet.

## Final measured mesh

| Property | Result |
|---|---:|
| Bounds min XYZ | `[-67.9234, -65.9271, 0.0000] mm` |
| Bounds max XYZ | `[67.4879, 62.2615, 199.1940] mm` |
| Overall size XYZ | **135.4113 x 128.1886 x 199.1940 mm** |
| Volume | **516,469.95 mm3** |
| Vertices / triangles | 5,900 / 11,844 |
| Bodies | **1** |
| Watertight / winding | **yes / consistent** |
| Degenerate / broken faces | **0 / 0** |
| Nonadjacent BVH overlap indicator | **0 pairs** |
| Z minimum | **0.0000 mm** |

The broad reused underside is slightly faceted rather than mathematically flat:
12,405 mm2 of downward area lies within 0.2 mm of Z=0. Four rays from below hit
its underside at Z=0.030-0.045 mm. The core-center ray measures a closed floor
thickness of **21.964 mm** against the 22 mm design value. The underside was not
punched through.

## Functional geometry

- Elliptical hollow core: center `(X=0, Y=25)`, radii **42.0 x 24.5 mm**,
  spanning Z=22-150 mm.
- Minimum sampled shell wall away from openings: **3.061 mm** at the upper
  core-to-dome transition. Representative mid-body samples are 3.23-4.82 mm.
- Back inlet (+Y): rounded **46 x 42 mm** clear cutter, center Z=139 mm.
- Front outlet (-Y): rounded **46 x 38 mm** clear cutter, center Z=41 mm,
  sill Z=22 mm, discharging directly onto the retained bottom tray.
- Opening penetration: 9/9 tested rays clear through each opening from outside
  to an analytically interior core point on the actual STL.
- Three staggered rounded baffles: nominal **4.5 mm** thick, 45 degrees,
  alternating back/front/back at center Z values 136, 90, and 46 mm.
- Reloaded measured baffle thicknesses: **4.4934, 4.4935, 4.4935 mm**.
- Each baffle has 2.5 mm designed radial shell overlap. Expected-zone faces on
  the actual STL reach both the core and shell band, and the final mesh remains
  one connected topological body. The upper baffle is locally cleared by the
  inlet at its center but remains fused on both side flanks.

## Supported die and path evidence

Supported size is **22 mm maximum**. A conservative axis-aligned 22 mm cube was
swept through the prescribed zig-zag waypoints from the back inlet to the front
outlet. OpenSCAD CGAL intersected that swept volume with the **actual final STL
reloaded from disk**. The top-level intersection was empty, no collision STL was
created, and collision volume is 0 mm3.

See `reports/die_path_clearance.json` and the orange centerline in
`previews/functional_unicorn_dice_tower_cutaway_verified_path.png`.
This is a geometric path-clearance test, not a gravity, rotation, bounce, or jam
simulation. 24 mm dice are not claimed. Pass several real 22 mm dice through a
prototype before relying on repeated operation.

## FDM guidance

- Exact print orientation: keep STL coordinates unchanged; bottom disc on bed,
  +Z upward.
- Preferred material: PLA for easier 30-32 mm opening-crown bridges. PETG is
  usable after bridge tuning but is more prone to sag/stringing.
- Recommended nozzle/layer: **0.4 mm / 0.20 mm**; use 0.16 mm for finer exterior
  ornament if desired.
- Use 4-5 perimeters, at least 5 top/bottom layers, and 10-15% infill.
- Automated 45-degree normal analysis found 765 candidate faces totaling
  9,148.98 mm2 (7.98% of the surface). Candidates include exterior decorative
  facets, opening crowns, and rounded baffle undersides.
- The baffles are nominally at the self-support threshold. Use bridge cooling
  and approximately 20-30 mm/s for the opening crowns.
- Prefer support blockers inside the core. Dense automatic internal supports can
  become difficult to remove between alternating baffles. If needed, use
  organic/tree, build-plate-only support under accessible exterior lips and the
  outlet crown.
- A 5-8 mm brim is optional; the broad base already provides substantial area.

No PrusaSlicer, OrcaSlicer, CuraEngine, Cura, or SuperSlicer executable was
available, so no layer preview or G-code is claimed. Inspect an actual slicer
preview for bridges, thin ornament, internal support, and first-layer contact,
then make one physical PLA test print.

## Validation reports

- `reports/functional_unicorn_dice_tower.mesh.json` — shared Trimesh gate.
- `reports/functional_validation.json` — underside, wall, opening, baffle, hash,
  and path evidence.
- `reports/functional_unicorn_dice_tower.self_intersection.json` — Blender BVH
  nonadjacent-overlap indicator.
- `reports/die_path_clearance.json` and `.log` — actual-STL cube-sweep evidence.
- `reports/functional_unicorn_dice_tower.fdm.json` — shared FDM gate.
- `reports/fdm_assessment.json` and `.md` — manufacturing interpretation.
- `reports/preview_inspection.json` — image hashes and visual observations.
- `reports/source_preparation.json` — source transform provenance.

## Final previews

- `previews/functional_unicorn_dice_tower_isometric.png`
- `previews/functional_unicorn_dice_tower_front_minus_y.png`
- `previews/functional_unicorn_dice_tower_back_plus_y.png`
- `previews/functional_unicorn_dice_tower_cutaway_verified_path.png`

The first three import the actual final STL directly into Blender. The cutaway
uses an OpenSCAD `Simple: yes` X-half derivative made from that actual STL and
overlays the verified path centerline. Rejected low-cost previews and failed
intermediate path collisions are isolated under `diagnostics/`.

## Reproduction

Run from this directory:

```bash
python3 prepare_source.py
bash /workspace/skills/openscad/tools/validate.sh functional_tower.scad
openscad -o exports/functional_unicorn_dice_tower.stl \
  -D 'preview_fn=48' -D 'render_mode="final"' functional_tower.scad
python3 /workspace/skills/mesh-validation/scripts/validate_mesh.py \
  exports/functional_unicorn_dice_tower.stl --units mm --max-bodies 1 \
  --report reports/functional_unicorn_dice_tower.mesh.json
python3 validate_function.py
blender --background --python check_self_intersections.py
python3 /workspace/skills/fdm-printability/scripts/inspect_printability.py \
  exports/functional_unicorn_dice_tower.stl --units mm \
  --bed 256,256,256 --nozzle 0.4 --layer-height 0.2 \
  --declared-min-wall 3.060914 --declared-min-feature 1.5 \
  --material PLA --self-support-angle 45 --max-bodies 1 \
  --report reports/functional_unicorn_dice_tower.fdm.json
openscad -o diagnostics/actual_final_cutaway.stl \
  -D 'preview_geometry_mode="cutaway"' actual_preview_geometry.scad
blender --background --python render_previews.py
```

`parameters.json` is authoritative. `generated_parameters.scad` is regenerated
from it and should not be hand-edited.

## Limitations

- Voxel-free CSG and mesh checks prove digital geometry, not real dice dynamics.
- The source is intentionally polygonal; visible faceting is preserved.
- Local shell thickness varies with the imported art.
- 24 mm dice, heavily pointed dice, simultaneous multiple dice, bridge quality,
  support removability, and long-term impact durability require physical tests.
