/*
  Zwei lange, flache Silicagel-Behälter für BAUHAUS / Ezy Storage 18 L.
  Jeweils body und lid zweimal drucken.
  part = "body", "lid" oder "layout".

  Default-Außenmaße:
  Body 276 x 35.2 x 24 mm
  Deckel-Fußabdruck 280.4 x 39.6 mm
  Geschlossene Bauhöhe ca. 26 mm
*/
part="layout";
$fn=48;
L=276; W=35.2; H=24;
wall=2; floor_h=2; rail_h=3.2;
bar=2.0; gap=1.6; step=bar+gap;
clearance=0.6; skirt=1.6; skirt_h=4; top_t=2; frame=3.2;

module body(){
  union(){
    cube([L,W,floor_h]);
    cube([wall,W,H]);
    translate([L-wall,0,0]) cube([wall,W,H]);
    for(y=[0,W-wall]){
      translate([0,y,floor_h]) cube([L,wall,rail_h]);
      translate([0,y,H-rail_h]) cube([L,wall,rail_h]);
      for(x=[wall:step:L-wall-bar])
        translate([x,y,floor_h+rail_h]) cube([bar,wall,H-floor_h-2*rail_h]);
    }
  }
}
module lid(){
  cavL=L+2*clearance; cavW=W+2*clearance;
  outL=cavL+2*skirt; outW=cavW+2*skirt;
  union(){
    // Übersteck-Rand
    cube([outL,skirt,skirt_h]);
    translate([0,outW-skirt,0]) cube([outL,skirt,skirt_h]);
    cube([skirt,outW,skirt_h]);
    translate([outL-skirt,0,0]) cube([skirt,outW,skirt_h]);
    // Rahmen und Lüftungsstege
    translate([0,0,skirt_h]) cube([outL,frame,top_t]);
    translate([0,outW-frame,skirt_h]) cube([outL,frame,top_t]);
    translate([0,0,skirt_h]) cube([frame,outW,top_t]);
    translate([outL-frame,0,skirt_h]) cube([frame,outW,top_t]);
    for(x=[frame:step:outL-frame-bar])
      translate([x,frame,skirt_h]) cube([bar,outW-2*frame,top_t]);
  }
}
if(part=="body") body();
else if(part=="lid") lid();
else { body(); translate([0,W+20,0]) lid(); }
