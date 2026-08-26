# CadQuery workflow

CadQuery is the preferred baseline for dimensionally controlled molds built from STEP/BREP sources. It combines Python automation with OpenCascade solids and exports STEP plus tessellated print files.

## Best uses

- parametric blocks, shells, ribs, flanges, keys, funnels, vents, and fixtures;
- scaling a STEP solid using measured shrinkage;
- robust planar splitting and boolean construction;
- reusable mold families and machine-readable manifests;
- neutral STEP delivery for inspection or later CAD work.

CadQuery's normal import workflow supports STEP and other listed CAD formats, but not arbitrary STL as a first-class BREP import. For dense mesh sources, repair/process in Blender or convert carefully in FreeCAD, then provide a STEP solid only if conversion remains tractable.

## Coordinate convention

The included script uses millimetres, Z up, and an X-plane split through the cavity center. It recenters the imported or demo master around its bounding-box center before applying shrinkage.

## Import and validate STEP

```python
import cadquery as cq

master = cq.importers.importStep("master.step").val()
if master.isNull():
    raise RuntimeError("STEP import produced a null shape")
print(master.BoundingBox().xlen)
```

A STEP file may contain an assembly or multiple solids. Decide whether to fuse, preserve, or reject them; do not silently use the first unrelated solid in production code.

## Scaling for shrinkage

OpenCascade shape scaling is uniform through a transform in many straightforward workflows. For anisotropic compensation, transform the shape with an affine matrix or scale the parametric dimensions before constructing the master. Verify the resulting BREP because non-uniform transforms can change analytic surfaces and downstream robustness.

The included baseline handles axis-specific scaling through a transformation matrix and records the values.

## Block mold algorithm

1. Load or create the positive master.
2. Move the master to a documented datum.
3. Apply compensation scale.
4. Create a box with side, bottom, and top margins.
5. Subtract the master to form the cavity.
6. Subtract sprue/reservoir and vents.
7. Intersect with X half-spaces to create mold A and B.
8. Fuse male registration keys to A.
9. Subtract larger matching sockets from B.
10. Export STEP and STL plus manifest.

The baseline script is intentionally simple. For a real article, replace planar split logic with process-specific parting solids and add flanges/ribs before export.

## Shell construction

CadQuery `shell()`/thickness operations can fail where offset surfaces intersect, at sharp concavities, or on complex imported geometry. Safer alternatives include:

- a parametric outer envelope minus a controlled inner void;
- section-by-section lofted outer walls;
- a cavity insert mounted in a separate structural frame;
- a mesh-derived detail insert combined at assembly level, not one massive BREP boolean.

When shelling succeeds, inspect every edge and measure minimum thickness. Do not assume a successful operation means a printable or watertight shell.

## Ribs and flanges

Construct ribs from the external datum surfaces and fuse them before or after the cavity boolean depending on stability. Add root fillets when robust. Keep the casting cavity as a separate named intermediate so structural changes do not repeatedly re-evaluate the expensive source subtraction during development.

A robust pattern is:

```python
outer = make_outer_frame(params)
structure = outer.union(make_ribs(params)).union(make_bosses(params))
complete = structure.cut(master).cut(feed_channels)
```

## Keys

Use `cq.Solid.makeCone` or cylinders with lead-in chamfers. Orient the key along the parting-surface normal. Add clearance only to the socket, and record it in the manifest.

For plaster cases, large broad keys can be more durable than small precision dowels. For printed direct molds, external metal dowels may provide better repeatability than printed micro-keys.

## Funnel, sprue, and vents

Build feed geometry as real solids and subtract it from the complete mold before splitting. Use a tapered sprue with a removable funnel lip. Add vents as cylinders or swept wires reaching outside the mold.

Check that the smallest channel survives STL tessellation and slicing. A CAD cylinder can disappear when its diameter is below the slicer's printable line policy.

## Export

Keep both STEP and STL/3MF where possible:

```python
cq.exporters.export(mold_a, "mold_A.step")
cq.exporters.export(
    mold_a,
    "mold_A.stl",
    tolerance=0.05,
    angularTolerance=0.1,
)
```

Select tessellation tolerance from the physical detail budget. Very small tolerances inflate files without improving the print.

## CQ-editor and command line

The scripts are plain Python and can run headless. For interactive inspection, open the model in CQ-editor and use `show_object()` in a local wrapper.

```bash
python scripts/cadquery/block_mold.py --demo bowl --output-dir build/bowl
python scripts/cadquery/detail_coupon.py --output-dir build/coupon
```

## Performance rules

- Prefer STEP/BREP primitives for structural geometry.
- Keep the source cavity subtraction as a cached/exported intermediate.
- Split oversized tools into modules before adding small repeated details.
- Avoid converting millions of mesh triangles into BREP faces.
- Use simple cylinders/cones for channels rather than high-control-point splines.
- Export low-resolution review STL and final production STL separately.
- Catch boolean failures and save operands for diagnosis.

## Validation

Run the common mesh preflight on exported STL and inspect the STEP in an independent viewer. Verify:

- each result is a valid solid;
- volume is positive and cavity is present;
- keys belong to the intended half;
- socket clearance is nonzero after tessellation;
- the sprue/vents reach the cavity and exterior;
- mold halves share one datum and assemble without overlap.
