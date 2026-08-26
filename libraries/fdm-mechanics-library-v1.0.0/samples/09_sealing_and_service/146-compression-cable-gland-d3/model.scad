/*
Sample 146: Kompressions-Kabeldurchführung — Kabel 3 mm
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

sample_cable_gland(
    view=view,
    cable_d=3,
    seal_clearance=0.3,
    compression_l=4.5,
    thread_d=16,
    pitch=3,
    strain_relief=12,
    wall=3
);
