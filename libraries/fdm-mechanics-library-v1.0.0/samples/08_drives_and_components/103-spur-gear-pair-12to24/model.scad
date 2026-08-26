/*
Sample 103: Stirnradpaar auf Stiftbasis — 1:2
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

sample_spur_gears(
    view=view,
    teeth_a=12,
    teeth_b=24,
    module_size=1.5,
    clearance=0.25
);
