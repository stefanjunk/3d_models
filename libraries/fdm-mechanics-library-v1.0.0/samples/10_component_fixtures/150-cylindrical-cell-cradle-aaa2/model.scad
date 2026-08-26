/*
Sample 150: Zylindrischer Zellhalter — 2 x AAA
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

sample_cell_cradle(
    view=view,
    cell_d=10.5,
    cell_l=44.5,
    count=2,
    cell_gap=2,
    clearance=0.35,
    strap_w=6,
    contact_keepout=5
);
