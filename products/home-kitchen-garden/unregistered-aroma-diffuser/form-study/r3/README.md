# FLUENT R3 — parametrische Empfehlung

Weiterentwicklung der vom Nutzer ausgewählten parametrischen R2/003-Form.
Empfehlung: R3 Run 001, mattes warmes Elfenbein, 12 fließende Rippen,
gekaufter Ø5 × 200-mm-Faserdocht für den optischen Test auf 160 mm gekürzt.
Die Duftleistung dieser Kürzung ist offen.

[Hauptansicht mit nominalen Kaufteilen und 160-mm-Docht](assembly/trimmed-160/assembly-hero.png) ·
[Rückansicht der Form](runs/001/fluent-back.png) ·
[Seitenansicht](runs/001/fluent-side.png) ·
[3D-Modell GLB](runs/001/fluent-visual.glb) ·
[Blender-Szene](runs/001/fluent-parametric-study.blend)

## Was verändert wurde

- Höher getragener, etwas voller wirkender Bauch als Gegengewicht zur Krone.
- Schmalere gerundete Rippenkämme mit klareren Lichtlinien; 150° Gesamtverdrehung.
- Zwei leicht seitlich versetzte Kronenspitzen; durchgehende Bündelung der Rippen.
- Tatsächliche Modellrender, ohne KI-Nachbearbeitung, auch mit Kaufteil-Proxies.

Gesamthülle mit visuellem Fuß ungefähr **96.27 × 89.96 × 240 mm**.
Die Parameter width_mm/depth_mm sind Profil-Skalierungsfaktoren, keine exakten
Bounding-Box-Maße. Sichtbare Oberflächen bleiben parametrisch erzeugt.
Der Fuß ist nur ein optischer Platzhalter, noch keine funktionale Verbindung.

## Wo die parametrische Variante liegt

Editierbare Autorität: [parameters.json](parameters.json) und
[source/geometry.py](source/geometry.py), ausgeführt durch
[source/build_fluent.py](source/build_fluent.py).
Die .blend-Datei enthält das generierte Mesh und die Studioszene, keinen
CAD-Parameterbaum. GLB verwendet Meter, der Prüf-OBJ Millimeter.
Es gibt weder STEP/B-Rep noch einen freigegebenen STL-/3MF-Drucksatz.

Aus diesem Verzeichnis neu erzeugen; immer einen unbenutzten Ausgabeordner wählen:

```sh
blender --background --factory-startup -t 12 --python source/build_fluent.py -- --out runs/next-unused --views hero,back,side --samples 24 --resolution 1000
```

Eine bearbeitete Parameterkopie lässt sich mit --params /absoluter/pfad.json
übergeben. Bauch-/Taillen-/Mittellinienprofile, Höhe, Tiefe, Breite, Rippen und
Kronenbewegung sind editierbar. Lieferantenmaße sind davon unabhängig.
Der Builder hält die ursprünglichen nominalen Referenzen Ø50 × 64 / Ø5 × 200
in einer ausgeblendeten Sammlung; der Diagnose-Renderer liest ihre Maße aus
den übergebenen Parametern und zeigt die explizit angegebene Dochtlänge.
Kaufteile sind nicht im visuellen GLB/Schalen-OBJ enthalten.

## Kaufteile und sichtbarer Docht

Nominalbasis unverändert: Vaza 9-161, 50 ml, Ø50 × H64 mm, PP28;
Faserdocht Ø5 × 200 mm aus der bestehenden Lieferantenrecherche in Konzept R1.
Dies sind Referenzmaße, kein universeller Passungsstandard oder vermessenes Muster.

[Ungekürzter 200-mm-Docht](assembly/nominal-200/assembly-hero.png) ist in der
Hauptansicht störend sichtbar. Der gemeinsame exakte Mesh-Boolean-Prüfer findet
13.9634 mm³ Überschneidung mit der Hülle. Der lange Docht ist in dieser
zentrierten Lage daher kein gültiger Montagevorschlag.
Der auf 160 mm gekürzte Docht bleibt in der geprüften Hauptansicht verdeckt;
nominale Fiole und kurzer Docht zeigen jeweils 0 mm³ Überschneidung.
Das ist eine Kollisionsdiagnose, kein Nachweis für Mindestabstand oder Passung.
Fiole: vereinfachter Zylinder, Unterseite z=4 mm; Docht: Unterseite z=5 mm.
Halter, Hals-/Kappendetails, Einbauweg, Kippsicherheit und Medientests fehlen.

## Prüfstatus und nächster Schritt

Siehe [Prüf- und Sichtbericht](VISUAL-REVIEW.md), mesh-policy.json,
validation-project.json sowie die unveränderten Laufartefakte.
Die Außenform ist eine weiterentwickelte **Formstudie, nicht druckfertig**.
Preflight 003 bleibt CONCEPT_ONLY / C3 / R0 / K2 / Lane E, Lifecycle P0.
Die Routenauswahl durch den Nutzer ist keine formale Freigabe dieser Revision.

Nächste konstruktive Phase: sichtbare Form beurteilen, reale Kaufteile und
passenden Docht-Halter vermessen; dann verdeckte Aufnahme/servicefähigen Fuß
entwickeln, normale Wandstärke und Krone prüfen und mit exakten Profilen slicen.
Ein Mattsurface-/Kronenabschnitt am echten Druck muss den Render-Look bestätigen.
Keine Druckerübertragung oder Druckauslösung erfolgt.

## Reproduzierbare Diagnostik

Für die vorhandenen gemeinsamen Mesh-Tools wurde die bereits installierte
Python-3.11-Umgebung verwendet; ihr exakter Interpreterpfad steht in sweep.json.
Keine Pakete installiert. Befehle vom Repository-Root:

```sh
python .agents/skills/functional-3d-design/scripts/validate_design_spec.py products/home-kitchen-garden/unregistered-aroma-diffuser/design-spec.yaml --require-current-preflight
```

Mit dem Interpreter aus sweep.json: fdm_ci.py audit-mesh mit mesh-policy.json;
run-sweep mit sweep.json und neuem --output-root; check-interfaces mit
trimmed-interfaces.json. Die gemeinsamen Werkzeuge liegen unter
.agents/skills/validate-printable-3d-projects/scripts/.
Nominale Montageansicht aus diesem R3-Ordner:

```sh
blender --background --factory-startup -t 12 --python source/inspect_assembly.py -- --scene runs/001/fluent-parametric-study.blend --params parameters.json --out assembly/next-unused --reed-length 160 --views hero
```

Kurvendiagnostik: source/export_rails.py extrahiert zwei dichte Leitlinien aus
dem unveränderten Modell; der gemeinsame analyze_curve.py wertet sie mit
--count 192 aus. Diese numerischen Indikatoren zertifizieren keine G2-Fläche.
Parameter-Sweep-OBJ bleiben lokal regenerierbar und unversioniert; Parameter,
Kommandos, Ergebnisse, gewählte Modelle und Render werden erhalten.
R2 und die verworfene Step1X-Alternative bleiben unverändert historisch erhalten.
Feature-Branch-Kandidat nach Push: merge-ready, nicht in main integriert und
nicht kommerziell freigegeben.
