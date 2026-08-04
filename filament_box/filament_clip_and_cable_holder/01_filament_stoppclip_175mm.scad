// Filament-Stoppclip fuer 1,75-mm-Filament
// Ein Teil drucken. Auf das ca. 10 mm aus dem PTFE-Schlauch ragende Filament aufschnappen.
$fn = 96;

clip_length = 13.0;
clip_width = 10.0;
clip_thickness = 3.2;
corner_radius = 2.0;
filament_pocket_d = 2.05;
snap_slot_width = 1.3;
mouth_width = 3.0;
pocket_x = -1.2;

module rounded_rect_2d(size=[10,10], r=2) {
    offset(r=r) square([size[0]-2*r, size[1]-2*r], center=true);
}

module filament_stoppclip() {
    linear_extrude(height=clip_thickness)
    difference() {
        rounded_rect_2d([clip_length, clip_width], corner_radius);
        translate([pocket_x,0]) circle(d=filament_pocket_d);
        // schmaler federnder Einsteckschlitz
        translate([(pocket_x + clip_length/2 + 0.8)/2,0])
            square([clip_length/2 + 0.8 - pocket_x, snap_slot_width], center=true);
        // aufgeweitete Einfuehrung
        translate([clip_length/2-0.8,0])
            square([2.8, mouth_width], center=true);
    }
}

filament_stoppclip();
