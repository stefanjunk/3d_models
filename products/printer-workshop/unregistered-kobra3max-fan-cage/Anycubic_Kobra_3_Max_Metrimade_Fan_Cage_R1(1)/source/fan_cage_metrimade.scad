// Original Anycubic Kobra 3 Max wraparound honeycomb cover with owner-supplied Metrimade SVG.
// Visible/camera face is z=0; +Y is down in the installed camera view; +Z points rearward.
// The Python voxel generator is authoritative for the supplied production STL/3MF files.

part = "assembly"; // assembly | body_navy | brand_teal | brand_aqua | brand_sand | singlecolor | fit_test
target_bezel_diameter = 52; // supplied candidates: 50, 52 and 54 mm

cover_thickness = 1.6;
badge_thickness = 2.4;
inlay_depth = 0.6;
fan_module_outer_diameter = 59.2;
ring_inner_diameter = 50.8;
spoke_width = 1.6;
clip_outer_radius = 28.4;
clip_half_angle = 12;
cover_frame = 2.0;
perimeter_shell_depth = 4.8;
side_clip_depth = 10.8;
shell_edge_nominal_width = 69.0;
honeycomb_radius = 4.2;
honeycomb_rib = 1.2;

mark_center_svg = [101.95, 106.58];
mark_scale = 0.15372002; // 30 mm source-mark height
wordmark_center_svg = [407.5, 108.2257];
wordmark_scale = 0.13913043; // 48 mm outlined-wordmark width
label_center_y = -38.2;
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

module outer_cover_2d() {
    polygon([
        [-30,-52], [30,-52], [36,-48], [36,29],
        [32,36], [-32,36], [-36,29], [-36,-48]
    ]);
}

module outer_frame_2d() {
    difference() {
        outer_cover_2d();
        offset(delta=-cover_frame) outer_cover_2d();
    }
}

module hex_edge_2d(center, radius=honeycomb_radius, width=honeycomb_rib) {
    for (index=[0:5])
        line_2d(
            center + [radius*cos(60*index), radius*sin(60*index)],
            center + [radius*cos(60*(index+1)), radius*sin(60*(index+1))],
            width
        );
}

module honeycomb_2d() {
    intersection() {
        outer_cover_2d();
        difference() {
            union()
                for (column=[-7:7])
                    for (row=[-8:8])
                        hex_edge_2d([
                            column*1.5*honeycomb_radius,
                            row*sqrt(3)*honeycomb_radius + (column%2)*sqrt(3)*honeycomb_radius/2
                        ]);
            circle(d=fan_module_outer_diameter-0.8);
        }
    }
}

module cover_carrier_2d() {
    union() {
        outer_frame_2d();
        honeycomb_2d();
        line_2d([-28.8,0],[-35.4,0],spoke_width);
        line_2d([28.8,0],[35.4,0],spoke_width);
        line_2d([0,-28.8],[0,-34],spoke_width);
        line_2d([0,28.8],[0,35.2],spoke_width);
    }
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

module fan_badge_2d() {
    union() {
        difference() {
            circle(d=fan_module_outer_diameter);
            circle(d=ring_inner_diameter);
        }
        support_links_2d();
        brand_full_2d();
    }
}

module front_2d() { union() { cover_carrier_2d(); fan_badge_2d(); } }

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

module top_stabilizer_2d() {
    intersection() {
        outer_cover_2d();
        translate([0,-51]) square([80,6], center=true);
    }
}

module perimeter_shell() {
    translate([0,0,1.4]) linear_extrude(height=perimeter_shell_depth-1.4) outer_frame_2d();
    translate([0,0,1.4]) linear_extrude(height=perimeter_shell_depth-1.4) top_stabilizer_2d();
}

module side_stabilizer_positive(y_start) {
    // Shallow side wall plus a small compliant rear bead and lead-in.
    translate([35.05,y_start,1.4]) cube([2.15,12,8.6]);
    translate([34.4,y_start,9.2]) cube([2.8,12,0.8]);
    hull() {
        translate([34.4,y_start,10.0]) cube([2.8,12,0.2]);
        translate([35.3,y_start,10.6]) cube([1.9,12,0.2]);
    }
}

module side_stabilizers() {
    for (y_start=[-41,15]) {
        side_stabilizer_positive(y_start);
        mirror([1,0,0]) side_stabilizer_positive(y_start);
    }
}

module body_navy() {
    difference() {
        union() {
            linear_extrude(height=cover_thickness) cover_carrier_2d();
            linear_extrude(height=badge_thickness) fan_badge_2d();
            perimeter_shell();
            side_stabilizers();
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
        linear_extrude(height=cover_thickness) cover_carrier_2d();
        linear_extrude(height=badge_thickness) fan_badge_2d();
        perimeter_shell();
        side_stabilizers();
        clip_tabs();
    }
}

module fit_test() {
    union() {
        linear_extrude(height=1.2) outer_frame_2d();
        linear_extrude(height=1.2)
            union() {
                difference() { circle(d=fan_module_outer_diameter); circle(d=ring_inner_diameter); }
                line_2d([-28.8,0],[-35.4,0],spoke_width);
                line_2d([28.8,0],[35.4,0],spoke_width);
                line_2d([0,-28.8],[0,-34],spoke_width);
                line_2d([0,28.8],[0,35.2],spoke_width);
            }
        perimeter_shell();
        side_stabilizers();
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
