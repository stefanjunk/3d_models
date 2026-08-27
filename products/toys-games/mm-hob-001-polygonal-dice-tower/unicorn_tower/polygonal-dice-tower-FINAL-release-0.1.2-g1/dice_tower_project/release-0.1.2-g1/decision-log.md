# Entscheidungsprotokoll

## 0.1.2-g1 — Finalfreigabe

- Nutzerfreigabe: JuSt-Innovation-Wasserzeichen und vollständiger markierter Produktionskandidat am 2026-08-11 freigegeben.
- Freigegebenes Mesh: `polygonal-dice-tower-DRAFT-watermarked-0.1.2-g1.stl`, SHA-256 `e1bcd78ef49aadfa71c1e82cc8f263b75f39994be50cf12138348411bebe6d6a`.
- Promotion: Der freigegebene Kandidat wird ohne Geometrie- oder Byteänderung als `polygonal-dice-tower-FINAL-0.1.2-g1.stl` veröffentlicht.
- Status: final und digital validiert; Slicer-G-Code-Prüfung und reale Falltests bleiben als physische Fertigungsnachweise offen.

## 0.1.2 — Kanalstutzen verkürzt

- Nutzerwunsch: oberer und unterer Kanal sollen näher an der Außenhülle enden.
- Freigegebene Zielmaße: oben 5 mm sichtbarer Überstand entlang der 45°-Achse, unten 8 mm sichtbarer Überstand.
- Umsetzung: Nur die äußeren Endpunkte der beiden parametrischen Kanal-Liner wurden zurückgesetzt. Die verlängerten Schneidkörper, Öffnungsquerschnitte, Innenübergänge, drei Fallstufen und der Würfelweg blieben unverändert.
- Ergebnis: exportierte Liner messen 5,000004 mm beziehungsweise 8,000000 mm Überstand; beide liegen innerhalb ±0,02 mm des freigegebenen Ziels.
- Regression: ein Körper, wasserdicht, keine offenen oder überbelegten Kanten, 94/94 digitale 25-mm-Würfelpositionen bestanden, Horn und Rückwand geschützt.
- Release-Status: durch die spätere Freigabe `0.1.2-g1` abgelöst.

## 0.1.1 — Schutzbereiche und Kanalform

- Dachhorn und Rückwand außerhalb der Einwurf-ROI wurden als Schutzbereiche festgelegt.
- Einwurf auf kurzen runden 45°-Kanal, Auswurf auf klaren Rundbogenkanal umgestellt.
- Innenzylinder auf Ø 57 mm und Fallstufen auf drei reduziert.
