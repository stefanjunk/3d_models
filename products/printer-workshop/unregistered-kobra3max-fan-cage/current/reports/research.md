# Recherche- und Ableitungsprotokoll

Stand: 2026-08-26

## Primärquellen

1. Anycubic, **Kobra 3 Max – Print head cooling fan replacement guide**  
   https://wiki.anycubic.com/en/fdm-3d-printer/kobra-3-max/print-head-cooling-fan-replacement-guide

   Beobachtungen: mittiger runder Lüftereinlass an der Frontschale; separate Modellkühl- und Druckkopfkühl-Lüfter; Frontschale wird nach Entfernen der Luftdüse über zwei rückseitige Schrauben gelöst und seitlich gedrückt. Die Fotos zeigen einen erhabenen runden Frontring, veröffentlichen aber keine Maße.

2. Anycubic, **Kobra 3 Max product page / specifications**  
   https://store.anycubic.com/collections/kobra-3-series/products/kobra-3-max

   Beobachtungen: Standarddüse 0.4 mm; PETG wird als unterstütztes Material geführt; Bauvolumen 420 × 420 × 500 mm. Diese Angaben steuern Druckprofil und Bettprüfung, nicht die Clipschnittstelle.

## Nicht übernommene Quellen

Suchtreffer zu fremden Fankäfigen, Fan-Ducts und Cover-Modellen wurden nicht als Geometriequelle verwendet. Es wurde keine Fremddatei heruntergeladen oder geöffnet. So bleibt die Formgebung eigenständig und es entsteht keine unklare Remix-/Lizenzkette.

## Evidenzklassen

| Aussage | Klasse | Vertrauen |
|---|---|---|
| Lüfter sitzt mittig hinter der runden Frontöffnung | beobachtet, offizielle Fotos | hoch |
| Frontschale besitzt einen erhabenen runden Außenring | beobachtet, offizielle Fotos | hoch |
| Originalschale wird rückseitig verschraubt und seitlich gelöst | beobachtet/beschrieben, offizielle Anleitung | hoch |
| Erhabener Ring liegt ungefähr im Bereich 50–54 mm Außendurchmesser | aus unkalibrierten Fotos abgeleitet | niedrig |
| D52 ist der beste digitale Startkandidat | Designentscheidung | mittel-niedrig |
| PETG ist für die Schnappsegmente geeignet | Designannahme; physisch zu prüfen | mittel |

## Markenquelle

Der Projektinhaber lieferte `metrimade-lockup-horizontal-color.svg` als maßgebliche Markenquelle. Die 13 bereits in Pfade umgewandelten Formen und ihre vier sRGB-Farben werden ohne Fremdschrift und ohne Neuzeichnung übernommen. Für FDM werden die Pfade lediglich einheitlich auf eine 56-mm-ViewBox-Breite skaliert und auf das deterministische 0,20-mm-Fertigungsraster abgebildet. Die Quelldatei und ihr SHA-256 sind im Paket dokumentiert.
