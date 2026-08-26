# Installation und Rebuild

## Nur verwenden

ZIP entpacken, `CATALOG.html` öffnen und STL-Dateien direkt importieren oder slicen.

## Geometrie neu erzeugen

Systempakete: OpenSCAD und optional Xvfb. Python-Pakete:

```bash
python3 -m pip install -r requirements.txt
python3 tools/build_library.py --workers 3
```

## OpenCode

Projektlokal bleibt `.opencode/` im entpackten Wurzelordner. Der Skill wird automatisch als Projekt-Skill erkannt. Für eine globale Installation kann der Ordner `.opencode/skills/fdm-mechanical-sample-library` nach `~/.config/opencode/skills/` kopiert werden; der eigentliche Katalogpfad muss dann über `FDM_MECH_LIBRARY_ROOT` gesetzt oder als Projektressource zugänglich sein.
