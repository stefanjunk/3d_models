# Barfußschuh V4.1 – Performance-optimiert

Diese Version behebt die Meldung:

```text
Normalized tree is growing past 200000 elements
CSG normalization resulted in an empty tree
```

## Ursache

Die vollständige Laufsohle enthält je nach Einstellungen sehr viele einzelne
Grip-Elemente. Zusammen mit Innenzellen, Textbeschriftungen und verschachtelten
Booleschen Operationen kann OpenSCADs F5-Vorschau die CSG-Grenze überschreiten.

## Neues Verhalten

Bei **F5 / Preview** sind standardmäßig deaktiviert:

```scad
preview_show_grip = false;
preview_show_internal_cells = false;
preview_show_pattern_labels = false;
```

Die Außenform, Randgeometrie, Stoßschutz und Befestigungsteile bleiben sichtbar.
Bei **F6 / Render** und beim STL-/3MF-Export wird die vollständige Geometrie erzeugt.

Zum Prüfen einzelner Details kannst du die Optionen temporär aktivieren:

```scad
preview_show_grip = true;
preview_show_internal_cells = true;
preview_show_pattern_labels = true;
```

Nicht alle drei gleichzeitig aktivieren, wenn das Modell groß ist.

## Weitere Optimierungen

- Grip-Noppen werden nur noch innerhalb der örtlichen Sohlenbreite erzeugt.
- Runde Grip-Elemente verwenden eine eigene, niedrigere Segmentzahl.
- Komplexe Grip- und Zellteilbäume werden beim finalen Rendern frühzeitig
  über `render()` zu Meshes zusammengefasst.
- Die allgemeine Segmentzahl ist in der Vorschau niedriger.

## Empfohlener Ablauf

### Sohle bearbeiten

```scad
output_part = "sole_only";
preview_show_grip = false;
preview_show_internal_cells = false;
```

Mit F5 Maße und Form prüfen. Erst danach F6 drücken.

### Laufprofil allein prüfen

```scad
output_part = "sole_only";
preview_show_grip = true;
preview_show_internal_cells = false;
```

Falls F5 erneut zu groß wird, Grip wieder ausblenden und direkt F6 verwenden.

### Schnittmuster bearbeiten

```scad
output_part = "pattern_all";
preview_show_pattern_labels = false;
```

Beschriftungen erst für den finalen SVG-/DXF-Export über F6 aktivieren.

## Noch schnellerer Test

Für schnelle Konturtests:

```scad
outsole_style = "plain";
internal_structure = "solid";
toe_bumper_enabled = false;
```

Danach die Funktionen schrittweise wieder aktivieren.

## Hinweis zu deinem Log

Der erste Abschnitt stammt aus der CSG-Vorschau und wurde abgebrochen. Der
anschließende Abschnitt mit `Rendering Polygon Mesh using CGAL` zeigt, dass
OpenSCAD bereits den exakten F6-Render gestartet hat. Die V4.1 verhindert in
der Regel, dass die normale Vorschau vorher leer wird.
