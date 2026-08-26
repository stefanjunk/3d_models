# ZEN KINTSUGI WAVE v2.1 – DRAFT-Release-Kandidat

Status: **DRAFT – finale Modell-/Releasefreigabe und physische Prüfungen stehen aus.**

Diese Version ersetzt den technischen Käfig des Vorgängers durch dünne geschlossene Freiform-Seitenschalen, fünf skulpturale Ovalbänder, eine offene Bandkrone, echte Gold- und Sand-Farbkörper, eine feine keramische Außentextur, schlanke Bronze-/Walnussholme und eine rückwärtige Wellenstrebenstruktur ohne X-Verstrebungen.

## Kernfunktion

- Wandhängender Speicher für fünf Rollen bis Ø 120 × 105 mm.
- Passives FIFO: oben nachfüllen, unten entnehmen, nächste Rolle fällt selbstständig nach.
- Parametrischer Quellcode für 3–8 Rollen.
- Offene Front zeigt den Bestand unmittelbar.
- Abnehmbare rechte Duftstein-Schale.
- Vier benannte PETG-Farbkörper: Elfenbein, Antikgold, Walnuss/Bronze und warmer Sand.

## Digitale Prüfergebnisse

- 122 × 107 mm Prüfrolle: 121 Höhenpositionen, 0 Kollisionen.
- Definierter unterer Rollenanschlag: positiver Eingriff bei 0,6 mm Überfahrt.
- 22 Fertigungs-STLs: nach STL-Roundtrip wasserdicht, konsistente Wicklung, positives Volumen und dokumentierte Körperzahl.
- 5 Multicolor-3MFs: gültige ZIP-/3MF-Struktur, vier Materialgruppen, alle eingebetteten Meshobjekte wasserdicht.
- Unabhängige Release-Regression: PASS; Bericht unter `reports/release-regression-DRAFT.json`.
- Dünnwandige Seite: 1,80 mm nominal; tiefste Inlaytasche 0,38 mm; rechnerische Restwand 1,42 mm.
- Körper ohne abnehmbare Schale: 141,6 × 120,9 × maximal 666 mm.
- Größtes Einzelmodul: 141,6 × 115,9 × 124 mm; alle Teile passen in 420 × 420 × 500 mm.
- CAD-Solidvolumen: 612.553 mm³; 31,20 % weniger als der v2.0-Referenzkörper.
- JSI-WM-001-R1: kompakt, 11,423 × 10,000 mm, ungedreht und normal lesbar, 0,40 mm vertieft; 4,80 mm Reststärke im zentralen Bronzeholm.

Die exakte Druckzeit, Slicermasse, Purge-Menge, Supports und ACE-Slot-Zuordnung müssen noch in **Anycubic Slicer Next** bestätigt werden. Physische FIFO-, Passungs-, Wisch- und Wandmontagetests sind nicht durch digitale Prüfungen ersetzbar.

## Empfohlene Druckreihenfolge

1. `FIT_COUPON_*` gemeinsam laden und Pin-/Taschenpassung prüfen.
2. `TEXTURE_COUPON_ivory.stl` drucken und mit trockenem Papier sowie feuchtem Tuch testen.
3. Ein `MODULE_MIDDLE_A_4COLOR.3mf` drucken und mit zwei realen Rollen als FIFO-Teilprototyp prüfen.
4. Untermodul, zwei Mittelmodule A, zwei Mittelmodule B und Krone einzeln drucken.
5. 20 Verbinder drucken; die im Coupon beste Größe kann über den parametrischen Generator angepasst werden.
6. Erst nach erfolgreicher Trockenmontage die Wandbefestigung mit zur tatsächlichen Wand passenden Schrauben/Ankern ausführen.

## Stückzahlen für fünf Rollen

| Bauteil | Anzahl | Datei |
|---|---:|---|
| Ausgabemodul, vier Farben | 1 | `3MF/MODULE_OUTPUT_4COLOR.3mf` |
| Mittelmodul A, vier Farben | 2 | `3MF/MODULE_MIDDLE_A_4COLOR.3mf` |
| Mittelmodul B, vier Farben | 2 | `3MF/MODULE_MIDDLE_B_4COLOR.3mf` |
| Krone, vier Farben | 1 | `3MF/MODULE_CROWN_4COLOR.3mf` |
| Verbinder Ø 4,8 mm | 20 | `STL/connector_pin_4p8mm_bronze.stl` |
| Duftstein-Schale | 1 | `STL/scent_tray_sand.stl` |
| Wandanker/-schrauben | wandabhängig, maximal 11 Positionen | nicht enthalten |

Die große Baugruppen-3MF dient primär als Farb- und Montagekontrolle; zum Drucken die vier Einzelmodul-3MFs verwenden.

## Startprofil

- Drucker: Anycubic Kobra 3 Max mit ACE 2 Pro.
- Material: vier trockene PETG-Filamente derselben Polymerfamilie.
- Düse 0,4 mm; Linienbreite 0,45 mm; Schichthöhe 0,20 mm.
- Module aufrecht auf Z=0, 4 Wände, 5 obere/untere Schichten, 12–18 % Gyroid als Startwert.
- Lokale organische Supports nur dort, wo die Slicer-Vorschau sie unter Ovalbogen/Krone verlangt; keine Supports im FIFO-Schacht oder in den Inlaytaschen.
- Naht auf rückwärtige Niedrigaufmerksamkeitszonen legen; keine Fuzzy-Skin-Textur ergänzen.
- ACE-Purge-Turm außerhalb der Teile platzieren; Flush-in-Infill zunächst deaktiviert lassen.

## Parametrischer Neuaufbau

```bash
PYTHONPATH=/pfad/zu/python-packages python source/generate_zen_kintsugi_v21.py \
  --output . --roll-diameter 120 --roll-width 105 --roll-count 5 \
  --clearance 4 --quality final

PYTHONPATH=/pfad/zu/python-packages python source/generate_watermark_evidence.py
PYTHONPATH=/pfad/zu/python-packages python source/validate_release_candidate.py
```

Erforderliche Python-Pakete stehen in `source/requirements.txt`. Die Produktionsautorität ist der Generator. Die früheren organischen GLB-Entwürfe wurden nur als Stilreferenzen ausgewertet; sie sind keine Fertigungsgeometrie und deshalb nicht Teil dieses kompakten DRAFT-Pakets. Ihre Herkunft und Prüfsummen bleiben in `specs/organic-source-manifest.json` dokumentiert.

## Wichtige Grenzen

- Stark feuchte, gequetschte, übergroße oder ovale Rollen können trotz geometrischer Reserve klemmen.
- Die Wandbefestigung hat keine universelle Traglastfreigabe. Schrauben und Anker müssen zum realen Untergrund passen und physisch geprüft werden.
- Die Duftschale ist nur für einen trockenen Duftstein gedacht, nicht für Flüssigkeiten oder offenes Duftöl.
- STEP wurde nicht erzeugt: Die sichtbare Architektur ist eine reproduzierbare parametrische Mesh-/Freiformkonstruktion; im validierten Build war kein B-Rep-Kernel verfügbar.
- Die Markierung identifiziert das Produkt, ersetzt aber keine Marken-, Design-, Sicherheits- oder Rechtsprüfung.

Alle offenen Prüfungen und Akzeptanzkriterien stehen in `specs/design-spec.yaml`, `reports/slicer-preflight-DRAFT.json` und `tests/test-plan.yaml`.
