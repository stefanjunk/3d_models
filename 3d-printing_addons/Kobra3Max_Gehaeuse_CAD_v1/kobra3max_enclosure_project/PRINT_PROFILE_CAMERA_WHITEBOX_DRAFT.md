# Druckprofil – Kobra 3 Max Kamera-Whitebox DRAFT

## Gemeinsame Startwerte

- Drucker: Anycubic Kobra 3 Max;
- Material: PETG nach Herstellerprofil, für Sichtblenden mattweiß;
- Düse: 0,6 mm;
- Schichthöhe: 0,30 mm;
- geplante Linienbreite: ungefähr 0,68 mm;
- vier Wände für Halter, Kameraschlitten, Arm, Kugel und Socket;
- vier bis fünf Deck-/Bodenschichten;
- 20–30 % Gyroid/Cubic für belastete Halter;
- 15–20 % für großflächige Blenden und Fensterrahmen;
- Brim nur bei Warping;
- keine Supports in den vorgesehenen Standardorientierungen; Kugel und Socket im Preview kontrollieren.

## Reihenfolge und Orientierung

| Bauteil | Druckbettfläche / Hinweis |
|---|---|
| Kamera-Passring | flache Ringseite; als erstes drucken |
| Kugel-Teststift | quadratische Basis, Kugel nach oben |
| Dreifach-Socket-Coupon | lange Grundplatte, Öffnungen nach oben |
| Kameragabel-Coupon | rechteckige Grundplatte |
| Kameraschlitten | große abgerundete Montageplatte |
| kurzer Socket-Arm | flache Armseite, Socketöffnung nach oben |
| Kamerafrontschale | optische Frontfläche auf dem Bett |
| Rückdeckel mit Kugel | flache Deckelfläche, Kugel nach oben |
| Innenblende/Klemmrahmen | jeweils große flache Seite |
| 7°-Fensterkeil | ebene Rückseite |
| Dachkassetten-Lokator | quadratische Basis |
| Lüfter-Sichtblende | geschlossene weiße Frontfläche |
| Serviceplatte | große Außenfläche, Zentrierrand nach oben |
| Lüfteradapter | quadratischer Flansch |

## Coupon-Auswertung

- Kameraring: Kamera darf nicht geklemmt, PCB/Gehäuse nicht gebogen und Kabel nicht gequetscht werden.
- Socket-Coupon, von links nach rechts: 0,15 / 0,28 / 0,40 mm radiales Spiel.
- Gewählt wird der kleinste Socket, der sich ohne Schaden aufdrücken und von Hand verstellen lässt sowie 24 Stunden ohne sichtbares Kriechen hält.
- Gabel-Coupon: 6,0-mm-Armauge muss in 6,65-mm-Gabel frei drehen und mit M4 klemmbar sein.

## Kritische Slicerprüfung

- keine ungeplanten Supports in Kugel, Socket, Lüftungsschlitzen oder Luftkanal;
- mindestens vier zusammenhängende Bahnen im Kameraarm und um M4/M5-Befestigungen;
- saubere Brücken in der Kugelpfanne, ohne den Haltekragen zuzusetzen;
- M2,5-Pilot-/Durchgangsbohrungen im Kameragehäuse bleiben offen;
- vier durchgehende Bahnen an der 2,6-mm-Lüfterblende;
- keine Lücken in den Standoff-Säulen der Blende;
- Spitzenvolumenstrom unter dem gemessenen Limit des konkreten PETG-Profils.

Ein ausführbarer lokaler Orca-/Prusa-Slicer wurde nicht gefunden. Zeit, Material, Layerzahl, Support und Werkzeugpfade bleiben deshalb `NOT_RUN`; dieses Dokument ist kein freigegebenes Produktionsprofil.
