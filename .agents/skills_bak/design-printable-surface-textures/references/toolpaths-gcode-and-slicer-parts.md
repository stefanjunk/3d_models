# Toolpath, G-code, and slicer-defined surface textures

## Contents

1. Select among slicer, modifier, and direct-path methods
2. Use Fuzzy Skin deliberately
3. Use top-surface patterns and directional gloss
4. Use exposed infill as a surface subsystem
5. Preserve parts that must fuse into one object
6. Create individual filling patterns
7. Control direct G-code safely
8. Record the manufacturing contract
9. Failure modes

## 1. Select among slicer, modifier, and direct-path methods

| Method | Best for | Geometry cost | Main limitation |
|---|---|---:|---|
| Slicer top/bottom pattern | horizontal planar skins, direction/gloss | none | does not conform to arbitrary exterior surfaces |
| Fuzzy Skin/perimeter perturbation | rough side walls, grip, stone-like microtexture | none | slicer-specific scope and randomness |
| Per-part or modifier settings | local texture zones | simple envelope only | project/profile required; boundary semantics vary |
| Exposed infill | porous nozzle-scale screens | simple envelope only | pattern exists only after slicing |
| Vector relief sliced normally | flat or curved repeatable motifs | low to moderate | repeated Booleans/perimeters can still grow |
| Authored extrusion paths | custom flowers, weave, nonstandard line art | no STL texture mesh | machine-specific safety and process burden |

Prefer a slicer method when it directly produces the required paths. Prefer authored paths only when ordinary slicing cannot express the pattern and the added control justifies validation.

## 2. Use Fuzzy Skin deliberately

Fuzzy Skin perturbs sampled perimeter points and is useful for random roughness, layer-line masking, and some grips. Treat it as a side/perimeter effect unless the exact slicer/version proves otherwise.

Control:

- target named surfaces or part/modifier;
- perturbation thickness/amplitude;
- point spacing/density;
- outer versus all walls;
- seam, thin-wall, clearance, and dimensional impact;
- speed, cooling, and short-segment behavior.

Do not use it for directional carbon weave, crisp wood grain, text, seals, sliding fits, or surfaces whose thickness and cleanability are critical.

## 3. Use top-surface patterns and directional gloss

Top fill orientation changes the visible line field and reflected highlight. Test aligned, monotonic, concentric, or authored patterns on the actual material and light direction. Keep the top skin adequately supported and avoid under-extruding production parts merely to reveal the pattern.

For a carbon-look coupon, compare:

- uniform `+45°` top paths;
- uniform `-45°` top paths;
- alternating vector/tile regions;
- one shallow geometric twill layer;
- material/film baseline.

For brushed metal, prefer one coherent direction and a metallic material/finish. For wood, use wavy vector paths or a thin texture skin when the slicer cannot author a grain field.

## 4. Use exposed infill as a surface subsystem

Represent the region as a closed named `LATTICE_ENVELOPE` and retain a separate solid `FRAME`. Apply locally:

```text
walls/perimeters = 0
top solid layers = 0
bottom solid layers = 0
automatic/periodic solid infill = off
selected infill pattern/density/angle/line width/layer count
```

Do not assume zero walls disables all skins, bridge fill, gap fill, or ironing. Inspect each generated layer.

Use the complete `optimize-fdm-design/references/exposed-infill-patterns.md` contract for anchoring, crossing buildup, open-area measurement, guard limitations, and acceptance.

## 5. Preserve parts that must fuse into one object

Use this state model:

```text
logical manufacturing model: selectable CORE/TEXTURE_SKIN/FRAME/LATTICE parts
printer job: coordinated registered paths with deliberate capture/overlap
physical result: one bonded object unless replacement is intended
```

Requirements:

1. Use one project origin, units, axes, and transforms.
2. Import/group bodies as parts of one multi-part object; do not auto-arrange them independently.
3. Assign local settings/materials while identities remain selectable.
4. Define a positive interface compatible with the slicer's overlapping-volume semantics.
5. Make texture/lattice paths enter or overlap a sufficient solid capture band.
6. Inspect feature-colored layers and print a representative joint coupon.
7. Preserve the exact 3MF/project and source bodies.

A single fused STL loses settings identity. Separate unregistered STLs lose placement. Tangential contact can be clipped into a gap.

## 6. Create individual filling patterns

Three routes exist:

### Pattern from a slicer library

Choose the nearest existing infill family and tune pitch, density, angle sequence, layer count, and clipping envelope. This is fastest but does not create an arbitrary lotus or floral topology.

### Pattern from a vector envelope or modifier

Use petal-, leaf-, or ornament-shaped volumes to control where an existing infill appears. The visible strands remain the slicer's pattern; the floral silhouette comes from the envelope/frame.

### Fully authored paths

Generate the actual petal/flower/weave centerlines as extrusion paths. This supports individual motifs and avoids dense strand meshes, but it is no longer ordinary CAD-to-slicer production. Parameterize minimum radius, path spacing, speed, extrusion per length, seam/start points, crossing order, and layer support.

For an open lotus panel, first test vector petals as closed openings or a lotus-shaped `LATTICE_ENVELOPE`. Use fully authored paths only when the strand topology itself must be floral.

## 7. Control direct G-code safely

Treat G-code as a compiled machine job, not a portable model.

### Preferred architecture

1. Generate geometric centerlines and process events in a machine-neutral source.
2. Transform and clip paths to a declared safe build region.
3. Calculate extrusion using the calibrated line cross-section and filament area.
4. Emit only with a named printer/firmware/material/nozzle/profile adapter.
5. Reuse trusted start/end, homing, heating, purge, leveling, tool-change, and shutdown routines.
6. Preview/simulate the complete output and check the first layer manually.

### Mandatory checks

- absolute versus relative XYZ and E modes;
- units and workspace/coordinate offsets;
- bed bounds, clamps, purge areas, and keep-outs;
- safe travel Z and collision with existing print or non-planar paths;
- extrusion reset/position, retraction, pressure advance, acceleration, jerk, and flow;
- maximum volumetric flow and minimum layer time;
- arc support/tessellation and controller segment load;
- temperature, fan, material change, pause, and recovery behavior;
- start/end safety and emergency-stop access.

Do not paste free-form path snippets into an unrelated file without reconciling machine state. Do not execute a generated job merely because it renders correctly. First use a dry/air preview where safe, then a small expendable coupon with conservative speed and clearance.

The peer-reviewed FullControl approach demonstrates that unconstrained parametric print-path design is feasible, including non-planar paths, but it does not remove machine-specific validation.

## 8. Record the manufacturing contract

Persist:

```text
slicer/path generator and version
printer, firmware, nozzle, material, and build surface
object revision, origin, orientation, and part names
texture method and source revision/seed
top/perimeter/infill pattern, angle sequence, density, and line width
walls, top/bottom layers, modifier rules, and overlap
layer heights/count, speed, acceleration, flow, cooling, and temperatures
extruder/material assignment and purge behavior
preview/simulation file and coupon measurements
final 3MF/project and generated G-code checksum
```

Do not make G-code the only editable source.

## 9. Failure modes

| Failure | Cause | Prevention |
|---|---|---|
| Texture appears on wrong faces | global setting or modifier leakage | use named part/painted region; inspect all layers |
| Carbon pattern looks like scratches | motif below path scale or only one cue represented | enlarge stylized cell; combine path direction/material |
| Lattice detaches | endpoints only touch frame | capture band and joint coupon |
| Nozzle strikes grid crossings | same-layer buildup, warp, overextrusion | non-crossing family, layer staggering, tuned flow/clearance |
| Floral infill becomes ordinary grid | envelope changes silhouette, not strand topology | author vector paths if strand topology is essential |
| Curved texture drifts | planar/UV coordinates used without metric correction | map by surface distance and validate marker coupon |
| Controller stutters | excessive tiny G-code segments | simplify centerlines, use supported arcs, benchmark controller |
| Direct path starts in wrong state | incompatible modes/start code | machine-specific adapter and complete-file simulation |
| Settings disappear on export | only STL/STEP retained | preserve exact 3MF/project and named sources |
