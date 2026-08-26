/*
Sample 148: Kompressions-Kabeldurchführung — Kabel 6 mm
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
    cable_d=6,
    seal_clearance=0.4,
    compression_l=6,
    thread_d=20,
    pitch=4,
    strain_relief=16,
    wall=3.2
);
