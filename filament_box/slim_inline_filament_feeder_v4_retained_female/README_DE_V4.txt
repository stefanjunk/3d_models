MODULARER INLINE-FILAMENTFEEDER V4 – VERSTAERKTE FEMALE-T-NUT

Aenderung gegenueber V3
-----------------------
Die weibliche T-Nut besitzt jetzt eine 1,20 mm starke aeussere Fanglippe.
Die breite Kammer fuer den T-Kopf ist damit nach aussen geschlossen. Nur der
schmale Halsdurchgang bleibt offen. Die Verbindung kann weiterhin von oben
zusammengeschoben werden, aber die Module koennen seitlich nicht mehr aus der
Nut springen.

Passung
-------
Maennlicher Hals:       5,00 mm
Weiblicher Hals:        5,80 mm  (0,40 mm Spiel pro Seite)
Maennlicher T-Kopf:     8,00 mm
Weibliche Kopfkammer:   8,90 mm  (0,45 mm Spiel pro Seite)
Einlauf oben: zusaetzlich aufgeweitet
Rastermass:             26 mm

Diese Werte sind bewusst etwas locker fuer PETG mit 0,4-mm-Duese gewaehlt.
Bei sehr starkem Elephant Foot die unteren 0,3–0,5 mm im Slicer kompensieren.

Dateien
-------
01_gehaeuse_modular_T_nut_verstaerkt_8x_drucken.stl   8x drucken
02_TPU_druckrad.stl                                    8x drucken
03_TPU_federlippe_2x_drucken.stl                      16x drucken
05_endkappe_links_optional.stl                         optional
06_endkappe_rechts_verstaerkte_female_optional.stl    optional
07A_T_nut_passprobe_male.stl                           zuerst 1x drucken
07B_T_nut_passprobe_female_mit_aussenkante.stl         zuerst 1x drucken

Montage
-------
1. Zuerst die beiden Passproben drucken.
2. Male-Probe von oben in die Female-Probe schieben.
3. Die Verbindung soll ohne Werkzeug gleiten, aber seitlich formschluessig sein.
4. Danach die Feeder nacheinander von oben ineinanderschieben.
5. Nicht seitlich auseinanderziehen; zum Trennen ein Modul wieder nach oben schieben.

Feinanpassung im OpenSCAD-Skript
--------------------------------
female_neck_w und female_head_w vergroessern, falls die Passung zu eng ist.
Empfohlener Schritt: jeweils +0,15 mm.
Bei zu viel Spiel beide Werte um 0,10–0,15 mm reduzieren.

Druck
-----
Gehäuse: PETG, 0,4-mm-Duese, 0,18–0,22 mm, 4–5 Waende, ohne Support.
Steckseite sauber halten; Naht nach Moeglichkeit nicht in die T-Nut legen.
