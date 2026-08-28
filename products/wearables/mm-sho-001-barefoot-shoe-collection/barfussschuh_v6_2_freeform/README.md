# MM-SHO-001 Barfußschuh V6.2 Freeform Upper

`6.2.0-draft.3` ist die aktuelle Korrekturspezifikation für ein glattes,
direkt parametrisiertes Upper ohne Voxel-, Distanzfeld- oder
Marching-Cubes-Erzeugung. Der V6.1-Sohlen-/Lippenanschluss bleibt geschützt.
Der vorherige Draft-2-Kandidat wurde wegen sichtbarer Endöffnungen und einer
zu hohen Mittelfuß-/Vamp-Kontur durch Nutzerfeedback ersetzt.

## Aktueller Stand

- Draft-2-Spezialvalidierung: digital `PASS` (14/14 Checks), aber vom Nutzer
  geometrisch abgelehnt
- Draft-3-Anforderungen: `approved`
- Draft-3-Konzept: `approved`
- Draft-3-Spezialvalidierung: digital `PASS` (17/17 Checks)
- alle sechs Draft-3-Upper-STLs: je ein wasserdichtes, positiv orientiertes
  Volumen; `0` Randkanten, `0` nichtmanifold Kanten und `0` degenerierte Flächen
- Draft-3-Formreview: `PASS`; Ferse und Zehe sind geschlossen, die Mittellinie
  fällt ab der Kragenvorderkante von `z=52,0 mm` ohne zweiten Hochpunkt ab
- Projektweiter Draft-Status: `REVIEW_REQUIRED`, ausschließlich wegen der noch
  offenen Slicer-, Material- und physischen Prüfungen
- Offen: exaktes Anycubic-Maschinen-/Prozess-/TPU-Profil, Slicer-Preflight,
  physischer Kragen-Coupon, Anprobe sowie Material-/Hautkontaktprüfung

Das Modell ist damit ein druckbarer **Draft-Kandidat**, aber keine finale
Druck-, Trage- oder Veröffentlichungsfreigabe.

## Quellen und Ausgaben

- Parameter: `parameters.yaml`
- Generator: `generate_v6_2.py`
- Herstellungsmeshes: `exports/manufacturing/`
- Kragen-Coupon: `exports/coupons/`
- editierbarer High-Fidelity-Master: `exports/master/`
- freigegebene Konzeptansicht: `previews/concept-v6.2.0-draft.3.png`
- geprüfte Draft-3-Renderansichten: `previews/production-v6.2.0-draft.3/`
- deterministische Evidenz: `validation/`
- aggregierter Vertrag: `validation-project.json`

Verworfene Draft-1- und Draft-2-Attempt-1-Artefakte bleiben als negative
Vergleichsevidenz erhalten und sind nicht die aktuellen Fertigungsdateien.

## Reproduzieren

```bash
python3 generate_v6_2.py --parameters parameters.yaml
python3 validate_freeform_v6_2.py --parameters parameters.yaml
blender --background --factory-startup --python render_v6_2.py -- \
  --mesh exports/manufacturing/DRAFT-MM-SHO-001-6.2.0-draft.3-upper-fuzzy-shell-left.stl \
  --output previews/production-v6.2.0-draft.3/fuzzy-shell
python3 ../../../../.agents/skills/validate-printable-3d-projects/scripts/fdm_ci.py \
  validate-project validation-project.json --profile draft \
  --json-out validation/project-validation-draft3.json
```

## Nächster Gate

Vor einem Vollschuhdruck zuerst das exakte Maschinen-, Prozess-, Filament- und
Orientierungsprofil festlegen und den Kragen-Coupon drucken. Danach werden
Kantenkomfort, Wandaufbau, Layerhaftung und 50 starke Handbiegezyklen bewertet.
Ein dauerhaftes Produkt-Wasserzeichen bleibt bis zur stabilen Release-Geometrie
zurückgestellt, weil jede spätere Änderung die jetzige Mesh- und Renderevidenz
erneut ungültig machen würde.
