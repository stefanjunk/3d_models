// Schlanker manueller Inline-Filamentvorschub
// Für 1,75-mm-Filament und 4-mm-PTFE-Schlauch
// Konstruktion: geschlossenes Gehäuse, seitliches Handrad, TPU-Andruckschuh.
// Auswahl über part: "body", "cover", "wheel", "pad", "tire", "assembly"

part = "assembly";
$fn = 96;

// Hauptparameter
body_length = 56;
body_width  = 24;
body_height = 10;
cover_height = 3;
corner_radius = 2.4;

filament_d = 1.75;
filament_channel_d = 2.5;
ptfe_od = 4.0;
ptfe_socket_d = 4.3;
ptfe_insert_depth = 19;
path_z = 5;

wheel_d = 20;
wheel_thickness = 6;
wheel_x = 0;
wheel_y = 9.2;
axle_d = 3.3;
oring_major_r = 8.85;
oring_groove_r = 1.15; // passend für ca. 18x2-mm-O-Ring

pad_length = 14;
pad_width = 7.2;
pad_height = 5.6;

module rounded_box(size=[10,10,10], r=2, center=false) {
    x=size[0]; y=size[1]; z=size[2];
    translate(center ? [-x/2,-y/2,-z/2] : [0,0,0])
    hull() {
        for (ix=[r,x-r], iy=[r,y-r])
            translate([ix,iy,r]) sphere(r=r);
        for (ix=[r,x-r], iy=[r,y-r])
            translate([ix,iy,z-r]) sphere(r=r);
    }
}

module cyl_x(d,l) rotate([0,90,0]) cylinder(d=d,h=l,center=true);

module body() {
    difference() {
        translate([-body_length/2,-body_width/2,0])
            rounded_box([body_length,body_width,body_height],corner_radius);

        // Handrad-Tasche
        translate([wheel_x,wheel_y,-0.1]) cylinder(r=11.3,h=body_height+0.2);
        translate([wheel_x,wheel_y,-0.1]) cylinder(d=axle_d,h=body_height+0.2);

        // PTFE-Aufnahmen links/rechts
        translate([-18.75,0,path_z]) cyl_x(ptfe_socket_d,19.5);
        translate([ 18.75,0,path_z]) cyl_x(ptfe_socket_d,19.5);
        translate([0,0,path_z]) cyl_x(filament_channel_d,14);

        // kurze Einlaufkonen
        translate([-8,0,path_z]) rotate([0,90,0]) cylinder(d1=ptfe_socket_d,d2=filament_channel_d,h=4,center=true);
        translate([ 8,0,path_z]) rotate([0,90,0]) cylinder(d1=filament_channel_d,d2=ptfe_socket_d,h=4,center=true);

        // Tasche für TPU-Andruckschuh
        translate([-7.3,-7.8,2.3]) cube([14.6,7.0,8]);

        // Deckelschrauben, selbstschneidend M3
        for (x=[-21,21]) translate([x,-7.3,5]) cylinder(d=2.7,h=6);
        // PTFE-Klemmschrauben, selbstschneidend M3
        for (x=[-20,20]) translate([x,0,5.7]) cylinder(d=2.7,h=5);
    }
}

module cover() {
    difference() {
        translate([-body_length/2,-body_width/2,0])
            rounded_box([body_length,body_width,cover_height],corner_radius);
        translate([wheel_x,wheel_y,-0.1]) cylinder(r=11.6,h=cover_height+0.2);
        for (x=[-21,21]) translate([x,-7.3,-0.1]) cylinder(d=3.4,h=cover_height+0.2);
        for (x=[-20,20]) translate([x,0,-0.1]) cylinder(d=3.4,h=cover_height+0.2);
        translate([-5,-1.75,-0.1]) cube([10,3.5,cover_height+0.2]);
    }
}

module wheel() {
    difference() {
        union() {
            cylinder(d=wheel_d,h=wheel_thickness);
            for (a=[0:15:345])
                rotate([0,0,a]) translate([wheel_d/2+0.6,0,0.7]) cylinder(r=0.9,h=wheel_thickness-1.4);
        }
        translate([0,0,-0.1]) cylinder(d=axle_d,h=wheel_thickness+0.2);
        // umlaufende O-Ring-Nut
        translate([0,0,wheel_thickness/2])
        rotate_extrude()
            translate([oring_major_r,0]) circle(r=oring_groove_r,$fn=40);
    }
}

module pad() {
    difference() {
        translate([-pad_length/2,-pad_width/2,0])
            rounded_box([pad_length,pad_width,pad_height],1.2);
        // Längsnut für Filament, zur Radseite offen
        translate([0,pad_width/2+0.15,pad_height/2]) cyl_x(2.3,pad_length+2);
        // kleine Flexschlitze
        for (x=[-4,4]) translate([x-0.5,-pad_width/2-0.1,0.8]) cube([1,2.1,2.5]);
    }
}

module tire() {
    translate([0,0,1.5]) rotate_extrude()
        translate([oring_major_r,0]) circle(r=1.25,$fn=48);
}

module assembly() {
    color("lightgray") body();
    color("gray") translate([0,0,body_height]) cover();
    color("orange") translate([wheel_x,wheel_y,2]) wheel();
    color("darkorange") translate([wheel_x,wheel_y,2]) tire();
    color("gold") translate([0,-4.2,2.3]) pad();
    color("blue") translate([-body_length/2-14,0,path_z]) cyl_x(4,28);
    color("blue") translate([ body_length/2+14,0,path_z]) cyl_x(4,28);
}

if (part=="body") body();
else if (part=="cover") cover();
else if (part=="wheel") wheel();
else if (part=="pad") pad();
else if (part=="tire") tire();
else assembly();
