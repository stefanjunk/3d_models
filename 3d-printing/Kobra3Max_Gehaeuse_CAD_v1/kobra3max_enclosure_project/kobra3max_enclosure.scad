/*
 Anycubic Kobra 3 Max – parametric budget enclosure hardware
 Hybrid construction: 20x20 mm timber battens + 4 mm acrylic panels.
 Default outer dimensions: 900 x 1050 x 900 mm (W x D x H).
 License: CC BY 4.0.
*/

PART = is_undef(PART) ? "rail_286" : PART;
ENC_W = is_undef(ENC_W) ? 900 : ENC_W;
ENC_D = is_undef(ENC_D) ? 1050 : ENC_D;
ENC_H = is_undef(ENC_H) ? 900 : ENC_H;
BATTEN = is_undef(BATTEN) ? 20 : BATTEN;
GLASS = is_undef(GLASS) ? 4.0 : GLASS;
GLASS_CLEARANCE = is_undef(GLASS_CLEARANCE) ? 0.40 : GLASS_CLEARANCE;

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
else rail_test_coupon();
