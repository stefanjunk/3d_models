# Beschaffungs-BOM — MM-TOY-003 `0.1.0-bom.1`

Prüfdatum: 2026-08-30

Status: **Beschaffungskandidat; keine Produktions-, Druck- oder Betriebsfreigabe**

Die vollständige zeilenweise BOM mit Herstellerteilenummern, Mengen, Preisen,
Massen, Händler- und Alternativlinks steht in
[`architecture/bom-procurement-v0.1.0-bom.1.csv`](../architecture/bom-procurement-v0.1.0-bom.1.csv).
Preise sind Momentaufnahmen inklusive Umsatzsteuer, soweit der Händler sie so
ausweist, aber ohne Versand, Zoll und Mengenrabatte.
Die maschinenlesbaren Summen- und Strukturprüfungen stehen in
[`validation/procurement-bom-validation-v0.1.0-bom.1.json`](../validation/procurement-bom-validation-v0.1.0-bom.1.json).

## Ergebnis

Die Beschaffung ist technisch auf eine zusammenhängende Kette festgelegt:

- zwei Pololu-4755-Encodergetriebemotoren mit den gefrästen
  Pololu-1995-Haltern und 2686-Adaptern;
- zwei 120 × 42 mm INJORA-Reifen auf 1,9-Zoll-Aluminium-Beadlockfelgen mit
  12-mm-Sechskant;
- ein Gens ace `GEA503S60X6GT`, 3S/5000 mAh/XT60, als Traktionsakku;
- ein Pololu-Dual-VNH5019-Treiber `2507` anstelle des bisherigen
  Cytron-MDD10A-Kandidaten;
- Teensy 4.1, Adafruit-ISM330DHCX `4502` über SPI und RadioMaster RP3 V2 über
  CRSF-UART;
- Pololu-D24V50F5 als 5-V-Schiene sowie ein definierter 15-A-ATO-Schutzpfad;
- RunCam Phoenix 2 SE V2 und SpeedyBee TX800 für den unabhängigen Analog-FPV-Pfad.

Alle kritischen Teile sind konkret identifizierte Herstellerprodukte; beim
TX800 muss vor der Bestellung allerdings die Wiederverfügbarkeit geprüft
werden. Amazon oder AliExpress sind dort als Alternative eingetragen, wo die
Identität über Herstellerteilenummer oder SKU kontrollierbar ist. Für Motoren,
Treiber, Sensoren, Sicherung und Spannungsregler werden autorisierte
Elektronik- oder Robotikhändler bevorzugt, weil bei diesen Teilen ein ähnlich
aussehendes Marketplace-Modul nicht automatisch elektrisch gleichwertig ist.

## Kostenrahmen

| Warenkorb | Schätzwert ohne Versand |
|---|---:|
| Rover-Bauteile P01–P22 | 571,67 € |
| plus Sender, Senderzellen und Ladegerät A01–A03 | 706,86 € |
| plus neue Skyzone-Cobra-SD-Brille A04 | 945,86 € |

Die FPV-Brille ist optional, falls bereits ein kompatibler analoger
5,8-GHz-Empfänger vorhanden ist. Die vierer Reifen- und Felgensätze enthalten
je zwei Ersatzteile. Verbrauchsmaterial, Versand und mögliche Mehrfachbestellungen
nach einem fehlgeschlagenen Test sind nicht belastbar eingepreist.

## Warum diese Komponenten zusammenpassen

### Antrieb

Der [Pololu 4755](https://www.pololu.com/product/4755) liefert bei 12 V
100 min⁻¹ Leerlaufdrehzahl. Mit 120-mm-Rädern ergibt das ideal etwa 2,26 km/h
und liegt damit nahe am festgelegten 2,5-km/h-Limit. Der 6-mm-D-Schaft wird mit
dem [Pololu-2686-Adapter](https://www.pololu.com/product/2686) auf den
12-mm-Sechskant der INJORA-Felge umgesetzt. Die Herstellerwerte von 5,5 A und
34 kg·cm am Blockierpunkt sind extrapolierte Grenzwerte und ausdrücklich keine
Dauerfreigabe.

Der ausgewählte [Dual-VNH5019-Treiber](https://www.pololu.com/product/2507)
verträgt 3,3-V-Logik, bietet zwei Strommessausgänge mit etwa 140 mV/A,
EN/DIAG-Leitungen sowie thermische und Kurzschlussschutzfunktionen. Damit lässt
sich die geforderte Strom- und Fehlerüberwachung wesentlich direkter aufbauen
als mit dem bisherigen MDD10A. Das ersetzt trotzdem keinen gemessenen
Stromgrenzwert und keinen thermischen Versuch.

### Regelung und Funk

Der [Teensy 4.1](https://www.pjrc.com/store/teensy41.html) hat genügend
Timer-, Encoder- und SPI-Ressourcen für die vorgesehenen 500-Hz-IMU- und
250-Hz-Regelzyklen. Das [Adafruit-ISM330DHCX-Board](https://www.adafruit.com/product/4502)
ist ein konkretes, lieferbares 6-Achs-Board. Für die endgültige Montage wird es
starr verschraubt und per SPI angebunden; ein flexibles Qwiic-Kabel ist keine
zulässige finale IMU-Lagerung.

Der [RadioMaster RP3 V2](https://www.radiomasterrc.com/products/rp3-expresslrs-2-4ghz-nano-receiver)
liefert CRSF statt einzelner PWM-Leitungen, besitzt Antennendiversität und
ermöglicht explizite Link- und Frame-Überwachung. Dazu passt der
[Pocket ELRS EU-LBT](https://www.radiomasterrc.com/products/pocket-radio-controller-m2).
Firmware-Domain, Arm-Schalter, Begrenzungen und Failsafe werden vor einem
Rad-am-Boden-Test protokolliert geprüft.

### Energie und FPV

Der 5000-mAh-Akku ist bewusst größer als ein 2200-mAh-Shorty gewählt. Er nutzt
den Akku als funktionale, hoch liegende Pendelmasse und gibt für das
20-Minuten-Ziel deutlich mehr Reserve. Mit 80 % nutzbarer Kapazität erfordert
20 Minuten Laufzeit höchstens etwa 12 A mittleren Akkustrom; die reale
Stromaufnahme muss geloggt werden, bevor daraus eine Laufzeitaussage wird.

Die 5-V-Verbraucher hängen am
[Pololu D24V50F5](https://www.pololu.com/product/2851). Der positive Akkupfad
erhält einen [Littelfuse-ATO-FKH-Halter](https://de.rs-online.com/web/p/sicherungshalter/7874340)
mit [15-A-ATO-Sicherung](https://www.digikey.de/de/products/detail/littelfuse-inc/0ATO015-V/2519127).
15 A ist ein Startwert für den Prüfstand: Er muss Leitungen schützen, darf aber
bei zulässigen kurzen Balanceimpulsen nicht ungewollt auslösen. Der zugängliche
XT60E-M ist ein Service-Trenner. Wo möglich, werden zuerst beide Motorkanäle
über EN/DIAG deaktiviert; das Abziehen unter regenerativem Strom bleibt bis zur
Oszilloskopprüfung gesperrt.

RunCam-Kamera und TX800 bilden einen vollständig getrennten Videopfad. Für den
TX800 wird die EU-Tabelle geladen und ausschließlich eine am Betriebsort
zulässige Einstellung verwendet; die jeweils aktuelle Frequenzzuteilung muss
vor Betrieb anhand der
[Bundesnetzagentur-Allgemeinzuteilungen](https://www.bundesnetzagentur.de/DE/Fachthemen/Telekommunikation/Frequenzen/Allgemeinzuteilungen/start.html)
geprüft werden. FPV-Ausfall darf niemals Arming, Balance-Failsafe oder Stoppen
blockieren.

## Massen- und CAD-Auswirkung

Die neue BOM passt nicht unverändert in den aktuellen Proxy:

| Gruppe | bisheriger Proxy | BOM-Schätzung | Wirkung |
|---|---:|---:|---|
| zwei Räder einschließlich Hub/Adapter | 210 g | ca. 358 g | +148 g direkt auf Achshöhe |
| Akku und geschätzter Schutz-/Kabelpfad | 390 g | ca. 440 g | ungefähr gleicher hoher Massenblock |
| Treiber, MCU, IMU und Empfänger | 150 g | ca. 52 g | rund 98 g weniger im Obergeschoss |
| Kamera, VTX und Antennen | 43 g | ca. 19 g | rund 24 g weniger oben |

Unter Beibehaltung der derzeitigen gedruckten B-Rep-Massen ergibt die
BOM-Schätzung vor Trimmgewicht rund **1,95 kg** und einen vertikalen Schwerpunkt
von nur ungefähr **60 mm**. Das verletzt `ACC-MASS-001` mit 70–110 mm. Rund
**180 g** mechanisch eingeschlossene Stahlsegmente bei etwa `z = 186 mm`
würden rechnerisch ungefähr **2,13 kg / 70,8 mm** ergeben. Wegen Liefer- und
Slicermassentoleranzen wird kein fester Ballastwert freigegeben; zu erwarten
sind etwa 150–250 g in 5-g-Schritten. Oberhalb von 2200 g ist die Konfiguration
unzulässig.

Der Akku ist mit 153 mm zudem länger als der bestehende 100-mm-Cradle-Proxy.
Felgenbreite, Null-Offset, Adapterlänge und Reifenbreite verändern ebenfalls
die Achs-/Karosserieschnittstelle. Eine neue CAD-Revision muss daher um die
gemessenen Teile aufgebaut werden; der aktuelle `parametric.2`-Stand bleibt
DRAFT.

## Bestell- und Prüfablauf

1. P01–P19 nach bestätigtem Lagerbestand als je einen realen
   Prüfstand-/Integrationssatz bestellen; P14 erst bei Wiederverfügbarkeit,
   von Motoren und Haltern jeweils zwei Stück. P20/P21 erst nach eingefrorenem
   Kabel- und Schraubenplan ablängen bzw. final zählen.
2. Jede Lieferung mit Hersteller-ID, Fotos, Waage und Messschieber erfassen.
   Besonders Akku, Felge/Reifen, Adapter, Motorwelle, IMU-Achsen und
   PCB-Lochbilder werden nicht aus Shopbildern abgeleitet.
3. Den vollständigen Rover ohne Trimmmasse wiegen und den Schwerpunkt messen.
   P22 ausschließlich in einer verschraubten oberen Kassette einsetzen; die
   Klebeschicht ist nicht die mechanische Halterung.
4. Erst danach Batteriecradle, Radabstand, Elektroniktray und Ballastkassette
   als neue CAD-Revision erzeugen und `ACC-MASS-001`, Breite, Kollisionsfreiheit
   und Landeschutz erneut prüfen.
5. Stromversorgung zunächst mit frei drehenden Rädern und Strombegrenzung
   testen. Danach folgen Encoder-/IMU-Richtung, Watchdog, Fehlerpfade und der
   bereits definierte gefesselte Balance-Test. Freies Fahren bleibt bis dahin
   gesperrt.

## Offene Freigabepunkte

- gelieferte Teile sind noch nicht vermessen oder gewogen;
- Felge, Adapter und Motor wurden noch nicht gemeinsam auf axialen Sitz,
  Rundlauf und Sicherung geprüft;
- reale Druckmasse und Trimmgewicht fehlen;
- Sicherungswert, Verkabelung, Stromgrenzen, Regeneration, BEC-Brownout und
  Motorkühlung sind nicht praktisch qualifiziert;
- TX800-Verfügbarkeit war eingeschränkt, Kamera-Bestände waren knapp;
- keine Firmware, kein Hardware-in-the-loop-Test und kein physischer
  Balanceversuch existiert.

Die BOM ist damit als Beschaffungsgrundlage für Muster und Prüfstand verwendbar;
P14 wartet auf Lagerbestand. Sie ist nicht ausreichend für eine Aussage wie
„aufbauen, einschalten und sicher frei fahren“.
