// Generic clean-mesh CSG template. The source mesh must already be manifold.
source_file = "source-clean.stl";
eps = 0.20;
cut_center = [0, 0, 50];
cut_radius = 25;
cut_height = 100;
$fn = 128;

module source_mesh() {
    import(source_file, convexity=30);
}

module functional_cutter() {
    translate([cut_center.x, cut_center.y, cut_center.z - cut_height/2 - eps])
        cylinder(r=cut_radius, h=cut_height + 2*eps);
}

difference() {
    source_mesh();
    functional_cutter();
}
