// Modularer, normally-open Inline-Filamentvorschub – 8-fach steckbar
// 1,75-mm-Filament, 4-mm-PTFE, TPU-Druckrad.
// Jedes Gehaeuse hat rechts zwei T-Zungen und links zwei offene T-Nuten.
// Nachbarmodule werden von oben ineinander geschoben.
// part = "body", "wheel", "spring", "washer", "left_cap", "right_cap", "assembly8"
part = "assembly8";
$fn = 96;

body_length = 54;
body_width = 18;
module_pitch = 26;      // 8 mm Freiraum zwischen den Gehaeusen
base_height = 10;
corner_radius = 2.4;
filament_path_z = 6.5;
filament_d = 1.75;
filament_channel_d = 2.50;
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

connector_x = [-18,18];
connector_z0 = 1.15;
connector_z1 = 8.80;

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

module male_T(xx) {
    translate([xx,(9+13.15)/2,(connector_z0+connector_z1)/2])
        cube([5,13.15-9,connector_z1-connector_z0],center=true);
    translate([xx,(12.75+15.45)/2,(connector_z0+connector_z1)/2])
        cube([8,15.45-12.75,connector_z1-connector_z0],center=true);
}
module female_receiver(xx) {
    difference() {
        translate([xx,(-13-9)/2,(0.45+9.45)/2]) cube([11.5,4,9],center=true);
        translate([xx,(-13.15-10.05)/2,(1+10.1)/2]) cube([8.55,3.1,9.1],center=true);
        translate([xx,(-13.45-11.75)/2,(1+10.1)/2]) cube([5.55,1.7,9.1],center=true);
        translate([xx,-11.65,9.35]) cube([9.25,3.9,1.8],center=true);
    }
}

module body() {
    difference() {
        union() {
            rounded_box([body_length,body_width,base_height],corner_radius);
            for(s=[-1,1])
                translate([0,s*(wall_inner_gap/2+(body_width/2-wall_inner_gap/2)/2),wall_bottom_z+wall_height/2])
                    cube([wall_length,body_width/2-wall_inner_gap/2,wall_height],center=true);
            for(xx=connector_x) male_T(xx);
            for(xx=connector_x) female_receiver(xx);
        }
        translate([0,0,filament_path_z]) cyl_x(filament_channel_d,body_length+2);
        for(s=[-1,1])
            translate([s*(body_length/2-(ptfe_insert_depth+1)/2),0,filament_path_z])
                cyl_x(ptfe_socket_d,ptfe_insert_depth+1);
        translate([0,0,14.5]) cube([21,9,15],center=true);
        vertical_slot_y(axle_slot_d,wheel_center_engaged_z,wheel_center_open_z,body_width+2);
        for(s=[-1,1])
            translate([-10.2,s*(body_width/2-2.15/2),(13.0+14.75)/2])
                cube([6.0,2.15,1.75],center=true);
    }
}

module wheel() difference() {
    rotate_extrude(convexity=10)
        polygon([[0,0],[8.5,0],[8.85,1.4],[9.0,wheel_width/2],[8.85,wheel_width-1.4],[8.5,wheel_width],[0,wheel_width]]);
    translate([0,0,-0.1]) cylinder(d=axle_hole_d,h=wheel_width+0.2);
}
module spring_lip() union() {
    translate([-10.2,1.0,0.7]) cube([5.6,2.0,1.4],center=true);
    translate([-3.25,3.7,0.7]) cube([9.5,3.8,1.4],center=true);
    translate([0,3.7,0]) cylinder(d=6.2,h=1.4);
}
module washer() difference() { cylinder(d=7,h=0.7); translate([0,0,-.1]) cylinder(d=3.5,h=.9); }

module left_cap() {
    union() {
        translate([0,-17.15,4.9]) cube([46,3,8.8],center=true);
        for(xx=connector_x) {
            translate([xx,-14.55,(connector_z0+connector_z1)/2]) cube([5,5.2,connector_z1-connector_z0],center=true);
            translate([xx,-11.65,(connector_z0+connector_z1)/2]) cube([8,2.7,connector_z1-connector_z0],center=true);
        }
    }
}
module right_cap() {
    difference() {
        union() {
            translate([0,18,4.9]) cube([46,3,8.8],center=true);
            for(xx=connector_x) translate([xx,15.15,(0.45+9.45)/2]) cube([11.5,5.7,9],center=true);
        }
        for(xx=connector_x) {
            translate([xx,14.10,(1+10.1)/2]) cube([8.55,3.15,9.1],center=true);
            translate([xx,12.95,(1+10.1)/2]) cube([5.55,1.9,9.1],center=true);
            translate([xx,14.2,9.35]) cube([9.25,4.2,1.8],center=true);
        }
    }
}

module one_assembly() {
    color("lightgray") body();
    color("orange") translate([0,0,wheel_center_open_z]) rotate([90,0,0]) wheel();
    color("gold") translate([0,0,filament_path_z]) cyl_x(filament_d,18);
    color("deepskyblue") for(s=[-1,1]) translate([s*20,0,filament_path_z]) cyl_x(4,14);
}
module assembly8() {
    for(i=[0:7]) translate([0,i*module_pitch,0]) one_assembly();
    color("dimgray") left_cap();
    color("dimgray") translate([0,7*module_pitch,0]) right_cap();
}

if(part=="body") body();
else if(part=="wheel") wheel();
else if(part=="spring") spring_lip();
else if(part=="washer") washer();
else if(part=="left_cap") left_cap();
else if(part=="right_cap") right_cap();
else assembly8();
