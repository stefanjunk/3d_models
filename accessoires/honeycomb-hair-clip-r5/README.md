# Monolithische Waben-Haarspange – Revision 5

Dieses Paket enthält Revision 5 der einteiligen, metallfreien PETG-Haarspange. Die vollständigen Waben bilden jetzt am Gelenk und am Clip dieselbe gestufte Hoch-Tief-Endkontur. Die Rastmechanik bleibt unter der dekorativen Clip-Endwabe frei und unverändert.

Status: **experimenteller, digital validierter Prototyp**. STL und 3MF sind geometrisch bestanden. Flexur, Rastung, Komfort und Dauerhaltbarkeit müssen mit dem realen PETG und Druckprofil geprüft werden.

## Wichtigste Dateien

- `output/masculine-honeycomb-hair-clip-r5.3mf` – bevorzugte Druckdatei in Millimetern
- `output/masculine-honeycomb-hair-clip-r5.stl` – universelle Druckdatei
- `output/hair-clip-latch-coupon-r5.stl` – Rast-/Flexurtest vor dem Gesamtdruck
- `hair_clip.mjs` – parametrischer, reproduzierbarer Manifold-3D-Quellcode
- `design-spec.yaml` – freigegebene Anforderungen und Akzeptanzkriterien
- `validation/validation-report.md` – digitale Prüfergebnisse und offene physische Tests
- `renders/r5-overview.png` – freigegebenes Konzept und aktuelle CAD-Ansichten

## Revision-5-Geometrie

- Außenmaß: ca. 64,93 × 24,15 × 26,60 mm
- strukturelle Grundbreite: 22,0 mm
- 17 Wabenzellen in fünf versetzten Reihen mit der Zellfolge 3 / 4 / 3 / 4 / 3
- davon 14 vollständige Hexagone und 3 an der Druckebene halbierte Hexagone
- äußerste Nicht-Bett-Reihe: 3 vollständige Hexagone mit gestufter Hoch-Tief-Kontur
- Hexagon-Schlüsselweite: 10,0 mm
- nominale reale Fuge zwischen Nachbarzellen: 0,8 mm
- identischer Wabenüberstand über Schalenanfang und -ende: je 6,47 mm
- kontrollierte Längsskalierung des Rasters: 95,7 %, damit die vollständigen Endwaben innerhalb 65 mm bleiben
- Armor-Erhöhung über der Schale: 0,9 mm
- mittlere Breite der verschlankten unteren Schiene: 12,5 mm
- volle Schienenbreite an Gelenk und Rastclip: 22,0 mm
- Schalenstärke: 2,4 mm; Flexur und Rastzunge: 1,6 mm
- Volumen: ca. 8,47 cm³; geschätzte PETG-Masse: ca. 10,76 g

Alle Zellen haben dieselbe Orientierung. Das Raster verwendet für 10-mm-Zellen und 0,8-mm-Fugen die korrekten Gitterabstände; die Fugen werden nicht durch überlappende Nachbarzellen zugeschmolzen. Nur die Reihe an `Z = 0` wird durch die Druckebene halbiert. Die Zellen der gegenüberliegenden Außenreihe bleiben vollständig und reichen bis `Z = 26,6 mm`.

Die früheren Schulterblöcke sind entfallen. Stattdessen läuft der 2,4-mm-Schalenbogen dünn bis in Gelenk- und Fangzone weiter. Je zwei vollständige Waben der versetzten Reihen kragen an beiden Enden aus und erzeugen eine spiegelgleiche Stufenkontur. Kamm, Rastzunge, Entriegelungszugang, Hartanschlag und Flexurprinzip bleiben erhalten.

## Empfohlener Druckstartpunkt

- Material: ungefülltes PETG; kein PETG-CF/GF für die Flexur
- Düse: 0,4 mm
- Schichthöhe: 0,20 mm
- Linienbreite: etwa 0,45 mm gemäß kalibriertem Profil
- Wände: 4
- Deck-/Bodenschichten: 6 / 6
- Infill: 25 % Gyroid oder Cubic
- Support: zunächst aus; Layer-Vorschau kontrollieren
- Geschwindigkeit als konservativer Start: 45 mm/s
- Temperatur, Kühlung und Trocknung: Profil des konkreten Filamentherstellers
- Naht: nicht an Flexurwurzeln, Zahnspitzen oder Wabenfugen platzieren
- optional 3–5 mm Brim, falls die Seitendruckfläche nicht sicher haftet

Das Modell ist bereits für den Seitendruck ausgerichtet und beginnt bei `Z = 0`. Kamm, Flexur, Rastzunge und die drei halben Bettzellen werden direkt vom Druckbett aufgebaut. Die 0,8-mm-Fugen und die gestufte Nicht-Bett-Kante müssen im realen Anycubic-Slicerprofil Schicht für Schicht geprüft werden.

## Test- und Benutzungsablauf

1. Zuerst `hair-clip-latch-coupon-r5.stl` mit exakt demselben PETG, Profil und derselben Orientierung drucken.
2. Coupon entgraten und 50-mal betätigen. Bei Weißbruch, Rissen oder bleibender Verformung den Vollclip nicht drucken.
3. Im Slicer besonders die 0,8-mm-Fugen, die drei halben Bettzellen und die vollständige äußere Wabenreihe kontrollieren.
4. Vollclip drucken und alle Haar-/Hautkontaktkanten vorsichtig entgraten. Zahn- und Hexagonspitzen dürfen nicht scharf sein.
5. Zum Schließen die untere Kammschiene zur Schale drücken, bis die Rastzunge unter dem Fanghaken einrastet.
6. Zum Öffnen die Rastzunge in Richtung Gelenk drücken und die Kammschiene kontrolliert absenken.
7. Zunächst kurz tragen. Akzeptiert ist der Clip erst nach 30 Minuten Halt ohne schmerzhaftes Ziehen oder Druckstellen.

## Parametrisch neu erzeugen

Voraussetzung ist eine aktuelle Node.js-Version.

```bash
npm ci
npm test
```

Die zentralen Werte stehen am Anfang von `hair_clip.mjs` in `DEFAULTS`. `armorAcrossFlats`, `armorGap`, `armorRise`, `armorLongitudinalScale` und `railCentralWidth` steuern die wesentlichen Revisionsmerkmale. Nach jeder Geometrieänderung `npm test` ausführen und Rast-/Flexurtests wiederholen.

## Grenzen

- Die Vorlage bleibt eine perspektivische Konzeptdarstellung ohne kalibrierten Maßstab oder Rückansicht; das Modell ist eine funktionale Interpretation.
- Die linearen Balkenrechnungen bilden große gekrümmte Verformungen, FDM-Anisotropie, PETG-Kriechen und Ermüdung nicht vollständig ab.
- Ein exakter Anycubic-Slicer-Dry-Run und realer Testdruck wurden nicht durchgeführt.
- Filamentmarketing allein belegt keine Haut- oder Medizinverträglichkeit. Bei Irritationen nicht weiterverwenden.
