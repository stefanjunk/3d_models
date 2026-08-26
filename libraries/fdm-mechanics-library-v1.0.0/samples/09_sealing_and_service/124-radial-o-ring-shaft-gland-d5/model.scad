/*
Sample 124: Radiale O-Ring-Wellendichtung — Welle 5 mm
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
    shaft_d=5,
    oring_id=5,
    oring_cs=2,
    radial_squeeze=0.13,
    clearance=0.25,
    land_l=12,
    lead_in=1.4,
    grease_reservoir=1.6,
    wall=3.2
);
