/*
  Schmaler, wandgeklebter Drybox-Stangenhalter
  für Aluminiumrohr Außendurchmesser 23.5 mm.
  Identisches Teil zweimal drucken.

  Die große flache Rückseite wird an die beiden gegenüberliegenden
  Innenwände der Box geklebt. Die Aufnahme ist nach oben offen, sodass
  das Rohr mitsamt Rollen herausgehoben werden kann.
*/
$fn = 160;

rohr_d = 23.5;
aufnahme_d = 24.8;       // 1,3 mm Gesamtspiel
platte_b = 48.0;
platte_h = 78.0;
platte_t = 9.0;
ecken_r = 5.0;
aufnahme_y = 57.0;
trichter_start_y = 67.0;
trichter_oben_b = 32.0;

module rounded_rect_2d(w,h,r) {
  hull() {
    for (x=[-1,1], y=[0,1])
      translate([x*(w/2-r), r+y*(h-2*r)]) circle(r=r);
  }
}

module wandhalter() {
  linear_extrude(height=platte_t)
  difference() {
    rounded_rect_2d(platte_b, platte_h, ecken_r);
    translate([0,aufnahme_y]) circle(d=aufnahme_d);
    translate([-aufnahme_d/2,aufnahme_y])
      square([aufnahme_d,trichter_start_y-aufnahme_y+0.1]);
    polygon(points=[
      [-aufnahme_d/2,trichter_start_y],
      [ aufnahme_d/2,trichter_start_y],
      [ trichter_oben_b/2,platte_h+0.5],
      [-trichter_oben_b/2,platte_h+0.5]
    ]);
  }
}

wandhalter();
