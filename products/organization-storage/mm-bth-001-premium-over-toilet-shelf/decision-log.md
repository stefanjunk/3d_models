# Decision Log

## DEC-009 - Requirements-Freigabe Revision 0.2.0

- Status: approved by Stefan on 2026-08-20.
- Entscheidung: `design-spec.yaml` Revision 0.2.0 ist als strukturierte Anforderungsbasis freigegeben.
- Umfang: bodenstehender Rahmen mit zwingender Wand-Anti-Kipp-Sicherung; 256-mm-Segmentierung; PETG/0.6-mm-Prozess; zwei Ebenen; 4-kg-UDL-Ziel je Ebene; modulare und austauschbare Personalisierung.
- Folge: Das Concept-Gate ist `pending`. Es darf ein revisionsgebundenes Konzeptbild erstellt werden; Produktions-CAD und Fertigungsexporte bleiben bis zur separaten Konzeptfreigabe blockiert.

## DEC-010 - Konzeptkandidat Revision 0.2.0

- Status: approved by Stefan on 2026-08-20 for specification revision 0.2.0.
- Asset: `assets/concept/premium_over_toilet_shelf_r0.2.0_concept.png`.
- Dargestellt: bodenstehender Rahmen, Wand-Anti-Kipp-Sicherung, zwei Organisations-/Regalebenen, Drawer, Bin, Tray, Hanger und austauschbare Akzentflächen.
- Darstellungsgrenze: Die Visualisierung ist nicht maßhaltig. Vier einzelne Aufstandspunkte und die genaue Anzahl/Position der Wandhalter sind im finalen CAD aus der Spezifikation abzuleiten und im Konzeptbild nur vereinfacht lesbar.
- Folge: Architekturabgleich und Produktions-CAD für Revision 0.2.0 sind freigegeben. Fertigungsexporte bleiben DRAFT bis zur Verifikation, Kennzeichnung und finalen Freigabe.

## DEC-011 - Produktionsarchitektur des bodenstehenden Default-Builds

- Status: selected for the revision 0.2.0 DRAFT implementation on 2026-08-20; physical qualification pending.
- Rahmen: 620 mm freie Shelf-Breite zwischen zwei 20-mm-Seitenrahmen, 240 mm Rahmentiefe und 1650 mm Gesamthöhe ab Boden.
- Drucksegmentierung: sieben gleich hohe Segmente je Seite. Bei 11.2 mm Rahmen-Bodendatum ergeben sich 234.114 mm Segmentkörper und 246.114 mm maximale Druckausdehnung einschließlich 12-mm-Verbindungszapfen; rechnerisch innerhalb 256 x 256 mm.
- Aufstand: vier getrennte PETG-Füße mit austauschbaren TPU-Pads; zwei Kontaktpunkte je Seitenrahmen. Kein Lastpfad über den Spülkasten.
- Shelf-Startquerschnitt: zwei durchgehende 14 x 32 mm Randträger plus Haut/Rippen. Der konservative Einfachträger-Vergleich ergibt bei 4 kg UDL und E=1400/1800/2200 MPa etwa 1.138/0.885/0.724 mm momentane Durchbiegung ohne Plattenbeitrag; Kriechen, Nähte und Druckanisotropie bleiben physisch zu prüfen.
- Höhenraster: 50 mm, Default-Shelf-Oberseiten bei 1050 und 1400 mm ab Boden.
- Anti-Kipp: je ein höhenversetzbarer hinterer Abstandshalter pro Seitenrahmen, an zwei benachbarten 50-mm-Rasterachsen; Wandanker bleiben substratspezifische Kaufteile.
- Breite 3-Spalten-Module: Montagekörper bleiben 3-spaltig; Fertigungskörper werden bei Überschreitung von 245 mm an der Mittellinie geteilt und mit prüfpflichtigen, lösbaren M3-Nahtverbindern gefügt.
- Blockiert: Lastfreigabe, Wand-/Ankerfreigabe und Release bis zu Coupons, Slicer-, Montage-, Creep-, Proof-, Cycle- und Anti-Kipp-Tests.

## DEC-014 - Sitzkorrektur der M3-Modulnahtplatten

- Status: implemented as geometry revision `r0.2.0-draft.2` on 2026-08-21; physical seam qualification remains pending.
- Befund: Die sechs M3-Nahtplatten der geteilten Drawer-Housing-, Drawer- und Bin-Körper waren im Assembly um eine halbe Plattendicke (1.5 mm) über den 6-mm-Bossen positioniert. Die bisherige digitale Prüfung verwendete denselben falschen Bezug und meldete diesen Luftspalt als sitzend.
- Korrektur: Plattenunterseite und Bossoberseite besitzen jetzt einen expliziten parametrischen Kontaktspalt von 0.0 mm. Platten-, Loch-, Boss- und Stationsmaße liegen gebündelt unter `module_grid.wide_module_seam`; ein von null abweichender Kontaktspalt wird vor der Geometrieerzeugung abgelehnt.
- Verifikation: Unit-Regressionen prüfen den Kontakt an Housing, Drawer und Bin. Die vollständige Integration meldet für alle sechs Platten `plate_boss_contact_gap_mm: 0.0` und offene koaxiale M3-Achsen.
- Grenze: Die Korrektur stellt nur den digitalen Flächenkontakt her. Exakte M3-Inserts oder Captive Nuts, Schraubenlänge, Montagewerkzeug, Prozesscoupon, Nahtlast und Montagezyklen bleiben release-blockierend.

## DEC-012 - Revision 0.2.0 DRAFT-Geometrie und digitale Baseline

- Status: digital DRAFT candidate generated and checked on 2026-08-20; manufacturing and release blocked.
- Ergebnis: 42 eindeutige Druckdateien, 69 konfigurierte Instanzen einschließlich drei Coupon-Dateien und 63 Assembly-Körper wurden nach `output/rev-0.2.0-draft/` exportiert.
- Digitale Checks: Mesh- und Integrationsstatus PASS; vier Aufstandspunkte, sieben Seitensegmente je Seite, drei Shelf-Tiles je Ebene, Shelf-Datums 1050/1400 mm, zwei Wandhalter und sechs M3-Modulnahtverbinder nachgewiesen.
- Mesh-Bürde der Baseline vor `r0.2.0-draft.2`: 113692 Dreiecke und 5.425 MiB über alle eindeutigen Druck-STLs; globale verlustbehaftete Vereinfachung ist geometrisch nicht vorteilhaft.
- Blocker: Kein Prusa-/Orca-/Bambu-/Cura-/SuperSlicer-CLI ist verfügbar. Exakte 3MF-, Toolpath-, Zeit- und Materialwerte sowie die unabhängige Slicer-Auflösungsprüfung fehlen.
- Evidenz: `reports/optimization-baseline.md`, `reports/mesh-complexity.md` und `output/rev-0.2.0-draft/reports/validation_report.*`.

## DEC-013 - Interface-Korrekturen nach unabhängiger DRAFT-Prüfung

- Status: revised, revision-bound rebuilt and digitally regressed on 2026-08-20; manufacturing and physical qualification pending.
- Fastener-Stack: Shelf-Bracket auf M5 x 45, Shelf-to-Bracket auf M4 x 20 und Shelf-Joiner auf M4 x 16 getrennt; exakte Kaufteildimensionen und Coupons bleiben offen.
- Floor-Interface: jeder der vier Füße erhält einen M4 x 50 Querbolzen; jeder TPU-Pad vier formschlüssige Noppen. Ein eigener PETG/TPU/Rail/Lock-Coupon wurde ergänzt.
- Split-Module: Assembly- und Kollisionsprüfung verwenden jetzt die zwei realen Druckhälften und beide M3-Nahtplatten statt eines monolithischen Ersatzkörpers.
- Module: eine durchgehende 6-mm-Frontanschlagleiste begrenzt das Vorziehen; 10-N-/5-mm-Modulretention und definierte Drawer/Bin/Tray/Hanger-Lasten bleiben physisch zu prüfen.
- Traceability: Floor-Foot-Envelope, Header-Interface-Owner, Coupon-Body-Counts und Langzeitstatus wurden mit der aktuellen Source-of-Truth abgeglichen.
- Folge: Unit-, Architektur-, Spec-, Build- und vollständige DRAFT-Validation wurden erneut mit PASS abgeschlossen; Slicer-, Coupon- und physische Gates bleiben offen.

## DEC-000 - Workflow- und Bestandsstatus für Revision 0.2.0

- Status: Requirements- und Concept-Gate am 2026-08-20 für Revision 0.2.0 freigegeben.
- Entscheidung: Die vorhandene Revision 0.1.0 wird nur als digitaler Alt-Prototyp und nicht als freigegebene Produktionsgeometrie behandelt.
- Basis: Es sind digitale Builds und Reports vorhanden, aber keine revisionsgebundene Requirements-/Concept-Freigabe und keine vollständige physische oder Slicer-Evidenz.
- Folge: `design-spec.yaml` Revision 0.2.0 ist die alleinige Anforderungsquelle. Vor expliziter Concept-Freigabe werden weder Produktionsgeometrie noch Fertigungsexporte geändert oder neu erzeugt.

## DEC-006 - Installationsarchitektur

- Status: selected by user and included in the approved requirements revision 0.2.0 on 2026-08-20.
- Entscheidung: bodenstehender Rahmen mit zwingender Wand-Anti-Kipp-Sicherung.
- Basis: universeller Lastpfad ohne unqualifizierte Belastung des Spülkastendeckels.
- Trade-off: mehr Material und längere Rahmenteile als beim vorhandenen kompakten Cistern-Top-Prototyp.
- Blockiert: Concept-, Geometrie-, Last- und Release-Gate.

## DEC-007 - Prozessziel

- Status: selected by user and included in the approved requirements revision 0.2.0 on 2026-08-20.
- Entscheidung: portable Segmentierung für 256 x 256 x 300 mm, PETG, 0.6-mm-Düse und 0.30-mm-Strukturschicht.
- Basis: robuste funktionale Details und breite Druckerkompatibilität.
- Blockiert: Segmentierung, Coupons, Slicer-Baseline und finale Mesh-Exporte.

## DEC-008 - Last- und Lebensdauerziel

- Status: selected by user and included in the approved requirements revision 0.2.0 on 2026-08-20.
- Entscheidung: zwei Ebenen, 4 kg gleichmäßig verteilt je Ebene, 8 kg Proof-Test, fünf Jahre Ziel-Lebensdauer, 1000 Shelf- und 5000 Drawer-Zyklen.
- Basis: messbares Premium-Ziel ohne vorzeitige Lastfreigabe.
- Blockiert: Dimensionierung, Optimierung, physische Prüfung und Release.

## DEC-001 - Installation mode

- Status: superseded by DEC-006 for revision 0.2.0
- Decision: the default is a compact cistern-top frame with two mandatory wall-gap spacers clamped by screws through the rear tower rails into the wall.
- Basis: substantially less printed material than a floor-standing tower while keeping the storage volume above the cistern.
- Blocks: physical/release until the exact cistern and wall substrate are measured and tested.

## DEC-002 - Shelf load path

- Status: provisional
- Decision: 24 mm closed edge beams, two internal span ribs, cross ribs, male/female alignment tongues and two bolted underside seam joiners per shelf.
- Basis: a conservative hand calculation gives about 1.19 mm ideal deflection for two 24 x 12 mm continuous edge beams at 4 kg UDL before seam and creep effects. The actual ribbed panel adds stiffness, while the seam adds uncertainty.
- Blocks: physical/release until 4 kg creep, 8 kg proof and cycle tests pass.

## DEC-003 - Decoration authority

- Status: resolved
- Decision: shelf finishes, shelf text and image relief live on replaceable fascias or a replaceable header insert. Drawer/bin labels are generated into their customer-specific module bodies. Structural faces, bolt seats, shelf tops, joiners and side-grid holes remain untextured.
- Basis: preserves fits and load paths and lets customers change style without reprinting the frame.

## DEC-004 - Image relief

- Status: resolved for the digital pipeline; physical gate open
- Decision: preserve the source, generate a 16-bit build master at physical scale, and export a separate watertight relief insert. Default pitch is 0.60 mm and default engraving depth is 0.45 mm into a 2.2 mm insert.
- Basis: the 180 x 70 mm demo produces 142,068 triangles, 0.0% physical aspect error and a minimum remaining wall of 1.75 mm.
- Blocks: manufacturing/release until exact-slicer preview and a relief coupon pass.

## DEC-005 - Hardware

- Status: provisional
- Decision: M5 through-bolts retain shelf brackets; M4 heat-set inserts retain shelf tiles and seam joiners; M4 through-bolts lock side segments.
- Basis: serviceability and repeatable clamping are preferable to printed snaps for the primary load path.
- Blocks: release until actual purchased hardware is measured and coupon-tested.
