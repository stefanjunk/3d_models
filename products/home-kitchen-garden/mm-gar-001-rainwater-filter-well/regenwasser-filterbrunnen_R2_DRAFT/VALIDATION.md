# Validierungsbericht · Revision 2 DRAFT

## Digital bestanden

- parametrischer Build mit Replicad 0.23.1 und OpenCascade-WASM 0.23.0;
- 14 druckbare Teiltypen und eine 13-Komponenten-Montagebaugruppe exportiert;
- alle 14 binären STL unabhängig eingelesen und geprüft;
- 14/14 STL: ein zusammenhängender Körper, keine degenerierten Dreiecke, keine offenen oder nichtmanifold Kanten, positive Orientierung und keine widersprüchlichen gespeicherten Normalen;
- B-Rep-/Mesh-Volumendifferenz je Teil unter 1 %;
- jedes Teil innerhalb 410 × 410 × 490 mm reserviertem Nutzraum;
- montierte Höhe 816 mm, Stand-Ø 330 mm, Stellfläche mit Kaskade 330 × 406 mm;
- Kennzeichnung auf allen drei Primärgehäusen: Originalasset JSI-WM-001-R1, kompakt, 1,5×, 17,1349 × 15,0 mm, exakt 0,40 mm tief, Bett-Datum unverändert, Restwand 5,60 mm;
- vollständige Regression nach Kennzeichnungsintegration erneut bestanden.

Die detaillierten Messwerte stehen in `build/draft-r2/metadata/stl-validation.md` und `geometry-metadata.json`.

Exakter Mesh-Satz SHA-256: `c7c7fb09c676a8be4be187382f383bc95025949f6076b72a9f12fc1582ccf4ee`. Einzelhashes und der zeitstempelabhängige STEP-Satz stehen in `build/draft-r2/metadata/candidate-hash.json`.

## Fertigungsprüfung

| Thema | Ergebnis | Grenze |
|---|---|---|
| Bauraum | PASS | geometrische Hülle, kein Maschinen-G-Code |
| gespeicherte Druckorientierung | PASS mit lokalen Stützen | Stützerreichbarkeit muss im konkreten Slicer bestätigt werden |
| Wasserwand | 4,8 mm / mindestens sieben nominale Linien | reale Porosität unbekannt |
| Basis | 6,0 mm | reale Verformung/Haftung unbekannt |
| M5/M6/M8-Bohrungen | geometrisch vorhanden | Schrumpfung und Schraubenpassung physisch prüfen |
| 1,7-mm-radiales Stapelspiel | geometrisch vorhanden | Großteil-Warping kann es aufzehren |
| Materialbedarf | etwa 10,15 kg kompletter Satz | Slicer-Stützmaterial und Ausschuss fehlen |
| Slicer-Dry-Run | BLOCKIERT | kein FDM-Slicer in der Ausführungsumgebung installiert |

## Hydraulik und Sicherheit

Querschnitte, Lamellenfläche, Aufenthaltszeit, Notüberlauf und hydrostatische Größenordnung sind analytisch plausibilisiert. Es wurden weder CFD noch physische Wasser-, Trübungs-, Dichtheits-, Dauer-, UV-, Frost- oder Kippversuche durchgeführt. Filtermedienwiderstand ist ohne konkretes Produkt und Verschmutzungszustand nicht vorhersagbar.

## Kennzeichnungsgate

Vorhanden sind fertige STL-Unterseitenansicht, bemaßte Nahansicht, parametrischer Schnitt, geometrische Schichtkonturen und aktualisierte Mesh-/B-Rep-Prüfung. Nicht vorhanden ist der vorgeschriebene echte Slicer-Toolpath-Blick der ersten Lagen. Deshalb bleibt `workflow.watermark_approval.status` blockiert und es wird noch keine finale Modellfreigabe angefordert.

## Offene Freigabepunkte

1. offizielles Druckerprofil mit dem DRAFT-Profil zusammenführen und alle Teile slicen;
2. Kennzeichnungslagen und lokale Stützen visuell prüfen;
3. Coupon-, Pass-, Dichtheits-, Durchfluss-, Notüberlauf- und Kippprüfungen durchführen;
4. Ergebnisse eintragen und Kennzeichnung explizit freigeben;
5. erst danach finale Modellfreigabe und nicht als DRAFT bezeichnete Exporte erzeugen.
