/* Multi-purpose FDM calibration coupons for the design skill. */

coupon = "all"; // [all,fit,walls,engraving,bridges]
nominal_hole = 6.0;
fit_offsets = [-0.20,-0.10,0,0.10,0.20,0.30,0.40];
wall_widths = [0.45,0.68,0.90,1.35,1.80];
engraving_depths = [0.2,0.3,0.4,0.6,0.8,1.0];
bridge_spans = [10,20,30,40,50];
$fn = 48;

module label(txt, size=3, depth=0.35) {
    linear_extrude(height=depth)
        text(txt, size=size, halign="center", valign="center", font="Liberation Sans");
}

module fit_coupon() {
    difference() {
        cube([86,28,5]);
        for (i=[0:len(fit_offsets)-1]) {
            x = 8 + i*11.5;
            translate([x,14,-0.5]) cylinder(h=6,d=nominal_hole+fit_offsets[i]);
            translate([x,4.5,4.72]) label(str(fit_offsets[i]),2.2,0.4);
        }
    }
}

module wall_coupon() {
    union() {
        cube([78,22,2]);
        for (i=[0:len(wall_widths)-1]) {
            x=8+i*15;
            translate([x,3,2]) cube([wall_widths[i],16,20]);
            translate([x+wall_widths[i]/2,11,1.72]) label(str(wall_widths[i]),2.2,0.4);
        }
    }
}

module engraving_coupon() {
    difference() {
        cube([86,36,4]);
        for (i=[0:len(engraving_depths)-1]) {
            x=8+i*13;
            translate([x,9,4-engraving_depths[i]]) cube([7,18,engraving_depths[i]+0.2]);
            translate([x+3.5,30,3.72]) label(str(engraving_depths[i]),2.4,0.45);
        }
    }
}

module bridge_coupon() {
    // Rows share a thin base so the exported coupon is one connected body.
    base_w = max(bridge_spans) + 20;
    row_pitch = 15;
    union() {
        cube([base_w, len(bridge_spans)*row_pitch, 2]);
        for (i=[0:len(bridge_spans)-1]) {
            span=bridge_spans[i];
            y=i*row_pitch+2.5;
            translate([5,y,2]) cube([5,10,16]);
            translate([10+span,y,2]) cube([5,10,16]);
            translate([10,y,16.8]) cube([span,10,1.2]);
            translate([base_w-6,y+5,2]) label(str(span),2.4,0.5);
        }
    }
}

if (coupon == "fit") fit_coupon();
else if (coupon == "walls") wall_coupon();
else if (coupon == "engraving") engraving_coupon();
else if (coupon == "bridges") bridge_coupon();
else {
    translate([0,0,0]) fit_coupon();
    translate([0,40,0]) wall_coupon();
    translate([0,78,0]) engraving_coupon();
    translate([0,125,0]) bridge_coupon();
}
