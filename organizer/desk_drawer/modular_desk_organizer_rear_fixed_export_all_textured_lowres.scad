// Modular Desk Organizer - parametric OpenSCAD source
// Inspired by the generated concept image: soft rounded forms, subtle ribs,
// drawer tower, cubby, open trays and vertical slide-dovetail connections.
// Units: mm

$fn = 48;
// Select exactly one part for STL export.
// Available parts:
//   PART = "drawer_housing";  // Schubladen-Gehäuse
//   PART = "drawer_1";        // Schublade 1
//   PART = "drawer_2";        // Schublade 2 (identische Geometrie)
//   PART = "drawer_pair";     // beide Schubladen nebeneinander
//   PART = "cubby";           // offenes Ablagefach
//   PART = "shallow_tray";    // flache Ablageschale / Top-Tray
//   PART = "divided_bin";     // unterteiltes Bin / Organizerfach
//   PART = "pen_cup";         // hoher Stiftehalter
//   PART = "connector_test";  // Steckverbinder-Testteil
//   PART = "layout";          // komplette Vorschau
//
// Intuitive aliases also work:
//   "housing", "drawer", "ablage", "tray", "bin", "pen_holder"
PART = "layout";
FIT = 0.35;               // connector clearance per side; try 0.25..0.45 depending on printer/material
TEXTURE = false;          // avoid overlapping ribs when image engraving is enabled

// Optional image-based engraving texture.
// IMPORTANT: OpenSCAD's surface() can use a lot of RAM at high image sizes.
// Therefore this script uses a LOW-RES image workflow.
//
// 1) Keep your original image as SOURCE.
// 2) Create a reduced file with the helper script `prepare_texture_image.py`.
// 3) The generated low-res image is then loaded by OpenSCAD.
//
// Default target resolution is chosen as the highest usually meaningful
// size for FDM engraving on typical 0.4 mm nozzles.
IMAGE_TEXTURE_ENABLE = false;
IMAGE_TEXTURE_SOURCE_FILE = "carbon_fiber_heightmap_source.png";   // original image
IMAGE_TEXTURE_TARGET_RES = 256;  // default: highest usually sensible low-res value
IMAGE_TEXTURE_FILE = str("carbon_fiber_heightmap_", IMAGE_TEXTURE_TARGET_RES, ".png");
IMAGE_TEXTURE_INVERT = true;
IMAGE_TEXTURE_DEPTH = 0.6;       // engraving depth in mm
IMAGE_TEXTURE_TOP_CLEAR = 4;     // keep this much free at the top
IMAGE_TEXTURE_BOTTOM_CLEAR = 4;  // keep this much free at the bottom
IMAGE_TEXTURE_FRONT_MARGIN = 2;  // free border on front panels (left/right)
IMAGE_TEXTURE_SIDE_MARGIN = 3;   // free border on side panels (front/back)

module rr2d(w,d,r) {
    translate([r,r]) offset(r=r) square([w-2*r,d-2*r], center=false);
}

module rounded_prism(w,d,h,r) {
    linear_extrude(height=h) rr2d(w,d,r);
}

module cup(w,d,h,wall=3,bottom=3,r=12) {
    difference() {
        rounded_prism(w,d,h,r);
        translate([wall,wall,bottom])
            rounded_prism(w-2*wall,d-2*wall,h-bottom+0.2,max(1,r-wall));
    }
}

// A rounded cup rotated so its opening points toward the front (negative Y / Y=0 side).
module front_cup(w,d,h,wall=3.2,back=3.2,r=12) {
    translate([0,d,0]) rotate([90,0,0]) cup(w,h,d,wall,back,r);
}

module u_shell_2d(w,d,r,wall=3.2,back=3.2) {
    // Rounded outer footprint with a fully open, straight front.
    // The cavity follows the rear corner radius instead of cutting a
    // rectangular notch through the rounded back corners.
    inner_w = w - 2*wall;
    inner_d = d - back;
    inner_r = max(1, r - wall);

    difference() {
        rr2d(w,d,r);
        union() {
            // Main inner cavity with matching rear radii.
            translate([wall,0]) rr2d(inner_w,inner_d,inner_r);
            // Square off only the FRONT corners so the drawers still slide
            // straight in from y=0. Rear corners remain rounded/closed.
            translate([wall,-0.2])
                square([inner_w,inner_r+0.2], center=false);
        }
    }
}

module u_shell_layer(w,d,h,r,wall=3.2,back=3.2) {
    linear_extrude(height=h) u_shell_2d(w,d,r,wall,back);
}

module connector_pair(w,d,h,fit=FIT,rail_h=56,rail_z=12,p=4,base=8,head=12,rail_t=2.2) {
    overlap = 0.25;
    y0 = d/2;
    zh = min(rail_h,h-rail_z-5);

    // Male vertical dovetail on RIGHT: narrow at body, wider at head.
    translate([0,0,rail_z]) linear_extrude(height=zh)
        polygon(points=[
            [w-overlap,y0-base/2],
            [w+p-overlap,y0-head/2],
            [w+p-overlap,y0+head/2],
            [w-overlap,y0+base/2]
        ]);

    // Female receiver on LEFT is external, so no hidden support-heavy groove is required.
    mouth = base + 2*fit;
    inner = head + 2*fit;
    translate([0,0,rail_z]) linear_extrude(height=zh)
        polygon(points=[
            [-p-0.15,y0+mouth/2],
            [overlap,y0+inner/2],
            [overlap,y0+inner/2+rail_t],
            [-p-0.15,y0+mouth/2+rail_t]
        ]);
    translate([0,0,rail_z]) linear_extrude(height=zh)
        polygon(points=[
            [-p-0.15,y0-mouth/2-rail_t],
            [overlap,y0-inner/2-rail_t],
            [overlap,y0-inner/2],
            [-p-0.15,y0-mouth/2]
        ]);
}

module rib_ring(w,d,r,z,amp=0.38,rib_h=0.75) {
    translate([0,0,z]) difference() {
        translate([-amp,-amp,0])
            linear_extrude(height=rib_h) rr2d(w+2*amp,d+2*amp,r+amp);
        translate([0,0,-0.1])
            linear_extrude(height=rib_h+0.2) rr2d(w,d,r);
    }
}

module mount_key(w=12,d=8,h=1.2,r=1.8) {
    rounded_prism(w,d,h,r);
}


module image_texture_heightmap(panel_w, panel_h, depth) {
    // Loads the PRE-DOWNSAMPLED image file specified by IMAGE_TEXTURE_FILE.
    resize([panel_w, panel_h, depth], auto=[false,false,false])
        surface(file=IMAGE_TEXTURE_FILE,
                center=false,
                invert=IMAGE_TEXTURE_INVERT,
                convexity=8);
}

module engrave_front_panel(x0, y_plane, z0, panel_w, panel_h, depth) {
    translate([x0, y_plane, z0 + panel_h])
        rotate([-90,0,0])
            image_texture_heightmap(panel_w, panel_h, depth);
}

module engrave_left_side(x_plane, y0, z0, panel_w, panel_h, depth) {
    translate([x_plane, y0, z0])
        rotate([0,0,90])
            rotate([90,0,0])
                image_texture_heightmap(panel_w, panel_h, depth);
}

module engrave_right_side(x_plane, y0, z0, panel_w, panel_h, depth) {
    translate([x_plane, y0, z0])
        mirror([1,0,0])
            rotate([0,0,90])
                rotate([90,0,0])
                    image_texture_heightmap(panel_w, panel_h, depth);
}

module apply_image_engraving(x0, y0, z0, w, d, h, front=true, sides=true, front_plane_y=0) {
    panel_h = h - IMAGE_TEXTURE_TOP_CLEAR - IMAGE_TEXTURE_BOTTOM_CLEAR;
    front_w = w - 2*IMAGE_TEXTURE_FRONT_MARGIN;
    side_w = d - 2*IMAGE_TEXTURE_SIDE_MARGIN;

    if (!IMAGE_TEXTURE_ENABLE || panel_h <= 0)
        children();
    else
        difference() {
            children();

            if (front && front_w > 0)
                engrave_front_panel(
                    x0 + IMAGE_TEXTURE_FRONT_MARGIN,
                    front_plane_y,
                    z0 + IMAGE_TEXTURE_BOTTOM_CLEAR,
                    front_w,
                    panel_h,
                    IMAGE_TEXTURE_DEPTH
                );

            if (sides && side_w > 0) {
                engrave_left_side(
                    x0,
                    y0 + IMAGE_TEXTURE_SIDE_MARGIN,
                    z0 + IMAGE_TEXTURE_BOTTOM_CLEAR,
                    side_w,
                    panel_h,
                    IMAGE_TEXTURE_DEPTH
                );
                engrave_right_side(
                    x0 + w,
                    y0 + IMAGE_TEXTURE_SIDE_MARGIN,
                    z0 + IMAGE_TEXTURE_BOTTOM_CLEAR,
                    side_w,
                    panel_h,
                    IMAGE_TEXTURE_DEPTH
                );
            }
        }
}

module drawer_housing() {
    // Built from z-layers so the cavity geometry matches the exported STL.
    // No front engraving here because the front is interrupted by the drawer
    // openings. Side engraving remains available.
    w=96; d=96; h=80; wall=3.2; back=3.2; r=15; shelf=3.2;
    open_h = 34.8;
    lower_z = 4.2;
    upper_z = lower_z + open_h + shelf;
    key_w = 12; key_d = 8; key_h = 1.2; key_r = 1.8;
    key_x1 = 18; key_x2 = w-18-key_w; key_y = (d-key_d)/2;
    apply_image_engraving(0,0,0,w,d,h,front=false,sides=true) {
        union() {
            translate([0,0,0]) rounded_prism(w,d,lower_z,r);
            translate([0,0,lower_z]) u_shell_layer(w,d,open_h,r,wall,back);
            translate([0,0,lower_z+open_h]) rounded_prism(w,d,shelf,r);
            translate([0,0,upper_z]) u_shell_layer(w,d,open_h,r,wall,back);
            translate([0,0,upper_z+open_h]) rounded_prism(w,d,h-(upper_z+open_h),r);
            // shallow runners for the drawers
            for (z=[lower_z+1.2, upper_z+1.2]) {
                translate([wall-0.3,7,z]) cube([1.4,d-back-10,1.5]);
                translate([w-wall-1.1,7,z]) cube([1.4,d-back-10,1.5]);
            }
            // subtle top docking keys for the shallow tray
            translate([key_x1,key_y,h]) mount_key(key_w,key_d,key_h,key_r);
            translate([key_x2,key_y,h]) mount_key(key_w,key_d,key_h,key_r);
            connector_pair(w,d,h);
        }
    }
}

module drawer() {
    // Image engraving can be applied to the front face and both outer sides.
    body_w=88.6; body_d=91; body_h=32.2; body_r=10.0;
    face_w=89.1; face_h=34.6; face_t=2.4; face_r=11.2;
    x0 = -(face_w-body_w)/2;
    y0 = -face_t;
    total_d = body_d + face_t;
    apply_image_engraving(x0,y0,0,face_w,total_d,face_h,front=true,sides=true,front_plane_y=y0) {
        union() {
            cup(body_w,body_d,body_h,2.4,2.4,body_r);
            // front bezel with radii visually matched to the housing opening
            translate([x0,-face_t,0])
                rounded_prism(face_w,face_t,face_h,face_r);
            // low-profile rounded pull centered on the bezel
            translate([(body_w-30)/2,-4.2,9.7]) rounded_prism(30,5.5,6.2,2.4);
        }
    }
}

module cubby() {
    w=96; d=96; h=80;
    // Front remains unengraved because it is largely open.
    apply_image_engraving(0,0,0,w,d,h,front=false,sides=true) {
        union() {
            front_cup(w,d,h,3.2,3.2,13);
            connector_pair(w,d,h);
        }
    }
}

module shallow_tray() {
    // Optional top-docking tray for the drawer housing.
    // Matching sockets on the underside fit over the housing's low-profile keys.
    w=96; d=96; h=26; r=14;
    key_w = 12; key_d = 8; key_h = 1.2; key_r = 1.8; fit = 0.25;
    key_x1 = 18; key_x2 = w-18-key_w; key_y = (d-key_d)/2;
    apply_image_engraving(0,0,0,w,d,h,front=true,sides=true) {
        difference() {
            union() {
                cup(w,d,h,3,3,r);
                translate([46.5,3.2,3]) cube([2.4,d-6.4,15.5]);
                connector_pair(w,d,h,rail_h=14,rail_z=6);
            }
            // hidden underside sockets for top mounting on the drawer housing
            translate([key_x1-fit,key_y-fit,0])
                mount_key(key_w+2*fit,key_d+2*fit,key_h+0.35,key_r+fit);
            translate([key_x2-fit,key_y-fit,0])
                mount_key(key_w+2*fit,key_d+2*fit,key_h+0.35,key_r+fit);
        }
    }
}

module divided_bin() {
    w=96; d=96; h=78; r=15;
    apply_image_engraving(0,0,0,w,d,h,front=true,sides=true) {
        union() {
            cup(w,d,h,3,3,r);
            translate([46.7,3,3]) cube([2.6,d-6,57]);
            translate([3,47,3]) cube([43.7,2.6,57]);
            translate([49.3,58,3]) cube([43.7,2.6,57]);
            connector_pair(w,d,h);
            if (TEXTURE) for (z=[10:5.5:60]) rib_ring(w,d,r,z);
        }
    }
}

module pen_cup() {
    w=64; d=96; h=110; r=17;
    apply_image_engraving(0,0,0,w,d,h,front=true,sides=true) {
        union() {
            cup(w,d,h,3,3,r);
            translate([3,50,3]) cube([w-6,2.6,87]);
            connector_pair(w,d,h,rail_h=56,rail_z=12);
            if (TEXTURE) for (z=[10:5.5:79]) rib_ring(w,d,r,z);
        }
    }
}

module connector_test() {
    // Print two copies and slide them together vertically.
    w=24; d=34; h=30;
    union() {
        cube([w,d,h]);
        connector_pair(w,d,h,rail_h=20,rail_z=5);
    }
}

module layout() {
    gap = 4.35;  // natural spacing produced by the external sliding connector
    // back row
    translate([0,0,0]) drawer_housing();
    translate([96+gap,0,0]) divided_bin();
    translate([2*(96+gap),0,0]) cubby();
    translate([3*(96+gap),0,0]) pen_cup();

    // drawers shown partially inserted for a useful preview
    translate([(96-88.6)/2,-5,4.2]) drawer();
    translate([(96-88.6)/2,-10,43.1]) drawer();

    // extra shallow tray nearby
    translate([96+gap,-115,0]) shallow_tray();
}

// ---------------------------------------------------------------------------
// Export selector
// ---------------------------------------------------------------------------
// For individual STL files set PART above, press F6, then:
// File -> Export -> Export as STL
//
// The two drawers are intentionally identical. "drawer_1" and "drawer_2"
// therefore export the same geometry, allowing you to save them under two
// separate filenames if desired.

if (PART == "drawer_housing" || PART == "housing") drawer_housing();
else if (PART == "drawer" || PART == "drawer_1") drawer();
else if (PART == "drawer_2") drawer();
else if (PART == "drawer_pair") {
    drawer();
    translate([98,0,0]) drawer();
}
else if (PART == "cubby" || PART == "ablage") cubby();
else if (PART == "shallow_tray" || PART == "tray") shallow_tray();
else if (PART == "divided_bin" || PART == "bin") divided_bin();
else if (PART == "pen_cup" || PART == "pen_holder") pen_cup();
else if (PART == "connector_test") connector_test();
else layout();
