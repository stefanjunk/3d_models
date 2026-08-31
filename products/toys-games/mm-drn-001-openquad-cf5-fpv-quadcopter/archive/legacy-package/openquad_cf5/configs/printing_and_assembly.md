# OpenQuad CF5 - Druck- und Montageanweisung

Status: **experimenteller Prototyp, nicht flugerprobt**. Die CAD-Quelle ist
parametrisch, aber in dieser Arbeitsumgebung nicht durch einen OpenSCAD-Kernel
gerendert oder als STL exportiert worden. Vor Fertigung sind F6-Render,
Mesh-Pruefung, Slicer-Vorschau und reale Passproben Pflicht.

## 1. Werkstoff und Startprofil

- Flugteile: bevorzugt PA11-CF oder PA612-CF15. PA6-CF20 ist moeglich, nimmt
  aber mehr Feuchte auf. PLA ist wegen Temperatur und Kriechen ausgeschlossen;
  PETG dient nur fuer billige Passprototypen.
- Exaktes Herstellerprofil verwenden. Beispiel PA6-CF20: der Hersteller nennt
  280-300 °C Duesentemperatur und 100 °C/8 h Trocknung. Diese Werte nicht auf
  andere Filamente uebertragen.
- Gehaertete 0,6-mm-Duese, geschlossener Drucker, trockene Filamentzufuhr.
- Startpunkt, noch zu qualifizieren: 0,30-mm-Schicht, sechs Konturen, sieben
  Deck-/Bodenschichten, 35 % Gyroid. Lokale Geometrie wird dadurch weitgehend
  vollwandig; Masse aus dem echten Slicer dokumentieren.
- Keine Skalierung im Slicer. X/Y/Z-Kompensation zunaechst null.

## 2. Orientierung und Teilezahl

| Teil | Anzahl | Orientierung | Support |
|---|---:|---|---|
| `hub_bottom` | 1 | grosse Platte auf Bett | nein |
| `hub_top` | 1 | glatte Seite auf Bett | nein |
| `battery_deck` | 1 | flach | nein |
| `motor_saddle` | 4 | Grundplatte auf Bett, Kanal nach oben | nein |
| `motor_plate` | 4 | flach | nein |
| `retention_plug` | 4 | Flansch auf Bett | nein |
| `arm_fit_coupon` | mindestens 3 | Grundplatte auf Bett | nein |

Zuerst nur Passcoupons drucken. Ziel ist ein spielfreier Schiebesitz ohne
Aufspreizen. Das Sollmass 10,25 mm ist ein Startwert; jedes Rohrlos messen.

## 3. CFK vorbereiten

1. Vier Rohre auf **103,0 mm** schneiden; Zielgleichheit +/-0,2 mm.
2. Bevorzugt zugeschnitten kaufen. Sonst nass oder wirksam abgesaugt schneiden,
   geeigneten Atem-/Augenschutz tragen und Elektronik fernhalten. CFK-Staub ist
   leitfaehig.
3. Kanten entgraten, reinigen und Rohrenden mit duennem Epoxid versiegeln.
4. Keine Bohrungen: Die quadratische Klemmung uebertraegt Drehmoment und haelt
   die Arme austauschbar.

## 4. Mechanische Montage

1. Vier innere Haltepfropfen vor dem Schliessen des Hubs in die Rohre setzen.
2. Rohre auf `hub_bottom` bis zum Anschlag positionieren. Motorzentren muessen
   jeweils 115,0 mm vom Mittelpunkt liegen.
3. `hub_top` mit acht M3-Durchgangsschrauben, Metallunterlegscheiben und
   Nyloc-Muttern schliessen. Gleichmaessig ueber Kreuz anziehen.
4. Kein pauschales Drehmoment uebernehmen. An identischen Coupons eine
   Drehmoment-/Schlupf-Reihe durchfuehren und das kleinste reproduzierbar
   schlupffreie Drehmoment mit Sicherheitsabstand zur ersten Schaedigungsanzeige
   festlegen.
5. Je Arm `motor_saddle` unter das Rohr und `motor_plate` darueber montieren.
   Die 0,15-mm-Vorspanngeometrie darf das Rohr nicht sichtbar eindruecken.
6. Motoren auf 16x16-mm-Lochbild befestigen. Schraubenlaenge so waehlen, dass
   keine Wicklung beruehrt wird; Schraubensicherung nur Metall-auf-Metall.
7. FC/ESC mit passenden Silikongummis auf 30,5x30,5 mm montieren. Sensor darf
   die gedruckten Platten nicht beruehren.
8. Vier 25-mm-M3-Alu-Abstandshalter und das 80x52-mm-Akkudeck montieren. Zwei
   unabhaengige Gurte plus rutschhemmende Auflage verwenden.

## 5. Leitungsfuehrung

- Motorkabel aussen am Rohr in Gewebeschlauch/TPU-Clips fuehren. Keine blanken
  Kabel durch scharfkantiges oder leitfaehiges CFK ziehen.
- Kabelschlaufen duerfen weder Propellerhuelle noch Gyro/FC beruehren.
- Antennen vom Carbon und von Hochstromleitungen absetzen; Zugentlastung vorsehen.
- Der im Stack enthaltene Kondensator sitzt mit kurzen Leitungen direkt am
  Batterieeingang; Polaritaet doppelt pruefen.

## 6. CAD-Export

In `CAD/openquad_cf5.scad` den Parameter `part` auf das gewuenschte Teil setzen,
mit OpenSCAD F6 vollstaendig rendern und als STL exportieren. `print_layout` ist
nur eine visuelle Anordnung; fuer reproduzierbare Slicer-Jobs Einzelteile
exportieren. Nach jeder Parameterveraenderung `analysis/validate_design.py`
angleichen und erneut ausfuehren.
