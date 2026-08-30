# Montageplan — 0.1.0-parametric.3 (DRAFT)

Dieser Plan beschreibt die digitale Passlogik der 19 Druckteile. Er ist keine
Freigabe für einen freien Fahr- oder Balancetest. Vor dem Vollausdruck müssen
die sechs Passform-Coupons mit den tatsächlich gelieferten BOM-Komponenten und
dem vorgesehenen Material-/Druckprofil geprüft werden.

## 1. Bauteileingang und Coupons

1. Beide Pololu-4755-Motoren, 1995-Halter, 2686-Adapter, die montierten
   INJORA-Räder, den Gens-ace-Akku, alle Leiterplatten, Kamera, XT60E-M und
   Sicherungshalter eindeutig kennzeichnen, wiegen und vermessen.
2. Die sechs Dateien unter
   `cad/coupons/v0.1.0-parametric.3/validation-mesh/` prozessgleich drucken.
3. Bracket-Slots, Akkuweite, Kameraweite/Schraubschlitz,
   Pololu-2507-Lochbeziehung, TX800-Lochbild und XT60-Panelpassung gegen die
   gelieferten Teile protokollieren. Ein Klemmsitz darf Kabel, LiPo-Hülle oder
   Leiterplatte nicht belasten.
4. Abweichungen zuerst in `cad/component_parameters.py` korrigieren; danach
   alle STEP/STL- und Validierungsartefakte neu erzeugen.

## 2. Unterbau und gemeinsame Achse

1. `side-frame-left/right`, `axle-crossmember` und beide `motor-pod`-Teile
   locker mit Metall-Durchgangsschrauben montieren.
2. Je einen Pololu-1995-Halter mit seinen drei M3-Punkten in den axialen
   8-mm-Slots ausrichten. Beide Motorachsen müssen denselben Y-Datum bilden;
   die Langlöcher sind nur für die registrierte Musterlage vorgesehen.
3. Pololu 4755, 2686-Adapter und die fertig montierten INJORA-Räder einsetzen.
   Rundlauf, axiale Sicherung und Freigang über eine vollständige Radumdrehung
   prüfen. Der CAD-Nennwert beträgt 6,0 mm zwischen 42-mm-Reifenhülle und
   Druckteil; 44-mm-Reifenbreite ist mit 5,0 mm noch im deklarierten Vertrag.
4. Erst nach koaxialer Ausrichtung alle Strukturverbindungen gleichmäßig
   anziehen und gegen selbstständiges Lösen sichern.

## 3. Akku, Elektronik und Versorgung

1. `battery-crossmember` und `battery-cradle` montieren. Die 28-mm-Slots
   erlauben mindestens ±12 mm Längstrimm; die Mittellage markieren.
2. Akku ausschließlich mit zwei mechanischen Gurten halten. Keine Schraube,
   scharfe Kante oder Drucknase darf die LiPo-Hülle berühren.
3. `electronics-crossmember`, `electronics-deck` und `imu-datum` montieren.
   Die IMU starr, wiederholbar und achsenrichtig befestigen; weiche Klebepads
   sind nicht der definierte Datumspfad.
4. Pololu 2507, Teensy 4.1, Adafruit 4502, Pololu 2851, RP3 und TX800 erst nach
   bestandenem Coupon-/Musterabgleich befestigen. RF-Aktivbereiche und
   Kühlflächen freihalten.
5. `power-service-panel` mit XT60E-M und ATO-FKH bestücken. Leistungsleitungen
   nicht über Steckbrettkontakte führen; Zugentlastung und berührungssichere
   Isolation vorsehen. Der 15-A-Fuse-Wert ist nur ein Startwert für den
   gefesselten Stromtest.

## 4. Kamera, Antennen, Landung und Trimmgewicht

1. RunCam in `camera-guard` montieren und optisches Sichtfeld, Steckerzugang
   sowie Linsenfreigang prüfen.
2. `antenna-guide-left/right` so einsetzen, dass leitfähige Struktur und
   bewegte Reifen von den aktiven Antennenbereichen fernbleiben.
3. `landing-front/rear` mit Metall-Durchgangsschrauben befestigen. Beide Teile
   sind nicht rollend und sollen erst ab mindestens 22° Neigung tragen.
4. `ballast-cassette` und `ballast-lid` mit vier M3-Durchgangsschrauben
   schließen. Stahlsegmente müssen vollständig eingeschlossen sein; Kleber ist
   keine strukturelle Rückhaltung.
5. Ohne Messung keine 180 g einsetzen. Der digitale Rechenpunkt verwendet
   120 g und ergibt 2114,66 g Gesamtmasse bei COM-Z 71,16 mm. Tatsächlich nur
   so viel Trimmgewicht einsetzen, dass das gewogene Gesamtsystem die
   freigegebenen Massengrenzen einhält.

## 5. Abnahmefolge vor Motorleistung

- Mechanische Vollständigkeit, Schraubensicherung, freie Räder und erreichbare
  Trennstelle prüfen.
- Gesamtmasse, COM-Lage, Radhalbmesser und Massenträgheit erfassen und das
  Regelungsmodell neu korrelieren.
- Polarität, Encoder-Richtung, Überstrom-, Unterspannungs-, Diagnose- und
  RC-Verlustpfade bei abgenommenen Rädern bzw. gefesselt prüfen.
- Erst danach den dokumentierten gefesselten Testaufbau verwenden. Ein freier
  Balancetest, Druckstart oder Upload zum Drucker benötigt eine separate
  menschliche Freigabe.
