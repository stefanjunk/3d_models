# Recherche- und Ableitungsprotokoll

Stand: 2026-08-26 · Revision R5-wraparound-cover

## Primärquellen

1. Anycubic, **Kobra 3 Max – Print head cooling fan replacement guide**  
   https://wiki.anycubic.com/en/fdm-3d-printer/kobra-3-max/print-head-cooling-fan-replacement-guide

   Beobachtungen: zentraler runder Lüftereinlass; die Serienfront ist eine räumliche Schale. Nach dem Lösen zweier rückseitiger Schrauben wird sie seitlich zusammengedrückt und abgezogen. Die Anleitung zeigt Front-, Rück- und Innenansichten, aber keine bemaßte Schalenzeichnung und keinen Lüfterringdurchmesser.

2. Anycubic, **Kobra 3 Max – Model cooling fan replacement guide**  
   https://wiki.anycubic.com/en/fdm-3d-printer/kobra-3-max/model-cooling-fan-replacement-guide

   Beobachtungen: Der untere Modellkühlkanal ist ein separates, abnehmbares Bauteil und bleibt ein freizuhaltender Keep-out. Das neue Cover endet oberhalb dieses Bereichs.

3. Anycubic, **Kobra 3 Max product page / specifications**  
   https://store.anycubic.com/products/kobra-3-max

   Beobachtungen: Standarddüse 0,4 mm, PETG-Unterstützung und 420 × 420 × 500 mm Bauvolumen. Diese Werte steuern den Fertigungsrahmen, nicht die unsichere Clipschnittstelle.

## Bildskalierung und Designmargen

Die annähernd frontale Serviceaufnahme wurde nur als Proportionsquelle verwendet. Die vorhandene Auswertung ergab ungefähr 254 px maximale Serienfrontbreite, 313 px Hauptschalenhöhe und 202 px für den äußeren runden Frontring. Mit D52 als reinem Ring-Startkandidaten entspricht das ungefähr 65,4 × 80,6 mm.

R5 übernimmt diese Werte nicht als Kopie der Serienkontur. Für einen sichtbaren Vollfront-Rahmen wurden bewusst Fertigungs- und Kameramargen hinzugefügt:

| Merkmal | R5-Entscheidung | Begründung |
|---|---:|---|
| sichtbare Front | 72 × 88 mm | vollständiger Rahmen außerhalb des geschätzten Serienumrisses; gerundete/chamfered Eigenkontur |
| äußerste Breite | 74,4 mm | vier seitliche, federnde Stabilisatoren |
| räumliche Tiefe | 10,8 mm | flache offene Schale statt zweidimensionaler Blende |
| vorläufige Seitenpassung | 69,0 mm | bildbasierter Startwert; sekundäre Stabilisierung, nicht primäres Datum |
| Lüfterring | D50/D52/D54 | physische Passrahmen statt behauptetem Herstellermaß |

Die Außenkontur ist eine unabhängige polygonale Konstruktion. Der Lüfterring bleibt das primäre Montagedatum; die vier seitlichen Finger reduzieren nur Rotation und Flattern. Dadurch ist eine moderate Abweichung der Serienbreite leichter korrigierbar als bei einer vollständig formschlüssigen Ersatzschale.

## Community-Referenzen ohne Geometrieübernahme

Öffentlich sichtbare Seiten und statische Vorschaubilder mehrerer Kobra-3-Cover wurden darauf geprüft, welche Montageprinzipien vorkommen. Besonders relevant war ein ausdrücklich als „reverse engineered“ gekennzeichnetes Referenzmodell mit flacher Frontschale und vier seitlichen Ansätzen:

https://3dgo.app/models/printables/1323789

Die Seite nennt CC BY-SA und weist selbst auf Maßabweichungen hin. Deshalb wurde keine STL-/CAD-Datei geladen, importiert, vermessen oder nachgezeichnet. Ausschließlich folgende abstrakte Prinzipien flossen in die eigenständige Konstruktion ein: räumliche statt flache Front, vier lokale Seitenstabilisierungen, offene Rückseite und ein vollständiger Passrahmen vor dem Hauptdruck. Die statischen Arbeitsbilder werden ebenso wie Herstellerfotos aus dem auslieferbaren ZIP ausgeschlossen.

## Evidenzklassen

| Aussage | Klasse | Vertrauen |
|---|---|---|
| Lüfter sitzt zentral hinter der runden Frontöffnung | beobachtet, offizielle Fotos | hoch |
| Serienfront ist eine abnehmbare räumliche Schale | beobachtet/beschrieben, offizielle Anleitung | hoch |
| Zwei Schrauben und seitliches Zusammendrücken gehören zur Serienmontage | beschrieben, offizielle Anleitung | hoch |
| Unterer Modellkühlkanal muss frei bleiben | beobachtet, offizielle Anleitung | hoch |
| D52 ist ein sinnvoller Ring-Startkandidat | aus unkalibrierten Fotos abgeleitet | niedrig |
| 72 × 88 mm ist eine geeignete Vollfront-Hülle | unabhängige Designentscheidung | mittel-niedrig |
| 69,0 mm eignet sich für die seitlichen Stabilisatoren | bildbasierte Designannahme | niedrig |
| Grobe modellierte Waben sind für den Slicer portabler als wallless Infill | Fertigungsentscheidung | hoch |
| PETG eignet sich für die federnden Clips | Designannahme; physisch zu prüfen | mittel |

## Markenquelle

Der Projektinhaber lieferte `metrimade-lockup-horizontal-color.svg` als alleinige Markenquelle. Bildmarke und Schriftzug werden getrennt skaliert: 30 mm hohe perforierte Bildmarke im Lüfterkreis und 48 mm breiter Schriftzug auf der geschlossenen oberen Fläche. Formen, vier sRGB-Farben und SHA-256 der Quelldatei sind im Paket dokumentiert.
