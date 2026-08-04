// Zweiteiliger Kabel-/PTFE-Buendelhalter
// Diese Halbschale zweimal drucken und mit 2x M3x18/M3x20 + Muttern verschrauben.
// Standard: 8 PTFE-Schlaeuche (4 mm AD) und ein USB-/Steuerkabel in der Mitte.
$fn = 96;

holder_length = 80.0;
holder_depth = 18.0;
half_thickness = 6.0;
corner_radius = 2.5;
ptfe_channel_d = 4.6;
usb_width = 7.5;
usb_height = 4.8;
screw_d = 3.5;
ptfe_x = [-28,-21,-14,-7,7,14,21,28];
screw_x = [-35.5,35.5];

module rounded_rect_2d(size=[10,10], r=2) {
    offset(r=r) square([size[0]-2*r, size[1]-2*r], center=true);
}

module cable_holder_half() {
    difference() {
        linear_extrude(height=half_thickness)
            rounded_rect_2d([holder_length,holder_depth],corner_radius);

        // Acht PTFE-Nuten, Achse entlang Y
        for (xpos=ptfe_x)
            translate([xpos,0,half_thickness])
                rotate([90,0,0]) cylinder(d=ptfe_channel_d,h=holder_depth+2,center=true);

        // Ovale Nut fuer USB-/Steuerkabel
        translate([0,0,half_thickness])
            rotate([90,0,0])
                scale([usb_width/usb_height,1,1])
                    cylinder(d=usb_height,h=holder_depth+2,center=true);

        // M3-Durchgangsbohrungen
        for (xpos=screw_x)
            translate([xpos,0,-1]) cylinder(d=screw_d,h=half_thickness+2);
    }
}

cable_holder_half();
