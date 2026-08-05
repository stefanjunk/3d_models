SCHLANKER INLINE-FILAMENTVORSCHUB V2 – NORMALLY OPEN

Funktion
- Das Filament läuft während des normalen Drucks frei durch den geraden Kanal.
- Das TPU-Rad steht im Ruhezustand ca. 1,5 mm über seiner Eingriffsposition und berührt das Filament nicht.
- Zum manuellen Bewegen das Rad mit dem Daumen herunterdrücken und gleichzeitig drehen.
- Nach dem Loslassen heben zwei kleine TPU-Federlippen die Achse wieder nach oben.
- Gedacht für wenige Zentimeter Vor- oder Rücklauf, nicht als Extruder und nicht zum Ziehen gegen einen geschlossenen Druckkopf-Extruder.

Abmessungen
- Gehäuse: ca. 54 x 18 x 21 mm
- Gesamthöhe mit offen stehendem Rad: ca. 27 mm
- TPU-Rad: Ø18 x 7 mm
- Achsweg: ca. 1,55 mm
- PTFE-Aufnahmen: Ø4,30 mm für üblichen PTFE-Schlauch Ø4,0 mm
- Filamentkanal: Ø2,50 mm für 1,75-mm-Filament

Teile drucken
- 01_gehaeuse_normally_open.stl: 1x PETG
- 02_TPU_druckrad.stl: 1x TPU 95A
- 03_TPU_federlippe_2x_drucken.stl: 2x TPU 95A
- 04_distanzscheibe_optional_2x.stl: optional 2x PETG; alternativ normale M3-Unterlegscheiben

Benötigte Hardware
- 1x M3x25 bis M3x30 Schraube als verschiebbare Radachse
- 1x M3-Stoppmutter
- 2x M3-Unterlegscheibe, besonders wichtig als Auflage auf den TPU-Federlippen
- optional 2x M3x6 bis M3x8 zum sehr leichten Fixieren der PTFE-Enden

Montage
1. Zwei PTFE-Stücke rechtwinklig abschneiden und von beiden Seiten bis zum inneren Anschlag einschieben.
2. Filament durch beide PTFE-Enden und den mittleren Kanal führen.
3. TPU-Rad zwischen die Seitenwangen setzen.
4. M3-Schraube durch erstes Langloch, Rad und zweites Langloch führen.
5. Außen je eine Unterlegscheibe montieren und die Stoppmutter nur so weit anziehen, dass das Rad frei dreht und die Achse im Langloch frei auf/ab gleitet.
6. Je eine TPU-Federlippe von der hinteren Stirnseite in die schmale Nut jeder Außenwand einschieben. Die breite runde Spitze liegt unter der M3-Unterlegscheibe.
7. Prüfen, ob das Rad nach dem Loslassen selbstständig nach oben fährt und mindestens etwa 0,8–1,2 mm Abstand zum Filament hat.

Bedienung
- Rad nach unten drücken, bis es das Filament greift.
- Unter Druck vorwärts oder rückwärts drehen.
- Loslassen: Das Rad fährt hoch und das Filament läuft wieder frei.
- Nicht mit Gewalt drehen, wenn der Extruder des Druckers das Filament festhält. Zum Entladen zuerst am Drucker den Extruder öffnen bzw. den vorgesehenen Unload-Vorgang starten.

Druckempfehlung
Gehäuse, optionale Scheiben:
- PETG
- 0,4-mm-Düse empfohlen
- 0,18–0,22 mm Schichthöhe
- 4–5 Wandlinien
- 35–50 % Infill
- Gehäuse mit dem flachen Boden auf das Druckbett
- kein Support; kleine horizontale PTFE-Bohrungen werden gebridged

Rad und Federlippen:
- TPU 95A
- 0,4-mm-Düse
- 0,16–0,20 mm Schichthöhe
- langsam drucken
- Rad auf einer Seitenfläche drucken
- Federlippen flach drucken

Feinabstimmung
- Rad berührt das Filament im Ruhezustand: wheel_center_open_z im SCAD um 0,3–0,6 mm erhöhen oder Federlippe minimal dicker skalieren.
- Rad greift beim Drücken nicht: wheel_center_engaged_z um 0,2–0,4 mm reduzieren oder ein etwas weicheres TPU verwenden.
- Federlippen heben zu stark: Federlippen in Z auf 85–90 % skalieren.
- Federlippen heben zu schwach: Federlippen in Z auf 110–120 % skalieren.
- PTFE sitzt zu stramm: ptfe_socket_d im SCAD um 0,10–0,20 mm erhöhen.

Hinweis
Die Konstruktion wurde geometrisch und als geschlossenes STL-Mesh geprüft, aber noch nicht physisch mit deinem konkreten PTFE-Schlauch, TPU und Drucker getestet. Zuerst ein Exemplar drucken und die Eingriffshöhe prüfen.
