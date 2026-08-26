/*
Sample 129: Kompakte asymmetrische Wellenkupplung — 2 auf 3 mm
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
    input_d=2,
    output_d=3,
    input_clearance=0.15,
    output_clearance=0.15,
    length=16,
    outer_d=11,
    fastener=2.4,
    axial_stop=0.8
);
