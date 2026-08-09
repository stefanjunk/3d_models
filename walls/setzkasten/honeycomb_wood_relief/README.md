# Waben-Setzkasten mit druckgerechtem Holzrelief

Dieses Projekt ergänzt den bestehenden CadQuery-Waben-Setzkasten um eine echte,
in das STL eingravierte Holzoberfläche aus `../holz.png`. Maße sind in Millimetern.

## Methodenentscheidung

**Bewusster Hybrid: CadQuery-B-Rep + adaptiv verfeinertes Oberflächenmesh.**

- CadQuery bleibt die exakte Quelle für Wabenkontur, Wandstärke, Aufhängung,
  Schwalbenschwanz-Nuten und Verbinder. Die STEP-Dateien sind die editierbaren
  Konstruktionsmaster.
- Die Bildgravur wird ausschließlich in der tessellierten STL-Ableitung erzeugt.
  Nur sichtbare Texturzonen werden mit einem kantenkonformen, adaptiven Netz bis
  zur düsengerechten Zielkante verfeinert; gemeinsame Kanten bleiben gemeinsam.
- Eine globale feste Unterteilung wie in V4 ist ungeeignet: sechs Stufen erzeugten
  14.221.312 Dreiecke bzw. rund 679 MiB für eine einzelne Wabe.
- Ein vollständiges 3D-Voxelfeld ist ebenfalls unnötig und speicherintensiv. Bei
  circa 231 x 201 x 55 mm und 0,20 mm Voxeln wären schon etwa 320 Mio. Voxel nötig,
  also rund 1,3 GB für nur ein `float32`-Feld und deutlich mehr mit Zwischenfeldern.
  Das Relief ist eine reine Oberflächenoperation, daher ist das adaptive Mesh die
  kleinste ausreichende Methode.

Der STEP-Master und das texturierte STL sind absichtlich nicht geometrisch
identisch: STEP enthält die präzise glatte Funktion, STL zusätzlich das Relief.

## Druckgerechte Auflösung

- Düse: 0,4 mm
- angenommene Linienbreite: 0,45 mm
- Schichthöhe: 0,20 mm
- kleinste beabsichtigte Holzstruktur: 1,2 mm
- finale maximale Netzkante in Texturzonen: 1,00 mm
- Vorschau-Netzkante: 2,00 mm
- maximale Gravur: 0,45 mm an Seiten, 0,35 mm an der vorderen Stirnfläche
- die Heightmap wird vor der Gravur tiefpassgefiltert; feinere Bilddetails als
  Düse und Netzkante werden bewusst nicht nachgebildet.

Die inneren und äußeren Seiten werden nur von z=1,2 bis z=33,0 mm texturiert.
Damit bleiben die rückseitigen Verbinder-Nuten ab z=35 mm sowie Aufhängungen
unverändert. Übergänge werden über 1,2 mm ausgeblendet. Die Rückseite bleibt glatt.

## Autoritative Parameter und Annahmen

Alle Werte stehen in `parameters.json`. Wesentliche Annahmen:

- PETG, 0,4-mm-Düse, 0,20-mm-Schichten, Bauraum 256 x 256 x 256 mm
- Druckorientierung: vordere Wabenkante bei z=0 auf dem Druckbett
- Nennwand 4,5 mm; bei gleichzeitig maximaler Innen-/Außengravur verbleiben
  rechnerisch mindestens 3,6 mm
- Verbinder-Spiel: 0,25 mm je Seite; für den realen Druck ist ein Passcoupon nötig
- Die runden Aufhängebosse überlappen die Innenwand direkt. Die fehlerhaft um den
  globalen Ursprung rotierten Hilfsbrücken des Ausgangsskripts werden lokal nicht erzeugt.
- Last wirkt bei Wandmontage überwiegend in der Wandebene nach unten. Schrauben,
  Dübel, Wand, Materialkriechen und Verbinder benötigen einen physischen Lasttest.

## Akzeptanzkriterien

1. CadQuery-B-Rep gültig, genau ein Solid je Wabe, STEP erfolgreich neu geladen.
2. Nennabmessungen der glatten Wabe ungefähr 200 x 229,70 x 55 mm.
3. Jedes exportierte STL wird von Datenträger neu geladen: wasserdicht,
   konsistente Orientierung, ein Körper, positives Volumen, keine degenerierten
   oder gebrochenen Flächen.
4. Relief greift nicht in Verbinder-Nuten, Aufhängungen oder die rückseitigen
   20 mm ein; texturierte Außenmaße überschreiten den glatten Master nicht.
5. Pro texturierter Wabe höchstens 1.500.000 Dreiecke und höchstens 80 MiB STL.
6. Mehrwinkelansichten und Detailansicht zeigen erkennbare Holzmaserung ohne
   offene Nähte oder grobe Facetten.
7. Automatische FDM-Prüfung besteht für die dokumentierten Annahmen. Eine echte
   Slicer-Lagenansicht und ein physischer Testdruck bleiben erforderlich.

## Struktur

```text
parameters.json               autoritative Maße und Fertigungsannahmen
source/generate.py            CadQuery-Master, Heightmap und adaptive Gravur
source/render_previews.py     reproduzierbare Mehrwinkel-Renderings
exports/                      STEP-Master, glatte und texturierte STL-Ableitungen
previews/                     Heightmap, Vorschau-STL und PNG-Ansichten
reports/                      CAD-, Mesh-, Ressourcen- und FDM-Nachweise
```

## Reproduktion

```bash
python3 source/generate.py --quality preview --variant plain
python3 source/generate.py --quality final --variant both
python3 source/render_previews.py
```

Die Quelle `../holz.png` wird direkt eingelesen und per SHA-256 im Bericht
protokolliert. Das Originalbild wird nicht verändert.

## Validiertes Ergebnis

- Holzrelief-STL ohne Aufhängung: 630.400 Dreiecke, 30,06 MiB.
- Holzrelief-STL mit Aufhängung: 662.516 Dreiecke, 31,59 MiB.
- Gemessene Ausdehnung beider Varianten: 199,9999 x 229,7024 x 55,0 mm.
- STEP-Neuladen, Mesh-Prüfungen und automatische FDM-Prüfungen: **PASS**.
- Gesamturteil: **CONCERNS**, weil kein Slicer installiert war und Pass-/Lasttests
  physisch erfolgen müssen. Details: `reports/design_report.md`.
