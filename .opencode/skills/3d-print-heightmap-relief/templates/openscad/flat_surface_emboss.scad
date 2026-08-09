/*
Flat image relief in native OpenSCAD.

OpenSCAD surface() maps image gray values to nominal Z values 0..100.
Set the exact raster dimensions below; preserve aspect ratio deliberately.
For curved objects, generate a watertight patch with relief_patch.py and use
templates/openscad/imported_patch_boolean.scad instead.
*/
image_file = "heightmap.png";
image_width_px = 512;
image_height_px = 256;
physical_width_mm = 80;
physical_height_mm = 40;
relief_depth_mm = 0.8;
overlap_mm = 0.08;
invert_image = false;
operation = "engrave"; // "emboss" or "engrave"

base_width_mm = 90;
base_height_mm = 50;
base_thickness_mm = 3;

module native_height_solid(extra_depth = 0) {
    scale([
        physical_width_mm / max(1, image_width_px),
        physical_height_mm / max(1, image_height_px),
        (relief_depth_mm + extra_depth) / 100
    ])
        surface(file=image_file, center=false, invert=invert_image, convexity=20);
}

module base() {
    cube([base_width_mm, base_height_mm, base_thickness_mm]);
}

x0 = (base_width_mm - physical_width_mm) / 2;
y0 = (base_height_mm - physical_height_mm) / 2;

if (operation == "emboss") {
    union() {
        base();
        translate([x0, y0, base_thickness_mm - overlap_mm])
            native_height_solid(overlap_mm);
    }
} else {
    difference() {
        base();
        // Mirror so bright pixels extend down into the body.
        translate([x0, y0, base_thickness_mm + overlap_mm])
            mirror([0, 0, 1])
                native_height_solid(overlap_mm);
    }
}
