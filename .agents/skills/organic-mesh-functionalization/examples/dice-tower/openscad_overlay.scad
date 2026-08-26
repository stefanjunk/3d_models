// Proof-of-concept only: use on a clean manifold source mesh.
source = "decorated-tower.stl";
eps = 0.10;
inner_radius = 28;
inner_height = 110;
portal_w = 25;
portal_h = 24;

module removal_cutters() {
    union() {
        translate([0,0,-inner_height/2-eps]) cylinder(r=inner_radius, h=inner_height+2*eps, $fn=128);
        translate([-portal_w/2, inner_radius-5, -inner_height/2]) cube([portal_w, 30, portal_h]);
        translate([-portal_w/2, -portal_w/2, inner_height/2-10]) cube([portal_w, portal_w, 30]);
    }
}

module stairs() {
    for (i=[0:6]) {
        translate([-22.5, 13-i*1.8, -42+i*12]) cube([45,15,3]);
    }
}

union() {
    difference() {
        import(source, convexity=10);
        removal_cutters();
    }
    stairs();
}
