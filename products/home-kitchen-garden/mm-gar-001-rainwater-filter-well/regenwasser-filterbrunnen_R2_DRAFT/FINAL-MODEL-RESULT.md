# Modell-Ergebnisbericht · Revision 2 DRAFT

## Ergebnis

Das freigegebene Konzept ist als vollständige parametrische 3D-Baugruppe umgesetzt: drei stapelbare Primärgehäuse, Wirbel-/Schlammstufe, Lamellenstufe, drei Medienkörbe, Verteiler, austauschbarer Auslauf, Schlauchanschlüsse, Blinddeckel und Passcoupon. Die Wasserwege sind drucklos getrennt und wartungszugänglich.

## Validierte Kennzahlen

- 816 mm Montagehöhe;
- 300 mm Modul- und 330 mm Standdurchmesser;
- 14 druckbare Teiltypen, 17 Dateien nach Stückzahl;
- 14/14 STL geometrisch bestanden;
- etwa 9,96 kg PETG in Basiskonfiguration, 10,15 kg für den vollständigen Alternativ-/Coupon-Satz;
- 800 L/h Auslegung, 1.200 L/h geometrisch plausibilisierte Obergrenze;
- drei markierte Primärgehäuse mit dem originalen JuSt-Asset.

## Anforderungsaudit

| Anforderung | CAD-Stand | Nachweisstatus |
|---|---|---|
| drei separat druckbare Module | umgesetzt | digital bestanden |
| Wirbel-, Lamellen- und Medienfolge | umgesetzt | digital; Wirkung physisch offen |
| 25-mm-Zulauf | umgesetzt plus 3-fach Coupon | Passprüfung offen |
| Kaskade plus optionaler Schlauch | umgesetzt | Pass-/Dichtheitsprüfung offen |
| 0,6-mm-PETG-Prozess | konstruktiv berücksichtigt | Slicer/physisch offen |
| Kobra-3-Max-Bauraum | alle Teile passen mit Reserve | digital bestanden; Maschinen-Dry-Run offen |
| wartbare Einsätze | separat und von oben entnehmbar | physischer Wartungszyklus offen |
| Notüberlauf | 80 mm breit umgesetzt | Blockiertest offen |
| druckloser Betrieb | offene Überläufe und Warnhinweise | Betriebsdisziplin erforderlich |

## Freigabeurteil

**Digitaler DRAFT-Freigabekandidat: bestanden. Finale Fertigungs-/Produktfreigabe: noch blockiert.**

Blocker sind der echte Slicer-Dry-Run einschließlich Kennzeichnungslagen sowie die im Prüfplan genannten physischen Pass-, Dichtheits-, Durchfluss-, Überlauf- und Standversuche. Ohne diese Nachweise dürfen Dateinamen und Status nicht von DRAFT auf RELEASE geändert werden.

