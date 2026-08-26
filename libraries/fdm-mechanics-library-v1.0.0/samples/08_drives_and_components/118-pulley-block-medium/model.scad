/*
Sample 118: Umlenkrollen-Block — 28 mm / Seil 3 mm
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

sample_pulley_block(
    view=view,
    rope_d=3,
    outer_d=28,
    pin_d=4,
    clearance=0.25
);
