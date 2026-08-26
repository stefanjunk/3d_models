/*
Sample 057: Schraubdom mit seitlicher Muttertasche — M2,5
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

sample_nuttrap_screw(
    view=view,
    screw_d=2.9,
    nut_flat=5,
    nut_h=2.1,
    head_d=5.2
);
