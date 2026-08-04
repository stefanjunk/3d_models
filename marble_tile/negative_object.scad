/*
    Symmetrische Fliese und Negativform für Gips

    Erwartete Orientierung des STL:
    - gewünschte Fliesenmitte bei CENTER_X / CENTER_Y
    - flache Rückseite bei Z = BACK_Z
    - Relief zeigt nach +Z
    - Maße in Millimetern
*/

// --------------------------------------------------
// Einstellungen
// --------------------------------------------------

INPUT_FILE = "/home/stefan/Projekte/3d_models/marble_tile/xs_strong_new.stl";

// Außenmaße der fertigen Fliese
TILE_X = 200;
TILE_Y = 200;

// Maximale Gesamthöhe von Rückseite bis Reliefspitze
TILE_HEIGHT = 15;

// Tatsächliche Mitte des importierten Modells
CENTER_X = 0;
CENTER_Y = 0;

// Z-Position der flachen Rückseite
BACK_Z = 0;

// Formabmessungen
SIDE_WALL = 10;
BOTTOM_THICKNESS = 8;

// Kleine Überlappung für robuste Boolean-Operationen
EPSILON = 0.10;

// Größe der Hilfsgeometrie
CLIP_SIZE = 10000;

// true: Negativform anzeigen
// false: symmetrische positive Fliese anzeigen
SHOW_MOLD = true;


// --------------------------------------------------
// Import und Ausrichtung
// --------------------------------------------------

module source_tile() {
    translate([
        -CENTER_X,
        -CENTER_Y,
        -BACK_Z
    ])
    rotate([90,0,0])
        import(
            file = INPUT_FILE,
            convexity = 50
        );
}


// --------------------------------------------------
// Ein Viertel behalten
//
// Dieses Beispiel verwendet +X / +Y.
// Die geringe negative Erweiterung erzeugt an den
// Spiegelachsen eine kleine Überlappung.
// --------------------------------------------------

module selected_quarter() {
    intersection() {
        source_tile();

        translate([
            -EPSILON,
            -EPSILON,
            -CLIP_SIZE
        ])
            cube([
                CLIP_SIZE + EPSILON,
                CLIP_SIZE + EPSILON,
                2 * CLIP_SIZE
            ]);
    }
}


// --------------------------------------------------
// Viertel auf vier Bereiche spiegeln
// --------------------------------------------------

module symmetric_tile() {
    union() {
        // +X / +Y
        selected_quarter();

        // -X / +Y
        mirror([1, 0, 0])
            selected_quarter();

        // +X / -Y
        mirror([0, 1, 0])
            selected_quarter();

        // -X / -Y
        mirror([1, 0, 0])
            mirror([0, 1, 0])
                selected_quarter();
    }
}


// --------------------------------------------------
// Cutter für die offene Gipsform
//
// Durch die Drehung zeigt das Relief nach unten.
// Die flache Rückseite liegt knapp oberhalb der
// Formöffnung.
// --------------------------------------------------

module tile_cutter() {
    translate([0, 0, EPSILON])
        rotate([180, 0, 0])
            symmetric_tile();
}


// --------------------------------------------------
// Formblock
// --------------------------------------------------

module mold_block() {
    outer_x = TILE_X + 2 * SIDE_WALL;
    outer_y = TILE_Y + 2 * SIDE_WALL;
    block_height = TILE_HEIGHT + BOTTOM_THICKNESS;

    translate([
        -outer_x / 2,
        -outer_y / 2,
        -block_height
    ])
        cube([
            outer_x,
            outer_y,
            block_height
        ]);
}


// --------------------------------------------------
// Fertige Negativform
// --------------------------------------------------

module mold_negative() {
    difference() {
        mold_block();
        tile_cutter();
    }
}


// --------------------------------------------------
// Ausgabe
// --------------------------------------------------

if (SHOW_MOLD) {
    mold_negative();
} else {
    symmetric_tile();
}
