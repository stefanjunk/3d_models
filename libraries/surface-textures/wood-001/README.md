# wood-001 — FDM-Holzgravur-Rezept

Wiederverwendbares Texturrezept für die Holz-Optik, die beim Honeycomb-Wandregal
(`mm-wall-001`) im Produktionsdruck ein sehr gutes Ergebnis erzielt hat.

## Warum dieses Rezept funktioniert

- **Orientierung:** Die texturierten Wände stehen vertikal; die Maserung
  (Bild-u-Achse) läuft entlang Modell-Z. Damit lösen die 0,12-mm-Schichten die
  feinen Rillen auf, während die langsame Variation quer dazu mit 0,45-mm-Meshpitch
  und 0,4-mm-Düse problemlos reicht.
- **Tiefe:** 0,6 mm Gravur = exakt 5 Layer bei 0,12 mm Schichthöhe → klar lesbar.
- **Kachel:** nahtlos periodisch nutzbar; durchgehender Umfangsparameter ohne
  Maserungsneustart pro Fläche; Edge-Taper 1,2 mm lässt die Gravur an Kanten
  auf null auslaufen (wasserdichte Stöße).
- **Kosten:** Das Bild-Sampling ist schnell; der Aufwand entsteht durch die
  Dreieckszahl. Pitch-Staffelung (0,45 mm Hero / 0,7 mm sekundär) und die
  Beschränkung auf Sichtflächen halten Teile unter 1M Dreiecken.

## Bekannte Misserfolgs-Kontexte (nicht wiederholen)

- Feine Muster auf **horizontalen Flächen**: Detail landet in XY und wird durch
  die 0,4-mm-Düse verschmiert (Beispiel: `mm-org-001` Bildgravur auf Böden).
- Bild-Kacheln ohne Aspect-/Nahtkontrolle: Stretching und harte Tile-Nähte
  (dokumentiert im `mm-org-001` Decision-Log R1.2/R1.3).
- Subprozess-Detail (Kratzer, Poren) als Geometrie: gehört in Material und
  Slicer-Pfadrichtung, nicht ins Mesh.

## Inhalt

| Datei | Zweck |
| --- | --- |
| `master/wood-001-tile-16bit.png` | Geometrie-Master (16 Bit, bit-treu aus `holz.png`) |
| `master/wood-001-tile-16bit.png.source.json` | Registrierung: Quelle, SHA-256, Konvertierung, Nahtmetriken |
| `recipe.json` | Tiefen, Taper, Pitches, Orientierungsregeln, Keep-outs, Budgets |
| `build_master.py` | deterministischer Neubau des Masters; `--blend-px N` aktiviert einen periodischen Kantenverschnitt |

## Anwendung

1. Zielobjekt so orientieren, dass Texturflächen vertikale Wände sind.
2. Nur gewählte Flächengruppen texturieren; Keep-outs aus `recipe.json` glatt lassen.
3. Pitch nach `recipe.json` staffeln; Triangle-Budget vor der Geometrie mit dem
   `3d-print-heightmap-relief`-Budgetskript prüfen.
4. Restwandstärke ≥ 2,0 mm nach maximaler Gravurtiefe nachweisen.
5. Vor Freigabe: Mesh-Gate (wasserdicht, 1 Körper, Volumen) + Ziel-Slicer-Gate
   + physischer Coupon in Rezepttiefe.

Der rohe Tile hat messbare Kachelkanten (siehe `source.json`); der Referenzdruck
hat sie toleriert. Für lange umlaufende Flächen `build_master.py --blend-px 24`
nutzen und den Coupon erneut prüfen.

## Druckreferenz

0,4-mm-Düse, 0,12-mm-Schicht, PETG, Bauteil flach auf dem Bett. Änderungen an
Düse/Schicht/Material machen dieses Rezept zu einem neuen Kandidaten, der erneut
per Coupon zu qualifizieren ist.
