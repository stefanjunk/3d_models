# Validierungszusammenfassung R3

## Ergebnis

**GO** für vertikale M3-Messlehre, Waben-/Logo-Probe und Anycubic-Slicer-Importtest. **Noch kein GO** für unbeaufsichtigten Betrieb.

| Gate | Status | Ergebnis |
|---|---|---|
| Architektur | PASS | Kompakter Fangkorb, separater loser Unterbehälter |
| Feder-Auswurf-Konzept | PASS digital | Massive 64-mm-Prallwand; 10-mm-Fanghaube ab Z=48 mm |
| Hauben-Druckbarkeit | PASS Proxy | maximal 43,2° von der Vertikalen; Support aus vorgesehen |
| Befestigungsrichtung | PASS digital | zwei vertikale 8 × 4,2-mm-Langlöcher statt horizontalem 52-mm-Schlitz |
| Eigene Meshprüfung | PASS | 7/7 STL-Dateien geschlossen, positive Volumen, keine Rand-, Nichtmanifold-, Winding- oder Duplikatfehler |
| Eigene 3MF-Prüfung | PASS | 3/3 ZIP/XML/Objekt/Material-/Dreiecksprüfungen |
| Logo-Quelltreue | PASS | 13/13 Pfade, volle `viewBox`, vier Farben, keine Neuanordnung oder Spiegelung |
| Drei Logo-Seiten | PASS | Vorderseite, linke Seite und rechte Displayseite |
| Seiten-Wabenhaut | PASS | 1,0-mm-Innenhaut digital lückenlos; Wabenrippen vorhanden; Prallwand massiv |
| Anycubic Slicer Next | NOT_RUN | Programm lokal nicht vorhanden; gemeinsamer STL-Import bleibt Fallback |
| Maschinenpassung | PENDING | Schraubenabstand, Schraubenlänge und dynamischer Auswerferraum physisch prüfen |
| Purge-Funktion | PENDING | drei beaufsichtigte Zyklen erforderlich |

Wesentliche Kennzahlen:

- obere Fangöffnung 68 × 46 mm; Gesamtgeometrie ca. 68 × 49 × 64 mm.
- 40,76 % weniger Öffnungsfläche und 23,81 % weniger Höhe als R2.
- Montierter Anteil inklusive drei vollständiger Logos: ca. 40,9 g PETG; 34,59 % unter R2.
- Freier Fangkorbauslass: ca. 39 × 23 mm.
- Vertikale Schraubenpaarung: 20,0 mm bildabgeleiteter Startwert; Langlöcher decken ca. 16,2–23,8 mm ab.
- Unterbehälter: ca. 1,75 l.

Die offizielle Dokumentation bestätigt die federbelastete Rückstellung, veröffentlicht aber weder Schraubenabstand noch Fragmentgeschwindigkeit oder Flugbahn. Deshalb bleiben Messlehre, ausgeschalteter Vollbewegungstest und drei beobachtete Purge-Zyklen zwingende Stop-Gates.
