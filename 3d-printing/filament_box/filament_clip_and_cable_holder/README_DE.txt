FILAMENT-STOPPCLIP UND KABEL-/PTFE-HALTER
==========================================

1) FILAMENT-STOPPCLIP
---------------------
Dateien:
- 01_filament_stoppclip_175mm.stl
- 01_filament_stoppclip_175mm.scad

Funktion:
Etwa 10 mm Filament aus dem PTFE-Schlauch herausstehen lassen und den Clip seitlich
auf das Filament schnappen. Der Clip ist groesser als der 4-mm-PTFE-Schlauch und
verhindert dadurch, dass das Filament in den Schlauch zurueckrutscht.

Standardmasse:
- fuer 1,75-mm-Filament
- Filamenttasche: 2.05 mm
- federnder Einsteckschlitz: 1.30 mm
- Aussenmass: ca. 13 x 10 x 3.2 mm

Druck:
- PETG empfohlen; alternativ PA oder zaehes PLA
- 0,4-mm-Duese empfohlen
- 0,16-0,20 mm Schichthoehe
- 4-5 Waende, 100 % oder hohes Infill
- flach drucken, kein Support

Ist der Clip zu fest oder zu locker, in der SCAD-Datei snap_slot_width und
filament_pocket_d in 0,1-mm-Schritten anpassen. Kanten nach dem Druck entgraten.

2) KABEL-/PTFE-BUENDELHALTER
----------------------------
Dateien:
- 02_kabelhalter_8xPTFE_1xUSB_halbschale_2x.stl
- 02_kabelhalter_8xPTFE_1xUSB.scad

Funktion:
Die Halbschale zweimal drucken. Acht PTFE-Schlaeuche liegen in den runden Nuten;
das USB-/Steuerkabel liegt in der ovalen mittleren Nut. Beide Haelften mit zwei
M3x18- oder M3x20-Schrauben, Unterlegscheiben und Muttern locker verschrauben.
Nur so weit anziehen, dass die Schlaeuche gehalten, aber nicht gequetscht werden.

Standardmasse:
- 8 Kanaele fuer PTFE AD 4,0 mm, Nutdurchmesser 4.6 mm
- USB-Nut ca. 7.5 x 4.8 mm
- Halter komplett montiert ca. 80 x 18 x 12 mm
- M3-Durchgangsbohrungen 3.5 mm

Druck:
- PETG empfohlen
- 0,4- oder 0,6-mm-Duese
- 0,20-0,28 mm Schichthoehe
- 4 Waende, 30-50 % Infill
- Nutseite nach oben, kein Support

WICHTIG:
Die genaue Form des Druckkopf-Steuerkabels kann abweichen. Vor dem Seriendruck
Breite und Dicke messen und usb_width / usb_height in der SCAD-Datei anpassen.
Die PTFE-Schlaeuche duerfen durch den Halter nicht oval gedrueckt werden.
