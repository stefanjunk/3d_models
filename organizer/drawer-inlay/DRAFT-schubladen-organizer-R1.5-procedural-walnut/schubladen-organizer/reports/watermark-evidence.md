# Kennzeichnungsnachweis – R1.5 Walnussstruktur DRAFT

## Integration

| Merkmal | Wert |
|---|---|
| Asset | `JSI-WM-001-R1` compact |
| Operation | 0,40 mm vertieft |
| Skalierung | 1,4 gleichförmig |
| tatsächliche Hülle | 15,993 × 14,000 mm |
| Ausgangs-/Restboden | 2,60 / 2,20 mm |
| Platzierung | druckbettseitige Unterseite aller vier Hauptmodule |
| Oberseiten-Keepout | 1,50 mm um die Markenhülle |
| separater Kamm | durch markierte Baugruppe abgedeckt |

Die exakte gebündelte DXF-Geometrie wurde als letzte geplante Solid-Änderung geschnitten. Es entsteht keine Geometrie unter z = 0; umliegende Bettauflage, Einbauhülle und Textur-Keep-outs bleiben unverändert.

## Evidenz

- `watermark-underside.png` – direkte fertige Unterseitenansicht
- `watermark-closeup.png` – Maße und Sicherheitsfläche
- `watermark-section.png` – Tiefe und Restboden
- `watermark-layer-preview.png` – geometrische Schichtsimulation
- `watermark-selection.json` – Profil-/Flächentest
- `build-final.json` und `geometry-sha256.txt` – Produktionsgeometrie und Hashes

## Gate

Digitale Geometrie und Restboden bestehen. Die Schichtdarstellung ist keine druckerspezifische G-Code-Vorschau; das Kennzeichnungs- und Final-Release-Gate bleibt bis zur Prüfung im exakten Ziel-Slicer und ausdrücklichen Freigabe blockiert.
