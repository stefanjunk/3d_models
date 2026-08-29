# Bau-, Prüf- und Inbetriebnahmeplan

## 0. Sicherheitsregeln

- erwachsene Aufsicht; nie mit Menschen oder Tieren im Wasser betreiben;
- Propeller erst nach allen Trocken-Failsafe-Tests montieren;
- LiPo nur mit Balancer-Lader und feuersicherer Umgebung laden, niemals im WTE;
- Topside möglichst aus Laptopakku; Netzteile nur über RCD/FI und weit vom Wasser;
- Schutzbrille beim Thruster-Tanktest, Haare/Kleidung fernhalten;
- ein undichtes oder aufgeblähtes System nicht erneut einschalten.

## 1. Einkaufs-Gate: zuerst nur ein Thruster-Modul

Vor dem Vollkauf bestellen und vermessen:

1. einen 2828-Motor;
2. je einen CW-/CCW-60-mm-Propeller;
3. einen bidirektionalen ESC;
4. einen WetLink bzw. das vorgesehene Kabelstück.

Prüfen: stationärer Befestigungsbereich, Schraubenmuster/-tiefe, Propelleraufnahme,
axiale Lage des Propellers, realer Außen- und Kabeldurchmesser. Danach Parameter
in `cad/generate_parts.py` anpassen und nur Nozzle/Adapter/Guard drucken.

Akzeptanz: mindestens 3,0 mm radialer und 2,0 mm axialer Freiraum bei von Hand
gedrehtem Propeller, keine Berührung bei leichtem radialem Spiel, alle Schrauben
greifen ohne Motorwicklungen zu gefährden.

## 2. FDM-Coupons und Teile

1. Sattel-Coupon und Motoradapter drucken;
2. 10-mm-Rohr mit 0,3-mm-TPU/EPDM einlegen, Kabelbinder auf Montagefestigkeit;
3. zehnmal montieren/demontieren; keine Weißbrüche oder Risse;
4. Sattel 24 h nass, 24 h trocken; erneut prüfen;
5. erst dann Vollsatz mit 0,6-mm-Düse/0,30-mm-Layer.

Im Slicer kontrollieren: vier Wandpfade, keine ungewollten Einzelbahnen, keine
Supportreste im Nozzle, geschlossene erste Schichten und mindestens drei Bahnen
in jedem Gittersteg. Druckzeiten und Materialmassen aus dem finalen G-Code im
Build-Log notieren.

## 3. Rahmenbau

1. CFK/GFK: 2×300 mm und 2×190 mm schneiden; Schnittstaub nass binden/absaugen.
2. Schnittkanten entgraten, Innen-/Außenkante mit Epoxid versiegeln.
3. Je zwei `tube_saddle` Rücken an Rücken 90° versetzt verschrauben; TPU-Pad.
4. Rechteck auf ebener Platte ausrichten, Kabelbinder paarweise anziehen.
5. Zwei `wte_cradle_75mm` über Sattel an den Querrohren befestigen.
6. Nozzles/Schieberinge lose montieren; endgültig erst nach Strömungsprüfung.
7. `tether_strain_relief` hinten oben so montieren, dass ein Zug nie am WLP anliegt.

CFK nie direkt gegen Aluminium/A4 klemmen. Kabelbinder nach den ersten fünf
Nasszyklen und danach regelmäßig ersetzen.

## 4. Elektrik – propellerlos

```text
Akku → 30-A-Sicherung → Verteilung
                     ├→ 10 A → ESC links → Motor links
                     ├→ 10 A → ESC rechts → Motor rechts
                     ├→ 10 A → ESC vertikal → Motor vertikal
                     └→ Elektronik-Sicherung → 5-V-BEC → Pi + Pico
Pico GPIO 2/3/4 → ESC-Signal, gemeinsame Signalmasse
Pico GPIO 15 ← Lecksensor (wet = LOW)
Pico ADC0/GPIO26 ← 100k/33k-Akkuteiler + 100 nF
```

Alle Hochstromverbindungen crimpen oder fachgerecht löten und zugentlasten.
Freiliegende Kontakte isolieren. BEC mit elektronischer Last testen: Pi-Kamera
streamt, Pico und Ethernet aktiv; 30 min ohne Unterspannungssymbol/Reset.

## 5. Software-/Failsafe-Gate

1. Pico flashen, **ohne Propeller** einschalten: alle Ausgänge 1500 µs.
2. Pi-Agent starten; Steuerpakete bewegen PWM erst nach 1,5 s neutralem Armzustand.
3. Nacheinander trennen: Gamepad, Topside-Prozess, Ethernet, Pi-Agent, USB-Serial.
4. Jedes Mal müssen Ausgänge innerhalb 300 ms auf Neutral fallen.
5. Lecksensor mit feuchtem Tuch brücken: sofort Neutral, Telemetrie `leak=true`.
6. Neustart mit nichtneutralem Gamepad: kein Anlaufen.
7. Strombegrenzung des Pilotprogramms auf 0,35 belassen.

Akzeptanz wird mit Oszilloskop/Logic Analyzer oder drei Servotestern dokumentiert,
nicht durch Zuhören am Motor.

## 6. Einzelthruster-Tanktest

Testwanne mit Schutzdeckel/Gitter, Motor vollständig getaucht, ESC trocken.

| Schritt | Dauer | Messwerte |
|---|---:|---|
| Neutral | 60 s | Strom, unbeabsichtigte Bewegung |
| +20 % / −20 % | je 30 s | Strom, Laufruhe, Richtung |
| +35 % / −35 % | je 60 s | Strom, Schub, Temperatur nach Stopp |
| +50 % / −50 % | je 30 s | nur wenn 35 % unauffällig |

Schub mit Küchenwaage/Lever-Stand, Strom mit Wattmeter. Abbruch bei Berührung,
starkem Vibrieren, Blasen aus Kabel/Harz, Geruch oder schneller Erwärmung.
Sicherungen und Softwarelimit werden erst anhand dieser Messung finalisiert.

## 7. Druckkörper und Durchführung

Nach jeder Arbeit an Flansch, Endkappe, O-Ring oder Penetrator:

1. Haare/Staub/Kratzer prüfen; dünn spezifiziertes Silikonfett;
2. unbenutzte Bohrungen mit passenden Blindstopfen schließen;
3. Vent offen beim Zusammenbau, anschließend schließen;
4. WTE ohne LiPo vakuumtesten nach
   [Blue-Robotics-Anleitung](https://bluerobotics.com/learn/using-the-vacuum-test-plug/);
5. als konservatives Montage-Gate mindestens etwa 31 kPa / 9 inHg Vakuum für
   15 min halten; Pumpen-/Temperaturdrift dokumentieren;
6. danach 30 min im Bad mit trockenem Papier/Feuchteindikator, noch ohne Elektrik;
7. erst dann Elektronik einbauen und Lecksensor erneut testen.

Ein Vakuumtest beweist keine beliebige Drucktiefe, findet aber Montagelecks. Die
aktuelle v0.1-Freigabe bleibt bis zum Stufentest bei 0,5–1 m.

## 8. Auftrieb und passive Stabilität

1. ROV komplett, Akku-Dummy oder geschützten Akku einsetzen, Thruster aus.
2. Schaum symmetrisch oben hinzufügen, bis das ROV gerade schwimmt.
3. 20–40 g Masse entfernen: langsamer positiver Auftrieb.
4. Roll/Pitch um etwa 30° auslenken und loslassen; es muss reproduzierbar in die
   Ausgangslage zurückkehren, ohne auf der Seite zu bleiben.
5. Edelstahlballast unten längs verschieben, bis Kamera/WTE nahezu waagrecht.
6. Maße und endgültige Schaum-/Ballastmasse protokollieren.

## 9. Gestufte Wassererprobung

| Gate | Umgebung | Dauer / Limit | Weiter nur wenn … |
|---|---|---|---|
| A | 0,3–0,5 m, klar/still | 5 min, 25 % | trocken, Failsafe und Rückkehrtrimmung ok |
| B | 1 m | 15 min, 35 % | kein Leck, keine lockeren Teile, Motorstrom plausibel |
| C | 1 m | 3 Akkuzyklen | wiederholbar, WTE nach jedem Zyklus trocken |
| D | 2 m | 10 min | erneuter Vakuumtest, Inspektion bestanden |
| E | max. 3 m | projektbezogen | dokumentierte Freigabe des schwächsten WTE-/Kabelteils |

Erste Fahrt immer in Reichweite, Tether sauber ausgelegt, Bergewerkzeug bereit.
Nach jedem Einsatz: ausschalten, Süßwasser spülen, Motoren von Hand drehen,
trocknen, WTE außen trocknen, erst dann öffnen und Akku entnehmen.
