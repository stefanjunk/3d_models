# Digitaler Validierungsbericht – R1.3 aspect-safe 0,30 mm DRAFT

Datum: 2026-08-12  
Status: **digital PASS; physisch und druckerspezifisch noch nicht qualifiziert**

## Ergebnis

R1.3 behält die freigegebene R1-Geometrie, die kontinuierliche signierte Reliefabbildung, den Ein-Befehl-Bildwechsel und die speichereffiziente 0,30-mm-Geometrieabstastung bei. Korrigiert wurde die R1.2-Streckung nichtquadratischer Ersatzbilder: natürliche Quadratpixel-Seitenverhältnisse bleiben jetzt in physischen Millimetern invariant.

Alle neun STL-Dateien sowie die neue gestreamte 3MF bestehen die digitalen Prüfungen. Ein echter Slicer oder physischer Druck wurde in dieser Umgebung nicht ausgeführt.

## Ein-Befehl-Rebuild

```bash
python3 rebuild.py /pfad/zur/neuen-textur.png
```

Der Befehl liest alle weiteren Werte aus `relief/organizer/relief-job.json`, `config/relief-config.json` und `config/model-params.json`. Er registriert die Quelle, berechnet Repeat-Fit zuerst in Millimetern, erzeugt 16-Bit-Build-Map/Vorschau/Metadaten, prüft den physischen Aspekt und die 20-mm-Kreis-/Quadratdiagnose, baut Manifest/Geometrie, repariert nur kollabierte Float32-Mikrokanten, streamt die 3MF, validiert die Exporte und schreibt das Revisions-ZIP. Source- und Build-Hashes verhindern einen stillen Rebuild mit einem veralteten Bild.

## Tonwert-, PPI- und Reliefübertragung

| Stufe | Raster | Pitch / PPI | Unterschiedliche Werte | Status |
|---|---:|---:|---:|---|
| registrierter Quellmaster | 1536 × 1024 | 0,1171875 mm / 216,75 PPI isotrop | 16-Bit-Container; 8-Bit-Quellpräzision | registriert |
| Fertigungs-Zielmap | 900 × 900 | 0,20 mm / 127 PPI | 180 × 180 mm Zielbereich | PASS |
| extrahierte Wiederholkachel | 900 × 600 | 0,20 mm / 127 PPI | 46.214 uint16 | PASS |
| Geometriemanifest | 601 × 401 | 0,30 mm / 84,67 PPI | 39.402 uint16 | PASS |
| STL-Bodenband je Modul | Float32 | – | 138.901–190.705 Z-Werte | PASS |

Das Manifest enthält 241.001 kontinuierliche 16-Bit-Samples. Median 25.214 ist neutral; dunklere Werte werden proportional bis 0,50 mm graviert, hellere proportional bis 0,55 mm erhaben. Es existieren keine Schwellwerte, Tiefenklassen, Rasterläufe oder bewusste Höhenquantisierung. Binär-STL schreibt Koordinaten normbedingt als IEEE-754 Float32; unmittelbar benachbarte numerische Werte können dadurch zusammenfallen.

Die 900 × 900-Build-Map wird unabhängig vom 0,30-mm-Manifold-Backend erhalten. Ihr physischer Maßstab, Pitch, PPI, Pixelgröße, Bit-Tiefe, Fit, Gamma, Polarität, Surface-Mapping und Quellhash stehen in `relief/organizer/build/current-heightmap.png.json`. Für die Geometrie wird daraus die exakt periodische 900 × 600-Quellkachel extrahiert; nach der 7-mm-Nahtüberblendung beträgt deren gemessene X/Y-Randabweichung exakt 0.

## Physisches Seitenverhältnis

`steel1.png` besitzt 1536 × 1024 Quadratpixel und damit den natürlichen Aspekt 1,5. Mit dem konfigurierten 180-mm-Breitenanker wird die Quelle als 180 × 120 mm registriert. Die Repeat-Kachel misst 900 × 600 Pixel bei 0,20 mm/Pixel; Quell-, platzierter und rekonstruierter physischer Aspekt betragen jeweils exakt 1,5. Metadatenfehler: **0,000000 %**, Toleranz: 1,5 %, `aspect_policy=preserve`, Achsenstreckung: false.

Der separate 20-mm-Diagnosetest läuft vor jeder Geometrieerzeugung durch dieselbe Raster-/0,30-mm-Geometriepipeline. Gemessen wurden 19,8 × 20,1 mm für Quadrat und Kreis; Kreiselliptizität 1,493 %, PASS. `stretch` oder eine explizit falsch proportionierte Wiederholkachel bricht vor dem Modulbuild ab. Nachweise: `aspect-diagnostic.json` und `current-heightmap.png.json`.

Maschineller Nachweis: `continuous16-validation.json`.

## Speicherbedarf bei 0,30 mm

| Isolierter Node/WASM-Prozess | Peak-RSS |
|---|---:|
| driver-front | 1.276,1 MiB |
| driver-back | 1.494,6 MiB |
| hardware-front | 2.084,0 MiB |
| hardware-back | 1.929,3 MiB |
| Zubehör | 216,1 MiB |

Der echte Worst Case ist **2.083,953 MiB = 2,035 GiB = 2,185 GB dezimal**. Die Werte stammen aus `process.resourceUsage().maxRSS` jedes frisch gestarteten Prozesses. 4 GB verfügbarer RAM sind die praktische Untergrenze; 8 GB Gesamt-RAM geben bessere Reserve für Betriebssystem und Slicer.

Speichersenkende Änderungen:

- ein Modul pro Prozess;
- ein Reliefpatch pro Boolean-Stufe statt aller Boden-/Wandpatches gleichzeitig;
- blockweiser STL-Export ohne JS-Dreiecksobjektliste;
- reparierte indexierte Mesh-Caches;
- direkt gestreamtes 3MF-ZIP/XML;
- ein unabhängiger Validatorprozess pro STL.

## Baugruppe und Materialreserve

| Merkmal | Ergebnis | Status |
|---|---:|---|
| Baugruppenhülle | 227 × 357 × 64 mm | PASS |
| größter Druck-Footprint | 135 × 186,5 mm | PASS für 220 × 220 mm |
| Hardwarefächer | 8, angeordnet 2 × 4 | PASS |
| U-Griffnuten | 8 Stück, 22 × 8 mm, Radius 4 mm | PASS |
| Boden / Wand | 2,6 / 3,2 mm | PASS |
| maximale Gravur / Erhöhung | 0,50 / 0,55 mm | PASS |
| Restboden unter maximaler Gravur | 2,10 mm | PASS ≥ 2,0 mm |
| Reststärke doppelseitige Trennwand | 2,20 mm | PASS ≥ 2,0 mm |
| Reststärke Innen-/Außenwand | 2,20 mm | PASS ≥ 2,0 mm |

Eine Wandverdickung ist bei den freigegebenen Tiefen nicht erforderlich. Emboss ist Bestandteil der signierten Abbildung und stellt für helle Nieten/Patchkanten bis 0,55 mm zusätzliche Höhe bereit.

## Netzprüfung

Prüfer: `src/validate_stl.py`, exaktes Float32-Vertex-Matching.

| Datei | Größe mm | Dreiecke | Ergebnis |
|---|---:|---:|---|
| driver-front | 100 × 186,5 × 64 | 1.274.694 | PASS |
| driver-back | 100 × 178,5 × 64 | 1.258.794 | PASS |
| hardware-front | 135 × 186,5 × 64 | 1.865.820 | PASS |
| hardware-back | 135 × 178,5 × 64 | 1.629.914 | PASS |
| Schraubendreherkamm | 84 × 10 × 20 | 612 | PASS |
| Eckcoupon | 40 × 40 × 12 | 100 | PASS |
| Reliefcoupon | 90 × 32 × 3,1172 | 104.790 | PASS |
| Connector männlich | 28 × 20 × 2,6 | 152 | PASS |
| Connector weiblich | 20 × 20 × 2,6 | 144 | PASS |

Für jede Datei: 0 Randkanten, 0 nicht-manifold Kanten, 0 inkonsistent orientierte Kanten, 0 Nullflächendreiecke, 0 doppelte Flächen, genau ein zusammenhängender Körper und positives Volumen.

Beim Float32-Export kollabierte eine mikroskopische Kante in `hardware-front`. `src/repair_stl.py` zog sie lokal zusammen und entfernte zwei flächenlose Dreiecke. Driver-front, Driver-back, Hardware-back und Reliefcoupon benötigten keine Änderung. Die reparierten indexierten Caches sind auch die Quelle der 3MF.

## 3MF

`DRAFT-R1.3-aspect-safe-030mm-assembly.3mf` enthält vier benannte Modellobjekte und vier Build-Items im 3MF-Core-Namensraum. ZIP-CRC und Core-Namespace sind PASS; die Hülle ist exakt 227 × 357 × 64 mm. Die Model-XML wurde direkt aus den indexierten Mesh-Caches in den ZIP-Stream geschrieben, nicht als vollständiger Speicherbaum aufgebaut.

## Noch offene Nachweise

- echte Slicer-Vorschau von Reliefbahnen, 3,2-mm-Wandfüllung, U-Nuten und Unterseitenkennzeichnung;
- Reliefcoupon in PETG mit 0,4-mm-Düse und 0,20-mm- beziehungsweise optional 0,12-mm-Schichten;
- reale Schubladenpassung und Connector-Coupon;
- optional ein Hardware-Probedruck zur Beurteilung von Reliefwirkung, Reinigung und Wandknoten.

Ohne diese Nachweise und die abschließende Nutzerfreigabe bleibt der Stand korrekt als `DRAFT` gekennzeichnet.
