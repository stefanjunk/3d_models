/*
Sample 128: O-Ring-vorgespanntes Rampenbajonett — 25 % radiale Kompression
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

sample_ramped_bayonet(
    view=view,
    core_d=24,
    running_clearance=0.35,
    lug_w=6,
    ramp_h=0.85,
    turn_deg=42,
    oring_id=21,
    oring_cs=2,
    radial_squeeze=0.25,
    hard_stop=1.5
);
