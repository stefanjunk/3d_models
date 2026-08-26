# Validierungszusammenfassung — R1

## Bestanden

- Parametrischer Quellenvertrag und Logo-Hash
- Architektur-/Zerlegungsplan: 0 Fehler, 0 Warnungen
- Zwei aufeinanderfolgende Builds: byte-identische STLs, 3MFs und Manifest
- 7/7 STL-Solids: geschlossen, positives Volumen, 0 Randkanten, 0 Non-Manifold-Kanten, 0 Windungsfehler, 0 degenerierte und 0 doppelte Flächen
- Ausgewählter Behälter: 1 zusammenhängende Komponente, 168 × 118 × 152 mm, 1,86 l konservatives Nutzvolumen
- Halter: 1 Komponente, 68 × 42 × 14 mm, geschlossen
- Lehre: 1 Komponente, 68 × 16 × 1,2 mm, geschlossen
- Kit-3MF: 4 Objekte inklusive Assembly, 3 Materialien, alle Verweise und Indizes gültig
- Badge-3MF: 5 Objekte inklusive Assembly, 4 Materialien, alle Verweise und Indizes gültig
- Digitale Schnittstellen: zwei Haken, durchgehender Rand und 52 × 4 mm M3-Langloch konsistent

## Absichtlich offen / blockiert

- Kein kompatibles Anycubic-/Orca-Slicer-CLI in der Laufzeit: Layer-Vorschau, reale Werkzeugpfade, Druckzeit, Support- und Purge-Menge wurden nicht ausgeführt.
- Der allgemeine FDM-CI-Mesh-Backendtest konnte ohne `trimesh` nicht laufen; deshalb wurde zusätzlich ein projektspezifischer Standardbibliotheks-Audit verwendet. Dessen vollständige Metriken stehen in `mesh-audit.json`.
- Anycubic veröffentlicht den Schraubenabstand nicht: reale Passung zuerst mit der dünnen Lehre prüfen.
- Physischer Druck, Achskollision, Purge-Fallweg, Haltekraft, Optik und kommerzielle Freigabe benötigen menschliche Evidenz.

Der aggregierte Projektstatus lautet deshalb `NOT_RUN`, obwohl alle lokal ausführbaren Geometrie-, 3MF- und digitalen Schnittstellenprüfungen bestanden sind. Das verhindert eine irreführende Behauptung, der Satz sei bereits physisch freigegeben.

