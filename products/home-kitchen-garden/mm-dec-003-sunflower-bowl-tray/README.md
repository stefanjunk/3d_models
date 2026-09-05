# MM-DEC-003 — Sunflower Bowl / Tray

Status: `v0.2.0 digital candidate` — technisch geprüft, physisch und kommerziell nicht freigegeben.

Der sichtbare Schalenkörper ist eine unveränderte, untexturierte Step1X-3D-Geometrie aus Run 004. Er wurde lediglich auf 200 mm maximale XY-Ausdehnung registriert. Parametrisch ergänzt wurde ausschließlich der vom Eigentümer bestätigte Fuß: eine Scheibe mit 80 mm Durchmesser und 6 mm Dicke. Es erfolgte keine parametrische Rekonstruktion oder Reparatur der Blüte.

Die alten STLs, die alte 3MF-Datei und die alte OpenSCAD-Geometrie sind wegen unzureichender Herkunfts- und Lizenznachweise für die neue Ableitung gesperrt. Aus der alten 3MF wurden nur die sachlichen Scheibenmaße und die Nutzerabsicht abgelesen; keine Dreiecke oder Flächen wurden übernommen.

## Hauptartefakte

- digitaler Fertigungskandidat: `result/MM-DEC-003-sunflower-bowl-tray-v0.2.0-step1x-run-004-footed-digital-candidate.stl`
- unveränderter registrierter Step1X-Körper: `organic/work/run-004/01-registered-raw.stl`
- parametrische Fußscheibe: `organic/work/run-004/02-parametric-foot-disc.stl`
- Step1X-Rohgeometrie: `organic/raw/step1x/run-004/geometry.raw.glb`
- ausgewählter lokaler G-Code: `exports/v0.2.0/slice-run-004-footed-support-run-002/plate_1.gcode`
- Projektvertrag: `validation-project.json`
- Ergebnisbericht: `reports/final-model-result-v0.2.0.md`
- unabhängige Mesh-Bewertung: `reports/organic-mesh-review-v0.2.0.md`
- Lizenzprüfung: `evidence/legacy-license-audit-v0.2.0.md`

Der ältere generische v0.2.0-Kandidat und sämtliche Run-001-Artefakte sind verworfene Entwicklungshistorie. Sie sind nicht der aktuelle Kandidat.

## Reproduzierbare Geometriephase

Aus dem Repository-Root:

```bash
uv run --with-requirements products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/source/requirements.txt \
  python products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/source/register_generated_mesh.py \
  products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/organic/raw/step1x/run-004/geometry.raw.glb \
  products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/organic/work/run-004/01-registered-raw.stl \
  --target-longest-xy-mm 200 \
  --report products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/reports/run-004/registration-raw.json

uv run --with-requirements products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/source/requirements.txt \
  python products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/source/add_parametric_foot.py \
  products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/parameters/foot-disc-v0.2.0.json \
  products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/organic/work/run-004/01-registered-raw.stl \
  products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/organic/work/run-004/02-parametric-foot-disc.stl \
  products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/organic/work/run-004/03-footed-candidate.stl \
  --report products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/reports/run-004/foot-union.json
```

Run, Runtime-Snapshot und Attestation binden Eingabebild, lokalen Fork-Commit, Modell-Snapshots, Vorverarbeitung und Ausgabe-Hashes. Der rohe Run-Record bleibt unverändert.

## Validierung und Slice

```bash
uv run --with-requirements products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/source/requirements.txt \
  python .agents/skills/validate-printable-3d-projects/scripts/fdm_ci.py validate-project \
  products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/validation-project.json \
  --profile draft \
  --json-out products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/reports/project-validation-v0.2.0.json
```

Der ausgewählte Slice verwendet Anycubic Kobra 3 Max, 0,4-mm-Hartstahldüse, 0,20-mm-PETG und das produktlokale Prozessprofil mit automatischem Baum-Support vom Druckbett bei 80 mm/s. Der supportfreie Kontrolllauf meldete schwebende Regionen; der erste Supportlauf überschritt das konservative 13,3-mm³/s-Prüflimit. Beide Läufe bleiben als verworfene Evidence erhalten.

Die Slice-Ausgabe ist ausschließlich ein lokaler Export. Upload oder Druckstart wurden nicht ausgeführt.

## Offene Freigaben

- finale Layer-/Support-/Seam-Vorschau durch einen Menschen;
- realer PETG-Druck einschließlich erster Schicht, Supportentfernung, Ebenheit, Kipp-/Wackeltest, Rand- und Petalenspitzenprüfung;
- Bestätigung der finalen Produktabmessungen und des gelben Zielmaterials;
- metriMade-Release-Markierung nach stabiler Freigabegeometrie;
- OpenAI-Konto-/Planbedingungen, Step1X-Abhängigkeiten sowie IP/FTO-, GPSR-/Produktsicherheits-, Export- und Marktprüfung;
- signierte kommerzielle Freigabe und vollständiges Evidence-Manifest.

Bis dahin sind Veröffentlichung, Fertigung zum Verkauf und Versand gesperrt.
