/*
Sample 151: Zylindrischer Zellhalter — 1 x AA
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
    cell_d=14.5,
    cell_l=50.5,
    count=1,
    cell_gap=2,
    clearance=0.4,
    strap_w=8,
    contact_keepout=6
);
