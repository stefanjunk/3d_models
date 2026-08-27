MODULARER INLINE-FILAMENTVORSCHUB V3 – 8-FACH STECKBAR

Zweck
- Acht getrennte 1,75-mm-Filamente lassen sich jeweils wenige Zentimeter manuell vor- oder zurückbewegen.
- Während des Drucks stehen die TPU-Räder offen und berühren das Filament nicht.
- Zum manuellen Vorschub das gewünschte Rad herunterdrücken und drehen.
- Die acht identischen Module werden seitlich zu einer kompakten Einheit zusammengesteckt.

Modulverbindung
- Rechts am Modul: zwei T-Zungen.
- Links am Modul: zwei nach oben offene T-Nuten.
- Das nächste Modul wird von oben in die beiden Nuten eingeschoben.
- Mit 8 Modulen beträgt die Breite ohne Endkappen ungefähr 210,5 mm, mit Endkappen etwa 215 mm.
- Zwischen den eigentlichen Gehäusen bleiben 8 mm. Das schafft Platz für M3-Schraubenkopf, Stoppmutter, Unterlegscheiben und TPU-Federlippen.
- Die Module können einzeln wieder nach oben herausgeschoben werden.

Zu druckende Teile für 8 Filamente
- 01_gehaeuse_modular_T_nut_8x_drucken.stl: 8x PETG
- 02_TPU_druckrad.stl: 8x TPU 95A
- 03_TPU_federlippe_2x_drucken.stl: 16x TPU 95A
- 04_distanzscheibe_optional_2x.stl: optional 16x; normale M3-Unterlegscheiben sind besser
- 05_endkappe_links_optional.stl: optional 1x PETG
- 06_endkappe_rechts_optional.stl: optional 1x PETG
- 07_T_nut_passprobe_2x_drucken.stl: vorab 2x als Passprobe drucken

Hardware je Modul
- 1x M3x25 bis M3x30 als Radachse
- 1x M3-Stoppmutter
- 2x M3-Unterlegscheibe

Gesamt für acht Module
- 8x M3-Achsschraube
- 8x M3-Stoppmutter
- 16x M3-Unterlegscheibe

Passprobe
1. Zuerst 07_T_nut_passprobe_2x_drucken.stl zweimal drucken.
2. Ein Teil seitlich versetzt über das andere halten und von oben einschieben.
3. Die Verbindung soll ohne Gewalt gleiten, aber nicht stark wackeln.
4. Zu eng: im SCAD slot_head_x und slot_neck_x um 0,15–0,30 mm erhöhen oder XY-Lochkompensation im Slicer verwenden.
5. Zu locker: Werte entsprechend verkleinern.

Montage des 8-fach-Blocks
1. Je Modul Rad, Achse und Federlippen wie bei V2 montieren.
2. Alle M3-Schraubenköpfe auf dieselbe Seite und alle Muttern auf die andere Seite setzen. Dadurch nutzen die Nachbarmodule den 8-mm-Spalt am besten.
3. Modul 2 über Modul 1 halten, die beiden T-Zungen über den T-Nuten ausrichten und senkrecht nach unten schieben.
4. Mit den weiteren Modulen wiederholen.
5. Optional linke und rechte Endkappe ebenfalls von oben einschieben.
6. Erst danach die acht PTFE-Paare einsetzen und Filamente durchführen.

PTFE- und Filamentmaße
- PTFE-Aufnahmen: Ø4,30 mm für üblichen Ø4,0-mm-Schlauch
- Filamentkanal: Ø2,50 mm für 1,75-mm-Filament
- Modul: ca. 54 mm lang; Gehäuse 18 mm breit
- Rastermaß verbunden: 26 mm

Druckempfehlung Gehäuse/Endkappen
- PETG
- 0,4-mm-Düse empfohlen
- 0,18–0,22 mm Schichthöhe
- 4–5 Wandlinien
- 35–50 % Infill
- Boden flach auf dem Druckbett
- keine Supports

Druckempfehlung TPU-Rad/Federlippen
- TPU 95A
- 0,4-mm-Düse
- 0,16–0,20 mm Schichthöhe
- langsam drucken

Wichtige Hinweise
- Das System ist nur für kurze manuelle Korrekturen gedacht, nicht als Extruder.
- Nicht gegen einen geschlossenen oder festhaltenden Druckkopf-Extruder drehen.
- Die T-Nut-Verbindung wurde konstruktiv und als geschlossenes Mesh geprüft, aber noch nicht physisch mit deinem Drucker testgedruckt.
- Wegen unterschiedlicher PETG-Schrumpfung und Flow-Einstellung unbedingt zuerst die kleine Passprobe drucken.
