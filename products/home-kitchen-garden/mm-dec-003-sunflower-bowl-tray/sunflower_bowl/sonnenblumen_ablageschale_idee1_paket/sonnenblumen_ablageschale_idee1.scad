/*
  Sonnenblumen-Ablageschale – Idee 1 "Sanfte Blüte"
  Maßeinheit: mm

  Standardabmessungen:
  - Außendurchmesser: ca. 200 mm
  - Höhe: ca. 32 mm
  - flache Standfläche: 126 mm Durchmesser
  - 20 Blütenblätter
  - minimale vertikale Materialstärke: ca. 3 mm

  Das Modell ist als geschlossenes Polyeder aufgebaut und benötigt bei
  normaler Ausrichtung mit der flachen Unterseite auf dem Druckbett keinen Support.
*/

// ---------- Hauptparameter ----------
petal_count       = 20;     // Anzahl der Blütenblätter
petal_tip_radius  = 100;    // Außenradius an den Blattspitzen
petal_valley_radius = 92;   // Außenradius zwischen den Blättern
petal_sharpness   = 1.70;   // größer = schmalere Blattspitzen

base_radius       = 63;     // Radius der flachen Unterseite
base_thickness    = 3.20;   // Bodenstärke in der Mitte
floor_rise        = 0.40;   // sehr sanfter Anstieg des Innenbodens

petal_tip_height  = 32;     // Höhe an den Blattspitzen
petal_valley_height = 27;   // Höhe zwischen den Blättern
wall_exponent     = 1.10;   // Krümmung der Schalenwand

bottom_slope      = 0.74;   // supportfreundliche Unterseitensteigung
bottom_cap        = 24.50;  // maximale Höhe der Unterseite

ridge_height      = 0.45;   // dezente Mittelrippe auf jedem Blatt
ridge_sharpness   = 10;

// ---------- Sonnenblumen-Kerntextur ----------
seed_texture_enabled = true;
seed_radius       = 45;
seed_spacing      = 5.0;
seed_height       = 0.38;
seed_sigma        = 1.05;
seed_fade         = 5.0;

// ---------- Auflösung ----------
// Für schnelle Vorschau z.B. 180 / 55 verwenden.
// Für sehr feinen STL-Export z.B. 480 / 110 verwenden.
angular_steps     = 360;
radial_steps      = 90;

function clamp(x, lo=0, hi=1) = min(max(x, lo), hi);

function petal_phase(a) =
    pow((1 + cos(petal_count * a)) / 2, petal_sharpness);

function outer_radius(a) =
    petal_valley_radius
    + (petal_tip_radius - petal_valley_radius) * petal_phase(a);

function edge_height(a) =
    petal_valley_height
    + (petal_tip_height - petal_valley_height) * petal_phase(a);

function seed_texture(r, a) =
    (!seed_texture_enabled || r > seed_radius)
    ? 0
    : let(
        k      = max(1, round(r / seed_spacing)),
        rr     = k * seed_spacing,
        n      = max(6, round(2 * PI * rr / seed_spacing)),
        turns  = a * n / 360,
        frac   = turns - round(turns),
        arc    = rr * 2 * PI * frac / n,
        dr     = r - rr,
        fade   = clamp((seed_radius - r) / seed_fade),
        ring   = seed_height
                 * exp(-(dr*dr + arc*arc) / (2 * seed_sigma * seed_sigma))
                 * fade,
        center = seed_height
                 * exp(-(r*r) / (2 * seed_sigma * seed_sigma))
      ) max(ring, center);

function top_height(s, a) =
    let(
        R          = outer_radius(a),
        r          = s * R,
        t          = clamp((r - base_radius) / (R - base_radius)),
        floor_z    = base_thickness
                     + floor_rise * pow(min(r / base_radius, 1), 2),
        floor_edge = base_thickness + floor_rise,
        wall_z     = floor_edge
                     + (edge_height(a) - floor_edge)
                     * pow(t, wall_exponent),
        base_z     = r <= base_radius ? floor_z : wall_z,
        ridge_phase = pow(max(0, cos(petal_count * a)), ridge_sharpness),
        ridge      = ridge_height * ridge_phase
                     * pow(t, 0.80) * (1 - 0.25 * t)
    ) base_z + ridge + seed_texture(r, a);

function bottom_height(s, a) =
    let(
        r = s * outer_radius(a)
    ) min(bottom_cap, max(0, (r - base_radius) * bottom_slope));

function top_index(i, j) =
    1 + (i - 1) * angular_steps + (j % angular_steps);

function bottom_center_index() =
    1 + radial_steps * angular_steps;

function bottom_index(i, j) =
    bottom_center_index() + 1
    + (i - 1) * angular_steps + (j % angular_steps);

points = concat(
    // oberer Mittelpunkt
    [[0, 0, top_height(0, 0)]],

    // obere Fläche
    [for (i = [1:radial_steps])
        for (j = [0:angular_steps-1])
            let(
                s = i / radial_steps,
                a = 360 * j / angular_steps,
                r = s * outer_radius(a)
            ) [r*cos(a), r*sin(a), top_height(s, a)]
    ],

    // unterer Mittelpunkt
    [[0, 0, 0]],

    // untere Fläche
    [for (i = [1:radial_steps])
        for (j = [0:angular_steps-1])
            let(
                s = i / radial_steps,
                a = 360 * j / angular_steps,
                r = s * outer_radius(a)
            ) [r*cos(a), r*sin(a), bottom_height(s, a)]
    ]
);

faces = concat(
    // oberer Mittelpunktfächer
    [for (j = [0:angular_steps-1])
        [0, top_index(1, j), top_index(1, j+1)]
    ],

    // obere Ringflächen
    [for (i = [1:radial_steps-1])
        for (j = [0:angular_steps-1]) each [
            [top_index(i, j),   top_index(i+1, j),   top_index(i+1, j+1)],
            [top_index(i, j),   top_index(i+1, j+1), top_index(i, j+1)]
        ]
    ],

    // unterer Mittelpunktfächer, umgekehrte Orientierung
    [for (j = [0:angular_steps-1])
        [bottom_center_index(), bottom_index(1, j+1), bottom_index(1, j)]
    ],

    // untere Ringflächen, umgekehrte Orientierung
    [for (i = [1:radial_steps-1])
        for (j = [0:angular_steps-1]) each [
            [bottom_index(i, j), bottom_index(i+1, j+1), bottom_index(i+1, j)],
            [bottom_index(i, j), bottom_index(i, j+1),   bottom_index(i+1, j+1)]
        ]
    ],

    // geschlossener Außenrand
    [for (j = [0:angular_steps-1]) each [
        [top_index(radial_steps, j),
         bottom_index(radial_steps, j),
         bottom_index(radial_steps, j+1)],
        [top_index(radial_steps, j),
         bottom_index(radial_steps, j+1),
         top_index(radial_steps, j+1)]
    ]]
);

polyhedron(points=points, faces=faces, convexity=12);
