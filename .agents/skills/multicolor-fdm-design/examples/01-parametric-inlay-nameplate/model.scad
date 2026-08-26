// Four-color parametric nameplate. Export with -D 'part="base"' etc.
part = "all";
label_text = "METRIMADE";
plate_w = 88;
plate_h = 34;
plate_t = 3.0;
corner_r = 4;
inlay_depth = 0.6;
border_w = 1.8;
eps = 0.04;

module rounded_rect_2d(w, h, r) {
    offset(r=r) square([w-2*r, h-2*r], center=true);
}

module plate_2d() { rounded_rect_2d(plate_w, plate_h, corner_r); }

module border_2d() {
    difference() {
        rounded_rect_2d(plate_w-2.2, plate_h-2.2, corner_r-0.8);
        rounded_rect_2d(plate_w-2.2-2*border_w, plate_h-2.2-2*border_w, max(corner_r-0.8-border_w, 0.8));
    }
}

module text_2d() {
    translate([-8, 0]) text(label_text, size=7.4, halign="center", valign="center", font="DejaVu Sans:style=Bold", spacing=1.02);
}

module star_2d(r1=6.0, r2=2.8, n=5) {
    polygon(points=[for (i=[0:2*n-1]) let(r=(i%2==0?r1:r2), a=90+i*180/n) [r*cos(a), r*sin(a)]]);
}
module icon_2d() { translate([31,0]) star_2d(); }

module accent_volume(profile="border", cutter=false) {
    z0 = plate_t - inlay_depth - (cutter ? eps : 0);
    hh = inlay_depth + (cutter ? 2*eps : 0);
    translate([0,0,z0]) linear_extrude(height=hh) {
        if (profile=="border") border_2d();
        if (profile=="text") text_2d();
        if (profile=="icon") icon_2d();
    }
}

module base() {
    difference() {
        linear_extrude(height=plate_t) plate_2d();
        accent_volume("border", true);
        accent_volume("text", true);
        accent_volume("icon", true);
    }
}
module border() { accent_volume("border", false); }
module lettering() { accent_volume("text", false); }
module icon() { accent_volume("icon", false); }

if (part=="base") base();
else if (part=="border") border();
else if (part=="lettering") lettering();
else if (part=="icon") icon();
else {
    color("#25282B") base();
    color("#27B9D3") border();
    color("#F2F0E8") lettering();
    color("#F26A21") icon();
}
