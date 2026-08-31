---
name: 3d-design-preflight
description: Bewerte vor Beginn eines 3D-Druck- oder CAD-Designs die intrinsische Produktkomplexität, Interface-Reife, Kritikalität, Dateneignung und Workflow-Machbarkeit. Verwende diesen Skill vor jedem funktionalen Design, bei Baugruppen, Passungen, menschlichen Interfaces, Kaufteilen, bewegten Teilen, Lasten, Wärme/Strömung, Fahrzeug-/Maschinenbezug oder wenn die Erfolgswahrscheinlichkeit des 3D-Design-Workflows eingeschätzt werden soll.
metadata:
  version: "0.9"
---

# 3D Design Preflight

## Zweck

Führe vor CAD-Erzeugung eine strukturierte Machbarkeitsprüfung durch. Trenne strikt:

1. **Komplexität C0-C5** - inhärente Schwierigkeit der Aufgabe.
2. **Reife R0-R5** - Qualität und Validierung der vorhandenen Daten.
3. **Kritikalität K0-K4** - Konsequenz eines Fehlers und notwendige Prüfstrenge.
4. **Workflow-Lane A-E** - zulässiger Designpfad.
5. **Confidence Band** - qualitative Erfolgszuversicht; keine erfundene Prozentzahl.

Lade Detailrubriken nur bei Bedarf aus `rubrics/scoring-rubric.yaml`. Nutze die JSON-Schemas als verbindliche Ausgabeformate.

## Nicht verhandelbare Regeln

- Erfinde niemals Maße, Toleranzen, Varianten, Lasten, Materialeigenschaften oder versteckte Geometrie.
- Ein optisch plausibles Mesh oder CAD-Modell ist kein Nachweis für Passung, Funktion oder Sicherheit.
- `UNKNOWN` bleibt `UNKNOWN`; Unsicherheit darf nicht durch einen Durchschnittsscore verdeckt werden.
- Kritische Interfaces werden nach dem **schwächsten Evidenzglied** bewertet.
- Komplexität, Reife und Kritikalität niemals zu einem einzigen Durchschnitt verschmelzen.
- Ohne eigene historische Kalibrierung keine numerische Erfolgswahrscheinlichkeit ausgeben.
- Bei K3: nur Expert-in-the-loop-Prototyping. Bei K4: keine autonome Freigabe; Konzept- und Datenerfassungsunterstützung.
- Keep-outs, Servicezugänge, Luft-/Fluidpfade, Nutzerkontakt, Umwelt und Software sind Interfaces, auch ohne direkten Festkörperkontakt.

## Pflichtartefakt und Lebenszyklus

Dokumentiere jeden Preflight im jeweiligen Produktordner als
`preflight/preflight-result.json`. Das Artefakt muss
`schemas/preflight-result.schema.json` erfüllen und mit
`scripts/validate_preflight.py` validiert werden. Verlinke es im
`workflow.preflight`-Abschnitt der zugehörigen `design-spec.yaml`.

Führe den Preflight zu Beginn eines neuen Designs aus, bevor Konzeptbilder,
CAD-Geometrie, Quellcode oder Fertigungsexporte erzeugt werden. Eine minimale
Projekt-ID und Revision dürfen vorher nur angelegt werden, um die Artefakte
eindeutig zuzuordnen. Kennzeichne diesen Normalfall in
`traceability.mode` als `PROSPECTIVE`.

Bei einem bestehenden Design ohne Preflight erstelle den Preflight
nachträglich, bevor die nächste Designänderung beginnt:

- bewerte den aktuellen, belegbaren Stand und rekonstruiere keinen angeblichen
  historischen Wissensstand;
- setze `traceability.mode` auf `RETROSPECTIVE` und nenne
  `backfill_missing_preflight` als Change Trigger;
- verlinke die vorhandenen Anforderungen, CAD-/Mesh-Stände, Messungen, Profile
  und Tests in `basis_refs`;
- behandle nicht belegte historische Angaben als `UNKNOWN`.

Setze den Preflight auf `stale` und aktualisiere ihn vor der nächsten
betroffenen Designaktion, wenn sich Nutzung oder Scope, Host-Variante,
Anforderungen/Akzeptanzkriterien, Entitäten oder Interfaces, Evidenz,
Lasten/Umwelt, Kritikalität, Material, Drucker, Düse, Orientierung,
Prozessprofil, Verifikationsplan oder Test-/Prototypenergebnisse ändern. Eine
Aktualisierung erhält eine neue `assessment_id` oder
`assessment_version`, verweist mit `previous_assessment_id` auf den Vorgänger
und dokumentiert die tatsächlichen `change_triggers`. `current` bedeutet nur,
dass die Bewertung aktuell ist; `HOLD`, `CONCEPT_ONLY` und Lane D/E bleiben
inhaltlich bindend.

## Preflight-Ablauf

### 1. Scope und Nutzung festlegen

Erfasse:

- beabsichtigte Funktion und Ausschlüsse,
- genaue Host-/Produktvariante,
- Nutzer und Einsatzort,
- Lebenszykluszustände: Transport, Montage, Nutzung, Reinigung, Service, Demontage, Lagerung,
- erwartete Lasten, Temperaturen, Medien, Dauer und Fehlfolgen.

Falls ein sicherheitsrelevanter Kontext möglich ist, bewerte konservativ und markiere ihn ausdrücklich.

### 2. System in Entitäten zerlegen

Erstelle Knoten für:

- jedes kundenspezifische Druckteil oder Subassembly,
- Kauf-/Normteile,
- Host-Objekte,
- Mensch/Körper,
- Umgebung/Medien,
- Energie, Elektronik, Software und Daten.

### 3. Interface Register erstellen

Eine Kante ist ein prüfbarer funktionaler Vertrag zwischen zwei Entitäten. Benenne sie:

`IF-[BOUNDARY]-[DOMAIN]-[FUNCTION]-[GEOMETRY]-[NNN]`

Beispiel: `IF-EXT-GEO-CON-VOLUME-001 - Inlay zu Schubladeninnenraum`.

Erzeuge pro Interface einen Vertrag nach `schemas/interface-contract.schema.json`. Ein Interface darf mehrere Domänen haben. Teile es auf, wenn unabhängige Ausfälle, Akzeptanzkriterien oder Lebenszykluszustände existieren.

### 4. Interfaces vollständig entdecken

Prüfe systematisch:

- Auflage/Stabilität und Schwerpunkt,
- Lokalisierung, Befestigung und Lastübertragung,
- Einführrichtung, Montagefolge und Demontage,
- erlaubte/verhinderte Freiheitsgrade,
- Bewegung, Anschläge, Reibung und Verschleiß,
- Hüllräume, Kollisionsräume und Servicezugang,
- Dichtung, Drainage, Luft-/Fluidstrom,
- Wärme, Elektrik, Daten, Sicht/Sensorik,
- Nutzerkontakt, Anatomie, Ergonomie und Variabilität,
- Umwelt, Chemie, UV, Schmutz, Temperatur und Zeit.

### 5. Evidenz und Datenroute bewerten

Weise jedem kritischen Interface E0-E5 zu:

- E0 unbekannt/angenommen
- E1 Beschreibung oder unskaliertes Bild
- E2 skalierte Aufnahme/grober Scan/Teilquelle
- E3 kalibrierter Scan, offizielle Nominaldaten oder vollständige Geometrie
- E4 variantenbestätigter Vertrag mit Toleranz/Unsicherheit und Kontrollmaß
- E5 physisch validierter Test oder bewährtes Interface

Wähle die Datenerfassungsroute nach Interface-Typ:

- 2,5D-Innenraum/ebene Kante: Marker-/ChArUco-geführtes Video und analytisches Flächenfitting.
- standardisiertes Kaufteil: Hersteller-CAD, Zeichnung und Revision.
- sichtbare Freiform: kalibrierte Photogrammetrie/Strukturlichtscan plus Kontrollmaß.
- verdeckter Clip/enge Rastung: Originalteil ausbauen, Detailerfassung und Interface-Testcoupon.
- menschlich/deformierbar: Körper-/Formscan, Bewegungszustände, Material- und Nutzerprüfung.
- dynamische/lasttragende Verbindung: Geometrie plus Lastfälle, Simulation und physischer Nachweis.

### 6. Per-Interface-Komplexität berechnen

Bewerte GEO, KIN, TOL, PHY, VAR, LIF jeweils 0-4. Berechne `IC = Summe`, Bereich 0-24, Tier I0-I5. Nutze die Detailrubrik.

Leite den Projektwert INT aus Anzahl, Mittelwert und maximaler Interface-Komplexität ab. Das härteste Interface erhält die höchste Gewichtung.

### 7. Produktkomplexität PC berechnen

Bewerte REQ, CTX, PAR, INT, CPL, MOT, GEO, PHY, MAT, EXT, VER jeweils 0-4. Berechne:

`PC = Summe(Gewicht[d] * Score[d] / 4)`

Klassifiziere C0-C5. Dokumentiere die drei größten Treiber und begründe jeden Score in einem Satz.

### 8. Reife bestimmen

Bewerte jeweils R0-R5:

- Scope/Variante,
- Anforderungen,
- kritische Interfaces,
- Fertigungsprofil/Material,
- Verifikationsplan und Ergebnisse.

Projekt-Reife = Minimum dieser Werte und aller kritischen Interface-Werte. Ein kritisches E0/E1 oder `UNKNOWN` blockiert eine Fit-/Funktionsfreigabe.

### 9. Kritikalität bestimmen

Bestimme K0-K4 anhand glaubwürdiger Fehlfolgen. Produktgröße ist kein Ersatz für Kritikalität. Kontext zählt: dasselbe Regal über einem Bett ist kritischer als bodennah im Abstellraum.

Für K2-K4 erstelle eine kurze funktionale FMEA:

- möglicher Fehler,
- lokale und finale Wirkung,
- Erkennung,
- Gegenmaßnahme,
- Verifikationsmethode.

### 10. Hard Gates auswerten

- G0 Scope/Variante/Nutzung bekannt
- G1 Entitäten und Interfaces entdeckt
- G2 kritische Evidenz ausreichend
- G3 Material, Drucker, Düse, Orientierung und Prozessprofil bekannt
- G4 Akzeptanzkriterien und Prüfmethoden definiert
- G5 Kritikalität für autonomen Workflow zulässig
- G6 Montage, Service und Lebenszyklus berücksichtigt

Ein `FAIL` führt zu `HOLD` oder `CONCEPT_ONLY`, nicht zu stillen Annahmen.

### 11. Workflow-Lane wählen

- **A Generativ:** C0-C1, K0; direkter Entwurf.
- **B Parametric Fit:** C1-C2, K0-K1, R>=3; Interface-Master + Fit-Coupon.
- **C Iteratives Engineering:** C2-C3, K<=2; Subsysteme, Coupons, Funktionsschleifen.
- **D Expert-in-the-loop:** C4 oder K3; Fachprüfung, Simulation, gestufte Prototypen.
- **E Hold/Restricted:** K4, R<=1 oder Gate-Fail; keine autonome Freigabe.

Wähle konservativ, falls Regeln kollidieren.

### 12. Confidence Band ausgeben

- HIGH: keine Gate-Fails, R4/R5, C0-C2, K0-K1
- MEDIUM_HIGH: keine Gate-Fails, R4/R5, C3, K<=2
- CONDITIONAL: C3/C4 oder R3; Tests zwingend
- LOW_UNKNOWN: R0-R2 oder kritisches Interface unbekannt
- NOT_AUTONOMOUSLY_RELEASABLE: K3/K4 gemäß Lane

### 13. Ergebnis und nächste Schritte

Gib zuerst eine kompakte Scorecard aus:

`[Produkt] | C# (PC/100) | R# | K# | Lane X | Confidence`

Danach:

1. Entscheidung und Begründung,
2. Interface Register,
3. fehlende/unsichere Daten,
4. Hard Gates,
5. minimaler nächster Nachweis mit Exit-Kriterium,
6. empfohlener Design-/Testpfad.

Nutze `schemas/preflight-result.schema.json` für maschinenlesbare Ausgabe.
Speichere die validierte Ausgabe unter `preflight/preflight-result.json` und
führe aus:

```bash
python .agents/skills/3d-design-preflight/scripts/validate_preflight.py \
  path/to/product/preflight/preflight-result.json
```

## Warncodes

- `VARIANT_UNKNOWN`
- `CRITICAL_INTERFACE_UNKNOWN`
- `HIDDEN_GEOMETRY`
- `SCAN_UNCERTAINTY_EXCEEDS_ALLOWANCE`
- `DEFORMABLE_HUMAN_INTERFACE`
- `DYNAMIC_OR_FATIGUE_LOAD`
- `THERMAL_OR_FLOW_CRITICAL`
- `PURCHASED_PART_REVISION_UNKNOWN`
- `DENSE_INTERFACE_COUPLING`
- `VERIFICATION_NOT_DEFINED`
- `SAFETY_EXPERT_REQUIRED`
- `AUTONOMOUS_RELEASE_PROHIBITED`

## Post-Prototype-Lernschleife

Nach jedem Test aktualisieren:

- R-Level und E-Level,
- Interface-Vertrag und validierte Clearances,
- Anzahl Iterationen bis Fit/Funktion,
- Zeit, Material und manuelle CAD-Eingriffe,
- Fehlerklasse: Interface, Anforderung, Fertigung, Material, Montage, Sicherheit,
- akzeptiert/abgebrochen.

Erst mit ausreichend eigenen Fällen dürfen empirische Erfolgsraten nach C/R/K/Lane kalibriert werden. Erhalte auch Fehlversuche und Abbrüche, um Survivorship Bias zu vermeiden.
