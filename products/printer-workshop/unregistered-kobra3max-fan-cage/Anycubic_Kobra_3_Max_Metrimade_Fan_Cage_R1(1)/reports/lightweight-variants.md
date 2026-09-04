# Leichtbau-Entscheidung

Die Funktionsanforderung hat sich vom kleinen Lüftergitter zum sichtbaren Vollfront-Cover geändert. Deshalb ist der frühere kleine Käfig kein gleichwertiger Gewichts-Baseline, sondern nur die verworfene Ausgangsarchitektur. Verglichen wurden drei eigenständige Vollfront-Prinzipien.

| Kandidat | Tragstruktur | Luftführung | Gewicht/Herstellbarkeit | Entscheidung |
|---|---|---|---|---|
| A – geschlossene Vollschale | 1,6-mm-Fläche über ca. 72 × 88 mm plus Seitenwände | nur lokaler Lüfterausschnitt; übrige Serienöffnungen potenziell abgeschirmt | steif, aber unnötig schwer und thermisch riskant | verworfen |
| B – feine Wabe | viele kleine Zellen, schmale Rippen | hohe nominelle Offenfläche | sehr viele kurze Extrusionszüge, höhere Druckzeit und empfindliche Rippen | verworfen |
| C – grobe Waben-Schale | Radius 4,2 mm, Rippe 1,2 mm, 2,0-mm-Rand, lokaler 4,8-mm-Rücksprung und vier Seitenfinger | ca. 56,2 % projizierte Offenfläche im Umfeld; eigener verstärkter Fan-Einsatz | D52-CAD-Volumen 9692,94 mm³, daraus ca. 12,31 g PETG bei 1,27 g/cm³; ohne Supports | gewählt |

Der gewählte Entwurf konzentriert Material auf Außenrahmen, Lüfterring, sechs Clipfedern, vier lokale Seitenstabilisatoren und Schriftzugplatte. Die große Fläche bleibt Wabennetz; nur die seitlichen Finger und der Lüfterring sind Passbereiche. Die 0,8-mm-Markenlinien bleiben für eine 0,4-mm-Düse bewusst mindestens zwei typische Linienbreiten sichtbar.

Exakte Druckzeit, Purge-Menge und Slicergewicht sind **NOT_RUN**, weil Anycubic Slicer Next beziehungsweise ein kompatibler CLI-Slicer in der Validierungsumgebung nicht verfügbar ist. Diese Werte müssen im verwendeten Druckprofil bestätigt werden.
