# Validierungszusammenfassung R5

## Ergebnis

**GO** für M3-Messlehre, Slicer-Importtest und anschließend einen beaufsichtigten Funktionstest. **Noch kein GO** für unbeaufsichtigten Betrieb.

| Gate | Status | Ergebnis |
|---|---|---|
| Architektur | PASS | kurze bodenlose Fanghaube, separater loser Behälter |
| Referenztrennung | PASS | Beispiel nur qualitativ betrachtet; keine Meshes oder Maße übernommen |
| Feder-Auswurf-Konzept | PASS digital | 58-mm-Prallwand, massive Trefferzone, 8-mm-Überhang |
| Orientierung | PASS digital | vom Drucker vorne: Schraub-/Displayseite rechts (`−X`), Prallwand links (`+X`) |
| Durchfall | PASS digital | 57 × 39 mm offen; keine Innen-Bodenfläche |
| Waben | PASS digital | glatte analytische Hexagonalrippen; Körper nicht voxelisiert |
| Hauben-Druckbarkeit | PASS Proxy | maximal 45° von der Vertikalen |
| Befestigung | PASS digital | zwei vertikale 8 × 4,2-mm-Langlöcher im Displayseiten-Ohr |
| Eigene Meshprüfung | PASS | 7/7 STL-Meshes geschlossen, positiv und ohne Rand-/Nichtmanifold-/Windingfehler |
| Eigene 3MF-Prüfung | PASS | 3/3 Core-3MF-Pakete mit gültigen Referenzen |
| Logo-Quelltreue | PASS | 13/13 SVG-Pfade, volle `viewBox`, vier Farben, keine Neuanordnung oder Spiegelung |
| Logo-Hintergrund | PASS | keine Hintergrundplatte; analytische Pfadextrusion direkt auf Waben/Tragstreben |
| Logo-Startkontakt | PASS Proxy | 42/42 getrennte Komponenten auf drei Seiten beginnen auf Körpermaterial |
| Drei Logo-Seiten | PASS | Vorderseite, Prallwand und Displayseite |
| Anycubic Slicer Next | NOT_RUN | lokal nicht vorhanden; gemeinsamer STL-Import bleibt Fallback |
| Maschinenpassung | PENDING | Schraubenabstand, -länge und dynamischer Freiraum physisch prüfen |
| Purge-Funktion | PENDING | drei beaufsichtigte Zyklen erforderlich |

Kennzahlen:

- Fangbereich 62 × 44 mm, Prallhöhe 58 mm.
- Freier Durchfall 57 × 39 mm.
- Montierter Anteil inklusive drei Logos: ca. 20,6 g PETG als geometrischer Proxy.
- Analytische Waben: keine Voxelstufen am Fangkorb oder Logo.
- Schraubenpaarung: 20,0 mm bildabgeleiteter Startwert; ca. 16,2–23,8 mm Einstellbereich.
- Optionaler Unterbehälter: ca. 1,75 l.

Da weder offizielle Lochmaße noch eine Purge-Flugkurve veröffentlicht sind, bleiben Messlehre, ausgeschalteter Vollbewegungstest und drei beobachtete Purge-Zyklen zwingende Stop-Gates.
