/*
Sample 132: Kompakte asymmetrische Wellenkupplung — 3 auf 5 mm
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

sample_micro_shaft_coupler(
    view=view,
    input_d=3,
    output_d=5,
    input_clearance=0.18,
    output_clearance=0.2,
    length=20,
    outer_d=14,
    fastener=2.4,
    axial_stop=1
);
