/*
Sample 155: Abgedichtete Magnetbetätiger-Tasche — Wand 3 mm
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

sample_magnetic_actuator(
    view=view,
    wall_t=3,
    magnet_d=6,
    magnet_l=3,
    switch_keepout=[18, 6, 6],
    travel=22,
    retention=1.4,
    clearance=0.4
);
