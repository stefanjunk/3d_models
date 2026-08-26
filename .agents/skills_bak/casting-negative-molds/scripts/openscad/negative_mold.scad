/*
  Printable negative-mold baseline for OpenSCAD.

  Modes:
    block               - full solid block around the cavity
    hollow_block        - block with large exterior pockets along split axis
    conformal_shell     - thin offset shell using 3D Minkowski (expensive)
    ribbed_shell        - conformal shell plus flange, backing rails, and ribs

  This script does not solve undercuts. Verify pull directions and replace the
  planar split with process-specific parting solids when required.
*/

part = "assembly";               // "A", "B", "assembly", "full", "master"
mode = "block";                  // "block", "hollow_block", "conformal_shell", "ribbed_shell"
split_axis = "X";                // "X" or "Y"

use_import = false;
master_file = "master.stl";       // imported master must be centered and in mm
master_size = [50, 50, 80];       // unscaled bounding size; required for envelopes/keys
shrink_pct = [0, 0, 0];           // measured X/Y/Z linear shrinkage percentages

side_margin = 12;
bottom_margin = 10;
top_margin = 18;
shell_thickness = 3.2;
flange_thickness = 4;
flange_extra = 10;
rib_thickness = 3.2;
rib_height = 8;
rib_pitch = 24;

key_radius = 4;
key_depth = 3;
key_clearance = 0.25;
key_overlap = 0.25;

sprue_enabled = true;
sprue_bottom_radius = 4;
sprue_top_radius = 10;
vent_positions = [];              // e.g. [[12, 0], [-12, 0]] as X/Y positions
vent_radius = 1.2;

preview_facets = 36;
offset_facets = 12;               // keep low for Minkowski; raise only after memory test
clip_pad = 5;
eps = 0.02;

scale_xyz = [
    1 / (1 - shrink_pct[0] / 100),
    1 / (1 - shrink_pct[1] / 100),
    1 / (1 - shrink_pct[2] / 100)
];
scaled_master_size = [
    master_size[0] * scale_xyz[0],
    master_size[1] * scale_xyz[1],
    master_size[2] * scale_xyz[2]
];
outer_size = [
    scaled_master_size[0] + 2 * side_margin,
    scaled_master_size[1] + 2 * side_margin,
    scaled_master_size[2] + bottom_margin + top_margin
];
outer_center_z = (top_margin - bottom_margin) / 2;
outer_zmin = -scaled_master_size[2] / 2 - bottom_margin;
outer_zmax = scaled_master_size[2] / 2 + top_margin;

module demo_master() {
    h = master_size[2];
    r = min(master_size[0], master_size[1]) * 0.31;
    base_h = h * 0.16;
    cap_h = h * 0.18;
    union() {
        translate([0, 0, -h/2])
            cylinder(h=base_h, r=r*1.32, $fn=preview_facets);
        translate([0, 0, -h/2 + base_h*0.72])
            cylinder(h=base_h*0.28, r=r*1.42, $fn=preview_facets);
        translate([0, 0, -h/2 + base_h])
            cylinder(h=h-base_h-cap_h, r1=r*1.02, r2=r*0.92, $fn=preview_facets);
        translate([0, 0, h/2-cap_h])
            cylinder(h=cap_h*0.70, r1=r*1.05, r2=r*1.32, $fn=preview_facets);
        translate([-r*1.38, -r*1.38, h/2-cap_h*0.30])
            cube([r*2.76, r*2.76, cap_h*0.30]);
    }
}

module raw_master() {
    if (use_import)
        import(master_file, convexity=20);
    else
        demo_master();
}

module adjusted_master() {
    scale(scale_xyz) raw_master();
}

module outer_block() {
    translate([-outer_size[0]/2, -outer_size[1]/2, outer_zmin])
        cube(outer_size);
}

module split_flange_slab() {
    if (split_axis == "X")
        translate([-flange_thickness/2,
                   -(outer_size[1]+2*flange_extra)/2,
                   outer_zmin-flange_extra])
            cube([flange_thickness,
                  outer_size[1]+2*flange_extra,
                  outer_size[2]+2*flange_extra]);
    else
        translate([-(outer_size[0]+2*flange_extra)/2,
                   -flange_thickness/2,
                   outer_zmin-flange_extra])
            cube([outer_size[0]+2*flange_extra,
                  flange_thickness,
                  outer_size[2]+2*flange_extra]);
}

module conformal_outer() {
    // Computationally expensive on dense imported meshes.
    minkowski() {
        adjusted_master();
        sphere(r=shell_thickness, $fn=offset_facets);
    }
}

module hollow_pockets() {
    // Removes bulk from the two external sides while retaining a cavity-facing
    // skin measured from the supplied master bounding box.
    if (split_axis == "X") {
        a_end = -scaled_master_size[0]/2 - shell_thickness;
        b_start = scaled_master_size[0]/2 + shell_thickness;
        translate([-outer_size[0]/2-eps, -outer_size[1]/2+shell_thickness,
                   outer_zmin+shell_thickness])
            cube([max(eps, a_end + outer_size[0]/2),
                  outer_size[1]-2*shell_thickness,
                  outer_size[2]-2*shell_thickness]);
        translate([b_start, -outer_size[1]/2+shell_thickness,
                   outer_zmin+shell_thickness])
            cube([max(eps, outer_size[0]/2-b_start+eps),
                  outer_size[1]-2*shell_thickness,
                  outer_size[2]-2*shell_thickness]);
    } else {
        a_end = -scaled_master_size[1]/2 - shell_thickness;
        b_start = scaled_master_size[1]/2 + shell_thickness;
        translate([-outer_size[0]/2+shell_thickness, -outer_size[1]/2-eps,
                   outer_zmin+shell_thickness])
            cube([outer_size[0]-2*shell_thickness,
                  max(eps, a_end + outer_size[1]/2),
                  outer_size[2]-2*shell_thickness]);
        translate([-outer_size[0]/2+shell_thickness, b_start,
                   outer_zmin+shell_thickness])
            cube([outer_size[0]-2*shell_thickness,
                  max(eps, outer_size[1]/2-b_start+eps),
                  outer_size[2]-2*shell_thickness]);
    }
}

module rib_cage() {
    // Open, inspectable ribs outside the nominal master bounds.
    if (split_axis == "X") {
        for (side=[-1,1]) {
            x0 = side * (scaled_master_size[0]/2 + shell_thickness + rib_height/2);
            for (z=[outer_zmin+rib_pitch : rib_pitch : outer_zmax-rib_pitch/2])
                translate([x0-rib_height/2,
                           -(outer_size[1]+2*flange_extra)/2,
                           z-rib_thickness/2])
                    cube([rib_height,
                          outer_size[1]+2*flange_extra,
                          rib_thickness]);
            for (y=[-outer_size[1]/2 : rib_pitch : outer_size[1]/2])
                translate([x0-rib_height/2,
                           y-rib_thickness/2,
                           outer_zmin])
                    cube([rib_height, rib_thickness, outer_size[2]]);
        }
    } else {
        for (side=[-1,1]) {
            y0 = side * (scaled_master_size[1]/2 + shell_thickness + rib_height/2);
            for (z=[outer_zmin+rib_pitch : rib_pitch : outer_zmax-rib_pitch/2])
                translate([-(outer_size[0]+2*flange_extra)/2,
                           y0-rib_height/2,
                           z-rib_thickness/2])
                    cube([outer_size[0]+2*flange_extra,
                          rib_height,
                          rib_thickness]);
            for (x=[-outer_size[0]/2 : rib_pitch : outer_size[0]/2])
                translate([x-rib_thickness/2,
                           y0-rib_height/2,
                           outer_zmin])
                    cube([rib_thickness, rib_height, outer_size[2]]);
        }
    }
}

module structural_outer() {
    if (mode == "block") {
        outer_block();
    } else if (mode == "hollow_block") {
        difference() {
            outer_block();
            hollow_pockets();
        }
    } else if (mode == "conformal_shell") {
        union() {
            conformal_outer();
            split_flange_slab();
        }
    } else if (mode == "ribbed_shell") {
        union() {
            conformal_outer();
            split_flange_slab();
            rib_cage();
        }
    } else {
        assert(false, str("Unknown mode: ", mode));
    }
}

module feed_cutters() {
    if (sprue_enabled) {
        start_z = scaled_master_size[2]/2 - 1;
        translate([0, 0, start_z])
            cylinder(h=outer_zmax-start_z+2,
                     r1=sprue_bottom_radius,
                     r2=sprue_top_radius,
                     $fn=preview_facets);
    }
    for (p=vent_positions) {
        start_z = scaled_master_size[2]/2 - 1;
        translate([p[0], p[1], start_z])
            cylinder(h=outer_zmax-start_z+2,
                     r=vent_radius,
                     $fn=max(16, preview_facets/2));
    }
}

module complete_negative() {
    difference() {
        structural_outer();
        adjusted_master();
        feed_cutters();
    }
}

module halfspace(which="A") {
    if (split_axis == "X") {
        if (which == "A")
            translate([-outer_size[0]-flange_extra-clip_pad,
                       -outer_size[1]-flange_extra-clip_pad,
                       outer_zmin-flange_extra-clip_pad])
                cube([outer_size[0]+flange_extra+clip_pad,
                      2*(outer_size[1]+flange_extra+clip_pad),
                      outer_size[2]+2*(flange_extra+clip_pad)]);
        else
            translate([0,
                       -outer_size[1]-flange_extra-clip_pad,
                       outer_zmin-flange_extra-clip_pad])
                cube([outer_size[0]+flange_extra+clip_pad,
                      2*(outer_size[1]+flange_extra+clip_pad),
                      outer_size[2]+2*(flange_extra+clip_pad)]);
    } else {
        if (which == "A")
            translate([-outer_size[0]-flange_extra-clip_pad,
                       -outer_size[1]-flange_extra-clip_pad,
                       outer_zmin-flange_extra-clip_pad])
                cube([2*(outer_size[0]+flange_extra+clip_pad),
                      outer_size[1]+flange_extra+clip_pad,
                      outer_size[2]+2*(flange_extra+clip_pad)]);
        else
            translate([-outer_size[0]-flange_extra-clip_pad,
                       0,
                       outer_zmin-flange_extra-clip_pad])
                cube([2*(outer_size[0]+flange_extra+clip_pad),
                      outer_size[1]+flange_extra+clip_pad,
                      outer_size[2]+2*(flange_extra+clip_pad)]);
    }
}

function key_side_offset() = split_axis == "X"
    ? scaled_master_size[1]/2 + side_margin*0.55
    : scaled_master_size[0]/2 + side_margin*0.55;

function key_z_low() = max(outer_zmin + key_radius*1.6,
                           -scaled_master_size[2]/2 + scaled_master_size[2]*0.20);
function key_z_high() = min(outer_zmax - key_radius*1.6,
                            scaled_master_size[2]/2 - scaled_master_size[2]*0.20);

module one_key(pos=[0,0,0], clearance=0) {
    if (split_axis == "X")
        translate([-key_overlap, pos[1], pos[2]])
            rotate([0,90,0])
                cylinder(h=key_depth+2*key_overlap,
                         r1=key_radius+clearance,
                         r2=key_radius*0.82+clearance,
                         $fn=preview_facets);
    else
        translate([pos[0], -key_overlap, pos[2]])
            rotate([-90,0,0])
                cylinder(h=key_depth+2*key_overlap,
                         r1=key_radius+clearance,
                         r2=key_radius*0.82+clearance,
                         $fn=preview_facets);
}

module all_keys(clearance=0) {
    o = key_side_offset();
    zl = key_z_low();
    zh = key_z_high();
    if (split_axis == "X") {
        one_key([0,-o,zl], clearance);
        one_key([0, o,zl], clearance);
        one_key([0,-o,zh], clearance);
        one_key([0, o*0.72,zh], clearance);
    } else {
        one_key([-o,0,zl], clearance);
        one_key([ o,0,zl], clearance);
        one_key([-o,0,zh], clearance);
        one_key([ o*0.72,0,zh], clearance);
    }
}

module mold_A() {
    union() {
        intersection() {
            complete_negative();
            halfspace("A");
        }
        all_keys(0);
    }
}

module mold_B() {
    difference() {
        intersection() {
            complete_negative();
            halfspace("B");
        }
        all_keys(key_clearance);
    }
}

if (part == "A") {
    mold_A();
} else if (part == "B") {
    mold_B();
} else if (part == "full") {
    complete_negative();
} else if (part == "master") {
    adjusted_master();
} else {
    // Assembly view; parts overlap at their intended mating position.
    color("steelblue", 0.75) mold_A();
    color("sandybrown", 0.75) mold_B();
}
