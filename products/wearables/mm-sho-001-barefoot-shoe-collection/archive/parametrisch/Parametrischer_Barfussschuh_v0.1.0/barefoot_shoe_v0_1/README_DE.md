# Parametrischer Barfußschuh v0.1

Dieses Paket enthält zwei linke und rechte Schuhvarianten im Stil der orange-schwarzen Referenzbilder:

1. **Textilvariante:** gedruckte TPU-Sohle, 1:1-Schnittmuster für atmungsaktiven Stoff, Zunge, Fersenverstärkung und Schlaufe.
2. **Voll gedruckte Variante:** dieselbe TPU-Sohle plus offener TPU-Netzoberschuh und acht verstärkte Schnürösen als positionierte 3MF-Baugruppe.

Die Modelle sind vollständig parametrisch. Version 0.1 ist jedoch **ein Passform-Prototyp auf angenommenen Standardmaßen**, kein fertiger medizinischer oder sportlicher Schuh. Vor längerer Nutzung müssen Maße, Material, Haftung, Nassgriff, Abrieb und Ermüdung praktisch geprüft werden.

## Standardmodell dieser Revision

| Größe | Annahme je Fuß |
|---|---:|
| Fußlänge | 265 mm |
| Ballenbreite | 103 mm |
| Fersenbreite | 67 mm |
| Ferse–Ballen | 182 mm |
| Ballenumfang | 255 mm |
| Ristumfang | 252 mm |
| Risthöhe | 61 mm |
| Zehenhöhe | 27 mm |
| Innenlängen-Zugabe | 12 mm gesamt |
| resultierende Sohlenlänge | 277 mm |
| maximale parametrische Sohlenbreite | ca. 112 mm, ca. 118 mm inklusive seitlicher Wölbung |
| geschätzte Masse nur Sohle, vollmassiv bei 1,20 g/cm³ | ca. 151 g |
| geschätzte Masse Voll-TPU-Variante, vollmassiv | ca. 190 g je Schuh |

Diese Werte ähneln grob einer langen EU-42/kurzen EU-43-Passform, sind aber **keine Größentabellen-Zuordnung**. Fußlänge und Umfang allein reichen nicht für eine sichere Passform.

## Welche Dateien wichtig sind

- `config.json` – alle Fuß-, Passform-, Sohlen-, Netz- und Fertigungsparameter.
- `barefoot_shoe_generator.py` – editierbarer Master; erzeugt alle Ausgaben neu.
- `generated/left|right/textile_variant/*outsole*.stl` – druckbare Sohle für geklebtes Textil.
- `generated/left|right/textile_variant/*cut_pattern_1to1.svg` – maßstäbliches Schnittmuster.
- `generated/left|right/textile_variant/*insole_template_1to1.svg` – Einlagen-/Spacer-Schablone.
- `generated/left|right/printed_mesh_variant/*full_printed_barefoot_shoe.3mf` – vollständige positionierte Baugruppe.
- `generated/left|right/printed_mesh_variant/*lattice_upper.stl` – Netzoberschuh separat.
- `generated/test_coupons/*` – zuerst drucken: Netz- und Ösenprobe.
- `generated/validation_report.json` – Maße und digitale Mesh-Prüfungen.
- `VALIDATION_AND_TEST_PLAN.md` – sichere Reihenfolge vom Papierfit bis zum Gehversuch.

## Geometrische Entscheidungen

### Sohle

- **Nullsprengung:** Ferse und Ballen liegen auf derselben Grundhöhe. Nur die vordersten 13 % erhalten eine lokale Zehenaufbiegung von maximal 1,2 mm.
- **Breite, asymmetrische Zehenbox:** Die Großzehenseite ist gerader; der Vorfuß wird nicht zu einer symmetrischen Spitze zusammengezogen.
- **Dünne, berechenbare Basis:** 4,6 mm nominal. Der lokale Restquerschnitt unter den tiefsten Flexrillen bleibt im CAD mindestens 2,8 mm.
- **Führung ohne starre Gewölbestütze:** Der Fußboden bleibt weitgehend flach. Eine weiche, 5 mm hohe Seitenlippe und höhere Zehen-/Fersenkappen halten den Fuß, ohne einen harten medialen Keil zu erzwingen.
- **Lüftung ohne Wassereintritt:** 0,55 mm tiefe, blinde S-Kanäle und Querrillen bilden unter einer luftdurchlässigen Einlage einen kleinen Luftverteiler. Es gibt keine Durchgangslöcher durch die Laufsohle.
- **Referenznahe Optik:** wechselnde diagonale Zonen, Rautenkreuzung im Mittelfuß, gebogene Flexlinien und eine leicht gewellte/segmentierte Seitenwand. Das ist echte parametrische Geometrie, kein schweres Bild-Heightmap-Mesh.

### Gedruckter Netzoberschuh

- 1,4 mm dicke, echte gelochte Schale statt vieler sich überschneidender Stäbe.
- 3,2 mm nominelle Bänder bei 17 mm Gitterteilung.
- Durchgehender unterer Anbindungsstreifen, Zehenschutz, Fersengegenhalt und zwei Längs-Lastpfade.
- Vier Ösenpaare für 3–4 mm elastische Schnur mit Kordelstopper.
- Offene Zunge/Kehlzone und großer Kragenausschnitt ermöglichen Anpassung an unterschiedliche Ristvolumen.

Der 3MF enthält mehrere **einzeln geschlossene, absichtlich überlappende** Körper an exakter Position: Sohle, Netzschale und Ösen. Im Slicer als eine Baugruppe importieren, Positionen beibehalten und die Option zum Vereinigen/Überlappungen zusammenführen aktivieren. Die Einzelteile nicht automatisch neu anordnen.

## Empfohlener Verschluss

Die beste einfache Lösung für beide Varianten ist eine **elastische Speed-Lace-Schnürung**:

- 3–4 mm elastische Rundschnur;
- Zickzack durch vier Ösenpaare;
- ein Kordelstopper oben;
- optional ein zweiter kurzer Stopper unten, wenn Vorfuß und Rist unabhängig eingestellt werden sollen.

Damit lässt sich Volumen fein einstellen, während die Zehenbox frei bleibt. Eine starre BOA-ähnliche Mechanik wäre schwerer und konzentriert die Last stärker auf wenige gedruckte Punkte.

## Welche Maße ich von dir brauche

Beide Füße abends, im Stehen und mit der vorgesehenen Socke getrennt messen. Millimeterwerte genügen.

| Parameter in `config.json` | Messmethode | Warum er wichtig ist |
|---|---|---|
| `foot_length_mm` | längster Zeh bis hinterster Fersenpunkt | Innenlänge |
| `ball_width_mm` | größte belastete Vorfußbreite | Zehenbox/Sohlenbreite |
| `heel_width_mm` | größte belastete Fersenbreite | Fersenhalt |
| `heel_to_ball_mm` | Ferse bis Mittelpunkt Großzehengrundgelenk | Lage der Flexrille |
| `ball_girth_mm` | Maßband um beide Ballengelenke | Volumen des Vorderfußes |
| `instep_girth_mm` | Maßband über höchsten Rist und unter dem Fuß | Kehlöffnung/Schnürweg |
| `instep_height_mm` | Boden bis höchster Rist, senkrecht | Höhe des Oberteils |
| `toe_height_mm` | Boden bis Oberseite des höchsten Zehs | Zehenfreiheit |
| `ankle_opening_girth_mm` | Umfang durch Fersenpunkt und Rist | Kragenöffnung |
| `toe_splay_mm` | zusätzliche Breite bei maximal gespreizten Zehen | dynamische Zehenfreiheit |
| `big_toe_bias_mm` | seitliche Abweichung Großzehlinie | Asymmetrie der Zehenbox |

Zusätzlich ideal:

- Foto oder Scan des belasteten Fußumrisses von oben, mit Lineal im gleichen Bild;
- Foto von medial, lateral und vorne auf Millimeterpapier;
- Körpergewicht und Hauptnutzung;
- gewünschte Socke und Einlagenstärke;
- Druckermodell, Bauraum, Extruderart, Düse und exaktes TPU.

Die mitgelieferte `*_measurement_guide.svg` zeigt die wichtigsten Längen. Die Einlagen-Schablone zuerst bei 100 % drucken und im Stand prüfen. Rundum sollen etwa 3–4 mm Bewegungsspiel bleiben; vor dem längsten Zeh sind hier 9 mm vorgesehen.

## Regenerieren

Im Projektordner:

```bash
python3 barefoot_shoe_generator.py --config config.json --output generated
```

Erforderlich sind Python 3 und NumPy. Die Ausgabe wird in Millimetern erzeugt. Nach jeder Parameteränderung `generated/validation_report.json` prüfen.

## Druckempfehlung: Textilvariante / einzelne Sohle

| Einstellung | Startwert 0,4-mm-Düse | Alternative 0,6-mm-Düse |
|---|---:|---:|
| TPU | 90A–95A, abriebfeste Sorte | gleich |
| Schichthöhe | 0,20–0,24 mm | 0,25–0,30 mm |
| Linienbreite | ca. 0,46 mm | ca. 0,65–0,70 mm |
| Wände | 4–5 | 4 |
| Top/Bottom | je 6–8 Schichten | je 5–6 Schichten |
| Infill | zunächst 100 % für reproduzierbare Biegung | zunächst 100 % |
| Außenwandgeschwindigkeit | 18–25 mm/s | 15–22 mm/s, flussabhängig |
| Support | aus | aus |
| Ausrichtung | Laufsohle auf das Bett | Laufsohle auf das Bett |

Die Sohle ist dünn; viele Wand- und Deckschichten verbrauchen bereits fast den gesamten Querschnitt. Wenn sie zu steif ist, zuerst `footbed_thickness_mm` in kleinen Schritten und nur nach einem Flex-/Abriebtest ändern. Niedrigeres Infill allein erzeugt in einer so dünnen Platte oft keine gleichmäßige, kontrollierte Weichheit.

Auf einem quadratischen 250-mm-Bett passt das Standardmodell nach der CAD-Hüllkurvenprüfung bei ungefähr **47° Z-Rotation** in etwa 228 × 228 mm; ein moderater Brim bleibt damit möglich. Auf 220 × 220 mm passt es ungeteilt nicht. Der Slicer muss die tatsächliche Hüllkurve einschließlich Brim, Purge-Strukturen und Maschinen-Sperrflächen erneut prüfen.

Temperatur, Bett, Lüfter, Rückzug und maximale Flussrate müssen aus dem Datenblatt und einer Kalibrierung des konkreten TPU kommen. Flexibles Filament vor dem Druck nach Herstellerangabe trocknen. Ein Direktextruder ist für weiches TPU deutlich einfacher.

## Druckempfehlung: kompletter TPU-Netzschuh

- 0,4-mm-Düse, 0,20 mm Schichthöhe, 0,46 mm Linienbreite;
- Arachne/variable Linienbreite aktivieren, dünne Wände nicht ignorieren;
- Netz, Ösen und Sohle als Baugruppe zusammenführen;
- Laufsohle nach unten, breite Kontaktfläche, 6–10 mm Brim nur falls erforderlich;
- langsame Außenwände 15–22 mm/s, geringe Beschleunigung, kalibrierter TPU-Flow;
- Brückenlüfter nach Coupon einstellen;
- zunächst organischen Support nur von der Bauplatte testen. TPU-Support kann stark verschweißen; wenn die selbsttragende Netzgeometrie auf deinem Drucker nicht sauber gelingt, ist die Textilvariante oder ein separat flach gedrucktes/thermisch geformtes Oberteil die robustere Route.

Der vollständige Netzschuh ist bewusst als **experimenteller In-place-Druck** gekennzeichnet. Erst `generated/test_coupons/tpu_lattice_and_eyelet_coupon.3mf`, dann gegebenenfalls einen abgeschnittenen Oberteilbereich und erst danach den ganzen Schuh drucken.

## Textilaufbau und Kleben

Empfohlener leichter Aufbau:

1. 1,5–2,5 mm atmungsaktives 3D-Spacer-Mesh oder abriebfestes Sport-Mesh;
2. dünne, nicht dehnbare Verstärkung nur an Ösen, Ferse und seitlichen Lastpfaden;
3. weiches elastisches Einfassband am Kragen;
4. optional sehr dünnes glattes Futter gegen Reibung.

Schnittmuster bei **100 % ohne Seitenanpassung** drucken und das 50-mm-Kontrollquadrat messen. Erst aus billigem Probestoff nähen. Medial- und Lateralteil an Zehenmittelnaht und Ferse verbinden, Zunge einsetzen, dann den 12-mm-Unterrand auf einem Fußleisten spannen und in den umlaufenden Klebesitz legen.

Für TPU zu Textil einen **flexiblen PU-Schuhklebstoff oder kompatiblen TPU-Hotmeltfilm** verwenden, nicht irgendeinen spröden Sekundenkleber. Oberfläche und Aktivierung ausschließlich nach technischem Datenblatt des konkreten Klebstoffs vorbereiten; vorher einen Schälcoupon aus genau deinem Filament und Stoff herstellen. Covestro beschreibt TPU und flexible PU-Klebstoffsysteme ausdrücklich für Obermaterial und Sohlen im Schuhbau: <https://solutions.covestro.com/en/highlights/articles/theme/applications/shoes-and-footwear>.

## Einlage und Fußsohlenlüftung

Empfohlener Startaufbau, insgesamt 2–3 mm:

- oben 1–1,5 mm 3D-Spacer-Textil oder feuchtigkeitsleitendes Mesh;
- darunter 1–1,5 mm perforiertes EVA oder ein sehr dünner, gelochter Komfortschaum;
- keine ausgeprägte starre Gewölbestütze, sofern sie nicht fachlich verordnet ist.

Das Spacer-Mesh hält die Haut von den TPU-Kanälen fern, verteilt Feuchte und erlaubt etwas Luftbewegung beim Abrollen. Ein geschlossener dicker Schaum ohne Perforation würde die Kanäle weitgehend blockieren. Die Einlage bleibt herausnehmbar und kann über `*_insole_template_1to1.svg` zugeschnitten werden.

## Technische Grenzen und Gesundheit

Minimal-/Barfußschuhe verändern Bewegungsmuster und Lasten; „minimal“ ist nicht automatisch verletzungssicher. Die Literatur berichtet je nach Population und Übergang sowohl biomechanische Veränderungen als auch mögliche Beschwerden/Verletzungen. Deshalb langsam eingewöhnen und bei Schmerzen, Diabetes, Neuropathie, ausgeprägter Fehlstellung oder verordneter Orthese fachlich abklären. Quellen: [Systematic Review zu Schuhkonstruktionen](https://pmc.ncbi.nlm.nih.gov/articles/PMC7039038/) und [Review zum Übergang auf Minimalschuhe](https://pmc.ncbi.nlm.nih.gov/articles/PMC5602809/).

Gedruckte TPU-Strukturen erlauben zonierbare Eigenschaften, aber Zellform, Dichte und Druckrichtung ändern die Mechanik stark; ein CAD-Muster ersetzt keine Materialprüfung. Eine experimentelle Studie zu 3D-gedruckten Außensohlen zeigt genau diese Formabhängigkeit: <https://pmc.ncbi.nlm.nih.gov/articles/PMC9371032/>.

Nicht als Arbeitsschutz-, Kletter-, Motorrad-, medizinischen oder Wettkampfschuh verwenden, bevor die dafür einschlägigen Prüfungen tatsächlich bestanden sind.
