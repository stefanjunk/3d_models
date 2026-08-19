# Example 1 — 300 mm Roman pillar with marble relief

## Goal

Create a 300 mm-tall Roman-style pillar with base, shaft, and capital. A marble image supplies low-relief veins/engraving. The workflow must support a plaster final cast and, as an alternative, a ceramic cast.

## Recommended decomposition

Do not begin with one monolithic 300 mm negative. Separate the article into:

1. base, approximately 45–60 mm high;
2. shaft, approximately 180–210 mm high;
3. capital, approximately 45–70 mm high.

Use concealed locating sockets/tenons for post-cast assembly when an assembled final object is acceptable. This removes many undercuts, fits more printers, reduces mold-section mass, and allows failed details to be reprinted or recast.

When the final object must be monolithic, retain the same decomposition in the **tooling** as stacked, indexed rings and side sectors.

## Geometry strategy

### Shaft

- Use a rotational or near-rotational parametric core.
- Use two vertical mold sections for a smooth tapered shaft.
- Use four vertical sectors when flutes, projecting bands, or marble relief create side undercuts.
- Place seams in flute valleys or along the rear visual axis.
- Add a small taper/draft or divide at molding bands.

### Base

- Use two side sections plus an open top/bottom strategy depending fill orientation.
- Place the seam at strong architectural edges.
- Avoid fragile plaster blades under deep torus moldings; split at those ridges or soften the undercut.

### Capital

A Corinthian/acanthus capital is the hardest region. Options in descending robustness:

1. simplify leaves to pull-safe bas-relief and use four side sections plus a top section;
2. use loose inserts for the deepest leaf hooks;
3. make a silicone detail skin and a 3D-printed four-part mother mold;
4. cast the capital separately from the shaft.

For a fully rigid plaster working mold, do not hide severe undercuts inside a nominal two-part split.

## Mold architecture

Default for a plaster final cast:

- rib-stiffened conformal printed shell;
- four vertical sections for the capital, two/four for shaft, two/four for base;
- broad external clamp flanges;
- asymmetric conical keys;
- top funnel/reservoir and vents at leaf tips/high points;
- optional reusable frame around the shaft sections.

Default for porcelain/stoneware slip casting:

- print a positive compensated master or reusable section cases;
- create absorbent pottery-plaster working-mold sections;
- add a removable pour spout at the top;
- provide a stable inverted drain cradle;
- size plaster sections for safe lifting and complete drying.

## Marble texture workflow

A mold transfers **topography**, not marble color. Use the image to create selective vein relief, then use stains, engobes, underglaze, glaze, or post-finish for color.

1. Choose a seamless or deliberately placed marble image.
2. Convert to 16-bit grayscale.
3. Remove broad illumination gradients unrelated to veins.
4. Use gamma/levels to reserve full depth for major veins.
5. Blur isolated pixel noise.
6. Map continuously around the shaft with cylindrical UVs; define one rear seam.
7. Map base/capital separately but maintain one preferred vein direction where visually required.
8. Use local displacement only on the visible outer skin.

Starting coupon for 0.4 mm FDM master/case:

- major vein width: 0.8–1.5 mm;
- minor vein width: 0.5–0.8 mm;
- depth/height: 0.2–0.5 mm;
- layer height: 0.10–0.14 mm.

For finer veins, use a smaller nozzle or SLA detail insert. Do not create full-height random 0.1 mm noise; it will read as roughness and may trap release or glaze.

## Shrinkage example

The final height is 300 mm. Suppose a **measured** combined linear shrinkage test for the exact ceramic route gives 12.0% in XY and 13.0% in Z:

```text
X/Y scale = 1 / (1 - 0.12) = 1.13636
Z scale   = 1 / (1 - 0.13) = 1.14943
modeled green/tool height = 300 × 1.14943 = 344.83 mm
```

This is only an illustration. Replace with measured coupon values and account for whether the master, plaster case, and working mold introduce additional dimensional changes.

## Fill and vent plan

For a solid plaster cast:

- fill from the top center through a tapered funnel;
- add a reservoir above the capital;
- vent every leaf-tip pocket and the highest edges of the abacus;
- brush a face coat into the capital before bulk filling;
- consider casting capital separately to reduce bubbles.

For hollow ceramic slip casting:

- removable top pour spout;
- dwell based on wall-build test;
- drain through the same opening with mold inverted on a cradle;
- avoid interior shelves at capital/base transitions that retain slip;
- allow the green body to stiffen and shrink before opening.

## Print segmentation

For a 300 mm part on an FDM printer:

- split each mold section into rings no taller than the reliable build/warp limit;
- use external tongue-and-groove alignment and through-bolts or clamp rails;
- stagger structural ring seams relative to article seams where possible;
- process high-resolution capital data separately from the simpler shaft;
- print casting faces upward/vertical to minimize support damage.

## Memory plan

Do not voxelize the full 300 mm pillar at the vein pitch. Keep:

- parametric shaft/base solids as BREP or low-poly meshes;
- capital as a locally high-resolution organic mesh;
- marble relief as a texture/displacement patch;
- ribs/flanges/keys as parametric solids;
- modules exported independently.

A 300 mm cube at 0.1 mm voxel pitch is 27 billion voxels before overhead; use local crops and coarser structural resolution.

## Acceptance criteria

- assembled final height after process: 300 mm within project tolerance;
- shaft axis straight; ring/module alignment does not produce a visible step;
- all mold sections remove without bending greenware;
- no trapped air defect at capital leaf tips larger than the agreed limit;
- major marble veins recognizable at 0.5–1 m viewing distance;
- no vein becomes a fragile plaster knife edge or a glaze-filled dirt trap;
- seams lie in flute valleys/rear edges and can be finished without flattening ornament.

## Suggested scripts

```bash
python scripts/common/prepare_heightmap.py marble.png build/marble-1024.png \
  --physical-size-mm 220 220 --sample-pitch-mm 0.20 --mode tile --gamma 1.2

python scripts/common/mold_planner.py assets/examples/roman-pillar.json \
  --output build/roman-pillar-plan.md

python scripts/cadquery/block_mold.py --demo roman-pillar \
  --height 300 --output-dir build/roman-pillar-demo
```
