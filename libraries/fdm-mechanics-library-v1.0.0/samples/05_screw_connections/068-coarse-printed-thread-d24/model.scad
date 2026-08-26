/*
Sample 068: Grobgewinde aus dem Drucker — Ø 24 / P 5
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

sample_printed_thread(
    view=view,
    d=24,
    pitch=5,
    clearance=0.45,
    length=20
);
