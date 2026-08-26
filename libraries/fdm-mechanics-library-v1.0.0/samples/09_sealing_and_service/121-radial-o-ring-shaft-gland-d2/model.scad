/*
Sample 121: Radiale O-Ring-Wellendichtung — Welle 2 mm
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

sample_radial_shaft_gland(
    view=view,
    shaft_d=2,
    oring_id=2,
    oring_cs=1.5,
    radial_squeeze=0.12,
    clearance=0.18,
    land_l=10,
    lead_in=1,
    grease_reservoir=1.2,
    wall=3
);
