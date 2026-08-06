// Diagnostic cutaway generated from the actual final STL reloaded from disk.
include <generated_parameters.scad>
preview_geometry_mode = is_undef(preview_geometry_mode) ? "cutaway" : preview_geometry_mode;

module actual_final() {
    import(final_mesh_path, convexity = 32);
}

module actual_cutaway() {
    difference() {
        actual_final();
        // Remove X<0 and retain X>=0. Camera looks into the exposed X=0 section.
        translate([-100, -100, -2]) cube([100, 200, 204], center = false);
    }
}

if (preview_geometry_mode == "cutaway") {
    actual_cutaway();
} else {
    actual_final();
}
