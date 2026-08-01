/*
Parametrischer Barfußschuh V4 – Sohle und Textilschnittmuster
================================

Neue Funktionen:
- drei Schuhmodi: Textilschaft, Sandale, Sockenschuh
- umlaufender Klebe-/Nährand
- Zehenstoßschutz
- breite Flexkerbe unter dem Ballen
- Sandalenlaschen und optionale Zehenschlaufe
- Sockenschuh-Seitenwand
- separate perforierte TPU-Decklage
- textile Schnittschablone
- Luft- und Feuchtigkeitskanäle an der Fußseite

Koordinaten:
X = quer, bei linker Sohle +X medial/Großzehenseite
Y = Ferse -> Zehen
Z = Laufsohle -> Fuß

Das Modell ist ein technischer Prototyp und kein Medizinprodukt.
*/

/* [Ausgabe] */
output_part = "assembled";               // [assembled,sole_only,footbed_only,textile_template,pattern_all,pattern_vamp,pattern_medial_quarter,pattern_lateral_quarter,pattern_tongue,pattern_heel_band,pattern_collar,pattern_sock_medial,pattern_sock_lateral,pattern_sock_gusset,pattern_toe_reinforcement,pattern_heel_reinforcement,pattern_strobel_board,pattern_lasting_band,pattern_interface_overlay]
shoe_mode = "textile_upper";             // [textile_upper,sandal,sock_shoe]
foot_side = "left";                      // [left,right]
render_pair = false;                     // [false,true]
show_footbed_next_to_sole = false;
pair_gap = 20;
part_gap = 20;

/* [Fußgeometrie] */
foot_length = 260;
toe_clearance = 8;
ball_width = 101;
toe_box_width = 106;
heel_width = 67;
waist_width = 70;
edge_allowance = 3.0;
medial_toe_shift = 5.0;

/* [Sohlenkörper] */
sole_thickness = 4.9;
internal_structure = "solid";            // [solid,light_cells]
top_skin = 0.9;
bottom_skin = 1.0;
perimeter_wall = 3.2;
cell_shape = "hex";                      // [hex,round,diamond]
cell_pitch = 10.5;
cell_rib_width = 1.7;
cell_cavity_depth = 2.5;

/* [Laufsohle] */
outsole_style = "footprint_grip";        // [plain,dots,bars,chevrons,footprint,footprint_grip]
grip_height = 0.65;
grip_size = 1.7;
grip_spacing = 5.2;
grip_margin = 3.0;
footprint_recess_depth = 0.45;

/* [Normale Flexrillen] */
minor_flex_grooves = true;
minor_flex_width = 1.2;
minor_flex_depth = 0.55;
minor_flex_positions = [0.50, 0.57, 0.76, 0.83];

/* [Große Ballen-Flexkerbe] */
ball_flex_enabled = true;
ball_flex_position = 0.685;
ball_flex_width = 6.0;
ball_flex_depth = 1.45;
ball_flex_radius = 2.0;
ball_flex_edge_margin = 5.5;

/* [Textilschaft: Klebe-/Nährand] */
bond_sew_rim_enabled = true;
rim_width = 6.0;
rim_thickness = 1.3;
rim_outer_upstand = 2.5;
rim_upstand_thickness = 1.4;
stitch_holes_enabled = true;
stitch_hole_diameter = 1.8;
stitch_hole_spacing = 15;
stitch_hole_edge_offset = 2.5;
rim_exclude_toe = false;
rim_exclude_heel = false;

/* [Zehenstoßschutz] */
toe_bumper_enabled = true;
toe_bumper_start = 0.79;
toe_bumper_height = 11.0;
toe_bumper_thickness = 2.0;
toe_bumper_outset = 0.8;
toe_bumper_top_lip = 1.5;
toe_bumper_vent_slots = true;
toe_bumper_slot_width = 4.0;
toe_bumper_slot_spacing = 12.0;

/* [Sandale] */
sandal_side_tabs = true;
sandal_tab_y_positions = [0.30, 0.58, 0.73];
sandal_tab_width = 14;
sandal_tab_length = 10;
sandal_tab_thickness = 3.0;
sandal_slot_width = 4.0;
sandal_slot_length = 10.0;
sandal_heel_tabs = true;
sandal_toe_loop_hole = false;
sandal_toe_hole_diameter = 4.5;
sandal_toe_hole_x = 0.18;
sandal_toe_hole_y = 0.80;

/* [Sockenschuh] */
sock_wall_height = 7.0;
sock_wall_thickness = 1.5;
sock_wall_outset = 0.7;
sock_wall_vent_slots = true;
sock_wall_slot_width = 4.0;
sock_wall_slot_spacing = 15.0;
sock_wall_open_heel = false;

/* [Fußseitige Oberfläche] */
top_surface = "air_channels";            // [smooth,rough_grid,glue_channels,air_channels]
top_texture_depth = 0.35;
top_channel_width = 1.2;
top_channel_spacing = 9.0;
top_margin = 4.0;

/* [Separate weiche Decklage] */
footbed_enabled = true;
footbed_type = "perforated_tpu";         // [perforated_tpu,textile_template]
footbed_thickness = 1.25;
footbed_inset = 1.5;
footbed_hole_pattern = "hex";            // [round,hex,slots]
footbed_hole_diameter = 2.3;
footbed_hole_spacing = 5.6;
footbed_border = 4.0;
footbed_underside_nubs = false;
footbed_nub_height = 0.45;
footbed_nub_diameter = 1.8;

/* [Textilschablone] */
textile_template_allowance = 4.0;
textile_template_thickness = 0.5;
textile_template_mark_holes = true;


/* [Integriertes Textilschnittmuster] */
pattern_style = "textile_shoe";          // [textile_shoe,sock_shoe]
pattern_include_labels = true;
pattern_include_notches = true;
pattern_include_grainlines = true;
pattern_include_stitch_line = true;
pattern_sheet_spacing = 18;

/* [Zusätzliche Fußmaße für das Oberteil] */
instep_girth = 245;                      // Umfang über dem Spann
ball_girth = 250;                        // Umfang über dem Ballen
ankle_girth = 235;                       // Umfang am späteren Schuhkragen
heel_to_instep_length = 155;             // hinterste Ferse bis hoher Spannbereich

/* [Passform des Oberteils] */
pattern_fit_ease = 5;
pattern_stretch_reduction = 0.00;        // z. B. 0.06 für elastisches Mesh
pattern_toe_volume_gain = 1.05;
pattern_instep_height_gain = 1.00;
pattern_heel_hold_gain = 1.00;

/* [Nahtzugaben des Oberteils] */
pattern_seam_allowance = 7;
pattern_sole_attachment_allowance = 9;
pattern_collar_turn_allowance = 8;
pattern_tongue_seam_allowance = 7;
pattern_reinforcement_allowance = 3;

/* [Leichter Textilschuh] */
pattern_vamp_length_ratio = 0.48;
pattern_vamp_opening_width = 48;
pattern_quarter_height = 78;
pattern_quarter_front_overlap = 24;
pattern_heel_seam_overlap = 12;
pattern_eyelet_extension = 18;
pattern_tongue_length = 125;
pattern_tongue_base_width = 46;
pattern_tongue_top_width = 58;

/* [Sockenschuh-Schnitt] */
pattern_sock_upper_height = 92;
pattern_sock_gusset_enabled = true;
pattern_sock_gusset_width = 34;
pattern_sock_gusset_length = 105;

/* [Verstärkungsteile] */
pattern_toe_reinforcement_enabled = true;
pattern_heel_reinforcement_enabled = true;
pattern_toe_reinforcement_length = 78;
pattern_heel_reinforcement_height = 50;

/* [Exakte Schnittstelle zur Sohle] */
pattern_strobel_inset = 0.0;             // 0 = exakt dieselbe Außenkontur wie die Sohle
pattern_lasting_band_width = 12;         // exakter umlaufender Textilring
pattern_interface_outer_allowance = 0;   // 0 = Außenkante exakt Sohlenkante
pattern_interface_mark_holes = true;
pattern_interface_mark_flexline = true;

/* [Markierungen] */
pattern_notch_size = 3;
pattern_stitch_line_offset = 4;
pattern_grainline_length = 45;
pattern_label_size = 7;

/* [Darstellung] */
$fn = 48;


// -----------------------------------------------------------------------------
// Abgeleitete Maße und Prüfungen
// -----------------------------------------------------------------------------

sole_length = foot_length + toe_clearance;
max_foot_width = max(ball_width, toe_box_width) + 2 * edge_allowance;
pair_offset = max_foot_width + 2 * rim_width + pair_gap;

assert(sole_thickness > 2.2, "Sohle zu dünn.");
assert(ball_flex_depth < sole_thickness - 1.2,
       "Ballen-Flexkerbe lässt zu wenig Restmaterial.");
assert(internal_structure == "solid" ||
       cell_cavity_depth <= sole_thickness - top_skin - bottom_skin - 0.15,
       "Innenzellen kollidieren mit Ober- oder Unterhaut.");


// -----------------------------------------------------------------------------
// Funktionen für Kontur und Befestigungspositionen
// -----------------------------------------------------------------------------

function lerp(a, b, t) = a + (b - a) * t;
function clamp(v, lo, hi) = min(max(v, lo), hi);

function half_width_at(y) =
    y < 0.18 * sole_length
        ? lerp(0.48 * heel_width, 0.54 * heel_width,
               y / (0.18 * sole_length))
    : y < 0.43 * sole_length
        ? lerp(0.54 * heel_width, 0.50 * waist_width,
               (y - 0.18 * sole_length) / (0.25 * sole_length))
    : y < 0.69 * sole_length
        ? lerp(0.50 * waist_width, 0.50 * ball_width,
               (y - 0.43 * sole_length) / (0.26 * sole_length))
    : y < 0.84 * sole_length
        ? lerp(0.50 * ball_width, 0.50 * toe_box_width,
               (y - 0.69 * sole_length) / (0.15 * sole_length))
    : lerp(0.50 * toe_box_width, 0.36 * toe_box_width,
           clamp((y - 0.84 * sole_length) / (0.14 * sole_length), 0, 1));

function center_shift_at(y) =
    y < 0.43 * sole_length
        ? lerp(0, -0.045 * waist_width,
               y / (0.43 * sole_length))
    : y < 0.69 * sole_length
        ? lerp(-0.045 * waist_width, 0,
               (y - 0.43 * sole_length) / (0.26 * sole_length))
    : lerp(0, medial_toe_shift,
           clamp((y - 0.69 * sole_length) / (0.27 * sole_length), 0, 1));


// -----------------------------------------------------------------------------
// 2D-Grundkontur
// -----------------------------------------------------------------------------

module station_2d(y, w, d, x_shift = 0) {
    translate([x_shift, y])
        scale([w / 2, d / 2])
            circle(r = 1);
}

module raw_foot_outline_left_2d() {
    y0 = 0.060 * sole_length;
    y1 = 0.215 * sole_length;
    y2 = 0.425 * sole_length;
    y3 = 0.685 * sole_length;
    y4 = 0.825 * sole_length;
    y5 = 0.940 * sole_length;

    union() {
        hull() {
            station_2d(y0, heel_width, 0.120 * sole_length, 0);
            station_2d(y1, heel_width * 1.08, 0.180 * sole_length,
                       -0.01 * heel_width);
        }
        hull() {
            station_2d(y1, heel_width * 1.08, 0.180 * sole_length,
                       -0.01 * heel_width);
            station_2d(y2, waist_width, 0.175 * sole_length,
                       -0.045 * waist_width);
        }
        hull() {
            station_2d(y2, waist_width, 0.175 * sole_length,
                       -0.045 * waist_width);
            station_2d(y3, ball_width, 0.160 * sole_length, 0);
        }
        hull() {
            station_2d(y3, ball_width, 0.160 * sole_length, 0);
            station_2d(y4, toe_box_width, 0.155 * sole_length,
                       medial_toe_shift * 0.40);
        }
        hull() {
            station_2d(y4, toe_box_width, 0.155 * sole_length,
                       medial_toe_shift * 0.40);
            station_2d(y5, toe_box_width * 0.72, 0.120 * sole_length,
                       medial_toe_shift);
        }
    }
}

module sole_outline_left_2d() {
    offset(delta = edge_allowance)
        raw_foot_outline_left_2d();
}

module inner_outline_left_2d(margin = perimeter_wall) {
    offset(delta = -margin)
        sole_outline_left_2d();
}

module rounded_rect_2d(w, h, r) {
    offset(r = r)
        square([max(0.1, w - 2*r), max(0.1, h - 2*r)], center = true);
}


// -----------------------------------------------------------------------------
// Innenzellen
// -----------------------------------------------------------------------------

module cell_shape_2d(r) {
    if (cell_shape == "hex")
        rotate(30) circle(r = r, $fn = 6);
    else if (cell_shape == "round")
        circle(r = r);
    else
        rotate(45) square([1.45*r, 1.45*r], center = true);
}

module light_cell_cutters_left() {
    pitch_y = cell_pitch * 0.8660254;
    rows = ceil(sole_length / pitch_y) + 3;
    cols = ceil(max_foot_width / cell_pitch) + 4;
    r = max(0.8, (cell_pitch - cell_rib_width) / 2);

    intersection() {
        translate([0, 0, bottom_skin])
            linear_extrude(height = cell_cavity_depth)
                inner_outline_left_2d();

        union() {
            for (row = [-2 : rows]) {
                y = row * pitch_y;
                shift = ((row + 1000) % 2) * cell_pitch / 2;
                for (col = [-cols : cols]) {
                    x = col * cell_pitch + shift;
                    translate([x, y, bottom_skin - 0.01])
                        linear_extrude(height = cell_cavity_depth + 0.02)
                            cell_shape_2d(r);
                }
            }
        }
    }
}


// -----------------------------------------------------------------------------
// Laufsohlenprofile
// -----------------------------------------------------------------------------

module dot_pattern_left_2d() {
    intersection() {
        offset(delta = -grip_margin) sole_outline_left_2d();

        union() {
            for (y = [0 : grip_spacing : sole_length])
                for (x = [-max_foot_width : grip_spacing : max_foot_width])
                    translate([
                        x + ((floor(y / grip_spacing) % 2) * grip_spacing / 2),
                        y
                    ])
                        circle(d = grip_size);
        }
    }
}

module bar_pattern_left_2d() {
    intersection() {
        offset(delta = -grip_margin) sole_outline_left_2d();
        union() {
            for (y = [0 : grip_spacing * 1.35 : sole_length])
                translate([0, y])
                    square([2.2 * max_foot_width, grip_size], center = true);
        }
    }
}

module chevron_pattern_left_2d() {
    intersection() {
        offset(delta = -grip_margin) sole_outline_left_2d();
        union() {
            for (y = [0 : grip_spacing * 1.45 : sole_length])
                for (x = [-max_foot_width : grip_spacing * 1.9 : max_foot_width])
                    translate([x, y])
                        polygon(points = [
                            [-grip_size, 0],
                            [0, grip_size],
                            [grip_size, 0],
                            [0.38 * grip_size, 0],
                            [0, 0.38 * grip_size],
                            [-0.38 * grip_size, 0]
                        ]);
        }
    }
}

module footprint_pattern_left_2d() {
    union() {
        translate([0, 0.12 * sole_length])
            scale([0.42 * heel_width, 0.10 * sole_length]) circle(r = 1);

        translate([-0.05 * waist_width, 0.40 * sole_length])
            rotate(-8)
                scale([0.20 * waist_width, 0.16 * sole_length]) circle(r = 1);

        translate([0, 0.69 * sole_length])
            scale([0.50 * ball_width, 0.09 * sole_length]) circle(r = 1);

        translate([0.26 * toe_box_width, 0.89 * sole_length])
            scale([0.13 * toe_box_width, 0.06 * sole_length]) circle(r = 1);

        for (i = [0 : 3])
            translate([
                (0.08 - 0.12 * i) * toe_box_width,
                (0.895 - 0.003 * i) * sole_length
            ])
                scale([
                    (0.10 - 0.01 * i) * toe_box_width,
                    (0.045 - 0.003 * i) * sole_length
                ])
                    circle(r = 1);
    }
}

module outsole_positive_left() {
    if (outsole_style == "dots" ||
        outsole_style == "footprint_grip")
        linear_extrude(height = grip_height)
            dot_pattern_left_2d();

    else if (outsole_style == "bars")
        linear_extrude(height = grip_height)
            bar_pattern_left_2d();

    else if (outsole_style == "chevrons")
        linear_extrude(height = grip_height)
            chevron_pattern_left_2d();
}

module footprint_recess_left() {
    if (outsole_style == "footprint" ||
        outsole_style == "footprint_grip")
        translate([0, 0, -0.01])
            linear_extrude(height = footprint_recess_depth + 0.02)
                intersection() {
                    offset(delta = -grip_margin) sole_outline_left_2d();
                    footprint_pattern_left_2d();
                }
}


// -----------------------------------------------------------------------------
// Flexkerben
// -----------------------------------------------------------------------------

module minor_flex_cutters_left() {
    if (minor_flex_grooves)
        for (p = minor_flex_positions)
            intersection() {
                translate([0, p * sole_length, -0.01])
                    linear_extrude(height = minor_flex_depth + grip_height + 0.02)
                        rounded_rect_2d(
                            2.2 * max_foot_width,
                            minor_flex_width,
                            min(0.5, minor_flex_width / 2)
                        );

                linear_extrude(height = sole_thickness)
                    offset(delta = -5)
                        sole_outline_left_2d();
            }
}

module ball_flex_cutter_left() {
    if (ball_flex_enabled)
        intersection() {
            translate([0, ball_flex_position * sole_length, -0.01])
                linear_extrude(height = ball_flex_depth + grip_height + 0.02)
                    rounded_rect_2d(
                        2.2 * max_foot_width,
                        ball_flex_width,
                        min(ball_flex_radius, ball_flex_width / 2 - 0.05)
                    );

            linear_extrude(height = sole_thickness)
                offset(delta = -ball_flex_edge_margin)
                    sole_outline_left_2d();
        }
}


// -----------------------------------------------------------------------------
// Fußseitige Kanäle und Oberflächentexturen
// -----------------------------------------------------------------------------

module top_channel_area_left_2d() {
    offset(delta = -top_margin)
        sole_outline_left_2d();
}

module top_surface_cutters_left() {
    if (top_surface == "rough_grid" ||
        top_surface == "glue_channels" ||
        top_surface == "air_channels")
        intersection() {
            translate([0, 0, sole_thickness - top_texture_depth])
                linear_extrude(height = top_texture_depth + 0.03)
                    top_channel_area_left_2d();

            union() {
                for (y = [0 : top_channel_spacing : sole_length])
                    translate([0, y, sole_thickness - top_texture_depth / 2])
                        cube([
                            2.2 * max_foot_width,
                            top_channel_width,
                            top_texture_depth + 0.05
                        ], center = true);

                if (top_surface == "rough_grid")
                    for (x = [-max_foot_width : top_channel_spacing : max_foot_width])
                        translate([
                            x, 0.5 * sole_length,
                            sole_thickness - top_texture_depth / 2
                        ])
                            cube([
                                top_channel_width,
                                1.2 * sole_length,
                                top_texture_depth + 0.05
                            ], center = true);

                if (top_surface == "air_channels")
                    translate([
                        0, 0.5 * sole_length,
                        sole_thickness - top_texture_depth / 2
                    ])
                        cube([
                            top_channel_width * 1.4,
                            1.1 * sole_length,
                            top_texture_depth + 0.05
                        ], center = true);
            }
        }
}


// -----------------------------------------------------------------------------
// Umlaufender Klebe-/Nährand
// -----------------------------------------------------------------------------

module rim_ring_left_2d() {
    difference() {
        offset(delta = rim_width)
            sole_outline_left_2d();
        sole_outline_left_2d();
    }
}

module rim_mask_left_2d() {
    difference() {
        translate([0, 0.50 * sole_length])
            square([
                3 * (max_foot_width + rim_width),
                1.25 * sole_length
            ], center = true);

        if (rim_exclude_toe)
            translate([0, 0.92 * sole_length])
                square([
                    3 * max_foot_width,
                    0.24 * sole_length
                ], center = true);

        if (rim_exclude_heel)
            translate([0, 0.06 * sole_length])
                square([
                    3 * max_foot_width,
                    0.18 * sole_length
                ], center = true);
    }
}

module stitch_hole_positions_left() {
    y_start = 0.09 * sole_length;
    y_end = 0.90 * sole_length;
    count = floor((y_end - y_start) / stitch_hole_spacing);

    // Seiten
    for (i = [0 : count]) {
        y = y_start + i * stitch_hole_spacing;
        hw = half_width_at(y) + edge_allowance
             + rim_width - stitch_hole_edge_offset;
        cs = center_shift_at(y);

        translate([cs + hw, y])
            children();
        translate([cs - hw, y])
            children();
    }

    // Fersenbogen
    for (a = [-55 : 22 : 235]) {
        x = 0.50 * (heel_width + 2*edge_allowance + 2*rim_width
                   - 2*stitch_hole_edge_offset) * cos(a);
        y = 0.085 * sole_length
            + 0.065 * sole_length * sin(a);
        translate([x, y])
            children();
    }

    // Zehenbogen
    for (a = [15 : 22 : 165]) {
        x = medial_toe_shift
            + 0.47 * (toe_box_width + 2*edge_allowance + 2*rim_width
                      - 2*stitch_hole_edge_offset) * cos(a);
        y = 0.87 * sole_length
            + 0.10 * sole_length * sin(a);
        translate([x, y])
            children();
    }
}

module bond_sew_rim_left() {
    if (bond_sew_rim_enabled &&
        (shoe_mode == "textile_upper" || shoe_mode == "sock_shoe"))
        difference() {
            union() {
                translate([0, 0, sole_thickness - rim_thickness])
                    linear_extrude(height = rim_thickness)
                        intersection() {
                            rim_ring_left_2d();
                            rim_mask_left_2d();
                        }

                if (rim_outer_upstand > 0)
                    translate([0, 0, sole_thickness])
                        linear_extrude(height = rim_outer_upstand)
                            intersection() {
                                difference() {
                                    offset(delta = rim_width)
                                        sole_outline_left_2d();
                                    offset(delta = rim_width -
                                                   rim_upstand_thickness)
                                        sole_outline_left_2d();
                                }
                                rim_mask_left_2d();
                            }
            }

            if (stitch_holes_enabled)
                stitch_hole_positions_left()
                    translate([0, 0, sole_thickness - rim_thickness - 0.2])
                        cylinder(
                            h = rim_thickness + rim_outer_upstand + 0.5,
                            d = stitch_hole_diameter
                        );
        }
}


// -----------------------------------------------------------------------------
// Zehenstoßschutz
// -----------------------------------------------------------------------------

module toe_region_mask_2d() {
    translate([0, (toe_bumper_start + 1) * sole_length / 2])
        square([
            3 * max_foot_width,
            (1 - toe_bumper_start) * sole_length
        ], center = true);
}

module toe_bumper_wall_left() {
    if (toe_bumper_enabled)
        difference() {
            union() {
                translate([0, 0, sole_thickness])
                    linear_extrude(height = toe_bumper_height)
                        intersection() {
                            difference() {
                                offset(delta = toe_bumper_outset +
                                               toe_bumper_thickness)
                                    sole_outline_left_2d();
                                offset(delta = toe_bumper_outset)
                                    sole_outline_left_2d();
                            }
                            toe_region_mask_2d();
                        }

                if (toe_bumper_top_lip > 0)
                    translate([
                        0, 0,
                        sole_thickness + toe_bumper_height -
                        toe_bumper_top_lip
                    ])
                        linear_extrude(height = toe_bumper_top_lip)
                            intersection() {
                                difference() {
                                    offset(delta = toe_bumper_outset +
                                                   toe_bumper_thickness + 1.0)
                                        sole_outline_left_2d();
                                    offset(delta = toe_bumper_outset - 0.3)
                                        sole_outline_left_2d();
                                }
                                toe_region_mask_2d();
                            }
            }

            if (toe_bumper_vent_slots)
                for (x = [-0.42 * toe_box_width :
                           toe_bumper_slot_spacing :
                           0.48 * toe_box_width])
                    translate([
                        x,
                        0.92 * sole_length,
                        sole_thickness + toe_bumper_height * 0.55
                    ])
                        cube([
                            toe_bumper_slot_width,
                            0.30 * sole_length,
                            toe_bumper_height * 0.55
                        ], center = true);
        }
}


// -----------------------------------------------------------------------------
// Sandalenlaschen
// -----------------------------------------------------------------------------

module capsule_slot_2d(w, h) {
    hull() {
        translate([0, -h/2 + w/2]) circle(d = w);
        translate([0,  h/2 - w/2]) circle(d = w);
    }
}

module sandal_tab_at_left(y, side = 1) {
    cs = center_shift_at(y);
    hw = half_width_at(y) + edge_allowance;
    x = cs + side * (hw + sandal_tab_length / 2 - 1);

    translate([x, y, sole_thickness - 0.3])
        linear_extrude(height = sandal_tab_thickness)
            difference() {
                rounded_rect_2d(
                    sandal_tab_length,
                    sandal_tab_width,
                    min(3, sandal_tab_width/2 - 0.1)
                );
                capsule_slot_2d(
                    sandal_slot_width,
                    sandal_slot_length
                );
            }
}

module sandal_tabs_left() {
    if (shoe_mode == "sandal" && sandal_side_tabs)
        union() {
            for (p = sandal_tab_y_positions) {
                sandal_tab_at_left(p * sole_length, 1);
                sandal_tab_at_left(p * sole_length, -1);
            }

            if (sandal_heel_tabs) {
                sandal_tab_at_left(0.13 * sole_length, 1);
                sandal_tab_at_left(0.13 * sole_length, -1);
            }
        }
}

module sandal_toe_hole_left() {
    if (shoe_mode == "sandal" && sandal_toe_loop_hole)
        translate([
            sandal_toe_hole_x * toe_box_width,
            sandal_toe_hole_y * sole_length,
            -0.1
        ])
            cylinder(
                h = sole_thickness + grip_height + 0.3,
                d = sandal_toe_hole_diameter
            );
}


// -----------------------------------------------------------------------------
// Sockenschuh-Seitenwand
// -----------------------------------------------------------------------------

module sock_wall_mask_left_2d() {
    if (sock_wall_open_heel)
        translate([0, 0.59 * sole_length])
            square([
                3 * max_foot_width,
                0.82 * sole_length
            ], center = true);
    else
        translate([0, 0.50 * sole_length])
            square([
                3 * max_foot_width,
                1.25 * sole_length
            ], center = true);
}

module sock_wall_left() {
    if (shoe_mode == "sock_shoe")
        difference() {
            translate([0, 0, sole_thickness])
                linear_extrude(height = sock_wall_height)
                    intersection() {
                        difference() {
                            offset(delta = sock_wall_outset +
                                           sock_wall_thickness)
                                sole_outline_left_2d();
                            offset(delta = sock_wall_outset)
                                sole_outline_left_2d();
                        }
                        sock_wall_mask_left_2d();
                    }

            if (sock_wall_vent_slots)
                for (y = [0.18 * sole_length :
                           sock_wall_slot_spacing :
                           0.82 * sole_length]) {
                    hw = half_width_at(y) + edge_allowance +
                         sock_wall_outset + sock_wall_thickness / 2;
                    cs = center_shift_at(y);

                    translate([
                        cs + hw, y,
                        sole_thickness + 0.58 * sock_wall_height
                    ])
                        rotate([0, 90, 0])
                            cylinder(
                                h = 3 * sock_wall_thickness,
                                d = sock_wall_slot_width,
                                center = true
                            );

                    translate([
                        cs - hw, y,
                        sole_thickness + 0.58 * sock_wall_height
                    ])
                        rotate([0, 90, 0])
                            cylinder(
                                h = 3 * sock_wall_thickness,
                                d = sock_wall_slot_width,
                                center = true
                            );
                }
        }
}


// -----------------------------------------------------------------------------
// Separate Decklage / textile Schnittschablone
// -----------------------------------------------------------------------------

module footbed_outline_left_2d(extra = 0) {
    offset(delta = -footbed_inset + extra)
        sole_outline_left_2d();
}

module footbed_holes_left_2d() {
    pitch_y = footbed_hole_pattern == "hex"
        ? footbed_hole_spacing * 0.8660254
        : footbed_hole_spacing;

    rows = ceil(sole_length / pitch_y) + 3;
    cols = ceil(max_foot_width / footbed_hole_spacing) + 4;

    intersection() {
        offset(delta = -footbed_border)
            footbed_outline_left_2d();

        union() {
            for (row = [-2 : rows]) {
                y = row * pitch_y;
                shift = footbed_hole_pattern == "hex"
                    ? ((row + 1000) % 2) * footbed_hole_spacing / 2
                    : 0;

                for (col = [-cols : cols]) {
                    x = col * footbed_hole_spacing + shift;

                    translate([x, y])
                        if (footbed_hole_pattern == "slots")
                            capsule_slot_2d(
                                footbed_hole_diameter,
                                footbed_hole_diameter * 2.1
                            );
                        else if (footbed_hole_pattern == "hex")
                            rotate(30)
                                circle(
                                    d = footbed_hole_diameter,
                                    $fn = 6
                                );
                        else
                            circle(d = footbed_hole_diameter);
                }
            }
        }
    }
}

module footbed_nubs_left() {
    if (footbed_underside_nubs)
        intersection() {
            translate([0, 0, -footbed_nub_height])
                linear_extrude(height = footbed_nub_height)
                    offset(delta = -footbed_border)
                        footbed_outline_left_2d();

            union() {
                for (y = [footbed_hole_spacing :
                           footbed_hole_spacing * 2 :
                           sole_length])
                    for (x = [-max_foot_width :
                              footbed_hole_spacing * 2 :
                              max_foot_width])
                        translate([x, y, -footbed_nub_height])
                            cylinder(
                                h = footbed_nub_height,
                                d = footbed_nub_diameter
                            );
            }
        }
}

module perforated_footbed_left() {
    difference() {
        union() {
            linear_extrude(height = footbed_thickness)
                footbed_outline_left_2d();
            footbed_nubs_left();
        }

        translate([0, 0, -footbed_nub_height - 0.1])
            linear_extrude(
                height = footbed_thickness +
                         footbed_nub_height + 0.2
            )
                footbed_holes_left_2d();
    }
}

module textile_template_left() {
    difference() {
        linear_extrude(height = textile_template_thickness)
            offset(delta = textile_template_allowance)
                sole_outline_left_2d();

        if (textile_template_mark_holes)
            stitch_hole_positions_left()
                translate([0, 0, -0.1])
                    cylinder(
                        h = textile_template_thickness + 0.2,
                        d = stitch_hole_diameter + 0.8
                    );
    }
}


// -----------------------------------------------------------------------------
// Hauptsohle
// -----------------------------------------------------------------------------

module sole_core_left() {
    difference() {
        union() {
            linear_extrude(height = sole_thickness)
                sole_outline_left_2d();

            outsole_positive_left();
            bond_sew_rim_left();
            toe_bumper_wall_left();
            sandal_tabs_left();
            sock_wall_left();
        }

        if (internal_structure == "light_cells")
            light_cell_cutters_left();

        footprint_recess_left();
        minor_flex_cutters_left();
        ball_flex_cutter_left();
        top_surface_cutters_left();
        sandal_toe_hole_left();
    }
}


// =============================================================================
// INTEGRIERTES TEXTILSCHNITTMUSTER
// =============================================================================
//
// Exakt zur Sohle passende Elemente:
// - pattern_strobel_board_left()
// - pattern_lasting_band_left()
// - pattern_interface_overlay_left()
//
// Sie verwenden unmittelbar sole_outline_left_2d() und
// stitch_hole_positions_left(). Dadurch ändern sich Kontur und Lochbild
// automatisch gemeinsam mit der TPU-Sohle.
//
// Die dreidimensionale Fußform kann aus Umfangsmaßen nur angenähert werden.
// Vamp, Seitenteile und Sockenteile sind deshalb Startschnittmuster;
// die Sohlenanschlussfläche selbst ist hingegen geometrisch identisch.
// -----------------------------------------------------------------------------


// -----------------------------------------------------------------------------
// Abgeleitete Schnittmustermaße
// -----------------------------------------------------------------------------

pattern_effective_scale = 1 - pattern_stretch_reduction;
pattern_upper_length = sole_length + pattern_fit_ease;
pattern_effective_ball_girth =
    ball_girth * pattern_effective_scale;
pattern_effective_instep_girth =
    instep_girth * pattern_effective_scale;
pattern_effective_ankle_girth =
    ankle_girth * pattern_effective_scale;

pattern_half_ball_wrap = pattern_effective_ball_girth / 2;
pattern_half_instep_wrap = pattern_effective_instep_girth / 2;
pattern_half_ankle_wrap = pattern_effective_ankle_girth / 2;

assert(pattern_stretch_reduction >= 0 &&
       pattern_stretch_reduction < 0.25,
       "pattern_stretch_reduction sollte zwischen 0 und 0.24 liegen.");


// -----------------------------------------------------------------------------
// Allgemeine Schnittmuster-Helfer
// -----------------------------------------------------------------------------

module pat_rounded_polygon(points, radius = 2) {
    offset(r = radius)
        offset(delta = -radius)
            polygon(points = points);
}

module pat_cut_piece(allowance = pattern_seam_allowance) {
    offset(delta = allowance)
        children();
}

module pat_stitch_line(offset_value = pattern_stitch_line_offset) {
    if (pattern_include_stitch_line)
        difference() {
            offset(delta = offset_value + 0.35)
                children();
            offset(delta = offset_value - 0.35)
                children();
        }
}

module pat_notch(x, y, angle = 0) {
    if (pattern_include_notches)
        translate([x, y])
            rotate(angle)
                polygon(points = [
                    [0, 0],
                    [-pattern_notch_size, -pattern_notch_size],
                    [pattern_notch_size, -pattern_notch_size]
                ]);
}

module pat_grainline(x, y, angle = 90) {
    if (pattern_include_grainlines)
        translate([x, y])
            rotate(angle)
                union() {
                    square([pattern_grainline_length, 0.7],
                           center = true);

                    translate([pattern_grainline_length / 2, 0])
                        polygon(points = [
                            [0, 0], [-4, 2], [-4, -2]
                        ]);

                    translate([-pattern_grainline_length / 2, 0])
                        rotate(180)
                            polygon(points = [
                                [0, 0], [-4, 2], [-4, -2]
                            ]);
                }
}

module pat_label(txt, x, y, rot = 0) {
    if (pattern_include_labels)
        translate([x, y])
            rotate(rot)
                text(
                    txt,
                    size = pattern_label_size,
                    halign = "center",
                    valign = "center"
                );
}

module pat_hole_marks_2d(d = stitch_hole_diameter + 0.8) {
    stitch_hole_positions_left()
        circle(d = d);
}

module pat_ball_flex_mark_2d() {
    if (pattern_interface_mark_flexline)
        translate([0, ball_flex_position * sole_length])
            square([
                1.9 * max_foot_width,
                0.7
            ], center = true);
}


// -----------------------------------------------------------------------------
// EXAKTE SCHNITTSTELLE: Vollflächige Strobelsohle
// -----------------------------------------------------------------------------

module pattern_strobel_board_left() {
    difference() {
        offset(delta = -pattern_strobel_inset)
            sole_outline_left_2d();

        if (pattern_interface_mark_holes)
            pat_hole_marks_2d();
    }

    pat_ball_flex_mark_2d();

    pat_label(
        "STROBELSOHLE – EXAKTE SOHLENKONTUR",
        0,
        0.48 * sole_length,
        90
    );

    pat_grainline(0, 0.48 * sole_length, 90);

    pat_notch(
        center_shift_at(0.69 * sole_length),
        0.69 * sole_length,
        0
    );
}


// -----------------------------------------------------------------------------
// EXAKTE SCHNITTSTELLE: umlaufender Anschluss-/Zwickring
// -----------------------------------------------------------------------------

module pattern_lasting_band_left() {
    difference() {
        difference() {
            offset(delta = pattern_interface_outer_allowance)
                sole_outline_left_2d();

            offset(delta = -pattern_lasting_band_width)
                sole_outline_left_2d();
        }

        if (pattern_interface_mark_holes)
            pat_hole_marks_2d();
    }

    pat_ball_flex_mark_2d();

    pat_label(
        "ANSCHLUSSRING – EXAKT ZUR SOHLE",
        0,
        0.50 * sole_length,
        90
    );

    // Gemeinsame Passmarken an Ferse, Ballen und Zehe.
    pat_notch(
        center_shift_at(0.08 * sole_length),
        0.08 * sole_length,
        180
    );
    pat_notch(
        center_shift_at(0.69 * sole_length),
        0.69 * sole_length,
        0
    );
    pat_notch(
        center_shift_at(0.95 * sole_length),
        0.95 * sole_length,
        0
    );
}


// -----------------------------------------------------------------------------
// Überlagerung zur Kontrolle: Sohle + Rand + Löcher
// -----------------------------------------------------------------------------

module pattern_interface_overlay_left() {
    // Außenkontur
    difference() {
        offset(delta = 0.35)
            sole_outline_left_2d();
        offset(delta = -0.35)
            sole_outline_left_2d();
    }

    // Innenkante des Klebe-/Nährands
    difference() {
        offset(delta = -rim_width + 0.35)
            sole_outline_left_2d();
        offset(delta = -rim_width - 0.35)
            sole_outline_left_2d();
    }

    pat_hole_marks_2d(stitch_hole_diameter + 1.2);
    pat_ball_flex_mark_2d();

    pat_label(
        "KONTROLLÜBERLAGERUNG",
        0,
        0.49 * sole_length,
        90
    );
}


// -----------------------------------------------------------------------------
// Leichter Textilschuh: Vorderblatt/Vamp
// -----------------------------------------------------------------------------

module pat_vamp_base() {
    L = pattern_upper_length * pattern_vamp_length_ratio;
    W_toe = toe_box_width * pattern_toe_volume_gain;
    W_ball = pattern_half_ball_wrap * 0.88;
    neck_half = pattern_vamp_opening_width / 2;

    pat_rounded_polygon([
        [-W_toe / 2, 0],
        [ W_toe / 2, 0],
        [ W_ball / 2, 0.34 * L],
        [ neck_half + pattern_quarter_front_overlap, 0.73 * L],
        [ neck_half, L],
        [-neck_half, L],
        [-neck_half - pattern_quarter_front_overlap, 0.73 * L],
        [-W_ball / 2, 0.34 * L]
    ], 4);
}

module pattern_vamp_left() {
    pat_cut_piece(pattern_seam_allowance)
        pat_vamp_base();

    pat_stitch_line(pattern_stitch_line_offset)
        pat_vamp_base();

    pat_grainline(
        0,
        0.45 * pattern_upper_length *
        pattern_vamp_length_ratio,
        90
    );

    pat_label(
        "VAMP / VORDERBLATT",
        0,
        0.48 * pattern_upper_length *
        pattern_vamp_length_ratio,
        0
    );

    pat_notch(0, -pattern_seam_allowance, 180);
    pat_notch(
        -pattern_vamp_opening_width / 2,
        pattern_upper_length * pattern_vamp_length_ratio,
        0
    );
    pat_notch(
         pattern_vamp_opening_width / 2,
         pattern_upper_length * pattern_vamp_length_ratio,
         0
    );
}


// -----------------------------------------------------------------------------
// Mediales und laterales Seitenteil
// -----------------------------------------------------------------------------

module pat_quarter_base(medial = true) {
    L = heel_to_instep_length * 0.98;
    lower_front = pattern_quarter_front_overlap;
    top_front = pattern_eyelet_extension +
                (medial ? 4 : 0);
    ankle_half = pattern_half_ankle_wrap * 0.48;
    heel_h = pattern_quarter_height *
             pattern_heel_hold_gain;
    instep_h = pattern_quarter_height * 0.82 *
               pattern_instep_height_gain;

    pat_rounded_polygon([
        [0, 0],
        [L, 0],
        [L - lower_front, instep_h * 0.50],
        [L - top_front, instep_h],
        [ankle_half, heel_h],
        [0, heel_h * 0.78]
    ], 4);
}

module pattern_quarter_left(medial = true) {
    pat_cut_piece(pattern_seam_allowance)
        pat_quarter_base(medial);

    pat_stitch_line(pattern_stitch_line_offset)
        pat_quarter_base(medial);

    pat_grainline(
        0.48 * heel_to_instep_length,
        0.33 * pattern_quarter_height,
        0
    );

    pat_label(
        medial
            ? "MEDIALES SEITENTEIL"
            : "LATERALES SEITENTEIL",
        0.47 * heel_to_instep_length,
        0.50 * pattern_quarter_height,
        0
    );

    pat_notch(0, 0, 180);
    pat_notch(heel_to_instep_length * 0.50, 0, 180);
    pat_notch(
        heel_to_instep_length * 0.96,
        pattern_quarter_height * 0.52,
        90
    );
}


// -----------------------------------------------------------------------------
// Zunge
// -----------------------------------------------------------------------------

module pat_tongue_base() {
    pat_rounded_polygon([
        [-pattern_tongue_base_width / 2, 0],
        [ pattern_tongue_base_width / 2, 0],
        [ pattern_tongue_top_width / 2,
          0.82 * pattern_tongue_length],
        [ 0.38 * pattern_tongue_top_width,
          pattern_tongue_length],
        [-0.38 * pattern_tongue_top_width,
          pattern_tongue_length],
        [-pattern_tongue_top_width / 2,
          0.82 * pattern_tongue_length]
    ], 5);
}

module pattern_tongue_left() {
    pat_cut_piece(pattern_tongue_seam_allowance)
        pat_tongue_base();

    pat_stitch_line(pattern_stitch_line_offset)
        pat_tongue_base();

    pat_grainline(
        0,
        0.48 * pattern_tongue_length,
        90
    );

    pat_label(
        "ZUNGE",
        0,
        0.50 * pattern_tongue_length,
        0
    );

    pat_notch(
        0,
        -pattern_tongue_seam_allowance,
        180
    );
}


// -----------------------------------------------------------------------------
// Fersenband und Kragenband
// -----------------------------------------------------------------------------

module pat_heel_band_base() {
    band_len = heel_width +
               2 * pattern_heel_seam_overlap;
    band_h = pattern_heel_reinforcement_height * 0.85;

    pat_rounded_polygon([
        [0, 0],
        [band_len, 0],
        [band_len - 5, band_h],
        [5, band_h]
    ], 3);
}

module pattern_heel_band_left() {
    pat_cut_piece(pattern_seam_allowance)
        pat_heel_band_base();

    pat_stitch_line(pattern_stitch_line_offset)
        pat_heel_band_base();

    pat_label(
        "FERSENBAND",
        (heel_width +
         2 * pattern_heel_seam_overlap) / 2,
        pattern_heel_reinforcement_height * 0.40,
        0
    );

    pat_grainline(
        (heel_width +
         2 * pattern_heel_seam_overlap) / 2,
        pattern_heel_reinforcement_height * 0.20,
        0
    );
}

module pattern_collar_left() {
    binding_len = pattern_effective_ankle_girth +
                  2 * pattern_seam_allowance;
    binding_w = 2 * pattern_collar_turn_allowance;

    square([binding_len, binding_w]);

    if (pattern_include_stitch_line)
        translate([0, binding_w / 2 - 0.35])
            square([binding_len, 0.7]);

    pat_label(
        "KRAGENBAND",
        binding_len / 2,
        binding_w / 2,
        0
    );

    pat_grainline(
        binding_len / 2,
        binding_w / 2,
        0
    );
}


// -----------------------------------------------------------------------------
// Sockenschuh-Hauptteile
// -----------------------------------------------------------------------------

module pat_sock_side_base(medial = true) {
    L = pattern_upper_length * 0.92;
    toe_h = 0.25 * pattern_half_ball_wrap *
            pattern_toe_volume_gain;
    instep_h = 0.42 * pattern_half_instep_wrap *
               pattern_instep_height_gain;
    ankle_h = pattern_sock_upper_height;
    heel_h = pattern_sock_upper_height *
             pattern_heel_hold_gain;
    top_bias = medial ? 5 : 0;

    pat_rounded_polygon([
        [0, 0],
        [L, 0],
        [L, toe_h],
        [0.77 * L, 0.78 * instep_h],
        [0.56 * L, instep_h + top_bias],
        [0.26 * L, ankle_h],
        [0, heel_h]
    ], 5);
}

module pattern_sock_side_left(medial = true) {
    pat_cut_piece(pattern_seam_allowance)
        pat_sock_side_base(medial);

    pat_stitch_line(pattern_stitch_line_offset)
        pat_sock_side_base(medial);

    pat_grainline(
        0.46 * pattern_upper_length,
        0.33 * pattern_sock_upper_height,
        0
    );

    pat_label(
        medial ? "SOCKE MEDIAL" : "SOCKE LATERAL",
        0.47 * pattern_upper_length,
        0.52 * pattern_sock_upper_height,
        0
    );

    pat_notch(0, 0, 180);
    pat_notch(0.50 * pattern_upper_length, 0, 180);
    pat_notch(
        0.78 * pattern_upper_length,
        0.72 * pattern_sock_upper_height,
        90
    );
}

module pat_sock_gusset_base() {
    pat_rounded_polygon([
        [-pattern_sock_gusset_width / 2, 0],
        [ pattern_sock_gusset_width / 2, 0],
        [ 0.65 * pattern_sock_gusset_width / 2,
          pattern_sock_gusset_length],
        [-0.65 * pattern_sock_gusset_width / 2,
          pattern_sock_gusset_length]
    ], 5);
}

module pattern_sock_gusset_left() {
    pat_cut_piece(pattern_seam_allowance)
        pat_sock_gusset_base();

    pat_stitch_line(pattern_stitch_line_offset)
        pat_sock_gusset_base();

    pat_grainline(
        0,
        0.48 * pattern_sock_gusset_length,
        90
    );

    pat_label(
        "SPANNZWICKEL",
        0,
        0.50 * pattern_sock_gusset_length,
        0
    );

    pat_notch(
        0,
        -pattern_seam_allowance,
        180
    );
}


// -----------------------------------------------------------------------------
// Verstärkungen
// -----------------------------------------------------------------------------

module pat_toe_reinforcement_base() {
    W = toe_box_width * 0.92;
    L = pattern_toe_reinforcement_length;

    pat_rounded_polygon([
        [-W / 2, 0],
        [ W / 2, 0],
        [ 0.40 * W, 0.72 * L],
        [ 0.22 * W, L],
        [-0.22 * W, L],
        [-0.40 * W, 0.72 * L]
    ], 5);
}

module pattern_toe_reinforcement_left() {
    pat_cut_piece(pattern_reinforcement_allowance)
        pat_toe_reinforcement_base();

    pat_label(
        "ZEHENVERSTÄRKUNG",
        0,
        0.48 * pattern_toe_reinforcement_length,
        0
    );

    pat_grainline(
        0,
        0.45 * pattern_toe_reinforcement_length,
        90
    );
}

module pat_heel_reinforcement_base() {
    W = heel_width * 1.08;
    H = pattern_heel_reinforcement_height;

    pat_rounded_polygon([
        [-W / 2, 0],
        [ W / 2, 0],
        [ 0.44 * W, H],
        [-0.44 * W, H]
    ], 5);
}

module pattern_heel_reinforcement_left() {
    pat_cut_piece(pattern_reinforcement_allowance)
        pat_heel_reinforcement_base();

    pat_label(
        "FERSENVERSTÄRKUNG",
        0,
        0.48 * pattern_heel_reinforcement_height,
        0
    );

    pat_grainline(
        0,
        0.42 * pattern_heel_reinforcement_height,
        90
    );
}


// -----------------------------------------------------------------------------
// Gesamtlayouts
// -----------------------------------------------------------------------------

module pattern_textile_layout_left() {
    x1 = 0;
    x2 = toe_box_width +
         2 * pattern_seam_allowance +
         pattern_sheet_spacing;
    x3 = x2 +
         heel_to_instep_length +
         2 * pattern_seam_allowance +
         pattern_sheet_spacing;

    translate([x1, 0])
        pattern_vamp_left();

    translate([x2, 0])
        pattern_quarter_left(true);

    translate([x3, 0])
        pattern_quarter_left(false);

    row2_y =
        pattern_upper_length *
        pattern_vamp_length_ratio +
        2 * pattern_seam_allowance +
        pattern_sheet_spacing;

    translate([0, row2_y])
        pattern_tongue_left();

    translate([
        pattern_tongue_top_width +
        2 * pattern_tongue_seam_allowance +
        pattern_sheet_spacing,
        row2_y
    ])
        pattern_heel_band_left();

    row3_y =
        row2_y +
        pattern_tongue_length +
        2 * pattern_seam_allowance +
        pattern_sheet_spacing;

    translate([0, row3_y])
        pattern_collar_left();

    if (pattern_toe_reinforcement_enabled)
        translate([
            pattern_effective_ankle_girth +
            4 * pattern_seam_allowance +
            pattern_sheet_spacing,
            row3_y
        ])
            pattern_toe_reinforcement_left();

    if (pattern_heel_reinforcement_enabled)
        translate([
            pattern_effective_ankle_girth +
            toe_box_width +
            8 * pattern_seam_allowance +
            2 * pattern_sheet_spacing,
            row3_y
        ])
            pattern_heel_reinforcement_left();

    // Exakte Sohlenanschlussteile in einer weiteren Reihe.
    row4_y =
        row3_y +
        max([
            2 * pattern_collar_turn_allowance,
            pattern_toe_reinforcement_length,
            pattern_heel_reinforcement_height
        ]) +
        2 * pattern_seam_allowance +
        pattern_sheet_spacing;

    translate([0, row4_y])
        pattern_strobel_board_left();

    translate([
        max_foot_width +
        2 * pattern_sole_attachment_allowance +
        pattern_sheet_spacing,
        row4_y
    ])
        pattern_lasting_band_left();
}

module pattern_sock_layout_left() {
    x2 =
        pattern_upper_length +
        2 * pattern_seam_allowance +
        pattern_sheet_spacing;

    translate([0, 0])
        pattern_sock_side_left(true);

    translate([x2, 0])
        pattern_sock_side_left(false);

    row2_y =
        pattern_sock_upper_height +
        2 * pattern_seam_allowance +
        pattern_sheet_spacing;

    if (pattern_sock_gusset_enabled)
        translate([0, row2_y])
            pattern_sock_gusset_left();

    translate([
        pattern_sock_gusset_width +
        2 * pattern_seam_allowance +
        pattern_sheet_spacing,
        row2_y
    ])
        pattern_collar_left();

    if (pattern_toe_reinforcement_enabled)
        translate([
            pattern_sock_gusset_width +
            pattern_effective_ankle_girth +
            6 * pattern_seam_allowance +
            2 * pattern_sheet_spacing,
            row2_y
        ])
            pattern_toe_reinforcement_left();

    if (pattern_heel_reinforcement_enabled)
        translate([
            pattern_sock_gusset_width +
            pattern_effective_ankle_girth +
            toe_box_width +
            10 * pattern_seam_allowance +
            3 * pattern_sheet_spacing,
            row2_y
        ])
            pattern_heel_reinforcement_left();

    row3_y =
        row2_y +
        max([
            pattern_sock_gusset_length,
            2 * pattern_collar_turn_allowance,
            pattern_toe_reinforcement_length,
            pattern_heel_reinforcement_height
        ]) +
        2 * pattern_seam_allowance +
        pattern_sheet_spacing;

    translate([0, row3_y])
        pattern_strobel_board_left();

    translate([
        max_foot_width +
        2 * pattern_sole_attachment_allowance +
        pattern_sheet_spacing,
        row3_y
    ])
        pattern_lasting_band_left();
}

module pattern_all_left() {
    if (pattern_style == "textile_shoe")
        pattern_textile_layout_left();
    else
        pattern_sock_layout_left();
}


// =============================================================================
// GEMEINSAME AUSGABE
// =============================================================================

module selected_left_part_v4() {
    if (output_part == "sole_only")
        sole_core_left();

    else if (output_part == "footbed_only")
        perforated_footbed_left();

    else if (output_part == "textile_template")
        textile_template_left();

    else if (output_part == "pattern_all")
        pattern_all_left();

    else if (output_part == "pattern_vamp")
        pattern_vamp_left();

    else if (output_part == "pattern_medial_quarter")
        pattern_quarter_left(true);

    else if (output_part == "pattern_lateral_quarter")
        pattern_quarter_left(false);

    else if (output_part == "pattern_tongue")
        pattern_tongue_left();

    else if (output_part == "pattern_heel_band")
        pattern_heel_band_left();

    else if (output_part == "pattern_collar")
        pattern_collar_left();

    else if (output_part == "pattern_sock_medial")
        pattern_sock_side_left(true);

    else if (output_part == "pattern_sock_lateral")
        pattern_sock_side_left(false);

    else if (output_part == "pattern_sock_gusset")
        pattern_sock_gusset_left();

    else if (output_part == "pattern_toe_reinforcement")
        pattern_toe_reinforcement_left();

    else if (output_part == "pattern_heel_reinforcement")
        pattern_heel_reinforcement_left();

    else if (output_part == "pattern_strobel_board")
        pattern_strobel_board_left();

    else if (output_part == "pattern_lasting_band")
        pattern_lasting_band_left();

    else if (output_part == "pattern_interface_overlay")
        pattern_interface_overlay_left();

    else {
        sole_core_left();

        if (footbed_enabled && show_footbed_next_to_sole)
            translate([
                max_foot_width +
                2 * rim_width +
                part_gap,
                0,
                0
            ])
                perforated_footbed_left();
    }
}

module selected_part_v4() {
    if (foot_side == "left")
        selected_left_part_v4();
    else
        mirror([1, 0, 0])
            selected_left_part_v4();
}

if (render_pair &&
    (output_part == "sole_only" ||
     output_part == "assembled" ||
     output_part == "footbed_only" ||
     output_part == "textile_template" ||
     output_part == "pattern_strobel_board" ||
     output_part == "pattern_lasting_band" ||
     output_part == "pattern_interface_overlay")) {

    translate([-pair_offset / 2, 0, 0])
        selected_left_part_v4();

    translate([pair_offset / 2, 0, 0])
        mirror([1, 0, 0])
            selected_left_part_v4();

} else {
    selected_part_v4();
}
