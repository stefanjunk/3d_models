/*
Sample 144: Captiver servicefähiger Gelenkstift — Stift 5 mm
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

sample_captive_hinge_pin(
    view=view,
    pin_d=5,
    bearing_clearance=0.3,
    head_d=8,
    retainer_clearance=0.3,
    grip_l=14,
    leaf_l=30
);
