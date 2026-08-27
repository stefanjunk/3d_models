# Druckprofil – R1.6 parametrische Oberflächen (DRAFT)

## Gemeinsamer Startpunkt

| Parameter | Startwert |
|---|---:|
| Düse | 0,40 mm |
| Linienbreite | 0,44 mm |
| Schichthöhe | 0,20 mm |
| Orientierung | Unterseite flach |
| Supports | aus |
| Fuzzy Skin | aus |

## Profilabhängige Wirkung

| Profil | Materialstart | Top-Pfad | Hinweis |
|---|---|---|---|
| `carbon` | tiefschwarzes Satin-PETG oder PLA | monoton, möglichst +45° | trocknen; Glanz unter drei Winkeln prüfen |
| `carbon-wave` | tiefschwarzes Satin-PETG oder PLA | monoton, links–rechts / entlang der horizontalen Tows | 0/90-Korbgewebe und Bundles unter drei Winkeln prüfen |
| `micro-cast` | mattes PLA oder PETG | monoton, eine feste Richtung je Modul | kein geometrisches Wandtop-Muster; optional Topmost-Ironing erst nach Coupon |
| `walnut` | mattes walnussbraunes PETG | monoton, vorn–hinten | optionale Wash/Mattschicht nur nach Coupon |
| `steel` | metallisches Graphit-PETG | monoton, einheitlich | Abrasionshinweise des Herstellers beachten |
| `plain` | qualifiziertes Basismaterial | Standardprofil | Nulltextur-Vergleich |

Zuerst den Oberflächencoupon drucken. Prüfkriterien sind erkennbare Musterfamilie bei 300–700 mm Abstand, saubere kurze Pfade, keine scharfen Kanten, Wischreinigung, keine verlorenen Zellen sowie glatte funktionale Keep-outs. Bei `carbon-wave` müssen die breiten 0/90-Tow-Paare und der diagonale Wechsel erkennbar bleiben. Bei `micro-cast` müssen die Drucklinien weniger zusammenhängend erscheinen, ohne sichtbare Löcher oder unangenehme Wandoberseiten zu erzeugen. Carbongefülltes Filament ist optional und kann abrasiv sein; es ersetzt weder Gewebegeometrie noch Düsenprüfung.

Für `micro-cast` Fuzzy Skin zunächst ausgeschaltet lassen. Falls nach dem Maßcoupon noch stärkere Maskierung an vertikalen Wänden gewünscht ist, nur diese Flächen sehr mild und per Slicer-Painting texturieren; Böden und Wandtops nicht global mit Fuzzy Skin belegen. Ironing auf dem Boden kann die Linien weiter beruhigen, kann aber die Facetten optisch abflachen und muss deshalb am Coupon verglichen werden.
