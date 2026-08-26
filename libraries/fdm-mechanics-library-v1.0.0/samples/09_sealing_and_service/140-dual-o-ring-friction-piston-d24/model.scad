/*
Sample 140: Doppel-O-Ring-Reibkolben — Bohrung 24 mm
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
    bore_d=24,
    travel=26,
    oring_id=20.5,
    oring_cs=2,
    groove_depth=1.44,
    groove_spacing=5.2,
    lead_in=1.4,
    anti_loss_stop=5,
    clearance=0.25
);
