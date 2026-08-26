// Four-color fox badge with semantic top inlays.
part = "all";
plate_t = 3.0;
inlay_depth = 0.72;
eps = 0.04;

module ellipse(rx, ry) { scale([rx, ry]) circle(r=1, $fn=64); }
module fox_silhouette_2d() {
    union() {
        hull() {
            translate([0,6]) ellipse(22,19);
            translate([0,-15]) ellipse(17,17);
        }
        polygon(points=[[-18,17],[-12,36],[-3,22]]);
        polygon(points=[[18,17],[12,36],[3,22]]);
        hull() { translate([16,-14]) circle(r=8,$fn=48); translate([34,-5]) circle(r=11,$fn=56); }
    }
}
module black_raw_2d() {
    translate([-7,9]) ellipse(2.1,3.0);
    translate([7,9]) ellipse(2.1,3.0);
    translate([0,0]) polygon(points=[[-2.6,1.5],[2.6,1.5],[0,-2.5]]);
}
module white_raw_2d() {
    union() {
        translate([-6,1]) ellipse(8.5,6.5);
        translate([6,1]) ellipse(8.5,6.5);
        translate([0,-13]) ellipse(8.5,11);
        translate([34,-5]) ellipse(7.2,8.5);
    }
}
module blue_raw_2d() {
    union() {
        translate([0,-4]) offset(r=1.3) square([26,4.2],center=true);
        translate([8,-10]) rotate(-18) polygon(points=[[0,0],[10,-7],[6,4]]);
    }
}
module white_2d() { intersection() { fox_silhouette_2d(); difference(){ white_raw_2d(); black_raw_2d(); blue_raw_2d(); } } }
module black_2d() { intersection() { fox_silhouette_2d(); black_raw_2d(); } }
module blue_2d() { intersection() { fox_silhouette_2d(); difference(){ blue_raw_2d(); black_raw_2d(); } } }
module all_accents_2d() { union() { white_2d(); black_2d(); blue_2d(); } }

module color_volume(which="white", cutter=false) {
    z0=plate_t-inlay_depth-(cutter?eps:0);
    hh=inlay_depth+(cutter?2*eps:0);
    translate([0,0,z0]) linear_extrude(height=hh) {
        if(which=="white") white_2d();
        if(which=="black") black_2d();
        if(which=="blue") blue_2d();
    }
}
module base() {
    difference() {
        linear_extrude(height=plate_t) fox_silhouette_2d();
        translate([0,0,plate_t-inlay_depth-eps]) linear_extrude(height=inlay_depth+2*eps) all_accents_2d();
    }
}
module white_part(){color_volume("white",false);}
module black_part(){color_volume("black",false);}
module blue_part(){color_volume("blue",false);}

if(part=="base") base();
else if(part=="white") white_part();
else if(part=="black") black_part();
else if(part=="blue") blue_part();
else {
    color("#F26A21") base();
    color("#F2F0E8") white_part();
    color("#181818") black_part();
    color("#2979C7") blue_part();
}
