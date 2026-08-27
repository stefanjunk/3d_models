// Sternfoermiger Einclip-Halter fuer 8 PTFE-Schlaeuche + 1 Steuerkabel
// Flach drucken, keine Supports. Alle Leitungen werden radial von aussen eingeclippt.
$fn = 96;

part = "8PTFE_1USB"; // "8PTFE_1USB" oder "9PTFE"
thickness = 6.0;
hub_radius = 9.5;
clip_center_radius = 18.5;
arm_radius = 2.35;
angles = [for(i=[0:8]) 90-i*40];
ptfe_outer_diameter = 4.0;
ptfe_pocket_diameter = 4.5;
ptfe_clip_outer_radius = 4.25;
ptfe_throat_width = 3.15;
ptfe_mouth_width = 4.9;
usb_cable_width = 7.5;
usb_cable_height = 4.8;
usb_pocket_tangential = 8.1;
usb_pocket_radial = 5.4;
usb_clip_outer_radius = 6.2;
usb_throat_width = 4.0;
usb_mouth_width = 6.8;

module capsule_between(r1, r2, radius) {
    hull() { translate([r1,0]) circle(r=radius); translate([r2,0]) circle(r=radius); }
}
module ptfe_clip_2d() {
    difference() {
        union() {
            capsule_between(hub_radius-0.7, clip_center_radius-ptfe_clip_outer_radius+0.8, arm_radius);
            translate([clip_center_radius,0]) circle(r=ptfe_clip_outer_radius);
        }
        translate([clip_center_radius,0]) circle(d=ptfe_pocket_diameter);
        translate([clip_center_radius+(ptfe_clip_outer_radius+1.0)/2,0])
            square([ptfe_clip_outer_radius+1.0,ptfe_throat_width],center=true);
        translate([clip_center_radius+ptfe_clip_outer_radius-0.10,0])
            square([2.3,ptfe_mouth_width],center=true);
    }
}
module usb_clip_2d() {
    difference() {
        union() {
            capsule_between(hub_radius-0.7, clip_center_radius-usb_clip_outer_radius+0.8, arm_radius);
            translate([clip_center_radius,0]) circle(r=usb_clip_outer_radius);
        }
        translate([clip_center_radius,0])
            scale([usb_pocket_radial/usb_pocket_tangential,1]) circle(d=usb_pocket_tangential);
        translate([clip_center_radius+(usb_clip_outer_radius+1.1)/2,0])
            square([usb_clip_outer_radius+1.1,usb_throat_width],center=true);
        translate([clip_center_radius+usb_clip_outer_radius-0.15,0])
            square([2.7,usb_mouth_width],center=true);
    }
}
module star_holder_2d(mixed=true) {
    union() {
        circle(r=hub_radius);
        for(i=[0:8]) rotate(angles[i]) if(mixed && i==0) usb_clip_2d(); else ptfe_clip_2d();
    }
}
linear_extrude(height=thickness) star_holder_2d(mixed=(part=="8PTFE_1USB"));
