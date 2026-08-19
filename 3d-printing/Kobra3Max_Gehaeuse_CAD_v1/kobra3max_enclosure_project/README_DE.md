# Parametrisches Gehäuse für den Anycubic Kobra 3 Max

## Konzept

Dieser Entwurf ist ein **preisgünstiges Hybrid-Gehäuse** aus:

- einem tragenden Rahmen aus 20 × 20 mm Holzleisten,
- zugeschnittenen Plexiglas-/Acrylplatten,
- gedruckten Führungsschienen, Eckverbindern und Haltern,
- einer austauschbaren Serviceplatte für Lüfter, Abluftschlauch, Kabel und Filament.

Die Standardgröße beträgt außen **900 × 1050 × 900 mm (B × T × H)**. Der freie Innenraum beträgt **860 × 1010 × 860 mm**. Der Entwurf berücksichtigt als konservativen Planungsraum ungefähr **706 × 940 × 753 mm** für Drucker, Bettbewegung und Kabel. Die 940 mm Tiefe sind eine konstruktive Sicherheitsannahme und kein offizielles Anycubic-Maß.

**Vor dem Plexiglas-Zuschnitt unbedingt prüfen:** Bett von Hand vollständig nach vorn und hinten bewegen, Heizbettkabel beobachten und alle äußersten Punkte messen. Zwischen bewegten Teilen und Gehäuse sollten mindestens etwa 25–35 mm bleiben. ACE Pro beziehungsweise Filamentrolle sind für diesen Entwurf außerhalb des warmen Gehäuses vorgesehen.

## Wichtiger Statushinweis

Die STL-Dateien wurden rechnerisch auf geschlossene, wasserdichte Netze geprüft. Der Entwurf wurde hier jedoch nicht physisch aufgebaut oder probegedruckt. Tatsächliche Passungen hängen von Extrusionsfaktor, Drucker-Kalibrierung und der realen Plattendicke ab. Deshalb zuerst `rail_test_coupon.stl` drucken und mit einem Reststück Plexiglas testen.

---

## Dateien

### Parametrische Quellen

| Datei | Zweck |
|---|---|
| `kobra3max_enclosure.scad` | Parametrische OpenSCAD-Quelldatei für alle Druckteile |
| `assembly_preview.scad` | Nicht druckbare Gesamtansicht des Gehäuses |
| `dimensions_calculator.py` | Berechnet Holz- und Plexiglas-Zuschnitt für andere Außenmaße |
| `build_stls.sh` | Exportiert alle Standard-STLs erneut |
| `default_cut_list.txt` | Zuschnittliste für 900 × 1050 × 900 mm |

### Druckteile und Standardstückzahlen

| STL | Anzahl | Funktion |
|---|---:|---|
| `rail_test_coupon.stl` | 1 zuerst | 50-mm-Teststück für die Plexiglas-Passung |
| `rail_286.stl` | 18 | Drei Segmente je vertikaler Schiene, insgesamt sechs Schienenläufe |
| `rail_splice_pin.stl` | 14 | 12 benötigt, zwei Ersatz; richtet Schienensegmente aus |
| `rail_end_stop.stl` | 0–12 optional | Verschließt Schienenenden; meist nicht notwendig |
| `corner_gusset_3way.stl` | 8 | Außenliegende Dreifach-Eckverbinder für den Holzrahmen |
| `flat_t_bracket.stl` | 2 | Befestigt die mittlere Dachleiste vorn und hinten |
| `base_anchor.stl` | 4 | Verankert den Rahmen auf einer OSB-/Multiplex-Bodenplatte |
| `front_panel_shelf.stl` | 2–3 | Trägt das Gewicht der abnehmbaren Frontscheibe |
| `turn_clip.stl` | 16 | Drehbare Halter für Front- und Dachplatten |
| `turn_clip_spacer.stl` | 16 | 5-mm-Distanzscheiben unter den Drehhaltern |
| `panel_knob.stl` | 2 | Griffe für die abnehmbare Frontscheibe |
| `panel_retainer_clip.stl` | 6 optional | Zusätzliche Halter gegen Wölbung großer Scheiben |
| `service_panel_120_ports.stl` | 1 | 120-mm-Lüfter, Kabel- und Filamentdurchführungen |
| `service_panel_blank.stl` | 1 optional | Leere Alternative für eigene Bohrungen |
| `fan_adapter_120_to_100.stl` | 1 | Adapter von 120-mm-Lüfter auf 100-mm-Abluftschlauch |
| `fan_guard_120.stl` | 1 | Berührungsschutz auf der freien Lüfterseite |
| `cable_grommet_half_A/B.stl` | je 1 | Geteilte Reduzierung für die 38-mm-Kabelöffnung |
| `rail_143.stl` | nach Bedarf | Halbsegment für abweichende Abmessungen |

---

## Standard-Zuschnitt

### Holzleisten, 20 × 20 mm

| Anzahl | Länge | Verwendung |
|---:|---:|---|
| 4 | 900 mm | Vertikale Pfosten |
| 4 | 860 mm | Vordere/hintere Querleisten, oben und unten |
| 5 | 1010 mm | Seitliche Tiefenleisten plus mittlere Dachleiste |

Gesamtlänge: etwa **12,1 m**. Etwas Reserve für Fehl- und Sägeschnitte einplanen.

### Plexiglas/Acryl, Standard 4 mm

| Anzahl | Zuschnitt | Verwendung |
|---:|---:|---|
| 2 | 999 × 856 mm | Linke und rechte Seitenwand |
| 1 | 849 × 856 mm | Rückwand |
| 1 | 880 × 880 mm | Abnehmbare Frontplatte |
| 2 | 450 × 1040 mm | Zweiteiliges Dach |

Die beiden Dachplatten liegen auf Außenrahmen und Mittelsteg auf und überlappen sich über dem Mittelsteg leicht. Die Frontplatte überdeckt die 860 × 860 mm große Öffnung rundum um etwa 10 mm.

Für die Serviceplatte wird in die Rückwand ein rechteckiger Ausschnitt von **250 × 170 mm** geschnitten. Die gedruckte Platte misst 280 × 200 mm, besitzt einen Zentrierrand und wird mit acht M4-Schrauben sowie großen Unterlegscheiben befestigt. Den Ausschnitt bevorzugt im oberen hinteren Bereich platzieren, jedoch mindestens etwa 35 mm Abstand zu Scheibenkanten lassen.

### Mögliche Plattenaufteilung

Bei verfügbaren Rohplatten von 2000 × 1000 mm lassen sich die Teile typischerweise auf drei Platten verteilen:

1. Beide Seitenwände übereinander.
2. Rückwand und Frontplatte übereinander.
3. Beide Dachhälften nebeneinander.

Vor Bestellung die tatsächliche Schnittbreite des Baumarkts berücksichtigen.

---

## Einkaufsliste

### Rahmen und Abdichtung

- etwa 13–14 m gerade 20 × 20 mm Holzleisten,
- 18 mm OSB3 oder Multiplex, 900 × 1050 mm, als Bodenplatte,
- 4-mm-Plexiglas nach obigem Zuschnitt,
- 8–10 m geschlossenporiges EPDM-/Schaumdichtband, ungefähr 10 mm breit und 2 mm dick,
- neutralvernetzendes Silikon nur für dauerhaft geschlossene Fugen, optional,
- Holzschrauben 3,5 × 16 mm für die Schienen, mindestens 40 Stück,
- Holzschrauben 4 × 16 beziehungsweise 4 × 20 mm mit breitem Kopf für Eckverbinder und Halter, etwa 90 Stück,
- M4-Schrauben, Muttern und große Unterlegscheiben für Serviceplatte, Lüfter und Griffe.

### Lüftung

- regelbarer 120-mm-Lüfter oder 120-mm-PC-Lüfter mit geeignetem Netzteil,
- Drehzahlregler/PWM-Regler,
- 100-mm-Abluftschlauch, Schelle und sichere Fensterdurchführung,
- optional zwei PC4-M10-/M10-Bulkhead-Anschlüsse für 4-mm-PTFE-Schlauch,
- optional M20-/PG13.5-Kabelverschraubung.

Der Lüfter soll **nach außen absaugen**. Während des Drucks nur so stark laufen lassen, dass ein leichter Unterdruck entsteht. Nach Druckende kann für einige Minuten stärker gespült werden. Die Zuluft kommt bei der Budgetversion über die gedichteten, aber nicht hermetisch geschlossenen Frontfugen. Keine zusätzliche Heizung in das Gehäuse stellen.

---

## Druckeinstellungen

### Material

- **PETG** ist für den ersten Aufbau die praktischste Wahl.
- **ASA** ist ebenfalls geeignet, sobald bereits ein provisorisches Gehäuse vorhanden ist.
- **PLA nicht empfohlen**, da sich lange Schienen und Halter bei erhöhter Gehäusetemperatur verformen können.

### Startwerte

- Düse: 0,6 mm empfohlen; 0,4 mm funktioniert ebenfalls,
- Schichthöhe: 0,24–0,30 mm,
- Außenwände: 4,
- obere/untere Schichten: 5,
- Schienen: 15–20 % Infill,
- Eckverbinder, Dachverbinder und Frontauflagen: 30–40 % Infill,
- Lüfteradapter: mindestens 4 Wände,
- Brim bei langen Schienen und der großen Serviceplatte,
- keine Supports für die Standardausrichtung erforderlich; kleine horizontale Schraublöcher werden gebrückt.

`service_panel_120_ports.stl` wird mit der großen glatten Platte auf dem Druckbett und dem Zentrierrand nach oben gedruckt. `fan_adapter_120_to_100.stl` wird mit der quadratischen Flanschfläche auf dem Bett gedruckt.

### Passung der Plexiglasnut

Standardmäßig ist die Nut **4,4 mm** breit: 4,0 mm Material plus 0,4 mm Spiel. Baumarktplatten können hiervon abweichen.

1. Plattendicke mit Messschieber messen.
2. `rail_test_coupon.stl` drucken.
3. Das Plexiglas soll ohne Gewalt eingeschoben werden können, aber nur wenig klappern.
4. Bei Bedarf `GLASS` oder `GLASS_CLEARANCE` in OpenSCAD ändern und erneut exportieren.

Beispiel für eine gemessene Scheibendicke von 4,2 mm:

```bash
openscad -o rail_286_4p2.stl \
  -D 'PART="rail_286"' \
  -D 'GLASS=4.2' \
  -D 'GLASS_CLEARANCE=0.45' \
  kobra3max_enclosure.scad
```

Nicht die komplette Schiene im Slicer skalieren, da dadurch Schraublöcher und Segmentlänge ebenfalls verändert werden.

---

## Montage

### 1. Boden und unteren Rahmen aufbauen

1. OSB-/Multiplexplatte eben ausrichten.
2. Untere Holzleisten zu einem 900 × 1050 mm großen Rechteck zusammensetzen.
3. Vier `base_anchor` montieren und den Rahmen mit der Bodenplatte verbinden.
4. Die vier senkrechten Pfosten ansetzen und zunächst nur mäßig festschrauben.
5. Unteren Rahmen diagonal messen und rechtwinklig ausrichten.

### 2. Schienen montieren

An den vier Eckpfosten werden innen sechs vertikale Schienenläufe montiert:

- zwei für die linke Seitenwand,
- zwei für die rechte Seitenwand,
- zwei für die Rückwand.

Jeder Lauf besteht aus drei `rail_286`-Segmenten. Die flache Lasche liegt auf dem Holz; die Nut zeigt in die jeweilige Öffnung. Zwischen den Segmenten wird ein `rail_splice_pin` eingesetzt. Die Schienen jeweils etwa 1 mm oberhalb des unteren Rahmens beginnen lassen.

Erst ein Schienenpaar probeweise montieren und die zugehörige Scheibe einsetzen. Danach die übrigen Schienen verschrauben.

### 3. Feste Scheiben einsetzen

1. Dünnes Dichtband auf die Oberseite der unteren Holzleisten kleben.
2. Seiten- und Rückwand von oben in die Schienen schieben.
3. Scheiben nicht verspannen; rundum etwas Bewegung zulassen.
4. Oberen Holzrahmen aufsetzen, ausrichten und mit den acht `corner_gusset_3way` verbinden.
5. Dichtband zwischen Scheiben und oberem Rahmen verwenden.

### 4. Dach montieren

1. Mittlere 1010-mm-Dachleiste mittig einsetzen.
2. Vorn und hinten je einen `flat_t_bracket` montieren.
3. Dichtband auf den drei tragenden Dachlinien anbringen.
4. Beide Dachscheiben auflegen.
5. Mit Drehhaltern am Außenrahmen und über dem Mittelsteg sichern.

Das Dach bleibt dadurch für Wartung abnehmbar.

### 5. Frontplatte montieren

1. Zwei oder drei `front_panel_shelf` an der unteren vorderen Leiste befestigen.
2. Dichtband rund um die Frontöffnung anbringen.
3. Frontscheibe auf die Auflagen stellen.
4. Mit jeweils mehreren `turn_clip` links, rechts und oben anpressen.
5. Zwei `panel_knob` mit M4-Schrauben und großen Unterlegscheiben befestigen.

Die Auflagen tragen das Gewicht; die Drehhalter sollen die Scheibe nur anpressen, nicht allein halten.

### 6. Serviceplatte und Abluft

Empfohlene Reihenfolge von innen nach außen:

`Lüftergitter → 120-mm-Lüfter → Serviceplatte → 120-auf-100-mm-Adapter → Abluftschlauch → Fenster`

Je nach Lüfterbauform kann Lüfter und Gitter auch vertauscht werden. Entscheidend ist, dass der Luftstrom aus dem Gehäuse in den Schlauch zeigt. Zwischen Lüfter, Platte und Adapter dünnes Schaumdichtband verwenden.

Die beiden 10,2-mm-Bohrungen sind für M10-/PC4-M10-Durchführungen gedacht. Die 20,5-mm-Bohrung nimmt eine M20-/PG13.5-Kabelverschraubung auf. Die 38-mm-Öffnung ist für einen abnehmbaren Netz- oder Datenstecker; das zweiteilige Grommet reduziert sie anschließend auf ungefähr 8,5 mm Kabeldurchmesser.

---

## Parametrische Anpassung

Neue Zuschnittmaße berechnen:

```bash
python3 dimensions_calculator.py --width 950 --depth 1100 --height 950
```

Die Eckverbinder sind gegenüber geringfügig abweichenden Holzmaßen unkritisch, da sie außen aufgeschraubt werden. Für andere Scheibendicken müssen vor allem Schiene und Halter neu exportiert werden.

Eine beliebige Schienenlänge lässt sich in OpenSCAD durch Ändern des Selektors erzeugen. Beispiel: Im unteren Dateibereich vorübergehend `acrylic_rail(220,true);` aufrufen oder ein zusätzliches `PART` ergänzen.

---

## Sicherheitsgrenzen

- Das Gehäuse ist **kein Brandschutzschrank**. Plexiglas, Holz und gedruckte Kunststoffe sind brennbar.
- Einen Rauchmelder im Raum vorsehen und die ersten langen ASA-Drucke beaufsichtigen.
- Keine Heizmatte, keinen Heizlüfter und keine offene Zusatzheizung in das Gehäuse stellen.
- Netzteil, Hauptplatine, Motoren und Steckverbindungen beobachten; die Gehäusetemperatur zunächst niedrig halten und mit einem Thermometer messen.
- Abluft nicht in einen anderen Innenraum, Dachboden oder Keller leiten.
- Den Drucker vor der endgültigen Inbetriebnahme im ausgeschalteten Zustand über den gesamten Bewegungsbereich prüfen. Bett, Heizbettkabel, Druckkopf, Z-Achse und Filamentleitung dürfen nirgends anstoßen.
- Scharfe Acrylkanten entgraten. Bohrungen mit niedriger Drehzahl und geeigneter Unterlage herstellen, damit die Scheibe nicht reißt.

---

## Lizenz

Die hier erstellten CAD-Dateien und Anleitungen stehen unter **Creative Commons Attribution 4.0 International (CC BY 4.0)**. Nutzung, Anpassung und Weitergabe sind erlaubt; ein Hinweis auf den Ursprung des Entwurfs genügt.
