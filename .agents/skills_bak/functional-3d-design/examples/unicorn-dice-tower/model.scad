/*
Integrated unicorn dice tower and landing tray.
OpenSCAD 2021.01 compatible.

The outer tower, internal alternating ramps, and tray are one printed part.
The unicorn silhouette is original project artwork imported from unicorn.svg.
*/

/* [Main dimensions] */
tower_width = 92;
tower_depth = 82;
tower_height = 205;
corner_radius = 7;
wall = 3.0;
bottom = 3.0;

/* [Dice path] */
ramp_angle = 47;              // degrees from horizontal
ramp_thickness = 3.0;
ramp_depth = 50;
ramp_width_clearance = 3.0;
ramp_levels = [158, 108, 58];
exit_width = 63;
exit_height = 43;

/* [Tray] */
tray_extension = 112;
tray_side_margin = 16;
tray_wall = 3.0;
tray_lip_height = 17;
tray_base = 3.0;
tray_corner_radius = 11;

/* [Engraving] */
engraving_enabled = true;
engraving_depth = 0.65;
engraving_width = 47;
engraving_height = 63;
engraving_z = 118;

/* [Quality] */
$fn = 48;

inner_width = tower_width - 2*wall;
inner_depth = tower_depth - 2*wall;

assert(exit_width < inner_width - 4, "Exit must be narrower than inner tower width.");
assert(ramp_depth < inner_depth - 8, "Ramp depth must leave a dice drop gap.");
assert(ramp_angle >= 42, "Default support-light design expects a sufficiently steep ramp.");

module rounded_rect_2d(w, d, r) {
    assert(w > 2*r && d > 2*r);
    hull() {
        for (x = [-w/2+r, w/2-r])
            for (y = [-d/2+r, d/2-r])
                translate([x,y]) circle(r=r);
    }
}

module rounded_prism(w, d, h, r) {
    linear_extrude(height=h) rounded_rect_2d(w,d,r);
}

module tower_shell() {
    difference() {
        rounded_prism(tower_width, tower_depth, tower_height, corner_radius);

        translate([0,0,bottom])
            rounded_prism(
                inner_width,
                inner_depth,
                tower_height-bottom+1,
                max(1, corner_radius-wall)
            );

        // Front exit (negative Y side).
        translate([-exit_width/2, -tower_depth/2-1, bottom])
            cube([exit_width, wall+3, exit_height]);

        // Shallow front-face engraving above the exit.
        if (engraving_enabled)
            unicorn_engraving_cutter();
    }
}

module ramp_raw(level, from_back=true) {
    // A sloped plate grows from one wall toward the opposite side.
    // The underside angle is intentionally near 45 degrees for support-light FDM.
    xw = inner_width - 2*ramp_width_clearance;
    y0 = from_back ? tower_depth/2-wall-1 : -tower_depth/2+wall+1;
    dir = from_back ? -1 : 1;

    translate([0, y0, level])
        rotate([dir*ramp_angle,0,0])
            translate([-xw/2, from_back ? -ramp_depth : 0, -ramp_thickness/2])
                cube([xw, ramp_depth, ramp_thickness]);

    // Triangular side gussets reduce peel at the wall/ramp junction.
    for (x = [-xw/2+4, xw/2-4])
        translate([x, y0-dir*2, level-4])
            rotate([90,0,90])
                linear_extrude(height=4, center=true)
                    polygon(points=[[0,0],[11,0],[0,11]]);
}

module ramp(level, from_back=true) {
    // Clip rotated geometry to an envelope that overlaps the inner wall by 0.9 mm.
    // This joins the ramp to the tower without allowing corners to protrude outside.
    intersection() {
        ramp_raw(level, from_back);
        translate([0,0,bottom])
            rounded_prism(
                tower_width-2*(wall-0.9),
                tower_depth-2*(wall-0.9),
                tower_height-bottom,
                max(1,corner_radius-wall+0.9)
            );
    }
}

module tray() {
    tray_width = tower_width + 2*tray_side_margin;
    tray_depth = tray_extension;
    tray_center_y = -tower_depth/2 - tray_depth/2 + 1;

    union() {
        // Base.
        translate([0,tray_center_y,0])
            rounded_prism(tray_width, tray_depth, tray_base, tray_corner_radius);

        // Side/front ring; rear gate is cut so dice flow from tower into tray.
        difference() {
            translate([0,tray_center_y,0])
                difference() {
                    rounded_prism(tray_width, tray_depth, tray_lip_height, tray_corner_radius);
                    translate([0,0,tray_base])
                        rounded_prism(
                            tray_width-2*tray_wall,
                            tray_depth-2*tray_wall,
                            tray_lip_height-tray_base+1,
                            max(2,tray_corner_radius-tray_wall)
                        );
                }

            // Remove rear-center wall where it meets the tower exit.
            translate([-exit_width/2-3, -tower_depth/2-5, tray_base])
                cube([exit_width+6, 12, tray_lip_height+2]);
        }
    }
}

module unicorn_engraving_cutter() {
    // SVG lies in XY and extrudes in Z; rotate so extrusion points into front wall.
    translate([-engraving_width/2, -tower_depth/2+engraving_depth-0.02, engraving_z])
        rotate([90,0,0])
            linear_extrude(height=engraving_depth+0.05)
                resize([engraving_width, engraving_height], auto=false)
                    import("unicorn.svg", center=false);
}

module dice_tower() {
    union() {
        tower_shell();
        tray();
        ramp(ramp_levels[0], true);
        ramp(ramp_levels[1], false);
        ramp(ramp_levels[2], true);
    }
}

dice_tower();
