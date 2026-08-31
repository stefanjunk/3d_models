# OpenQuad CF5 - Verdrahtung und Software-Setup

Baseline: SpeedyBee F405 V5/OX32 55A, Betaflight, RadioMaster RP1 V2 ELRS
2.4 GHz LBT, vier EMAX ECO II 2207 2400KV, 4S. Die Bezeichnungen am realen
Board und das aktuelle Herstellerhandbuch haben immer Vorrang.

## Verdrahtungsmatrix

| Funktion | FC-Pad/Port | Gegenstelle | Regel |
|---|---|---|---|
| ELRS Versorgung | 5V + GND | RP1 5V + GND | Polaritaet und Spannung vor Loeten messen |
| ELRS Daten | UART2 T2/R2 | RP1 RX/TX | gekreuzt: FC-TX -> RX-RX, FC-RX <- RX-TX |
| GPS optional | UART4/GPS-Port, 4.5V/GND | GM10 TX/RX/VCC/GND | gekreuzte UART-Leitungen; erst nach Basisflug |
| Buzzer | BZ+ / BZ- | VIFLY Finder 2 | VIFLY-Handbuch beachten; Selbstversorgungsfunktion testen |
| ESC | 10-poliges Stackkabel | OX32 ESC | Kabelbelegung nicht selbst umordnen |
| Hauptakku | BAT+/BAT- am ESC | XT60, 12-14 AWG | 1000-uF-Kondensator kurz und polrichtig |
| Motoren | M1-M4 am ESC | drei Phasen je Motor | Richtung spaeter softwareseitig pruefen/aendern |

Radio-UART2 und GPS-UART4 entsprechen der F405-V5-Dokumentation. UART1 wird
vom Bluetooth-System genutzt; UART5 ist ESC-Telemetrie. Beim Wechsel auf V3,
V4 oder einen anderen FC **nicht** diese Tabelle kopieren, sondern neu mappen.

## Software-Baseline (Stand 13.08.2026)

- Flight Controller: aktuelle stabile Betaflight-Version; bei Recherche war
  2026.6.1 aktuell. Cloud-Build-Target `SPEEDYBEEF405V5`.
- Funk: ExpressLRS 4.1.0 oder eine spaetere stabile, untereinander kompatible
  4.x-Version auf Sender und Empfaenger; EU/LBT-Regulatory-Domain.
- Sender: zur Pocket passende stabile EdgeTX-Version. Vor Updates Modelle,
  Kalibrierung und SD-Inhalt sichern.
- ESC: OX32-Werkzeug/Firmware nach Hersteller. OX32 ist nicht Open Source.
  Offenere Alternative: kompatibler AM32-ESC; Restposten V3-BLHeli_S kann mit
  Bluejay betrieben werden.

Keine fremden `diff all`-Dateien blind einspielen. Erst den Werkszustand sichern,
danach jede Aenderung in kleinen, testbaren Schritten.

## Betaflight-Einrichtung

1. **Propeller abnehmen.** USB verbinden, Board sichern (`diff all`, `dump`,
   Ziel/Version notieren).
2. Nur das dokumentierte Target flashen. Nach Flash erneut Boardbewegung im
   3D-Modell pruefen. Die deklarierte Flugrichtung liegt diagonal zwischen +X
   und +Y der CAD-Geometrie; daraus darf kein unbestaetigter Yaw-Wert abgeleitet
   werden.
3. Mixer QUADX. Motor-Wizard verwenden und reale Motorposition/-richtung
   einzeln verifizieren. Runaway-Prevention aktiviert lassen.
4. UART2 Serial RX aktivieren, Empfaengerprotokoll CRSF. Kanalmitten,
   Endpunkte, Arming-Schalter und Stickrichtung pruefen.
5. DShot300 als konservativen Startpunkt. Bidirectional DShot/RPM-Telemetrie
   nur aktivieren, wenn alle vier ESCs fehlerfrei Rueckmeldung liefern.
6. Stromsensor: Hersteller nennt fuer den V5/OX32 Scale 27, Offset -2644.
   Das sind nur Startwerte; gegen einen bekannten Verbrauch bzw. ein Messgeraet
   kalibrieren.
7. Keine aggressiven Filter- oder PID-Presets vor Blackbox-Daten. Zuerst
   Standardwerte, neue unbeschaedigte Low-Pitch-Props und optional 70 %
   Motor-Output-Limit.
8. Failsafe Stage 1/2 mit echter emulierter RX-Unterbrechung testen. Ohne
   validiertes GPS ist `DROP` in freiem Testgebiet die klarste Baseline.
9. GPS Rescue erst nach mehreren sicheren manuellen Fluegen, korrektem Home-Fix
   und eigenen Nah-/Fern-Tests aktivieren; es ist kein Ersatz fuer Flugplanung.

## Funk-Startprofil

- 250-Hz-Linkmodus ist ein robuster Ausgangspunkt; Dynamic Power und
  Telemetrierate konservativ einstellen.
- Empfaengerantenne als geraden Dipolbereich frei von Carbon, Akku und VTX
  montieren. Reichweitentest am Boden mit reduzierter Leistung nach
  ExpressLRS-Anleitung.
- LQ/RSSI-dBm, Akkuspannung, verbrauchte mAh und Warnungen im Sender anzeigen.
- Gesetzlich zulaessige Leistung und Frequenzregion fuer den Einsatzort pruefen.

## Alternativ-Stacks

| Ziel | Stack/Software | Einordnung |
|---|---|---|
| Beschaffung 2026 | F405 V5 + OX32 / Betaflight | guenstig und aktuell, ESC proprietaer |
| Mehr Offenheit | separater F405/H7-FC + T-Motor F55A AM32 | AM32 offen, ca. 50-100 EUR teurer |
| Restposten | F405 V3 BLS + Bluejay | offenere ESC-Kette, Hersteller hat V3 eingestellt |
| Navigation | dokumentiert unterstuetzter FC + INAV | nicht automatisch dieselbe V5-Konfiguration |
| Forschung/Autonomie | Pixhawk-Klasse + ArduPilot/PX4 | groesser, teurer, eigene mechanische Revision |
