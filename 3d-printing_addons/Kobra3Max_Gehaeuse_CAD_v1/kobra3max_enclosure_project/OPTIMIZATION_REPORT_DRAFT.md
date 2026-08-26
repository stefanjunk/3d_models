# FDM-Effizienzbericht – Kamera-Whitebox DRAFT

## Vorläufige Auswahl

Ausgewählt ist die Hybridvariante mit Kaufplatten, Holzrahmen, Metallscharnier/-griffen und nur funktionsspezifischen Druckteilen. Standardclips für gekaufte LED-Aluminiumprofile werden bevorzugt; `DRAFT_led_profile_clip_17x8.stl` bleibt eine optionale, erst am realen Profil zu prüfende Rückfalllösung.

Geschützte Funktionen sind der Druckerfreiraum, das bodenlose Überstülpen, die Tür- und Griffbelastung, der weiße Kamera-Hintergrund, Kameraschnittstelle, 11-mm-Kugelgelenk, optischer Fensterblick, Lüfterquerschnitt und supportarme Druckorientierung.

## Deterministische Geometrievergleiche

Die Werte stammen aus den geprüften STL-Netzvolumina und dokumentierten Stückzahlen. Festvolumen und daraus abgeleitete 100-%-Masse sind keine Slicer-Verbrauchsprognose.

| Kennwert | v1-Baseline | vollständige Whitebox v1.3 | Änderung |
|---|---:|---:|---:|
| gedruckte Instanzen inkl. vier Coupons | 94 | 47 | −50,0 % |
| aufsummiertes CAD-Festvolumen | 1394,8 cm³ | 934,3 cm³ | −33,0 % |
| theoretische PETG-Masse bei 1,27 g/cm³ und 100 % | 1771,4 g | 1186,5 g | −33,0 % |
| aufsummierte Dreiecke nach Stückzahl | 81.612 | 76.164 | −6,7 % |
| aufsummierte STL-Dateigröße nach Stückzahl | 12,28 MiB | 12,07 MiB | −1,7 % |

Die 47 Instanzen enthalten Kamera-, Kugel- und Gabelcoupons, aber keine optionalen LED-Clips. Zwölf gedruckte Clips würden zusätzlich etwa 25,9 cm³ Festvolumen erfordern; deshalb sind passende Metall-/Lieferantenclips die günstigere Standardwahl.

## Kandidaten

| Kandidat | Geometrie | Prozess | Evidenz/Status |
|---|---|---|---|
| A – Ausgangsbasis | v1 mit langen gedruckten Plattenschienen und abnehmbarer Vollfront | vorhandene Baseline-Annahmen | exakt erhaltene Geometrie; 1394,8 cm³ Festvolumen |
| B – nur Geometrie | vollständige Whitebox v1.3 | hypothetisches feineres 0,4-mm-Profil | 934,3 cm³ Festvolumen; Slicerwerte `NOT_RUN` |
| C – kombiniert | vollständige Whitebox v1.3 | PETG, 0,6 mm, 0,30 mm, ca. 0,68-mm-Linie | vorläufig ausgewählt; exakte Slicerwerte `NOT_RUN` |

Kandidat C ist vorläufig Pareto-bevorzugt: Er halbiert die Teilezahl und senkt das Festvolumen deutlich, ohne Scharnier, Hebegriffe oder großflächige Struktur in gedruckten Kunststoff zu verlagern. Eine endgültige Zeit-/Materialentscheidung bleibt mangels ausführbarem lokalem Slicer blockiert.

## Querschnitte und Fertigungslogik

Der Planungswert 0,6-mm-Düse / 0,68-mm-Linie / 0,30-mm-Schicht ergibt nominell etwa 2,53 mm für vier funktionale Bahnen und 1,50 mm für fünf Deck-/Bodenschichten. Der angeforderte Volumenstrom bei 45 mm/s läge rechnerisch bei 9,18 mm³/s und muss gegen das reale Filamentprofil geprüft werden.

- Metallscharnier, Gegenleiste und Metallgriffe tragen wiederholte bzw. sicherheitsrelevante Lasten.
- Flächige HDF-/PMMA-Kaufteile sparen lange Druckschienen und verringern dunkle Innenfugen.
- Der kurze Arm ersetzt zwei lange Gelenkarme und reduziert Hebelarm sowie Schwingung.
- Drei Socket-Werte verhindern, dass das komplette Kamerateil nur wegen lokaler PETG-Toleranz neu gedruckt werden muss.
- Der Fensterkeil schafft Reflexionskontrolle lokal, ohne ein teures geneigtes Vollfrontpanel.

## Bewusst verworfene Varianten

- gedruckte Vollhöhen-Plattenschienen: zu viele lange Teile und Fugen;
- gedrucktes Türband oder gedruckte Hebegriffe: unpassend für Zyklen und Haubenhandhabung;
- Vollflächen-LED-Wände: mehr Leistung, Wärme, Kosten und Wartung bei flacherer Bildwirkung;
- innenliegende Kamera: ungünstiger für Temperatur, Service und eine mögliche spätere Heizrevision;
- langer 2×150-mm-Kameraarm: mehr Schwingung und größerer Sicht-/Türkonflikt;
- verlustbehaftete STL-Vereinfachung: die parametrischen Netze liegen bereits unter den Budgets.

## Noch fehlende Evidenz

- exakte Slicer-Zeit, tatsächliche Modell-/Supportmasse, Layerzahl und Spitzenvolumenstrom;
- physische Kamera-, Gabel- und Kugel/Socket-Coupons;
- realer Druckerbewegungsraum, Türlauf und Zwei-Personen-Handhabung;
- Kamera-FOV, Fensterreflexe, Licht-/Flimmertest und Temperaturmessung.
