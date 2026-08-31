# OpenQuad CF5

## Deep-Research-Entwurf eines modularen 5-Zoll-Quadcopters aus 3D-Druck und COTS-Komponenten

**Stand:** 13.08.2026  
**Entwurfsstatus:** PRELIMINARY / NOT FLIGHT PROVEN  
**Regionale Annahme:** Deutschland / EASA Open Category  
**CAD:** parametrisches OpenSCAD-Modell, CERN-OHL-P-2.0  
**Baseline-Software:** Betaflight + ExpressLRS + EdgeTX

> Dieser Bericht ist eine technisch begruendete Vorentwicklung, keine
> Flugfreigabe, Zertifizierung oder Rechtsberatung. Die numerischen Checks
> pruefen Geometrie und transparente Annahmen. Gedruckte Klemmen, Ermuedung,
> Resonanz, Propulsion und Reglerverhalten muessen physisch qualifiziert werden.

---

## 1. Ergebnis in einem Satz

Der sinnvollste Hybrid ist **kein vollstaendig gedruckter Rahmen**, sondern ein
steifer, symmetrischer Lastkern aus vier handelsueblichen 10x10x1-mm-CFK-
Vierkantrohren und wenigen austauschbaren PA-CF-Knoten: 230 mm Motorabstand,
5-Zoll-Low-Pitch-Propeller, 4S/1300 mAh, aktuelle F405-V5-Elektronik und offener
Betaflight-/ExpressLRS-Softwarestack.

Die Konstruktion ist fuer Reparierbarkeit, lokale Fertigung und Experimente
interessant. Wenn das einzige Ziel ein moeglichst guenstiger und schnell
flugfaehiger 5-Zoll-Quad ist, bleibt ein konventioneller Carbonplattenrahmen wie
der [TBS Source One V6](https://www.team-blacksheep.com/products/product%3A8547)
die rationalere Wahl: etwa 30 US-Dollar, aktuelle Verfuegbarkeit, offene
[CAD-Daten](https://github.com/tbs-trappy/source_one), weniger unbekannte
Klemmstellen und ein grosserer Erfahrungsschatz.

### Empfohlene Baseline

| Bereich | Auswahl | Begruendung |
|---|---|---|
| Rahmen | vier CFK-Vierkantrohre 10x10x1 mm, je 103 mm | guenstig, bohrungsfrei, verwindungsfest, einzeln tauschbar |
| Druckteile | PA11-CF oder PA612-CF15 | bessere Temperatur-/Kriechreserve als PLA/PETG |
| Geometrie | 230 mm Diagonale, QUADX, FRONT auf 45° | ausreichend Platz fuer 5,1-Zoll-Huelle, kompakter COTS-Stack |
| Motor/Prop | EMAX ECO II 2207 2400KV + 5x3.1x3 | leicht beschaffbarer 4S-Startpunkt; niedrige Steigung fuer Ersttests |
| FC/ESC | SpeedyBee F405 V5 + OX32 55A | aktuelle Beschaffungsbaseline, 30,5-mm-Standard, Blackbox, Telemetrie |
| Funk | RadioMaster Pocket + RP1 V2, ELRS 2.4 GHz LBT | preiswert, offene Funksoftware, gute Telemetrie |
| Akku | 4S 1300 mAh XT60 | gaengiger 5-Zoll-Standard, passt auf 80x52-mm-Deck |
| Flugsoftware | Betaflight 2026.6.x stabil zum Bauzeitpunkt | beste Passung fuer manuell geflogenen 5-Zoll-Quad |
| Optional | M10-GPS + autonomer Buzzer | Bergung/GPS Rescue erst nach validiertem Basisflug |

Die aktuelle F405-V5-ESC-Firmware OX32 ist **proprietaer**. Wer maximale
Offenheit priorisiert, kombiniert einen separat beschafften FC mit einem
AM32-ESC; ein aktuell in der EU gelistetes Beispiel ist der
[T-Motor F55A Pro III AM32](https://www.drone-fpv-racer.com/en/f55a-pro-iii-4in1-esc-38s-am32-t-motor-11888.html).
Das kostet gegenueber dem V5-Komplettstack grob 50-100 EUR mehr. Die frueher
attraktiven SpeedyBee-V3/V4-BLHeli_S-Stacks koennen mit Bluejay offen betrieben
werden, werden vom Hersteller inzwischen jedoch als eingestellt gefuehrt und
sind daher nur Restpostenoptionen.

---

## 2. Missionsrahmen und bewusst gesetzte Grenzen

Der Entwurf ist kein Kamera-Cinelifter, kein BVLOS-System und kein autonomer
Lastentraeger. Er ist ein reparierbarer Forschungs-/Freizeit-Quad fuer manuelle
VLOS-/FPV-Fluege in einem rechtlich geeigneten Gebiet.

### Entwurfsannahmen

- 5-Zoll-Klasse, 4S, ca. 230 mm Motor-zu-Motor diagonal.
- Abflugmasse deutlich ueber 250 g; Zielwert etwa 540 g.
- Vier einzeln wechselbare Arme ohne Bohren oder Kleben.
- Druckteile nur dort, wo Formkomplexitaet Nutzen bringt: Knoten, Klemmen,
  Batterieplattform und Schutz-/Haltefunktionen.
- Standardisierte 30,5x30,5-mm-Elektronik und 16x16-mm-Motorlochbild.
- Keine Nutzlast ausser Flugakku, optionalem GPS/Buzzer und leichtem FPV-System.
- Erstflug nur nach dokumentierter mechanischer, elektrischer und softwareseitiger
  Gate-Pruefung.

### Nicht geloeste oder absichtlich spaet geloeste Punkte

- Keine behauptete Bruchlast der gedruckten Klemmen.
- Kein finaler PID-/Filter-Tune ohne Blackbox-Daten.
- Kein Schub-/Stromnachweis fuer die exakte Motor-Prop-Akku-Kombination.
- Kein STL-Export in der vorliegenden Laufzeitumgebung; OpenSCAD-F6-Render und
  Meshpruefung sind vor Fertigung offen.
- Keine universelle Schraubendrehmoment-Angabe fuer PA-CF. Sie wird an identischen
  Coupons experimentell festgelegt.
- Kamera-/VTX-Halter bleiben missionsspezifisch, damit der Flugkern unveraendert
  qualifiziert werden kann.

---

## 3. Was bestehende Projekte lehren

### 3.1 Vergleichsmatrix

| Projekt | Loesung | Uebernommene Lehre | Nicht uebernommen |
|---|---|---|---|
| [TBS Source One](https://github.com/tbs-trappy/source_one) | offene, konventionelle Carbonplatten | Markt-/Massen-/Reparaturbenchmark; Standardlochbilder | gefraeste Spezialplatten als alleiniger Rahmen |
| [DroneNet](https://github.com/jackyzha0/DroneNet) | gedruckter Kern plus 100-mm-Carbonrohre | Hybrid ist machbar; lange Lastpfade gehoeren ins Carbon | grosse gedruckte Rahmenmasse und projektspezifische Alt-Elektronik |
| [CogniFly](https://arxiv.org/abs/2103.04423) | sub-250-g, kollisionsrobust, semi-rigide/soft joints | Crashschutz vom steifen Flugkern trennen | weiche Gelenke im primaeren 5-Zoll-Regelpfad |
| [OpenDrone](https://github.com/ljbotero/OpenDrone) | integrierter 3D-Druckrahmen fuer FPV/Navigation | Volumenintegration und offene Dokumentation | vollgedruckte lange Arme |
| [Flix](https://github.com/okalachev/flix) | offener ESP32-Lernquad mit Simulation | kleiner, nachvollziehbarer Softwarestack fuer Lehre | ESP32 als primaerer 5-Zoll-FC |
| [Peon230](https://www.thingiverse.com/thing:629338) / [MHQ2](https://www.thingiverse.com/thing:511668) | fruehe vollgedruckte 230-mm-Rahmen | lokale Reproduzierbarkeit, modulare Ersatzteile | armtragende FDM-Geometrie und veraltete Packaging-Annahmen |
| [MFPV](https://github.com/mikeymascatu/MFPV) | modularer offener 4-/5-Zoll-Druckrahmen | Modultausch und offene Schnittstellen | Voll-FDM als Steifigkeitsbaseline |
| [Aeroptera Lace](https://aeroptera.xyz/) | grosser modularer Forschungsquad, Druckteile ausser Armen | aktuelles Beispiel fuer COTS-Rohre + gedruckte Knoten | 800-mm-/5-kg-Massstab ist nicht direkt uebertragbar |

### 3.2 Kernerkenntnisse

1. **Lange, zyklisch belastete Arme sollten nicht aus normalem FDM entstehen.**
   FDM ist hier schwerer, richtungsabhaengig und crash-/temperaturabhaengiger als
   ein preiswertes CFK-Profil.
2. **Crashschutz und Regelsteifigkeit sind verschiedene Funktionen.** CogniFly
   zeigt den Nutzen nachgiebiger Schutzstrukturen; der Gyro-/Motor-Lastpfad des
   OpenQuad bleibt dagegen steif und symmetrisch.
3. **Knoten sind der Engpass.** Das Carbonrohr ist voraussichtlich nicht das
   schwache Glied. Klemmschlupf, Layertrennung, lokale Quetschung und Schrauben-
   vorspannungsverlust dominieren die Validierung.
4. **Vibration muss gemessen werden.** Eine experimentelle Modalanalyse von
   Quadrotorrahmen identifiziert Motor-/Propellereinheiten als wesentliche
   Anregungsquellen und zeigt, dass Elektronikpositionen nicht beliebig sind
   ([ISMA-Paper](https://past.isma-isaac.be/downloads/isma2016/papers/isma2016_0797.pdf)).
5. **Simulation allein reicht nicht.** Aktuelle Arbeiten zu simulationsgetriebener
   Optimierung und FDM-Materialien sind wertvoll fuer Iterationen, ersetzen aber
   keine Coupons und physische Akzeptanztests
   ([Methodik 2025](https://www.mdpi.com/2073-431X/14/8/328),
   [FDM-Materialstudie 2025](https://www.mdpi.com/1996-1944/18/11/2465)).

---

## 4. Mechanisches Konzept

![OpenQuad CF5 Draufsicht](../output/figures/openquad_top_view.png)

### 4.1 Lastpfad

Motorzug und Motormoment laufen vom Metallmotor ueber eine flach gedruckte
Motorplatte in den U-Sattel, dann ueber 28 mm Klemmweg in das CFK-Vierkantrohr.
Der Arm liegt 31 mm im Zentralknoten und wird zwischen oberer und unterer
PA-CF-Platte vorgespannt. Acht M3-Durchgangsschrauben mit Metallunterlegscheiben
und Nyloc-Muttern schliessen den Hub. Gedruckte Gewindeeinsaetze liegen **nicht**
im primaeren Lastpfad.

Das quadratische Rohr hat drei Vorteile gegenueber Rundrohr:

- Drehmoment wird geometrisch aufgenommen; die Klemmung muss nicht allein auf
  Reibung gegen Rotation vertrauen.
- Keine Bohrung und damit keine zusaetzliche Kerbe oder Ausrichtoperation.
- Ein 1-m-Profil liefert vier Flugteile und mehrere identische Ersatzarme.

Nachteile sind mehr Stirnwiderstand, weniger Lieferanten als bei Rundrohr und
hohe lokale Kontaktspannungen an den Kanten. Deshalb haben die Sattel 10,25 mm
Startluft und die Gegenplatten eine kontrollierte 0,15-mm-Vorspanngeometrie;
das reale Rohrlos entscheidet nach Couponmessung.

### 4.2 Zentralknoten

- Aussenmass 86x86 mm, Eckradius 8 mm.
- Unter-/Oberplatte je 3,0 mm.
- Vier Rohrkanäle, Rohre beginnen 12 mm vom Mittelpunkt.
- Acht M3-Klemmpunkte bei radial 30 mm und +/-10 mm seitlich.
- Druckanschlaege enden 0,15 mm unter nominaler Rohrhoehe.
- 30,5x30,5-mm-FC-/ESC-Lochbild auf der Oberplatte.
- Vier externe Deckpunkte bei +/-32 x +/-20 mm.

Die innere Rohrluecke laesst Kabelraum im Zentrum. Kleine gedruckte Innenpfropfen
greifen als sekundaere Auszugsicherung hinter die Fuehrung, ohne das Carbon zu
bohren. Sie sind kein Ersatz fuer eine qualifizierte Klemmung.

### 4.3 Motorpods

- U-Sattel: 28 mm lang, 26 mm breit, Kanal 10,25 mm.
- Sattelseiten enden 0,15 mm unter der Rohr-Oberkante.
- Obere Motorplatte: 36-mm-Scheibe mit 28x26-mm-Zunge, 3,6 mm dick.
- Motorbild parametrisch 16x16 mm, optional 19x19 mm.
- Vier M3-Schrauben pro Pod liegen seitlich ausserhalb des Carbonprofils.

Der Motor bleibt COTS und austauschbar. Die Motorbefestigungsschrauben muessen
kurz genug sein, um keine Wicklung zu beruehren. Motorkabel werden aussen,
geschuetzt und zugentlastet gefuehrt; ein leitfaehiges, scharfes Carbonrohr ist
kein geeigneter ungeschuetzter Kabelkanal.

![Korrigierte Motorpod-Lochlage](../output/figures/openquad_motor_pod_detail.png)

### 4.4 Batterie-/Elektronikaufbau

![OpenQuad CF5 Seitenaufbau](../output/figures/openquad_side_stack.png)

Das 80x52x3-mm-Akkudeck sitzt auf vier gaengigen 25-mm-M3-Aluminium-
Abstandshaltern. Ein 74x33-mm-CNHL-Akku hat seitlich Platz; die vier Schrauben
liegen ausserhalb der Akku-Grundflaeche. Zwei unabhaengige Gurte und eine
rutschhemmende Auflage sichern den Akku. Die horizontale Propellerhuelle hat
10,15 mm Mindestabstand zur Deckkante; diese kleine, aber positive Reserve muss
am realen Aufbau inklusive flexibler Props erneut gemessen werden.

---

## 5. Geometrie- und Plausibilitaetspruefung

Die automatisierte Pruefung liegt in `analysis/validate_design.py`; Ergebnisse
werden als JSON, Markdown und Abbildungen erzeugt.

| Regel | Ergebnis | interne Entwurfsgrenze | Status |
|---|---:|---:|:---:|
| Motorabstand diagonal | 230,0 mm | festgelegt | PASS |
| Abstand benachbarter Propellerspitzen | 32,93 mm | >=20 mm | PASS |
| XY-Abstand Propeller/Akkudeck | 10,15 mm | >=8 mm | PASS |
| XY-Abstand Propeller/Nabenplatte | 7,15 mm | >=5 mm | PASS |
| Armklemmweg im Hub | 31,0 mm | >=25 mm | PASS |
| Armklemmweg im Motorpod | 28,0 mm | >=25 mm | PASS |
| Deckschraube ausserhalb Akku-Huelle | 3,50 mm | >=1,70 mm | PASS |
| Mindeststeg Motorloch/Pod-Klemmloch | 4,74 mm | >=2 mm | PASS |
| Mindeststeg Pod-Klemmloch/Rohrkanal | 2,17 mm | >=2 mm | PASS |
| Mindeststeg Pod-Klemmloch/Aussenkante | 2,30 mm | >=2 mm | PASS |

`PASS` bedeutet nur, dass die definierte Geometrieregel erfuellt ist. Es sagt
nichts ueber Druckqualitaet, Festigkeit, Ermuedung oder Flugsicherheit aus.

### 5.1 Transparentes Rohr-Screening

Fuer das 10x10x1-mm-Vierkantrohr gilt bei idealisierter, homogener Geometrie:

- Flaechentraegheitsmoment: 492 mm^4.
- Freie Laenge ab Hubkante: 72 mm.
- Illustrative Spitzenlast: 15 N.
- Nur fuer das Screening angenommener Laengs-E-Modul: 60 GPa.
- Rechenspannung am Rohransatz: ca. 11,0 MPa.
- Rechendurchbiegung an der Spitze: ca. 0,063 mm.

Diese kleine Rechenverformung zeigt lediglich, dass das Rohr im idealisierten
Modell nicht der offensichtliche Engpass ist. Lieferanten-Layup, Faserwinkel,
Kanten, Klemmpressung, Stoesse, Fatigue und insbesondere der gedruckte Knoten
sind nicht erfasst. Die 15 N sind **keine** freigegebene Pruef- oder Betriebslast.

---

## 6. Massen-, Energie- und Leistungsbudget

### 6.1 Massenabschaetzung

| Position | Masse |
|---|---:|
| vier CFK-Arme, aus Querschnitt/Dichte geschaetzt | 23,0 g |
| alle Druckteile, vor Slicer | 123 g nominal (110-135 g) |
| Schrauben, Abstandshalter, Gurte | 35 g |
| vier EMAX-Motoren | 134 g |
| SpeedyBee F405 V5 FC + ESC | 27,2 g |
| 4S/1300-mAh-Akku | 151 g |
| vier Props | 14,4 g |
| RP1, Buzzer, Kabel/XT60/Schutz | 32,2 g |
| **Startmasse nominal** | **ca. 540 g** |

Realistisch ist bis nach Slicer und Waage ein Fenster von etwa 515-575 g.
Optionales GPS addiert rund 4,7 g, ein analoges FPV-System typischerweise weitere
15-30 g. Der Entwurf ist nicht sinnvoll auf sub-250 g zu bringen, ohne Klasse,
Material und Systemarchitektur grundlegend zu aendern.

### 6.2 Energie

Ein 4S-1300-mAh-Akku hat nominal 19,24 Wh. Bei einer bewusst konservativen
80-%-Nutzung stehen etwa 15,4 Wh zur Verfuegung. Fuer nur illustrative
Schwebeleistungen von 120-160 W ergibt sich rechnerisch 5,8-7,7 min. Das ist
keine Flugzeitgarantie: Propeller, Tune, Wind, Akkuinnenwiderstand und Flugstil
dominieren. Telemetrie und nachgeladene mAh muessen die Annahme ersetzen.

### 6.3 Propulsion

Der [EMAX ECO II 2207](https://shop.emaxmodel.com/products/emax-eco-ii-series-2207-3-6s-1700kv-1900kv-2400kv-brushless-motor-for-rc-drone-fpv-racing)
ist breit verfuegbar; 2400KV passt zu 4S. Ein Haendlerdatensatz nennt fuer diese
Variante bis 43 A/720 W unter einem nicht automatisch identischen Testaufbau
([Detailquelle](https://www.readymaderc.com/products/details/EMAX-ECO-II-2207-Brushless-Motor-2400KV)).
Darum ist ein 55-A-ESC plausibel, aber nicht durch Katalogwerte freigegeben.
Der Start mit 5x3.1x3, frischem Prop, 70-%-Motor-Output-Limit und einem
instrumentierten Pruefstand reduziert das Risiko. Schub, Strom, Temperatur und
Vibration der **exakten** Kombination sind ein Gate vor dem Erstflug.

---

## 7. Markt- und Budgetanalyse

### 7.1 Beschaffungsbaseline 2026

Der [SpeedyBee F405 V5/OX32 55A](https://www.speedybee.com/speedybee-f405-v5-55a-stack/)
ist die aktuelle Generation: STM32F405, ICM42688P, Barometer, 16-MB-Blackbox,
30,5-mm-Lochbild, 3-6S, 55 A pro Kanal, DShot300/600, ESC-Telemetrie und
27,2 g FC+ESC. Der Hersteller listet 93,99 US-Dollar vor Versand/Steuern.

Die V3-50A- und V3-60A-Seiten zeigen inzwischen `Discontinued`. Sie bleiben nur
dann attraktiv, wenn ein serioeser EU-Haendler echten Lagerbestand hat und der
Preis deutlich unter dem V5 liegt. Ihr BLHeli_S-ESC kann mit
[Bluejay](https://github.com/mathiasvr/bluejay) und dem
[ESC Configurator](https://esc-configurator.com/) offen betrieben werden.

### 7.2 Budgetbaender

| Paket | Inhalt | Richtwert inkl. typischer EU-Aufschlaege, ohne Werkzeuge |
|---|---|---:|
| Fluggeraet | Rahmenmaterial, Druckverbrauch, Stack, 4 Motoren, Props, RX, 1 Akku, Buzzer, Kabel/Hardware | **285-390 EUR** |
| Startpaket | Fluggeraet + Pocket-Sender + 18650 + Ladegeraet + Smoke Stopper + LiPo-Schutz | **435-605 EUR** |
| GPS-Erweiterung | M10-GPS | 21-25 EUR |
| Analog-FPV an Bord | Kamera + TX800 + Antenne | ca. 70-95 EUR |
| FPV-Brille | nicht festgelegt | zusaetzlich, stark systemabhaengig |
| Offener AM32-Leistungspfad | separater FC + hochwertiger AM32-ESC statt V5-Stack | grob +50 bis +100 EUR |

Die vollstaendige zeilenweise BOM steht in `BOM/bom_budget_de.csv`. Marktpreise
sind volatil; Versand, deutsche Umsatzsteuer und regionale Funkvarianten koennen
das Ergebnis veraendern.

### 7.3 Einzelentscheidungen

- **Carbon:** Ein deutscher Anbieter listet 1 m
  [10x10x1-mm-CFK-Vierkantrohr](https://shop.carbon-shop.eu/Carbon-Vierkant-Rohr-100x100-x-1000-mm-CFK)
  fuer 10,50 EUR. Das reicht fuer vier Arme und mehrere Ersatzstuecke.
- **Funk:** Der [RadioMaster RP1 V2](https://radiomasterrc.com/products/rp1-expresslrs-2-4ghz-nano-receiver)
  kostet beim Hersteller 18,99 US-Dollar, wiegt 2,2 g und ist als FCC- oder
  LBT-Variante verfuegbar. Fuer Deutschland ist die passende LBT/CE-Konfiguration
  zu beschaffen.
- **Sender:** Die [RadioMaster Pocket M2](https://radiomasterrc.com/products/pocket-radio-controller-m2)
  kombiniert EdgeTX, Hall-Gimbals und internes ELRS zu niedrigen Kosten.
- **Akku:** Ein EU-Angebot des
  [CNHL 4S 1300](https://www.prodroneparts.com/en/shop/1301304bk-battery-cnhl-black-series-lipo-4s-1300mah-130c-xt60-v2-1008)
  lag bei 19,49 EUR; Marketing-C-Raten werden nicht als Designstrom verwendet.
- **Bergung:** Der [VIFLY Finder 2](https://viflydrone.com/products/vifly-finder-v2-fpv-racing-drone-buzzer)
  bleibt nach Trennung des Flugakkus aktiv. Ein Buzzer ist bei einem Prototypen
  sinnvoller als dekorative LEDs.
- **Inbetriebnahme:** Ein elektronischer
  [VIFLY ShortSaver 2](https://viflydrone.com/products/vifly-shortsaver-v2-smart-smoke-stopper)
  ist Pflichtbudget, kein optionales Komfortteil.

---

## 8. Softwarearchitektur

### 8.1 Empfohlener Stack

| Ebene | Software | Aufgabe | Offenheit |
|---|---|---|---|
| Flugregler | [Betaflight](https://github.com/betaflight/betaflight/releases) | QUADX-Regelung, Failsafe, Blackbox, optional GPS Rescue | Open Source |
| Funklink | [ExpressLRS](https://github.com/ExpressLRS/ExpressLRS/releases) | CRSF-Steuerung und Telemetrie | Open Source |
| Sender | [EdgeTX](https://github.com/EdgeTX/edgetx/releases) | Modell, Mischer, Warnungen, Telemetrie | Open Source |
| ESC Baseline | OX32 | Motor-Kommutierung/Telemetrie | proprietaer |
| ESC Alternative | [AM32](https://github.com/am32-firmware/AM32) | Motor-Kommutierung/Telemetrie | Open Source |
| CAD | OpenSCAD | parametrische Fertigungsgeometrie | Open Source |
| Analyse | Python/Matplotlib | Geometrie-, Masse-, Screening-Checks | Open Source Toolchain |

Zum Recherchezeitpunkt war Betaflight 2026.6.1 die aktuelle stabile Ausgabe,
ExpressLRS 4.1.0 und INAV 9.1.0; ArduPilot Copter 4.7.0 sowie PX4 1.17.0 waren
ebenfalls aktuell. Vor dem Bau ist jeweils die aktuelle stabile Version und das
korrekte Hardwaretarget neu zu pruefen.

### 8.2 Warum Betaflight hier gewinnt

Betaflight hat fuer einen manuell geflogenen 5-Zoll-Quad die kuerzeste und am
besten dokumentierte Kette: Motor-Wizard, Runaway-Prevention, DShot/RPM-Filter,
Blackbox und ELRS/CRSF. Die offiziellen Dokumente verlangen echte Failsafe-Tests
([Failsafe](https://betaflight.com/docs/wiki/guides/current/Failsafe)) und warnen
bei Runaway-Ursachen wie falscher Motorreihenfolge, Drehrichtung, Props oder
Sensororientierung
([Runaway Prevention](https://betaflight.com/docs/wiki/guides/current/Runaway-Takeoff-Prevention)).

RPM-Filter kann motorbezogenen Laerm gezielter unterdruecken; der dynamische
Notch bleibt fuer Rahmen-/Propellerresonanz relevant
([DShot RPM Filtering](https://betaflight.com/docs/wiki/guides/current/DSHOT-RPM-Filtering)).
Genau deshalb wird nicht vorsorglich aggressiv gefiltert: Zuerst Standardwerte,
dann Blackbox, dann eine begruendete Aenderung.

### 8.3 GPS Rescue

[GPS Rescue](https://betaflight.com/docs/wiki/guides/current/GPS-Rescue) kann den
Quad nach Funk-/Videolinkverlust in Reichweite zurueckbringen und inzwischen
auch landen. Es bleibt eine fortgeschrittene Sicherheitsfunktion, die korrekten
Home-Fix, Sensorverhalten und wiederholte Tests voraussetzt. Es wird erst nach
mehreren sicheren manuellen Fluegen aktiviert und niemals als Rechtfertigung
fuer BVLOS verwendet.

### 8.4 Wann INAV, ArduPilot oder PX4 sinnvoller sind

- **INAV:** wenn Position Hold, Wegpunkte und navigationsorientiertes Verhalten
  wichtiger werden. Die V3 hatte eine dokumentierte INAV-Prozedur; fuer den V5
  muss Support aktuell verifiziert werden.
- **ArduPilot:** wenn robuste Missionen, komplexe Failsafes und Autonomie im
  Vordergrund stehen. Die ArduPilot-Dokumentation betont reale Motor-/Prop-
  Kennfelder und warnt, dass zu grosse/langsame Props Resonanz/Oszillation
  ausloesen koennen
  ([Advanced Multicopter Design](https://ardupilot.org/copter/docs/advanced-multicopter-design.html)).
  Dafuer waere ein dokumentiert unterstuetzter H7/Pixhawk-Controller sinnvoller.
- **PX4:** fuer Forschungsintegration, ROS-2-/MAVLink-nahe Workflows und
  Pixhawk-Hardware. Das ist eine andere, groessere und teurere Systemrevision.

---

## 9. Funk- und Elektrointegration

Der F405 V5 dokumentiert UART2 und UART6 fuer Empfaenger, UART4 fuer GPS, UART5
fuer ESC-Telemetrie und UART1 fuer Bluetooth. Die Baseline nutzt UART2 fuer den
RP1 und UART4 erst spaeter fuer GPS. TX/RX werden gekreuzt. Das 10-polige
Stackkabel verbindet FC und ESC; der enthaltene 1000-uF-Kondensator sitzt mit
kurzen, polrichtigen Leitungen am Batterieeingang.

### Wichtige Inbetriebnahmeregeln

1. Props ab, Konfiguration sichern, Target `SPEEDYBEEF405V5` bestaetigen.
2. 3D-Modellbewegung im Configurator physisch pruefen. Die CAD-FRONT-Richtung
   liegt diagonal zwischen +X/+Y; ein Yaw-Wert wird nicht geraten.
3. Motorposition und -drehrichtung mit Motor-Wizard einzeln pruefen.
4. CRSF/Serial RX auf dem tatsaechlichen UART, EU/LBT auf TX und RX.
5. DShot300 als Start. Telemetrie/RPM nur akzeptieren, wenn alle vier Kanaele
   fehlerfrei melden.
6. Hersteller-Stromsensorwerte sind Startwerte und werden gegen reale mAh oder
   ein Messgeraet kalibriert.
7. Antennen frei von Carbon, Akku, VTX und Hochstromkabeln; Reichweitentest mit
   reduzierter Leistung.
8. Erster Akkuanschluss nach jeder Loetarbeit ueber Smoke Stopper.

Eine detaillierte Matrix steht in `configs/wiring_and_setup.md`.

---

## 10. Additive Fertigung

### 10.1 Materialwahl

[Prusament PA11-CF](https://prusament.com/materials/prusament-pa11-nylon-carbon-fiber/)
bietet gute mechanische, chemische und thermische Eigenschaften bei relativ
geringem Warp; eine gehaertete Duese ist Pflicht. CF-Fuellung reduziert jedoch
die Layerhaftung gegenueber ungefuelltem Polyamid, weshalb Z-belastete Sattel
weiterhin getestet werden muessen.

[PA612-CF15](https://fiberon.polymaker.com/product/pa612-cf15/) ist eine
interessante Alternative mit geringerer Feuchteempfindlichkeit als PA6-CF.
[PA6-CF20](https://polymaker.com/product/polymide-pa6-cf/) ist steif, verlangt
aber konsequente Trocknung; der Hersteller nennt 280-300 °C und 100 °C/8 h.
Das exakte Spulenprofil hat Vorrang.

PLA scheidet wegen Waerme/Kriechen aus. PETG ist fuer Passcoupons geeignet, aber
nicht als freigegebenes Flugmaterial. ASA ist UV-/waermebestaendiger als PETG,
aber fuer die primaeren Klemmen erst nach eigener Couponserie eine Alternative.

### 10.2 Startprozess

- gehaertete 0,6-mm-Duese, trockene Filamentbox, geschlossener Bauraum;
- 0,30 mm Schicht, sechs Konturen, sieben Deck-/Bodenschichten, 35 % Gyroid als
  **Startpunkt**, nicht als bewiesenes Optimum;
- Hubplatten, Deck und Motorplatten flach; Sattel Grundseite unten;
- Haltepfropfen Flansch unten; keine Supports notwendig;
- zuerst mindestens drei Kanalcoupons, dann ein einzelner Motorpod, erst danach
  der ganze Satz;
- jedes Teil wiegen und Charge/Feuchte/Profil dokumentieren.

Topologie-Optimierung darf erst nach erfolgreicher Baseline Masse entfernen.
Die effektivsten spaeteren Hebel sind lokale Fenster fern von Klemmen,
verjuengte nichttragende Deckbereiche und weniger Hardware. Primaere Bossen,
Lochraender, Klemmzungen und Lastuebergange bleiben vollwandig.

---

## 11. Montage- und Validierungsstrategie

### 11.1 Warum Gate-basiert

Ein Quad kann bei falscher Orientierung oder Motorzuordnung in Sekundenbruchteilen
unkontrolliert hochdrehen. Betaflight dokumentiert Runaway-Prevention genau fuer
diese Fehlerklasse. Der Aufbau wird deshalb nicht als ein grosser Endtest
behandelt, sondern in unabhaengige Gates geteilt:

1. Material-/Passcoupon.
2. Rahmengeometrie und Klemmung.
3. Elektrik/Polaritaet/Kurzschluss.
4. FC/Funk/Failsafe ohne Props.
5. Instrumentierter Propulsionstest in Schutzumgebung.
6. kurzes Erstschweben im freien, legalen Testgebiet.
7. erst danach GPS, FPV, hoeherer Motoroutput oder Acro.

Der vollstaendige Plan steht in `configs/acceptance_test_plan.md`.

### 11.2 Akzeptanzkriterien

- keine Risse, weissen Bruchlinien, Knackgeraeusche oder bleibende Setzung;
- keine sichtbare Armwanderung oder geaenderte Schraubenmarkierung;
- identische Diagonalen/Armlaengen und kein Rahmenkippeln;
- keine Leitung in Propellerhuelle oder an Carbonkante;
- korrektes Boardmodell, QUADX, Motorreihenfolge und Drehrichtung;
- echte RX-Unterbrechung erzeugt geplanten Failsafe;
- Blackbox und ESC/RPM-Telemetrie plausibel;
- keine unerklaerte Resonanz oder Uebertemperatur;
- nach jedem Ersttest vollstaendige Nachpruefung.

### 11.3 Abbruchkriterien

Sofort stromlos bei Rauch, Geruch, ungewoehnlichem Ruhestrom, heissem Bauteil,
Layertrennung, Carbonquetschung, Armbewegung, fehlender Motortelemetrie,
inkonsistenter Sensorbewegung oder Oszillation. Staerkeres Anziehen ist keine
Fehlerbehebung fuer eine beschaedigte FDM-Klemme.

---

## 12. Betrieb in Deutschland / EU

Mit etwa 540 g ist der privat gebaute OpenQuad kein A1-sub-250-g-UAS. In der
EASA Open Category faellt ein privat gebautes UAS unter 25 kg grundsaetzlich in
**A3**. Dort gelten unter anderem: keine unbeteiligten Personen im Betriebsbereich,
150 m horizontaler Abstand zu Wohn-, Gewerbe-, Industrie- und Erholungsgebieten
und maximal 120 m Hoehe; Betreiberregistrierung und A1/A3-Onlinekompetenz sind
erforderlich
([EASA Open Category](https://www.easa.europa.eu/en/domains/drones-air-mobility/operating-drone/open-category-low-risk-civil-drones),
[EASA FAQ](https://www.easa.europa.eu/en/the-agency/faqs/open-category)).

Fuer FPV verlangt die Open Category weiterhin VLOS. Eine zweite Person muss den
Quad direkt sehen und unmittelbar mit dem Piloten kommunizieren koennen
([EASA FPV FAQ](https://www.easa.europa.eu/en/the-agency/faqs/i-am-drone-racing-andor-flying-drones-goggles-fpv-open-category)).

In Deutschland zusaetzlich:

- Betreiber beim [Luftfahrt-Bundesamt](https://www.lba.de/DE/Drohnen/UAS_Betreiberregistrierung/UAS_Betreiberregistrierung_node.html)
  registrieren und e-ID regelkonform anbringen.
- Geozonen und aktuelle Einschraenkungen unmittelbar vor jedem Flug in
  [DIPUL](https://www.dipul.de/homepage/de/) pruefen.
- Haftpflichtversicherung nach
  [Paragraph 43 LuftVG](https://www.gesetze-im-internet.de/luftvg/__43.html)
  sicherstellen.
- Funkleistung, Frequenzregion, VTX-Kanaele und LBT-Konfiguration einhalten.

Remote ID ist nicht pauschal allein wegen `privat gebaut + A3` abzuleiten. EASA
nennt die Pflicht insbesondere fuer Specific-Operationen und klassenmarkierte
UAS; nationale/geografische Zusatzauflagen und die konkrete Betriebsart sind
aktuell zu pruefen
([EASA Remote Identification](https://www.easa.europa.eu/en/document-library/general-publications/remote-identification-will-become-mandatory-drones-across)).

---

## 13. Risikoregister

| Risiko | Eintritt / Wirkung | Gegenmassnahme | Nachweis-Gate |
|---|---|---|---|
| Klemmschlupf oder PA-CF-Layerbruch | mittel / hoch | drei Coupons, Drehmoment-/Schlupf-Reihe, Markierungen, Proof-Load | 1-2 |
| Rahmenresonanz durch modulare Knoten | mittel / hoch | steife Symmetrie, Low-Pitch-Props, Blackbox, keine blinden Filterpresets | 4-6 |
| Propellerkontakt Deck/Kabel | niedrig-mittel / sehr hoch | 10,15-mm-XY-Reserve, reale Huelle messen, Kabelzugentlastung | 2, 5 |
| ESC-Ueberstrom/Hitze | mittel / hoch | echte Schubstandmessung, 55-A-Marge, Output-Limit, Temperatur | 5 |
| falsche Board-/Motororientierung | mittel / sehr hoch | Configurator-3D-Test, Motor-Wizard, Props ab, Runaway Prevention | 4 |
| Funkverlust | niedrig-mittel / hoch | ELRS-LBT, Antennenabstand, Range Test, echter Failsafe-Test | 4, 6 |
| LiPo-Brand/Kurzschluss | niedrig / sehr hoch | Polpruefung, Smoke Stopper, Balance-Lader, geeigneter Ladeort | 3 |
| leitfaehiger CFK-Staub | mittel bei Zuschnitt / hoch fuer Elektronik | zugeschnitten kaufen oder nass/abgesaugt schneiden, PPE, reinigen/versiegeln | Fertigung |
| Lieferwechsel/abgekuendigte Elektronik | hoch / mittel | 30,5-mm-/M3-Standards, BOM vor Kauf aktualisieren | 0 |
| proprietaerer V5-ESC | sicher / mittel | dokumentieren; optional separater AM32-ESC | Beschaffung |
| unzulaessiger Einsatzort | mittel / sehr hoch | A3, LBA, Versicherung, DIPUL, VLOS-Beobachter | 0, 6 |

---

## 14. Offene Punkte und naechste Iteration

### Vor jeder Bestellung

1. V5-Stack, Motor, LBT-Empfaenger, Akkuabmessung und Carbonprofil beim konkreten
   EU-Haendler erneut bestaetigen.
2. Entscheiden, ob Beschaffbarkeit (V5/OX32) oder maximal offene ESC-Kette
   (separater AM32) wichtiger ist.
3. Optionales FPV-System festlegen; erst dann Kamera-/Antennenhalter parametrieren.

### Vor dem Druck

1. `CAD/openquad_cf5.scad` in einer aktuellen OpenSCAD-Version mit F6 rendern.
2. Jede Part-Variante einzeln als STL exportieren; Mesh auf geschlossen/manifold
   pruefen.
3. Slicer-Vorschau auf duenne Inseln, Perimeterfluss, Naht und Supportfreiheit
   pruefen; Masse und Zeit in den Bericht zurueckschreiben.
4. Kanalcoupon mit dem realen Rohr drucken und `arm_clearance` anpassen.

### Vor dem Erstflug

1. Qualifizierte mechanische/elektrische Review.
2. Coupon- und Rahmen-Proof-Tests.
3. Instrumentierter Propulsionstest.
4. Vollstaendiger Props-off-Software-/Failsafe-Test.
5. Rechtlicher/raeumlicher Check.
6. Sehr kurzes Erstschweben, danach Demontage-/Blackbox-Inspektion.

---

## 15. Schlussentscheidung

Der OpenQuad CF5 ist als **modularer Lern- und Forschungsrahmen** technisch
sinnvoll: Die 3D-Druckteile konzentrieren Komplexitaet, die COTS-Carbonrohre
tragen die langen Lastpfade, und alle teuren Komponenten bleiben standardisiert.
Das Design laesst sich lokal reparieren, ohne vier neue Arme oder gefraeste
Sonderplatten zu bestellen.

Es ist aber nicht automatisch billiger oder robuster als ein Source-One-Rahmen.
Die ehrliche Entscheidung lautet daher:

- **Fliegen mit minimalem Risiko/Aufwand:** Source One V6 oder aehnlicher
  konventioneller Rahmen, gleiche Elektronik/Software.
- **Lernen, Knoten optimieren, lokale Ersatzteile und eigene Payload-Geometrie:**
  OpenQuad CF5 bauen, aber strikt nach Gate-Plan und mit physischer Qualifikation.
- **Maximale Open-Source-Kette:** separaten AM32-ESC budgetieren; der aktuelle
  guenstige V5-Komplettstack ist auf der ESC-Ebene nicht offen.

Das Entwurfspaket liefert dafuer die parametrisierte CAD-Quelle, automatisierte
Geometrie-/Massenchecks, BOM, Verdrahtungsplan, Druck-/Montageanweisung,
Abnahmetests und das vollstaendige Quellenverzeichnis.
