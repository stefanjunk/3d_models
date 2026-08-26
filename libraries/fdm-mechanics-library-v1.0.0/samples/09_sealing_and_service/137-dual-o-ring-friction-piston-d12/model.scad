/*
Sample 137: Doppel-O-Ring-Reibkolben — Bohrung 12 mm
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

sample_friction_piston(
    view=view,
    bore_d=12,
    travel=20,
    oring_id=9.5,
    oring_cs=1.5,
    groove_depth=1.08,
    groove_spacing=4.4,
    lead_in=1,
    anti_loss_stop=4,
    clearance=0.2
);
