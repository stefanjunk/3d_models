# Alignment, fitting, and replacement shapes

## Coordinate-frame discipline

Record a right-handed coordinate frame in the project specification:

- origin landmark;
- up axis;
- forward axis;
- left/right convention;
- units;
- transform from source file to working frame.

Apply object scale/rotation before Boolean operations. Save the transform matrix. Do not trust the imported file's axes or STL units.

## Landmark hierarchy

Use the strongest available registration evidence in this order:

1. explicit mechanical datums or known dimensions;
2. manually marked landmarks;
3. planar or cylindrical fitted regions;
4. multiple cross-section centroids and outlines;
5. principal axes/PCA;
6. bounding box alone.

PCA is only an initial guess. Symmetry, appendages, and decorative mass can rotate principal axes away from the intended functional axis.

## Cross-section fitting

For towers and shoe soles, sample many parallel slices. For each section record:

- centroid;
- area;
- minimum and maximum radius from candidate axis;
- fitted circle/ellipse residual;
- protected-wall distance;
- local seam position.

A cylinder is appropriate only if the residual and wall reserve are acceptable through the full height. Otherwise use a tapered cylinder, loft, spline tube, or capsule.

## Common replacement/cutter forms

### Cylinder or tube

Use for dice towers, bottle cavities, shafts, ducts, hinge bosses, and round sockets. Fit axis and radius from several sections. A single bounding cylinder can breach thin decorative walls.

### Box or rounded box

Use for electronics, drawers, battery bays, flat doors, and mounting blocks. Rounded boxes reduce stress concentration and are more compatible with organic shells.

### Capsule

Use for elongated cavities in toys, handles, limbs, and bellies. It avoids sharp internal corners and distributes wall thickness more smoothly.

### Cone or tapered loft

Use where the organic body changes section gradually. Good for tower interiors, horns, shoe sidewalls, and insertion paths.

### Section-driven loft

Use for shoe soles and irregular tunnels. Derive 2D outlines at known stations, simplify them, and loft in CadQuery/FreeCAD/Blender. Keep section order and correspondence stable.

### Offset shell

Use for uniform wall thickness. In mesh workflows use Solidify only after checking self-intersections; for complex geometry use an SDF level-set offset.

### Swept path

Use for cable channels, dice chutes, fluid ducts, and latch paths. Define centerline, cross-section, bend radius, and clearance envelope.

### Convex hull or blended SDF

Use for forgiving internal voids and transitions. A smooth union can avoid thin sliver geometry but changes dimensions; validate the blend radius.

## Fit and interface allowances

Separate these values:

- geometric clearance;
- printer/process compensation;
- adhesive gap;
- assembly lead-in;
- motion clearance;
- registration uncertainty;
- decorative shell reserve.

A robust interface normally includes a lead-in chamfer, overlap or shoulder, anti-rotation feature, and a repeatable datum. Avoid relying on an organic surface as the only datum.

## Protected-wall fitting

To prevent a cutter from breaching exterior walls:

1. define desired minimum remaining wall `w_min`;
2. add model uncertainty `u` and Boolean tolerance `e`;
3. require cutter-to-exterior distance at every critical point to exceed `w_min + u + e`;
4. inspect sections around the full path, not only nearest vertices;
5. verify final thickness with ray or maximal-sphere sampling.

## Seam selection

Prefer seams that are:

- hidden by existing ornament, fur, clothing, sole sidewall, or belly contour;
- approximately planar or smoothly developable;
- accessible for adhesive, screws, pins, or stitching;
- away from maximum bending stress;
- wide enough for a flange;
- printable without trapped supports.
