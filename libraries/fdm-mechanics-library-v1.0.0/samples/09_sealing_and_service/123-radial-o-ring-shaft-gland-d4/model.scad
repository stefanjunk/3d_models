/*
Sample 123: Radiale O-Ring-Wellendichtung — Welle 4 mm
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
    shaft_d=4,
    oring_id=4,
    oring_cs=1.5,
    radial_squeeze=0.15,
    clearance=0.22,
    land_l=11,
    lead_in=1.2,
    grease_reservoir=1.4,
    wall=3
);
