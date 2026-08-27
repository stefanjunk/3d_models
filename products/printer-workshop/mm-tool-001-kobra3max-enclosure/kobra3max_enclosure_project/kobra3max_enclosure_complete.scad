/*
 Anycubic Kobra 3 Max camera-whitebox enclosure – complete DRAFT assembly.

 Coordinate system: X width, Y depth (front at Y=0), Z height.
 The assembly is a fabrication reference, not a single printable export.
 Purchased timber, sheet, hardware, lights, fan, extrusion and camera are shown
 together with the project-authored printed parts.

 License for project-authored geometry: CC BY 4.0.
*/

W=900;
D=1050;
H=900;
B=20;
PANEL=3;
DOOR_G=4;
DIFFUSER=3;
SERVICE_BAY_W=140;
DOOR_OVERLAP=10;
DOOR_ANGLE=28;
LIGHT_CASSETTE_H=60;
LIGHT_CASSETTE_INSET=24;
WINDOW_CX=820;
WINDOW_CZ=590;
WINDOW_CUT_W=72;
WINDOW_CUT_H=82;
CAMERA_RAIL_H=500;
CAMERA_RAIL_Z=320;

SHOW_PRINTER=is_undef(SHOW_PRINTER) ? true : SHOW_PRINTER;
SHOW_DOOR_OPEN=is_undef(SHOW_DOOR_OPEN) ? true : SHOW_DOOR_OPEN;
SHOW_ROOF=is_undef(SHOW_ROOF) ? true : SHOW_ROOF;

LIBRARY_MODE=true;
include <kobra3max_enclosure.scad>

IW=W-2*B;
ID=D-2*B;
IH=H-2*B;
STILE_X=W-B-SERVICE_BAY_W;
DOOR_W=STILE_X-B+2*DOOR_OVERLAP;
DOOR_H=IH+2*DOOR_OVERLAP;
SERVICE_PANEL_X=W-SERVICE_BAY_W-10;

assert(IW-2*PANEL>=706+50,
  "Width no longer preserves the planned Kobra 3 Max margin");
assert(ID-PANEL>=940+50,
  "Depth no longer preserves the planned Kobra 3 Max margin");
assert(IH>=753+35,
  "Height no longer preserves the planned Kobra 3 Max margin");
assert(SERVICE_BAY_W>=110 && SERVICE_BAY_W<=220,
  "Service bay must remain within the approved range");
assert(WINDOW_CUT_W+24<SERVICE_BAY_W,
  "Camera window and fastener border do not fit the service bay");

module timber_x(l) cube([l,B,B]);
module timber_y(l) cube([B,l,B]);
module timber_z(l) cube([B,B,l]);

module body_frame() {
  color([0.66,0.45,0.25]) {
    for (x=[0,W-B],y=[0,D-B]) translate([x,y,0]) timber_z(H);
    for (z=[0,H-B],y=[0,D-B]) translate([B,y,z]) timber_x(IW);
    for (z=[0,H-B],x=[0,W-B]) translate([x,B,z]) timber_y(ID);
    translate([(W-B)/2,B,H-B]) timber_y(ID);
    translate([STILE_X,0,B]) timber_z(IH);
  }
}

module white_inner_panels() {
  // Panels sit inside the external battens; the camera sees their white faces.
  color([0.97,0.97,0.95]) {
    translate([B,0,0]) cube([PANEL,D,H]);
    translate([W-B-PANEL,0,0]) cube([PANEL,D,H]);
    translate([0,D-B-PANEL,0]) cube([W,PANEL,H]);
  }
}

module fixed_service_panel() {
  // One-side-white hardboard replaces the former full-height clear front bay.
  color([0.97,0.97,0.95])
    difference() {
      translate([SERVICE_PANEL_X,-PANEL,B-DOOR_OVERLAP])
        cube([SERVICE_BAY_W,PANEL,DOOR_H]);
      translate([WINDOW_CX-WINDOW_CUT_W/2,-PANEL-EPS,
                 WINDOW_CZ-WINDOW_CUT_H/2])
        cube([WINDOW_CUT_W,PANEL+2*EPS,WINDOW_CUT_H]);
    }
}

module clear_door() {
  angle=SHOW_DOOR_OPEN ? -DOOR_ANGLE : 0;
  color([0.70,0.90,0.97,0.30])
    translate([B-DOOR_OVERLAP,-DOOR_G-3,B-DOOR_OVERLAP])
      rotate([0,0,angle]) cube([DOOR_W,DOOR_G,DOOR_H]);

  // Purchased continuous hinge and aluminium counterstrip.
  color([0.70,0.72,0.74])
    translate([B-DOOR_OVERLAP-4,-DOOR_G-5,48])
      rotate([0,0,angle]) cube([8,4,804]);
}

module optical_window_assembly() {
  fw=CAMERA_WINDOW_W+16;
  fh=CAMERA_WINDOW_H+16;

  // Matte-white inner bezel hides all dark cut edges in camera view.
  color([0.98,0.98,0.96])
    translate([WINDOW_CX-fw/2,PANEL+0.5,WINDOW_CZ-fh/2])
      rotate([90,0,0]) camera_window_inner_bezel();

  // Outside wedge establishes a controlled 7-degree anti-reflection tilt.
  color([0.18,0.19,0.20])
    translate([WINDOW_CX-fw/2,-PANEL-0.5,WINDOW_CZ-fh/2])
      rotate([90,0,0]) camera_window_outer_wedge();

  // Purchased clear PMMA/polycarbonate pane, shown as a thin optical plate.
  color([0.70,0.92,0.98,0.28])
    translate([WINDOW_CX-CAMERA_WINDOW_W/2,-10,
               WINDOW_CZ-CAMERA_WINDOW_H/2])
      rotate([0,0,CAMERA_WINDOW_TILT])
        cube([CAMERA_WINDOW_W,2,CAMERA_WINDOW_H]);

  color([0.18,0.19,0.20])
    translate([WINDOW_CX-fw/2,-15,WINDOW_CZ-fh/2])
      rotate([90,0,0]) camera_window_clamp_frame();
}

module roof_light_cassette() {
  color([0.94,0.97,0.97,0.72])
    translate([B,B,H+1]) cube([IW,ID,DIFFUSER]);

  if (SHOW_ROOF) {
    z=H+12;
    cw=W-2*LIGHT_CASSETTE_INSET;
    cd=D-2*LIGHT_CASSETTE_INSET;
    color([0.66,0.45,0.25]) {
      translate([LIGHT_CASSETTE_INSET,LIGHT_CASSETTE_INSET,z]) cube([cw,B,B]);
      translate([LIGHT_CASSETTE_INSET,D-LIGHT_CASSETTE_INSET-B,z]) cube([cw,B,B]);
      translate([LIGHT_CASSETTE_INSET,LIGHT_CASSETTE_INSET,z]) cube([B,cd,B]);
      translate([W-LIGHT_CASSETTE_INSET-B,LIGHT_CASSETTE_INSET,z]) cube([B,cd,B]);
    }

    // Six purchased aluminium heat spreaders with neutral-white high-CRI LEDs.
    for (x=[120,252,384,516,648,780]) {
      color([0.73,0.75,0.77]) translate([x,55,H+10]) cube([17,D-110,8]);
      color([1.0,0.86,0.36]) translate([x+4,56,H+9]) cube([9,D-112,2]);
    }

    color([0.94,0.94,0.92])
      translate([LIGHT_CASSETTE_INSET,LIGHT_CASSETTE_INSET,
                 H+LIGHT_CASSETTE_H])
        cube([cw,cd,3]);
  }
}

module fill_lights() {
  // Purchased opal aluminium profiles; independent dimming restores modelling.
  for (x=[B+PANEL+5,W-B-PANEL-15]) {
    color([0.73,0.75,0.77]) translate([x,B+6,120]) cube([10,14,610]);
    color([1.0,0.91,0.55]) translate([x+2,B+8,122]) cube([6,2,606]);
  }
}

module camera_subsystem() {
  rail_x=861;
  slider_z=552;

  // Purchased 2020 rail, completely outside the enclosure interior.
  color([0.55,0.57,0.59])
    translate([rail_x-10,-44,CAMERA_RAIL_Z]) cube([20,20,CAMERA_RAIL_H]);

  // Project-authored slider and short socket arm.
  color([0.17,0.18,0.19])
    translate([rail_x-22,-46,slider_z-45])
      rotate([90,0,0]) camera_2020_slider_fork();

  color([0.17,0.18,0.19])
    translate([rail_x-80,-59,slider_z-13])
      rotate([90,0,0]) camera_short_socket_arm();

  // Independently reconstructed case. Lens face points through the window.
  color([0.10,0.11,0.12])
    translate([WINDOW_CX-17,-22,WINDOW_CZ-25])
      rotate([90,0,0]) camera_front_shell();
  color([0.12,0.13,0.14])
    translate([WINDOW_CX-18.8,-35,WINDOW_CZ-26.9])
      rotate([90,0,0]) camera_back_cover_ball();
}

module exhaust_system() {
  ex_y=D-245;
  ex_z=650;

  // Project-authored matte-white internal sight baffle.
  color([0.97,0.97,0.95])
    translate([W-B-PANEL-3,ex_y,ex_z])
      rotate([0,90,0]) exhaust_camera_baffle_120();

  // Purchased 120 mm fan and optional printed hose adapter outside the wall.
  color([0.16,0.17,0.18])
    translate([W+2,ex_y+85,ex_z+85])
      rotate([0,90,0]) cylinder(d=120,h=26,$fn=72);
  color([0.25,0.26,0.27])
    translate([W+28,ex_y+85,ex_z+85])
      rotate([0,90,0]) fan_adapter_120_to_100();
}

module handling_hardware() {
  // Purchased through-bolted side handles with counterplates.
  color([0.18,0.19,0.20]) {
    translate([-12,D/2-70,400]) cube([12,140,26]);
    translate([W,D/2-70,400]) cube([12,140,26]);
  }
}

module approximate_printer_keepout() {
  px=(W-706)/2;
  py=(D-940)/2;
  color([0.14,0.15,0.16]) {
    translate([px+55,py+215,30]) cube([596,500,55]);
    translate([W/2-210,D/2-210,118]) cube([420,420,10]);
    translate([px+95,py+400,75]) cube([36,60,625]);
    translate([px+575,py+400,75]) cube([36,60,625]);
    translate([px+95,py+412,645]) cube([516,36,36]);
    translate([W/2-30,D/2-20,485]) cube([60,55,80]);
    translate([W-B-SERVICE_BAY_W+42,18,72]) cube([92,25,94]);
  }
  color([0.50,0.51,0.53])
    translate([W/2-75,D/2-75,128]) cylinder(d1=145,d2=95,h=220,$fn=80);
}

module table_reference() {
  color([0.75,0.75,0.72]) translate([-50,-50,-8]) cube([W+100,D+100,8]);
}

module complete_enclosure() {
  table_reference();
  body_frame();
  white_inner_panels();
  fixed_service_panel();
  clear_door();
  optical_window_assembly();
  roof_light_cassette();
  fill_lights();
  camera_subsystem();
  exhaust_system();
  handling_hardware();
  if (SHOW_PRINTER) approximate_printer_keepout();
}

complete_enclosure();
