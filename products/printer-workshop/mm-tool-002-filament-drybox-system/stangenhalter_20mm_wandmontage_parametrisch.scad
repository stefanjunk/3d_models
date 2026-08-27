/*
  Schmale Wandhalter für BAUHAUS / Ezy Storage 18 L
  Aluminium-Rundstange Ø20 mm, identisches Teil 2x drucken.

  Die große flache Rückseite wird an die beiden kurzen Innenwände geklebt.
  Die Boxwand bildet den axialen Anschlag. Die U-Nut bleibt oben offen,
  sodass die Stange mitsamt Rollen nach oben herausgehoben werden kann.

  Empfohlene Einbauposition für typische Rollen bis Ø203,2 mm:
    Stangenmitte 107 mm über dem tiefsten Boxboden.
    Stangenmitte etwa 104 mm von der vorderen Innenwand.
  Die zweite Angabe muss an der realen Box geprüft werden.
*/
$fn = 128;
rod_d = 20.0;
seat_d = 21.2;
plate_t = 8;
plate_w = 44;
plate_h = 76;
seat_z = 56;

module rounded2d(w,h,r) {
  hull() for (x=[-1,1], y=[-1,1])
    translate([x*(w/2-r), y*(h/2-r)]) circle(r=r);
}

module wall_holder_20mm() {
  difference() {
    linear_extrude(height=plate_t)
      translate([0,plate_h/2]) rounded2d(plate_w,plate_h,5);

    translate([0,seat_z,-0.2]) cylinder(d=seat_d,h=plate_t+0.4);
    translate([-seat_d/2,seat_z,-0.2]) cube([seat_d,plate_h-seat_z+1,plate_t+0.4]);
    hull() {
      translate([-seat_d/2,67,-0.2]) cube([seat_d,1,plate_t+0.4]);
      translate([-14.6,75,-0.2]) cube([29.2,1.5,plate_t+0.4]);
    }
  }
}

wall_holder_20mm();
