# FDM-Mechanikbibliothek — 156 parametrische Muster

**Status: `1.1.0-draft.1`, `experimental-draft` und `unqualified`.** Die Erweiterung 121–156 ist digital geprüft, aber weder physisch noch hinsichtlich Dichtheit, Last, Lebensdauer oder Sicherheit qualifiziert.

Diese Sammlung enthält **156 mechanische FDM-Muster in 39 Familien**. Jede Familie liegt in vier Größen-, Spiel-, Steifigkeits-, Dichtungs- oder Übersetzungsvarianten vor. Die Modelle sind als experimentelle DRAFT-Druckproben und als Geometriebausteine für eigene Projekte gedacht.

## Enthaltene Kategorien

| Kategorie | Familien | Varianten |
|---|---:|---:|
| Eindimensionale Drehbewegung | 5 | 20 |
| Zweiachsige Bewegung | 3 | 12 |
| Kugelgelenke | 2 | 8 |
| Dauerhafte Steck- und Schiebverbindungen | 5 | 20 |
| Schraubverbindungen | 3 | 12 |
| Periodisch lösbare Verschlüsse | 4 | 16 |
| Periodische Linearbewegung | 3 | 12 |
| Antriebe und weitere Mechanik | 8 | 32 |
| Dicht- und Serviceschnittstellen | 4 | 16 |
| Komponentenhalter | 2 | 8 |
| **Gesamt** | **39** | **156** |

Zusätzlich zu Gelenken, Steckverbindungen, Schnappern und Schienen enthält die Bibliothek Zahnstange/Ritzel, Stirnradpaare, Rastindexierung, Wellenkupplungen, Kabelclips, Umlenkrollen, O-Ring-Dichtungen, Kurbel-Schwingen, Kabeldurchführungen sowie Batterie- und Magnetaktorhalter.

Die implementierten Erweiterungen 31–39 und ihre noch offenen physischen
Qualifikationsprüfungen sind in
[ROADMAP_RECOMMENDATIONS.md](ROADMAP_RECOMMENDATIONS.md) dokumentiert. Digitale
Meshprüfung ist keine Funktions-, Dichtheits- oder Dauerfestigkeitsfreigabe.

## Was in jedem Musterordner liegt

```text
samples/<kategorie>/<id>-<familie>-<variante>/
├── model.scad          # parametrisches Quellmodell
├── print_plate.stl     # DRAFT-Druckanordnung; nicht physisch qualifiziert
├── preview.png         # farbige Montage-/Explosionsvorschau
├── README.md           # Funktion, Druck, Montage und Integration
├── metadata.json       # maschinenlesbare Parameter und Hinweise
├── components.json     # Meshmetriken und ursprüngliche Positionen
└── parts/
    ├── part_01.stl     # Einzelkörper auf Ursprung verschoben
    └── ...
```

`print_plate.stl` ist die digital meshgeprüfte, physisch unqualifizierte DRAFT-Druckanordnung. Die Dateien unter `parts/` sind für den direkten Import einzelner Körper in CAD-, Mesh- oder Slicer-Projekte gedacht. Bei Print-in-Place-Muster 005–008 muss die gemeinsame Druckplatte verwendet werden, damit die konstruierten Abstände erhalten bleiben.

## Schnellstart

1. Öffne [CATALOG.html](CATALOG.html) lokal im Browser oder die Kontaktübersicht unter `catalog/contact-sheet-39-families.png`.
2. Wähle zunächst die Standard- oder mittlere Variante einer Familie.
3. Drucke `print_plate.stl` mit 0,4-mm-Düse, 0,2-mm-Schichthöhe und mindestens vier Außenlinien.
4. Prüfe Bewegung, Haltekraft, Verschleiß und Montagekraft.
5. Übernimm anschließend `parts/part_XX.stl` oder passe `model.scad` an.

Katalogsuche im Terminal:

```bash
python3 tools/query_catalog.py kugel leichtgängig
python3 tools/query_catalog.py --category linear --material PETG
python3 tools/query_catalog.py schraube --hardware-free
```

Ein einzelnes Muster neu erzeugen:

```bash
python3 tools/build_library.py --ids 030 --workers 1
```

Alle Quellen neu bauen:

```bash
python3 tools/generate_sources.py
python3 tools/build_library.py --workers 3
python3 tools/build_contact_sheets.py
python3 tools/validate_library.py
```

Benötigt werden Python 3.10+, OpenSCAD, NumPy, Trimesh und Pillow. Unter Linux wird `xvfb-run` für headless Vorschaurendering verwendet.

## Parametrische Anpassung

Jede `model.scad` enthält die aktiven Parameter direkt am Dateiende. Beispiel:

```scad
sample_pin_hinge(
    view=view,
    clearance=0.25,
    pin_d=4,
    leaf_l=28
);
```

Für neue Varianten sollten zuerst nur semantische Parameter wie `clearance`, `beam_t`, `ball_d`, `pitch`, `module_size` oder `bore_d` geändert werden. Das gemeinsame Modul liegt in `library/fdm_mechanisms.scad`.

## Grundlegende FDM-Regeln

- Alle Maße sind Millimeter.
- Spielwerte sind konstruktive Startwerte **pro Seite**, sofern die Musterbeschreibung nichts anderes sagt.
- PLA ist gut für starre Proben; PETG, PA oder PP sind für Schnapper und Festkörperfedern geeigneter.
- Mindestens vier Außenlinien verwenden. Stifte, Haken, Federarme und Gewinde profitieren von fünf oder sechs Außenlinien.
- Elephant-Foot, Flow, Materialschrumpfung und Naht können eine nominelle 0,25-mm-Passung stärker verändern als das CAD-Modell.
- Kugelzapfen können je nach Drucker von organischem Support oder einer feineren variablen Schichthöhe profitieren.
- Kleine horizontale Lagerbohrungen sind als kurze Brücken ausgelegt; gegebenenfalls nach dem Druck vorsichtig kalibrieren.

Ausführliche Hinweise stehen in [PRINTING_GUIDE_DE.md](PRINTING_GUIDE_DE.md), [TOLERANCE_MATRIX_DE.md](TOLERANCE_MATRIX_DE.md) und [INTEGRATION_GUIDE_DE.md](INTEGRATION_GUIDE_DE.md).

## Digitale Validierung

- 156/156 Druckplatten bestanden alle automatisierten Prüfungen.
- 384 getrennte Funktionskörper wurden erzeugt.
- Alle Körper sind wasserdicht, konsistent orientiert und besitzen positives Volumen.
- Keine Druckplatte enthält degenerierte Dreiecke.
- Alle Geometrien liegen auf oder über Z=0.
- Größte XY-Ausdehnung: etwa 146 mm.
- Maximale Höhe: 54 mm.

Die Validierung beweist Meshqualität, nicht Lebensdauer oder Tragfähigkeit. Physische Drucktests auf jedem Material und Drucker waren nicht möglich. Ein strukturierter Prüfplan liegt unter [PHYSICAL_TEST_PLAN_DE.md](PHYSICAL_TEST_PLAN_DE.md).

## OpenCode

Die Bibliothek enthält einen OpenCode-kompatiblen Skill unter:

```text
.opencode/skills/fdm-mechanical-sample-library/SKILL.md
```

Der Projektbefehl `/select-fdm-mechanism` kann Anforderungen wie Bewegungsart, Lösbarkeit, Last, Material und gewünschtes Spiel in passende Muster übersetzen.

## Lizenz

- Quellcode, OpenSCAD-Module und Hilfsskripte: MIT-Lizenz.
- Generierte STL-Dateien, Vorschaubilder und Metadaten: CC0 1.0.

Keine Zertifizierung und keine Freigabe für Personenlasten, Hebezeuge, Schutzfunktionen, Fahrzeuglenkung, medizinische Anwendungen oder andere sicherheitskritische Systeme.
