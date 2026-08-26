# Flapping-Tail Spielzeug-U-Boot (parametrisch, FDM)

Ein Spielzeug-U-Boot, das sich durch **Schlagen der Schwanzflosse** fortbewegt:
ein N20-Getriebemotor treibt über eine Kurbelscheibe mit Langloch eine
Schwanzwippe (Slotted-Rocker), an der die vertikale Heckflosse sitzt
(±~20° Schlagwinkel, Spitze ≈ ±15 mm Hub). Der Rumpf besteht aus
**Nase + 4 gelenkigen Gliedern + Elektronik-Kapsel**; jedes Glied ist ein
eigener wasserdichter Auftriebskörper, verbunden über vertikale
Bolzengelenke (±10° seitliche Schwenkfreiheit pro Gelenk).

Fünf **parametrisch geloftete Längsrippen** laufen über die obere und
seitliche Rumpfhälfte. Sie bilden eine fischähnliche Stromlinienform ab,
verjüngen sich an allen Gelenken und am Heck und lassen Unterseite, Kiel,
Deckel und Antrieb frei. Der Funktionskern wird dabei nicht verformt.

Die **Schwimmblase** ist ein Reibkolben in der Nase: Knopf drücken/ziehen
verstellt die Verdrängung um insgesamt ≈ 6,7 ml (±3,3 g Feintrimm).
Grobtrimm über Ballast: Kiel-Tasche (Stahlschrot + Epoxy, Gewinde-Stopfen
M12×1,5) und Ballast-Kasten (Münzen) in der Kapsel. Zielzustand: knapp
unter der Wasseroberfläche schwebend (Auslegung 98 % getaucht).

Rahmenkonvention: +X = Heckwärts, +Z = oben. Alle Maße in mm.

## Status / Validierung

- 21 Pytest-Tests grün (Kinematik, Gewinde, Kollisionen aller Bauteilpaare = 0,
  Dichtigkeit der Druckkörper, Auftrieb/Ballastplan, Bett-Passung).
- Preflight: 8 Checks PASS (`reports/preflight.json`).
- Surfacing-Contract gültig (`surfacing-spec.yaml`), Routing
  `bspline-loft-hybrid`; Details in `reports/surfacing.json`.
- Surfacing-Evidenz: `previews/fish_side.png`, `previews/fish_top.png`,
  `previews/fish_perspective.png` und `previews/fish_edges.png`.
- Mechanikbibliothek geprüft: Sample 002 liefert Gelenkprinzip/4-mm-Stift/
  0,25-mm-Spiel, Sample 078 das Bajonettprinzip mit 0,30-mm-Standardspiel.
  Auswahl und verworfene Kandidaten stehen unter `mechanism/`.
- Auftriebsrechnung `reports/buoyancy.json` (Standard-Config):
  Verdrängung ≈ 380 ml, Trockenmasse ≈ 289 g, nötiger Ballast ≈ 86,5 g
  (Kiel ≈ 63 g + Kasten ≈ 23,5 g), Blase ≈ 6,7 g Stellbereich.
- Passungs-Coupon für Scharnierfreiheit (0,15/0,25/0,35/0,45 mm je Seite):
  `reports/fit_coupon.scad` → `exports/stl/fit_coupon_hinge.stl`.
  **Vor dem ersten Boot-Druck Coupon mit demselben Profil drucken und die
  Scharnierpassung wählen** (Default `hinge_clearance = 0.25`).

## Druckliste (`exports/stl/`)

| Teil | Material | Ausrichtung/Hinweis |
|---|---|---|
| nose_body | PETG | stehend auf Heckfläche, Nase nach oben; Dorsalrippe sichtbar |
| bladder_piston | PETG | stehend, Knopf nach unten; 2× O-Ring 20×1,5 |
| segment_01..04 | PETG | liegend, Gelenkbolzen vertikal; Rippen nach oben/seitlich |
| capsule_body | PETG | Kiel unten; Rippen oben/seitlich, Supports nur am Gland-Boss |
| capsule_cap | PETG | Plug nach oben |
| pivot_pin, hinge_pin (×5) | PETG | stehend; Enden nach Montage leicht anschmelzen/vernieten |
| crank_disc, shaft_sleeve | PETG | Disc flach, Pin nach oben |
| tail_rocker | PETG | flach liegend; Langloch fetten |
| tail_fin | PETG oder TPU | flach liegend; TPU = weichere Flosse, mehr Schub |
| keel_plug | PETG | stehend; O-Ring 9×1,5, Gewinde M12×1,5 |
| ballast_box, ballast_lid | PETG | wie gedruckt |
| fit_coupon_hinge | wie Boot | zur Passungswahl |

Druck: 0,4er Düse, **4+ Perimeter** (Wand 2,4 mm = wasserdicht ausgelegt),
25 % Infill, PETG empfohlen (PLA nimmt Wasser auf). Fugen/O-Ringe mit
Silikonfett; Kapsel innen optional mit Epoxy versiegeln.

## Zukauf (BOM)

- 1× N20-Getriebemotor 3 V, ~150–300 U/min, **Welle ≥ 15 mm** (Ø3)
- 2× AAA (NiMH empfohlen) + Kabel, Lötkontakte
- 1× Reedschalter (NO) + Magnetstab (Schalter bleibt gekapselt, keine
  Rumpfdurchdringung)
- O-Ringe: 20×1,5 (×2, Blase), 36×1,5 (Kapseldeckel), 3×1,5 (Gland), 9×1,5 (Kiel)
- Silikonfett (lebensmittelecht), 2× Kabelbinder (Motor, Kurbel),
  optional Sekundenkleber (Shaft-Sleeve auf Motorwelle)
- Ballast: Stahlschrot + 2K-Epoxy (Kiel), Münzen (Kasten)

## Montage (Kurzfassung)

1. Coupon drucken, Scharnierfreiheit prüfen, ggf. `hinge_clearance` anpassen
   und neu generieren: `python3 generate_submarine.py`.
2. Glieder + Nase mit hinge_pins verbinden (Bolzen senkrecht, Enden vernieten).
3. Motor in den Sattel (Kapsel hinten), Welle durch die Gland-Bohrung
   (O-Ring 3×1,5 gefettet einlegen), Sleeve aufkleben, Kurbelscheibe
   aufklemmen (Kabelbinder durch den Schlitz).
4. Batterie-Sättel bestücken, Reedschalter in die Tasche oben vorn (Wand
   dort 1,7 mm), verdrahten: Batterie → Reed → Motor.
5. Ballast-Kasten grob nach Rechnung füllen, Deckel auflegen.
6. Kapseldeckel: O-Ring 36×1,5 gefettet, einsetzen, ~60–90° drehen
   (Bajonett), letzte Gliedzunge sitzt vor dem Deckel.
7. Heck: Rocker auf den pivot_pin (von vorn durch Auge 1, Nabe, Auge 2),
   Kurbelzapfen-Kopf vor die Nabe; Flosse zwischen die Rocker-Ohren,
   Bolzen Ø2,5-Loch (2,5-mm-Stift oder gedruckter Pin) von oben.
8. Kiel füllen (Schrot + Epoxy), Stopfen mit O-Ring.

## Trimmen auf "knapp unter Oberfläche"

1. Boot ohne Deckel-Ballast wiegen; Soll-Masse ≈ 0,98 × Verdrängung
   (siehe `reports/buoyancy.json`, Wert `required_ballast_g`).
2. Kiel zuerst füllen (tiefer Schwerpunkt = stabile Lage), Rest in den
   Ballast-Kasten.
3. Im Becken: Schwimmblase ganz eindrücken (Boot sinkt tiefer) bzw.
   herausziehen (steigt). Feinjustage bis der Rücken knapp unter der
   Wasserlinie bleibt. Magnet anlegen → Flossenschlag prüfen: Boot sollte
   langsam vorwärts schwimmen, nicht eintauchen.

## Decision-Log (Auszug)

- Schwimmblase als **Reibkolben** statt Gewinde: einfacher, klemmt nicht,
  hält über O-Ring-Reibung; Verstellweg 20 mm = 6,7 ml.
- Antrieb als **Langloch-Kurbel (Scotch-Yoke-artig)** statt Pleuel: ein
  bewegtes Teil weniger, unempfindlich gegen Schräglauf; dafür etwas Spiel
  im Langloch (fetten).
- Gland-Dichtung: O-Ring statisch im Boss, Welle rotiert (RC-Boot-Standard),
  gefettet; Boss kurz gehalten, Sleeve verlängert die Welle.
- Deckel als Bajonett ohne Schrauben; Nut 1,2 mm tief in der 2,4-mm-Wand.
- Glieder als einzelne Auftriebskörper: Leck in einem Glied ≠ Untergang.
- Fischform als **additive B-Rep-Loft-Rippen** statt Deformation des
  Druckkörpers: semantisch editierbar, keine Drift an Achsen/Dichtungen;
  fünf Winkel 0/±45/±90°, minimale Rippenbreite 1,44 mm.
- Mechanikbibliothek: Gelenkparameter aus Sample 002 beibehalten; beim
  Bajonett Sample 078s 0,30-mm-Standardspiel übernommen und die O-Ring-Nut
  separat auf 0,20 mm radiale Pressung kompensiert. Kupplung 109 bleibt wegen
  Bauraum, M3-Hardware und falschem Wellenpaar außen vor.

## Regenerieren

```bash
python3 generate_submarine.py            # STLs + Reports + Vorschau
python3 -m pytest tests -q               # Validierung
```

Parameter (Anzahl Glieder, Durchmesser, Blasenweg, Kurbelradius …) in
`submarine/config.py`; Rippenparameter beginnen mit `fish_rib_`. Alle
Prüfungen laufen über `submarine/preflight.py` und die Pytest-Suite.
