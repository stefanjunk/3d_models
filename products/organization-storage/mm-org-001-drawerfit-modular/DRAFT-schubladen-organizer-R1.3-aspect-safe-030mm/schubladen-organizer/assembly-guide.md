# Montage- und Lageplan – DRAFT

Orientierung im eingebauten Zustand: X = links/rechts, Y = Schubladenfront/Rücken, Z = unten/oben.

| Schubladenlage | Moduldatei | Baugruppenbereich |
|---|---|---|
| links vorn | `DRAFT-R2-driver-front-procedural-wood-unmarked.stl` | Schraubendreherzone vorn |
| links hinten | `DRAFT-R2-driver-back-procedural-wood-unmarked.stl` | Schraubendreherzone hinten |
| rechts vorn | `DRAFT-R2-hardware-front-procedural-wood-unmarked.stl` | Hardwarefächer vorn |
| rechts hinten | `DRAFT-R2-hardware-back-procedural-wood-unmarked.stl` | Hardwarefächer hinten |

## Einsetzen

1. Alle Connector-Bereiche nach dem Druck vollständig von Brim- oder Elefantenfußresten befreien.
2. Zuerst die beiden hinteren Module locker zusammenstecken und in die Schublade legen.
3. Die beiden vorderen Module miteinander verbinden und anschließend an die hintere Reihe schieben.
4. Nicht mit Gewalt fügen. Bei zu strammer Verbindung zuerst das Connector-Couponpaar auswerten und den Parameter `connectors.clearance` erhöhen.
5. Den separaten Schraubendreherkamm quer in die lange linke Zone einsetzen; seine Position kann entlang der Zone an die Werkzeuglängen angepasst werden.

`output/DRAFT/DRAFT-R2-procedural-wood-assembly.3mf` enthält die vier Hauptmodule bereits in ihrer korrekten Baugruppenposition. Der Kamm und die Coupons werden als separate R2-STL-Dateien geladen. Die aktuelle 3MF ist ein absichtlich unmarkierter DRAFT und noch keine finale Fertigungsfreigabe.
