# Validierungsbericht — FDM-Mechanikbibliothek 1.1.0-draft.1

**Status:** digitaler DRAFT-Prüfpunkt bestanden; keine Release-Freigabe.

Dieser Bericht dokumentiert die automatisierte Geometrie-, Parameter- und Paketprüfung der experimentellen Erweiterung. Er ersetzt keine physischen Druck-, Dichtheits-, Last-, Ermüdungs- oder Sicherheitsversuche. Wasserzeichen- und finale Release-Freigabe bleiben blockiert.

## Umfang

| Kennzahl | Ergebnis |
|---|---:|
| Parametrische Muster | 156 |
| Mechanikfamilien | 39 |
| Druckplatten-STLs | 156 |
| Getrennte Einzelkörper-STLs | 384 |
| Insgesamt validierte Dreiecke der Druckplatten | 277.186 |
| Summiertes Modellvolumen | 1.820,8 cm³ |
| Größte X-Ausdehnung | 146,031 mm |
| Größte Y-Ausdehnung | 96,870 mm |
| Maximale Z-Höhe | 54,000 mm |

## Ergebnis der Mesh-Prüfungen

| Prüfkriterium | Bestanden |
|---|---:|
| Druckplatte als Gesamtmesh wasserdicht | 156/156 |
| Orientierung/Winding konsistent | 156/156 |
| Alle getrennten Einzelkörper wasserdicht | 156/156 |
| Alle Einzelkörper mit positivem Volumen | 156/156 |
| Keine degenerierten Dreiecke | 156/156 |
| Geometrie vollständig auf oder über Z=0 | 156/156 |
| Passt in 220-mm-XY-Prüfbauraum | 156/156 |
| Komponentenanzahl stimmt mit Dokumentation überein | 156/156 |

Alle 156 Druckplatten erhielten den Status `passed`; es gab 0 Warnungen und 0 Fehler. Die vollständigen maschinenlesbaren Resultate liegen in `validation/build-summary.json` und `validation/samples/`.

Für die Erweiterung 121–156 wurden alle 36 STL-Druckplatten aus der aktuellen Quelle erzwungen neu gerendert. Ein zweiter unabhängiger Renderlauf ergab 36/36 identische kanonische Dreiecksgeometrien gegenüber den aktualisierten DRAFT-Artefakten. Zusätzlich bestanden 27/27 gültige beziehungsweise absichtlich ungültige Parameter-Grenzfälle. Diese Evidenz liegt in `validation/extension-build-summary.json` und `validation/extension-validation.json`.

Die nachfolgende Dokumentationskorrektur bestand zusätzlich 36/36 deterministische Claims-Bounded-Prüfungen in Katalog-JSON/CSV, Metadaten, Muster-READMEs, HTML-Karten und Markdown-Katalogzeilen. Darin enthalten sind 20/20 lokale Prüfungen der Dichtungsfamilien 31, 32, 35, 37 und 39 sowie 4/4 Prüfungen der Familie 39 auf die Abgrenzung zwischen ununterbrochener Wandbarriere und ungetesteter IP-/Wasserdichtheit. Der separate Bericht ist `validation/extension-claims-validation.json`.

Da diese Korrektur keine Geometriequelle änderte, wurden die 36 Druckplatten nicht unnötig neu gerendert. Vor und nach der Dokumentationsgenerierung blieben der SHA-256 der gemeinsamen SCAD-Quelle (`3e700ed8c0c544d9be352ff8f6329e7691c06cd5d2c8b542853ec79b763b5360`), der geordnete Aggregat-Hash der 36 Print-Plate-Hashzeilen (`66b73b12f66245863120dfda197cb6e543fc68d6df5bb6de76373927780b716b`) und der Konzept-Hash (`4827bae0290786e22d9dec3902d1fc50cda7a16aa1a557520d2e96631af3c6bc`) unverändert.

Die strikte Unique-Key-YAML-Prüfung und der offizielle `validate_design_spec.py`-Lauf bestanden. Dessen drei Warnungen entsprechen den bewusst offenen Gates für Wasserzeichen, Druckzeit-/Materialoptimierung und Mesh-Vereinfachung. Die Paketprovenienz trennt nun das tatsächliche Basisrelease 1.0.0 vom `2026-08-20` klar vom nicht-finalen DRAFT-Artefaktprüfpunkt `1.1.0-draft.1` vom `2026-08-21`; der deterministische Manifest-/Checksum-Check bestand mit 1.682 Manifestdateien und 1.683 Prüfsummeneinträgen.

Der formale Mesh-Vereinfachungsgate ist `pending`, weil sein verpflichtender Vergleich das Verhalten eines exakten Slicers umfasst und noch kein konkreter Drucker, kein Profil und kein Slicer benannt sind. Interimsentscheidung für den DRAFT: Die parametrisierte OpenSCAD-Quelle bleibt der Master, die niedrigkomplexen funktionalen CSG-STLs werden unverändert beibehalten, und es wird keine verlustbehaftete Vereinfachung versucht oder geplant. Geschützte Passungen, Dichtflächen und Gewinde sind erfasst; Geometrievergleich und Ressourcenfelder bleiben verlinkt beziehungsweise mangels Dense-Job/Messung bewusst `null`.

## Geprüfte Dateien je Muster

- `model.scad`: parametrisierbare OpenSCAD-Quelle
- `print_plate.stl`: vorgesehene Druckanordnung
- `preview.png`: aktuelle Montageansicht; mangels Xvfb über temporäres OpenSCAD-Assembly-STL und Matplotlib `Agg` gerendert
- `README.md`: Funktions-, Druck-, Montage- und Integrationshinweise
- `metadata.json`: Parameter und Katalogdaten
- `components.json`: Bounds, Volumen, Flächenzahl, Wasserdichtheit und SHA-256 pro Körper
- `parts/part_XX.stl`: automatisch getrennte, auf den Ursprung verschobene Einzelkörper

## Prüfverfahren

1. Die OpenSCAD-Quellen 121–156 wurden erzwungen zu neuen STL-Druckplatten gerendert; 001–120 wurden bei der anschließenden Bibliotheksgesamtprüfung unverändert wiederverwendet.
2. Jede STL wurde mit Trimesh eingelesen, bereinigt und in verbundene Körper zerlegt.
3. Gesamtmesh und Einzelkörper wurden auf Wasserdichtheit, konsistente Orientierung, positives Volumen und degenerierte Flächen geprüft.
4. Die Bounding Box wurde auf Z ≥ −0,03 mm sowie auf einen 220-mm-XY-Prüfbauraum geprüft.
5. Die ermittelte Komponentenanzahl wurde mit der Mechanismusdokumentation verglichen.
6. Jede getrennte STL und jede Druckplatte erhielt einen SHA-256-Hash in den jeweiligen Berichten. Die Reproduzierbarkeitsprüfung verwendet zusätzlich einen sortierunabhängigen kanonischen Dreiecks-Hash, weil OpenSCAD die Reihenfolge identischer STL-Facetten zwischen Prozessen ändern kann.
7. `tools/validate_extension.py` prüfte Gate-Revision, öffentliche Parameter, generierte Katalog-/Sample-Artefakte, 36/36 Geometrieäquivalenzen und 27/27 Grenzfälle.
8. Ein dokumentationsspezifischer Lauf von `tools/validate_extension.py` prüfte zusätzlich 36/36 Status-/Qualifikations-/Anspruchsgrenzen ohne Geometrierendering.
9. Die DRAFT-Struktur wurde zusätzlich mit `tools/validate_library.py` auf 156 Katalogeinträge, 39 Familien, vollständige Pflichtdateien, 384 Einzelteile, OpenCode-Skill, gemeinsame SCAD-Bibliothek und beide Extension-Berichte geprüft. Dabei wird der aktuelle Extension-Vertrag einschließlich aller 36 JSON/CSV-/Metadaten-/README-/HTML-/Markdown-Anspruchsgrenzen erneut direkt aus den gegenwärtigen Eingaben berechnet; gespeicherte PASS-Zustände allein genügen nicht.

## Nicht durch die digitale Abnahme nachgewiesen

- reale Passung auf einem konkreten Drucker, Material und Slicerprofil;
- Einrast-, Auszieh-, Klemm- oder Betätigungskräfte;
- Spiel, Reibung, Verschleiß und Lebensdauer nach wiederholten Zyklen;
- Tragfähigkeit, Stoßfestigkeit, Kriechen, Temperatur- oder Chemikalienbeständigkeit;
- Normkonformität von Gewinden, Zahnrädern, Lagern oder Verbindungselementen;
- Eignung für Personenlasten oder andere sicherheitskritische Anwendungen.

Der physische Prüfablauf ist in `PHYSICAL_TEST_PLAN_DE.md` beschrieben. Vor der Integration sollte pro Mechanikfamilie zunächst die Standard- oder mittlere Variante gedruckt und anschließend die passende Toleranzvariante gewählt werden.

## Reproduzierbarkeit

```bash
python3 tools/generate_sources.py
python3 tools/build_library.py --ids 121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156 --workers 3 --preview-backend mesh --summary validation/extension-build-summary.json
python3 tools/validate_extension.py --compare-packaged --render-boundaries --require-fresh-build-summary --workers 3
python3 tools/validate_extension.py --report validation/extension-claims-validation.json --require-fresh-build-summary
python3 tools/build_library.py --workers 3 --skip-existing --skip-previews
python3 tools/build_contact_sheets.py
python3 tools/validate_library.py
python3 tools/build_package_manifest.py --check
```

`tools/build_contact_sheets.py` erhält das bereits freigegebene Konzeptbild standardmäßig unverändert; `--write-concept` darf nur nach erneutem Konzept-Gate verwendet werden. Für einen reinen Struktur- und Artefaktcheck ohne erneutes Rendern genügen `tools/validate_library.py` und der Manifest-Check.
