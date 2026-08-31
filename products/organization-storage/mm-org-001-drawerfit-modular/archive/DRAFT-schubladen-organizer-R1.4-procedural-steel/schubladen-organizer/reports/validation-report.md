# Validierungsbericht – R1.4 prozedurale Stahltextur (DRAFT)

## Ergebnis

R1.4 ersetzt die bildbasierte Gravur vollständig durch ein deterministisches, mehrskaliges analytisches Dellenfeld. Alle vier Hauptmodule, der Kamm und vier Coupon-Typen sind digital wasserdicht/manifold und positiv volumig; die Baugruppen-3MF besteht die ZIP/CRC-Prüfung. Physische Textur-, Passungs- und Ziel-Slicer-Qualifikation stehen aus, daher bleibt der Kandidat `DRAFT`.

## Geometrie und Aufbau

| Merkmal | Ergebnis |
|---|---:|
| Baugruppenhülle | 227 × 357 × 64 mm |
| Größtes Einzelmodul | 135 × 186,5 × 64 mm |
| Hauptmodule | 4 |
| Hardwarefächer | 8, in 2 × 4 |
| Boden | 2,6 mm |
| Basiswand | 3,2 mm |
| Connector-Nennfreigabe | 0,30 mm |
| Druckorientierung | flache geschlossene Unterseite, supportfrei vorgesehen |

## Texturabdeckung

| Modul | Boden-Dellen | Innenwand-Dellen | Wandtop-Dellen |
|---|---:|---:|---:|
| Driver vorn | 297 | 710 | 37 |
| Driver hinten | 287 | 692 | 45 |
| Hardware vorn | 394 | 1.013 | 50 |
| Hardware hinten | 363 | 827 | 54 |

- Repräsentation: `deterministic-multiscale-analytic-dimple-field`
- Seed: `140421`
- Maximale Nenntiefen: Boden 0,28 mm; Innenwände 0,23 mm; Wandoberseiten 0,13 mm.
- Aktiv: Fachböden, innere Seitenwände, Wandoberseiten.
- Inaktiv/glatt: Außenwände, Connectoren, Wandknoten, Griffnuten, Gussets, Bettauflage und Kennzeichnungsbereiche.
- Bild-/Heightmap-Pfad im Produktionsbuild: inaktiv; dadurch kein Bildseitenverhältnis oder Stretch-Fit.

## Wandreserven

| Zone | berechnete Reststärke | Grenze |
|---|---:|---:|
| Boden unter tiefster Oberflächentextur | 2,32 mm | ≥ 2,00 mm |
| Boden unter Unterseitenkennzeichnung | 2,20 mm | ≥ 2,00 mm |
| doppelseitig texturierte Trennwand | 2,74 mm | ≥ 2,00 mm |
| einseitig texturierte Außenwand-Innenfläche | 2,97 mm | ≥ 2,00 mm |

## Netzprüfung

| Fertigungsdatei | Dreiecke | Ergebnis |
|---|---:|---|
| Driver vorn | 113.986 | PASS |
| Driver hinten | 115.332 | PASS |
| Hardware vorn | ca. 160.700 | PASS |
| Hardware hinten | ca. 143.900 | PASS |
| Schraubendreherkamm | 612 | PASS |
| Eckcoupon | 100 | PASS |
| Stahltextur-Coupon | 11.102 | PASS |
| Connector male | 152 | PASS |
| Connector female | 144 | PASS |

Für jede STL wurden geschlossene Kantenpaare, manifold Topologie, positive endliche Dreiecksflächen, positive Volumina und die erwartete Einzelkörperstruktur geprüft. Die vier Hauptmodelle benötigen nach Float32-Export nur einen lokalen Kollaps numerisch degenerierter Mikrokanten; Funktionsflächen werden dabei nicht versetzt.

## Connectorprüfung

- X- und Y-Connectoren werden aus demselben runden Zylinder-Lug plus geradem Hals erzeugt; im Produktionscode gibt es keine dreieckige Connectorvariante.
- Dreiecksprismen im Modell sind ausschließlich Wandwurzel-Gussets und nicht Teil der Steckverbinder.
- Male- und Female-Coupon sind byte-identisch zu R1.3; die Texturumstellung hat ihre Kontur nicht verändert.
- Die vom Nutzer gemeldete reale Nichtpassung ist deshalb noch offen. Die Geometrie ist digital konsistent, aber nicht physisch qualifiziert. Vor einem Connector-Redesign müssen Coupon-Istmaß, Druckorientierung und Elefantenfuß erfasst werden.

## Speicher und Sequenz

- Ein Modul je Prozess, Texturpatches sequenziell, CSG-Dellen in Batches.
- Gemessener Worst Case: 326,215 MiB = 0,319 GiB = 0,342 GB dezimal Peak-RSS.
- Konfiguriertes Ziel: 1.536 MiB; harter Stop: 3.072 MiB.
- Frühere R1.3-Heightmap: bis etwa 2.084 MiB und 1,26–1,87 Millionen Dreiecke je Modul.
- R1.4 reduziert den gemessenen Peak damit um rund 84 % und die Modulnetze grob um 90 %.

## Manufacturing-Mesh-Simplification-Gate

Ergebnis: `not-beneficial` für zusätzliche verlustbehaftete Decimation.

Die Komplexität wurde bereits an der frühesten sicheren Stelle reduziert: Bildraster und Heightfield wurden durch analytische Mehrskalenmerkmale ersetzt; Funktionsflächen werden parametergesteuert geschützt. Die aktuelle feinste Exportbereinigung beträgt 0,0001 mm und dient nur numerischer Redundanz. Eine zusätzliche globale Decimation würde Connectoren, Bettauflage, Wandtops und Kennzeichnung gefährden, ohne bei höchstens etwa 161.000 Dreiecken pro Hauptmodul einen sinnvollen Vorteil zu liefern. Referenz- und Fertigungsnetz bleiben daher dieselbe hochpräzise, reproduzierbare Ausgabe.

## 3MF und Reproduzierbarkeit

- 3MF: vier benannte Hauptobjekte in korrekter globaler Position.
- Container: Core-Namensraum und CRC vollständig geprüft.
- Parameterloser Rebuild: `python3 rebuild.py`.
- Alle Geometrie-, Textur-, Speicher- und Ausgabewerte stammen aus den beiden JSON-Parameterdateien.
- Geometriehashes und Release-Manifest werden beim Packaging neu erzeugt.

## Kennzeichnung

Die exakte kompakte JuSt-Innovation-Geometrie `JSI-WM-001-R1` ist 0,40 mm tief auf der druckbettseitigen Unterseite aller vier Hauptmodule eingelassen. Restboden und Bett-Datum bestehen die digitale Geometrieprüfung. Eine echte Ziel-Slicer-Vorschau der ersten kennzeichnungstragenden Schichten sowie erneute finale Nutzerfreigabe fehlen; das Watermark-Gate bleibt daher blockiert.

## Offene Freigabepunkte

1. Stahltextur-Coupon mit Zielmaterial, 0,40-mm-Düse und 0,20-mm-Schichten drucken und visuell/haptisch bewerten.
2. Connectorpaar drucken, Fügegefühl und Istmaße dokumentieren; bei Bedarf `connectors.clearance` in 0,05-mm-Schritten anpassen.
3. Eckcoupon in der realen Schublade prüfen.
4. Baugruppen-3MF im Ziel-Slicer öffnen und erste drei Schichten, Wandtops, Connectoren, glatte Keep-outs und Kennzeichnung kontrollieren.
5. Erst nach diesen Nachweisen finale Freigabe erteilen und `DRAFT` entfernen.
