# Validierungsbericht – R1.5 prozedurale Walnussstruktur (DRAFT)

## Ergebnis

R1.5 ersetzt die Stahloptik durch eine bildfreie, deterministische Walnussmaserung. Alle neun STL-Dateien sind geschlossen, manifold, einteilig und positiv volumig; die positionierte 4-Objekt-3MF besteht die CRC-Prüfung. Physische Holzoptik, Connectorpassung und exakte Ziel-Slicer-Pfade bleiben offen, daher `DRAFT`.

## Modell

| Merkmal | Ergebnis |
|---|---:|
| Baugruppenhülle | 227 × 357 × 64 mm |
| größtes Einzelmodul | 135 × 186,5 × 64 mm |
| Hauptmodule | 4 |
| Hardwarefächer | 8 in 2 × 4 |
| Boden / Basiswand | 2,6 / 3,2 mm |
| Connector-Nennfreigabe | 0,30 mm |
| Druckorientierung | Unterseite flach, supportfrei vorgesehen |

## Texturabdeckung

| Modul | Boden-Nuten | Innenwand-Nuten | Wandtop-Nuten | Äste |
|---|---:|---:|---:|---:|
| Driver vorn | 17 | 55 | 4 | 1 |
| Driver hinten | 16 | 56 | 4 | 1 |
| Hardware vorn | 49 | 157 | 16 | 1 |
| Hardware hinten | 42 | 106 | 10 | 0 |

- Repräsentation: `deterministic-vector-grain-and-knot-grooves`; Seed `150521`.
- Maximale Tiefe: Boden 0,20 mm, Innenwand 0,17 mm, Wandtop 0,12 mm.
- Bild-/Heightmap-Pfad: inaktiv; kein Bildfit, Stretching oder Seitenverhältnisparameter.
- Glatt geschützt: Außenwände, Connectoren, Junctions, Griffnuten, Gussets, Wandwurzeln, Bettauflage und Kennzeichnung.

## Materialreserven

| Zone | Reststärke | Grenze |
|---|---:|---:|
| Boden unter tiefster Obertextur | 2,40 mm | ≥ 2,00 mm |
| Boden unter Unterseitenmarke | 2,20 mm | ≥ 2,00 mm |
| doppelseitig texturierte Trennwand | 2,86 mm | ≥ 2,00 mm |
| einseitige Außenwand-Innenfläche | 3,03 mm | ≥ 2,00 mm |

## Netz und Ressourcen

| Datei | Dreiecke | Ergebnis |
|---|---:|---|
| Driver vorn | 28.064 | PASS |
| Driver hinten | 27.374 | PASS |
| Hardware vorn | 40.384 | PASS |
| Hardware hinten | 32.904 | PASS |
| Kamm | 612 | PASS |
| Eckcoupon | 100 | PASS |
| Walnusscoupon | 3.836 | PASS |
| Connector male / female | 152 / 144 | PASS |

- Reparatur: 0 kollabierte Kanten; alle Exporte waren bereits topologisch sauber.
- Peak-RSS: 164,75 MiB = 0,161 GiB = 0,173 GB dezimal.
- Review-Grenze: 1.000.000 Dreiecke/Modul; Mesh-Stop: 100 MiB/Modul; beides PASS.
- Zusätzliche globale Decimation: `not-beneficial`; hochpräzise reproduzierbare Netze bleiben erhalten.

## Connectorprüfung

Beide Connector-Coupons sind byte-identisch zu R1.4. Runde Lug-/Halsgeometrie ist digital konsistent; dreieckige Körper im Modell sind Gussets, keine Connectoren. Die gemeldete physische Nichtpassung bleibt offen und darf erst nach Coupon-Istmaß, Druckorientierung und Elefantenfußbewertung geändert werden.

## 3MF und Rebuild

- Vier benannte Hauptobjekte in korrekter globaler Lage; Hülle 227 × 357 × 64 mm.
- Core-Namensraum und ZIP/CRC PASS.
- Ein Befehl: `python3 rebuild.py`; alle Werte stammen aus den JSON-Parameterdateien.

## Offene Freigabepunkte

1. Walnusscoupon mit Zielmaterial drucken und Optik, Haptik, Wandtop-Komfort und Reinigung prüfen.
2. Connectorpaar drucken und messen; Nichtpassung dokumentiert auflösen.
3. Eckcoupon in der realen Schublade prüfen.
4. 3MF im Ziel-Slicer prüfen; erste drei Schichten, kurze Texturpfade und Unterseitenkennzeichnung kontrollieren.
5. Danach vollständiges Modell erneut prüfen und erst dann DRAFT-/Kennzeichnungsfreigabe erteilen.
