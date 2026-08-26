/*
Sample 062: Heizeinsatz-Schraubprobe — M2,5
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

sample_heatset_insert(
    view=view,
    pilot_d=3.8,
    screw_clear=2.9,
    head_d=5.2,
    insert_depth=5
);
