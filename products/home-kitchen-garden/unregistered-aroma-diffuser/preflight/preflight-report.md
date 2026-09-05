# Preflight 003 — FLUENT parametrische Formstudie R3

FLUENT | C3 (53.5/100) | R0 | K2 | Lane E | LOW_UNKNOWN

Entscheidung: CONCEPT_ONLY. Der Nutzer hat die visuelle Weiterentwicklung mit
vorläufigen handelsüblichen Kaufteilmaßen beauftragt. Produktionsfreigabe und
physische Funktionsaussagen bleiben offen. Der vorausgehende generische Audit
001 ist in Git erhalten; Assessment 002 liegt zusätzlich unter
history/preflight-002.json. Assessment 003 wurde vor der R3-Geometrie für
Revision 0.2.0 validiert. Die parametrische Entwicklungsroute ist vom Nutzer
ausgewählt; dies ist keine formale Erscheinungsbild- oder Fertigungsfreigabe.

## Komplexität und Reife

| Dimension | Score | Begründung |
|---|---:|---|
| REQ | 2 | Eleganz, Verdeckung und Luftzugang erzeugen Zielkonflikte. |
| CTX | 2 | Aufstellen, Nachfüllen, Reinigen und wechselnder Füllstand. |
| PAR | 2 | Hülle, Fuß und austauschbare Aufnahme vorgesehen. |
| INT | 3 | Acht Interfaces; IC-Mittel 10, Maximum 12; Rubrik ergibt ceil(2.1667)=3. |
| CPL | 1 | Gemeinsamer Innenraum, getrennte Außen-/Kaufteilparameter. |
| MOT | 1 | Einfache Montage-/Servicebewegung. |
| GEO | 3 | Freiform, verdeckte Öffnungen und Hohlraum. |
| PHY | 2 | Passive Verdunstung, geringe Lasten und Standfestigkeit. |
| MAT | 2 | Orientierung und Überhänge für spätere Fertigung relevant. |
| EXT | 2 | Gekaufte Fiole, Docht und Halter. |
| VER | 3 | Gestufte Fit-, Oberflächen-, Duft- und Standtests. |

Gewichtete Rubriksumme: 53.5. R0 wegen offener exakter Halter-/Medien- und
Fertigungsschnittstellen. K2 betrifft das spätere befüllte Produkt; Bilder sind
keine physischen Prototypen.

## Interfaces und Gates

Acht einzelne Verträge im JSON: Flasche/Aufnahme, Hülle/Fuß, Halter/Flasche,
Öl/Docht, Docht/Raumluft, Öl/Druckhülle, Fuß/Tisch und Nutzer/Hülle.

G0 PASS, G1 PASS, G2 FAIL, G3 FAIL, G4 WARN, G5 PASS, G6 WARN.
G2/G3: Lieferantennennmaße sind keine Mustermaße, Toleranzen oder exakten
Prozessdaten. G4/G6: messbare Funktions- und Servicekriterien noch festlegen.

## Funktionale FMEA für spätere Entwicklung

| Fehler | Wirkung | Erkennung | Gegenmaßnahme / Prüfung |
|---|---|---|---|
| Kippen | Öl tritt aus, Glasbruch | Stand-/Rutschtest voll und leer | Schwerpunkt und Standfläche anhand realer Massen auslegen |
| Unpassender Halter | Docht kippt oder benetzt Hülle | Lieferanten-/Musterprüfung | Passenden Halter kaufen; Reduzierer 11175 ausgeschlossen |
| Docht berührt Hülle | Flecken, mögliche Materialschäden | Kontakt-/Medientest | Freiraum und Eignung für genaue Mischung prüfen |
| Hülle behindert Verdunstung | Zu wenig Duft | A/B-Vergleich mit/ohne Hülle | Echte Öffnungen, Massenverlust und Wahrnehmung testen |
| Spitze bricht | Beschädigung, scharfe Kante | Handhabungsmuster | Abgerundete Enden, untere Griffzone, Orientierung prüfen |

Diese Phase: echte parametrisierte Geometrie, mehrere Modellansichten,
Topologie-/Parameterdiagnostik und Sichtbarkeit nominaler Kaufteile.
Komponentenbezogene virtuelle Evidenz R2; die globale Interface-Reife bleibt
R0. Die Proxies sind keine vermessenen Kaufteilmodelle. Radiale Schalenstärke
ist kein Nachweis einer minimalen normalen Wandstärke.
Danach: menschliche Beurteilung der tatsächlichen Geometrie; separate
PORT-102-Regularisierung auf main; Mustermaße, Halter, genauer Prozess,
Wand-/Spitzenprüfung, Slicer und physische Tests.
