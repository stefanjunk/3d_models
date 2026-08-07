// Modular Desk Organizer - parametric OpenSCAD source
// Inspired by the generated concept image: soft rounded forms, subtle ribs,
// drawer tower, cubby, open trays and vertical slide-dovetail connections.
// Units: mm

$fn = 48;
PART = "layout";          // layout, drawer_housing, drawer, cubby, shallow_tray, divided_bin, pen_cup, connector_test
FIT = 0.35;               // connector clearance per side; try 0.25..0.45 depending on printer/material
TEXTURE = true;           // subtle horizontal ribs on selected modules

module rr2d(w,d,r) {
    translate([r,r]) offset(r=r) square([w-2*r,d-2*r], center=false);
}

module rounded_prism(w,d,h,r) {
    linear_extrude(height=h) rr2d(w,d,r);
}

module cup(w,d,h,wall=3,bottom=3,r=12) {
    difference() {
        rounded_prism(w,d,h,r);
        translate([wall,wall,bottom])
            rounded_prism(w-2*wall,d-2*wall,h-bottom+0.2,max(1,r-wall));
    }
}

// A rounded cup rotated so its opening points toward the front (negative Y / Y=0 side).
module front_cup(w,d,h,wall=3.2,back=3.2,r=12) {
    translate([0,d,0]) rotate([90,0,0]) cup(w,h,d,wall,back,r);
}

module u_shell_2d(w,d,r,wall=3.2,back=3.2) {
    // Rounded outer footprint with an open front notch.
    difference() {
        rr2d(w,d,r);
        translate([wall,0]) square([w-2*wall,d-back+0.2], center=false);
    }
}

module u_shell_layer(w,d,h,r,wall=3.2,back=3.2) {
    linear_extrude(height=h) u_shell_2d(w,d,r,wall,back);
}

module connector_pair(w,d,h,fit=FIT,rail_h=56,rail_z=12,p=4,base=8,head=12,rail_t=2.2) {
    y0 = d/2;
    zh = min(rail_h,h-rail_z-5);

    // Male vertical dovetail on RIGHT: narrow at body, wider at head.
    translate([0,0,rail_z]) linear_extrude(height=zh)
        polygon(points=[
            [w,y0-base/2],
            [w+p,y0-head/2],
            [w+p,y0+head/2],
            [w,y0+base/2]
        ]);

    // Female receiver on LEFT is external, so no hidden support-heavy groove is required.
    mouth = base + 2*fit;
    inner = head + 2*fit;
    translate([0,0,rail_z]) linear_extrude(height=zh)
        polygon(points=[
            [-p-0.15,y0+mouth/2],
            [0,y0+inner/2],
            [0,y0+inner/2+rail_t],
            [-p-0.15,y0+mouth/2+rail_t]
        ]);
    translate([0,0,rail_z]) linear_extrude(height=zh)
        polygon(points=[
            [-p-0.15,y0-mouth/2-rail_t],
            [0,y0-inner/2-rail_t],
            [0,y0-inner/2],
            [-p-0.15,y0-mouth/2]
        ]);
}

module rib_ring(w,d,r,z,amp=0.38,rib_h=0.75) {
    translate([0,0,z]) difference() {
        translate([-amp,-amp,0])
            linear_extrude(height=rib_h) rr2d(w+2*amp,d+2*amp,r+amp);
        translate([0,0,-0.1])
            linear_extrude(height=rib_h+0.2) rr2d(w,d,r);
    }
}

module drawer_housing() {
    // Built from z-layers so the cavity geometry matches the exported STL.
    // No front ribs: the drawer face area stays clean.
    w=96; d=96; h=80; wall=3.2; back=3.2; r=15; shelf=3.2;
    open_h = 34.8;
    lower_z = 4.2;
    upper_z = lower_z + open_h + shelf;
    union() {
        translate([0,0,0]) rounded_prism(w,d,lower_z,r);
        translate([0,0,lower_z]) u_shell_layer(w,d,open_h,r,wall,back);
        translate([0,0,lower_z+open_h]) rounded_prism(w,d,shelf,r);
        translate([0,0,upper_z]) u_shell_layer(w,d,open_h,r,wall,back);
        translate([0,0,upper_z+open_h]) rounded_prism(w,d,h-(upper_z+open_h),r);
        // shallow runners for the drawers
        for (z=[lower_z+1.2, upper_z+1.2]) {
            translate([wall-0.3,7,z]) cube([1.4,d-back-10,1.5]);
            translate([w-wall-1.1,7,z]) cube([1.4,d-back-10,1.5]);
        }
        connector_pair(w,d,h);
    }
}

module drawer() {
    // Updated together with the housing: larger visible front radii,
    // closer to the inner front opening while keeping slide clearance.
    body_w=88.6; body_d=91; body_h=32.2; body_r=10.0;
    face_w=89.1; face_h=34.6; face_t=2.4; face_r=11.2;
    union() {
        cup(body_w,body_d,body_h,2.4,2.4,body_r);
        // front bezel with radii visually matched to the housing opening
        translate([-(face_w-body_w)/2,-face_t,0])
            rounded_prism(face_w,face_t,face_h,face_r);
        // low-profile rounded pull centered on the bezel
        translate([(body_w-30)/2,-4.2,9.7]) rounded_prism(30,5.5,6.2,2.4);
    }
}

module cubby() {
    w=96; d=96; h=80;
    union() {
        front_cup(w,d,h,3.2,3.2,13);
        connector_pair(w,d,h);
    }
}

module shallow_tray() {
    w=96; d=96; h=26; r=14;
    union() {
        cup(w,d,h,3,3,r);
        translate([46.5,3.2,3]) cube([2.4,d-6.4,15.5]);
        connector_pair(w,d,h,rail_h=14,rail_z=6);
    }
}

module divided_bin() {
    w=96; d=96; h=78; r=15;
    union() {
        cup(w,d,h,3,3,r);
        translate([46.7,3,3]) cube([2.6,d-6,57]);
        translate([3,47,3]) cube([43.7,2.6,57]);
        translate([49.3,58,3]) cube([43.7,2.6,57]);
        connector_pair(w,d,h);
        if (TEXTURE) for (z=[10:5.5:60]) rib_ring(w,d,r,z);
    }
}

module pen_cup() {
    w=64; d=96; h=110; r=17;
    union() {
        cup(w,d,h,3,3,r);
        translate([3,50,3]) cube([w-6,2.6,87]);
        connector_pair(w,d,h,rail_h=56,rail_z=12);
        if (TEXTURE) for (z=[10:5.5:79]) rib_ring(w,d,r,z);
    }
}

module connector_test() {
    // Print two copies and slide them together vertically.
    w=24; d=34; h=30;
    union() {
        cube([w,d,h]);
        connector_pair(w,d,h,rail_h=20,rail_z=5);
    }
}

module layout() {
    gap = 4.35;  // natural spacing produced by the external sliding connector
    // back row
    translate([0,0,0]) drawer_housing();
    translate([96+gap,0,0]) divided_bin();
    translate([2*(96+gap),0,0]) cubby();
    translate([3*(96+gap),0,0]) pen_cup();

    // drawers shown partially inserted for a useful preview
    translate([(96-88.6)/2,-5,4.2]) drawer();
    translate([(96-88.6)/2,-10,43.1]) drawer();

    // extra shallow tray nearby
    translate([96+gap,-115,0]) shallow_tray();
}

if (PART == "drawer_housing") drawer_housing();
else if (PART == "drawer") drawer();
else if (PART == "cubby") cubby();
else if (PART == "shallow_tray") shallow_tray();
else if (PART == "divided_bin") divided_bin();
else if (PART == "pen_cup") pen_cup();
else if (PART == "connector_test") connector_test();
else layout();
