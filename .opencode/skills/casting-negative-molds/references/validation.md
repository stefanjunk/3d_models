# Validation and acceptance checklist

Validation is staged. Do not discover basic geometry errors after a 300 mm print or a full plaster pour.

## Stage 0 — Source control

- [ ] Original file preserved and checksum recorded.
- [ ] Working units declared; no implicit STL unit assumption.
- [ ] Final target dimensions and datum recorded.
- [ ] Source orientation and intended fill orientation recorded.
- [ ] Copyright/licensing permits the intended use.

## Stage 1 — Source geometry

For meshes:

- [ ] One intentional article component or documented component set.
- [ ] Watertight where a solid is required.
- [ ] Consistent winding/normals.
- [ ] No degenerate faces, zero-area slivers, self-intersections, duplicated internal skins, or floating debris that affect the cavity.
- [ ] No accidental paper-thin walls or invisible internal cavities.
- [ ] Polygon count and minimum edge length are appropriate for the intended process.

For BREP/STEP:

- [ ] Valid solids, not only open shells.
- [ ] No invalid edges/faces or tiny residual topology from import.
- [ ] Assembly solids intentionally selected/fused/preserved.
- [ ] Curves and surfaces remain within modeling tolerance.

## Stage 2 — Process compatibility

- [ ] Final casting material identified.
- [ ] Working mold function identified: direct mold, master, case, core, insert, mother mold, or plaster working mold.
- [ ] Conventional ceramic slip-cast route uses an absorbent working face.
- [ ] Sealers/releases are assigned only to compatible interfaces.
- [ ] Material exotherm, water, chemical, temperature, and reuse requirements checked.
- [ ] Food-contact claims routed to final fired-object validation.

## Stage 3 — Compensation and dimensions

- [ ] Final dimensions are distinguished from green/tool dimensions.
- [ ] Shrinkage comes from exact body/process coupons or is explicitly marked provisional.
- [ ] X/Y/Z anisotropy considered.
- [ ] Coating, sanding, plaster tooling, seam finishing, and glaze effects considered.
- [ ] Calibration feature or gauge included where useful.
- [ ] Manifest records all scale factors.

## Stage 4 — Mold topology and demolding

For each mold part:

- [ ] Pull vector recorded.
- [ ] Removal order recorded.
- [ ] No unresolved undercut along the full extraction path.
- [ ] Draft appropriate to depth, texture, and material.
- [ ] Cast has a supported removal sequence.
- [ ] Closed loops and trapped cores resolved.
- [ ] Parting line avoids critical detail where practical.
- [ ] No plaster knife edges or fragile printed fins.
- [ ] Pry/lift features do not contact delicate cast surfaces.

A useful digital check is an incremental sweep:

1. duplicate the article and mold section;
2. move the mold section in 20–100 small steps along its pull vector;
3. check intersection at each step;
4. repeat for the cast removal path and intended shrinkage state.

## Stage 5 — Structure

- [ ] Minimum cavity-skin thickness meets the printer/material plan.
- [ ] Ribs support broad spans and clamp zones.
- [ ] Rib roots and flange transitions are radiused where possible.
- [ ] Flanges are flat, broad, and printable.
- [ ] Keys resist shear and rotation.
- [ ] Key/socket clearance is calibrated.
- [ ] Asymmetric registration prevents reversed assembly.
- [ ] Heavy mold sections have handles/lifting points.
- [ ] Closed structural voids have drain/inspection ports or are eliminated.

## Stage 6 — Fill, vent, drain, and cleaning

- [ ] Fill mode and actual gravity orientation recorded.
- [ ] Inlet reaches the cavity continuously.
- [ ] Reservoir remains above the highest required feed level.
- [ ] Every separated air pocket has a vent.
- [ ] Vents are printable and cleanable.
- [ ] Hollow slip cast can drain fully in a stable position.
- [ ] Open-face molds have overflow/screed control.
- [ ] No blind pocket traps liquid, slip, plaster, release, or wash water.
- [ ] Funnel/spout can be removed without breaking the cast rim.
- [ ] Leak-test method defined.

## Stage 7 — Resolution and memory

- [ ] Smallest required physical feature stated.
- [ ] Source/height-map pitch supplies at least 2–3 samples per smallest feature.
- [ ] Printer XY and layer-height capability can reproduce it.
- [ ] Tessellation tolerance is smaller than meaningful surface deviation but not wastefully small.
- [ ] Voxel/remesh memory estimate fits available RAM with operating margin.
- [ ] High detail is regional rather than global where possible.
- [ ] Detail coupon contains ridges, grooves, curvature, seam, and chosen finish.

## Stage 8 — Export and slicer

- [ ] Each mold part exported separately with stable naming.
- [ ] STEP retained for parametric/BREP designs.
- [ ] STL/3MF unit and dimensions verified.
- [ ] Mesh is manifold with positive volume.
- [ ] No unintended disconnected fragments.
- [ ] Slicer preview shows continuous cavity skin.
- [ ] No critical wall is omitted by minimum-feature rules.
- [ ] Orientation avoids supports on critical casting faces where possible.
- [ ] Bridges/overhangs are within qualified limits.
- [ ] Perimeters, top/bottom layers, infill/ribs, seam, and dimensional compensation documented.

## Stage 9 — Physical prototype ladder

Use the least expensive test that can fail first:

1. **Geometry slice:** 10–30 mm band through the hardest parting/undercut.
2. **Key/flange strip:** registration, clamping, gasket/release behavior.
3. **Detail coupon:** source → print → optional plaster transfer → cast → finish/glaze.
4. **Reduced-scale assembly:** checks part count and handling; do not infer full-scale stiffness blindly.
5. **Full-scale dry assembly:** no casting material.
6. **Water leak/fill/drain test:** only where tool materials tolerate it.
7. **Small material pour:** chemistry, exotherm, release, bubbles.
8. **Full production trial:** measured and documented.

## Stage 10 — Acceptance criteria

Define quantitative pass/fail criteria before testing. Example:

```yaml
dimensions:
  final_height_mm: 300.0
  tolerance_mm: 1.5
seams:
  max_flash_mm: 0.30
  visible_front_seam: false
detail:
  minimum_separated_groove_mm: 0.60
  recognizable_view_distance_mm: 500
demolding:
  mold_damage: none
  cast_chipping_count: 0
process:
  trapped_air_defects_over_1mm: 0
  complete_drain_time_s_max: 90
reuse:
  qualified_cycles: 10
```

## File/package audit

- [ ] `README` with process and assembly.
- [ ] Source CAD/mesh and neutral exports.
- [ ] Manifest with units, scale, shrinkage, version, part list, tolerances, and checksums.
- [ ] Render/exploded diagram with part IDs.
- [ ] Slicer profile or critical settings.
- [ ] Material product/SDS references and batch information.
- [ ] Test results and deviations.
- [ ] Cleaning, drying, storage, and retirement criteria.
