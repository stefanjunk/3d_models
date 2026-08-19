# Modell-Ergebnisbericht · Revision 3 DRAFT

## Ergebnis

Das freigegebene R3-Konzept ist als vollständige parametrische 3D-Baugruppe umgesetzt. Neu gegenüber R2 sind der offene Einlaufbecher mit sicherem Luftspalt, das separate 32-mm-Fallrohr mit getauchtem tangentialem 28-mm-Auslass, der auf 10 mm vergrößerte Stage-1-Schlammweg, zwei eigenständige DN25-Ablässe und der 5,02° geneigte Sedimentboden unter der Lamellenkassette.

## Validierte Kennzahlen

- Betriebsbereich 0–1.200 L/h ohne definierte Mindestmenge; Auslegungspunkt 800 L/h;
- 851 mm Montagehöhe einschließlich Schlauchhalter;
- 300 mm Modul- und 330 mm Standdurchmesser;
- 17 druckbare Teiltypen, 21 Druckteile nach Stückzahl;
- 17/17 STL geometrisch bestanden und 11/11 R3-Schnittstellenprüfungen bestanden;
- etwa 10,27 kg PETG in Basiskonfiguration, 10,55 kg im vollständigen Alternativ-/Coupon-Satz;
- 15,0 mm Luftspalt und 41,0 mm statische Überdeckung der Tangentialöffnung;
- 9,63 mm analytische Becherreserve bei 1.200 L/h unter dokumentierten Annahmen;
- 10,0 mm Stage-1-Schlammspalt, 5,02° Stage-2-Boden und 18,72 mm Lamellenabstand;
- drei Primärgehäuse mit originaler JuSt-Kontur regressionsgeprüft.

## Anforderungsaudit

| Anforderung | CAD-Stand | Nachweisstatus |
|---|---|---|
| drei separat druckbare Module | umgesetzt | digital bestanden |
| Wirbel-, Lamellen- und Medienfolge | umgesetzt | digital; reale Abscheidewirkung offen |
| 0–1.200 L/h ohne Mindestmenge | offener, belüfteter Becher | analytisch bestanden; Nasslauf offen |
| mindestens 15 mm Luftspalt | 15,0 mm Referenzabstand | digital bestanden; Montageprüfung offen |
| getauchter Stage-1-Auslass | 28-mm-Öffnung mit 41 mm statischer Überdeckung | digital bestanden |
| Stage-1-Schlammweg ≥10 mm | 10,0 mm plus DN25-Ablass | digital bestanden; Partikelspülung offen |
| Stage-2-Sedimentboden ≥5° | 5,02°, DN25-Ablass | digital bestanden; Sandspülung offen |
| Lamellenabstand zum Boden ≥15 mm | 18,72 mm konservativ | digital bestanden |
| 0,6-mm-PETG-Prozess | konstruktiv berücksichtigt | Slicer/physisch offen |
| Kobra-3-Max-Bauraum | alle Teile passen mit Reserve | digital bestanden; Maschinen-Dry-Run offen |
| wartbare Einsätze | separat und von oben entnehmbar | physischer Wartungszyklus offen |
| Notüberläufe | Becher und Stufe 3 offen umgesetzt | Blockadetests offen |

## Freigabeurteil

**Digitaler R3-DRAFT-Freigabekandidat: bestanden. Finale Fertigungs-/Produktfreigabe: noch blockiert.**

Blocker sind der echte Slicer-Dry-Run – insbesondere für den abgestützten Einlaufbecher-Ring – sowie die im Prüfplan genannten physischen Pass-, Dichtheits-, Rückfluss-, Schlamm-, Durchfluss-, Überlauf- und Standversuche. Bis dahin bleiben Status und Exporte ausdrücklich DRAFT.
