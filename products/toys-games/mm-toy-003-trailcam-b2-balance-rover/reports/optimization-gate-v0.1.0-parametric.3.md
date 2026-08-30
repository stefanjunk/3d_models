# Optimierungs-Gate — 0.1.0-parametric.3

## Entscheidung

Die ausgewählte Geometrie nutzt offene, verrippte Seitenrahmen, lokale
Kraftpfade und getrennte Funktionsmodule. Weitere automatische
Leichtbauänderungen oder verlustbehaftete Mesh-Vereinfachung wurden nicht
angewendet. Der Kandidat ist geometrisch effizient genug für die nächste
Couponrunde, aber mangels reproduzierbarem Slicer-Baseline noch kein
abgeschlossenes Fertigungsoptimum.

## Erhaltungsbedingungen

- Pololu-1995-Motorhalter-Slots und gemeinsame Radachse
- 6,0 mm nominaler 42-mm-Reifenfreigang und 5,0 mm bei 44 mm
- Gens-ace-Aufnahme mit 1,0 mm Nennspiel und ±12 mm Trimm
- Leiterplatten-, IMU-, Kamera-, XT60-, Sicherungs- und Antennenbereiche
- Metall-Durchgangsverschraubungen in Motor-, Akku-, Landungs- und
  Ballastlastpfaden
- Bodenflächen, Montageflächen und künftige Kennzeichnungsregion

## Digitaler Nachweis

- 597,86 g konservative Druckteilmasse bei angenommener Vollmaterialdichte;
  tatsächlicher Slicer-Materialeinsatz wird nicht daraus abgeleitet
- 68.582 Dreiecke und 3,272 MiB über 19 Rover-STL; größtes Mesh 9.072 Dreiecke
  bzw. 0,433 MiB
- direkte Tessellierung der analytischen CadQuery-B-Reps mit 0,10 mm linearer
  und 0,10 rad angularer Toleranz
- keine offene, nicht-mannigfaltige, degenerierte oder doppelte Meshfläche
- jedes dokumentierte Druckteil passt in 220 × 220 × 250 mm

Die Dateien sind klein und die kritischen Interfaces sind geschützt; eine
zusätzliche Mesh-Dezimierung hätte keinen belegten Nutzen und könnte
Passgeometrie verschieben. Sie ist deshalb als `not-beneficial` bewertet.

## Offene Optimierungsnachweise

Ein zulässiger A/B-Vergleich von Druckzeit und Material benötigt vollständige,
explizite Anycubic-Maschinen-, Prozess- und Filament-JSON-Profile sowie einen
unveränderten Slicer-Workflow. Diese Eingaben fehlen. Deshalb gibt es keine
Slicer-Metrik, keinen 3MF- und keinen G-Code-Nachweis. Nach Couponkorrekturen und
Profilfreigabe ist eine reproduzierbare Baseline zu schneiden; erst dann dürfen
Material-, Zeit-, Support- und Nahtvarianten quantitativ verglichen werden.
