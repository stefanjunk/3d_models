# Hydraulische Plausibilisierung · Revision 2 DRAFT

Diese Rechnung ist eine analytische Vorprüfung, keine CFD- oder Leistungszusage. Reale Verluste werden besonders von Schlauchlänge, Bögen, Pumpenregelung, Filtermedium, Verschmutzung und FDM-Oberfläche bestimmt.

## Querschnitte und Geschwindigkeiten

| Stelle | freier Querschnitt | 400 L/h | 800 L/h | 1.200 L/h |
|---|---:|---:|---:|---:|
| 18-mm-Zulaufpassage | 254,5 mm² | 0,437 m/s | 0,873 m/s | 1,310 m/s |
| 40-mm-Klarwasserstandrohre | 1.256,6 mm² | 0,088 m/s | 0,177 m/s | 0,265 m/s |
| 32-mm-Fallrohr | 804,2 mm² | 0,138 m/s | 0,276 m/s | 0,414 m/s |
| 100 × 28-mm-Kaskadenschlitz | 2.800 mm² | 0,040 m/s | 0,079 m/s | 0,119 m/s |

Die 40-mm-Standrohre sind gegenüber dem 18-mm-Zulauf deutlich großzügiger. Mit einem vereinfachten Eintrittsbeiwert Cd = 0,62 ergibt sich am 40-mm-Rohr nur etwa 4,15 mm notwendiger Überstand bei 800 L/h und 9,33 mm bei 1.200 L/h. Das ist eine Größenordnungsschätzung; der reale freie Überlauf wird im Wassertest gemessen.

## Abscheidebereiche

- Brutto-Wasservolumen der Wirbelkammer bis zum 210-mm-Überlauf: etwa 13,51 L, noch ohne Abzug von Trichter und Standrohr.
- Daraus folgt eine obere Aufenthaltszeit von etwa 60,8 s bei 800 L/h beziehungsweise 40,5 s bei 1.200 L/h. Das reale Volumen und damit die Zeit sind etwas kleiner.
- Zwölf Lamellen à 200 × 120 mm bei 60° ergeben horizontal projiziert etwa 0,144 m².
- Flächenbelastung des Lamellenpakets: etwa 5,56 m/h bei 800 L/h und 8,33 m/h bei 1.200 L/h.
- Nutzfläche einer Ø242-mm-Medienscheibe: etwa 0,0460 m². Filterflächenbelastung: 17,39 m/h bei 800 L/h und 26,09 m/h bei 1.200 L/h.

Die Abscheidegrenze kann daraus nicht seriös garantiert werden. Partikeldichte, Form, Flockung, Turbulenz und Verschmutzung müssen mit Vorher-/Nachher-Proben geprüft werden.

## Notüberlauf und statische Last

Für den 80-mm-Notüberlauf liefert die vereinfachte Wehrformel `Q = 1,84 · b · h^(3/2)` ungefähr 13,2 mm Überfallhöhe bei 800 L/h und 17,2 mm bei 1.200 L/h. Die 35-mm hohe Öffnung bietet geometrische Reserve; der reale Test erfolgt mit teilweise blockierter Feinmatte.

Bei der begrenzten Prüfhöhe von 1,2 m entstehen etwa 11,8 kPa hydrostatischer Druck. Eine reine Dünnwand-Näherung ergibt für 150 mm Radius und 4,8 mm Wand nur rund 0,37 MPa Umfangsspannung. Für FDM dominieren jedoch Schichtverbund, Naht, Poren, Kerben und Anschlüsse. Diese Rechnung ist keine Druckbehälterfreigabe; geschlossener oder pumpenseitig aufgestauter Betrieb bleibt verboten.

## Einregelung

Den Volumenstrom mit einem bekannten Behälter und Stoppuhr bestimmen. Bei 800 L/h werden 10 L in 45 s gefüllt; bei 1.200 L/h in 30 s. Die Pumpe über Bypass oder freies Drosselventil einregeln, sodass sie nie gegen einen geschlossenen Filter arbeitet.

