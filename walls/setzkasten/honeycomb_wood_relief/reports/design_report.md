# Konstruktions- und Validierungsbericht

## Verdict

**CONCERNS** – Konstruktion, STEP-Neuladen, Meshintegrität, Ressourcenbudget und
automatische FDM-Prüfung bestehen. Eine echte Slicer-Lagenansicht und physische
Pass-/Lasttests fehlen; deshalb keine finale Fertigungsfreigabe.

## Ergebnis

| Teil | Dreiecke | STL | gemessene Ausdehnung X/Y/Z | Mesh |
|---|---:|---:|---|---|
| Wabe ohne Aufhängung, Holzrelief | 630.400 | 30,06 MiB | 199,9999 / 229,7024 / 55,0 mm | PASS |
| Wabe mit Aufhängung, Holzrelief | 662.516 | 31,59 MiB | 199,9999 / 229,7024 / 55,0 mm | PASS |
| Verbinder | 32 | <0,01 MiB | 8,8548 / 2,6000 / 19,75 mm | PASS |

Beide STEP-Master wurden nach dem Export erneut mit CadQuery geladen: gültiges
B-Rep, je ein Solid, Ausdehnung 199,9999 x 229,7024 x 55,0 mm. Das texturierte
STL ist eine abgeleitete Mesh-Repräsentation und kein STEP-äquivalenter Master.

## Methode und Ressourcen

- Exakte Funktionsgeometrie: CadQuery 2.8.0.
- Relief: kantenkonforme adaptive Verfeinerung nur in sichtbaren Texturzonen,
  danach normalengerichtete Materialabtragung aus der Heightmap.
- Finale maximale Kante in Texturzonen: 1,0 mm.
- Bandbegrenzte kleinste Zielstruktur: 1,2 mm für 0,4-mm-Düse.
- Heightmap: 512 x 512, 0,58594 mm/Pixel bei 300-mm-Kachelung,
  periodisch gespiegelt und danach mit Wrap-Randbedingung gefiltert.
- Gravurtiefe: maximal 0,45 mm innen/außen und 0,35 mm an der Front.
- Rückseitige Funktionszone ab z=35 mm: 0 verschobene Vertices.
- Gemessener Spitzen-RSS des finalen Generierungslaufs: 1.437,39 MiB.
- Größte finale Datei: 31,59 MiB.

Vergleich zur vorhandenen V4-Aufhängungswabe: 14.221.312 Dreiecke und rund
679 MiB gegenüber 662.516 Dreiecken und 31,59 MiB. Das reduziert Dreiecke und
Dateigröße um ungefähr 95 % und vermeidet die globale 4^n-Unterteilung.

Die Vorschau zeigte außerdem fehlerhaft versetzte Hilfsbrücken des ursprünglichen
Aufhängungsskripts. Im lokalen CadQuery-Aufbau überlappen die runden Bosse die
Innenwand direkt; die um den globalen Ursprung rotierten Hilfsblöcke werden nicht
erzeugt. Der finale Aufhängungs-STEP ist gültig und die Mehrwinkelansicht zeigt
keine versetzten Blöcke mehr.

## Tatsächlich ausgeführte Prüfungen

- `git status --short --branch` vor Änderungen: Repository hatte bereits viele
  fremde/stagierte Änderungen; diese wurden nicht verändert.
- Python-Importprüfung: CadQuery 2.8.0, NumPy 2.4.6, Trimesh 4.4.1,
  Pillow 12.2.0, SciPy 1.17.1, Matplotlib 3.11.1 verfügbar.
- Vorschau: `python3 source/generate.py --quality preview --variant plain` – PASS,
  171.494 Dreiecke, 8,18 MiB, wasserdicht; 782,56 MiB Spitzen-RSS.
- Erster Finalversuch mit 12 Verfeinerungsiterationen: abgebrochen bei der
  Aufhängungsvariante; harte Grenze auf 16 erhöht, danach konvergiert in 13.
- Final: `python3 source/generate.py --quality final --variant both` – PASS.
- Rendering: VTK-Offscreen, je vier Ansichten für beide Varianten – PASS.
- `mesh-validation` auf allen exportierten STL-Dateien und dem Vorschau-STL:
  wasserdicht, konsistente Orientierung, ein Körper, positives Volumen,
  0 degenerierte und 0 gebrochene Flächen – PASS.
- `fdm-printability` mit 256 x 256 x 256 mm, PETG, 0,4-mm-Düse,
  0,20-mm-Schicht, 3,6-mm Mindestwand und 1,2-mm Mindestdetail – automatischer
  Geometrie-/Bauraumteil PASS, visuelle Slicer-Prüfung weiterhin erforderlich.

## FDM-Bewertung

- Bauraum: beide Waben passen in dokumentierter Orientierung.
- Rechnerische Mindestwand nach maximaler Gravur beider Wandseiten: 3,6 mm,
  deutlich über dem Zwei-Düsen-Ziel von 0,8 mm.
- Relief bleibt vor den Schwalbenschwanz-Nuten; Passflächen sind unverändert.
- Normbasierte Überhangkandidaten:
  - ohne Aufhängung: 36,60 mm² (0,044 % der Oberfläche),
  - mit Aufhängung: 384,64 mm² (0,456 %),
  - Verbinder: 0 mm².
- Diese Flächen müssen im Slicer insbesondere an Ösen, Nuten und Reliefübergang
  geprüft werden. Die Normalanalyse bestimmt keine reale Supportstrategie.
- Die gravierte Frontfläche liegt in der empfohlenen Orientierung am Druckbett;
  Elefantenfuß und erste Schichten können das dortige feine Relief reduzieren.

## Inspizierte Vorschauen

- `previews/holz_heightmap.png`: Holzmaserung aus `holz.png`, keine künstliche
  Kreuznaht nach periodischer Filterung.
- `previews/wood_relief_multiview.png`: Front, Front-Schräg, Rück-Schräg, Detail.
- `previews/hanger_multiview.png`: Aufhängungsösen und saubere Innenwände.
- Das Seitenrelief ist aus schrägen Ansichten erkennbar; Frontgravur ist wegen
  nur 4,5 mm Stirnbreite und 0,35 mm Tiefe bewusst subtil.

## Nicht validiert / erforderliche Tests

1. **BLOCKER für Fertigungsfreigabe:** Kein Slicer-CLI (`prusa-slicer`,
   `orca-slicer`, `CuraEngine`, `superslicer`) war installiert; keine echte
   Lagenvorschau oder G-Code-Erzeugung ausgeführt.
2. Passcoupon für Verbinder mit 0,25 mm Spiel je Seite drucken und messen.
3. Einzelwabe drucken; Sichtbarkeit der 1,2-mm-Holzstruktur, Naht und
   Elefantenfuß prüfen.
4. Aufhängungswabe mit vorgesehenem Schrauben-/Dübel-/Wandsystem testen.
5. Beladungs- und PETG-Kriechtest im realen Lastpfad durchführen.

Automatische Wasserdichtheit beweist weder Passung noch Tragfähigkeit.
