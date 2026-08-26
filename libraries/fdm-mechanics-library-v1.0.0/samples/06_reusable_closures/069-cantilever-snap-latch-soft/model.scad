/*
Sample 069: Wiederlösbarer Kragarm-Schnapper — weich 0,8 mm
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

sample_cantilever_snap(
    view=view,
    beam_t=0.8,
    clearance=0.25,
    hook=1.6
);
