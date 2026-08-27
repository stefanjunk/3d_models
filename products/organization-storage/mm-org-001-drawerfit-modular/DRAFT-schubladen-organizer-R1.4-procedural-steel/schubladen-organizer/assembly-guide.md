# Montage- und Lageplan – R1.4 DRAFT

Orientierung im eingebauten Zustand: X = links/rechts, Y = Schubladenfront/Rücken, Z = unten/oben.

| Schubladenlage | Moduldatei | Bereich |
|---|---|---|
| links vorn | `DRAFT-driver-front-textured.stl` | Schraubendreherzone vorn |
| links hinten | `DRAFT-driver-back-textured.stl` | Schraubendreherzone hinten |
| rechts vorn | `DRAFT-hardware-front-textured.stl` | Hardwarefächer vorn |
| rechts hinten | `DRAFT-hardware-back-textured.stl` | Hardwarefächer hinten |

## Vor der Vollbaugruppe

1. Stahltextur-Coupon beurteilen und die gewünschte Tiefe festlegen.
2. Connector-Coupons gemeinsam drucken und die reale Passung messen. Die R1.4-Connectoren sind geometrisch unverändert zu R1.3; der früher gemeldete schlechte Sitz ist deshalb erst nach diesem Test geklärt.
3. Eckcoupon im realen Schubladenrand prüfen.
4. Im Ziel-Slicer sicherstellen, dass Textur-Keep-outs und Unterseitenkennzeichnung sauber bleiben.

## Einsetzen

1. Connectorbereiche vollständig von Brim, Stringing und Elefantenfußresten befreien.
2. Die beiden hinteren Module locker zusammenstecken und in die Schublade legen.
3. Die beiden vorderen Module miteinander verbinden und anschließend an die hintere Reihe schieben.
4. Nicht mit Gewalt fügen. Bei zu strammer Verbindung zuerst das Couponmaß auswerten und `connectors.clearance` in 0,05-mm-Schritten erhöhen.
5. Den separaten Schraubendreherkamm quer in die lange linke Zone einsetzen und entlang der Zone an die Werkzeuglängen anpassen.

Die 3MF-Datei enthält die vier Hauptmodule bereits in korrekter Baugruppenposition. Kamm und Coupons werden als separate STL-Dateien geladen.

## Texturpflege

Die Dellen sind flach und breit ausgelegt. Keine aggressiven Metallwerkzeuge zum Reinigen verwenden. Wenn Staub in der 120-%-Couponvariante sichtbar hängen bleibt, die 100-%- oder 75-%-Stufe verwenden und das Modell neu bauen.

