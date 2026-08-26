# Worked examples

## Contents

1. [Toy: stylized dinosaur](#1-toy-stylized-dinosaur)
2. [Utility: wall-mounted cable clip](#2-utility-wall-mounted-cable-clip)
3. [Household: faceted ceramic planter](#3-household-faceted-ceramic-planter)

These examples demonstrate route selection and validation. Replace dimensions and print limits with project evidence; do not copy them as universal defaults.

## 1. Toy: stylized dinosaur

### Brief

Create a 90 mm-tall printable stylized dinosaur from a single three-quarter concept image plus a user-supplied side sketch. Preserve the oversized head, eye ridge, stance, and skin-color patches. Produce a monochrome FDM version and a textured GLB for review.

### Evidence and uncertainty

| Region | Evidence | Decision |
| --- | --- | --- |
| visible head/body silhouette | observed in concept image | high-confidence visual target |
| overall height | requested 90 mm | fixed scale |
| body depth | concept perspective + side sketch | medium confidence |
| far legs | partially occluded | mirror as first hypothesis, then pose for stable stance |
| back/tail underside | unseen | smooth simplest continuation, low confidence |
| skin pattern | observed color | texture/material only, not relief |
| eye ridge | changes silhouette/highlight | geometry |

Do not claim anatomical reconstruction. The result is a plausible design completion.

### Route

Use an image-to-3D model or Blender blockout to generate several organic bases. Use Blender for camera matching, sculpt correction, topology, and print preparation. Use a small CadQuery/FreeCAD construction only if a standardized keyed base or insert is required.

### Steps

1. Preserve sources and create clean masks with `preprocess_image.py`.
2. Build a perspective camera for the concept image and an orthographic camera for the side sketch.
3. Block head, torso, limbs, and tail as low-resolution masses. Ignore texture.
4. Compare concept and side silhouettes. Correct camera before sculpting local anatomy.
5. Generate or sculpt a base. Keep symmetry through the torso/head but allow stance asymmetry.
6. Check that all four feet touch a stable ground plane. Widen/contact-adjust feet only within the accepted silhouette budget.
7. Thicken claws, tail tip, and jaw/limb gaps according to the measured FDM coupon.
8. Remove mouth gaps that trap support or split the model if they are important and inaccessible.
9. Create a watertight print mesh; retain the sculpt master separately.
10. UV unwrap the review mesh and project/repaint color patches without baked highlights.
11. Export GLB for appearance and binary STL/3MF for print geometry.

### Memory plan

- L0 blockout: under roughly 20k faces.
- L1 sculpt/working mesh: choose resolution that captures the eye ridge and toes, not skin pixels.
- L2 print mesh: decimate/remesh until matched-view silhouette and ridge/toe geometry remain unchanged at the 90 mm target.
- Texture: preserve higher resolution independently of the print mesh.

Avoid a multi-million-face print mesh merely because the AI output contains pores that the FDM process cannot reproduce.

### Validation

Digital:

- matched concept and side silhouette;
- landmarks at snout, eye, hip, knee, feet, and tail tip;
- stable footprint and center of mass;
- no non-manifold/internal shells;
- slicer retains gaps between limbs and the eye ridge;
- no unsafe needle-like tips for the intended handling context.

Physical:

- print a 45 mm half-scale draft only if feature scaling remains meaningful, otherwise print a low-infill full-scale shell;
- check stance, tail/limb fragility, support scars on the face, and perceived proportions;
- revise under-foot contact and thin features without silently changing the visual target.

### Acceptance note

Report the unseen back and far-side anatomy as designed, not recovered. Report that color in the GLB is reference appearance unless the chosen 3MF/slicer/material workflow reproduces it.

## 2. Utility: wall-mounted cable clip

### Brief

Reconstruct a small cable clip from a front product photo, side photo with ruler, and measured cable diameter range. The clip screws to a wall, opens elastically, and must retain a 5.0–5.5 mm cable. Print in PETG with a 0.4 mm nozzle.

### Requirement ledger excerpt

| ID | Requirement | Evidence | Priority |
| --- | --- | --- | --- |
| REQ-001 | Cable diameter range 5.0–5.5 mm | requested/measured | critical |
| REQ-002 | Mounting hole center 8.0 mm from rear datum | ruler photo, confirm physically | critical |
| REQ-003 | Outside silhouette matches product photo | observed | important |
| REQ-004 | Clip arm opens without permanent set | requested | critical |
| REQ-005 | Front logo/color is cosmetic | observed | cosmetic |

The image does not determine PETG modulus, screw load, layer adhesion, or long-term creep. Treat structural dimensions as a redesign requiring testing.

### Route

Use CadQuery or FreeCAD as primary. Use the images as scaled references for envelope and style; drive the cable channel, flexure, mounting hole, and wall thickness from explicit parameters. OpenSCAD is also viable for a simpler CSG/2D-profile design.

### Steps

1. Correct/qualify photo perspective; use the ruler only if it lies in the same plane as the measured feature.
2. Establish the rear mounting face as datum, cable axis as a second datum, and symmetry plane.
3. Trace the outer side profile with a small number of arcs/lines.
4. Parameterize cable diameter, insertion opening, arm thickness, root radius, screw hole, countersink/counterbore, base thickness, and printer compensation.
5. Model nominal geometry first. Keep compensation parameters separate.
6. Add generous root fillet and choose print orientation based on flexure layer direction and screw load.
7. Generate a coupon containing several channel diameters, opening widths, and arm thicknesses.
8. Export STEP master and test STL/3MF at moderate tessellation.
9. Measure coupon behavior, then update compensation and final parameters.

### Suggested parameter scheme

```text
cable_max_mm = 5.5             requested
channel_nominal_mm = 5.7       initial hypothesis; coupon-controlled
opening_mm = 4.6               initial hypothesis; coupon-controlled
arm_thickness_mm = 1.8         structural hypothesis
root_radius_mm = 2.0           fatigue/stress hypothesis
base_thickness_mm = 3.0        structural hypothesis
hole_diameter_mm = measured screw + compensation
```

These values illustrate traceability, not validated design values.

### Validation

Geometry:

- critical dimensions in CAD and exported mesh;
- continuous material at flexure root;
- no tangent/zero-thickness Boolean artifacts;
- mounting screw head and tool access;
- cable insertion path, not only final channel size.

Slicer:

- count perimeters across the flexure and base;
- inspect layer direction at the flexure root;
- confirm small opening is not auto-closed;
- inspect seam placement and hole compensation.

Physical:

- test 5.0, 5.5, and 6.0 mm gauges/cables;
- cycle insertion/removal a declared number of times;
- test wall mounting with the actual screw/washer and a safe load protocol;
- check creep after a defined dwell if retention matters.

Do not certify a load or child-safety use from image comparison.

### Visual comparison

Render the photo cameras and compare the outer shell only after critical function passes. If a thicker root changes the silhouette, report the redesign deviation and let the user choose between visual identity and durability.

## 3. Household: faceted ceramic planter

### Brief

Create a 160 mm-tall planter from eight overlapping photos. The planter is rotationally regular at the rim but has a repeating faceted/fluted exterior. Add a drainage hole and a detachable saucer. Preserve the matte blue appearance for review, but produce a single-material FDM print master.

### Evidence and uncertainty

- Overall height and rim diameter come from physical measurement.
- Exterior profile and facet phase come from multiple photographs.
- Wall thickness and internal bottom are not visible; redesign them for printing/use.
- Blue color is appearance evidence, not geometry.
- Subtle mottling may be glaze/lighting and should not become full-frequency relief.

### Route alternatives

**Parametric-first:** Use CadQuery/FreeCAD/OpenSCAD when the flutes repeat around a known axis. Trace a vertical profile, model a rotational body, and apply periodic facet/flute geometry.

**Photogrammetry-first:** Use COLMAP/Meshroom when the actual handmade irregularity matters and the surface has enough stable texture. Scale and regularize the interior afterward.

**Hybrid choice:** Use photogrammetry for the outer shell, fit the main axis/rim plane, and replace the unseen interior, base, drainage, and saucer interface parametrically.

Select based on whether irregularity is a requirement or noise.

### Parametric workflow

1. Segment images and recover/estimate cameras.
2. Fit the center axis and measured rim/bottom planes.
3. Extract radius-versus-height profile from several views; average only if rotational symmetry is intended.
4. Determine facet/flute count and angular phase from top/three-quarter views.
5. Build one periodic sector and pattern/revolve it.
6. Create a controlled inner surface with printable wall and bottom thickness.
7. Add drainage hole, underside feet, and a saucer locating feature.
8. Keep glaze color/mottling in Blender material or choose filament/paint separately.

### Photogrammetry/hybrid workflow

1. Check photos for overlap, reflections, weak texture, and background consistency.
2. Reconstruct sparse cameras and dense exterior.
3. Remove table/background fragments and scale from two independent dimensions.
4. Fit rim plane/axis and compare cross-sections.
5. Preserve a raw scan; create a reduced clean outer mesh.
6. Cut the unreliable top opening/bottom cleanly.
7. Model interior, base, hole, and saucer interface in CAD.
8. Combine with controlled overlap; avoid triangle-to-BRep conversion of the entire scan.
9. Compare before/after outer silhouettes and surface deviation.

### Resolution and memory

Do not retain full photo resolution throughout dense reconstruction if it exceeds available VRAM/RAM without visible benefit. Run a medium-resolution subset first. Preserve high-resolution images for texture and a final region-of-interest reconstruction.

For a procedural facet pattern, analytic CAD is far more memory-efficient than a dense displacement map. For irregular glaze mottling, use color texture. For tactile flutes, model geometry at sector/profile resolution and tessellate at export.

### Validation

Visual:

- rim ellipse and overall profile in every photo view;
- facet count, phase, and depth;
- base proportion and visible foot gap;
- matte blue appearance in a separate controlled render.

Geometry/function:

- rim diameter and circularity/intentional irregularity;
- wall and bottom thickness;
- drainage cross-section and no trapped internal volume;
- saucer clearance and water capacity;
- stable footprint and center of mass.

Print:

- slicer perimeter continuity through flutes;
- seam placement away from a key front face;
- bridge/support need around drainage and saucer lip;
- warp risk at the base;
- test a short rim/flute band and saucer-fit ring before the full-height print.

### Acceptance note

Deliver separate claims: the exterior is reconstructed to the selected view/dimension tolerances; the interior and drainage are an engineered redesign; blue glaze is an appearance reference unless a validated material/painting method is included.
