# Scripts

Run commands from the skill directory so local imports resolve naturally.

## `prepare_heightmap.py`

Physically aware image preprocessing.

```bash
python scripts/prepare_heightmap.py input.png output.png \
  --physical-width-mm 100 --physical-height-mm 50 \
  --sample-pitch-mm 0.25 --fit cover \
  --levels 1,99 --blur-mm 0.1 --bit-depth 16 \
  --preview preview.png --report report.json
```

Outputs can also include NumPy, OpenSCAD DAT, or SCAD array files.

## `analyze_heightmap.py`

Reports source pitch, seams, image statistics, relief slopes, small components, print-planning heuristics, and mesh working-set estimates.

## `relief_patch.py`

Reads `schemas/relief-config.schema.json`-compatible JSON and generates a closed STL/PLY/OBJ/GLB/OFF relief body.

Supported surfaces:

- plane;
- cylinder;
- cone/frustum;
- rounded rectangular wall;
- polygon wall;
- sphere band;
- torus;
- polygon ring plane;
- arbitrary `grid_npz`.

## `mesh_boolean.py`

Performs difference, union, or intersection. `--engine auto` attempts Manifold, Blender, then OpenSCAD.

## `validate_mesh.py`

Checks watertightness, winding, volume, body count, boundary/non-manifold edges, bounds, volume, and tiny faces.

## `generate_example_images.py`

Regenerates the procedural unicorn, carbon-fibre, and wood source height maps.

## `generate_mapping_test_image.py`

Creates an asymmetric orientation/seam test image.

## `build_examples.py`

Prepares images, generates CadQuery bases, creates relief cutters, runs Booleans, and writes a build summary.

## `self_test.py`

Runs 16-bit, mapping, topology, arbitrary-grid, CadQuery, and OpenSCAD tests where dependencies are available.

## Dependency behavior

Core scripts require NumPy, Pillow, SciPy, and trimesh. CadQuery, OpenSCAD, Blender, FreeCAD, and Manifold are optional. A report must never claim an optional backend was tested merely because a template exists.
