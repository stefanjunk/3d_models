# Case studies

## 1. Decorated dice tower

### Requirements decomposition

- protected: all visible ornament except inlet/outlet seam bands;
- removed: interior passage, top inlet, lower exit;
- added: staircase/baffles, lower landing interface, optional removable inspection panel;
- constraints: largest die envelope, remaining shell wall, stable base, printable support strategy.

### Preferred route

1. In Blender, fit the tower axis from 5–10 cross-sections.
2. Determine the minimum exterior radius per section.
3. Create a tapered/lofted interior cutter rather than assuming a perfect cylinder if residuals are large.
4. Generate staircase in CadQuery with step rise/run, rotation, clearance, and attachment ribs.
5. Subtract the union of interior and portal cutters in Blender/Manifold.
6. Union or mechanically retain the staircase.
7. Validate with a swept/animated dice clearance body and physical drop tests.

### Edge cases

- ornaments protrude inward as duplicated shells;
- roof is not actually closed;
- base courtyard is a separate disconnected component;
- lower portal removes the only structural bridge;
- internal staircase creates impossible supports.

## 2. Barefoot shoe

### Requirements decomposition

- source may mix sole and textile into one arbitrary surface;
- textile should be removed;
- sole region may be fully replaced or only internally replaced;
- upper attachment must be defined parametrically;
- zero drop, toe box, thickness, flex, and tread must be measurable.

### Preferred routes

**A. Reference-only rebuild:** derive footprint and seam; rebuild the sole. Safest for dimensional function.

**B. Skin-preserving:** retain a decorative outsole/sidewall skin, hollow its interior, fit a parametric core with adhesive/mechanical keys.

**C. Complete envelope replacement:** cut the entire model at a designed seam and union/attach the new sole.

Avoid selecting textile solely with `z > threshold` unless the seam is planar by design. Use manually recorded seam points and section curves.

### Validation

- no hidden old-sole fragments;
- no enclosed void between skin and core unless deliberately vented;
- minimum sidewall and outsole thickness;
- upper flange continuity;
- left/right mirroring does not erase anatomical asymmetry;
- bend and peel coupons pass.

## 3. Unicorn belly compartment

### Requirements decomposition

- cavity with minimum remaining wall;
- belly opening and door seam;
- separate door, liner, hinge/latch, and clearance;
- no sharp edges or inaccessible trapped support.

### Preferred route

1. Choose a rounded box/capsule aligned with the torso axis.
2. Compute safe cavity size from thickness samples.
3. Place seam along a natural belly contour.
4. Generate liner and door in CadQuery; use a Blender/SDF transition if the belly surface is strongly organic.
5. Subtract cavity and opening; union hinge supports only where wall reserve is adequate.
6. Validate door sweep with collision geometry and print hinge/latch coupons.

### Edge cases

- legs or internal decorative shells intrude into cavity;
- belly wall is locally too thin;
- hinge axis cannot be printed or assembled;
- door is a choking hazard for intended age;
- cavity traps uncured resin/water/support.
