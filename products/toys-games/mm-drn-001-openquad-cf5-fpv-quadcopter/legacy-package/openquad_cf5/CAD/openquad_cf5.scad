// OpenQuad CF5 - parametric hybrid 5-inch quadcopter prototype
// SPDX-License-Identifier: CERN-OHL-P-2.0
// Units: millimetres. Coordinate system: +Z up.
//
// This is an experimental airframe, not a certified or flight-proven product.
// Export each printable item by changing `part` below and rendering with F6.

part = "assembly";
// assembly | hub_bottom | hub_top | battery_deck | motor_saddle |
// motor_plate | retention_plug | arm_fit_coupon | print_layout

$fn = 72;

// --- Design basis ---------------------------------------------------------
wheelbase = 230;                 // opposing motor centres
motor_radius = wheelbase / 2;
prop_diameter = 129.7;           // Gemfan 51433 envelope; 5.1 inch

arm_outer = 10.0;                // square CF tube outside
arm_inner = 8.0;                 // square CF tube inside
arm_clearance = 0.25;            // total channel clearance; tune by coupon
arm_inner_radius = 12.0;         // inner end of CF tube from frame centre
arm_length = motor_radius - arm_inner_radius;

hub_size = 86;
hub_corner_radius = 8;
plate_thickness = 3.0;
guide_height = 2.0;
guide_width = 2.0;
hub_window_radius = 8.0;         // bottom plate only in selected version

clamp_radial = 30;
clamp_lateral = 10;
clamp_hole = 3.4;
clamp_boss_diameter = 7.2;
// Bosses stop just short of the nominal tube height. This creates controlled
// plate preload without asking the printed plates to crush the CF tube.
clamp_gap = 0.15;
clamp_boss_height = arm_outer - clamp_gap;

fc_hole_spacing = 30.5;
fc_hole = 3.5;

deck_length = 80;
deck_width = 52;
deck_corner_radius = 5;
deck_hole_x = 32;
deck_hole_y = 20;
deck_hole = 3.4;
deck_thickness = 3.0;
deck_standoff_height = 25;       // common COTS female-female M3 size

motor_pattern = 16;              // set 19 for a 19 x 19 mm motor
motor_hole = 3.25;
motor_centre_hole = 8.0;
motor_plate_thickness = 3.6;
motor_disk_diameter = 36;
motor_tongue_length = 28;
motor_tongue_width = 26;
// Keep pod-clamp holes clear of both 16 x 16 and optional 19 x 19 motor holes.
motor_clamp_x = [-22, -16];
motor_clamp_y = [-9, 9];

saddle_length = 28;
saddle_width = 26;
saddle_base = 3.0;
// Side rails are 0.15 mm lower than the nominal tube. The through-bolted
// motor plate therefore preloads the tube instead of bottoming on the rails.
saddle_height = saddle_base + arm_outer - clamp_gap;

plug_shank = arm_inner - 0.35;
plug_length = 10;
plug_flange = arm_outer + 2.0;
plug_flange_thickness = 2.0;

// --- Shared helpers -------------------------------------------------------
module rounded_rect_2d(size = [10, 10], radius = 2) {
    offset(r = radius)
        square([size[0] - 2 * radius, size[1] - 2 * radius], center = true);
}

module through_hole(d, h = 50) {
    translate([0, 0, -1]) cylinder(d = d, h = h + 2);
}

module clamp_points() {
    for (angle = [0, 90, 180, 270])
        for (side = [-1, 1])
            rotate([0, 0, angle])
                translate([clamp_radial, side * clamp_lateral, 0])
                    children();
}

module fc_points() {
    for (x = [-fc_hole_spacing / 2, fc_hole_spacing / 2])
        for (y = [-fc_hole_spacing / 2, fc_hole_spacing / 2])
            translate([x, y, 0]) children();
}

module deck_points() {
    for (x = [-deck_hole_x, deck_hole_x])
        for (y = [-deck_hole_y, deck_hole_y])
            translate([x, y, 0]) children();
}

module front_arrow_2d() {
    // The aircraft's declared forward direction is between the +X and +Y arms.
    rotate([0, 0, 45])
        translate([24, 0])
            polygon(points = [
                [-8, -2.5], [1, -2.5], [1, -5], [9, 0],
                [1, 5], [1, 2.5], [-8, 2.5]
            ]);
}

module hub_outline_2d() {
    rounded_rect_2d([hub_size, hub_size], hub_corner_radius);
}

// --- Hub -----------------------------------------------------------------
module hub_bottom() {
    difference() {
        union() {
            linear_extrude(height = plate_thickness)
                difference() {
                    hub_outline_2d();
                    for (x = [-29, 29])
                        for (y = [-29, 29])
                            translate([x, y]) circle(r = hub_window_radius);
                }

            // Two short guide rails per arm: square tube cannot rotate, while
            // the inner plug flange catches the rail ends as secondary retention.
            for (angle = [0, 90, 180, 270])
                rotate([0, 0, angle]) {
                    for (side = [-1, 1])
                        translate([
                            (arm_inner_radius + hub_size / 2) / 2,
                            side * (arm_outer / 2 + arm_clearance / 2 + guide_width / 2),
                            plate_thickness
                        ])
                            cube([
                                hub_size / 2 - arm_inner_radius,
                                guide_width,
                                guide_height
                            ], center = true);
                }

            // Compression stops / screw bosses.
            clamp_points()
                translate([0, 0, plate_thickness])
                    cylinder(d = clamp_boss_diameter, h = clamp_boss_height);
        }

        clamp_points() through_hole(clamp_hole, plate_thickness + clamp_boss_height);
    }
}

module hub_top() {
    difference() {
        linear_extrude(height = plate_thickness) hub_outline_2d();
        clamp_points() through_hole(clamp_hole, plate_thickness);
        fc_points() through_hole(fc_hole, plate_thickness);
        deck_points() through_hole(deck_hole, plate_thickness);

        // Shallow, geometric orientation mark. Never rely on a numeric yaw
        // value alone: verify the configurator's 3D model with props removed.
        translate([0, 0, plate_thickness - 0.55])
            linear_extrude(height = 1.0) front_arrow_2d();
    }
}

// --- Battery deck ---------------------------------------------------------
module strap_slot_2d(length = 13, width = 3.5) {
    rounded_rect_2d([length, width], width / 2);
}

module battery_deck() {
    difference() {
        linear_extrude(height = deck_thickness)
            rounded_rect_2d([deck_length, deck_width], deck_corner_radius);

        deck_points() through_hole(deck_hole, deck_thickness);

        // Two straps; all four deck screws stay outside a 74 x 33 mm battery.
        for (x = [-22, 22])
            for (y = [-17, 17])
                translate([x, y, -1])
                    linear_extrude(height = deck_thickness + 2)
                        strap_slot_2d();
    }
}

// --- Motor clamp ----------------------------------------------------------
module motor_saddle() {
    difference() {
        translate([-saddle_length, -saddle_width / 2, 0])
            cube([saddle_length, saddle_width, saddle_height]);

        // Open-top channel. The tube is visible and inspectable after assembly.
        translate([
            -saddle_length - 0.2,
            -(arm_outer + arm_clearance) / 2,
            saddle_base
        ])
            cube([
                saddle_length + 0.4,
                arm_outer + arm_clearance,
                arm_outer + 0.5
            ]);

        for (x = motor_clamp_x)
            for (y = motor_clamp_y)
                translate([x, y, 0]) through_hole(clamp_hole, saddle_height);
    }
}

module motor_plate_2d() {
    union() {
        circle(d = motor_disk_diameter);
        translate([-motor_tongue_length / 2, 0])
            square([motor_tongue_length, motor_tongue_width], center = true);
    }
}

module motor_plate() {
    difference() {
        linear_extrude(height = motor_plate_thickness) motor_plate_2d();
        through_hole(motor_centre_hole, motor_plate_thickness);

        for (x = [-motor_pattern / 2, motor_pattern / 2])
            for (y = [-motor_pattern / 2, motor_pattern / 2])
                translate([x, y, 0]) through_hole(motor_hole, motor_plate_thickness);

        for (x = motor_clamp_x)
            for (y = motor_clamp_y)
                translate([x, y, 0]) through_hole(clamp_hole, motor_plate_thickness);
    }
}

// --- Secondary arm retention and fit coupon ------------------------------
module retention_plug() {
    // Print flange-down. Tune plug_shank for the supplier's actual ID.
    linear_extrude(height = plug_flange_thickness)
        rounded_rect_2d([plug_flange, plug_flange], 1.2);
    translate([0, 0, plug_flange_thickness])
        linear_extrude(height = plug_length, scale = 0.96)
            rounded_rect_2d([plug_shank, plug_shank], 0.8);
}

module arm_fit_coupon() {
    coupon_length = 20;
    difference() {
        translate([-coupon_length / 2, -saddle_width / 2, 0])
            cube([coupon_length, saddle_width, saddle_height]);
        translate([
            -coupon_length / 2 - 0.2,
            -(arm_outer + arm_clearance) / 2,
            saddle_base
        ])
            cube([
                coupon_length + 0.4,
                arm_outer + arm_clearance,
                arm_outer + 0.5
            ]);
    }
}

// --- Non-printing assembly reference -------------------------------------
module carbon_tube(length = arm_length) {
    difference() {
        cube([length, arm_outer, arm_outer]);
        translate([-0.1, (arm_outer - arm_inner) / 2, (arm_outer - arm_inner) / 2])
            cube([length + 0.2, arm_inner, arm_inner]);
    }
}

module dummy_motor() {
    color([0.35, 0.38, 0.42]) {
        cylinder(d = 28, h = 17);
        translate([0, 0, 17]) cylinder(d = 5, h = 12);
    }
}

module assembly() {
    color([0.96, 0.48, 0.12]) hub_bottom();

    for (angle = [0, 90, 180, 270]) {
        rotate([0, 0, angle]) {
            color([0.07, 0.08, 0.09])
                translate([arm_inner_radius, -arm_outer / 2, plate_thickness])
                    carbon_tube();

            translate([motor_radius, 0, 0]) {
                color([0.96, 0.48, 0.12]) motor_saddle();
                color([1.0, 0.62, 0.18])
                    translate([0, 0, saddle_height]) motor_plate();
                translate([0, 0, saddle_height + motor_plate_thickness]) dummy_motor();
                color([0.1, 0.7, 0.9, 0.16])
                    translate([0, 0, saddle_height + motor_plate_thickness + 29])
                        cylinder(d = prop_diameter, h = 0.7);
            }
        }
    }

    color([1.0, 0.62, 0.18])
        translate([0, 0, plate_thickness + arm_outer]) hub_top();

    // Flight stack placeholders (30.5 x 30.5 mount).
    color([0.18, 0.55, 0.30, 0.75])
        translate([-19.5, -19.5, plate_thickness + arm_outer + plate_thickness + 3])
            cube([39, 39, 4.5]);
    color([0.18, 0.35, 0.65, 0.75])
        translate([-19.5, -19.5, plate_thickness + arm_outer + plate_thickness + 11])
            cube([39, 39, 4.5]);

    deck_points()
        color([0.65, 0.65, 0.68])
            translate([0, 0, plate_thickness + arm_outer + plate_thickness])
                cylinder(d = 5, h = deck_standoff_height);

    color([1.0, 0.62, 0.18])
        translate([
            0, 0,
            plate_thickness + arm_outer + plate_thickness + deck_standoff_height
        ])
            battery_deck();
}

module print_layout() {
    translate([-52, 0, 0]) hub_bottom();
    translate([52, 0, 0]) hub_top();
    translate([0, 68, 0]) battery_deck();
    for (i = [0:3])
        translate([-42 + i * 28, -68, 0]) motor_saddle();
    for (i = [0:3])
        translate([-42 + i * 28, -105, 0]) motor_plate();
    for (i = [0:3])
        translate([-42 + i * 28, -130, 0]) retention_plug();
}

// --- Part selector --------------------------------------------------------
if (part == "assembly") assembly();
else if (part == "hub_bottom") hub_bottom();
else if (part == "hub_top") hub_top();
else if (part == "battery_deck") battery_deck();
else if (part == "motor_saddle") motor_saddle();
else if (part == "motor_plate") motor_plate();
else if (part == "retention_plug") retention_plug();
else if (part == "arm_fit_coupon") arm_fit_coupon();
else if (part == "print_layout") print_layout();
else echo("Unknown part selector: ", part);
