# Monolithische geometrische Haarspange – Revision 2

Dieses Paket enthält eine einteilige, metallfreie Haarspange aus PETG, abgeleitet aus `concept-v2.png` und der beigefügten Anforderungsliste. Die sichtbare Schale übernimmt die kantige, segmentierte „Armor“-Formensprache. Die im Bild nicht eindeutig definierte Innenseite wurde funktional als Kamm, C-Flexur und federnde Rastzunge konstruiert.

Status: **experimenteller, digital validierter Prototyp**. Die Geometrie ist manifold/wasserdicht; Flexur, Rastung, Komfort und Dauerhaltbarkeit müssen mit dem realen Filament und Druckprofil getestet werden.

## Wichtigste Dateien

- `output/masculine-geometric-hair-clip-r2.3mf` – bevorzugte Druckdatei, Einheit Millimeter
- `output/masculine-geometric-hair-clip-r2.stl` – universelle Druckdatei
- `output/hair-clip-latch-coupon-r2.stl` – kleiner Rast-/Flexurtest vor dem Gesamtdruck
- `hair_clip.mjs` – parametrischer, reproduzierbarer Quellcode
- `design-spec.yaml` – freigegebene Anforderungen und Akzeptanzkriterien
- `validation/validation-report.md` – digitale Prüfergebnisse und offene physische Tests

## Abmessungen und Material

- Außenmaß: ca. 60,6 × 24,1 × 22,0 mm
- gezahnte Greifzone: ca. 34,2 mm
- Schalenstärke: 2,4 mm
- Flexur und Rastzunge: 1,6 mm
- berechnetes Volumen: ca. 9,37 cm³
- geschätzte Masse in PETG: ca. 11,90 g
- ein zusammenhängender Körper, keine Kaufteile

## Empfohlener Druckstartpunkt

- Material: ungefülltes PETG; kein PETG-CF/GF für die Flexur verwenden
- Düse: 0,4 mm
- Schichthöhe: 0,20 mm
- Linienbreite: etwa 0,45 mm gemäß kalibriertem Druckerprofil
- Wände: 4
- Deck-/Bodenschichten: 6 / 6
- Infill: 25 % Gyroid oder Cubic
- Support: aus
- Geschwindigkeit als konservativer Start: 45 mm/s
- Temperatur, Kühlung und Trocknung: Profil des konkreten Filamentherstellers verwenden
- Naht: nicht an Flexurwurzeln oder Zahnspitzen platzieren
- optional 3–5 mm Brim, falls die Seitendruckfläche nicht sicher haftet

Die Datei ist bereits für den Seitendruck orientiert: die große Funktionsseite liegt bei `Z = 0` auf dem Druckbett. Untere Schiene, Zähne, Flexur, Rastzunge und Anschlag beginnen auf dieser Ebene. Die Armor-Paneele besitzen nur kurze Reliefüberstände bis 0,9 mm; trotzdem muss die Layer-Vorschau im verwendeten Slicer kontrolliert werden.

## Test- und Benutzungsablauf

1. Zuerst `hair-clip-latch-coupon-r2.stl` mit exakt demselben PETG, Profil und derselben Orientierung drucken.
2. Coupon entgraten und 50-mal betätigen. Bei Weißbruch, Rissen oder bleibender Verformung den Vollclip nicht drucken.
3. Vollclip drucken und alle Haar-/Hautkontaktkanten vorsichtig entgraten. Zahnspitzen dürfen nicht scharf sein.
4. Zum Schließen die untere Kammschiene zur Schale drücken, bis die Rastzunge unter dem Fanghaken einrastet.
5. Zum Öffnen die kleine Rastzunge in Richtung Scharnier drücken und die Kammschiene kontrolliert absenken.
6. Zunächst nur kurz tragen. Der Clip gilt erst als akzeptiert, wenn er 30 Minuten hält, ohne schmerzhaft zu ziehen oder Druckstellen zu verursachen.

## Parametrisch neu erzeugen

Voraussetzung ist eine aktuelle Node.js-Version.

```bash
npm ci
npm run build
npm test
```

Die zentralen Werte stehen am Anfang von `hair_clip.mjs` in `DEFAULTS`. Für eine weichere Flexur zuerst `flexureBandWidth` in kleinen Schritten reduzieren; `flexureThickness` bleibt wegen der freigegebenen Mindeststärke bei mindestens 1,6 mm. Nach jeder Änderung `npm test` ausführen und erneut einen Coupon drucken.

## Grenzen

- Das Konzeptbild ist eine einzelne perspektivische Darstellung ohne Maßstab oder Rückansicht. Das Modell ist daher eine funktionale Interpretation, keine messtechnische Replik.
- Die linearen Balkenrechnungen bilden große gekrümmte Verformungen, FDM-Anisotropie, PETG-Kriechen und Ermüdung nicht vollständig ab.
- Es wurde kein exaktes Anycubic-Slicerprofil ausgeführt. Ein Layer-für-Layer-Dry-Run bleibt erforderlich.
- Filamentmarketing allein belegt keine Haut- oder Medizinverträglichkeit. Bei Irritationen nicht weiterverwenden.
