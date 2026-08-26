/*
 Anycubic Kobra 3 Max – parametric camera-whitebox enclosure hardware
 Hybrid construction: 20x20 mm timber battens, white hardboard and sheet goods.
 Default outer dimensions: 900 x 1050 x 900 mm (W x D x H).
 The camera parts are an independent reconstruction from documented interface
 dimensions. No supplier or legacy mesh is imported by this source.
 License: CC BY 4.0.
*/

PART = is_undef(PART) ? "rail_286" : PART;
ENC_W = is_undef(ENC_W) ? 900 : ENC_W;
ENC_D = is_undef(ENC_D) ? 1050 : ENC_D;
ENC_H = is_undef(ENC_H) ? 900 : ENC_H;
BATTEN = is_undef(BATTEN) ? 20 : BATTEN;
GLASS = is_undef(GLASS) ? 4.0 : GLASS;
GLASS_CLEARANCE = is_undef(GLASS_CLEARANCE) ? 0.40 : GLASS_CLEARANCE;
CAMERA_RAIL_W = is_undef(CAMERA_RAIL_W) ? 20.0 : CAMERA_RAIL_W;
CAMERA_ARM_EYE_T = is_undef(CAMERA_ARM_EYE_T) ? 6.0 : CAMERA_ARM_EYE_T;
CAMERA_HINGE_CLEARANCE = is_undef(CAMERA_HINGE_CLEARANCE) ? 0.65 : CAMERA_HINGE_CLEARANCE;
CAMERA_HINGE_D = is_undef(CAMERA_HINGE_D) ? 4.5 : CAMERA_HINGE_D;
BAFFLE_DEPTH = is_undef(BAFFLE_DEPTH) ? 60.0 : BAFFLE_DEPTH;
CAMERA_FACE_W = is_undef(CAMERA_FACE_W) ? 22.50 : CAMERA_FACE_W;
CAMERA_FACE_H = is_undef(CAMERA_FACE_H) ? 38.50 : CAMERA_FACE_H;
CAMERA_REFERENCE_FULL_H = is_undef(CAMERA_REFERENCE_FULL_H) ? 43.50 : CAMERA_REFERENCE_FULL_H;
CAMERA_REFERENCE_DEPTH = is_undef(CAMERA_REFERENCE_DEPTH) ? 25.00 : CAMERA_REFERENCE_DEPTH;
CAMERA_PROTECTED_DEPTH = is_undef(CAMERA_PROTECTED_DEPTH) ? 25.30 : CAMERA_PROTECTED_DEPTH;
CAMERA_FIT_CLEARANCE = is_undef(CAMERA_FIT_CLEARANCE) ? 0.30 : CAMERA_FIT_CLEARANCE;
CAMERA_LENS_D = is_undef(CAMERA_LENS_D) ? 14.30 : CAMERA_LENS_D;
CAMERA_LED_D = is_undef(CAMERA_LED_D) ? 5.50 : CAMERA_LED_D;
CAMERA_BALL_D = is_undef(CAMERA_BALL_D) ? 11.00 : CAMERA_BALL_D;
CAMERA_BALL_CLEARANCE = is_undef(CAMERA_BALL_CLEARANCE) ? 0.28 : CAMERA_BALL_CLEARANCE;
CAMERA_WINDOW_W = is_undef(CAMERA_WINDOW_W) ? 80.0 : CAMERA_WINDOW_W;
CAMERA_WINDOW_H = is_undef(CAMERA_WINDOW_H) ? 90.0 : CAMERA_WINDOW_H;
CAMERA_WINDOW_TILT = is_undef(CAMERA_WINDOW_TILT) ? 7.0 : CAMERA_WINDOW_TILT;

RAIL_REACH = 16.0;
RAIL_BACK = 5.0;
RAIL_SLOT_DEPTH = RAIL_REACH - RAIL_BACK;
RAIL_WALL = 2.4;
RAIL_T = GLASS + GLASS_CLEARANCE + 2*RAIL_WALL;
RAIL_FLANGE = 12.0;
RAIL_FLANGE_T = 3.0;
PIN_CAVITY_W = 2.8;
PIN_CAVITY_H = 5.2;
PIN_DEPTH = 16.0;
EPS = 0.05;
$fn = 64;

module screw_hole_z(d=4.2,h=10) { translate([0,0,-EPS]) cylinder(d=d,h=h+2*EPS); }
module screw_hole_x(d=4.2,h=10) { rotate([0,90,0]) translate([0,0,-EPS]) cylinder(d=d,h=h+2*EPS); }
module screw_hole_y(d=4.2,h=10) { rotate([-90,0,0]) translate([0,0,-EPS]) cylinder(d=d,h=h+2*EPS); }

module capsule(length=44,width=16,height=5) {
  linear_extrude(height=height)
    hull() {
      translate([width/2,width/2]) circle(d=width);
      translate([length-width/2,width/2]) circle(d=width);
    }
}

module rounded_prism(size=[20,20,4],r=3) {
  assert(size[0]>2*r && size[1]>2*r && size[2]>0,
    "Rounded-prism dimensions must exceed twice the corner radius");
  linear_extrude(height=size[2])
    hull()
      for (x=[r,size[0]-r],y=[r,size[1]-r])
        translate([x,y]) circle(r=r,$fn=32);
}

// U-channel for an acrylic edge, screwed to a flat timber face.
// Print flat on the mounting flange. The acrylic slot opens toward +Y.
module acrylic_rail(length=286,holes=true) {
  difference() {
    union() {
      cube([length,RAIL_REACH,RAIL_T]);
      translate([0,-RAIL_FLANGE,0]) cube([length,RAIL_FLANGE+4,RAIL_FLANGE_T]);
    }
    translate([-EPS,RAIL_BACK,RAIL_WALL])
      cube([length+2*EPS,RAIL_SLOT_DEPTH+EPS,GLASS+GLASS_CLEARANCE]);

    // Short alignment cavities at both ends; no long unsupported tunnel.
    translate([-EPS,1.1,(RAIL_T-PIN_CAVITY_H)/2])
      cube([PIN_DEPTH+EPS,PIN_CAVITY_W,PIN_CAVITY_H]);
    translate([length-PIN_DEPTH,1.1,(RAIL_T-PIN_CAVITY_H)/2])
      cube([PIN_DEPTH+EPS,PIN_CAVITY_W,PIN_CAVITY_H]);

    if (holes) for (x=[length*0.25,length*0.75]) {
      translate([x,-RAIL_FLANGE*0.58,-EPS]) cylinder(d=3.7,h=RAIL_FLANGE_T+2*EPS);
      translate([x,-RAIL_FLANGE*0.58,1.0])
        cylinder(d1=3.7,d2=7.2,h=RAIL_FLANGE_T-0.9+EPS);
    }
  }
}

module rail_splice_pin(length=30) {
  pin_w=PIN_CAVITY_W-0.25;
  pin_h=PIN_CAVITY_H-0.25;
  hull() {
    translate([1.2,0,0]) cube([length-2.4,pin_w,pin_h]);
    translate([0.3,0.25,0.25]) cube([length-0.6,pin_w-0.5,pin_h-0.5]);
  }
}

module rail_end_stop() {
  union() {
    cube([2,RAIL_REACH,RAIL_T]);
    translate([2,1.225,(RAIL_T-(PIN_CAVITY_H-0.25))/2])
      cube([12,PIN_CAVITY_W-0.25,PIN_CAVITY_H-0.25]);
  }
}

// Exterior 3-way timber corner bracket; one geometry works at all 8 corners by rotation.
module corner_gusset_3way(size=55,t=4) {
  difference() {
    union() {
      cube([size,size,t]);
      cube([size,t,size]);
      cube([t,size,size]);
      cube([12,12,12]);
    }
    for (p=[[16,34],[34,16],[40,40]]) translate([p[0],p[1],0]) screw_hole_z(4.3,t);
    for (p=[[16,34],[34,16],[40,40]]) translate([p[0],0,p[1]]) screw_hole_y(4.3,t);
    for (p=[[16,34],[34,16],[40,40]]) translate([0,p[0],p[1]]) screw_hole_x(4.3,t);
  }
}

module flat_t_bracket(t=4) {
  difference() {
    linear_extrude(height=t) union() {
      translate([0,18]) square([100,24]);
      translate([38,0]) square([24,60]);
    }
    for (p=[[15,30],[30,30],[70,30],[85,30],[50,10],[50,50]])
      translate([p[0],p[1],0]) screw_hole_z(4.3,t);
  }
}

module base_anchor(t=4) {
  difference() {
    union() { cube([45,28,t]); cube([45,t,28]); cube([8,8,8]); }
    for (x=[12,33]) translate([x,15,0]) screw_hole_z(4.3,t);
    for (x=[12,33]) translate([x,0,15]) screw_hole_y(4.3,t);
  }
}

module turn_clip() {
  difference() {
    union() { capsule(44,16,5); translate([34,3,5]) cube([8,10,1.2]); }
    translate([8,8,0]) screw_hole_z(4.4,7);
  }
}

module turn_clip_spacer() {
  difference() { cylinder(d=15,h=5); translate([0,0,-EPS]) cylinder(d=4.4,h=5+2*EPS); }
}

module panel_knob() {
  difference() {
    union() {
      cylinder(d=28,h=4);
      translate([0,0,4]) cylinder(d1=16,d2=13,h=15);
      translate([0,0,19]) cylinder(d=32,h=8);
    }
    translate([0,0,-EPS]) cylinder(d=4.4,h=28+2*EPS);
    translate([0,0,22]) cylinder(d=8.2,h=6.2);
  }
}

module panel_retainer_clip() {
  difference() {
    union() { cube([30,18,4]); translate([20,0,4]) cube([10,18,GLASS+1]); }
    translate([8,9,0]) screw_hole_z(4.3,4);
  }
}


module front_panel_shelf() {
  // Support ledge for the heavy removable front acrylic panel.
  // Print with the shelf on the bed; install the tall plate against the lower front timber.
  difference() {
    union() {
      cube([50,14,4]);          // horizontal shelf
      cube([50,4,30]);          // mounting plate
      translate([0,11,0]) cube([50,3,9]); // retaining lip
    }
    for (x=[13,37])
      translate([x,0,19]) screw_hole_y(4.3,4);
  }
}

module service_panel_120_ports() {
  pw=280; ph=200; pt=3; cw=250; ch=170; lt=3; lw=3; fx=82; fy=100;
  difference() {
    union() {
      cube([pw,ph,pt]);
      translate([(pw-cw)/2,(ph-ch)/2,pt])
        difference() {
          cube([cw-0.6,ch-0.6,lt]);
          translate([lw,lw,-EPS]) cube([cw-0.6-2*lw,ch-0.6-2*lw,lt+2*EPS]);
        }
    }
    translate([fx,fy,-EPS]) cylinder(d=114,h=pt+lt+2*EPS,$fn=128);
    for (dx=[-52.5,52.5],dy=[-52.5,52.5])
      translate([fx+dx,fy+dy,-EPS]) cylinder(d=4.5,h=pt+lt+2*EPS);
    for (p=[[190,145],[225,145]])
      translate([p[0],p[1],-EPS]) cylinder(d=10.2,h=pt+lt+2*EPS);
    translate([255,145,-EPS]) cylinder(d=20.5,h=pt+lt+2*EPS);
    translate([210,60,-EPS]) cylinder(d=38,h=pt+lt+2*EPS,$fn=96);
    translate([255,70,-EPS]) cylinder(d=6.5,h=pt+lt+2*EPS);
    for (p=[[10,10],[140,10],[270,10],[10,190],[140,190],[270,190],[10,100],[270,100]])
      translate([p[0],p[1],-EPS]) cylinder(d=4.3,h=pt+lt+2*EPS);
  }
}

module service_panel_blank() {
  pw=280; ph=200; pt=3; cw=250; ch=170; lt=3; lw=3;
  difference() {
    union() {
      cube([pw,ph,pt]);
      translate([(pw-cw)/2,(ph-ch)/2,pt])
        difference() {
          cube([cw-0.6,ch-0.6,lt]);
          translate([lw,lw,-EPS]) cube([cw-0.6-2*lw,ch-0.6-2*lw,lt+2*EPS]);
        }
    }
    for (p=[[10,10],[140,10],[270,10],[10,190],[140,190],[270,190],[10,100],[270,100]])
      translate([p[0],p[1],-EPS]) cylinder(d=4.3,h=pt+lt+2*EPS);
  }
}

module fan_adapter_120_to_100() {
  flange=125; ft=3; cone_h=45; tube_h=30; wall=2.5;
  difference() {
    union() {
      translate([-flange/2,-flange/2,0]) cube([flange,flange,ft]);
      translate([0,0,ft]) cylinder(h=cone_h,d1=120,d2=100,$fn=128);
      translate([0,0,ft+cone_h]) cylinder(h=tube_h,d=100,$fn=128);
      translate([0,0,ft+cone_h+tube_h-8]) cylinder(h=2,d=102,$fn=128);
      translate([0,0,ft+cone_h+tube_h-3]) cylinder(h=2,d=102,$fn=128);
    }
    translate([0,0,-EPS]) cylinder(h=ft+EPS,d=114,$fn=128);
    translate([0,0,ft-EPS]) cylinder(h=cone_h+2*EPS,d1=114,d2=95,$fn=128);
    translate([0,0,ft+cone_h-EPS]) cylinder(h=tube_h+2*EPS,d=95,$fn=128);
    for (dx=[-52.5,52.5],dy=[-52.5,52.5])
      translate([dx,dy,-EPS]) cylinder(d=4.5,h=ft+2*EPS);
  }
}

module fan_guard_120() {
  t=3;
  difference() {
    union() {
      // Connected square perimeter with airflow bars.
      difference() { cube([120,120,t]); translate([6,6,-EPS]) cube([108,108,t+2*EPS]); }
      translate([6,57.8,0]) cube([108,4.4,t]);
      translate([57.8,6,0]) cube([4.4,108,t]);
      translate([20,20,0]) rotate([0,0,45]) cube([113,3.4,t]);
      translate([20,100,0]) rotate([0,0,-45]) cube([113,3.4,t]);
    }
    for (x=[7.5,112.5],y=[7.5,112.5]) translate([x,y,-EPS]) cylinder(d=4.5,h=t+2*EPS);
  }
}

module cable_grommet_half(side=1) {
  difference() {
    intersection() {
      union() { cylinder(d=46,h=3,$fn=96); translate([0,0,3]) cylinder(d=37.6,h=4,$fn=96); }
      if (side>0) translate([0,-30,-EPS]) cube([30,60,8]);
      else translate([-30,-30,-EPS]) cube([30,60,8]);
    }
    translate([0,0,-EPS]) cylinder(d=8.5,h=8.2,$fn=64);
  }
}

module rail_test_coupon() { acrylic_rail(50,false); }

// Sliding camera base for a purchased 20x20 T-slot extrusion. The fork accepts
// the independently designed short socket arm below; no legacy arm is needed.
// Print with the rounded mounting plate on the bed; no support is required.
module camera_2020_slider_fork() {
  plate_w=44;
  plate_h=90;
  plate_t=5;
  plate_r=4;
  ear_r=9;
  ear_t=3.0;
  fork_gap=CAMERA_ARM_EYE_T+CAMERA_HINGE_CLEARANCE;
  fork_cx=-4;
  fork_cy=plate_h/2;
  fork_cz=plate_t+ear_r;
  neck_x=12;

  assert(CAMERA_RAIL_W>=15 && CAMERA_RAIL_W<=30,
    "CAMERA_RAIL_W must suit a compact T-slot extrusion");
  assert(fork_gap>CAMERA_ARM_EYE_T,
    "Camera fork gap must exceed arm-eye thickness");
  assert(CAMERA_HINGE_D>=4.2 && CAMERA_HINGE_D<=5.0,
    "Camera hinge hole must suit M4 hardware");

  difference() {
    union() {
      linear_extrude(height=plate_t)
        hull()
          for (x=[plate_r,plate_w-plate_r], y=[plate_r,plate_h-plate_r])
            translate([x,y]) circle(r=plate_r,$fn=32);

      for (ear_y=[fork_cy-fork_gap/2-ear_t, fork_cy+fork_gap/2]) {
        translate([fork_cx,ear_y,plate_t])
          cube([neck_x-fork_cx,ear_t,ear_r]);
        translate([fork_cx,ear_y,fork_cz])
          rotate([-90,0,0]) cylinder(r=ear_r,h=ear_t,$fn=64);
      }
    }

    // Two M5 slots allow alignment on a single 2020-extrusion T-slot.
    for (slot_y=[23,67]) {
      hull()
        for (dy=[-6,6])
          translate([plate_w/2,slot_y+dy,-EPS])
            cylinder(d=5.6,h=plate_t+2*EPS,$fn=36);
      hull()
        for (dy=[-6,6])
          translate([plate_w/2,slot_y+dy,plate_t-2.2])
            cylinder(d=10.2,h=2.2+EPS,$fn=48);
    }

    translate([fork_cx,
               fork_cy-fork_gap/2-ear_t-EPS,
               fork_cz])
      rotate([-90,0,0])
        cylinder(d=CAMERA_HINGE_D,
                 h=fork_gap+2*ear_t+2*EPS,
                 $fn=40);
  }
}

// Corner locator for the removable roof-light cassette.
// Four copies constrain the cassette laterally; two metal latches or screws
// retain it vertically. Print on the flat base without support.
module roof_cassette_corner_locator() {
  s=46;
  base_t=4;
  wall_t=4;
  wall_h=18;
  difference() {
    union() {
      cube([s,s,base_t]);
      cube([s,wall_t,wall_h]);
      cube([wall_t,s,wall_h]);
      translate([wall_t,wall_t,base_t])
        linear_extrude(height=wall_h-base_t)
          polygon([[0,0],[12,0],[0,12]]);
    }
    for (p=[[17,28],[28,17]])
      translate([p[0],p[1],-EPS])
        cylinder(d=4.3,h=base_t+2*EPS,$fn=32);
  }
}

// Small process coupon for the existing camera-arm eye. Print this before the
// complete slider and verify free rotation plus M4 clamp friction.
module camera_fork_fit_coupon() {
  base_w=34;
  base_h=38;
  base_t=4;
  ear_r=9;
  ear_t=3.0;
  fork_gap=CAMERA_ARM_EYE_T+CAMERA_HINGE_CLEARANCE;
  fork_cx=base_w/2;
  fork_cy=base_h/2;
  fork_cz=base_t+ear_r;

  difference() {
    union() {
      cube([base_w,base_h,base_t]);
      for (ear_y=[fork_cy-fork_gap/2-ear_t, fork_cy+fork_gap/2]) {
        translate([fork_cx-ear_r,ear_y,base_t])
          cube([2*ear_r,ear_t,ear_r]);
        translate([fork_cx,ear_y,fork_cz])
          rotate([-90,0,0]) cylinder(r=ear_r,h=ear_t,$fn=64);
      }
    }
    translate([fork_cx,
               fork_cy-fork_gap/2-ear_t-EPS,
               fork_cz])
      rotate([-90,0,0])
        cylinder(d=CAMERA_HINGE_D,
                 h=fork_gap+2*ear_t+2*EPS,
                 $fn=40);
  }
}

// Matte-white sight baffle for the inside of the 120 mm exhaust opening.
// The fan remains behind the wall; air enters through the full-width bottom
// gap while the camera sees a continuous white face. Print face-down.
module exhaust_camera_baffle_120() {
  cover=170;
  face_t=2.6;
  wall_t=2.6;
  depth=BAFFLE_DEPTH;
  boss_d=11;
  hole_d=4.5;
  boss_offset=13;

  assert(depth>=45,
    "BAFFLE_DEPTH below 45 mm restricts the bottom inlet excessively");
  assert(cover>=150,
    "Baffle cover must conceal a 120 mm fan and mounting hardware");

  difference() {
    union() {
      cube([cover,cover,face_t]);
      translate([0,0,face_t]) cube([wall_t,cover,depth-face_t]);
      translate([cover-wall_t,0,face_t]) cube([wall_t,cover,depth-face_t]);
      translate([0,cover-wall_t,face_t]) cube([cover,wall_t,depth-face_t]);

      // Through-bolt standoffs connect the face to the wall panel.
      for (x=[boss_offset,cover-boss_offset],
           y=[boss_offset,cover-boss_offset])
        translate([x,y,0]) cylinder(d=boss_d,h=depth,$fn=48);
    }

    for (x=[boss_offset,cover-boss_offset],
         y=[boss_offset,cover-boss_offset])
      translate([x,y,-EPS])
        cylinder(d=hole_d,h=depth+2*EPS,$fn=36);
  }
}

// Shallow ring that verifies the real camera face/body fit before the complete
// shell is printed. Nominal cavity: 22.50 x 38.50 mm plus 0.30 mm per side.
module camera_fit_frame_coupon() {
  cw=CAMERA_FACE_W+2*CAMERA_FIT_CLEARANCE;
  ch=CAMERA_FACE_H+2*CAMERA_FIT_CLEARANCE;
  wall=3.0;
  difference() {
    rounded_prism([cw+2*wall,ch+2*wall,4],2.2);
    translate([wall,wall,-EPS]) cube([cw,ch,4+2*EPS]);
  }
}

// Front shell for the original Anycubic Live View camera module. The retained
// optical openings follow the official reference interface; the outer styling,
// fasteners and all remaining geometry are newly authored here.
module camera_front_shell() {
  ow=34;
  oh=50;
  depth=13.5;
  face_t=2.2;
  cw=CAMERA_FACE_W+2*CAMERA_FIT_CLEARANCE;
  ch=CAMERA_FACE_H+2*CAMERA_FIT_CLEARANCE;
  lens_y=oh/2+5.57;
  led_y=oh/2-8.83;

  assert(CAMERA_FIT_CLEARANCE>=0.15 && CAMERA_FIT_CLEARANCE<=0.60,
    "Camera fit clearance must stay coupon-testable");
  assert(CAMERA_LENS_D>=14.0 && CAMERA_LENS_D<=15.0,
    "Camera lens opening is outside the documented interface range");

  difference() {
    rounded_prism([ow,oh,depth],3.0);
    translate([(ow-cw)/2,(oh-ch)/2,face_t])
      cube([cw,ch,depth-face_t+EPS]);
    translate([ow/2,lens_y,-EPS])
      cylinder(d=CAMERA_LENS_D+0.40,h=face_t+2*EPS,$fn=72);
    for (x=[ow/2-3.0,ow/2+3.0])
      translate([x,led_y,-EPS])
        cylinder(d=CAMERA_LED_D+0.40,h=face_t+2*EPS,$fn=48);

    // Two bounded M2.5 pilot holes for low-cost self-tapping case screws.
    for (x=[3.2,ow-3.2])
      translate([x,oh/2,depth-6]) cylinder(d=2.1,h=6+EPS,$fn=32);
  }
}

// Rear cap with an external overlap skirt, protected rear cavity, cable relief
// and integral 11 mm ball. Together with the 13.5 mm front shell it provides
// 25.3 mm protected depth (25.0 mm official reference extent + 0.3 mm).
// Print with the open mating side on the bed; the 24 mm roof bridge and ball
// grow between the two screw towers without generated support.
module camera_back_cover_ball() {
  shell_w=34;
  shell_h=50;
  skirt_clearance=0.25;
  skirt_wall=1.8;
  overlap_d=4.0;
  rear_inner_d=8.8;
  cap_t=3.0;
  cover_d=overlap_d+rear_inner_d+cap_t;
  ow=shell_w+2*(skirt_clearance+skirt_wall);
  oh=shell_h+2*(skirt_clearance+skirt_wall);
  shell_x=skirt_clearance+skirt_wall;
  shell_y=skirt_clearance+skirt_wall;
  rear_cavity_w=24.0;
  rear_cavity_h=40.2;
  ball_z=cover_d+6.0;

  assert(13.5+cover_d-overlap_d>=CAMERA_PROTECTED_DEPTH,
    "Front and rear shells do not provide the declared protected depth");
  assert(CAMERA_PROTECTED_DEPTH>=CAMERA_REFERENCE_DEPTH+0.20,
    "Protected depth needs at least 0.20 mm allowance over the reference");

  difference() {
    union() {
      difference() {
        rounded_prism([ow,oh,cover_d],3.5);
        // First section slips over the front shell.
        translate([shell_x,shell_y,-EPS])
          rounded_prism([shell_w+2*skirt_clearance,
                         shell_h+2*skirt_clearance,
                         overlap_d+EPS],2.9);
        // Rear cavity continues to the 3 mm protective cap.
        translate([(ow-rear_cavity_w)/2,(oh-rear_cavity_h)/2,
                   overlap_d-EPS])
          rounded_prism([rear_cavity_w,rear_cavity_h,
                         rear_inner_d+2*EPS],2.4);
      }

      // Long-screw towers bridge the rear cavity to the front-shell pilots.
      for (x=[shell_x+3.2,shell_x+shell_w-3.2])
        translate([x,shell_y+shell_h/2,overlap_d-EPS])
          cylinder(d=5.2,h=rear_inner_d+cap_t+EPS,$fn=40);

      translate([ow/2,oh/2,cover_d-EPS])
        cylinder(d=5.0,h=7.0,$fn=48);
      translate([ow/2,oh/2,ball_z]) sphere(d=CAMERA_BALL_D,$fn=72);
    }

    // Cable exits downward when the camera is installed.
    translate([ow/2-5,-EPS,-EPS])
      cube([10,(oh-rear_cavity_h)/2+2*EPS,cover_d-cap_t+EPS]);
    // M2.5 clearance holes align with the front-shell pilot holes.
    for (x=[shell_x+3.2,shell_x+shell_w-3.2])
      translate([x,shell_y+shell_h/2,-EPS])
        cylinder(d=2.8,h=cover_d+2*EPS,$fn=32);
    // Four rear ventilation slots remain outside the white-box interior.
    for (x=[ow/2-9,ow/2-5.5,ow/2+5.5,ow/2+9])
      translate([x-1,oh/2-9,cover_d-cap_t-EPS])
        cube([2,18,cap_t+2*EPS]);
  }
}

module camera_socket_body(clearance=CAMERA_BALL_CLEARANCE) {
  outer_d=20;
  body_h=13;
  cavity_d=CAMERA_BALL_D+2*clearance;
  cavity_z=7.5;
  entry_d=9.2;
  difference() {
    cylinder(d=outer_d,h=body_h,$fn=72);
    translate([0,0,cavity_z]) sphere(d=cavity_d,$fn=72);
    translate([0,0,cavity_z]) cylinder(d=entry_d,h=body_h,$fn=48);
    // Flex slit opens away from the arm and permits controlled ball insertion.
    translate([-1.0,-outer_d/2-EPS,cavity_z])
      cube([2.0,outer_d/2+EPS,body_h-cavity_z+EPS]);
  }
}

// Short, support-free arm. The 6 mm eye fits the slider fork; the three-value
// coupon below must select the production socket clearance for the local PETG.
module camera_short_socket_arm(clearance=CAMERA_BALL_CLEARANCE) {
  eye=[10,13];
  socket=[80,13];
  eye_t=CAMERA_ARM_EYE_T;
  difference() {
    union() {
      hull() {
        translate([eye[0],eye[1],0]) cylinder(d=20,h=eye_t,$fn=56);
        translate([socket[0],socket[1],0]) cylinder(d=20,h=eye_t,$fn=56);
      }
      translate([socket[0],socket[1],0]) camera_socket_body(clearance);
    }
    translate([eye[0],eye[1],-EPS])
      cylinder(d=CAMERA_HINGE_D,h=eye_t+2*EPS,$fn=40);
  }
}

module camera_ball_test_pin() {
  union() {
    rounded_prism([26,26,3],3);
    translate([13,13,3-EPS]) cylinder(d=5,h=7,$fn=48);
    translate([13,13,9]) sphere(d=CAMERA_BALL_D,$fn=72);
  }
}

// One connected coupon, left to right: 0.15 / 0.28 / 0.40 mm radial clearance.
module camera_ball_socket_coupon() {
  clearances=[0.15,0.28,0.40];
  difference() {
    union() {
      rounded_prism([82,30,2],3);
      for (i=[0:2])
        translate([15+26*i,15,0]) camera_socket_body(clearances[i]);
      for (i=[0:2],p=[0:i])
        translate([11+26*i+3*p,3,2]) cylinder(d=2.2,h=1.2,$fn=24);
    }
  }
}

module camera_window_inner_bezel() {
  outer_w=CAMERA_WINDOW_W+16;
  outer_h=CAMERA_WINDOW_H+16;
  opening_w=CAMERA_WINDOW_W-8;
  opening_h=CAMERA_WINDOW_H-8;
  difference() {
    rounded_prism([outer_w,outer_h,3],4);
    translate([(outer_w-opening_w)/2,(outer_h-opening_h)/2,-EPS])
      rounded_prism([opening_w,opening_h,3+2*EPS],2.5);
    for (x=[7,outer_w-7],y=[7,outer_h-7])
      translate([x,y,-EPS]) cylinder(d=4.5,h=3+2*EPS,$fn=32);
  }
}

// Wedge thickness varies across X to tilt the clear optical pane by 7 degrees.
module camera_window_outer_wedge() {
  outer_w=CAMERA_WINDOW_W+16;
  outer_h=CAMERA_WINDOW_H+16;
  frame=8;
  z0=3.0;
  dz=tan(CAMERA_WINDOW_TILT)*outer_w;

  module wedge_bar(x0,y0,x1,y1) {
    polyhedron(
      points=[
        [x0,y0,0],[x1,y0,0],[x1,y1,0],[x0,y1,0],
        [x0,y0,z0+dz*x0/outer_w],[x1,y0,z0+dz*x1/outer_w],
        [x1,y1,z0+dz*x1/outer_w],[x0,y1,z0+dz*x0/outer_w]
      ],
      faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],
             [2,3,7,6],[3,0,4,7]],convexity=4);
  }

  assert(CAMERA_WINDOW_TILT>=4 && CAMERA_WINDOW_TILT<=10,
    "Optical window tilt must remain between 4 and 10 degrees");
  difference() {
    union() {
      wedge_bar(0,0,outer_w,frame);
      wedge_bar(0,outer_h-frame,outer_w,outer_h);
      wedge_bar(0,frame,frame,outer_h-frame);
      wedge_bar(outer_w-frame,frame,outer_w,outer_h-frame);
    }
    for (x=[7,outer_w-7],y=[7,outer_h-7])
      translate([x,y,-EPS]) cylinder(d=4.8,h=z0+dz+2*EPS,$fn=32);
  }
}

module camera_window_clamp_frame() {
  outer_w=CAMERA_WINDOW_W+16;
  outer_h=CAMERA_WINDOW_H+16;
  difference() {
    rounded_prism([outer_w,outer_h,2.5],4);
    translate([8,8,-EPS])
      rounded_prism([outer_w-16,outer_h-16,2.5+2*EPS],2.5);
    for (x=[7,outer_w-7],y=[7,outer_h-7])
      translate([x,y,-EPS]) cylinder(d=5.2,h=2.5+2*EPS,$fn=32);
  }
}

// Optional screw-on clip for common 17 x 8 mm aluminium LED profiles.
module led_profile_clip_17x8() {
  difference() {
    union() {
      rounded_prism([31,18,3],3);
      translate([5,3,3]) cube([2.4,12,8]);
      translate([23.6,3,3]) cube([2.4,12,8]);
      translate([5,3,9]) cube([4.2,12,2]);
      translate([21.8,3,9]) cube([4.2,12,2]);
    }
    translate([15.5,9,-EPS]) cylinder(d=4.3,h=3+2*EPS,$fn=32);
  }
}

module render_selected_part() {
  if (PART=="rail_286") acrylic_rail(286,true);
  else if (PART=="rail_143") acrylic_rail(143,true);
  else if (PART=="rail_test_coupon") rail_test_coupon();
  else if (PART=="rail_splice_pin") rail_splice_pin(30);
  else if (PART=="rail_end_stop") translate([RAIL_T,0,0]) rotate([0,-90,0]) rail_end_stop();
  else if (PART=="corner_gusset_3way") corner_gusset_3way();
  else if (PART=="flat_t_bracket") flat_t_bracket();
  else if (PART=="base_anchor") base_anchor();
  else if (PART=="turn_clip") turn_clip();
  else if (PART=="turn_clip_spacer") turn_clip_spacer();
  else if (PART=="panel_knob") panel_knob();
  else if (PART=="panel_retainer_clip") panel_retainer_clip();
  else if (PART=="front_panel_shelf") front_panel_shelf();
  else if (PART=="service_panel_120_ports") service_panel_120_ports();
  else if (PART=="service_panel_blank") service_panel_blank();
  else if (PART=="fan_adapter_120_to_100") fan_adapter_120_to_100();
  else if (PART=="fan_guard_120") fan_guard_120();
  else if (PART=="cable_grommet_half_A") cable_grommet_half(1);
  else if (PART=="cable_grommet_half_B") cable_grommet_half(-1);
  else if (PART=="camera_2020_slider_fork") camera_2020_slider_fork();
  else if (PART=="camera_fork_fit_coupon") camera_fork_fit_coupon();
  else if (PART=="camera_fit_frame_coupon") camera_fit_frame_coupon();
  else if (PART=="camera_front_shell") camera_front_shell();
  else if (PART=="camera_back_cover_ball") camera_back_cover_ball();
  else if (PART=="camera_short_socket_arm") camera_short_socket_arm();
  else if (PART=="camera_ball_test_pin") camera_ball_test_pin();
  else if (PART=="camera_ball_socket_coupon") camera_ball_socket_coupon();
  else if (PART=="camera_window_inner_bezel") camera_window_inner_bezel();
  else if (PART=="camera_window_outer_wedge") camera_window_outer_wedge();
  else if (PART=="camera_window_clamp_frame") camera_window_clamp_frame();
  else if (PART=="led_profile_clip_17x8") led_profile_clip_17x8();
  else if (PART=="roof_cassette_corner_locator") roof_cassette_corner_locator();
  else if (PART=="exhaust_camera_baffle_120") exhaust_camera_baffle_120();
  else rail_test_coupon();
}

if (is_undef(LIBRARY_MODE) ? true : !LIBRARY_MODE) render_selected_part();
