// Functional Unicorn Dice Tower - spiral staircase interior (v2)
// Authoritative dimensions are generated from parameters.json.
include <generated_parameters.scad>

render_mode = is_undef(render_mode) ? "final" : render_mode;
$fn = is_undef(preview_fn) ? render_fn : preview_fn;

module rounded_rect_2d(width, height, radius) {
    offset(r = radius)
        square([width - 2 * radius, height - 2 * radius], center = true);
}

module radial_rounded_opening(center_y, center_z, depth, width, height, radius) {
    translate([core_center_x, center_y, center_z])
        rotate([90, 0, 0])
            linear_extrude(height = depth, center = true, convexity = 12)
                rounded_rect_2d(width, height, radius);
}

module core_void() {
    translate([core_center_x, core_center_y, core_start_z])
        scale([core_rx, core_ry, 1])
            cylinder(r = 1, h = core_end_z - core_start_z, center = false);
}

module inlet_void() {
    radial_rounded_opening(
        inlet_center_y, inlet_center_z, inlet_depth,
        inlet_width, inlet_height, inlet_radius
    );
}

module outlet_void() {
    radial_rounded_opening(
        outlet_center_y, outlet_center_z, outlet_depth,
        outlet_width, outlet_height, outlet_radius
    );
}

// ---- Spiral staircase -------------------------------------------------
// Descending parameter t (degrees): 90 -> -780 (2.4167 turns clockwise
// when viewed from above). Top surface height is linear in t. The outer
// edge overlaps the shell by spiral_out_r - core_r so the slide is fused
// into the wall everywhere. The inner edge floats; the inner void is
// smaller than a die so nothing can fall through it.

function spiral_z_of_t(t) =
    spiral_z_top - (spiral_z_top - spiral_z_end) * ((spiral_t_start - t) / (spiral_t_start - spiral_t_end));

function spiral_point(t, rx, ry) =
    [core_center_x + rx * cos(t), core_center_y + ry * sin(t), 0];

module rounded_post(center_xy, center_z, thickness, edge_r) {
    hull() {
        translate([center_xy[0], center_xy[1], center_z + (thickness / 2 - edge_r)])
            sphere(r = edge_r);
        translate([center_xy[0], center_xy[1], center_z - (thickness / 2 - edge_r)])
            sphere(r = edge_r);
    }
}

module spiral_tread_facet(t_high, t_low) {
    z_high = spiral_z_of_t(t_high);
    z_low = spiral_z_of_t(t_low);
    in_high = spiral_point(t_high, spiral_in_rx, spiral_in_ry);
    out_high = spiral_point(t_high, spiral_out_rx, spiral_out_ry);
    in_low = spiral_point(t_low, spiral_in_rx, spiral_in_ry);
    out_low = spiral_point(t_low, spiral_out_rx, spiral_out_ry);
    hull() {
        rounded_post(in_high,  z_high - spiral_thickness / 2, spiral_thickness, spiral_edge_radius);
        rounded_post(out_high, z_high - spiral_thickness / 2, spiral_thickness, spiral_edge_radius);
        rounded_post(in_low,   z_low  - spiral_thickness / 2, spiral_thickness, spiral_edge_radius);
        rounded_post(out_low,  z_low  - spiral_thickness / 2, spiral_thickness, spiral_edge_radius);
    }
}

module spiral_staircase() {
    $fn = spiral_fn;
    dt = (spiral_t_start - spiral_t_end) / spiral_facets;
    for (i = [0 : spiral_facets - 1]) {
        t_high = spiral_t_start - i * dt + spiral_facet_overlap;
        t_low = spiral_t_start - (i + 1) * dt - spiral_facet_overlap;
        spiral_tread_facet(t_high, t_low);
    }
}

module hollowed_exterior() {
    difference() {
        import(source_mesh_path, convexity = 24);
        core_void();
        inlet_void();
        outlet_void();
    }
}

module final_model() {
    // Openings are subtracted again after the union so they stay completely open.
    difference() {
        union() {
            hollowed_exterior();
            spiral_staircase();
        }
        inlet_void();
        outlet_void();
    }
}

module die_cube(index) {
    translate(die_path[index])
        rotate([0, 0, die_pose[index][0]])
            rotate([0, die_pose[index][1], 0])
                cube([die_size, die_size, die_size], center = true);
}

module die_sweep() {
    for (i = [0 : len(die_path) - 2])
        hull() {
            die_cube(i);
            die_cube(i + 1);
        }
}

module cutaway_model() {
    difference() {
        final_model();
        // Remove the -X half only for visual inspection; this is never the final STL.
        translate([-100, -100, -1]) cube([100, 200, 220], center = false);
    }
}

if (render_mode == "final") {
    final_model();
} else if (render_mode == "shell_only") {
    hollowed_exterior();
} else if (render_mode == "cutaway") {
    cutaway_model();
} else if (render_mode == "cutaway_with_path") {
    color([0.74, 0.58, 0.92, 1.0]) cutaway_model();
    color([1.0, 0.35, 0.05, 0.55]) die_sweep();
} else if (render_mode == "die_path") {
    die_sweep();
} else {
    assert(false, str("Unknown render_mode: ", render_mode));
}
