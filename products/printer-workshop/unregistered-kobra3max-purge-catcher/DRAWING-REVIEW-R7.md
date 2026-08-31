# Zeichnungsprüfung – R7-REQ5-DWG-001

## Status

- Anforderungsrevision: `0.7.0-requirements.5`
- Anforderungsfreigabe: aus der Benutzeranweisung „erstelle erstmal eine bemaßte zeichnung“ als Freigabe für dieses Prüfblatt erfasst
- Zeichnungs-/Konzeptfreigabe: **durch Stefan am 31. August 2026 freigegeben**
- Freigabeevidenz: Benutzerantwort „freigegeben“
- Produktions-CAD, Fertigungs-3MF und Slicing: **weiter durch Preflight und offene physische Interface-Gates gesperrt**

## Dateien

- Prüfansicht: `drawings/R7-REQ5-DWG-001-dimensioned-concept.png`
- editierbare Vektorquelle: `drawings/R7-REQ5-DWG-001-dimensioned-concept.svg`
- druckbares Blatt: `drawings/R7-REQ5-DWG-001-dimensioned-concept.pdf`

SHA-256:

- PNG: `f232575f1a235ccaa6df0462d0ea5ec3aafd5334f679a95260b54133bf403d7b`
- SVG: `d0fdf7b19a6ddf4a30557ec7c87b871c244be1040a75f7642f7eecca0b667925`
- PDF: `9a03557aca76e36928005b8c257ffc4c907cc2b89ded8994f88b300336dd0b57`

## Gezeigte Anforderungen

| Anforderung | Darstellung |
|---|---|
| einteilig und direkt verschraubt | integrale massive Schraubenzone am Umlenkerkörper |
| zwei vorhandene Wiper-Schrauben | zwei vertikale Lochachsen; 17 mm Mitte–Mitte |
| kein Clip oder Verschluss | fester Schnitt; Demontagehinweis nur durch vollständiges Lösen beider Schrauben |
| bodenlos | offener unterer Querschnitt und freie Fallpfeile |
| offene Wabenwände | offene schematische Wabenfelder auf Front und Seite |
| eigenes Logo mittig | mittige massive Logo-Insel auf der sichtbaren Hauptwand |
| eigene Messwerte | 17/10/37/40-mm-Datumsansichten |
| eigener Fangkopf | 62 × 44 × 62 mm, 12-mm-Haube und 57 × 39 mm freie Fallöffnung |

## Verbindlich eingetragene Eigenmaße

- vertikaler Schraubenabstand: `17 mm`
- untere Schraubenmitte bis Purge-Ablageebene: `10 mm`
- Schraubendatum bis horizontale Purge-Wurfbahn: `37 mm`; Achse und Enddatum vor CAD nochmals real bestätigen
- Schraubenebene bis rückwärtige Wiper-Ausdehnung: `40 mm`
- eigener Funktionskörper: Fangbereich `62 × 44 mm`, Prallwandhöhe `62 mm`, Haube `12 mm`, freie Fallöffnung `57 × 39 mm`

## Bewusst nicht erfunden

- Gewinde-/Schaftdurchmesser und Lochspiel
- Kopf-Ø, Kopfhöhe und Werkzeugzugang
- vorhandene Schraubenlänge, gedruckte Auflagendicke und verbleibender Gewindeeingriff
- vollständige Wiper-, Bett-, Rollen-, Kopf-, Kabel- und Servicehüllkurve
- endgültige Position und äußere Kontur des Fangkörpers relativ zur Maschine
- Wabenzellengröße, Wandstärken, Radien und Fertigungstoleranzen

Diese Punkte sind im Blatt rot als `TBD` gekennzeichnet. Die gestrichelte
Umlenkerkontur ist schematisch und darf nicht vermessen oder in CAD übertragen
werden.

## Clean-Room-Grenze

Die Drittanbieter-3MF wurde weder importiert noch nachgezeichnet. Das Blatt
verwendet nur die eigene R6-Fanggeometrie, eigene Benutzermaße, eigene Fotos und
die ausdrücklich gewählte neue Architektur.

## Erfasste Entscheidung

Stefan hat das Blatt mit „freigegeben“ bestätigt. Die Freigabe umfasst Lage und
Richtung der dargestellten Datumsbezüge, Formrichtung, direkte feste
Zweischraubenarchitektur, Waben-/Logoanordnung und bodenlosen Schnitt.

Sie erlaubt die Parametrik- und Couponplanung, aber noch keine Behauptung
physischer Passung. Rot markierte `TBD`-Werte bleiben ungelöst und dürfen nicht
aus der Zeichnung skaliert werden.
