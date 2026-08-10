# OpenSCAD workflow

OpenSCAD is effective for deterministic CSG around a known mesh or a parametric master: blocks, simple shells, planar splits, ribs, funnels, vents, keys, and fixtures. It is less suitable for repairing arbitrary organic meshes or creating global constant-thickness offsets from dense scans.

## Recommended division of labor

Use OpenSCAD for:

- importing a validated STL/3MF master;
- scaling and positioning;
- subtracting it from block or shell-like tooling;
- clipping mold halves with half-spaces;
- adding external flanges, keys, clamp pads, gates, and vents;
- generating simple repeatable architectural geometry;
- deterministic command-line export.

Use Blender or a mesh-repair tool first when the source is non-manifold, self-intersecting, open, or extremely dense.

## Coordinate convention

Adopt one convention and document it. The included script assumes:

- millimetres;
- Z is vertical/fill direction;
- the master is centered near the origin;
- the default split plane is X = 0;
- positive Z is the sprue/reservoir direction.

## Basic block negative

```scad
module master() {
    import("master.stl", convexity=10);
}

module cavity_block() {
    difference() {
        translate([-60,-45,-5]) cube([120,90,130]);
        master();
    }
}
```

A valid result requires a closed, consistently oriented master mesh. OpenSCAD CSG can fail or produce missing surfaces when the imported STL is not a proper solid.

## Shrinkage scaling

Scale around a known datum, not blindly around the world origin:

```scad
sx = 1/(1-shrink_x/100);
sy = 1/(1-shrink_y/100);
sz = 1/(1-shrink_z/100);

translate(master_datum)
    scale([sx,sy,sz])
        translate(-master_datum)
            master();
```

The included script accepts `shrink_pct = [x,y,z]`. Use measured values.

## Shell approaches

### Bounding shell

For simple objects, subtract the master from a larger parametric envelope and then subtract an inner void outside a controlled cavity-skin region. This avoids a costly global offset.

### Minkowski offset

`minkowski()` with a sphere can create a morphological outer offset:

```scad
minkowski() {
    master();
    sphere(r=4, $fn=24);
}
```

This is computationally expensive on dense meshes and rounds all features. Use only on a decimated proxy or simple parametric master. It is not a guaranteed robust CAD offset for arbitrary scans.

### Ribbed shell

Create a coarse outer shell or bounding envelope, then add an external rib grid and flange. Keep ribs outside the cavity. The included `negative_mold.scad` demonstrates a printable approximation intended to be customized.

## Mold splitting

Clip the complete mold with large half-spaces:

```scad
module half_A() {
    intersection() {
        complete_mold();
        translate([-1000,-1000,-1000]) cube([1000,2000,2000]);
    }
}
```

Use overlap or a tiny epsilon only to avoid coplanar ambiguity; do not intentionally create mismatched cavity dimensions.

For a sculpted parting surface, create a closed cutter solid representing each side. OpenSCAD is practical only when that cutter is simple enough to model parametrically.

## Registration keys

Build male keys on one half and subtract slightly larger female sockets from the other. Use a lead-in taper and calibrated clearance.

```scad
module male_key(p=[0,0,0], r=4, h=3) {
    translate(p) cylinder(r1=r, r2=r-0.5, h=h, $fn=48);
}

module female_key(p=[0,0,0], r=4, h=3, c=0.25) {
    translate(p) cylinder(r1=r+c, r2=r-0.5+c, h=h+0.3, $fn=48);
}
```

Orient keys normal to the parting surface. Keep them out of the cast cavity.

## Funnels and vents

Subtract a tapered cone/cylinder from the assembled mold before splitting, or split the channel so each half contains half of it. Add a reservoir that remains above the highest cavity point in fill orientation.

OpenSCAD does not simulate flow. Verify every isolated high point manually or with a fluid/air-path review.

## Image relief

OpenSCAD `surface()` can generate a height field from an image, but large images create dense geometry and can consume substantial memory. Load `3d-print-heightmap-relief` and preprocess with its `scripts/prepare_heightmap.py`. Use local patches rather than wrapping a huge height field around the complete object.

For curved surfaces, generate the displacement mesh externally or model a cylindrical relief analytically. Repeated planar projection onto different faces changes the texture direction and creates discontinuities.

## Command-line use

Built-in demo:

```bash
openscad -o mold_A.stl -D 'part="A"' scripts/openscad/negative_mold.scad
openscad -o mold_B.stl -D 'part="B"' scripts/openscad/negative_mold.scad
```

Imported master:

```bash
openscad -o mold_A.stl \
  -D 'part="A"' \
  -D 'use_import=true' \
  -D 'master_file="/absolute/path/master.stl"' \
  -D 'master_size=[80,60,120]' \
  scripts/openscad/negative_mold.scad
```

OpenSCAD string/path quoting varies by shell; prefer an absolute path.

## Performance rules

- Keep `$fn` low during design and raise it only for final export.
- Use `$fa`/`$fs` or local facet counts rather than one excessive global `$fn`.
- Avoid repeated imports of the same dense mesh in nested modules.
- Split the mold before applying details that exist on only one half.
- Avoid global Minkowski and high-resolution `surface()` unless the memory estimate passes.
- Export each mold section independently.
- Use `render()` strategically to cache intermediate CSG only when it improves the design.

## Validation

After STL export, run:

```bash
python scripts/common/mesh_preflight.py mold_A.stl
python scripts/common/mesh_preflight.py mold_B.stl
```

Inspect both halves assembled in a mesh viewer and in the slicer. Confirm units, seam contact, key clearance, cavity continuity, and support strategy.
