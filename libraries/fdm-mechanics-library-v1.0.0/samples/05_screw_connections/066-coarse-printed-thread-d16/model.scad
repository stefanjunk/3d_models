/*
Sample 066: Grobgewinde aus dem Drucker — Ø 16 / P 3
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
    d=16,
    pitch=3,
    clearance=0.3,
    length=16
);
