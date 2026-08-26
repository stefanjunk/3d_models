// Original Anycubic Kobra 3 Max fan-cage mechanics with owner-supplied Metrimade SVG.
// Visible/camera face is z=0; +Y is down in the installed camera view; +Z points rearward.
// The Python voxel generator is authoritative for the supplied production STL/3MF files.

part = "assembly"; // assembly | body_navy | brand_teal | brand_aqua | brand_sand | singlecolor | fit_test
target_bezel_diameter = 52; // supplied candidates: 50, 52 and 54 mm

face_thickness = 2.4;
inlay_depth = 0.6;
outer_diameter = 62;
ring_inner_diameter = 50.8;
spoke_width = 1.6;
clip_outer_radius = 28.4;
clip_half_angle = 12;

mark_center_svg = [101.95, 106.58];
mark_scale = 0.15372002; // 30 mm source-mark height
wordmark_center_svg = [407.5, 108.2257];
wordmark_scale = 0.13913043; // 48 mm outlined-wordmark width
label_center_y = -29.7;
label_size = [54, 8.8];

$fa = 3;
$fs = 0.25;

module line_2d(a, b, width) {
    hull() {
        translate(a) circle(d=width);
        translate(b) circle(d=width);
    }
}

module rounded_box_2d(size, radius) {
    hull()
        for (x=[-size[0]/2+radius, size[0]/2-radius])
            for (y=[-size[1]/2+radius, size[1]/2-radius])
                translate([x,y]) circle(r=radius);
}

module mark_solid_2d(name) {
    scale([mark_scale, mark_scale])
        translate([-mark_center_svg[0], -mark_center_svg[1]])
            import(str("../assets/metrimade-mark-", name, ".svg"));
}

module mark_lamellae_2d() {
    intersection() {
        square([40,40], center=true);
        union()
            for (offset=[-48:3.2:48])
                translate([offset,0]) rotate(-45) square([0.8,70], center=true);
    }
}

module mark_perforated_2d(name) {
    intersection() {
        mark_solid_2d(name);
        union() {
            difference() {
                mark_solid_2d(name);
                offset(delta=-0.8) mark_solid_2d(name);
            }
            mark_lamellae_2d();
        }
    }
}

module wordmark_2d() {
    translate([0,label_center_y])
        scale([wordmark_scale, wordmark_scale])
            translate([-wordmark_center_svg[0], -wordmark_center_svg[1]])
                import("../assets/metrimade-wordmark-navy.svg");
}

module label_plate_2d() {
    translate([0,label_center_y]) rounded_box_2d(label_size, 2);
}

module brand_full_2d() {
    union() {
        mark_perforated_2d("navy");
        mark_perforated_2d("teal");
        mark_perforated_2d("aqua");
        mark_perforated_2d("sand");
        label_plate_2d();
    }
}

module support_links_2d() {
    line_2d([-12,0],[-25.8,0],spoke_width);
    line_2d([12,0],[25.8,0],spoke_width);
    line_2d([0,-15],[0,-25.8],spoke_width);
    line_2d([0,15],[0,25.8],spoke_width);
}

module front_2d() {
    union() {
        difference() {
            circle(d=outer_diameter);
            circle(d=ring_inner_diameter);
        }
        support_links_2d();
        brand_full_2d();
    }
}

module brand_teal_2d() { mark_perforated_2d("teal"); }
module brand_aqua_2d() { mark_perforated_2d("aqua"); }
module brand_sand_2d() {
    union() {
        mark_perforated_2d("sand");
        difference() {
            label_plate_2d();
            wordmark_2d();
        }
    }
}

module non_navy_brand_2d() {
    union() {
        brand_teal_2d();
        brand_aqua_2d();
        brand_sand_2d();
    }
}

module annular_tab(center_angle, z0, height, inner_r0, inner_r1) {
    rotate([0,0,center_angle-clip_half_angle])
        rotate_extrude(angle=2*clip_half_angle, convexity=8)
            polygon([
                [inner_r0,z0],
                [clip_outer_radius,z0],
                [clip_outer_radius,z0+height],
                [inner_r1,z0+height]
            ]);
}

module clip_tabs(z_shift=0) {
    target_r = target_bezel_diameter/2;
    for (angle=[0,60,120,180,240,300]) {
        annular_tab(angle,z_shift+2.2,0.6,target_r-0.5,target_r-0.5);
        annular_tab(angle,z_shift+2.8,2.55,target_r+0.25,target_r+0.25);
        annular_tab(angle,z_shift+5.35,0.5,target_r-0.15,target_r-0.15);
        annular_tab(angle,z_shift+5.85,0.75,target_r-0.15,target_r+0.60);
    }
}

module body_navy() {
    difference() {
        union() {
            linear_extrude(height=face_thickness) front_2d();
            clip_tabs();
        }
        translate([0,0,-0.01])
            linear_extrude(height=inlay_depth+0.02)
                non_navy_brand_2d();
    }
}

module brand_teal() { linear_extrude(height=inlay_depth) brand_teal_2d(); }
module brand_aqua() { linear_extrude(height=inlay_depth) brand_aqua_2d(); }
module brand_sand() { linear_extrude(height=inlay_depth) brand_sand_2d(); }

module singlecolor() {
    union() {
        linear_extrude(height=face_thickness) front_2d();
        clip_tabs();
    }
}

module fit_test() {
    target_r = target_bezel_diameter/2;
    union() {
        linear_extrude(height=1.2)
            difference() {
                circle(r=28.6);
                circle(r=target_r-0.55);
            }
        clip_tabs(z_shift=-1.0);
    }
}

if (part == "body_navy") body_navy();
else if (part == "brand_teal") brand_teal();
else if (part == "brand_aqua") brand_aqua();
else if (part == "brand_sand") brand_sand();
else if (part == "singlecolor") singlecolor();
else if (part == "fit_test") fit_test();
else {
    color("#112431") body_navy();
    color("#08777D") brand_teal();
    color("#7FD5D3") brand_aqua();
    color("#C7AB82") brand_sand();
}
