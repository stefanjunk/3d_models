# Eckkommode MM-FUR-001 — Bauanleitung

**Revision 0.1.0 · Stand 2026-09-04 · Freigabestand: CONCEPT_ONLY**

> ## ⛔ Vor dem ersten Schnitt: Schritt 0 ist Pflicht
>
> Alle Maße in diesem Dokument gelten für eine **angenommene Nische von
> 1000 × 1000 mm**. Diese Nische ist **nicht gemessen**. Jedes der 13
> Plattenmaße und jede Bohrung leitet sich daraus ab. Wenn du auf diese
> Annahme zuschneiden lässt und die Nische in Wirklichkeit 988 mm hat oder
> eine Sockelleiste im Weg ist, sind rund 6 m² Platte und eine nicht
> nachschneidbare ESG-Scheibe Ausschuss.
>
> **Schritt 0 messen → `source/params.yaml` anpassen → Generator neu laufen
> lassen → dann bestellen.** Das ist eine halbe Stunde Arbeit.

---

## Was entsteht

| | |
|---|---|
| Höhe bis Holz-Deckplatte | **1000 mm** (Glas darauf: 1006 mm) |
| Grundfläche | Fünfeck, **965 mm** an jeder Wand, Front als **45°-Diagonale** |
| Frontbreite | **883,9 mm** |
| Tiefe auf der Eckwinkelhalbierenden | 923 mm |
| Türen | **4 × 440 × 439 × 18 mm**, 2 × 2, alle identisch |
| Fächer | 2 × **423 mm** lichte Höhe, dazwischen ein fester Mittelboden |
| Füße | 6 × höhenverstellbar **100 mm** |
| Glasplatte | Fünfeck, **6 mm ESG**, 0,729 m², **10,9 kg** |
| Gewicht fertig | ca. **81 kg** → **am Aufstellort montieren** |
| Plattenmaterial | 18 mm, eine einzige Dicke für alles |

Warum die Türen in der Mitte angeschlagen sind: bei Anschlag an den Außenenden
würde die Türspitze bei 90° Öffnung **1299 mm** von der Ecke entfernt stehen,
also aus der Nische heraus. Mit Mittelanschlag sind es **973 mm** — die Tür
bleibt vollständig innerhalb der 1-m-Nische. Deshalb sitzen auch alle vier
Griffe an den **Außenkanten** der Türen, nicht innen.

---

## Schritt 0 — Nische aufmessen (Pflicht)

Notiere jeden Wert und trage ihn danach in `source/params.yaml` ein.

| Messung | Wie | Wohin in `params.yaml` |
|---|---|---|
| Breite Wand 1 | in **drei** Höhen: 50 mm, 500 mm, 1000 mm über Boden | `niche.wall_1_mm` = **kleinster** Wert |
| Breite Wand 2 | ebenso | `niche.wall_2_mm` = kleinster Wert |
| Eckwinkel | großer Anschlagwinkel oder Winkelmesser | `niche.corner_angle_deg` |
| Wandebenheit | 1-m-Richtscheit an jede Wand, größter Spalt | erhöht `back_gap` |
| Sockelleiste | Dicke **und** Höhe, oder „keine" | `niche.back_gap_mm` = **Dicke + 3 mm** |
| Boden | Wasserwaage über die ganze Fläche, Höhendifferenz | nur Doku; die Füße gleichen ±8 mm aus |
| Umgebung vor der Nische | steht dort eine Rückwand, ein Türrahmen, eine Heizung? | begrenzt den Türöffnungswinkel |

**Drei Dinge, die hier schiefgehen:**

1. **Wände sind nie rechtwinklig.** Ist der Eckwinkel z. B. 91°, klemmt eine
   starre 18-mm-Rückwand. Bei > 1° Abweichung erhöhe `back_gap` auf 15–20 mm.
2. **Sockelleiste.** Der Entwurf lässt hinten nur 10 mm Luft. Eine 16-mm-Leiste
   schiebt den ganzen Korpus 6 mm vor — und die Front dreht sich aus der Nische.
   Entweder Leiste in der Nische entfernen, oder `back_gap` erhöhen, oder
   P03/P04 unten ausklinken.
3. **Kleinster Wert zählt.** Wenn du in 500 mm Höhe 1002 mm und unten 991 mm
   misst, rechne mit 991 mm.

Danach:

```bash
python3 source/corner_cabinet.py      # Zuschnittliste, Bohrplan, DXF neu
python3 source/drawings.py            # Zeichnungen neu
```

---

## Schritt 1 — Material und Zuschnitt bestellen

**Bezugsdatei: `exports/cut-list.csv`. Sie ist verbindlich, nicht dieser Text.**

### Holz

**Empfehlung: 18 mm Birke-Multiplex.** Nicht aus Sparsamkeit, sondern weil
**Ebenheit hier eine Funktionsanforderung ist**: auf der Deckplatte liegt eine
starre 11-kg-Glasscheibe. Wirft sich die Platte, kippelt das Glas und die Karten
liegen nicht mehr flach. Sperrholz mit gekreuzten Lagen hält das, Nadelholz-
Leimholz nicht zuverlässig. Multiplex ist echtes Holz (Massivholzfurniere, keine
Faser- oder Spanplatte), und deckend weiß lackiert sieht man die Holzart nicht.

*Alternative:* 18 mm **Leimholzplatte Fichte/Kiefer** („nach Maß" bis
1220 × 2500 mm) ist günstiger und unstrittig Massivholz. Dann aber: für die
**Deckplatte P02 trotzdem Multiplex** nehmen, und **Schellack-Absperrgrund**
gegen durchschlagende Astharze — sonst zeichnen sich die Äste durch den weißen
Lack.

### Bestellweg

**Empfohlen: die 13 Rohteile einzeln als Zuschnitt nach Maß bestellen.** Du
zahlst 6,084 m² und hast keinen Abfall zu Hause. Ganze 2500 × 1250-Platten sind
hier schlecht: drei Rohteile sind 927–965 mm breit, der Guillotine-Verschnitt
liegt bei ~49 % Ausnutzung und braucht 4 Platten (12,5 m²).

### Die drei Schrägschnitte

P01, P02 und P08 sind **Quadrate mit einem einzigen geraden Schnitt**:

| Teil | Rohteil | Schnitt von → nach | Länge |
|---|---|---|---|
| P01 Bodenplatte | 965 × 965 | (965; 340) → (340; 965) | 883,9 mm |
| P02 Deckplatte | 965 × 965 | identisch zu P01 | 883,9 mm |
| P08 Mittelboden | 927 × 927 | (927; 340) → (340; 927) | 830,1 mm |

Ob der Markt 45°-Schnitte macht, ist **filialabhängig**: OBI nennt gerade
Schnitte plus Eckfräsungen und Ausschnitte, toom nennt diagonale Eckplatten als
Sonderleistung, Hornbach sagt, die Schnittarten unterscheiden sich je Markt
(Mindestmaß 100 × 230 mm). **Vorher fragen.** Wenn nein: es ist pro Platte
*ein* gerader Schnitt — mit Handkreissäge und Führungsschiene gut machbar.

### Wareneingangsprüfung (nicht überspringen)

Jedes Rohteil: Länge, Breite, und **Diagonale gegen Diagonale**. Toleranz
± 1 mm, Rechtwinkligkeit 1 mm. Ein schiefes Rohteil verzieht den ganzen Korpus
und du kriegst die Türspalten nie gleichmäßig. Reklamieren, solange du im Markt
stehst.

---

## Schritt 2 — Bohren

**Bezugsdatei: `exports/drill-plan.csv`, Zeichnung `exports/drawings/05-bohrbilder.png`.**

Jede Bohrung ist mit **Fläche**, **x**, **y**, **Durchmesser** und **Tiefe**
angegeben. x und y werden immer von zwei **benannten Bezugskanten** gemessen.
Schreibe diese Kanten mit Bleistift auf jedes Teil, **bevor** du bohrst.

### P01 Bodenplatte — 32 Bohrungen, alle von der Oberseite angerissen

Lege die Platte mit der **Oberseite nach oben**, die 90°-Ecke zwischen den zwei
langen geraden Kanten links unten. Schreibe „OBEN", „Wand 1" und „Wand 2" drauf.

- **26 × Ø 4,5 mm durchgebohrt** — später mit 4,5 × 50 in die Unterkanten der
  Vertikalteile. Danach umdrehen und **von unten auf Ø 9 mm ansenken**.
- **6 × Ø 2,0 mm durchgebohrt** — nur Übertragungsmarken für die Füße. Platte
  umdrehen, Fußplatte auf die Marke zentrieren, 4 × Ø 4,0 × 12 mm vorbohren.

Die Schraubenpositionen sind im Generator **automatisch mindestens 45 mm von
jeder Fußmitte weggerückt** — sonst läge eine Senkung genau unter einer
Fußplatte.

### P02 Deckplatte — **keine einzige Bohrung**

Das ist Absicht. Diese Fläche liegt unter dem Glas und ist die Schauseite. Nimm
die ebenste, schönste Seite des Rohteils nach oben. Die Deckplatte wird
ausschließlich **von innen mit Winkeln** befestigt.

### P07 / P09 Mittelstege — je 8 × Ø 5,0 × 10 mm, auf **beiden** Seiten

Rechteck 450 × 423 mm. Vorderkante und Unterkante anschreiben. Alle Löcher
liegen **37 mm von der Vorderkante** (System 32), paarweise 32 mm auseinander.

| Fläche | y-Werte (von der Unterkante) |
|---|---|
| SIDE-1 (zur Wand-1-Seite) | 55 · 87 · 318 · 350 (P07) — 56 · 88 · 319 · 351 (P09) |
| SIDE-2 (zur Wand-2-Seite) | 39 · 71 · 334 · 366 (P07) — 40 · 72 · 335 · 367 (P09) |

**Warum versetzt:** Zwei Montageplatten auf beiden Seiten eines 18-mm-Bretts —
zwei gegenüberliegende Ø-5-Löcher mit 10 mm Tiefe wären 20 mm bei 18 mm Brett,
also ein Durchbruch. Die Bohrbilder sind deshalb um **16 mm** gegeneinander
versetzt; kein Lochpaar liegt auf einer Achse. Halte dich an die Werte.

### P10 Türen — 4 identische Rohteile, **2 Bohrbilder**

Lege jede Tür mit der **Innenseite nach oben**, **Scharnierkante links**,
**Unterkante unten**. Dann gilt für alle vier gleich:

| Bohrung | x | y | Ø | Tiefe |
|---|---|---|---|---|
| Topf 1 | 22,5 | Variante A: **88** / Variante B: **72** | 35 | **12,5** |
| Topf 2 | 22,5 | Variante A: **351** / Variante B: **367** | 35 | **12,5** |
| Griff oben | 400,0 | 283,5 | 5 | durch |
| Griff unten | 400,0 | 155,5 | 5 | durch |

- **Variante A** → die zwei Türen der Wand-1-Seite. **Variante B** → Wand-2-Seite.
- **Tiefenanschlag benutzen.** 12,5 mm im 18-mm-Brett lassen 5,5 mm stehen. Ohne
  Anschlag bohrst du durch die Schauseite.
- Ø 35 mm nur mit **Forstnerbohrer** und **Topfband-Bohrschablone** (oder
  Ständerbohrmaschine). Freihand wird das schief.
- Die zwei Topfschrauben nicht vorbohren: Band einlegen, durchstechen, dann
  Ø 2,5 mm.
- Griffbohrungen **von der Schauseite aus** mit Unterlegholz bohren, sonst reißt
  die Furnierlage aus.

### Alles andere: an Ort und Stelle bohren

Leisten, Winkel, Rückwandverbindungen: trocken zusammenstellen, durch das
bereits vorhandene Loch vorbohren. Das ist genauer als jedes Maß und der Grund,
warum P03–P06 und P08 im Bohrplan leer sind.

---

## Schritt 3 — Anreißen

**Bezugsdatei: `exports/layout-lines.csv`.** Auf P01 **und** P02 identisch:

- P03 Innenseite: parallel zur Wand-2-Kante bei **18 mm**
- P04 Innenseite: parallel zur Wand-1-Kante bei **18 mm**
- P05 Innenseite: parallel zur Wand-2-Kante, bei **x = 947 mm** entlang Wand 1
- P06 Innenseite: parallel zur Wand-1-Kante, bei **y = 947 mm** entlang Wand 2
- P07/P09: die **Winkelhalbierende** der 90°-Ecke; die Stegflächen liegen
  **9 mm** links und rechts davon und laufen **450 mm** von der Vorderkante nach hinten

Auf P03, P04, P05, P06 jeweils die **Oberkante der Traglatte** bei
**y = 423 mm** von der Unterkante.

---

## Schritt 4 — Erst lackieren, dann montieren

Diese Reihenfolge ist kein Geschmack, sondern die Gegenmaßnahme gegen das
Verwerfen der Deckplatte:

1. Kanten spachteln (Multiplex zeigt die Lagen), schleifen K120 → K180, nochmal
   spachteln, schleifen.
2. **Grundierung auf beide Seiten und alle Kanten jeder Platte.** Bei Fichte:
   Schellack-Absperrgrund.
3. Zwischenschliff K240.
4. **Zwei Schichten weißer Acryl-Buntlack, seidenmatt** (RAL 9010/9016), wieder
   **beide Seiten und alle Kanten**.

Ungleich versiegelte Platten nehmen einseitig Feuchte auf und schüsseln. Genau
das darf bei P02 nicht passieren. Zu lackierende Fläche insgesamt: **11,4 m²**.

Innenflächen mitlackieren ist optional, aber die **Kanten sind nicht optional**.

---

## Schritt 5 — Korpus montieren (am Aufstellort)

1. **Füße an P01.** Von unten, Platte auf zwei Böcken. 6 × Anschraubplatte auf
   die Ø-2-Marken zentrieren.
2. **Eckleisten L04** (3 × 423 mm) in die drei Innenecken P03/P04, P04/P05 und
   P03/P06, Oberkante bei z = 541 mm. Sie tragen später die Ecken des
   Mittelbodens — deshalb braucht P08 keine Ausklinkung.
3. **Traglatten L01, L02, L03** auf die angerissenen Linien, Oberkante 423 mm
   über der Unterkante des jeweiligen Teils. 4 × 40 mm, ca. 200 mm Abstand, mit Leim.
4. **Vertikalteile aufstellen**: P03 zuerst (voll durchlaufend, 965 mm), dann
   P04 dagegen (947 mm, stößt an die Innenfläche von P03), dann P05 und P06,
   dann P07. Von unten durch P01 mit 4,5 × 50 verschrauben, Leim auf jede Fuge.
   Nach jedem Teil den Winkel prüfen.
5. **Mittelboden P08** von oben einlegen — er liegt auf L01/L02/L03, den
   Eckleisten und der Oberkante von P07. Von unten durch die Latten mit
   4,0 × 30 hochschrauben.
6. **P09 oberer Mittelsteg** auf P08, genau über P07 (Winkelhalbierende), mit
   2 Winkeln unten und 2 oben.
7. **Deckplatte P02** auflegen. Leim auf alle Oberkanten, ausrichten, dann von
   **innen** mit **8 Winkeln 40 × 40** und **4 × 16 mm** Schrauben nach oben in
   P02 schrauben. 16 mm — nicht länger, sonst kommt die Spitze auf der Schauseite raus.
8. Kommode in die Nische schieben. **Füße einstellen: nicht den Boden, sondern
   die Deckplatte nivellieren**, in zwei Richtungen, ≤ 1 mm/m. Erst drei Füße
   ausrichten, dann die anderen drei bis zur Berührung nachdrehen.

---

## Schritt 6 — Türen

1. Montageplatten in die Ø-5-Löcher von P07/P09, **Distanz 0 mm**.
2. Topfbänder in die Türen, **Mittelanschlag/halbaufliegend** — nicht
   Vollauflage. Beide Türen einer Reihe schlagen auf demselben 18-mm-Steg an und
   überdecken ihn je **7,5 mm**.
3. **Eine** Tür einhängen und komplett einstellen: Spalt **3 mm ± 1 mm** an
   allen Kanten, Tür öffnet ≥ 90° ohne Kontakt zur Nachbartür. Erst wenn diese
   eine Tür stimmt, die anderen drei anschlagen.
4. Griffe: M4-Schrauben mindestens 22 mm.
5. 2 Türpuffer pro Tür auf die Korpus-Vorderkanten.
6. Nach der ersten Heizperiode nachstellen. Das ist normal, kein Fehler.

---

## Schritt 7 — Glas (immer zuletzt)

> **ESG lässt sich nicht nachschneiden.** Korpus fertig gebaut, lackiert und
> nivelliert → **fertige Deckplatte messen** → dann bestellen.

- Vorher mit dem Richtscheit prüfen: **Ebenheit ≤ 1,0 mm auf 900 mm**. Wenn die
  Platte schüsselt, kommt das Glas nicht darauf.
- Bestelltext: **ESG 6 mm, klar, Fünfeck nach DXF, alle Kanten geschliffen und
  poliert, Ecken gerundet R5.** DXF: `exports/dxf/P11-glass.dxf`.
- Sollmaß aus dem Modell: 961 × 961 mm Quadrat mit einem Schnitt von (961; 337)
  nach (337; 961). Gegen die **Ist-Maße** der gebauten Deckplatte abgleichen,
  Ziel: 1–3 mm Luft rundum.
- ESG, polierte Kanten und gerundete Ecken sind **Sicherheitsanforderungen**,
  keine Ausstattungsoptionen — du hebst diese Platte bei jedem Kartenwechsel an.
- **10,9 kg. Zu zweit tragen, an der Kante anfassen, nie an einer Ecke.**
- Karten einlegen: Vorderkante des Glases anheben, Karten einschieben. Optional
  2 Edelstahl-Glasanschläge an den beiden wandseitigen Kanten, damit die Scheibe
  nicht nach hinten rutscht; die Vorderkante bleibt frei.

---

## Abnahme

`design-spec.yaml → acceptance`, A-01 bis A-10. **Alle NOT_RUN.** Die
blockierenden: A-01 Messgate, A-02 Rohteilmaße, A-03 Einbau, A-04 Nivellierung,
A-05 Deckplatten-Ebenheit vor der Glasbestellung, A-06 Türspalt und 90°,
A-07 Glasspezifikation, A-09 Kippprüfung mit 200 N an der offenen unteren Tür.

Trage jedes Ergebnis nach — es hebt die Reife des Produkts von R1 auf R5.

## Wenn Kinder Zugang haben

Die Kommode ist tief und schwer und kippt im Entwurf nicht über die Wand ab.
Ein Kind, das sich auf eine offene untere Tür stellt, ist trotzdem ein
plausibler Versagensfall (Preflight `IF-HUM-USR-USR-VOLUME-010`, ungeprüft).
Dann **einen Kippschutzwinkel** in eine Wand setzen. Kostet 8 €.
