# Barfußschuh V6 – Organic Freeform Workflow

V6 ersetzt die bisherige „extrudierte Platte + Seitenwand“-Logik durch einen freien 3D-Formaufbau.

## 1. Architektur

Die Konstruktion ist funktional zerlegt:

1. **Organic sole body** – glatter Multi-Section-Loft aus CadQuery.
2. **Curved textile-overlap lip** – eigenständiger, überlappender TPU-Körper.
3. **Hex tread** – Wabenprofil unter der Sohle.
4. **Hex side wrap** – flache Wabenprägung an Flanke/Lippe.
5. **Upper infill envelope** – Volumen für einen Slicer-„Infill-only“-Oberschuh.
6. **Upper reinforcement frame** – feste Anschluss-, Fersen- und Kragenzonen.
7. **Upper fuzzy shell** – dünne geschlossene TPU-Haut als Alternative.
8. **Textile interface templates** – weiterhin nutzbar, wenn der Schaft aus Stoff gefertigt wird.

Die 3MF-Sohle enthält die vier Sohlenkörper als benannte, absichtlich überlappende Komponenten. Die Überlappung ist konstruktiv; beim Slicen als eine Assembly werden die Bereiche zu einem zusammenhängenden Druckpfad verarbeitet.

## 2. Organische Sohlengeometrie

Der Sohlenkörper wird aus 12 parametrischen Querschnitten erzeugt. Jeder Querschnitt besitzt eigene Werte für:

- Breite
- mediale/laterale Mittellinienverschiebung
- Höhe der Laufsohle
- Höhe der Fußseite
- Querwölbung der Laufsohle
- leichte Wölbung der Fußseite
- seitlichen Bauch

Die Querschnitte werden mit glatten periodischen Splines beschrieben und längs mit einem nicht-geruled Loft verbunden. Dadurch sind Ferse, Mittelfuß, Ballen und Zehen nicht mehr nur eine 2D-Kontur mit vertikaler Extrusion.

### Nullsprengung

Referenzwerte der Standardkonfiguration:

- belastbarer Fersenbereich bei s=0,12: **5,0 mm** Fußseitenhöhe
- Ballenbereich bei s=0,72: **4,9 mm**
- Differenz: **0,1 mm**

Die hochgezogene hinterste Fersenkante und die Zehenspitze sind Rocker-/Rundungsbereiche und keine klassische Fersenerhöhung.

### Toe rocker

Die Laufseite steigt erst im vorderen Bereich an. An der äußersten Spitze liegen standardmäßig ungefähr 5 mm Rocker vor. Dadurch entsteht eine moderne geschwungene Seitenansicht ohne einen Knick.

## 3. Curved TPU lip

Die Lippe ist Bestandteil der TPU-Sohlenbaugruppe und kein Textilteil.

Standard:

```json
"lip_root_z": 3.6,
"lip_top_z": 13.5,
"lip_outer_bulge": 1.6,
"lip_textile_overlap": 2.3
```

Die Lippe:

- beginnt im Sohlenkörper,
- wölbt sich außen nach außen,
- läuft oben wieder ein,
- überdeckt den unteren Schaftrand um 2,3 mm,
- schützt Klebung und Naht.

## 4. Wabendesign

Das Wabenmotiv bleibt funktionaler Bestandteil des Designs:

- 445 Hex-Ringe auf der Laufseite
- 196 Hex-Ringe als Seiten-/Lippenwrap
- 4,0 mm Zellradius
- 0,75 mm Rippenbreite
- 0,70 mm Laufseitenrelief
- 0,42 mm Seitenrelief

Die Flexzonen werden beim Laufprofil ausgespart.

## 5. Oberteil – Variante A: Infill-only

Dateien:

- `v6_upper_infill_envelope_left.stl`
- `v6_upper_reinforcement_frame_left.stl`

Das Envelope ist **kein dünnes Wandmodell**, sondern ein geschlossenes 4,5-mm-Hüllvolumen. Genau das ist für einen Infill-only-Workflow nötig: Der Slicer benötigt ein Volumen, in dessen Innerem er das offene Infill erzeugen kann.

Im Slicer werden nur beim Envelope die Perimeter sowie Top/Bottom ausgeschaltet. Der Verstärkungsrahmen wird normal mit Wänden gedruckt.

Vorteile:

- sehr weich
- offen und atmungsaktiv
- Struktur direkt durch Gyroid/Cubic/Infill einstellbar
- kein starrer geschlossener TPU-Film über dem Fuß

Nachteile:

- stark slicerabhängig
- Kanten brauchen den separaten Verstärkungsrahmen
- zuerst Testcoupon slicen

## 6. Oberteil – Variante B: dünne Fuzzy-Ripple-Haut

Dateien:

- `v6_upper_fuzzy_shell_left.stl`
- `v6_upper_reinforcement_frame_left.stl`

Die Default-Haut ist **1,4 mm** dick. 0,8–0,9 mm war bei der diskreten Mesh-Erzeugung in der Standardauflösung nicht zuverlässig zusammenhängend; 1,4 mm ist für die bereitgestellte Datei robust und bleibt mit weichem TPU deutlich flexibel.

Wer eine feinere Mesh-Auflösung nutzt, kann `upper_fuzzy_wall_thickness` weiter reduzieren.

Fuzzy Skin sollte nur auf der Außenkontur angewendet werden, damit die Hautseite glatt bleibt.

Wichtig: Fuzzy Skin ist eine Textur und keine kontrollierte Belüftung. Die Standard-Fuzzy-Datei hat daher keine CAD-Perforationen. Für echte Atmungsaktivität ist die Infill-only-Variante vorzuziehen.

## 7. Verstärkungsrahmen

Der Rahmen verstärkt nur die funktionalen Bereiche:

- untere Anschlusszone zur Sohle
- Fersenbereich
- Kragenbereich

So bleibt die große Schaftfläche weich, während die Verbindung zur Sohle und der Fersenhalt nicht nur aus offenem Infill bestehen.

## 8. Technische Schnittstellen

- 44 Näh-/Befestigungslöcher
- tatsächlicher Standardabstand ca. 15,15 mm
- 2,3 mm Lippenüberdeckung des Textils/Oberschuhs
- Ballen-Flexzone bei ca. 68,5 % der Sohlenlänge
- zusätzliche kleinere Flexzonen
- flache Luft-/Feuchtigkeitskanäle auf der Fußseite

## 9. Dateien

### Sohle

- `v6_sole_left.3mf` – finale linke Baugruppe
- `v6_sole_right.3mf` – finale rechte Baugruppe
- `v6_sole_body_smooth_left.step` – organischer Master-Solid ohne kleine Druckfeatures
- `v6_curved_lip_smooth_left.step` – Master-Lippe
- `v6_sole_master_smooth_compound_left.step` – STEP-Compound

### Oberteile

- `v6_upper_infill_envelope_left/right.stl`
- `v6_upper_fuzzy_shell_left/right.stl`
- `v6_upper_reinforcement_frame_left/right.stl`
- `v6_upper_reference_last.step`

### Schnittmuster / textile Alternative

- `v6_strobel_template.svg`
- `v6_textile_interface_overlay.svg`

### Tests

- `testcoupon_infill_only.stl`
- `testcoupon_lip_textile_overlap.stl`
- `VALIDATION.json`
- `validate_v6.py`

## 10. Regeneration

```bash
python -m pip install -r requirements.txt
python generate_v6.py
python validate_v6.py
```

OpenSCAD wird nur für die deterministischen kleinen Ausschnitte (Flexrillen, Luftkanäle und Nahtlöcher) verwendet. Die organische Hauptgeometrie entsteht in CadQuery/Python.
