# Kennzeichnungsnachweis – R1.1 continuous16 DRAFT

## Auswahl und Integration

| Merkmal | Wert |
|---|---|
| Asset | `JSI-WM-001-R1` |
| Variante | compact |
| Operation | vertieft |
| Skalierung | 1,4 gleichförmig |
| tatsächliche DXF-Hülle | 15,991 × 14,000 mm |
| Tiefe | 0,40 mm |
| Ausgangsboden | 2,60 mm |
| Restboden | 2,20 mm |
| Relief-Keepout auf der Oberseite | 1,50 mm um die Markenhülle |
| Platzierung | druckbettseitige Unterseite aller vier Hauptmodule |
| separate Kamm-Markierung | nein; durch die markierte Baugruppe abgedeckt |

Die exakte gebündelte DXF-Geometrie wurde beim R1.1-Neuaufbau nach der kontinuierlichen 16-Bit-Reliefstufe erneut als letzte geplante Geometrieänderung eingebracht. Die Unterseite bleibt bei z = 0; die Kennzeichnung ist eine lokale Aussparung und verändert weder Einbauhülle noch Druckbett-Datum. Das Oberseitenrelief wird über der Kennzeichnung lokal ausgespart, sodass die Restbodenvorgabe auch bei der kontinuierlichen R1.1-Gravur eingehalten wird.

## Evidenz

- `watermark-underside.png` – direkte Ansicht der fertigen vier Unterseiten; Leserichtung nach dem Umdrehen des Druckteils
- `watermark-closeup.png` – dimensionierte Nahansicht und Sicherheitsfläche
- `watermark-section.png` – Querschnitt mit 0,40-mm-Tiefe und 2,20-mm-Restboden
- `watermark-layer-preview.png` – geometrische Schichtsimulation bei z = 0,10 / 0,30 / 0,50 mm
- `watermark-selection.json` – maschineller Profil-/Flächentest, Status PASS
- `build-final.json` – getrennte Vorher-/Nachher-Geometriestatistik
- `geometry-sha256.txt` – Prüfsummen der R1.1-DRAFT-Geometrie

## Einschränkung

Die Schichtdarstellung ist eine geometrische Simulation mit 0,20-mm-Schichten und 0,44-mm-Linienbreite, kein druckerspezifisch erzeugter G-Code. Der Kennzeichnungs-Freigabeschritt und damit die finale Modellfreigabe bleiben blockiert, bis die R1.1-3MF/STL in einem realen Slicer geprüft wurde.
