# Komponentengetriebener Kandidat — 0.1.0-parametric.3

## Ergebnis

Die Druckkomponenten sind passend zur realen BOM `0.1.0-bom.1` als neuer,
parametrischer DRAFT-Kandidat aufgebaut. Der Rover besitzt weiterhin genau eine
geometrische Radachse und zwei unabhängig angetriebene Räder. Es entstanden 19
separate Roverteile sowie sechs kleine Passform-Coupons; jedes Roverteil liegt
als editierbares STEP und druckorientiertes STL vor.

Die Geometrie referenziert insbesondere Pololu 4755/1995/2686, INJORA
120 × 42 mm Reifen und Zero-Offset-Räder, den 153 × 44 × 25 mm Gens-ace-Akku,
Pololu 2507, Teensy 4.1, Adafruit 4502, SpeedyBee TX800, RadioMaster RP3,
RunCam Phoenix 2 SE V2, AMASS XT60E-M und den Littelfuse-Sicherungshalter.
Herstellerangaben sind noch keine Wareneingangsmessung; diese Grenze ist in den
Parametern und Prüfberichten gekennzeichnet.

## Modellresultat

- Baugruppenhülle: 183 × 258 × 249,5 mm (Länge × Breite × Boden-bis-Oberkante)
- Reifen: 120 × 42 mm, Spurweite 216 mm, 6,0 mm nominaler Druckteil-Freigang
- zulässiger deklarierter Reifenbreitenbereich: 42–44 mm; 46 mm liegt außerhalb
- Akkuaufnahme: 1,0 mm Nennspiel je Seite und mindestens ±12 mm Längstrimm
- Kameraaufnahme: 1,0 mm Nennspiel um den 19-mm-Körper; Schraubposition als Slot
- konservative Vollmaterialmasse der Druckteile: 597,86 g PETG
- vollständiger digitaler BOM-Rechenpunkt: 2114,66 g inklusive 120 g Ballast
- Schwerpunkt relativ zur Achse: `[0,31; -0,75; 71,16]` mm
- Ballastkassette: mechanisch verschlossen, 180 g Auslegungskapazität; der
  tatsächlich einzusetzende Wert bleibt messungsabhängig

## Verifikation

Die deterministische B-Rep-Prüfung meldet `PASS`: 19 gültige positive
Einzelsolids, Symmetrie, einachsige Zweiradarchitektur, Hülle, Einzelteil-
Bettpassung, Radabstand, Motor-Mittelspalt, Akku-/Kamera-Freiraum,
Elektronik-Footprints, Landekontakt sowie vollständige Masse/COM-Ledger.

Alle 25 STL-Dateien (Rover und Coupons) sind wasserdicht, konsistent orientiert,
positiv-volumig und frei von offenen, nicht-mannigfaltigen, degenerierten und
doppelten Flächen. Die 19 Rovermeshes enthalten zusammen 68.582 Dreiecke und
3,272 MiB; das größte Einzelmesh hat 9.072 Dreiecke bzw. 0,433 MiB. Eine
zertifizierte Selbstschnittprüfung ist in der aktuellen Umgebung nicht
konfiguriert und bleibt deshalb für jedes Mesh `NOT_RUN`.

Der komponentenkorrelierte 250-Hz-Modelltest besteht die idealisierten Fälle
bei ±8°: unter 1° nach 1,32 s, maximale Translation 0,219 m und maximale
Regleranforderung 8,85 N. Das ist Plausibilitätsnachweis, keine Firmware-,
Hardware- oder Sicherheitsfreigabe.

## Druckbereitschaft

Status: **DRAFT / nicht druckfreigegeben**.

Die STL-Dateien sind für ein 220 × 220 × 250 mm Druckvolumen orientiert. Als
Planungsbasis sind 0,6-mm-Düse, 0,24-mm-Schicht, 0,66-mm-Linienbreite und PETG
eingetragen. Ein konkretes PETG-Produkt, Konditionierungszustand und vollständige
Anycubic-Maschinen-/Prozess-/Filamentprofile fehlen. Daher wurden regelkonform
weder 3MF noch G-Code noch Druckzeit-/Filamentwerte erzeugt.

Vor einem Vollausdruck sind die sechs Coupons prozessgleich zu drucken und
gegen die gelieferten Komponenten zu messen. Die Diagnose der Mesh-Schnittstellen
bleibt wegen Nearest-Vertex-Fallback `REVIEW_REQUIRED`; kritische Passungen
werden von Coupon und realem Bauteil entschieden.

## Kennzeichnung und Freigabe

Das Wasserzeichen `MM-WM-001-R2` ist noch nicht integriert. Es ist als letzte
beabsichtigte Geometrieänderung erst nach digitaler und physischer
Kandidatenannahme zulässig; anschließend ist eine vollständige Regression
erforderlich. Auch freier Balancetest, Druckstart, Sicherheit und kommerzielle
Freigabe bleiben menschliche Gates.

## Lieferumfang

- parametrische Quelle: `cad/component_parameters.py` und
  `cad/build_component_rover.py`
- 19 STEP-Master und 19 druckorientierte DRAFT-STL unter
  `cad/exports/v0.1.0-parametric.3/`
- Baugruppen-STEP, GLB/PNG-Vorschau und registrierte Komponenten-Proxies
- sechs STEP/STL-Passform-Coupons unter `cad/coupons/v0.1.0-parametric.3/`
- Druckteile-BOM, Montageplan, Regelungsmodell, Parameter-Sweep sowie
  fail-closed Geometrie-, Mesh-, Schnittstellen- und Projektberichte
