# OpenSCAD-specific workflow

OpenSCAD is effective when the imported mesh is already clean and the operation can be expressed as robust CSG.

## Pattern

```scad
$fn = 96;
eps = 0.2;

module source_mesh() {
    import("source-clean.stl", convexity=20);
}

module cutter() {
    translate([0,0,-eps])
        cylinder(h=120 + 2*eps, r=28);
}

difference() {
    source_mesh();
    cutter();
}
```

Use F6/CLI render for the actual result; preview is not proof of successful CGAL geometry.

## Best uses

- simple cylindrical/box/capsule cavities;
- regular stairs or baffles;
- repeatable holes and ports;
- separate inserts and calibration coupons;
- quick parameter sweeps.

## Limits

- imported mesh must be manifold and free of holes/self-intersections for reliable CSG;
- dense imports and many Booleans can render slowly and consume substantial memory;
- OpenSCAD is not a visual segmentation or repair environment;
- no STEP master for the final imported-mesh composite;
- conformal surface fitting is limited.

Generate the functional insert in OpenSCAD, export it, and integrate in Blender/Manifold when the source mesh is difficult.

The package includes `scripts/openscad_boolean.py` as a logged CLI path for clean meshes. It validates that an output mesh exists and is watertight, but the same protected-region and section checks remain mandatory.
