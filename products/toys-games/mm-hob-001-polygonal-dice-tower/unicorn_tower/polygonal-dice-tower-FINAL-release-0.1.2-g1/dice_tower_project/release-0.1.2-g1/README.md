# Polygonaler Würfelturm

Finaler Stand: `0.1.2-g1` — verkürzte Kanalstutzen und JuSt-Innovation-Kennzeichnung freigegeben; das Fertigungsmesh ist digital validiert.

## Korrektur in 0.1.2-g1

- Der obere Einwurfstutzen ragt entlang seiner 45°-Achse nur noch `5,000 mm` sichtbar über die festgelegte Dachanschlussfläche hinaus.
- Der untere Auswurfkanal ragt nur noch `8,000 mm` über die festgelegte Turmwand-Anschlussfläche hinaus.
- Freier Einwurf-Ø 38 mm, 40 × 33 mm Auswurföffnung, 4-mm-Kanalwände und der vollständige Innenweg sind unverändert.

## Weiterhin gültige Korrekturen aus 0.1.1-g1

- Das Dachhorn ist ein expliziter Schutzbereich und bleibt unverändert.
- Der Einwurf ist ein runder, um 45° nach hinten-oben gerichteter Kanal mit 38 mm freiem Durchmesser und 4 mm Nennwand.
- Die Rückwand bleibt außerhalb der lokalen Einwurfzone unverändert.
- Der Auswurf ist ein sauberer 40-mm-Bogen mit kurzem, ausgekleidetem Kanal; innenliegende Rippen werden aus dem sichtbaren Tunnel ausgeschnitten.
- Der mittlere Hohlraum wurde von 61,85 mm auf 57,00 mm Durchmesser reduziert.
- Statt fünf gibt es drei versetzte, stützenarm konstruierte Fallstufen.

## Digitaler Prüfstand

- ein zusammenhängender, wasserdichter Körper
- 16.914 Dreiecke im finalen, gekennzeichneten Fertigungsmesh
- kleinste gemessene Zylinderwand: 5,926 mm
- Kanalwände: 4,0 mm; geschlossener Boden: mindestens 24,0 mm im Funktionsbereich
- 25-mm-Prüfwürfel: 94/94 digitale Posen bestanden
- Horn und Rückwand außerhalb der Editierbereiche innerhalb weniger Mikrometer zum Original erhalten
- Bauteilhülle: ca. 149,56 × 147,32 × 220,00 mm

Ein Slicer-Layercheck mit dem tatsächlich verwendeten Profil und physische Falltests mit den tatsächlich verwendeten Würfeln bleiben als reale Fertigungsnachweise erforderlich.

## Reproduzierbarer Build

Aus dem Projektverzeichnis:

```bash
npm ci
node scripts/build_dice_tower.mjs --parameters parameters/geometry-r0.1.2.json --quality final
node scripts/validate_dice_path.mjs --parameters parameters/geometry-r0.1.2.json
python3 scripts/validate_geometry.py --parameters parameters/geometry-r0.1.2.json
python3 scripts/render_geometry_review.py --parameters parameters/geometry-r0.1.2.json
python3 scripts/inspect_binary_stl.py result/polygonal-dice-tower-DRAFT-watermarked-0.1.2-g1.stl --require-watertight --max-components 1 --json reports/topology-DRAFT-watermarked-0.1.2-g1.json
python3 scripts/validate_watermark.py --parameters parameters/geometry-r0.1.2.json
python3 scripts/render_watermark_review.py --parameters parameters/geometry-r0.1.2.json
```

Das Originalmesh wird nicht überschrieben. Die reproduzierbaren Build-Ausgaben bleiben als DRAFT-Nachweise erhalten; die freigegebene, byteidentische Produktionskopie ist `result/polygonal-dice-tower-FINAL-0.1.2-g1.stl`. Das JuSt-Innovation-Wasserzeichen ist geometrisch validiert und vom Nutzer freigegeben.
