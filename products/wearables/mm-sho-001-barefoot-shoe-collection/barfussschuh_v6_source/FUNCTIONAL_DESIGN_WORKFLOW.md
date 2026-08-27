# Functional Design Workflow – V6

## Anforderungen

- barfußnahe Nullsprengung
- breite Zehenbox
- organische moderne Schuhform statt extrudierter Platte
- geschwungene Laufseite mit Toe Rocker
- flexible Ballenzone
- TPU-Lippe über dem Schaftrand
- Waben-Design als funktionales Profil und Seitenrelief
- textile und vollständig gedruckte Oberteiloption
- weiche/atmungsaktive Upper-Variante
- reproduzierbare Parametrik und deterministische Mesh-Validierung

## Dekomposition

| Komponente | Funktion | Fertigung |
|---|---|---|
| Organic sole body | Lastübertragung, Flex, Rocker | TPU, normaler Solid-Druck |
| Curved lip | Schaftschutz, Design, Klebe-/Nähschutz | TPU, mit Sohle gruppiert |
| Hex tread | Grip + Design | TPU, gleiche Assembly |
| Side hex wrap | visuelle Kontinuität | TPU, gleiche Assembly |
| Infill envelope | weicher offener Upper | nur Slicer-Infill |
| Fuzzy shell | geschlossener flexibler Upper | dünne TPU-Haut |
| Reinforcement frame | Ferse/Kragen/Sohlenanschluss | normale Wände |

## Geometrische Invarianten

- Ferse zu Ballen: praktisch 0-Drop
- Textil-/Upper-Überdeckung durch Lippe >= 2 mm
- Hex-Rippenbreite > typische 0,4-mm-Linienbreite
- Flexkerben werden vom Tread nicht geschlossen
- Upper und Frame nutzen dieselbe parametrische Last-/Sohlenreferenz
- linke/rechte Variante nur durch Spiegelung

## Validierungsstufen

1. CadQuery BREP Validity
2. STL Watertightness
3. Connected-component count
4. 3MF component naming
5. Nullsprengungs-Check
6. Lochabstand
7. Testcoupon Infill-only
8. Testcoupon Lippenüberdeckung
9. Slicer-Layer-Preview
10. mechanischer Handtest vor Tragen

## Druckversuche vor dem vollständigen Schuh

1. Infill-only Coupon in 3 Dichten drucken: 15 / 20 / 25 %.
2. Fuzzy-Wandstreifen mit drei Ripple-Amplituden drucken.
3. Lippen-Coupon mit dem vorgesehenen Textil oder Upper-Material verkleben/nähen.
4. Ballen-Flexbereich mindestens mehrfach stark von Hand biegen.
5. Wabenprofil auf glattem und rauem Boden testen.

## Manuelle Freigabe

Ein vollständiger Schuh sollte erst nach den Coupons und einer kontrollierten Slicer-Vorschau gedruckt werden. Das Modell ist ein technischer Prototyp, keine medizinische Orthese.
