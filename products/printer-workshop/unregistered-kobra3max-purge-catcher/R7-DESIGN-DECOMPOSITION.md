# R7 DRAFT-2 – Funktionszerlegung und Fertigungsarchitektur

## Status und Geltungsbereich

- Anforderungsrevision `0.7.0-requirements.2`: freigegeben
- Konzept `R7 Z-Rider v1`: freigegeben
- Geometriephase: `R7-DRAFT-2`, digital und couponpflichtig
- Physischer Sitz, Schraubeneingriff, Vollweg und Purge-Funktion: noch nicht qualifiziert
- Drittanbieterdateien: keine Geometrie-, Maß- oder Bildquelle

## Gemeinsames Bezugssystem

Der Ursprung liegt in der Mitte der unteren Wiper-Schraube auf der Schraubenauflageebene.

- `+X`: horizontal von der Schraubenachse durch das 37-mm-Purge-Datum zur Prallwand
- `+Y`: normal zur Schraubenauflage nach vorn und in Richtung der werkzeuglosen Entnahme; der gemessene rückwärtige Wiper-Raum liegt in `−Y`
- `+Z`: nach oben

Die untere Schraube liegt bei `(0, 0, 0)`, die obere bei `(0, 0, 17)`. R7-DRAFT-2 bindet die übrigen Benutzermaße direkt: Purge-Ablagedatum `Z=-10`, Fangmittelebene `X=37` und rückwärtige Wiper-Keep-out-Grenze `Y=-40`. Sämtliche neue Fertigungsgeometrie bleibt auf oder vor `Y=0`. Die Werte werden nicht aus Foto- oder Konzeptproportionen rekonstruiert.

## Komponenten

| ID | Art | Aufgabe | Wartung / Status |
|---|---|---|---|
| `WIPER_DATUM_PLATE` | PETG-Druckteil | Einmalige Verbindung zum bewegten 17-mm-Schraubendatum; trägt zwei kurze horizontale Führungsleisten und den Rastanschlag | Bleibt bei normaler Reinigung montiert; DRAFT bis Schrauben- und Vollwegcoupon |
| `MOVING_CATCHER` | PETG-Druckteil | R6-abgeleiteter Fangraum mit geschlossener Trefferzone, glatter Haube, offener Unterseite, großen Wabenöffnungen und integrierten Gegenführungen | Werkzeuglos nach `+Y` entnehmbar; DRAFT bis Pass-/Purge-Test |
| `PRINTED_LATCH` | integrierte PETG-Federzunge | Verhindert selbsttätige Entnahme; wird zum Lösen in `+X` gedrückt | 100 Zyklen auf eigenem Coupon erforderlich |
| `WIPER_FASTENERS` | vorhandene bzw. maßgerecht längere Metallschrauben | Klemmen die Datumplatte an der realen Wiper-Lasche | Gewinde, Kopf, Länge, Festigkeitsklasse, Bauteildicke und Restgewindeeingriff offen |
| `STATIONARY_BIN` | späteres PETG-Druckteil oder geeigneter vorhandener Behälter | Nimmt den frei fallenden Purge auf, ohne am Wiper mitzufahren | Größe und Lage erst nach neun markierten Flugbahntests |

## Neue Schnittstelle

Die feste Platte besitzt zwei in `Y` verlaufende, im `X/Z`-Querschnitt hinterschnittene 45°-Führungsleisten. Ihre Zentren liegen bei `Z=-8,5` und `Z=+8,5`, also außerhalb der angenommenen Schraubenkopf-Keep-outs. Der Fangkopf besitzt zwei offene Gegenkanäle mit Frontanschlag.

Zum Einsetzen wird der Fangkopf höchstens 12,6 mm entgegen `+Y` bewegt. Die obere Rastzunge läuft über einen eigenen Anschlag und schnappt formschlüssig hinter dessen Y-Flanke. Zum Reinigen wird die Zunge in `+X` bis zum gedruckten Hartanschlag gedrückt und der Fangkopf nach `+Y` abgezogen.

Die Geometrie besitzt zwei räumlich getrennte Führungsdatums. Die Rastung trägt nicht die Führungs- oder Biegelast; sie verhindert nur die Rückbewegung.

## Geschützte Regionen

- Schraubenauflageebene, unteres Runddatum und oberes toleranzausgleichendes Langloch
- beide Führungsquerschnitte, Kanalanschläge und die vollständige 12,6-mm-Servicebahn
- Rastwurzel, Federzunge, Haken, Gegenanschlag und Überbiege-Hartanschlag
- 62 × 44 mm R6-Fanghülle, Trefferband, Haube, Seitenwangen und offene Unterseite
- Purge-Flächen ohne horizontale Tasche oder Sackraum
- Wiper-, Bett-, Kopf- und Kabel-Keep-outs, sobald sie physisch erfasst sind
- spätere `metriMade.com`-Kennzeichnung als letzte Geometrieänderung

## Leichtbauentscheidung

R6 hatte digital rund 31,99 g bewegte PETG-Masse. DRAFT-2 hält die 62 × 44 × 62-mm-Fanghülle, verwendet in der ausgewählten Variante 1,35-mm-Wabenschalen und 1,60-mm-Vollwände sowie lokale Vollbereiche an Trefferzone, Seitenwangen, Schraubenplatte, Führungen und Rastung. Platte plus Fangkopf liegen digital bei rund 24,44 g und damit unter dem 25-g-Projektziel. Dieses Ziel ersetzt keine Herstellerlastfreigabe.

## Coupons vor Vollteil

1. `mount-pattern-gauge`: 17-mm-Abstand, unteres Rundloch und oberes Langloch; prüft nur Lage und Kopfauflage.
2. `lateral-slide-male` plus Gegenstücke mit 0,20 / 0,30 / 0,40 mm nominellem Flächenspiel.
3. `latch-cycle-coupon`: gleiche Federlänge, Dicke, Rampenhöhe und Hartanschlag wie DRAFT-1.
4. `mounted-clearance-stub`: Platte mit Führungen, aber ohne Fanghülle; stromloser X/Y/Z-Vollweg vor Montage des Vollteils.

Erst nach Schraubenidentifikation und Couponwahl wird die reale Schraubenlänge festgelegt. Erst nach markierten Niedrig-/Mittel-/Hoch-Z-Auswürfen wird der stationäre Behälter konstruiert.

## Druck- und Hardwareannahmen

- Anycubic Kobra 3 Max, 0,4-mm-Düse, 0,20-mm-Schichten, 0,45-mm-Linienbreite
- PETG als Zielmaterial; DRAFT-Slicing darf das vorhandene SUNLU-PETG-Profil verwenden, ist aber keine universelle Materialqualifikation
- Fangkopf auf der offenen Unterkante stehend; Haubenprofil höchstens 45° von der Vertikalen
- Datumplatte mit Schraubenauflagefläche auf dem Bett; Führungen wachsen nach oben
- keine Magnete, Klebstoffe, Inserts oder zusätzlichen Metallteile im DRAFT-Schnellverschluss
