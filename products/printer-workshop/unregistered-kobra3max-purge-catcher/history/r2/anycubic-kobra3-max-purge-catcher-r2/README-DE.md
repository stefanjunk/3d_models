# Anycubic Kobra 3 Max – metriMade Waben-Fangkorb R2

Der kleine Fangkorb sitzt an der Purge-/Wischereinheit, bremst seitlich wegfliegende Filamentreste und leitet sie durch den offenen Auslass nach unten. Der große Behälter steht **lose und mechanisch unabhängig** darunter. Nur der Fangkorb wird am Drucker verschraubt.

![Montageprinzip](previews/assembly-principle.png)

## Wabenaufbau

Die drei sichtbaren Seiten sind nicht offen perforiert. Sie bestehen aus einer durchgehenden 1,0-mm-Innenhaut und 1,5 mm tiefen äußeren Wabenrippen. Dadurch bleiben auch dünne Purge-Fäden im Fangkorb. Trichter, Ober- und Seitenkanten, rückseitige Befestigungsplatte und die Logo-Auflagen sind massiv.

- Wabenzellradius: 5,5 mm
- sichtbare Rippenbreite: 1,5 mm
- vollständige Wanddicke an Rippen und Rahmen: 2,5 mm
- rechnerische Körpervolumen-Reduktion gegenüber vollflächigen 2,5-mm-Wänden: ca. 8,46 %

## Exaktes Logo

Verwendet wird ausschließlich `evidence/metrimade-lockup-stacked-color.svg`. Die vollständige SVG-`viewBox`, Pfadpositionen, Gruppentransformationen, Zeichenreihenfolge, Symbol, Schriftzug und vier Originalfarben bleiben erhalten. Es gibt keinen Zusatztext und keinen Zuschnitt.

Das vollständige Lockup wird auf drei verfügbaren Außenseiten direkt mitgedruckt:

- Vorderseite `−Y`
- linke Seite `−X`
- rechte Displayseite `+X`

![Logo auf drei Seiten](previews/three-side-stacked-logo.png)

Ein neutralweißer Fangkorb plus die vier unveränderten Logofarben benötigt **fünf Materialzuweisungen**. Ein Vierfach-Farbsystem kann diese Kombination nicht in einem einzigen unveränderten Mehrfarbdruck ausgeben. Möglich sind dann ein bewusst monochromer Druck, eine zusammengelegte Farbe oder eine separate Nachbearbeitung.

## Dateien und Zusammenbau

Empfohlene Druckjobs:

1. `models/3mf/mount-fit-gauge-core.3mf` – zuerst die unbekannte Befestigungszone prüfen.
2. `models/3mf/metriMade-purge-catcher-3sides-5material-core.3mf` – kleiner Waben-Fangkorb.
3. `models/3mf/lower-bin-core.3mf` – großer freistehender Behälter.

Es gibt **keine mechanische Verbindung** zwischen Fangkorb und Unterbehälter. Der Fangkorb wird an der Wischereinheit verschraubt; der Behälter wird mit 10–40 mm Start-Luftspalt direkt unter den Auslass gestellt.

## STL-Fallback für Anycubic Slicer Next

Wenn der Slicer den Core-3MF weiterhin nicht öffnet, diese fünf Fangkorb-STLs **gemeinsam** importieren und als ein Objekt mit mehreren Teilen behandeln:

- `models/stl/catcher-body-white-honeycomb.stl`
- `models/stl/catcher-logo-navy-3sides.stl`
- `models/stl/catcher-logo-teal-3sides.stl`
- `models/stl/catcher-logo-aqua-3sides.stl`
- `models/stl/catcher-logo-sand-3sides.stl`

Die Teile teilen dasselbe Koordinatensystem. Nicht einzeln automatisch anordnen oder zentrieren. Das Körper-STL enthält den vollständigen funktionsfähigen Fangkorb; für einen monochromen Test können alle fünf Teile demselben Filament zugeordnet werden.

Die [offizielle Kurzanleitung](https://wiki.anycubic.com/en/software-and-app/new-page-anycubic-slicer-beta(orca-version)/anycubic-slicer-next-slicing-software-quick-start-guide) nennt `.3mf` und `.stl` als Importformate. Die Anycubic-Funktion [Split to Objects/Parts](https://wiki.anycubic.com/en/software-and-app/new-page-anycubic-slicer-beta(orca-version)/split-to-objects/parts) beschreibt die Objekt-/Teilbehandlung.

## Druckeinstellungen als Startpunkt

| Einstellung | Fangkorb | Unterbehälter | Messlehre |
|---|---:|---:|---:|
| Material | PETG | PETG | PETG/Restmaterial |
| Düse | 0,4 mm | 0,4 mm | 0,4 mm |
| Schichthöhe | 0,20 mm | 0,20–0,28 mm | 0,20 mm |
| Wände | 4 | 4 | 3 |
| Infill | 0–10 % | 0 % | 100 % durch geringe Dicke |
| Support | aus | aus | aus |
| Brim | 5 mm empfohlen | optional | nicht nötig |
| Orientierung | Auslassring auf Druckbett | Boden auf Druckbett | flach |

Die drei vertikalen Logos erzeugen viele Farbwechsel. Vor dem Export Farbwechselzahl, Purge-Tower, Abfallmenge und Druckdauer kontrollieren. Ein 30–40 mm breiter Wand-/Logo-Ausschnitt ist als Materialtest sinnvoll, bevor der vollständige Mehrfarbdruck gestartet wird.

## Konstruktionsdaten und offene Passung

- Fangkorb: ca. 88 × 63 × 84 mm, freier Auslass ca. 51 × 31 mm.
- Fangtrichter: maximal ca. 29,7° von der Vertikalen.
- Montierter PETG-Anteil inklusive drei Logos: geometrisch ca. 62,6 g.
- Unterbehälter: ca. 173 × 127 × 125 mm, rechnerisch ca. 1,75 l nutzbares Volumen.

Die [offizielle Kobra-3-Max-Produktansicht](https://store.anycubic.com/products/kobra-3-max) zeigt das Display vorne rechts; deshalb ist `+X` die Displayseite. Die [offizielle Purge-Wiper-Reparaturanleitung](https://wiki.anycubic.com/en/fdm-3d-printer/kobra-3-max/purge-wiper-components-replace-guide) enthält keine Maßzeichnung. Lochabstand, lokaler Bewegungsraum und Schraubenlänge müssen daher mit der Messlehre und am ausgeschalteten Drucker geprüft werden. M3×10 ist nur ein zu prüfender Startkandidat.

## Status

Eigene Geometrie-/Manifoldprüfung, Logo-Quelltreue und Standard-Core-3MF-Struktur: **PASS**. Anycubic-Slicer-Vorschau, Maschinenpassung und Purge-Funktion: **offen**. Die Reihenfolge und Stop-Kriterien stehen in `PRINT-CHECKLIST-DE.md`.

Reproduzierbarer Neuaufbau:

```bash
python src/generate_purge_catcher.py
```
