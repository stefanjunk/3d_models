# Validierungszusammenfassung R2

## Ergebnis

**GO** für Messlehre, Waben-/Logo-Probe und Anycubic-Slicer-Importtest. **Noch kein GO** für unbeaufsichtigten Betrieb.

| Gate | Status | Ergebnis |
|---|---|---|
| Architektur | PASS | Kleiner montierter Fangkorb, separater loser Unterbehälter |
| Eigene Meshprüfung | PASS | 7/7 STL-Dateien geschlossen, positive Volumen, keine Rand-, Nichtmanifold-, Winding- oder Duplikatfehler |
| Externe Meshprüfung | NOT_RUN | `trimesh` fehlt; Einschränkung dokumentiert |
| Eigene 3MF-Prüfung | PASS | 3/3 ZIP/XML/Objekt/Material-/Dreiecksprüfungen |
| Externe `fdm_ci`-3MF-Prüfung | PASS | 3/3 Standard-Core-Pakete gültig |
| Logo-Quelltreue | PASS | 13/13 Pfade, volle `viewBox`, vier Farben, keine Neuanordnung oder Spiegelung |
| Drei Logo-Seiten | PASS | Vorderseite, linke Seite und rechte Displayseite |
| Waben-Fanghaut | PASS | 1,0-mm-Innenhaut digital lückenlos; Wabenrippen vorhanden |
| Anycubic Slicer Next | NOT_RUN | Programm lokal nicht vorhanden |
| Maschinenpassung | PENDING | Messlehre, Schraubenlänge und Bewegung physisch prüfen |
| Purge-Funktion | PENDING | drei beaufsichtigte Zyklen erforderlich |

Wesentliche Kennzahlen:

- Montierter Anteil inklusive drei vollständiger Logos: ca. 62,6 g PETG.
- Wabenkörper: ca. 8,46 % weniger geometrisches Körpervolumen als die vollflächige 2,5-mm-Wandvariante.
- Erforderliche Innenhaut-Voxel: 142.488; fehlend: 0.
- Freier Fangkorbauslass: ca. 51 × 31 mm.
- Unterbehälter: ca. 1,75 l.
- Fangkorb-3MF: ein direktes Mesh-Objekt, null `components`-Knoten, fünf Materialdefinitionen.

Der erste Wabenbuild wurde wegen vier nichtmanifolder Kanten an zwei diagonalen Übergängen gestoppt. Der finale Build ergänzt acht lokale 0,5-mm-Topologiezellen innerhalb der zulässigen Wandzone; die Wiederholungsprüfung ist vollständig PASS.

Noch offen bleiben der tatsächliche Import in Anycubic Slicer Next, Slicer-Zeit/Filament/Purge, die Waben-/Logo-Probe, Maschinenpassung und der reale Fragmentfang.
