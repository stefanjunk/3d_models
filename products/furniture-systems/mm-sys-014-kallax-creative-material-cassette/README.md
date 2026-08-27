# Systemmöbel Top 20 - parametrische FDM-Konzeptmodelle

Dieses Paket setzt die 20 Produktideen aus `../bericht-top20-systemmoebel-zubehoer-ikea.md` als jeweils einteiliges, parametrisches CadQuery-Modell um.

> **Status: DRAFT / PROVISIONAL_UNVERIFIED.** Die Dateien sind geometrisch druckbare Konzeptprototypen, aber noch keine bestätigten IKEA-Passteile. Vor praktischer Nutzung müssen Möbelrevision, Toleranz, Last und Druckprofil mit Fit-Coupons und Testdrucken validiert werden.

## Lieferumfang

- 20 STL-Dateien in `exports/stl/`
- 20 editierbare STEP-Dateien in `exports/step/`
- parametrische CadQuery-Quellen in `systemmoebel_top20/models/`
- zentrale Standardparameter in `config/defaults.json`
- digitale Prüfberichte in `reports/`
- unabhängige digitale 3D-Designprüfung in `reports/independent-design-review.md`
- 20 Vorschaurender und Kontaktbogen in `previews/`

## Modelle

| Nr. | Produktmodell | System | Standard-Bounds mm | Primärmaterial |
|---:|---|---|---:|---|
| 1 | Inventarbasierte Arbeitsplatz-Schublade | ALEX | 210 × 160 × 32 | PETG/PLA Pro |
| 2 | Werkzeug-Shadow-Tray | BROR | 220 × 180 × 28 | PETG |
| 3 | Asymmetrisches Accessoire-Raster | PAX/KOMPLEMENT | 230 × 180 × 35 | PETG/PLA Pro |
| 4 | Sammlungsspezifischer Stufen-Riser | BILLY | 220 × 170 × 75 | PETG/PLA Pro |
| 5 | Werkzeugtafel-Workflow-Cluster | BROR | 220 × 120 × 35,5 | PETG |
| 6 | Brettspiel-Bibliotheksmatrix | KALLAX | 225 × 210 × 150 | PETG |
| 7 | Asymmetrische Sammlungzellen | PLATSA/HJÄLPA | 230 × 190 × 140 | PETG |
| 8 | Präzisionswerkzeug-Workflow-Cluster | SKÅDIS | 220 × 110 × 28,8 | PETG |
| 9 | Passive Medien-Topologie | BESTÅ | 220 × 180 × 18 | PETG/ASA |
| 10 | Belüftete Kleinteile-Regalauflage | OMAR | 210 × 180 × 10 | PETG |
| 11 | Dockingleiste für Reinigungszubehör | BOAXEL | 220 × 47 × 16,8 | PETG |
| 12 | Controller- und Medien-Schubladenraster | BESTÅ | 220 × 180 × 30 | PETG |
| 13 | Erwachsenen-Werkstatteinsatz | TROFAST | 220 × 160 × 45 | PETG |
| 14 | Kreativmaterial-Kassette | KALLAX | 220 × 220 × 180 | PETG |
| 15 | Korb-Mikrosortierer | BOAXEL | 220 × 160 × 80 | PETG |
| 16 | Faltmaßbasierte Schubladenteiler | MALM | 220 × 180 × 65 | PETG/PLA Pro |
| 17 | Bohrfreie Seitenrahmen-Inventarleiste | IVAR | 228 × 64,8 × 18 | PETG/ASA |
| 18 | Sammlungsspezifische Display-Matrix | BILLY | 220 × 170 × 70 | PETG/PLA Pro |
| 19 | Reversible Kabel-Parkleiste | LAGKAPTEN/ALEX | 200 × 66,1 × 38 | PETG |
| 20 | Zweifach-Bein-Mini-Dock | LACK | 118 × 137,6 × 110 | PETG |

## Erzeugen und prüfen

Abhängigkeiten sind in der aktuellen Arbeitsumgebung bereits vorhanden. Für eine neue Umgebung:

```bash
python -m pip install -r requirements.txt
```

Alle Modelle neu erzeugen:

```bash
python generate.py
```

Nur ausgewählte Nummern erzeugen:

```bash
python generate.py --only 1 8 19
```

Eine Implementierungsgruppe isoliert prüfen:

```bash
python validate_group.py a
python validate_group.py b
python validate_group.py c
python validate_group.py d
```

Vorschaubilder nach einem Build erzeugen:

```bash
python render_previews.py
```

## Parametrik und Schnittstellen

`config/defaults.json` ist die einzige Quelle für die Standardhülle und alle bekannten Möbelkontaktmaße. Die Werte sind bewusst konservative Entwurfsannahmen, keine bestätigten IKEA-Spezifikationen.

Vor einer Maßänderung:

1. Artikelnummer, Land, Kaufdatum und Möbelrevision festhalten.
2. Lichte Maße und Kontaktgeometrie an mindestens drei Stellen messen.
3. Funktionales Spiel, Prozesskompensation und Montagezugabe getrennt bestimmen.
4. Erst einen kleinen Fit-Coupon drucken.
5. Danach Parameter ändern und `python generate.py --only N` ausführen.

Die Markenbezeichnungen dienen ausschließlich zur Beschreibung der vorgesehenen Kompatibilität. Das Projekt ist nicht mit IKEA verbunden oder von IKEA freigegeben.

## Freigabegrenzen

Digital bestätigt sind derzeit:

- 20/20 STL-Dateien wasserdicht und winding-konsistent
- 20/20 STL-Dateien jeweils genau eine verbundene Komponente
- 20/20 STEP-Dateien jeweils als ein Volumenkörper reimportierbar
- alle Standardmodelle innerhalb 256 × 256 × 256 mm
- deklarierte gewöhnliche Funktionswände mindestens 2,4 mm; optionale Pad-Lands können dünner sein
- Geometrie mit supportfreier Entwurfsabsicht; noch keine Slicer-Bestätigung

Noch nicht bestätigt sind geometrisch gemessene Mindestwand über alle lokalen Details, reale Passung, Slicer-Toolpaths, Druckzeit, Materialverbrauch, Last, Clip-Fatigue, Kriechen, Möbeloberflächen-Schutz und Langzeitnutzung. Details stehen in `FIT-AND-TEST.md` und `reports/mesh-validation.md`.
