# OpenSCAD, CadQuery, FreeCAD, Blender

## Common rule

Every tool must consume the target heightmap with its physical width/height and X/Y pitch from metadata. Do not infer scale from raw PNG pixel aspect alone.

Generate dense geometry only where the physical height-field error requires it. Keep exact functional faces separate from reducible relief faces, and read `mesh-complexity-and-simplification.md` before exporting a high-density manufacturing mesh.

## OpenSCAD

Use explicit millimetre scaling. Native planar `surface()` workflows can be useful on flat maps, but curved wrapping is better performed with a pre-wrapped tool/mesh. If the geometry heightmap has non-square physical pixels, scale X and Y according to target millimetres—not according to image-viewer appearance.

Bound `$fn` and raster dimensions in preview mode. For large reliefs, create a validated adaptive cutter outside OpenSCAD rather than forcing `surface()` to represent every source pixel.

## CadQuery

Keep functional base geometry parametric. Dense image relief is often best as a separate mesh/surface tool. Any sampled relief coordinates must be generated from physical X/Y or metric surface distance before Boolean operations.

Retain STEP/B-Rep interfaces and simplify only the mesh cutter or final tessellation. Do not convert millions of relief triangles into a face-per-triangle B-Rep.

## FreeCAD

Retain physical scale during mesh import/conversion. Validate final dimensions and aspect after Boolean operations; do not rely on image DPI import behavior.

Keep precise datum/fit faces in the native body. Use mesh decimation only with measured deviation and protected boundaries; reimport and revalidate the manufacturing export.

## Blender

For single subjects, use a deliberately low-distortion UV patch or metric-aware local projection. Do not assume an undistorted-looking UV island preserves physical millimetres. For textures, triplanar/object-space projection can help uniform scale. Use enough mesh density before displacement and preserve the processed image as non-color data.

Prefer adaptive subdivision or a documented Decimate modifier on the relief surface set. A Decimate ratio is exploratory; production acceptance still requires a millimetre error measurement and checks for seams, bed planes, wall reserve, and relief amplitude.
