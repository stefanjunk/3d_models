# Digitale Validierung – JSI-WM-001-R1

Status: **bestanden; physischer Test ausstehend**  
Validiert: 2026-08-10T17:04:41.521Z

| Geometrie | B-Rep gültig | STL-Dreiecke | Randkanten | Nicht-manifold Kanten | B-Rep/Netz-Volumendifferenz |
|---|---:|---:|---:|---:|---:|
| just-innovation-compact-cutter-10af-d040 | ja | 920 | 0 | 0 | 0.0257 % |
| just-innovation-standard-cutter-32x10-d040 | ja | 4896 | 0 | 0 | 0.0226 % |
| just-innovation-trace-suffix-48x10-26A1-d040 | ja | 6388 | 0 | 0 | 0.0191 % |
| just-innovation-trace-full-60x10-JSI-26A1-d040 | ja | 7608 | 0 | 0 | 0.0198 % |
| just-innovation-depth-size-test-coupon | ja | 18624 | 0 | 0 | 0.0141 % |

## Bestandene Prüfungen

- OpenCascade-BRep-Prüfung für alle fünf STEP-Geometrien.
- Geschlossene, orientierte STL- und 3MF-Netze ohne Randkanten, nicht-manifold Kanten oder Nullflächendreiecke.
- Positive Volumina und maximal 0,5 % zulässige Abweichung zwischen B-Rep und Netz; alle Profile liegen darunter.
- Gültige 3MF-ZIP-Struktur mit Millimetereinheit, Release-ID und KI-Provenienzmetadaten.
- STEP-Grundstruktur, SVG-Fertigungspfade ohne Live-Schrift, DXF-R12-Millimetermetadaten und lesbare PNG-Dateien.
- OpenSCAD-Modulschnittstellen statisch vorhanden.

## Noch offen

Ein OpenSCAD-Parser, ein Ziel-Slicer und der reale Drucker standen in der digitalen Prüfumgebung nicht zur Verfügung. Deshalb müssen Slicer-Vorschau und Coupon-Druck gemäß `test-plan.yaml` vor dem Serieneinsatz abgeschlossen werden.
