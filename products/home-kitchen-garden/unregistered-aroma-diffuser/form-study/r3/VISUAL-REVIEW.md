# R3 — Sicht- und Prüfbefund

Bewertete Geometrie: runs/001; tatsächliche Blender-5.2.0-LTS-Render,
24 Samples, 800 × 1000 Pixel, unverändertes R2-Studio. Keine KI-Übermalung.
R1 dient als gestalterische Referenz, nicht als kalibriertes Messbild.

## Optik

Der Hauptagent und ein unabhängiger Read-only-Reviewer bevorzugen R3 gegenüber
R2/003. Höherer Bauch und schmalere Kämme ergeben mehr Gegengewicht und klarere
Lichtlinien; Hero, Rücken und Seite bleiben zusammenhängend. Die seitlich
versetzten Spitzen sind etwas besser unterscheidbar.

Verbleibende Schwäche: Die Krone wirkt gegenüber R1 noch aufrecht und
blütenartig; seitlich überdecken sich die Spitzen teilweise und bleiben
relativ stumpf. Eine stärkere seitliche Bewegung der Hauptspitze ist eine
mögliche nächste kleine Stilvariante, kein Anlass, die gewählte Route zu verwerfen.
Dies ist eine Agentenempfehlung, keine menschliche Erscheinungsbildfreigabe.

## Nominale Kaufteile

Der zusätzliche Render mit 200-mm-Docht zeigt einen störenden geraden Stab in
der oberen Öffnung. Exakter Manifold-Meshvergleich meldet 13.963413 mm³
Überschneidung zur Hülle; deshalb bleibt dieser Vorschlag als verworfenes
Diagnosebeispiel erhalten. 160 mm Dochtlänge bei gleicher Lage bewahren den
ruhigen Hero-Look und ergeben keine volumetrische Kollision. Die Fiole bleibt
ebenfalls kollisionsfrei. Der kurze Docht ist tatsächlich im Render aktiviert,
nicht ausgeblendet. Verdeckung gilt für die geprüfte Ansicht, nicht jeden Blickwinkel.

Keine Aussage über Diffusion, Kapillarität, Mindestspalt, reale Halterung oder
Ölverträglichkeit. Die Referenzfiole ist ein Zylinder ohne Halsdetail. Der
200-mm-Docht wird für diese optische Empfehlung um 40 mm gekürzt.

## Geometrie und Fertigungsgrenze

Der triangulierte Schalenexport hat 394232 Dreiecke, eine zusammenhängende
geschlossene Komponente, konsistente Flächenorientierung und positives Volumen.
Keine Randkanten, nicht-manifold Kanten, doppelten oder degenerierten Dreiecke
im gemeinsamen Audit. Der visuelle Fuß ist separat und nicht Teil dieses
Ein-Komponenten-Befunds. Exportabmessungen mit Fuß: ca. 96.27 × 89.96 × 240 mm.

Alle 29 Fälle des reduzierten Parameter-Sweeps bestehen die Topologieprüfungen.
Der Sweep prüft Default, deklarierte Einzelgrenzen und
ausgewählte Paare für Rippenkamm/-tiefe sowie Verdrehung/Kronenansatz.
Er bewertet Topologie, nicht sämtliche Kombinationen, finale Bevel-Geometrie,
Kaufteilfreiraum, Optik oder Druckbarkeit der Varianten.

Strenger Gesamtaudit: NOT_RUN, nicht PASS. Normale Mindestwand konnte wegen
fehlendem rtree nicht geprüft werden; für zertifizierte Selbstüberschneidungen
ist kein Backend eingerichtet. Keine Installation erfolgt. 2.4 mm radialer
Schalenparameter bedeutet nicht 2.4 mm normale Mindestwand.

Zwei dichte Leitlinien zeigen im numerischen Kurvenbericht jeweils einen vom
Heuristikfilter erkannten Krümmungsextremwert; maximale diskrete Krümmung rund
0.305/mm am Kamm und 0.237/mm am Rand. Hohe Krümmung an den weichen Endkappen
ist zu prüfen. Dies sind weder automatische Stilnoten noch G2-/Class-A-Nachweise;
insbesondere Kronenwurzel, Bündelung und Endkappe bleiben separat zu prüfen.

Offen: Wandstärke, Selbstüberschneidung, Kronenrobustheit, finale Tesselierung,
Aufnahme/Fußverbindung, gemessene Interfaces, exakte Maschine/Material/Profile,
Slicer/Supports, Oberfläche, Standfestigkeit, Service und Duftleistung.
Der gemeinsame Projekt-Gate bleibt gesperrt. Kein P2, STL-Druckkandidat oder
Herstellungs-G-Code und kein freigegebenes befülltes Produkt.
