# Mesh-Komplexitätsbericht – Kamera-Whitebox DRAFT

## Entscheidung

Mesh-Vereinfachung ist für alle 24 eindeutigen DRAFT-STLs nicht sinnvoll. Die Netze sind direkt aus parametrischem OpenSCAD erzeugt, wasserdicht und liegen klar unter den Projektbudgets. Eine verlustbehaftete Vereinfachung würde kleine Kugel-/Socketflächen, Schraublöcher und Kamerapassungen gefährden, ohne den Fertigungsablauf nennenswert zu verbessern.

Status je Fertigungsmesh: `not-beneficial`.

## Messwerte

- 24 eindeutige STL-Dateien;
- 52.268 Dreiecke über alle eindeutigen Dateien;
- 8,55 MiB über alle eindeutigen Dateien;
- größte Datei und höchster Dreiecksstand: Dreifach-Socket-Coupon, 13.066 Dreiecke, 2,28 MiB;
- größte Ausdehnung eines Druckteils: 280 mm;
- alle Dateien: genau eine Komponente, wasserdicht, konsistente Orientierung, positives Volumen;
- alle Dateien: null Randkanten, null nichtmannigfaltige Kanten, null degenerierte und null doppelte Flächen;
- alle Dateien passen bei erlaubter Achsendrehung in 420 × 420 × 500 mm.

Die erhöhte Netzauflösung der Kugel- und Socket-Coupons ist beabsichtigt, damit der Toleranztest nicht durch grobe Facetten verfälscht wird. OpenSCAD bleibt der editierbare Master; es wird kein zweites vereinfachtes Mesh erzeugt.

## Budgets

| Budget | Grenzwert | Ist |
|---|---:|---:|
| Dreiecke je STL | 100.000 | max. 13.066 |
| Dateigröße je STL | 20 MiB | max. 2,28 MiB |
| Komponenten je STL | genau 1 | 1 |
| Bauraum | 420 × 420 × 500 mm, Achsendrehung erlaubt | max. Ausdehnung 280 mm |
| exakte Slicerzeit | noch festzulegen | `NOT_RUN` |
