# Barfußschuh V4 – integrierte Sohle und Textilschnittmuster

## Wesentliche Änderung

Sohle und Schnittmuster befinden sich jetzt in **derselben OpenSCAD-Datei** und verwenden dieselben Parameter sowie dieselbe Konturfunktion:

```scad
sole_outline_left_2d()
```

Auch das Lochbild wird nur einmal berechnet:

```scad
stitch_hole_positions_left()
```

Dadurch stimmen folgende Teile geometrisch überein:

- TPU-Sohlenkontur
- Klebe-/Nährand
- Strobelsohle aus Textil
- umlaufender Anschlussring
- Lochmarkierungen
- Ballen-Flexmarkierung
- linke/rechte Spiegelung

Änderst du beispielsweise `foot_length`, `toe_box_width`, `waist_width`, `edge_allowance`, `rim_width` oder `stitch_hole_spacing`, werden Sohle und Schnittschnittstelle gemeinsam aktualisiert.

## Wichtige Ausgaben

### TPU-Sohle

```scad
output_part = "sole_only";
```

### Alle Schnittteile

```scad
output_part = "pattern_all";
pattern_style = "textile_shoe";
```

oder:

```scad
output_part = "pattern_all";
pattern_style = "sock_shoe";
```

### Exakte textile Strobelsohle

```scad
output_part = "pattern_strobel_board";
```

Das ist eine vollflächige textile Bodenschablone. Mit `pattern_strobel_inset = 0` besitzt sie exakt dieselbe Außenkontur wie die Sohle; für einen etwas kleineren Einsatz kann später ein positiver Inset-Wert gewählt werden.

### Exakter umlaufender Anschlussring

```scad
output_part = "pattern_lasting_band";
```

Der Ring ist besonders praktisch, wenn du den Oberschuh zuerst an einen Stoffring nähst und diesen anschließend auf den TPU-Klebe-/Nährand setzt.

### Kontrollüberlagerung

```scad
output_part = "pattern_interface_overlay";
```

Sie zeigt:

- Sohlenaußenkante
- Innenkante des Befestigungsrandes
- Nählöcher
- Ballen-Flexlinie

Damit kannst du nach dem Export prüfen, ob Druck- und Schnittdatei mit 100 % Maßstab übereinstimmen.

## Empfohlene Konstruktion

### Textilschuh

1. `pattern_all` exportieren.
2. Testschaft aus billigem Vlies oder Mesh nähen.
3. Schaft an `pattern_lasting_band` oder `pattern_strobel_board` nähen.
4. Die textile Schnittstelle anhand der Löcher auf der TPU-Sohle ausrichten.
5. Flexibel verkleben und anschließend vernähen.

### Sockenschuh

Für einen elastischen Schaft ist die vollflächige Strobelsohle meist sinnvoller. Sie stabilisiert die Unterseite und verhindert, dass der Stoff zwischen den Klebepunkten hochgezogen wird.

## Was wirklich exakt ist – und was angenähert bleibt

**Exakt gemeinsam abgeleitet:**

- Sohlenkontur
- Anschlussring
- Strobelsohle
- Lochpositionen
- Befestigungsrand
- Ballenmarkierung

**Aus Umfangsmaßen angenähert:**

- Spannhöhe
- Vampvolumen
- Fersenform
- Kragenform
- dreidimensionale Wölbung des Textils

Ein flaches Schnittmuster kann die 3D-Fußform ohne Leisten oder Fußscan nicht vollständig exakt entfalten. Deshalb zuerst einen Testschaft nähen. Die Verbindung zur Sohle bleibt dabei dennoch maßgleich.

## Export

Für Schnittmuster:

1. `output_part` auswählen.
2. F6 rendern.
3. Als SVG oder DXF exportieren.
4. Mit 100 % Skalierung drucken.
5. Eine Kontrollstrecke nachmessen, etwa `foot_length + toe_clearance`.

Für TPU:

1. `output_part = "sole_only"`.
2. F6 rendern.
3. Als STL oder 3MF exportieren.

## Sinnvolle Startwerte

Nicht elastisches Mesh oder Ripstop:

```scad
pattern_stretch_reduction = 0.00;
pattern_fit_ease = 5;
```

Elastisches Sport-Mesh:

```scad
pattern_stretch_reduction = 0.05;
pattern_fit_ease = 3;
```

Der Anschlussring sollte nicht verkleinert werden; nur die oberen Schaftteile erhalten die Stretchreduktion.
