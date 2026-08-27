// ============================================================================
// NameForm Bookends — MM-PER-001, spec revision 0.1.0
// Parametric source of truth (hero variant: WORD = "M")
//
// Coordinate system (mm): X = word direction, Y = depth (+Y viewer side,
// -Y book side), Z = up. Underside sits on the build plate at z = 0.
//
// Layout (derived from spec 0.1.0, decision log D2/D6/D7/D8):
//   base slab      x ∈ [0, BASE_W],        y ∈ [-BOOK_FACE_Y-BALLAST, +LETTER_FRONT], z ∈ [0, BASE_H]
//   letter (word)  x centered,             y ∈ [-PANEL_T+PANEL_OVERLAP, LETTER_FRONT], z ∈ [BASE_H, BASE_H+CAP]
//   stop panel     x full base width,      y ∈ [-PANEL_T, 0],                    z ∈ [BASE_H, BASE_H+CAP]
//   book face      at y = -PANEL_T  (books stand on the -Y side and lean against it)
//
// Stability: books (2.0 kg, CM 25 mm beyond book face) push in +Y; the part
// tips about the front bottom edge (y = LETTER_FRONT). The ballast toe behind
// the book face (BALLAST) plus the low base keep SF >= 1.5 (see
// validation/stability.json, computed from the exact mesh volume/CM).
//
// Manufacturing: upright, no supports, 0.2 mm layers, 0.4 mm nozzle.
// Anti-slip dimples + JuSt watermark (JSI-WM-001-R1) are recessed into the
// underside only. WATERMARK is the LAST solid change: master exports use
// WATERMARK=false, final exports use WATERMARK=true.
// ============================================================================

/* [Parameters] */
WORD = "M";                 // 1-10 uppercase letters; hero revision is "M"
SIZE = 192.95;              // font em size in mm (auto: min(192/advance, 180/cap_ratio))
CAP = 140.66;               // resulting cap height (reference; computed from SIZE)
BASE_W = 216;               // word width + 24 mm margin
BALLAST = 100;              // ballast depth behind book face (stability, decision D6)
BASE_H = 20;                // base slab height
LETTER_DEPTH = 50;          // letter extrusion (front-to-back)
PANEL_T = 4;                // stop panel thickness (research: 3 mm, +1 mm margin)
PANEL_OVERLAP = 2;          // bonding overlap between panel and letters
CHAMFER = 2;                // base corner chamfer (spec: 2 mm, hazard mitigation)
DIMPLE_PITCH = 6;           // anti-slip dimple grid pitch
DIMPLE_SIZE = 3;            // dimple edge length
DIMPLE_DEPTH = 0.4;         // dimple recess depth
WATERMARK = false;          // false = master export, true = final (last solid change)
WM_DXF = "watermark/wm-standard-centered.dxf";
WM_DEPTH = 0.4;             // standard watermark recess depth
/* [Parameters] */

LETTER_FRONT = LETTER_DEPTH - PANEL_T + PANEL_OVERLAP;   // = 48
BOOK_FACE_Y = -PANEL_T;                                   // = -4
UNDER_Y0 = BOOK_FACE_Y - BALLAST;                          // underside min y = -104
CENTER_Y = (UNDER_Y0 + LETTER_FRONT) / 2;                  // underside center y = -28

// ---- Hard acceptance constraints (fail fast at compile time) --------------
assert(BASE_W <= 216, "word width + margin exceeds 216 mm bed-safe width");
assert(LETTER_FRONT + BALLAST <= 216, "base depth exceeds bed-safe depth");
assert(BASE_H + CAP <= 240, "total height exceeds bed-safe height");
assert(CAP >= 40, "cap height below 40 mm tier limit — word too long, see listing");
assert(LETTER_DEPTH >= 40, "letter depth below 40 mm minimum");

// ---- Geometry --------------------------------------------------------------

module letter() {
  // Text in the XY plane (baseline y=0, caps toward +Y, centered on x=0),
  // extruded LETTER_DEPTH along Z, then rotated 90° about X so the letter
  // stands upright: caps toward +Z, depth toward -Y, text face toward +Y.
  // Finally translated so the letter back sits 2 mm into the panel (bond)
  // and the letter rests on the base top.
  translate([BASE_W / 2, LETTER_FRONT, BASE_H])
    rotate([90, 0, 0])
      linear_extrude(height = LETTER_DEPTH)
        text(WORD, font = "DejaVu Sans Bold", size = SIZE,
             halign = "Center", valign = "Baseline");
}

module corner_cut(cx, cy) {
  // 45° diamond centered on the corner axis cuts a right triangle of leg
  // CHAMFER at each base corner (full base height).
  s = CHAMFER * 1.4142;
  translate([cx, cy, -0.1])
    rotate([0, 0, 45])
      cube([s, s, BASE_H - 0.1], center = true);
}

module dimples() {
  // Anti-slip dimple grid on the underside, with a clean exclusion zone
  // around the watermark (15 mm margin).
  let(wm_x = [BASE_W/2 - 20, BASE_W/2 + 20])
  let(wm_y = [CENTER_Y - 12, CENTER_Y + 12])
  for (x = [DIMPLE_PITCH/2 : DIMPLE_PITCH : BASE_W - DIMPLE_PITCH/2 - 1])
    for (y = [BOOK_FACE_Y - BALLAST + DIMPLE_PITCH/2 : DIMPLE_PITCH : LETTER_FRONT - DIMPLE_PITCH/2])
      if (x < wm_x[0] || x > wm_x[1] || y < wm_y[0] || y > wm_y[1])
        translate([x, y, -0.1])
          cube([DIMPLE_SIZE, DIMPLE_SIZE, DIMPLE_DEPTH + 0.1]);
}

module watermark_cut() {
  // Standard JuSt watermark, centered on the underside, recessed WM_DEPTH.
  // The imported DXF is centered on the origin (see scripts/build.py).
  translate([BASE_W / 2, CENTER_Y, -0.1])
    linear_extrude(height = WM_DEPTH + 0.1)
      import(file = WM_DXF);
}

module part() {
  difference() {
    union() {
      // base slab (ballast): x width, y depth (back to front), z height
      translate([0, UNDER_Y0, 0])
        cube([BASE_W, LETTER_FRONT - UNDER_Y0, BASE_H]);
      // letters (word)
      letter();
      // full-height stop panel at the book side
      translate([0, BOOK_FACE_Y, BASE_H])
        cube([BASE_W, PANEL_T, CAP]);
    }
    // corner chamfers (base only)
    corner_cut(0, BOOK_FACE_Y - BALLAST);
    corner_cut(BASE_W, BOOK_FACE_Y - BALLAST);
    corner_cut(0, LETTER_FRONT);
    corner_cut(BASE_W, LETTER_FRONT);
    // anti-slip dimples (underside)
    dimples();
    // watermark — LAST solid change
    if (WATERMARK) watermark_cut();
  }
}

part();
