/*
Sample 133: Kurbel-Langloch-Schwinge — Kurbelradius 3 mm
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

sample_crank_rocker(
    view=view,
    crank_r=3,
    pivot_offset=16,
    slot_w=5.2,
    pin_d=4,
    rocker_r=22,
    plate_t=3
);
