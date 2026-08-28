# Flapping-Tail Spielzeug-U-Boot (parametrisch, FDM)

Ein Spielzeug-U-Boot, das sich durch **Schlagen der Schwanzflosse** fortbewegt:
ein N20-Getriebemotor treibt über eine Kurbelscheibe mit Langloch eine
Schwanzwippe (Slotted-Rocker), an der die vertikale Heckflosse sitzt
(±~20° Schlagwinkel, Spitze ≈ ±15 mm Hub). Der Rumpf besteht aus
**Nase + 4 gelenkigen Gliedern + Elektronik-Kapsel**; jedes Glied ist ein
eigener wasserdichter Auftriebskörper, verbunden über vertikale
Bolzengelenke (±10° seitliche Schwenkfreiheit pro Gelenk).

Eine **parametrische Freiform-Fischhülle** läuft über Nase, Gelenkglieder und
Kapsel. Natürliche kubische Seiten- und Draufsichtkurven führen registrierte
elliptische Loft-Querschnitte; der bestehende Druck-, Dicht- und Mechanikkern
bleibt dabei unverändert. Drei breite, nur 0,55–1,0 mm hohe Längskämme, eine
Rückenflosse, zwei nach unten geneigte Brustflossen und eine symmetrische
Schwanzflosse erzeugen die Fischsilhouette ohne Schuppen- oder Gesichtsdekor.

Die **Schwimmblase** ist ein Reibkolben in der Nase: Knopf drücken/ziehen
verstellt die Verdrängung um insgesamt ≈ 6,7 ml (±3,3 g Feintrimm).
Grobtrimm über Ballast: Kiel-Tasche (Stahlschrot + Epoxy, Gewinde-Stopfen
M12×1,5) und Ballast-Kasten (Münzen) in der Kapsel. Zielzustand: knapp
unter der Wasseroberfläche schwebend (Auslegung 98 % getaucht).

Rahmenkonvention: +X = Heckwärts, +Z = oben. Alle Maße in mm.

## Status / Validierung — 1.1.0-draft.1

- 29 Pytest-Tests grün (Kinematik, Gewinde, geschützte Schnittstellen,
  vollständiger Heckschlag, Dichtigkeit, C2-Führungskurven, Auftrieb,
  Bett-Passung und kanonische Produktkennzeichnung).
- Preflight: 8 Checks PASS (`reports/preflight-v1.1.0-draft.1.json`).
- Surfacing-Contract gültig (`surfacing-spec.yaml`), Routing
  `bspline-loft-hybrid`; Kurven-/Flossennachweis in
  `reports/surfacing-v1.1.0-draft.1.json` und
  `reports/surfacing-curves-v1.1.0-draft.1.csv`.
- Hardpoint-Drift: 0,00 mm an allen geschützten Punkten, Achsen und Ebenen
  (`reports/hardpoint-drift-v1.1.0-draft.1.json`).
- Modellansichten: `previews/production-v1.1.0-draft.1/assembly-side.png`,
  `assembly-top.png` und `assembly.png`.
- Die kanonische Compact-Kennzeichnung ist 0,40 mm tief in die Kielunterseite
  graviert; Gesamtansicht und lesbarer Nahnachweis liegen als
  `watermark-finished-underside.png` und `watermark-keel-closeup.png` im
  Produktions-Preview-Ordner. Physischer Coupon und Freigabe bleiben offen.
- Mechanikbibliothek geprüft: Sample 002 liefert Gelenkprinzip/4-mm-Stift/
  0,25-mm-Spiel, Sample 078 das Bajonettprinzip mit 0,30-mm-Standardspiel.
  Auswahl und verworfene Kandidaten stehen unter `mechanism/`.
- Auftriebsrechnung `reports/buoyancy-v1.1.0-draft.1.json`:
  Verdrängung ≈ 474,7 ml, Trockenmasse ≈ 408,7 g, nötiger Ballast ≈ 59,9 g
  (vollständig im Kiel möglich), Blase ≈ 6,7 g Stellbereich.
- Der exakte Anycubic-Slicer-Gate ist fail-closed `NOT_RUN`, weil Druckermodell
  und freigegebene vollständige Maschinen-/Prozess-/PETG-Profile noch fehlen.
  Diese Revision und alle neuen STLs bleiben deshalb ausdrücklich **DRAFT**.
- Passungs-Coupon für Scharnierfreiheit (0,15/0,25/0,35/0,45 mm je Seite):
  `reports/fit_coupon.scad` → `exports/stl/fit_coupon_hinge.stl`.
  **Vor dem ersten Boot-Druck Coupon mit demselben Profil drucken und die
  Scharnierpassung wählen** (Default `hinge_clearance = 0.25`).

## DRAFT-Druckliste (`exports/draft-v1.1.0-draft.1/`)

| Teil | Material | Ausrichtung/Hinweis |
|---|---|---|
| nose_body | PETG | stehend auf Heckfläche, Nase nach oben; Freiformhaut/Kämme sichtbar |
| bladder_piston | PETG | stehend, Knopf nach unten; 2× O-Ring 20×1,5 |
| segment_01..04 | PETG | liegend, Gelenkbolzen vertikal; breite Kämme oben/seitlich |
| capsule_body | PETG | Kiel unten; Rückenflosse oben, Brustflossen 45° abwärts geneigt |
| capsule_cap | PETG | Plug nach oben |
| pivot_pin, hinge_pin (×5) | PETG | stehend; Enden nach Montage leicht anschmelzen/vernieten |
| crank_disc, shaft_sleeve | PETG | Disc flach, Pin nach oben |
| tail_rocker | PETG | flach liegend; Langloch fetten |
| tail_fin | PETG oder TPU | flach liegend; symmetrische Schwanzform, Antriebsfläche 104,5 % der Baseline |
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
   (siehe `reports/buoyancy-v1.1.0-draft.1.json`, Wert `required_ballast_g`).
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
- Fischform als **additive B-Rep-Freiformhülle** statt Deformation des
  Druckkörpers: semantisch editierbar, keine Drift an Achsen/Dichtungen.
  Drei breite Kämme bei 0/±62° ersetzen die fünf runden Aufsatzrippen.
- Rücken- und Brustflossen sitzen ausschließlich an der großen Kapsel; die
  Brustflossen sind 45° nach unten geneigt, um die Seitenlesbarkeit zu stärken
  und in Kiel-unten-Drucklage ungünstige horizontale Unterseiten zu vermeiden.
- Die Rocker-Zunge, 2,5-mm-Stiftbohrung und der Flossenschlag bleiben exakt;
  nur die alte einseitige Ruderfläche wurde durch eine symmetrische Caudalform
  mit 1,045-facher projizierter Baselinefläche ersetzt.
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
`submarine/config.py`; Freiformparameter beginnen mit `fish_`, Flossenparameter
mit `dorsal_`, `pectoral_` oder `caudal_`. Alle Prüfungen laufen über
`submarine/preflight.py`, die Pytest-Suite und das Projekt-Validierungsmanifest.
