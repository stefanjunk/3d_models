# Top 20 Produkttypen für kommerzielle FDM-Massanfertigung
### Desk-Research-Bericht: Hochindividuelle, parametrische 3D-Druckprodukte ohne Serienwerkzeug

| | |
|---|---|
| **Datum** | 2026-08-17 |
| **Status** | Konzept / Entscheidungsgrundlage (noch keine validierten Marktdaten) |
| **Methode** | Desk Research auf Domänenwissen (FDM-Prozess, Nischenmärkte, E-Commerce-Kanäle). Keine Live-Marktdaten, keine Umsatzverifikation — als Arbeitshypothesen behandeln. |
| **Ziel** | 20 Produkttypen identifizieren, die (a) höchst individuell sind, (b) FDM gegenüber Spritzguss/Serienprodukten wirtschaftlich bevorzugt, (c) vollständig parametrisch ohne Handarbeit generierbar, (d) regulatorisch unproblematisch, (e) in gängige Drucker-Bauräume passen. Zu jedem Typ: ein konkretes Produkt + kopierfertiger AI-Design-Prompt. |

---

## 1. Executive Summary

Der wirtschaftliche Vorteil von FDM gegenüber Serienfertigung entsteht genau dort, wo eine oder mehrere der folgenden Bedingungen gelten:

1. **Long-Tail-Geometrie:** Das Produkt muss zu einem von hunderten Fremdmodellen passen (Fahrzeug, Gerät, Spiel, Maschine). Spritzguss lohnt sich erst ab ~1.000–5.000 identischen Teilen pro Variante — bei 500 Fahrzeugmodellen × 10 Baujahre ist das pro Variante nie erreichbar. FDM braucht keine Form.
2. **Körperindividualität:** Das Produkt passt zu einem individuellen Maß (Handscan, Kopfmaß, Pedalliste, Werkzeugliste). Serienprodukte bedienen Durchschnittsmaße; Individualisierung erzeugt Aufpreis-Bereitschaft von 50–300 %.
3. **Digitale Variantendatenbank statt Lager:** Die Varianten entstehen aus einer Datenbank (Maße bekannter Modelle) + Konfigurator. Lagerhaltung entfällt, jede Bestellung ist ein frischer Druck.

Die **Top 5** des Rankings (Details in Kap. 7):

| Rang | Produkttyp | Gew. Score |
|---|---|---|
| 1 | Fahrzeugspezifische Cockpit-Ablagen (z. B. VW T6.1) | 4.65 |
| 2 | Pedalboards aus Pedal-Listen | 4.60 |
| 3–6 | Tablet-Wandhalterungen, Geräte-Case-Inserts, Brettspiel-Organizer, Camper-Ausbau-Module | je 4.45 |

Alle 20 Produkte sind so gewählt, dass sie **ohne** Lebensmittelkontakt, ohne Kinderspielzeug-Regulatorik (EN 71), ohne Medizinprodukte- (MDR), ohne PSA- und ohne tragende Sicherheitsfunktion auskommen. Verbleibende Restpflichten (GPSR-Produktsicherheit, CE bei Elektronik-Berührung) sind je Produkt vermerkt.

---

## 2. Auswahlkriterien und Scoring-Modell

Jeder Kandidat wurde auf 6 Kriterien mit 1–5 Punkten bewertet:

| Kriterium | Gewicht | Bedeutung |
|---|---|---|
| **Individualisierungsvorteil** | 20 % | Wie stark schlägt „passt exakt zu mir/meinem Gerät" ein Serienprodukt? |
| **Parametrisierbarkeit** | 20 % | Lässt sich jede Variante aus Eingaben (Datenbank, Liste, Scan) ohne Handarbeit erzeugen? |
| **Marktgröße/Nachfrage** | 20 % | Existiert eine zahlungsbereite Nische mit Suchvolumen/Kaufverhalten? |
| **FDM-Prozessfit** | 15 % | Bauraum (≤ 450 mm Kante), Geometrie, Material, Druckzeit wirtschaftlich? |
| **Marge** | 15 % | Verkaufspreis vs. Material- + Druckzeitkosten (Ziel: ≥ 60 % Rohmarge)? |
| **Regulatorische Unbedenklichkeit** | 10 % | Abstand zu MDR, EN 71, Lebensmittelkontakt, PSA, tragender Sicherheit |

**Ausschlusskriterien (hart):** Lebensmittelkontaktflächen, Kinderspielzeug (< 14 J.), medizinische/therapeutische Claims, PSA/Schutzhelme mit Schutzwirkung, tragende Sicherheitsbauteile (Personensicherung), Produkte > 500 mm die sich nicht segmentieren lassen, Produkte mit zwingender Zertifizierung vor Verkauf.

---

## 3. Marktlogik: Wann schlägt FDM das Serienprodukt?

**Kostenmodell Spritzguss vs. FDM (vereinfacht, DACH 2026):**

| | Spritzguss | FDM |
|---|---|---|
| Werkzeugkosten | 8.000–40.000 € (einfache Form, 1 Kavität) | 0 € |
| Stückkosten | 0,30–2 € (ab 5.000 Stk.) | 3–15 € (Material 0,25–0,60 €/g + Druckzeit + Nacharbeit) |
| Break-even | ~2.000–10.000 identische Teile | ab Stück 1 |
| Variantenkosten | +8.000 € je Variante (neue Form) | ~0 € (nur neue Parameter) |

**Daraus folgen die drei tragfähigen Geschäftsmodelle dieses Berichts:**

- **Modell-Datenbank-Produkte:** Ein Produkt, N Fremdmodelle (Fahrzeug, Kamera, Headset, Spiel, Staubsauger). Der Kunde zahlt für „passt garantiert zu meinem X". Bekannte Maße aus Datenblättern/Community-Wikis → parametrische Tabelle.
- **Listen-Produkte:** Der Kunde liefert eine Liste (Pedale, Werkzeuge, Geräte, Gewürze…) und erhält eine exakt darauf ausgelegte Halterung/Organizer. Die Liste ist der Parametervektor.
- **Scan-Produkte:** Körpermaße (Hand, Kopf, Fußsohle) per Smartphone-Scan oder Maßband-Eingabe. Höchste Zahlungsbereitschaft, aber Scan-Pipeline nötig — deshalb mischt dieser Bericht bewusst Datenbank-Typen (sofort startbar) mit Scan-Typen (Phase 2).

**Preisanker:** Alle 20 Produkte liegen im Zielkorridor **18–300 €** Verkaufspreis bei 3–15 € Materialkosten — das ist der Bereich, in dem Etsy-eigene-Shop-Verkäufe mit 2–8 Stunden Druckzeit gesund rechnen.

---

## 4. Rahmenannahmen

- **Drucker:** Prosumer-/Kleinstserien-FDM (Bambu-Lab-Klasse, Prusa XL, Voron, BigTreeTech), Bauraum bis ~450 × 450 × 450 mm. Alle Produkte passen in 256³ mm oder sind sauber segmentierbar.
- **Materialien:** PLA (dekorativ/indoor), PETG (mechanisch), ASA (Fahrzeug/UV/hitzebeständig), TPU 95A (Kontaktflächen, Dämpfung), optional PA-CF. Mehrfach-/Mischkonstruktionen (rigid + flex + Gewindeeinsätze + Magnete) sind explizit Teil des Wertangebots.
- **Nozzle:** 0,4 mm Detail / 0,6 mm Standard — beides Standard, keine Exoten.
- **Kanäle:** Etsy, eigener Shopify-Shop, Fach-Communities (Foren, Discord, Subreddits), B2B-Direktvertrieb bei Werkstatt-/Flottenprodukten.
- **Recht:** Es gelten GPSR (allgemeine Produktsicherheit) und die üblichen Fernabsatzpflichten. Keines der Produkte ist zulassungspflichtig. Markenrecht: Produktnamen von Fremdherstellern nur als Kompatibilitätsangabe („passend für …") verwenden, nie als eigener Produktname.
- **Haftung:** Bei allen Halterungen mit Sachwert (Kamera, Tablet, Gerät) werden im Bericht Sicherungskonzepte (Fangband-Öse, zweiter Anschlagpunkt) mitgedacht.

---

## 5. Konzeptbilder

**Status: BLOCKED.** Die Bildgenerierung (AI-Konzeptrenders) war in dieser Sitzung nicht möglich — der Authentifizierungs-Token des Bildgenerierungsdienstes ist abgelaufen (`401 token_expired`). Die fertigen Bildprompts für die Top-6-Produkte liegen daher gebrauchsfertig in `konzeptbilder/bildprompts.md` und können nach erneutem Login unverändert erzeugt werden.

---

# 6. Produktkatalog Top 20 (in Ranking-Reihenfolge)

Jeder Eintrag: konkreter Produktvorschlag + kopierfertiger Prompt für eine CAD-AI (CadQuery/OpenSCAD). Alle Prompts erwarten als Übergabe eine `parameters.json` — die Werte kommen aus der jeweiligen Datenbank/Kundenliste.

---

## Nr. 1 — Fahrzeugspezifische Cockpit-Ablagen (VW T6.1)

**Typ:** Long-Tail-Modell-Datenbankprodukt · **Score:** 4.65 · **Preis:** 35–65 €/Set · **Kanal:** Etsy, Bus-/Camping-Foren, Bulli-Communities

**Konkretes Produkt:** Ein 2–3-teiliges Ablagen-Set (Mittelkonsole + Armaturenbrett-Mulde + Becherhalter-Einsatz) für VW T6.1 (2019–2024), das exakt in die OEM-Konturen der Mittelkonsole clipst. Material ASA (Hitze im Fahrzeug bis ~80 °C, UV), eingelegte TPU-Antirutsch-Böden (herausnehmbar, zweiteilig gedruckt). Kein Kleben, nur Form-/Clipschluss — rückstandslos entfernbar.

**Warum FDM statt Serie:** OEM-Zubehör und Zubehörhersteller decken nur Bestseller-Fahrzeuge ab; je Baujahr/Ausstattung (mit/ohne 2-DIN-Navy, mit/ohne Ablagefach-Abdeckung) entstehen Varianten, die sich für Spritzguss nie rechnen. ASA-CNC-Fertigung wäre 3–4× teurer.

**Parametrische Eingaben:** Fahrzeugmodell + Baujahr + Ausstattungscodes (Liste aus Konfigurator), je Ablage: Außenkontur (aus 3D-Scan oder vermessener OEM-Schale), Fachtiefe, Anzahl Becher/Zigarettenanzünder-Ausschnitte.

**Material & Druck:** ASA 0,6 mm Düse, 0,2 mm Schicht, 100 % Füllung an Clips, TPU 95A für Einlagen. Druckzeit ~6–10 h/Set. Segmentierbar bei > 256 mm.

**Regulatorik/Haftung:** Kein Airbag-/Sichtfeldbereich (Einbau nur unterhalb Sichtfeld, Montagehinweis Pflicht). Keine Zulassung nötig; GPSR: Warnhinweis „nicht im Airbag-Entfaltungsbereich montieren".

**AI-Design-Prompt:**

```
Entwirf ein parametrisches 3D-Modell (CadQuery) für ein zweiteiliges Fahrzeug-Ablagen-Set.
Eingaben (parameters.json): vehicle_model="VW T6.1", model_year=2021, console_pocket_outline (geschlossener 2D-Spline, mm), tray_depth=18, cup_cutout_d=68, cup_count=1, clip_positions=[(x,y,winkel)...], wall=2.5, material="ASA".
Geometrie: Unterschale mit 3 umlaufenden Rastnasen (Hinterschnitt 0,6 mm, 3° Einlaufschräge, Auslösefenster je Nase) passend zur Taschenkontur; obere Ablage mit Münz-/Kartenfach und Bechermulde; separate TPU-Antirusch-Einlage (2,0 mm) mit 4 Druckknopf-Pins, die in Senkungen der ABS-Schale schnappen. Alle Außenkanten R3 verrundet.
Randbedingungen: Bauraum 256×256×256 mm, sonst in ≤ 2 druckbare Segmente mit 3-Punkt-Präzisions-Passung teilen. Wandstärke ≥ 2,2 mm, keine Stützstrukturen auf Class-A-Sichtflächen (Ausrichtung flach auf Konsole). Schrumpfzuschlag ASA 0,7 %.
Ausgabe: STEP (Master), STL je Druckteil, parameters.json, Montagezeichnung als SVG.
Verifikation: Rastnasen-Abzugskraft-Abschätzung dokumentieren; Sichtprüfung auf Spaltmaße ≤ 0,8 mm an der Fahrzeugkontur.
```

---

## Nr. 2 — Pedalboard aus Pedal-Liste (Gitarre/Bass)

**Typ:** Listen-Produkt · **Score:** 4.60 · **Preis:** 90–220 € · **Kanal:** Etsy, Gitarren-Foren, Reverb.com-Umfeld

**Konkretes Produkt:** Ein individuelles Pedalboard (Boardfläche + 12°-Schrägaufsteller) exakt für die Pedal-Liste des Kunden: jede Pedalposition aus einer Pedal-Datenbank (Bodenplattengröße, Knopfposition), mit gefrästen/drucktechnischen Aussparungen zur Pedalbefestigung (Kabelbinder-Schlitze statt Klett), integriertem Kabelkanal auf der Unterseite und Ausschnitt für ein Standard-Netzteil (z. B. 9-V-Daisy-Chain-Position). Boardgröße ergibt sich automatisch aus Anordnung (Auto-Layout oder kundenseitiges Wunsch-Layout).

**Warum FDM statt Serie:** Boards von der Stange (z. B. Alu-Rahmen) sind entweder zu groß oder zu klein und bieten keine pedalexakte Befestigung. Ein Board „für genau meine 5 Pedale in meiner Reihenfolge" gibt es serienmäßig nicht — und Alu-CNC wäre ab 150 €+ ohne Individualisierung.

**Parametrische Eingaben:** Pedal-Liste (Name → Datenbank: L×B×H, Position Stromanschluss), Boardwinkel, Netzteil-Typ, ob Griff integriert, max. Board-Fläche.

**Material & Druck:** PETG, 0,6 mm, 3 Wandlinien, Gitter-Infill 25 %. Boards bis 400 mm einteilig druckbar; darüber 2 Segmente mit formschlüssiger Schwalbenschwanz-Verbindung + 2 Schrauben.

**Regulatorik/Haftung:** Unkritisch (kein Strom im Produkt selbst). Markenkompatibilitätsangabe beachten.

**AI-Design-Prompt:**

```
Entwirf ein parametrisches Pedalboard (OpenSCAD mit BOSL2 oder CadQuery).
Eingaben: pedals=[{name:"Boss SD-1", l:73, b:129, h:59, power_pos:"hinten"}...], tilt_deg=12, psu={"type":"9V-DaisyChain","l":120,"b":60}, grip=true, max_area=400×200.
Geometrie: Brettfläche aus Auto-Layout (Pedale mit 8 mm Randabstand, Reihen kompakt packen), je Pedal 2 Kabelbinder-Schlitze (4×1,5 mm) versetzt zur Bodenplatte, umlaufende Lippe 3 mm gegen Verrutschen; Rückseite: Kabelkanal 12×10 mm über die volle Breite + Netzteil-Bucht mit 2 Haltenasen; Füße als aufsteckbare TPU-Kappen (Rutschschutz). Aufsteller fest integriert, Winkel = tilt_deg. Bei Fläche > 256 mm: Schwalbenschwanz-Teilung mittig + 2× M4-Verbindung (Gewindeeinsatz).
Randbedingungen: PETG, 0,6 mm Düse, Bauraum 256³/400³, keine Stützen auf Pedal-Auflageflächen; Verzugskompensation über Gitter-Infill.
Ausgabe: STEP, STL je Segment, parameters.json, Render von oben/schräg.
Verifikation: Pedalgrundflächen müssen spielfrei zwischen den Lippen klemmen (0,3 mm Toleranz je Seite), Gesamtgewicht inkl. Pedale < 1,5 kg bei max. Fläche.
```

---

## Nr. 3 — Gerätespezifische Wandhalterung / Kommandozentrale (Smart-Home-Tablet)

**Typ:** Modell-Datenbankprodukt · **Score:** 4.45 · **Preis:** 25–45 € · **Kanal:** Etsy, Home-Assistant-Community, Smart-Home-Foren

**Konkretes Produkt:** Wandhalterung für ein konkretes Tablet-Modell (z. B. als Home-Assistant-Bedienpanel) mit Snap-in-Rahmen exakt um das Gerät, verdeckter Kabelführung (Ladekabel läuft im Sockel zur Wand), 10° Neigung und einer Blende, die das Ladekabel unsichtbar macht. Optional: Hohlwanddose-Aufnahme (EU-Standard 60 mm), sodass ein Unterputz-Netzteil direkt hinter dem Tablet sitzt.

**Warum FDM statt Serie:** Serienhalterungen sind generisch (Klemmmechanik, sichtbar klobig). „Exakt für mein Tablet-Modell, bündig wie ein eigenes Display, Kabel unsichtbar" ist nur gerätemodellspezifisch machbar — und es gibt > 300 relevante Tablet-Modelle.

**Parametrische Eingaben:** Tablet-Modell (Maß-DB: L, B, T, Kameraposition, Ladeport-Position, Tastenpositionen), Neigungswinkel, Montageart (Schraublochbild / Hohlwanddose / Klebeplatte), Kabelführung oben/unten.

**Material & Druck:** PETG, dünnwandig aber steif (2,4 mm Wand), Snap-Fit-Nasen TPU-überzogen gegen Verkratzen. Druckzeit ~4–6 h.

**Regulatorik/Haftung:** Tragfähigkeit ehrlich kommunizieren (bis ~800 g mit 2 Schrauben); bei Nutzung eines eigenen Netzteils wird das Gerät des Kunden verwendet → keine eigene CE-Pflicht für das Netzteil, aber Montagehinweis für Elektroanschluss durch Fachkraft.

**AI-Design-Prompt:**

```
Entwirf eine parametrische Geräte-Wandhalterung (CadQuery).
Eingaben: device={"model":"Lenovo Tab M10 G3","L":241,"B":160,"T":8.5,"port_x":121,"port_side":"unten","buttons":"rechts"}, tilt_deg=10, mount="hohlwanddose_60mm", cable_exit="unten".
Geometrie: Rückplatte mit 60-mm-Dosenaufnahme (2 Schraubdomen M3,5 in Dosen-Abstand 60 mm); Frontrahmen als umlaufender Snap-Fit: 4 Rastnasen (Ausladung 1,2 mm, TPU-Pads 0,5 mm als Kratzschutz) + Anlageflächen nur an den Gehäuserändern des Geräts (Aussparungen für Kamera/Buttons/Tastenfreigängigkeit); Ladekanal von der Geräteunterseite durch den Sockel zur Dosenöffnung, Kabelradius ≥ 5 mm; Gehäuse bündig: Spalt Gerät/Rahmen ≤ 0,4 mm.
Randbedingungen: PETG, Bauraum 256³, Wand ≥ 2,4 mm, druckbar ohne Stützen durch Neigungsaufbau Schicht für Schicht (selbsttragend ≤ 45°); Schrumpf 0,5 %.
Ausgabe: STEP, STL, parameters.json, Explosionsdarstellung PNG.
Verifikation: Haltekraft-Abschätzung (Gerätsgewicht × 2 Sicherheitsfaktor auf Rastnasen), Kollisionsprüfung Gerät↔Rahmen mit 0,4 mm Spiel, Wandabstand ≤ 18 mm.
```

---

## Nr. 4 — Einsatz für Gerätekoffer nach Ausstattungs-Liste (Case-Insert)

**Typ:** Listen-Produkt · **Score:** 4.45 · **Preis:** 45–90 € · **Kanal:** Etsy, Foto-/Drohnen-/Messtechnik-Communities, B2B (Servicetechniker)

**Konkretes Produkt:** Passgenauer Koffereinsatz (statt Schaumstoff-Pick-and-Pluck) für einen definierten Koffer (z. B. „Peli-Größe 1450" oder Kundenangabe Innenmaß) und eine definierte Ausrüstungsliste (z. B. DJI Mini 4 Pro + 3 Akkus + Fernsteuerung + Netzteil + Ersatzpropeller). Jedes Fach als Negativform mit Griffmulde zum Entnehmen, TPU-Bodenstreifen gegen Klappern, Deckel-Noppenelement flach.

**Warum FDM statt Serie:** Kofferschaumstoff ist Einweg-Fummelei ohne Haltbarkeit; gefräste Inserts (CNC) kosten 100 €+ und ändern sich nur über neue Programme. Der Druckansatz erlaubt die gleiche Flexibilität wie Schaum bei besserer Präzision und Reparierbarkeit (einzelnes Fach neu drucken). Besonders stark als B2B-Abo: „Einsatz für genau euren Gerätesatz".

**Parametrische Eingaben:** Koffer-Innenmaß (L×B×T), Geräteliste (jedes Teil: L×B×H + Orientierung + ob Akku/Ladegerät), Griffmulden ja/nein, Wand zwischen Fächern, Höhe der Nutzung (Deckel-Hohlraum).

**Material & Druck:** PETG oder PLA+ (je nach Einsatztemperatur), 0,6 mm, Vase-Modus ungeeignet → 3 Wände + 15 % Infill für Steifigkeit bei wenig Gewicht. Große Koffer: 2–4 Fliesensegmente mit Passstiften.

**Regulatorik/Haftung:** Unkritisch. Transportschäden am Gerät: Haftungsausschluss + Empfehlung, schwere Geräte zusätzlich zu sichern.

**AI-Design-Prompt:**

```
Entwirf einen parametrischen Koffereinsatz (CadQuery).
Eingaben: case={"L":350,"B":260,"T":150,"deckel_freiraum":35}, items=[{name:"Drohne","L":245,"B":190,"H":70,"orient":"unten"},{"name":"Akku","d":44,"h":97,"count":3}...], wall_between=8, finger_scoop=true, liner="TPU-Streifen".
Geometrie: Grundplatte 4–8 mm, je Item eine Tasche mit 1 mm Spielpassung (Bemaßung aus Item-Maßen +1), je Tasche eine halbrunde Griffmulde R20 an der Entnahmeseite, TPU-Bodenstreifen 1,5 mm als eigene druckbare Einleger; Zwischenstege formschlüssig mit der Grundplatte verbunden (nicht geklebt: Zapfen 6×3 mm alle 60 mm). Einsatz randbündig minus 0,5 mm auf Koffer-Innenmaß, mit 2 Fingerausnehmungen zum Herausheben.
Randbedingungen: Bauraum 256³ → sonst Segmentierung längs mit 4-Passstift-Verbindung (Ø6 h6/Passung). Mindestwand 3 mm, keine scharfen Innenecken (R2 min., gegen Rissbildung).
Ausgabe: STEP, STL je Segment, TPU-Einleger separat, parameters.json.
Verifikation: Volumenprüfung (Summe Taschen + Stege ≤ Koffervolumen − Deckelfreiraum), Entnahmesimulation: jedes Fach ohne Kollision mit Nachbarfach entnehmbar.
```

---

## Nr. 5 — Brettspiel-Organizer je Spieltitel

**Typ:** Modell-Datenbankprodukt (Spiel = „Modell") · **Score:** 4.45 · **Preis:** 35–70 € · **Kanal:** Etsy, BoardGameGeek-Communities, Vielspieler-Foren

**Konkretes Produkt:** Vollständiges Innenleben für die Original-Spieleschachtel eines konkreten Titels (Premiere: komplexe Kennerspiele mit 200+ Komponenten): Kartenschächte für alle Kartenstapel (auch gesleeved) mit Entnahmefinger-Schlitzen, Fächer für Marker/Ressourcen, Münzen-Schale mit Kippfunktion, herausnehmbare Spielertableaus und ein Deckel-Inlay gegen Verrutschen. Alles in der Originalbox verstaubar, Box schließt weiterhin.

**Warum FDM statt Serie:** Es gibt > 150.000 Brettspieltitel; Holz-Inserts existieren nur für Bestseller und kosten 50–120 €. Gedruckte Organizer je Titel sind das klassische Long-Tail-Geschäft: Die Datenbank (Kartengrößen, Komponenten aus BGG-Daten) erzeugt die Varianten automatisch.

**Parametrische Eingaben:** Spieltitel → DB: Schachtel-Innenmaß, Kartenanzahl/-format/-sleeve-Stärke, Komponentenliste mit Abmessungen, ob Spielplan-Fach nötig, Spielerzahl.

**Material & Druck:** PLA (Leichtbau, indoor), 0,6 mm, 2 Wände, 10–15 % Infill; Druckzeit je Set 8–14 h → über Nacht. Modular als 4–6 Einsätze für Zuverlässigkeit.

**Regulatorik/Haftung:** Unkritisch. Kein Spielzeug-Claim (ab 14 Jahre als Zubehör, nicht zum Spielen durch Kleinkinder — Standard-Disclaimer).

**AI-Design-Prompt:**

```
Entwirf einen parametrischen Brettspiel-Organizer (OpenSCAD mit strukturierten Modulen).
Eingaben: box={"L":295,"B":295,"H":72}, decks=[{name:"Ereignisse","cards":120,"format":"63.5×88","sleeved":true}], tokens=[{name:"Holz","d":12,"h":12,"count":60}...], player_count=4, plan_fold="4-seitig".
Geometrie: Kartenschächte = Innenformat Karten +0,8 mm Spiel, Schachttiefe = Stapelhöhe (Anzahl × 0,35 mm bei gesleeved) + 4 mm, an der Zugangsseite U-förmige Fingerausschnitte R12 je Schacht; Token-Fächer mit 3 mm Rand und einer Kippkante; Spielertablets als flache Einsätze mit Vertiefungen exakt auf Spieler-Material (Farbcodierung durch Filamentwechsel-Option); Deckel-Inlay 3 mm mit flachen Haltezapfen. Gesamt: Box schließt bei 72 mm — Aufbauhöhe der Einsätze ≤ 66 mm, Rest füllen Bodenelemente.
Randbedingungen: PLA, Bauraum 256³ (Einsätze einzeln drucken), keine Überhänge > 45° , Stapelbarkeit der Einsätze mit 2 mm Überstand gegen Verrutschen.
Ausgabe: STL je Einsatz, parameters.json, Druckbett-Layout-CSV, Montagefoto-Render.
Verifikation: Pack-Test-Simulation (Volumen aller Komponenten ≤ Boxvolumen − 8 % Reserve), Deckelschließ-Check bei voller Beladung.
```

---

## Nr. 6 — Fahrzeugindividueller Camper-Ausbau (Seitenpanel/Heck-Organizer)

**Typ:** Modell-Datenbankprodukt (hoher Warenkorb) · **Score:** 4.45 · **Preis:** 90–250 € · **Kanal:** Etsy, Camper-Selbstausbauer-Foren, Vanlife-Communities

**Konkretes Produkt:** Molle-/Schienen-Seitenpanel für einen definierten Transporter (z. B. Mercedes Sprinter W907 oder Ford Transit Custom), das sich an vorhandenen OEM-Zurrpunkten/Schraubenpunkten verschraubt und die Kontur des Seitenfensters exakt nachfährt (kein Blind-Loch an der Fensterscheibe). Integriert: Gurtbandschlitze für Tactix-Style-Molle, Halter für Besen/Feuerlöscher (Klemmen), Taschen-Aufnahmen. Zweiteilig bei > 450 mm, Verbindung über formschlüssige Kulisse + 4 Schrauben.

**Warum FDM statt Serie:** Camper-Ausbau-Zubehör (van equipment) ist ein stark wachsender Markt; fensterspezifische Konturen gibt es nur für Bestseller-Modelle, und Alu-/CNC-Panels kosten ab 180 €. Gedruckte ASA-Panels mit exakter Fensteraussparung und individueller Modul-Bestückung sind direkt konkurrenzfähig.

**Parametrische Eingaben:** Fahrzeugmodell + Baujahr + Radstand/Hochdach-Variante, Fensterausschnitt-Form (Scan oder DB), gewünschte Modulliste (Halter-Typen, Positionen), Befestigungspunkte (OEM-Zurrösen ja/nein).

**Material & Druck:** ASA zwingend (UV + Sommerhitze im Fahrzeug), 0,6 mm, ≥ 3 Wände, 30 % Infill an Lastpfaden; Segmente ≤ 400 mm. TPU-Schutzkanten auf der Fenster zugewandten Seite.

**Regulatorik/Haftung:** Keine Ladungssicherungs-Claims („kein Ersatz für Zurrösen, max. 8 kg Flächenlast"); Montageanleitung mit Drehmomentangaben. GPSR-Konformitätserklärung für eigene Produkte mitliefern.

**AI-Design-Prompt:**

```
Entwirf ein parametrisches Camper-Seitenpanel (CadQuery).
Eingaben: vehicle="Sprinter W907 L3H3, BJ 2020", window_outline=Spline-Kontur, mounting_points=[Ø8 OEM-Zurrösen ×4 mit Abständen], modules=[{"type":"Feuerlöscherhalter","d":110},{"type":"Besenklemme"},{"type":"Molle-Reihen","n":5}], max_load_kg=8, panel_t=4.
Geometrie: Platte 4 mm Kern mit Rippenkreuz (Rippe 2,5 mm, Abstand 30 mm) für Steifigkeit bei 8 kg; Fensteröffnung als versetztes Offset der window_outline +6 mm, umlaufend mit TPU-Kantenschutz (Nut 3×2 mm zum Eindrucken); Befestigung über 4 Schraubdomen (M6 Gewindeeinsätze) auf die OEM-Punkte; Modul-Montagefläche als 25-mm-Lochraster (Loch Ø6,5, alle 25 mm) plus dedizierte Aufnahmen je Modul mit 2-Punkt-Verschraubung.
Randbedingungen: ASA, Segmente ≤ 400×380 mm mit formschlüssiger Kulisse (Schwalbenschwanz 12° + 2 M4 pro Stoß), keine Bauteile in den Fahrzeugsichtbereich des Spiegels; Schrumpfung ASA 0,7 % kompensieren.
Ausgabe: STEP, STL je Segment, Montagezeichnung SVG mit Drehmomenten, parameters.json.
Verifikation: FEM-artige Lastannahme 8 kg an ungünstigstem Modulpunkt (Biegespannung < 30 MPa bei ASA), Klapperprüfung durch TPU-Anlageflächen an allen Fahrzeugkontakten.
```

---

## Nr. 7 — Ergonomisches Split-Keyboard-Gehäuse mit Scan-Passform

**Typ:** Scan-Produkt (Körpermaß) · **Score:** 4.40 · **Preis:** 90–180 € · **Kanal:** Etsy, Ergonomie-/Mech-Keyboard-Communities (r/ergodoxic)

**Konkretes Produkt:** Gehäuse (Case + Zelt-Unterstruktur + Handballenauflage) für ein definiertes Split-Keyboard-Layout (z. B. Corne, Kyria, Sofle), individuell auf Handgröße und Unterarmwinkel des Kunden: Die Handballenauflage wird aus einem Handballen-/Unterarm-Scan erstellt (oder aus 3 Maßzahlen generiert), der Tenting-Winkel aus dem Unterarm-Rotationswinkel abgeleitet, die Keywell-Wölbung (Dish) aus der Fingerlänge.

**Warum FDM statt Serie:** Serien-Split-Keyboards haben feste Tenting-Winkel (meist 10°) und Standard-Zeltkits; ergonomisch sinnvoll ist aber der individuelle Winkel. Kein Serienanbieter kann Scans verwerten — hier liegt die Marge (Keyboard-Enthusiasten geben 200 €+ für Custom-Cases aus Alu aus).

**Parametrische Eingaben:** PCB-Layout (Tastenanordnung + Befestigungslöcher der Platine), Tenting-Winkel, Keywell-Dish-Tiefe, Handballen-Scan-Mesh (STL) oder Maßwerte (Handlänge, Handballenbreite), Tilt.

**Material & Druck:** PETG-Case (steif), TPU-95A-Auflagefläche (Hautkontakt, abnehmbar waschbar), Messing-Gewindeeinsätze für Tenting-Füße.

**Regulatorik/Haftung:** Hautkontakt: Hautverträglichkeitshinweis (TPU/PETG unbedenklich bei intakter Haut, Reinigungshinweis). Keine Medizinprodukt-Claims („Komfort-Zubehör", nicht „therapeutisch").

**AI-Design-Prompt:**

```
Entwirf ein parametrisches Split-Keyboard-Case (CadQuery mit Import-Mesh-Support).
Eingaben: pcb="Kyria v3" (DXF mit Löchern), tenting_deg=14, dish_mm=8, palm_mesh=scan.stl (oder {palm_length:105, palm_width:85}), tilt_deg=4.
Geometrie: Unterschale exakt auf PCB-Umriss +2 mm mit 4 Schraubdomen (M2-Messingeinsätze) auf die PCB-Löcher; Keywell mit Dish-Tiefe dish_mm über Kugelfunktions-Offset (Radius aus Fingerlängen-DB); Zelt-Block mit Winkel tenting_deg, höhenverstellbare Füße (M6-Gewindeeinsätze, Hub 0–25 mm); Handballenauflage = palm_mesh geglättet (Laplacian 3 Iterationen), auf Dicke 12 mm abgesetzt, als separates TPU-Druckteil mit 4-Pin-Schnappverbindung zur Unterschale.
Randbedingungen: Bauraum 256³ (je Hälfte einzeln), Überhänge > 55° vermeiden durch Zeltgeometrie-Umkehr (Case auf der Zeltfläche liegend drucken), Gewindeeinsätze mit 0,2 mm Spielpassung für M6.
Ausgabe: STEP, STL für jede Hälfte + beide Auflagen + Füße, parameters.json, Tenting-Winkel-Lehre als Kalibrierdruck.
Verifikation: PCB-Passung Kollisionscheck mit 0,3 mm Spiel, Auflagefläche darf keine scharfen Kanten > 30° haben (Hautkomfort), Tenting-Fuß-Belastung: 25 N je Fuß ohne Setzen.
```

---

## Nr. 8 — Werkzeugspezifische Schubladen-Organizer / Shadow Boards

**Typ:** Listen-Produkt · **Score:** 4.40 · **Preis:** 40–90 € je Schublade · **Kanal:** Etsy, Werkstatt-/Schrauber-Communities, B2B (Werkstätten, Fuhrpark)

**Konkretes Produkt:** Schubladen-Einsatz für eine definierte Schublade (z. B. 396 × 263 mm, Rastermaß von Werkstattwagen-Herstellern), bestückt nach der Werkzeugliste des Kunden (z. B. „Wera Kraftform 12-tlg + 1/4"-Knarrenkasten"): jede Kontur als Schattenriss mit 1,5 mm Spielpassung, Grifffinger-Ausschnitt, Beschriftungsfeld im Druck (erhabene Schrift). Optional 2-farbig (Grundplatte schwarz, Kontur-Ebene farbig) als „Tool-Tetris"-Look.

**Warum FDM statt Serie:** CNC-gefräste Schaumstoff-Shadow-Boards kosten 60–150 € je Schublade und sind empfindlich; gedruckte Einsätze sind präziser, waschbar und je Werkzeugliste frei. B2B-Wiederkauf (neue Schublade = neue Datei, 10 Minuten Arbeit) macht das Modell skalierbar.

**Parametrische Eingaben:** Schubladen-Innenmaß + Eckradius, Werkzeugliste (je Werkzeug Silhouette aus Foto-Vermessung oder Standard-DB: Schraubendreher, Knarren, Schlüsselweiten), Raster-Optionen, Farbteilung.

**Material & Druck:** PLA (Werkstatt indoor), 0,4 mm für Konturdetails, Höhe 45–65 mm standardisiert; mehrfarbig über Filamentwechsel.

**Regulatorik/Haftung:** Unkritisch.

**AI-Design-Prompt:**

```
Entwirf einen parametrischen Shadow-Board-Schubladeneinsatz (OpenSCAD).
Eingaben: drawer={"L":396,"B":263,"H":60,"corner_r":12}, tools=[{type:"Schraubendreher","silhouette":dxf,"label":"PH2"}...], grid=true, two_color=true.
Geometrie: Grundplatte 5 mm mit 4 mm Umlaufrand; je Tool eine Tasche = Silhouette geoffsettet +1,5 mm, Tiefe = Toolhöhe + 2 mm, mit Grifffinger-Halbschale R14 am Entnahme-Ende; erhabene Beschriftung 4 mm Schrift (0,8 mm hoch, für 2-Farb-Druck zweite Ebene); Restfläche als Wabenstruktur 15 % Gewicht sparen; 4 Stapel-Nasen für Kombination mehrerer Einsätze.
Randbedingungen: PLA, Bauraum 256³ → sonst Segmentierung quer mit 2 Passzapfen, keine Überhänge (liegende Druckausrichtung), Schrumpf 0,5 %.
Ausgabe: STL (2 Dateien je Farbe bei two_color), parameters.json, Druckbett-Belegung.
Verifikation: Jedes Tool muss mit 2 Fingern ohne Kippen entnehmbar sein (Taschentiefe ≤ 60 % Toolhöhe prüfen), Flächenfüllung der Schublade ≥ 85 %.
```

---

## Nr. 9 — Fahrradspezifische Halterungen (Tacho/Licht/Actioncam)

**Typ:** Modell-Datenbankprodukt · **Score:** 4.35 · **Preis:** 25–45 € · **Kanal:** Etsy, Bike-Foren, Gravel-/Rennrad-Communities

**Konkretes Produkt:** Out-Front-Halterung für einen konkreten Radcomputer (z. B. Garmin Edge 1040) an einem konkreten Vorbau/Lenker (z. B. 31,8 mm Klemmung, Vorbauwinkel −17°), mit integriertem zweiten Arm für Actioncam oder Licht (GoPro-Interface) unter der Halterung. Die Halterung folgt exakt dem Lenkerdurchmesser und Vorbauwinkel, statt mit Gummi-Adaptern zu „wackeln".

**Warum FDM statt Serie:** Generische Halterungen nutzen Gummi-Ringe und passen „irgendwie"; modellspezifische Out-Front-Mounts gibt es nur für Cockpit-Systeme großer Hersteller. Die Kombination Lenkerdurchmesser × Gerätehersteller × Zusatzarm ist eine Multi-DB-Parametrik = klassischer FDM-Long-Tail.

**Parametrische Eingaben:** Lenker-Ø, Vorbauwinkel + -länge, Gerätemodell (Bajonett-DB: Garmin/Wahoo/Bryton/Liv), Zusatzinterface (GoPro/Actioncam), gewünschte Ausladung.

**Material & Druck:** ASA oder PA-CF (Steifigkeit + UV), 0,6 mm, Bajonett mit 0,2 mm Toleranz; Sicherheits-Fangöse (Kabelbinder-Öse) integriert.

**Regulatorik/Haftung:** Hinweis „Sachwerticherung": Bajonett + Fangband-Empfehlung. Keine sicherheitsrelevanten Behauptungen (kein Lenkungs-/Bremskontakt).

**AI-Design-Prompt:**

```
Entwirf eine parametrische Fahrrad-Out-Front-Halterung (CadQuery).
Eingaben: bar_d=31.8, stem_angle=-17, device="Garmin Edge 1040" (Bajonett-DB-Eintrag), arm="GoPro", outreach_mm=55.
Geometrie: Lenkerschelle als 2-Schalen-Klemmung (2× M4, 10 Nm-Auslegung) mit exaktem Radius bar_d/2 + 0,2 mm plus TPU-Einlage gegen Verrutschen/Kratzer; Ausleger in stem_angle-Ebene, Querschnitt als geschlossener Hohlkasten 18×12 mm; Geräte-Aufnahme als 1/4-Dreh-Bajonett aus der Geräte-DB mit Verriegelungsnase; darunter 90°-versetzter GoPro-Finger (3-Finger-Standard) mit M5-Edelstahl-Schraube als Achse; Fangösen-Punkt Ø4 am Schellenkörper.
Randbedingungen: ASA/PA-CF, Bauraum 256³, druckbar liegend ohne Stützen im Bajonett (Ausrichtung so, dass Rastflächen in X/Y liegen), Wand ≥ 2,5 mm an allen Lastpfaden.
Ausgabe: STEP, STL (Schale A/B, Bajonett-Teil, GoPro-Teil falls nötig), TPU-Einlage STL, parameters.json.
Verifikation: Klemmkraft auf Stahl-/Carbon-Lenker (Carbon: Drehmoment-Warnung 5 Nm im Datenblatt), Biegeprüfung Ausleger rechnerisch mit 150 g Gerät × 3 g Stoßfaktor, Bajonett-Verdrehmoment ≥ 2 Nm.
```

---

## Nr. 10 — Sim-Racing-Adapter und Cockpit-Zubehör je Lenkrad-Kombination

**Typ:** Modell-Datenbankprodukt · **Score:** 4.20 · **Preis:** 50–120 € · **Kanal:** Etsy, Sim-Racing-Foren/Discord (stark zahlungsbereit)

**Konkretes Produkt:** Adapterplatte Quick-Release-Basis (z. B. Fanatec/Thrustmaster-Verzahnung) → Momo-/350-mm-Lenkrad-Lochbild plus dazu passender Schaltknauf in individueller Handgröße (Länge/Griffdurchmesser aus Angabe), mit eingelassenem Magneten für Schaltpaddel-Zubehör. Sim-Racer kombinieren ständig Ökosysteme — Adapter zwischen Base/Rad/Booster sind deren Dauer-Thema.

**Warum FDM statt Serie:** Adapter existieren als Alu-Teile (40–80 €) nur für Top-Kombinationen; die Long-Tail-Kombinationen („meine Base" × „mein Lenkrad" × „mein Shifter") sind gedruckt in PA-CF/PETG genauso stabil bei Bruchteil der Kosten — und der Schaltknauf wird gleich noch hand-individuell.

**Parametrische Eingaben:** Basis-Typ (Verzahnungs-DB), Lenkrad-Lochbild (6× 70 mm M6 Standard oder kundenspezifisch), Knauf: Handlänge → Griff-Länge, Griff-Ø, Gewinde des Shifters (M10×1,25/M12×1,75-DB).

**Material & Druck:** PA-CF oder PETG (hohe Steifigkeit), Messing-Gewindeeinsätze, 0,6 mm; Knauf optional zweifarbig mit TPU-Griffring.

**Regulatorik/Haftung:** Unkritisch (Spiel-/Hobby-Equipment). Hinweis: keine Verwendung an echten Fahrzeugen.

**AI-Design-Prompt:**

```
Entwirf Sim-Racing-Adapter + Schaltknauf (CadQuery).
Eingaben: base="Fanatec Podium" (Zahnkranz-DB-Eintrag), wheel_pattern={"holes":6,"pcd":70,"thread":"M6"}, shifter_thread="M10x1.25", hand_length_mm=190.
Geometrie: Adapter = Grundplatte 12 mm mit formschlüssiger Aufnahme des Basis-Zahnkranzes (Spiel 0,15 mm) + 6 Gewindeeinsätzen M6 auf dem Lenkrad-Lochbild + Zentrierkonus; Auslösemechanik-Freigang gemäß Basis-Spezifikation. Schaltknauf: Länge = hand_length × 0,95, Griff-Ø 32 mm mit 3 TPU-Ringen (eingelegt), oben M12-Magnetbucht für optionale Ganganzeige-Platte, unten shifter_thread mit Gewindeeinsatz und Kontermutter-Nut.
Randbedingungen: PA-CF, Bauraum 256³, Adapter liegend drucken (Zahnkranz-Ebene = X/Y), keine Stützen in Verzahnung; Gewindeeinsätze mit Schmelz-Einpresspassung 0,2 mm.
Ausgabe: STEP, STL je Teil, parameters.json, Explosionsansicht.
Verifikation: Spielfreiheit der Verzahnung dokumentieren (0,15 mm), Knauf-Griffsicherheit: keine Kante > 30° an Handanlage, Gewinde-Auszugskraft > 200 N.
```

---

## Nr. 11 — VR-Zubehör je Headset-Modell (Interface, Strap, Lens-Carrier)

**Typ:** Modell-Datenbankprodukt · **Score:** 4.15 · **Preis:** 35–60 €/Bundle · **Kanal:** Etsy, VR-Communities (Quest-Nutzerbasis ist riesig)

**Konkretes Produkt:** Komfort-Bundle für ein konkretes Headset (z. B. Quest-Generation): Gesichtsauflage-Rahmen mit TPU-Kontaktfläche (austauschbar/waschbar), Adapter für Aftermarket-Riemen (Elite-Strap-Interface) und ein Einschubträger für Korrekturlinsen (Rezeptgläser des Optikers), der in den Headset-Linsenabstand eingesetzt wird. Drei Teile = ein Listing, das exakt auf das Headset-Modell passt.

**Warum FDM statt Serie:** Zubehörhersteller brauchen Monate für neue Headset-Generationen; die Variante „mein Headset + mein Riemen + meine Linsenstärke" baut sich aus 3 Datenbanken parametrisch. Kontaktfläche aus TPU ist im Spritzguss für Long Tail unwirtschaftlich.

**Parametrische Eingaben:** Headset-Modell (Gehäusekontur-Befestigungspunkte aus DB), Riemen-Typ (Interface-DB), Linsen-Träger: Glasdurchmesser (Optikerangabe), IPD-Korrekturposition optional.

**Material & Druck:** PETG-Träger + TPU 95A Kontaktfläche (zweiteilig, Schnappverbindung), 0,4 mm für Passflächen, Schicht 0,16 mm.

**Regulatorik/Haftung:** Hautkontakt-Hinweis (Reinigung, Materialunbedenklichkeit), keine optischen Claims („Träger für Korrekturlinsen vom Optiker", keine eigene Linsenwirkung).

**AI-Design-Prompt:**

```
Entwirf ein parametrisches VR-Zubehör-Bundle (CadQuery).
Eingaben: headset="QuestG3" (Befestigungs-DB: Nasenausschnitt-Kontur, 4 Clip-Punkte), strap="EliteStrap", lens={"d":38,"t":2.5,"count":2,"ipd":63}.
Geometrie: (1) Gesichtsrahmen = umlaufender Clip-Rahmen auf die Headset-Nasen-/Gesichtskontur mit 1,5 mm TPU-Auflageband (Schnappnut 2×1,5 mm), Belüftungsschlitze gegen Beschlagen (12× 2 mm). (2) Strap-Adapter: formschlüssige Aufnahme des Elite-Strap-Bügels mit 2 Rastnasen, spielfrei 0,2 mm. (3) Lens-Carrier: 2 Fassungen für Linsen d/t mit Snap-Ring, Abstand = ipd aus Headset-DB, Einsetztiefe bis 0,5 mm vor die Headset-Linse, mit Rand-Grifflasche zum Entnehmen.
Randbedingungen: PETG + TPU, Bauraum 256³, Passflächen mit 0,4 mm Düse bei 0,16 mm Schicht; keine scharfen Kanten zur Haut (R1 min).
Ausgabe: STEP, STL je Teil (Träger + TPU-Auflage + Adapter + 2× Fassung), parameters.json.
Verifikation: Clip-Pässe am Headset-Modell kollisionsfrei mit 0,2 mm Spiel, TPU-Auflage ohne Spalt, Linsenfassung hält 2,5 mm Glas ohne Klappern (0,3 mm Toleranzkette dokumentieren).
```

---

## Nr. 12 — Kosplay-/Fankostüm-Helme mit Kopfmaß-Segmentierung

**Typ:** Scan-Produkt (Kopfmaß) · **Score:** 4.15 · **Preis:** 120–300 € · **Kanal:** Etsy, Cosplay-/Prop-Communities

**Konkretes Produkt:** Parametrischer Sci-Fi-/Fantasy-Helm (generische Designs ohne Marken-IP) in exakter Kopfweite des Käufers (Kopfumfang + optionale Scan-Passung für Kinn/Breite): automatisch segmentiert in 4–6 druckbare Teile mit Passstiften und Magnet-Schließpunkten, inklusive Visier-Öffnung nach Wunschgröße und Belüftungsschlitzen. Kunde erhält den fertigen Druck (roh oder grundiert).

**Warum FDM statt Serie:** Serien-Cosplay-Helme sind Einheitsgröße (passen 80 % nicht) oder Resin-Bausätze ohne Größenanpassung. Kopfweite ist der Schmerzpunkt — und Segmentierung auf Druckergröße ist automatisch lösbar. Hohe Zahlungsbereitschaft (Kostüm-Markt 100 €+ je Teil).

**Parametrische Eingaben:** Kopfumfang (mm), Kopf-Breite/Kinn-Maß optional, Helm-Design-Variante (eigene Designbibliothek), Visier-Öffnung, Wandstärke, Segmentierungsstrategie (automatisch nach Bauraum).

**Material & Druck:** PLA (leicht, schleifbar) 0,6 mm, 3 Wände; Passstifte 6 mm, Neodym-Magnete 10×3 mm in Aufnahmen mit Schrumpfsitz.

**Regulatorik/Haftung:** Wichtig: Deko-Artikel, „kein Schutzhelm" (klar im Listing); nicht als Motorrad-/Ski-Ersatz. Markenfrei designen (eigene Designs oder lizenzfreie Vorlagen) — IP ist hier das Hauptrisiko, nicht Produktsicherheit.

**AI-Design-Prompt:**

```
Entwirf einen parametrischen Kopfhelm mit automatischer Segmentierung (CadQuery oder OpenSCAD + Mesh-Segmentierung).
Eingaben: head_circumference_mm=58, head_width_mm=152, design="eigenes_scifi_helm_design_v1" (eigene Mesh-Bibliothek, keine Marken-IP), visor_opening={"h":70,"b":160}, wall=2.8, build_volume=256³.
Geometrie: Helmschale = Design-Mesh auf Innendurchmesser aus head_circumference skaliert (Pi-Kette: d = Umfang/Pi + 8 mm Komfort-Spiel); Innenschale mit umlaufendem Stirn-/Kinn-Auflagering (TPU-Pads 2 mm); automatische Zerlegung in ≤ 6 Segmente so, dass jede Naht versetzt zur Sichtlinie liegt, je Naht 3 Passstift-Bohrungen Ø6 H7 + 2 Magnetbuchsen (Ø10×3, Schrumpfsitz −0,15 mm); Belüftung: 8 Schlitze 20×3 mm im Hinterkopfbereich; Visierkante 3 mm Rand gegen Ausreißen.
Randbedingungen: PLA, wanddickengerechte Ausrichtung je Segment (größte Fläche auf Bett), Stützen nur an < 30° Überhängen und dann lösungsmittelfreundlich (stegartig).
Ausgabe: STL je Segment + Stifte, Montageplan SVG, parameters.json, Render.
Verifikation: Innenvolumen ≥ Kopfmaß + Komfort, Nahtspalt ≤ 0,5 mm im Soll-Zustand, Magnetanzug je Segment ≥ 3 N.
```

---

## Nr. 13 — Zubehör für Systemmöbel (IKEA-&-Co.-Ökosysteme)

**Typ:** Modell-Datenbankprodukt · **Score:** 4.15 · **Preis:** 25–60 €/Set · **Kanal:** Etsy, IKEA-Hack-Communities (sehr groß), Einrichtungsnischen

**Konkretes Produkt:** Funktionales Zubehör-Set für ein definiertes Möbelsystem (Premiere: SKÅDIS-Lochwand, IVAR-Regal, KALLAX): z. B. ein SKÅDIS-Set nach Werkzeugliste des Kunden (Haken für jeden Akkuschrauber/Abroller/Zollstock mit 1:1-Aufnahme) plus Zubehörhalter, die es im Originalsortiment nicht gibt (Kabelroller-Halter, Winkel für Tiefenversatz). Die Möbelsystem-Geometrie (Lochraster, Plattenstärke) liegt als DB vor → 100 % parametrisch.

**Warum FDM statt Serie:** IKEA selbst macht nur Basis-Zubehör; Drittanbieter (Etsy!) bedienen Nischen bereits — aber nur wenige Top-Anwendungen. „Für genau meine Werkzeuge an genau meinem System" mit exakter Systemkompatibilität ist ein sauberer Differenzierer. Achtung: Abhängigkeit von Fremd-Ökosystemen (Strategierisiko, siehe Kap. 9).

**Parametrische Eingaben:** Möbelsystem + Zubehör-Typ, Werkzeugliste (Konturen), Sonderfunktionen (Tiefenversatz, Neigung), Farbe passend zum System (weiß/schwarz/orange-DB).

**Material & Druck:** PLA oder PETG (je nach Last), 0,6 mm; Systemfarben als Filament lagerhaltig.

**Regulatorik/Haftung:** Lastangaben je Halter (z. B. 2 kg bei 2-Punkt-Haken), Montage nur innerhalb der System-Spezifikation. Markenrecht: nur Kompatibilitätsangaben.

**AI-Design-Prompt:**

```
Entwirf parametrisches Zubehör für ein Lochwand-/Regalsystem (OpenSCAD).
Eingaben: system="SKADIS" (DB: Schlitzbreite 6, Schlitzlänge 55, Materialstärke 5, Rasterabstände), items=[{type:"Akkuschrauber","silhouette":dxf,"gewicht_g":900}...], extras={"kabelroller":true,"winkel_tiefe":2}.
Geometrie: Je Item ein Halter mit 2 Systemzapfen (6×55 Schlitz-Passung mit 0,4 mm Spiel und Rastnase gegen Herausfallen), Aufnahme = Silhouette +1 mm, Lastpfad so, dass Gewicht in Richtung Platte zieht (kein Hebel > 60 mm ohne dritten Abstützpunkt); Kabelroller-Halter mit Ø40-Rolle-Freiraum; Tiefenwinkel als U-Bügel mit 2 Zapfen und 40 mm Ausladung inkl. Versteifungsrippe.
Randbedingungen: PETG, Bauraum 256³, liegende Druckausrichtung für Zapfenfestigkeit (Faser-/Schichtrichtung beachten: Zuglast parallel zur Schicht vermeiden → Zapfen stehend drucken), Schrumpf 0,5 %.
Ausgabe: STL je Halter, parameters.json, Montagefoto-Render, Lasttabelle.
Verifikation: Jeder Halter: Haltekraft ≥ 3 × Itemgewicht je Zapfen (rechnerisch), kein Kippen bei einseitiger Last, Zapfen ohne Spiel in System-Schlitz.
```

---

## Nr. 14 — RC-Modell-Ersatz- und Tuningteile je Chassis

**Typ:** Modell-Datenbankprodukt · **Score:** 4.05 · **Preis:** 30–60 € · **Kanal:** Etsy, RC-Foren, Crawler-/Drift-Communities

**Konkretes Produkt:** Stoßdämpfer-/Ramschutz-Set (TPU-Bumper) plus Body-Mount-Adapter und Kabelhalter für ein konkretes RC-Chassis (z. B. TRX-4-Klasse Crawler): Befestigungslochbilder aus der Chassis-DB, TPU-Rammschutz vorne/hinten in 2 Härten (95A/60A als Variantenprodukt). RC-Fahrer drucken heute schon selbst — verkauft wird Designqualität + Passgenauigkeit + Materialkombi, die zu Hause kaum erreichbar ist (z. B. ASA + TPU zweifarbig).

**Warum FDM statt Serie:** OEM-Ersatzteile sind teuer und oft nur komplett (Träger + Bumper); gedruckte Tuningteile sind in der Szene akzeptiert und sogar erwartet. Long Tail an Chassis-Generationen, schnelle Iteration = FDM-Stärke.

**Parametrische Eingaben:** Chassis-Modell (Lochbild-/Achshöhen-DB), Bumper-Härte Variante, gewünschte Überstand-Höhe, Zusatzfeatures (Seilwinden-Halterung, LED-Aufnahme).

**Material & Druck:** TPU 95A/60A + ASA-Trägerplatten, 0,6 mm, flexible Teile dünn (1,2–2 mm) für Funktion.

**Regulatorik/Haftung:** Unkritisch (Hobby). Kein „bruchsicher bei Vollgas"-Claim.

**AI-Design-Prompt:**

```
Entwirf RC-Rammschutz + Anbauteile (CadQuery).
Eingaben: chassis="TRX4" (DB: Befestigungsbohrungen M3, Achshöhen, Body-Linie), hardness="95A", lift_mm=8, extras={"winch_mount":false,"led":"ja"}.
Geometrie: Front-/Heck-Bumper als 1,2 mm starke TPU-Lippe mit Wabenkern (Wabe 6 mm, Wand 0,8 mm) auf ASA-Montageplatte 3 mm, verschraubt über Chassis-Lochbild (Gewindeeinsätze M3); Bumper folgt der Body-Linie mit lift_mm Bodenfreiheit; LED-Aufnahme als 20-mm-Bohrung mit TPU-Dichtring; alle Schraubenköpfe versenkt.
Randbedingungen: TPU + ASA separat drucken, Bauraum 256³, TPU direkt drucken ohne Stützen (Wabenkern liegend), ASA-Platte mit 0,7 % Schrumpfkorrektur auf Lochbild.
Ausgabe: STEP, STL je Teil, parameters.json, Härtevarianten als eigene Dateien (_60A-Suffix).
Verifikation: Chassis-Passung kollisionsfrei (Achsausschlag links/rechts geprüft), Bumper-Federweg rechnerisch dokumentiert, Schraubauszug > 100 N je Punkt.
```

---

## Nr. 15 — Arca-Swiss-Platten & Rig-Zubehör je Kameramodell

**Typ:** Modell-Datenbankprodukt · **Score:** 4.00 · **Preis:** 25–45 € · **Kanal:** Etsy, Foto-/Video-Communities, Fuji/Sony-Foren

**Konkretes Produkt:** Schnellwechsel-Grundplatte (Arca-Swiss-Profil) exakt für ein Kameramodell (z. B. Fuji X-T-Generation): folgt der Gehäuseboden-Kontur, lässt Akku-/SD-Fach frei zugänglich, mit Sicherungsstift gegen Verdrehen und integriertem Kabelclip für Tethering; dazu optional L-Winkel-Aufsatz und Objektivdeckel-Halter am Gurt. Kameramaße aus DB (jedes Modell: Bodenkontur, Stativgewinde-Position, Klappe-Position).

**Warum FDM statt Serie:** Alu-Platten bedecken nur Bestseller-Bodies; Long-Tail-Bodies und Spezialfälle („mit Batteriegriff dran", „mit Cage darunter") sind gedruckt in PA-CF genauso belastbar für ≤ 2 kg Ausrüstung.

**Parametrische Eingaben:** Kameramodell (DB: Gehäusemaße, Gewindeposition, Klappen), Zubehör-Variante (Platte/L-Winkel), Sicherungsart (Stift/Stoppschraube).

**Material & Druck:** PLA-CF/PA-CF (steif, kratzfest), 0,4 mm für Arca-Profil (38 mm Schwalbenschwanz-Norm mit 0,1 mm Spiel).

**Regulatorik/Haftung:** Kamera-Fallschutz: Platten nur bis 2 kg freigeben + Hinweis auf Sicherungsleine; keine Gewährleistung für Geräte.

**AI-Design-Prompt:**

```
Entwirf eine Arca-Swiss-Schnellwechselplatte (CadQuery).
Eingaben: camera={"model":"X-T5-Gen","L":129,"B":85,"gewinde_x":32,"klappenbereich_x":[44,90]}, type="Grundplatte", pin=true.
Geometrie: Plattenkörper = Kamera-Bodenkontur +0,3 mm Spiel, Höhe 9 mm; Unterseite Arca-Schwalbenschwanz 38 mm (Flankenwinkel 45°, Spielpassung für Arca-Klemmen 0,1 mm); Stativgewinde 1/4"-20 Durchgangsbohrung auf gewinde_x mit versenkter Edelstahlschraube; Akku/SD-Klappe als Ausschnitt entlang klappenbereich_x mit 2 mm Sicherheitsrand; Verdrehsicherung: Stift Ø2,5 in Kamera-Gurtöse oder Stoppschraube M2,5; Kabelclip als TPU-Einleger seitlich.
Randbedingungen: PA-CF, Bauraum 256³, liegender Druck (Arca-Profil in X/Y = maßhaltig), Schrumpf 0,3 %, kein Verzug durch gleichmäßige Wandstärke 3 mm min.
Ausgabe: STEP, STL, TPU-Einleger STL, parameters.json, Toleranzdokumentation Arca-Profil.
Verifikation: Spiel in Standard-Arca-Klemme 0,05–0,15 mm, Klappenöffnung bei montierter Platte kollisionsfrei, Biegelast 2 kg mittig → Durchbiegung < 0,3 mm (rechnerisch).
```

---

## Nr. 16 — Angel-Kajak-Ausrüstungskonsolen je Boot-Modell

**Typ:** Modell-Datenbankprodukt · **Score:** 3.90 · **Preis:** 60–140 € · **Kanal:** Etsy, Kajak-Angler-Foren (zahlungskräftige Nische)

**Konkretes Produkt:** Modulare Mittelkonsole/Halterung für ein bestimmtes Angel-Kajak (z. B. Outback-Klasse): Fischfinder-Montagefläche mit exaktem Ausschnitt nach Geber-Kabelweg des Bootsmodells, 2 Rutenhalter im Winkel einstellbar, Köderbox-Aufnahme. Die Konsole clipst/schraubt an die vorhandenen Einschub- oder Drainage-Punkte des Bootsmodells — kein Bohren am Boot.

**Warum FDM statt Serie:** Angel-Kajaks sind hochgradig individualisiert (Boot × Fischfinder × Rutenanzahl); Zubehörhersteller liefern nur Generisches mit Wackelmontage. ASA/UV-beständig gedruckt ist hier dem Billig-Spritzguss-Zubehör qualitativ überlegen.

**Parametrische Eingaben:** Kajak-Modell (Befestigungspunkt-DB), Fischfinder-Modell (Display-Maße + Geber-Typ), Rutenhalter-Anzahl + Winkel, Köderbox-Größe.

**Material & Druck:** ASA zwingend (Salzwasser + UV), 0,6 mm, ≥ 3 Wände, Schraubdomen mit Messingeinsätzen, Rostschutz: nur Edelstahl-Schrauben als Zubehör.

**Regulatorik/Haftung:** Keine Personen-Sicherheitsclaims („kein Haltepunkt zum Einsteigen"), Lastangaben je Modul.

**AI-Design-Prompt:**

```
Entwirf eine Kajak-Ausrüstungskonsole (CadQuery).
Eingaben: kayak="OutbackKlasse" (DB: Drainage-Stopfen-Positionen Ø20, Schienenabstand), fishfinder={"display":"5 Zoll","geber":"Heck"}, rod_holders=2, rod_angle=35, box={"L":270,"B":180}.
Geometrie: Grundplatte folgt der Deck-Kontur des Kajaks an der Einbauposition (aus DB-Konturschnitt). Befestigung über 2 Drainage-Stopfen-Adapter. Fischfinder-Plattform mit Ausschnitt für Geber-Kabel (Kabelkanal bis zur Heckdurchführung, wasserdicht geführt), Display-Halter mit Kugelgelenk-Aufnahme (RAM-Arm-kompatibel, Ø25). Rutenhalter: Rohr Ø45 mit 35°-Neigung und Kardinal-Ausrichtung nach Wunsch. Köderbox-Aufnahme als Wanne mit Abflusslöchern.
Randbedingungen: ASA, Bauraum 256³ → Segmentierung längs mit 2 formschlüssigen Kulissen + 4×M5-Edelstahl, Wand ≥ 2,5 mm, keine scharfen Kanten Richtung Paddler (R3 min.).
Ausgabe: STEP, STL je Segment, parameters.json, Montageanleitung mit Edelstahlschrauben-Liste.
Verifikation: Last 5 kg auf Fischfinder-Plattform rechnerisch (Biegung < 0,5 mm), kein Kontaktkorrosions-Metallmix (nur VA + Kunststoff), Kabelkanal knickfrei (Radius ≥ 15 mm).
```

---

## Nr. 17 — Staubsauger-/Geräteadapter-System (Long-Tail-Durchmesser)

**Typ:** Modell-Datenbankprodukt (Volumen-Long-Tail) · **Score:** 3.90 · **Preis:** 18–35 € · **Kanal:** Etsy, eBay (Suchvolumen!), Ersatzteil-Marktplätze

**Konkretes Produkt:** Präzisions-Adapter von einem konkreten Staubsauger-Modell (z. B. Kobold-, Dyson-V-Klasse) auf Standard-Zubehördurchmesser (32/35/38 mm) oder auf Spezialdüsen, die es für das Modell nicht mehr gibt: mit Rast-/Drehverschluss je nach Original-Mechanik, optional mit Gummi-Lippe (TPU) als Dichtfläche. Zusätzlich „Adapter-Set Haushalt": Sauger + 3 Wunschanschlüsse.

**Warum FDM statt Serie:** Der Markt ist ein klassischer Long-Tail: je Saugermodell existieren 3–8 interessante Adapter, die kein Hersteller mehr macht. Suchanfragen („Adapter Kobold auf 35 mm") sind hoch kaufbereit. Datenbank + Druck = unendlich Varianten ohne Lager. Günstigster Einstieg mit klarem Such-Intent.

**Parametrische Eingaben:** Sauger-Modell (Außen-/Innen-Ø + Rastmechanik aus DB), Zielseite (Durchmesser oder Zubehörkontur), Dichtlippe ja/nein, Wandstärke, Toleranzklasse.

**Material & Druck:** PETG (schlagzäh, abriebfest innen), 0,4 mm für Passflächen, konische Dichtflächen 0,15 mm Toleranz.

**Regulatorik/Haftung:** Unkritisch; Hinweis: Motor-/Saugleistungs-Verluste durch Adapter nicht garantiert (ehrliche Angaben).

**AI-Design-Prompt:**

```
Entwirf einen parametrischen Staubsauger-Adapter (CadQuery).
Eingaben: source={"outer_d":53,"inner_d":48,"verriegelung":"Drehriegel","tiefe":22}, target={"d":35,"art":"Außenklemmung"}, seal=true.
Geometrie: Adapterkörper als konische Übergangshülse Länge 45 mm; Saugerseite als Muffe mit Innenkontur aus DB + Verriegelungsnase; Zielseite als Steckstutzen mit target-Ø und 2 Haltenasen; Dichtlippe als separater TPU-Ring in einer Ringnut (Nut 2,5×2 mm). Wandstärke ≥ 2 mm, innen strömungsglatt (Übergangsradius ≥ 8 mm).
Randbedingungen: PETG, stehender Druck (Achse = Z) für runde Passflächen (beste Maßhaltigkeit), Schrumpf 0,5 % auf alle Durchmesser gegengerechnet.
Ausgabe: STEP, STL, TPU-Ring STL, parameters.json.
Verifikation: Maßlehre je Durchmesser-Typ dokumentieren; Verriegelung muss 15 N Abzugskräfte halten; Durchströmquerschnitt ≥ 90 % des kleineren Anschlussquerschnitts.
```

---

## Nr. 18 — Ergonomische Maus-Shell aus Hand-Scan

**Typ:** Scan-Produkt (Körpermaß) · **Score:** 3.80 · **Preis:** 60–120 € · **Kanal:** Etsy, Ergonomie-/Gaming-/RSI-Communities

**Konkretes Produkt:** Individuelle Maus-Gehäuseschale (Shell) für eine Standard-Elektronik (z. B. ein leicht erhältliches Maus-PCB-Set oder die Elektronik einer vorhandenen Maus des Kunden), Oberfläche aus dem Hand-Scan (oder aus 4 Maßzahlen: Handlänge, Handbreite, Griffstil Claw/Palm/Fingertip). Zweiteilig: PETG-Tragschale + abnehmbare TPU-Auflagefläche an Daumen-/Handballenzone, Kabelauslass positionierbar.

**Warum FDM statt Serie:** Ergonomie-Mäuse (vertical u. ä.) gibt es in 2–3 Einheitsgrößen; wirklich passend ist nur die individuelle Schale. Der Markt (Ergonomie + Gaming + RSI-Betroffene, die kein Medizinprodukt brauchen) ist groß und zahlt für Custom-Shell-Beispiele.

**Parametrische Eingaben:** Hand-Scan-Mesh oder Maßwerte, Griffstil, Elektronik-Kontur (PCB-Bemaßung aus DB), Sensorposition (Höhe bestimmt Tischabstand), Kabelführung.

**Material & Druck:** PETG-Tragschale 0,16 mm Schicht für glatte Oberfläche, TPU-Auflage 95A als separates Druckteil mit Schnapprand, optional Aceton-Glätten bei PETG-Ersatzmaterial.

**Regulatorik/Haftung:** Hautkontakt = unbedenklich; keine therapeutischen Claims („Komfort, nicht Therapie"). Elektronik wird vom Kunden gestellt → keine eigene Elektronik-Zertifizierung.

**AI-Design-Prompt:**

```
Entwirf eine parametrische Maus-Shell (CadQuery + Mesh-Werkzeug oder Blender-basiert).
Eingaben: hand={"scan":hand.stl | "maße":{l:185,b:84,griff:"claw"}}, pcb="StandardMausSet v2" (DB: Umriss, Schraubenpunkte, Sensor-Lochposition), sensor_z=3.
Geometrie: Oberfläche = Handabdruck-Mesh geglättet (Laplacian, 4 Iterationen) mit Ballenzone als eigene Auflage; Unterschale exakt auf PCB-Umriss + Schraubdome; Sensoröffnung an DB-Position mit sensor_z als Tischabstand (Kollisionsprüfung gegen Gleitfläche); Daumenmulde mit 2 TPU-Pads (Schnappnut); Seitenflächen mit R2 verrundet gegen Scheuern.
Randbedingungen: PETG (Schale) + TPU 95A (Pads), Bauraum 256³, druckbar um 25° geneigt für Sichtflächenqualität; Wand ≥ 2 mm an Lastpunkten (Klickbereich 1,5 mm erlaubt).
Ausgabe: STEP, STL Schale/Pads, parameters.json, Gleitflächen-Layout (PTFE-Füße als Kaufteil).
Verifikation: Elektronik-Passung kollisionsfrei, Tischkontakt nur PTFE-Füße + Gleitkanten (Sensorfreiheit prüfen), TPU-Pads ohne Spalt auf der Oberfläche.
```

---

## Nr. 19 — Individuelle Kinn-/Schulterstützen für Streichinstrumente aus Scan

**Typ:** Scan-Produkt (hohe Zahlungsbereitschaft, kleine Nische) · **Score:** 3.75 · **Preis:** 80–180 € · **Kanal:** Etsy, Geigenbauer-Foren, Musikschulen/Lehrer als Multiplikatoren

**Konkretes Produkt:** Kinnstütze für 4/4-Geige, deren Auflageform aus einem Kinn-/Kiefer-Scan des Musikers erzeugt wird (Alternativ: Parametrisches Kinnprofil aus 3 Maßen: Kinnbreite, Kieferneigung, Halslänge). Grundkörper in Guarneri-/Zentralform mit Standard-Beschlag (Metallbügel als Kaufteil), Auflagefläche mit TPU-Haut (abnehmbar, waschbar). Schulterstützen-Adapterplatte in gleicher Logik als Zweitprodukt.

**Warum FDM statt Serie:** Standard-Kinnstützen sind Holz-Einheitsformen (Geiger kaufen 3–5 Stück bis eine „passt"); die individuelle Passform ist heute nur über Handarbeit für 200 €+ verfügbar. Scan + Druck senkt den Aufwand auf Minuten. Nische klein, aber Margen stark und Wiederkauf (Verschleiß, mehrere Instrumente).

**Parametrische Eingaben:** Scan-Mesh oder Profilmaße, Geigengröße (4/4, 7/8…), Beschlag-Typ (Kaufteil-DB), Auflagehöhe, TPU-Härte.

**Material & Druck:** PETG-Körper (Lackierung möglich), TPU 95A Haut; Beschlag = Kaufteil (kein eigenes Metall).

**Regulatorik/Haftung:** Hautkontakt unbedenklich (Reinigung); keine medizinischen Claims; Beschlag-Teile zukaufen etablierter Hersteller (Produkthaftung für Beschlag beim Zulieferer, Montageanleitung beilegen).

**AI-Design-Prompt:**

```
Entwirf eine parametrische Kinnstütze (CadQuery + Mesh-Pipeline).
Eingaben: chin={"scan":kinn.stl | "maße":{breite:48,neigung:12,hals:110}}, violin="4/4", fitting="Guarneri-Beschlag Standard" (Kaufteil-DB: Befestigungslochbild), pad_hardness="95A".
Geometrie: Auflagefläche = Kinn-Mesh gefittet (Offset −0,5 mm Spielpassung) und in eine Guarneri-Umrissplatte 3 mm eingebettet; Unterseite mit Aufnahmen für die Beschlag-Schrauben aus der Kaufteil-DB (Lochbild ±0,1 mm); TPU-Auflage 1,5 mm als separates Druckteil mit umlaufendem Schnapprand (Nut 1,8×1,2 mm). Seitenkanten R2 gegen Kiefer-Scheuern.
Randbedingungen: PETG + TPU, Bauraum 256³, liegender Druck für Maßhaltigkeit des Lochbildausschnitts; Schicht 0,16 mm für Passflächen.
Ausgabe: STEP, STL (Körper + TPU-Haut), parameters.json, Montagezeichnung mit Kaufteil-Stückliste.
Verifikation: Beschlag-Lochbild gegen Kaufteil-Toleranz prüfen, Auflagefläche ohne Druckstellen > 30° Neigung, Reinigungsfähigkeit dokumentieren (TPU abnehmbar).
```

---

## Nr. 20 — Ergonomische Griffe für Werkzeuge aus Hand-Scan

**Typ:** Scan-Produkt (Materialmix-Showcase) · **Score:** 3.75 · **Preis:** 50–120 €/Set · **Kanal:** Etsy, Werkstatt-Community, B2B (Ergonomie-Beratung, Werkstätten)

**Konkretes Produkt:** Individuelle Griffe für den Werkzeugsatz des Kunden (z. B. Stechbeitel, Feilen, Spachtel): der Griffkörper wird aus der Handform (Scan oder Maßangabe „Faustgröße") und dem Werkzeug-Schaftdurchmesser generiert; Zweikomponenten: PETG/PA-Kern mit formschlüssiger Schaftaufnahme (mit Madenschraube gegen Verdrehen) und TPU-Weichzone in der Druckauflage der Finger. Als Set vermarktet („deine 5 Werkzeuge, ein Griff-System").

**Warum FDM statt Serie:** Serielle Werkzeuge haben Standard-Griffe; bei Vielnutzung (Schreinerei, Modellbau) und bei Menschen mit Handproblemen ist der Individualgriff ein Komfortsprung — den es als Serienprodukt nicht gibt (nur Maßanfertigung vom Orthopädiemechaniker, 150 €+). FDM mit Materialmix bildet das wirtschaftlich ab.

**Parametrische Eingaben:** Hand-Scan oder Maße (Faustumfang, Fingerlänge), Werkzeugliste (Schaft-Ø, Schaftform rund/sechskant), Griffstil (Faustgriff/Präzisionsgriff), TPU-Zone ja/nein.

**Material & Druck:** PETG-Kern (0,6 mm), TPU 95A-Auflagen (Snap-Verbindung), optional Messing-Madenschraube M4 als Verdrehsicherung.

**Regulatorik/Haftung:** Wichtig: Werkzeugfunktion bleibt beim Kunden (wir liefern den Griff, nicht das Werkzeug) → keine Werkzeug-Sicherheitszertifizierung. Hinweis: keine Verwendung an stromführenden Werkzeugen (Griffe sind nicht isolationsgeprüft).

**AI-Design-Prompt:**

```
Entwirf parametrische Werkzeuggriffe (CadQuery + Mesh).
Eingaben: hand={"scan":faust.stl | "maße":{umfang:220,finger_l:75}}, tools=[{name:"Stechbeitel","schaft_d":24,"form":"achteck","tiefe":60}...], style="Faustgriff", zone="soft".
Geometrie: Grundkörper = aus Handabdruck abgeleitete Ellipsoid-/Tropfenform (Länge aus Handlänge × 1,1), mit 4 definierten Fingermulden (Ø aus finger_l abgeleitet); Schaftbohrung exakt schaft_d +0,2 mm mit innenliegender Verdrehsicherung (formschlüssig bei Achteck, Madenschraube M4 quer bei rund); TPU-Weichzonen als 2 mm starke, einknöpfbare Schalen auf Druckauflageflächen.
Randbedingungen: PETG + TPU, Bauraum 256³, stehender Druck für Schaftbohrung (Z-Achse), Wand ≥ 3 mm um den Schaft, keine scharfen Kanten zur Hand (R1).
Ausgabe: STEP, STL je Griff + TPU-Zonen, parameters.json, Set-Übersicht.
Verifikation: Verdrehtest rechnerisch (Madenschraube ≥ 15 Nm), Handanlage ohne Kanten > 30°, TPU-Zonen ohne Spalt auf dem Kern.
```

---

# 7. Score-Matrix und Ranking (gewichtet)

Gewichtete Summe (Individualisierung 20 %, Parametrik 20 %, Markt 20 %, FDM-Fit 15 %, Marge 15 %, Regulatorik 10 %):

| Rang | Produkt | Indi | Param | Markt | FDM | Marge | Regul | Score |
|---:|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | Cockpit-Ablagen fahrzeugspezifisch | 5 | 5 | 4 | 5 | 4 | 5 | **4.65** |
| 2 | Pedalboards aus Pedal-Liste | 5 | 5 | 3 | 5 | 5 | 5 | **4.60** |
| 3 | Tablet-Wandhalterungen je Gerät | 4 | 5 | 4 | 5 | 4 | 5 | **4.45** |
| 4 | Schutzcase-Inserts je Ausrüstung | 4 | 5 | 4 | 5 | 4 | 5 | **4.45** |
| 5 | Brettspiel-Organizer je Titel | 4 | 5 | 4 | 5 | 4 | 5 | **4.45** |
| 6 | Camper-Ausbau-Module je Fahrzeug | 5 | 4 | 4 | 4 | 5 | 5 | **4.45** |
| 7 | Split-Keyboard-Cases mit Scan-Passung | 5 | 4 | 3 | 5 | 5 | 5 | **4.40** |
| 8 | Shadow-Board-Schubladen je Werkzeugliste | 5 | 4 | 3 | 5 | 5 | 5 | **4.40** |
| 9 | Fahrrad-Halterungen je Rad/Gerät | 4 | 5 | 4 | 5 | 4 | 4 | **4.35** |
| 10 | Sim-Racing-Adapter je Kombination | 4 | 4 | 3 | 5 | 5 | 5 | **4.20** |
| 11 | VR-Zubehör je Headset | 4 | 4 | 4 | 5 | 4 | 4 | **4.15** |
| 12 | Cosplay-Helme mit Kopfmaß | 5 | 4 | 3 | 4 | 5 | 4 | **4.15** |
| 13 | Systemmöbel-Zubehör je Ökosystem | 4 | 5 | 4 | 4 | 3 | 5 | **4.15** |
| 14 | RC-Teile je Chassis | 3 | 5 | 3 | 5 | 4 | 5 | **4.05** |
| 15 | Arca-Platten je Kameramodell | 3 | 5 | 4 | 4 | 4 | 4 | **4.00** |
| 16 | Angelkajak-Konsolen je Boot | 4 | 4 | 3 | 4 | 4 | 5 | **3.90** |
| 17 | Staubsauger-Adapter-System | 3 | 5 | 3 | 5 | 3 | 5 | **3.90** |
| 18 | Maus-Shells aus Hand-Scan | 5 | 4 | 2 | 4 | 4 | 4 | **3.80** |
| 19 | Kinnstützen aus Kinn-Scan | 5 | 3 | 2 | 4 | 5 | 4 | **3.75** |
| 20 | Werkzeuggriffe aus Hand-Scan | 5 | 3 | 2 | 4 | 5 | 4 | **3.75** |

**Interpretation:** Produkte 1–10 sind „Sofort-Start"-Kandidaten (Datenbank/Liste, keine Scan-Pipeline nötig). Produkte 7, 11, 12, 18–20 entfalten ihr volles Potenzial erst mit einer Scan-/Mess-Pipeline (Phase 2). Produkt 17 ist der günstigste Markteinstieg (Suchvolumen auf Marktplätzen), Produkt 6 der größte Warenkorb.

---

# 8. Übergreifende Erfolgskritikerien

Damit aus den 20 Typen ein skalierbares Geschäft wird, sind vier Quer-Kapazitäten entscheidend:

1. **Variante = Datei, nicht Arbeit.** Jede Bestellung muss automatisch (oder in < 10 Min.) eine druckbare Datei erzeugen: Konfigurator (z. B. Onshape/OpenSCAD-Skript) + Parameter-DB (Fahrzeug-, Geräte-, Spiel-, Pedal-, Werkzeug-Tabellen). Die Prompts in diesem Bericht sind so gestellt, dass sie direkt in einen solchen Konfigurator münden.
2. **Scan-Pipeline als Burggraben (Phase 2):** Smartphone-Fotogrammetrie/App-Scan (Hand, Kopf, Kinn) + automatische Mesh-Bereinigung. Wer Scan-Produkte mit 10 Minuten Durchlaufzeit anbietet, hat kaum Wettbewerb.
3. **Materialmix als Differenzierer:** Rigid + TPU + Gewindeeinsätze/Magnete ist zu Hause kaum prozesssicher druckbar → rechtfertigt den Kaufpreis gegenüber „selbst drucken". Multi-Material-Fähigkeit (AMS/MMU oder 2. Drucker) ist Kernkompetenz.
4. **Recht & Listing-Disziplin:** Kompatibilitätsangaben („passend für …") statt Markennutzung, ehrliche Lastangaben, GPSR-Konformitätserklärung je Produkt, Warnhinweise wo nötig (Airbag, Kamera-Fallschutz, Deko-Helm).

# 9. Risiken und Ausschlüsse

| Risiko | Betroffen | Gegenmaßnahme |
|---|---|---|
| Abhängigkeit von Fremd-Ökosystemen (IKEA/Hersteller ändern Maße) | Nr. 13, 17, 9 | Maße selbst vermessen/db-pflegen; nicht exklusiv auf ein Ökosystem setzen |
| Marken-/IP-Verletzung | Nr. 12 (Helme), alle Kompatibilitäts-Produkte | Nur eigene Designs; Marken nur als „passend für"-Angabe |
| Sachschaden-Haftung | Nr. 15 (Kamera), Nr. 3, Nr. 9 | Fangösen/Sicherungen integrieren, Lastangaben, keine Garantie auf Fremdgeräte |
| Hautkontakt/Sensibilisierung | Nr. 7, 11, 18, 19, 20 | TPU/PETG, Reinigungs-/Allergiehinsweis, keine therapeutischen Claims |
| „Selbst drucken"-Konkurrenz | Nr. 14, 5, 8 | Design-Qualität, Materialmix, Passgarantie und fertigen Druck statt Datei verkaufen |
| Regulatorische Grauzonen (Medizin/Kind/Sicherheit) | — | Hart ausgeschlossen; bei Anfragen strikt ablehnen (Positionierung schützt) |

# 10. Empfohlene nächste Schritte

1. **2 Wochen:** Top-3 validieren (Nr. 1, 2 oder 3 je eigener Affinität): je 1 Musterteil drucken, Fotos, Test-Listing auf Etsy, Suchvolumen-Check.
2. **4 Wochen:** Datenbank + Konfigurator für den Gewinner aufbauen (parameters.json-getrieben, wie in den Prompts angelegt).
3. **Phase 2:** Scan-Pipeline (Hand/Kopf) pilotieren an Nr. 7 oder 20.
4. Vor jedem Produktstart: mesh-validation/fdm-printability-Prüfung + 1 Testdruck je Variante + Druckkosten-Kalkulation (Material + Zeit + Nacharbeit ≥ Preisuntergrenze).

---

*Dieser Bericht ist eine Entscheidungsgrundlage aus Domänenwissen ohne validierte Markt-/Umsatzdaten. Vor Investitionen: Stichproben-Validierung der Nachfrage (Test-Listings, Suchvolumen, Community-Gespräche).*
