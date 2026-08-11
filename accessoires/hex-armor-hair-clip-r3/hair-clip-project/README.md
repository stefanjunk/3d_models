# Monolithische Hexagon-Haarspange – Revision 3

Dieses Paket enthält die freigegebene Revision 3 der einteiligen, metallfreien PETG-Haarspange. Die rechteckigen Armor-Paneele aus Revision 2 wurden durch vollständige reguläre Hexagone ersetzt. Drei versetzte Reihen bedecken den oberen Bogen; eine zusätzliche, tangential ausgerichtete Reihe liegt auf der langen Seite gegenüber dem Druckbett. Die ungenutzte obere Zone der unteren Schiene wurde in der Mitte entfernt.

Status: **experimenteller, digital validierter Prototyp**. STL und 3MF sind geometrisch bestanden. Flexur, Rastung, Komfort und Dauerhaltbarkeit müssen mit dem realen PETG und Druckprofil geprüft werden.

## Wichtigste Dateien

- `output/masculine-hex-armor-hair-clip-r3.3mf` – bevorzugte Druckdatei in Millimetern
- `output/masculine-hex-armor-hair-clip-r3.stl` – universelle Druckdatei
- `output/hair-clip-latch-coupon-r3.stl` – unveränderter Rast-/Flexurtest vor dem Gesamtdruck
- `hair_clip.mjs` – parametrischer, reproduzierbarer Manifold-3D-Quellcode
- `design-spec.yaml` – freigegebene Anforderungen und Akzeptanzkriterien
- `validation/validation-report.md` – digitale Prüfergebnisse und offene physische Tests
- `renders/r3-overview.png` – Konzept- und CAD-Ansichten

## Revision-3-Geometrie

- Außenmaß inklusive vollständiger Panzerzellen: ca. 62,58 × 26,09 × 25,60 mm
- strukturelle Grundbreite: 22,0 mm
- 23 vollständige Hexagone auf dem oberen Bogen
- 8 vollständige Hexagone auf der Nicht-Druckbettseite
- Hexagon-Schlüsselweite: 8,0 mm
- nominale Rille: 0,8 mm
- Armor-Erhöhung: 0,9 mm
- mittlere Breite der verschlankten unteren Schiene: 12,5 mm
- volle Schienenbreite an Gelenk und Rastclip: 22,0 mm
- gezahnte Greifzone: ca. 34,2 mm
- Schalenstärke: 2,4 mm
- Flexur und Rastzunge: 1,6 mm
- berechnetes Volumen: ca. 9,40 cm³
- geschätzte Masse in PETG: ca. 11,94 g

Die vollständigen Randzellen enden nicht beschnitten. Dadurch ist die Armor-Hülle mit 25,6 mm breiter als der 22-mm-Strukturkörper. Die erste obere Reihe beginnt exakt bei `Z = 0`; die dritte Reihe wächst über die Nicht-Bettseite hinaus. Die Seitenzellen überlappen den Federbogen, bleiben aber von der Rastzungen-Freigabe entfernt.

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
- Naht: nicht an Flexurwurzeln, Zahnspitzen oder Rillen platzieren
- optional 3–5 mm Brim, falls die Seitendruckfläche nicht sicher haftet

Das Modell ist für den Seitendruck orientiert und beginnt bei `Z = 0`. Kamm, Flexur, Rastzunge und Anschlag werden direkt vom Bett aufgebaut. Die Hexagonreihe auf der Nicht-Bettseite erzeugt lokal kurze, etwa 2,8 mm auskragende Bereiche. Sie sind als supportfrei vorgesehen, müssen aber im realen Kobra-3-Max-Slicerprofil Schicht für Schicht geprüft werden.

## Test- und Benutzungsablauf

1. Zuerst `hair-clip-latch-coupon-r3.stl` mit exakt demselben PETG, Profil und derselben Orientierung drucken.
2. Coupon entgraten und 50-mal betätigen. Bei Weißbruch, Rissen oder bleibender Verformung den Vollclip nicht drucken.
3. Im Slicer besonders die 0,8-mm-Rillen, die vollständigen Randhexagone und die kurzen Seitenplatten-Auskragungen kontrollieren.
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

Die zentralen Werte stehen am Anfang von `hair_clip.mjs` in `DEFAULTS`. `armorAcrossFlats`, `armorGap`, `armorRise` und `railCentralWidth` steuern die Revision-3-Merkmale. Nach jeder Änderung `npm test` ausführen und Rast-/Flexurtests wiederholen.

## Grenzen

- Die Vorlage bleibt eine perspektivische Konzeptdarstellung ohne kalibrierten Maßstab oder Rückansicht; das Modell ist eine funktionale Interpretation.
- Die linearen Balkenrechnungen bilden große gekrümmte Verformungen, FDM-Anisotropie, PETG-Kriechen und Ermüdung nicht vollständig ab.
- Ein exakter Anycubic-Slicer-Dry-Run und realer Testdruck wurden nicht durchgeführt.
- Filamentmarketing allein belegt keine Haut- oder Medizinverträglichkeit. Bei Irritationen nicht weiterverwenden.
