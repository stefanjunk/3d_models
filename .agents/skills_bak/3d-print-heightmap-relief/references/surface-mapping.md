# Metric-aware surface mapping

## Plane / cube face

Use physical X/Y coordinates directly. A 20×20 mm square in the heightmap must measure 20×20 mm on the final face.

If artwork continues over a sharp cube corner, decide deliberately whether to split it into separate face charts. A single subject should usually remain on one face; a texture may use coordinated face projections.

## Cylinder

Use arc length, not raw angle, for horizontal image distance:

`s = R * theta`  (theta in radians)

For desired physical image width `W` on radius `R`:

`theta = W / R` radians.

If the image is a front patch, center this angular span on the viewing direction. If it is a full-wrap texture, map the whole circumference `2*pi*R` and place the seam intentionally.

The heightmap X sampling follows arc-length millimetres. Y typically follows cylinder Z.

## Rounded rectangle / rounded box

Build one continuous perimeter coordinate measured in millimetres:
- straight front length;
- fillet arc length `r*theta`;
- side length;
- next fillet, etc.

Do not map each face independently if a texture or band should remain continuous. For a portrait/logo on the front, use a bounded planar/front patch and stop/fade before the corner instead.

## Cone / frustum

A conical surface unwraps to a sector. Circumference varies with height, so full-width rectangular UV mapping can deform subjects. Use a bounded local patch for recognizable art; reserve full unwrap for textures/bands designed for it.

## Sphere

A standard longitude/latitude UV has changing horizontal physical scale:

`ds_longitude = R*cos(latitude)*dlongitude`.

Therefore a rectangle in UV space is not generally a rectangle in millimetres, especially near poles.

For a person/animal/logo, use a bounded front patch around a low-distortion region and evaluate actual surface lengths. Avoid poles. For a forgiving global texture, full UV mapping can be acceptable if distortion is expected.

## Ellipsoid

Ellipsoids have position-dependent metric scale in both parameter directions. Treat recognizable images as bounded local surface patches. Use a local tangent/normal projection, geodesic-aware tool, or carefully reviewed UV unwrap rather than assuming a rectangular UV island preserves millimetres.

## Arbitrary freeform / Blender UV

UV coordinates define correspondence, not physical scale. Inspect the UV-to-surface Jacobian or at least measure known reference distances after displacement. For single subjects, deliberately unwrap a low-distortion patch. For repeating textures, triplanar/object-space mapping may provide more uniform scale but can introduce its own seam/blend behavior.

## Surface-normal displacement

Once the 2D physical placement is correct, relief depth is applied along an appropriate normal field. Large emboss/engrave depths on tight curvature can self-intersect or change apparent scale near steep normals; validate the final mesh.

## Diagnostic map

Map a known circle/square through the same production mapping. Measure on the final surface, not only in UV or raster space.
