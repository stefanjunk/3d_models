# 3D Design Preflight Skill v1.0

Dieses Paket enthält ein research-basiertes, aber bewusst **noch nicht statistisch kalibriertes** Preflight-System für 3D-Druck- und CAD-Projekte.

## Dateien

- `SKILL.md` - kompakte Agentenlogik und Freigaberegeln
- `rubrics/scoring-rubric.yaml` - vollständige Bewertungsrubriken
- `schemas/interface-contract.schema.json` - Interface-Vertrag
- `schemas/preflight-result.schema.json` - maschinenlesbares Ergebnis
- `scripts/validate_preflight.py` - Schema-, Traceability- und Projektzuordnungsprüfung
- `templates/preflight-input.yaml` - Aufnahmeformular
- `templates/interface-register.yaml` - Interface-Register
- `examples/example-assessments.yaml` - Beispielbewertungen
- `examples/preflight-result.example.json` - vollständiges validierbares Ergebnisbeispiel
- `references/research-basis.md` - Forschungsbasis und Grenzen
- `references/product-intake.md` - SKU-, Produktordner-, Portfolio- und Lizenzketten-Gate

## Empfohlene Integration

1. Preflight als Pflichtschritt vor dem 3D Functional Design Workflow ausführen.
2. Bei Lane A/B kann der Design-Agent nach bestandenen Gates starten.
3. Bei Lane C erzeugt er zuerst Interface-Master und Testcoupons.
4. Lane D verlangt Fachprüfung und gestufte Nachweise.
5. Lane E blockiert Endfreigabe und beschränkt die Arbeit auf Konzept/Data Acquisition.

Der kanonische Projektpfad ist `preflight/preflight-result.json`. Neue Designs
verwenden `PROSPECTIVE`; ein fehlender Preflight in einem Bestandsdesign wird
vor der nächsten Designänderung als `RETROSPECTIVE` Backfill erstellt und mit
den tatsächlich vorhandenen Quellen verknüpft.

Neue Produktidentitäten müssen zusätzlich vor der Designerzeugung eindeutig
per SKU registriert, unter `products/<family>/<sku>-<slug>` abgelegt, in der
CSV-Quelle und der generierten Portfolio-XLSX erfasst und mit einer
produktlokalen Lizenz-/Provenienz-Kette verknüpft sein. Komponenten und
Vorprodukte eines bestehenden Produkts erhalten nicht automatisch eine neue
SKU.

Die Gewichte und Schwellwerte sind eine operationale Synthese. Sie sollten nach 30-100 dokumentierten Projekten gegen reale Erstpassungs-, Funktions- und Iterationsdaten kalibriert werden.
