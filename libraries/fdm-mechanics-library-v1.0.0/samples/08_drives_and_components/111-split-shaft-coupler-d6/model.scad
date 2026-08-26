/*
Sample 111: Geteilte Wellen-Klemmkupplung — 6-mm-Welle
Generated from the FDM Mechanical Sample Library.
Units: millimetres.

Override examples:
  openscad -o custom.stl -D 'view="plate"' -D 'render_fn=64' model.scad
  openscad -o preview.png -D 'view="assembly"' model.scad
*/
use <../../../library/fdm_mechanisms.scad>

render_fn = is_undef(render_fn) ? 48 : render_fn;
view = is_undef(view) ? "plate" : view;
$fn = render_fn;

sample_shaft_coupler(
    view=view,
    bore_d=6,
    clearance=0.2,
    screw_d=3.4,
    nut_flat=5.7
);
