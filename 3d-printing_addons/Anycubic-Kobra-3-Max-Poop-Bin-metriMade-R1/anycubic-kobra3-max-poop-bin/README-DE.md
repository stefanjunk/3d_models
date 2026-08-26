# Anycubic Kobra 3 Max Poop Bin — metriMade R1

Eigenständig konstruierter, parametrischer Auffangbehälter für Filamentreste am Purge-Wiper des Anycubic Kobra 3 Max. Der Satz enthält einen großen Behälter, eine getrennte verstellbare Halterung, eine dünne Befestigungslehre und ein optionales vierfarbiges `metrimade.com`-Badge.

## Wichtig vor dem großen Druck

Die offiziellen Anycubic-Unterlagen zeigen zwei Befestigungsschrauben und Positionierbohrungen, veröffentlichen aber keinen Lochabstand. Deshalb zuerst nur `kobra3-max-poop-bin-mount-fit-gauge.stl` drucken. Die Langlochlehre deckt nominell 8–48 mm Schraubenabstand ab. Passt sie nicht kollisionsfrei, `params/mount-bracket.json` anpassen und neu generieren.

Die Ersatzteilseite nennt für den Purge Wiper zwei M3×7-Schrauben. Für die 3,2-mm-Halterplatte ist M3×10 ein plausibler Startwert, aber Gewindeeingriff und mögliches Aufsetzen im Sackloch müssen am realen Drucker geprüft werden. Schrauben niemals mit Kraft eindrehen.

## Dateien

- `build/exports/kobra3-max-poop-bin-kit.3mf` — Behälter, Halter und Lehre auf einem Kobra-3-Max-Druckbett
- `build/exports/kobra3-max-poop-bin-balanced.stl` — ausgewählter Behälter
- `build/exports/kobra3-max-poop-bin-mount-fit-gauge.stl` — zuerst drucken
- `build/exports/kobra3-max-poop-bin-mount-bracket.stl` — verstellbare Halterung
- `build/exports/metrimade-badge-4color.3mf` — vier getrennte Farbsolids
- `build/exports/metrimade-badge-*.stl` — dieselben Badge-Farben einzeln
- `build/variants/` — kompakte, ausgewogene und große Behältervariante
- `src/generate_poop_bin.py` + `params/*.json` — editierbare Quelle

## Gewählte Variante

| Variante | Nutzvolumen bis zur niedrigen Frontkante | geometrische PETG-Masse | Status |
|---|---:|---:|---|
| compact | 1,37 l | ca. 217 g | Mesh PASS |
| balanced | 1,86 l | ca. 263 g | **ausgewählt; Mesh PASS** |
| high-capacity | 2,61 l | ca. 355 g | Mesh PASS |

Die Masse ist aus dem geschlossenen CAD-Volumen mit 1,27 g/cm³ berechnet, nicht aus einem Slicer. Druckzeit, Stützmaterial und tatsächlicher Filamentverbrauch sind deshalb noch nicht verifiziert.

## Abmessungen der ausgewählten Version

- Außenmaß inklusive Rand: 168 × 118 × 152 mm
- Boden außen: 150 × 102 mm
- Oberkante außen ohne Rand: 162 × 112 mm
- Front-/Rückwandhöhe: 124 / 152 mm
- Wand / Boden: 2,4 / 2,6 mm
- Badge: 100 × 44 × 2,0 mm; Farbrelief 0,6 mm
- Halter: 68 × 42 × 14 mm; 52 × 4 mm Langloch; Hakenmitten 44 mm

## Empfohlene Druckreihenfolge

1. **Lehre:** PETG, 0,20-mm-Schicht, 100 % Infill, ohne Support. Mit den vorhandenen Schrauben nur locker anhalten; Lochlage, Gehäusefreiheit und Auswurfrichtung prüfen.
2. **Halter:** PETG, 0,20 mm, 5 Perimeter, 100 % Infill, ohne Support. Exportierte flache Seite auf dem Bett lassen.
3. **Behälter:** PETG, 0,20 mm, 4–5 Perimeter, 5 Bodenschichten, 0 % Infill, ohne Support; Naht nach hinten, bei Bedarf 4–8 mm Brim.
4. **Badge:** flach drucken; Sand, Navy, Teal und Aqua den vier ACE-Slots zuweisen. Für Beschriftung auf beiden Seiten das Badge im Slicer zweimal platzieren. Mit dünnem, PETG-tauglichem Klebeband oder Klebstoff auf die ebenen Seitenflächen setzen.

Vor dem ersten unbeaufsichtigten Einsatz den gesamten X/Y/Z-Verfahrweg langsam prüfen. Behälter und Halter dürfen weder Bett, Werkzeugkopf, Kabel, Wischer noch ausgeworfenes Material behindern. Nach einem kurzen Purge-Test kontrollieren, ob alle Reste sicher in den Behälter fallen.

## Regenerieren

Im Projektordner:

```bash
python3 src/generate_poop_bin.py
```

Das Skript verwendet nur NumPy, Pillow und Matplotlib. Alle Maße stehen in JSON-Dateien unter `params/`. Das Original-SVG liegt unverändert unter `evidence/` und wird über seinen SHA-256-Hash nachverfolgt.

## Validierungsstatus

- Alle sieben STL-Solids: geschlossen, positive Volumina, keine Rand-, Non-Manifold-, degenerierten oder doppelten Flächen
- Beide 3MF-Pakete: ZIP/XML, Objektverweise, Dreiecksindizes und Materialien PASS
- Behälter, Halter und Badge liegen mit ihrer vorgesehenen Druckfläche auf Z=0
- Noch offen: Slicer-Vorschau/G-Code, reale Lochlage, Kollisionsfreiheit, Fallweg, Haltbarkeit und optische Freigabe

Die Dateien sind deshalb ein **geometrisch validierter Prototypensatz**, noch kein physisch freigegebenes Serienprodukt.

