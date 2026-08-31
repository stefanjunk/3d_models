# OpenQuad CF5 - automatischer Plausibilitaetsbericht

**Status:** PRELIMINARY / NOT FLIGHT PROVEN. Ein PASS bestaetigt nur die jeweilige
numerische Entwurfsregel, nicht die Flugsicherheit oder Bauteilfestigkeit.

## Geometrie

- Motorabstand diagonal: 230.0 mm
- Schnittlaenge je CFK-Arm: 103.0 mm
- Freiraum benachbarter Propellerspitzen: 32.9 mm
- XY-Freiraum Propeller/Akkudeck: 10.2 mm
- Einspannung Zentralknoten / Motorhalter: 31.0 / 28.0 mm

## Massen- und Energiebudget

- Geschaetzte Startmasse: 540 g
- Druckteile vor Slicer: 110-135 g
- Nutzbare Akkuenergie bei 80 %: 15.4 Wh
- Reine Rechen-Flugzeit bei 120-160 W: 5.8-7.7 min

## Rohr-Screening (kein Festigkeitsnachweis)

- Lastannahme: 15.0 N am 72.0 mm Kragarm
- angenommener E-Modul: 60.0 GPa
- Biegespannung Rohr: 11.0 MPa
- Enddurchbiegung Rohr: 0.063 mm
- Nicht abgedeckt: Klemmschlupf, Kerben, Druckteilfestigkeit, Alterung, Fatigue, Crash und Resonanz.

## Numerische Regeln

| Regel | Wert | Grenze | Ergebnis |
|---|---:|---:|:---:|
| Abstand benachbarter Propellerspitzen | 32.93 mm | >= 20.00 mm | PASS |
| Propellerabstand zum Akkudeck (XY-Huelle) | 10.15 mm | >= 8.00 mm | PASS |
| Propellerabstand zur Nabenplatte (XY-Huelle) | 7.15 mm | >= 5.00 mm | PASS |
| Einspannlaenge Arm in Zentralknoten | 31.00 mm | >= 25.00 mm | PASS |
| Einspannlaenge Arm im Motorhalter | 28.00 mm | >= 25.00 mm | PASS |
| Akkuschrauben ausserhalb 74 x 33 mm Grundflaeche | 3.50 mm | >= 1.70 mm | PASS |
| Mindeststeg Motorloch zu Pod-Klemmloch | 4.74 mm | >= 2.00 mm | PASS |
| Mindeststeg Pod-Klemmloch zu Rohrkanal | 2.17 mm | >= 2.00 mm | PASS |
| Mindeststeg Pod-Klemmloch zur Aussenkante | 2.30 mm | >= 2.00 mm | PASS |

Erzeugt durch `analysis/validate_design.py`.
