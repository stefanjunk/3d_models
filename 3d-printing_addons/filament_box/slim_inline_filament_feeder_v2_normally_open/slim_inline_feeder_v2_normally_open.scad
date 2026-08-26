// Schlanker, normally-open Inline-Filamentvorschub
// 1,75-mm-Filament, 4-mm-PTFE. Das TPU-Rad wird zum Vorschub heruntergedrückt.
// Zwei TPU-Federlippen heben die Achse danach wieder an.
// part = "body", "wheel", "spring", "washer" oder "assembly"
part = "assembly";
$fn = 96;

body_length = 54;
body_width = 18;
base_height = 10;
corner_radius = 2.4;
filament_path_z = 6.5;
filament_d = 1.75;
filament_channel_d = 2.50;
ptfe_od = 4.0;
ptfe_socket_d = 4.30;
ptfe_insert_depth = 19.5;

wheel_d = 18;
wheel_width = 7;
axle_hole_d = 3.45;
wheel_center_engaged_z = 16.35;
wheel_center_open_z = 17.90;
axle_slot_d = 3.65;
wall_inner_gap = 9;
wall_height = 13;
wall_bottom_z = 8;
wall_length = 26;

spring_thickness = 1.4;
spring_anchor_length = 5.6;
spring_arm_length = 9.5;

module rounded_box(size=[10,10,10], r=2) {
    x=size[0]; y=size[1]; z=size[2];
    hull() for(ix=[-x/2+r,x/2-r], iy=[-y/2+r,y/2-r], iz=[r,z-r])
        translate([ix,iy,iz]) sphere(r=r);
}
module cyl_x(d,l) rotate([0,90,0]) cylinder(d=d,h=l,center=true);
module cyl_y(d,l) rotate([90,0,0]) cylinder(d=d,h=l,center=true);
module vertical_slot_y(d,z1,z2,l) hull() {
    translate([0,0,z1]) cyl_y(d,l);
    translate([0,0,z2]) cyl_y(d,l);
}

module body() {
    difference() {
        union() {
            rounded_box([body_length,body_width,base_height],corner_radius);
            // Seitenwangen
            for(s=[-1,1])
                translate([0,s*(wall_inner_gap/2+(body_width/2-wall_inner_gap/2)/2),wall_bottom_z+wall_height/2])
                    cube([wall_length,body_width/2-wall_inner_gap/2,wall_height],center=true);
        }
        // durchgehender Filamentkanal
        translate([0,0,filament_path_z]) cyl_x(filament_channel_d,body_length+2);
        // PTFE-Aufnahmen
        for(s=[-1,1])
            translate([s*(body_length/2-(ptfe_insert_depth+1)/2),0,filament_path_z])
                cyl_x(ptfe_socket_d,ptfe_insert_depth+1);
        // Freiraum für das Rad; die untere Hälfte des Filamentkanals bleibt als Führung
        translate([0,0,14.5]) cube([21,9,15],center=true);
        // Langloch für M3-Achse
        vertical_slot_y(axle_slot_d,wheel_center_engaged_z,wheel_center_open_z,body_width+2);
        // M3-Pilotlöcher zum sehr leichten Fixieren der PTFE-Schläuche
        for(x=[-20.5,20.5]) translate([x,0,10]) cylinder(d=2.7,h=8,center=true);
        // Einschubnuten für die zwei TPU-Federlippen; von der hinteren Stirnseite einschieben
        for(s=[-1,1])
            translate([-10.2,s*(body_width/2-2.15/2),(13.0+14.75)/2])
                cube([6.0,2.15,1.75],center=true);
    }
}

module wheel() {
    difference() {
        // leicht ballige Lauffläche: TPU greift gut, ohne scharfe Zähne
        rotate_extrude(convexity=10)
            polygon([[0,0],[8.5,0],[8.85,1.4],[9.0,wheel_width/2],[8.85,wheel_width-1.4],[8.5,wheel_width],[0,wheel_width]]);
        translate([0,0,-0.1]) cylinder(d=axle_hole_d,h=wheel_width+0.2);
    }
}

module spring_lip() {
    union() {
        // Einschubzunge
        translate([-10.2,1.0,spring_thickness/2]) cube([spring_anchor_length,2.0,spring_thickness],center=true);
        // Federarm
        translate([-3.25,3.7,spring_thickness/2]) cube([spring_arm_length,3.8,spring_thickness],center=true);
        // breite Auflage unter Schraubenkopf bzw. Unterlegscheibe
        translate([0,3.7,0]) cylinder(d=6.2,h=spring_thickness);
    }
}

module washer() difference() {
    cylinder(d=7,h=0.7);
    translate([0,0,-0.1]) cylinder(d=3.5,h=0.9);
}

module assembly() {
    color("lightgray") body();
    // Radachse liegt im offenen Zustand oben im Langloch
    color("orange") translate([0,wheel_width/2,wheel_center_open_z]) rotate([90,0,0]) wheel();
    // Filament und PTFE nur zur Darstellung
    color("gold") translate([0,0,filament_path_z]) cyl_x(filament_d,18);
    color("deepskyblue") for(s=[-1,1]) translate([s*20,0,filament_path_z]) cyl_x(4,14);
    // Federlippen schematisch außen; links gespiegelt
    color("darkorange") translate([0,body_width/2-2.0,13.1]) spring_lip();
    color("darkorange") mirror([0,1,0]) translate([0,body_width/2-2.0,13.1]) spring_lip();
}

if(part=="body") body();
else if(part=="wheel") wheel();
else if(part=="spring") spring_lip();
else if(part=="washer") washer();
else assembly();
