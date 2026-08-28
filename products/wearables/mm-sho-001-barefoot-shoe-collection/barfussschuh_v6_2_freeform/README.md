# MM-SHO-001 Barfußschuh V6.2 Freeform Upper

`6.2.0-draft.2` ist der freigegebene digitale Formkandidat für ein glattes,
direkt parametrisiertes Upper ohne Voxel-, Distanzfeld- oder
Marching-Cubes-Erzeugung. Der V6.1-Sohlen-/Lippenanschluss bleibt geschützt.

## Aktueller Stand

- Spezialvalidierung: `PASS` (14/14 Checks)
- Visuelle Formprüfung: `PASS`
- Projektgate: `REVIEW_REQUIRED`
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
- freigegebene Renderansichten: `previews/production-v6.2.0-draft.2/`
- deterministische Evidenz: `validation/`
- aggregierter Vertrag: `validation-project.json`

Verworfene Draft-1- und Draft-2-Attempt-1-Artefakte bleiben als negative
Vergleichsevidenz erhalten und sind nicht die aktuellen Fertigungsdateien.

## Reproduzieren

```bash
python3 generate_v6_2.py --parameters parameters.yaml
python3 validate_freeform_v6_2.py --parameters parameters.yaml
blender --background --factory-startup --python render_v6_2.py -- \
  --mesh exports/manufacturing/DRAFT-MM-SHO-001-6.2.0-draft.2-upper-fuzzy-shell-left.stl \
  --output previews/production-v6.2.0-draft.2
python3 ../../../../.agents/skills/validate-printable-3d-projects/scripts/fdm_ci.py \
  validate-project validation-project.json --profile draft \
  --json-out validation/project-validation-draft2.json
```

## Nächster Gate

Vor einem Vollschuhdruck zuerst das exakte Maschinen-, Prozess-, Filament- und
Orientierungsprofil festlegen und den Kragen-Coupon drucken. Danach werden
Kantenkomfort, Wandaufbau, Layerhaftung und 50 starke Handbiegezyklen bewertet.
