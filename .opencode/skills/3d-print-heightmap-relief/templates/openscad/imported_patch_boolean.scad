/*
Boolean a closed relief patch against an existing base STL.

Create the patch:
  python ../../scripts/relief_patch.py relief-config.json relief-patch.stl

For engraving use difference(); for embossing change it to union().
Keep the patch protruding across the base surface by relief.overlap_mm.
*/
base_file = "base.stl";
relief_file = "relief-patch.stl";
operation = "engrave"; // "engrave" or "emboss"

module base_mesh() {
    import(base_file, convexity=20);
}
module relief_mesh() {
    import(relief_file, convexity=20);
}

render(convexity=20)
if (operation == "engrave") {
    difference() {
        base_mesh();
        relief_mesh();
    }
} else {
    union() {
        base_mesh();
        relief_mesh();
    }
}
