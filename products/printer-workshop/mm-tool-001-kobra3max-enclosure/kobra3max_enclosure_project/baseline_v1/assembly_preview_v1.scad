/* Visual, non-printable reference assembly for the Kobra 3 Max enclosure. */
W=900; D=1050; H=900; B=20; G=4;
IW=W-2*B; ID=D-2*B; IH=H-2*B;

module timber_x(l) cube([l,B,B]);
module timber_y(l) cube([B,l,B]);
module timber_z(l) cube([B,B,l]);

module frame() {
  color([0.72,0.52,0.28]) {
    for (x=[0,W-B],y=[0,D-B]) translate([x,y,0]) timber_z(H);
    for (z=[0,H-B],y=[0,D-B]) translate([B,y,z]) timber_x(IW);
    for (z=[0,H-B],x=[0,W-B]) translate([x,B,z]) timber_y(ID);
    translate([(W-B)/2,B,H-B]) timber_y(ID);
  }
}

module panels() {
  color([0.45,0.78,0.92,0.32]) {
    translate([B+3,B+5,B+2]) cube([G,999,856]);
    translate([W-B-3-G,B+5,B+2]) cube([G,999,856]);
    translate([B+5,D-B-3-G,B+2]) cube([849,G,856]);
    translate([10,-G-2,10]) cube([880,G,880]);
    translate([5,5,H+1]) cube([450,1040,G]);
    translate([W-455,5,H+1]) cube([450,1040,G]);
  }
}

module printer_keepout() {
  // Conservative planning envelope: 706 W x 940 D x 753 H.
  color([0.25,0.25,0.30,0.20])
    translate([(W-706)/2,(D-940)/2,18]) cube([706,940,753]);
}

module base() {
  color([0.45,0.30,0.18]) translate([0,0,-18]) cube([W,D,18]);
}

base(); frame(); panels(); printer_keepout();
