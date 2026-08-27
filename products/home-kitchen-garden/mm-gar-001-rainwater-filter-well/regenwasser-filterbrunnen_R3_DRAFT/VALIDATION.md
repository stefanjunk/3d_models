# Validierungsbericht · Revision 3 DRAFT

## Digital bestanden

- parametrischer Build mit Replicad 0.23.1 und OpenCascade-WASM 0.23.0;
- 17 druckbare Teiltypen und eine 14-Komponenten-Montagebaugruppe exportiert;
- 17/17 binäre STL unabhängig geprüft: jeweils ein zusammenhängender Körper, keine degenerierten Dreiecke, keine offenen oder nichtmanifold Kanten, positive Orientierung und konsistente Normalen;
- B-Rep-/Mesh-Volumendifferenz je Teil unter 1 %;
- jedes Teil innerhalb 410 × 410 × 490 mm reserviertem Nutzraum;
- montierte Höhe 851 mm, Stand-Ø 330 mm, Stellfläche mit Kaskade 330 × 406 mm;
- R3-Schnittstellenprüfung 11/11 PASS: 15,0-mm-Luftspalt, 41,0-mm-Düsenüberdeckung, 10,0-mm-Schlammspalt, DN25-Ablässe, 5,02° Boden und 18,72-mm-Lamellenabstand;
- analytische Einlaufreserve bei 1.200 L/h: 9,63 mm bis zum Becher-Notüberlauf unter dokumentierten Annahmen;
- Kennzeichnung auf allen drei Primärgehäusen: Originalasset JSI-WM-001-R1, 17,1349 × 15,0 mm, 0,40 mm tief, Bett-Datum unverändert, Restwand 5,60 mm;
- vollständige STL- und Schnittstellenregression nach Kennzeichnungsintegration bestanden.

Detaillierte Nachweise:

- `build/draft-r3/metadata/stl-validation.md`
- `build/draft-r3/metadata/engineering-validation.md`
- `build/draft-r3/metadata/geometry-metadata.json`
- `build/draft-r3/metadata/candidate-hash.json`

Exakter Mesh-Satz SHA-256: `c5c05d02a42d5b124e874f58f9e567a41fbc67b26e1183eadf1f24843f717bc7`.

## Fertigungsprüfung

| Thema | Ergebnis | Grenze |
|---|---|---|
| Bauraum | PASS | geometrische Hülle, kein Maschinen-G-Code |
| gespeicherte Druckorientierung | PASS mit lokalen Stützen | Stützerreichbarkeit im konkreten Slicer offen |
| Einlaufbecher-Stützring | CAD-seitig druckbar mit Stützen | 278-mm-Ring etwa 50 mm über Bett ist der kritischste Slicerpunkt |
| Wasserwand / Basis | 4,8 / 6,0 mm | reale Porosität und Warping unbekannt |
| M5/M6/M8-Bohrungen | geometrisch vorhanden | Schrumpfung physisch prüfen |
| 1,7-mm-Stapelspiel / 1,8-mm-Becherspiel | geometrisch vorhanden | Großteil-Warping kann Spiel aufzehren |
| Materialbedarf | etwa 10,55 kg vollständiger Satz | Stützen und Ausschuss fehlen |
| Slicer-Dry-Run | BLOCKIERT | kein konkreter Maschinen-Slicer in der Ausführungsumgebung |

## Hydraulik und Sicherheit

Die R3-Wasserwege und Mindestabstände sind analytisch plausibilisiert. Die Rechnung verwendet für den Einlauf `Cd=0,62`; zusätzliche reale Verluste können die 9,63-mm-Reserve verringern. Es wurden weder CFD noch physische Wasser-, Trübungs-, Dichtheits-, Schlamm-, Dauer-, UV-, Frost- oder Kippversuche durchgeführt.

Das System bleibt offen und drucklos. Der 15-mm-Luftspalt und der freie Becherüberlauf dürfen nicht verschlossen werden. Die beiden DN25-Ablässe werden nur bei gestoppter Pumpe geöffnet.

## Kennzeichnungsgate

STL-Unterseitenansicht, bemaßte Nahansicht, parametrischer Schnitt, geometrische Schichtkonturen und aktualisierte Mesh-/B-Rep-Regression sind vorhanden. Ein echter Slicer-Toolpath-Blick der ersten Lagen fehlt. Deshalb bleibt die finale Kennzeichnungs- und Modellfreigabe blockiert.

## Offene Freigabepunkte

1. konkretes Druckerprofil wählen und alle 17 Teile slicen;
2. Einlaufbecher-Stützen, Tangentialauslass, DN25-Ports und Kennzeichnungslagen visuell prüfen;
3. Coupon-, Pass-, Dichtheits-, Niedrigfluss-, Maximalfluss-, Rückfluss-, Schlamm-, Notüberlauf- und Kippprüfungen durchführen;
4. Ergebnisse dokumentieren und Kennzeichnung ausdrücklich freigeben;
5. erst danach finale Modellfreigabe und Exporte ohne DRAFT-Kennzeichnung erzeugen.
