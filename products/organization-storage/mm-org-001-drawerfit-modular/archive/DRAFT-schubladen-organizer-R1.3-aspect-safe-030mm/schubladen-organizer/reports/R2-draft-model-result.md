# R2 Schubladen-Organizer — DRAFT-Modellergebnis

Der vierteilige Schubladen-Organizer ist auf die freigegebene R2-Holzoptik umgestellt und als absichtlich unmarkierter DRAFT vollständig neu gebaut. Die aktuelle parametrische Quelle, neun STL-Dateien und die Vierobjekt-3MF bestehen die digitale Prüfung; exakte Slicer- und physische Prüfungen fehlen noch.

## Modellergebnis

- Baugruppenhülle 227 × 357 × 64 mm für eine nominell 230 × 360 × 80 mm große Innenschublade.
- Vier Puzzle-verbundene Hauptmodule: lange 92-mm-Schraubendreherzone links und acht Hardwarefächer in 2 × 4 Anordnung rechts.
- Separater Kamm mit acht Schraubendreherplätzen; acht 22 × 8-mm-U-Griffnuten und vollhohe verrundete T-/Kreuzungsknoten.
- Prozedurale Holzmaserung mit gespeichertem Seed: 0,90 mm breite, rein vertiefte Nuten; 0,20 mm auf Böden/Topflächen und 0,16 mm auf sichtbaren Innenwänden.
- Außen-, Unter-, Verbinder-, Pass-, Griffnut-, Wandwurzel- und Knotenflächen bleiben geometrisch geschützt und glatt.
- Das freigegebene Erscheinungsziel zeigt `concept-R2-v5.png`; das Bild ist keine Maß-, Slicer- oder Festigkeitsevidenz.

## Verifikation und Druckbereitschaft

| Prüfung | Ergebnis |
|---|---|
| Anforderungen/Konzept | R2 approved / R2 approved |
| STL-Topologie | 9/9 PASS: watertight, manifold, konsistent orientiert, einteilig, volumenhaltig; keine Null- oder Duplikatflächen |
| Hauptmodul-Meshes | 426.832 Dreiecke, 21.341.936 Bytes |
| Effizienz gegen R1.3 | 92,9206 % weniger Dreiecke; 92,9205 % weniger STL-Bytes |
| Restmaterial | Boden mindestens 2,40 mm; doppelseitig genutete Wand mindestens 2,88 mm |
| 3MF | CRC/Core-Namensraum PASS; vier benannte Objekte und Build-Items; Hülle PASS |
| Buildvolumen | Jedes Modul höchstens 135 × 186,5 mm; passend für 220 × 220 × 250 mm |
| Zielprozess | ungefülltes warmbraunes PETG, 0,4-mm-Düse, 0,45-mm-Linienbreite, 0,20-mm-Schichten, flach/supportfrei |
| Exakter Slicer | NOT_RUN — kein Slicer-CLI/gespeichertes Maschinenprofil verfügbar |
| Physische Prüfung | NOT_RUN — Holztextur-, Verbinder-, Eck-/Schubladen- und Probemodulprüfung offen |

Eine zusätzliche verlustbehaftete Mesh-Decimation ist `not-beneficial`: die kompakte parametrische Repräsentation unterschreitet die Mesh-/Datei-/Speicherbudgets bereits deutlich. Die strikte Float32-Exportsanitation entfernt nur exakt gegenläufige interne Flächenpaare und bricht bei mehrdeutigen Duplikaten ab.

## Deliverables

- DRAFT-Baugruppe: `output/DRAFT/DRAFT-R2-procedural-wood-assembly.3mf`
- Vier Hauptmodul-STLs, Kamm und vier Coupons: `output/DRAFT/DRAFT-R2-*.stl`
- Editierbarer Master: `src/manifold_model.mjs`, `src/procedural_wood.mjs`, `config/model-params.json`, `config/wood-texture-params.json`
- Rebuild: `rebuild.py`; Build/Validierung: `src/build_pipeline.py`, `src/validate_r2_procedural_wood.py`
- Stückliste, Montage und Prozess: `BOM.md`, `assembly-guide.md`, `print-profile.md`
- Digitale Evidenz: `reports/R2-procedural-wood-digital-validation.json`, `reports/R2-procedural-wood-unmarked-mesh-validation.json`, `reports/build-pipeline-R2-procedural-wood-unmarked.json`, `reports/three-mf-package-R2-procedural-wood-unmarked.json`
- Meshentscheidung: `reports/R2-mesh-simplification-decision.md`

Ein STEP-Modell ist nicht enthalten, weil der parametrische Master auf JavaScript/Manifold3D basiert. Ein finales Release-ZIP wird vor Slicer-/Couponnachweis, Kennzeichnung und finaler Nutzerfreigabe absichtlich nicht erzeugt.

## Offene Punkte

1. R1.3 und R2 mit demselben exakten Slicer-, Maschinen-, Material- und Prozessprofil importieren/slicen; Warnungen, fehlende Nuten/Wände, Kurzsegmente, Zeit und Material vergleichen.
2. Eck-/Schubladencoupon, Connector-Paar und Holztexturcoupon im Zielprozess drucken und messen; danach ein repräsentatives Hauptmodul testen.
3. Erst nach diesen Nachweisen die R2-Kennzeichnung als letzte Geometrieänderung integrieren, Regression wiederholen und die finale Freigabe anfordern.

## Kennzeichnung

- JuSt Innovation `JSI-WM-001-R1`, compact, vorgesehen auf den druckbettseitigen Unterseiten: für R2 noch blockiert und im aktuellen DRAFT absichtlich nicht enthalten.

Nächster Modellschritt ist die exakte Slicerprüfung und danach der Druck des Holztextur- und Passcoupon-Satzes.
