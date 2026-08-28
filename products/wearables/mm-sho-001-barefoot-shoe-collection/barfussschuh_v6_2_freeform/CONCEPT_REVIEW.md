# V6.2 Freeform-Upper – Konzeptprüfung

Status: `SUPERSEDED_BY_DRAFT_2_PROPOSAL`

Freigegeben durch Stefan am 2026-08-27.

Die digitale Draft-1-Umsetzung zeigte trotz des freigegebenen Formkonzepts nur
1,2 mm Materialreserve zwischen hinterer Öffnungsgrenze und Fersenabschluss.
Das erzeugte zwei spitze Kragenübergänge. Revision 6.2.0-draft.2 schlägt deshalb
eine etwa 15,2 mm große Fersenreserve bei praktisch unveränderter vorderer
Öffnungsgrenze vor. Die frühere Konzeptfreigabe ist dadurch formal ungültig.

Spezifikationsrevision: `6.2.0-draft.1`

Konzeptbild: `previews/concept-v6.2.0-draft.1.png`

SHA-256: `8838882cce73526bc0fc5104993d3a8988de7ae5a59f824131d573171ea1f8b5`

## Zuordnung zu den freigegebenen Anforderungen

- Die große Dreiviertelansicht zeigt eine vollständig geschlossene, glatte
  Freeform-Haut ohne Voxel-, Loch- oder Facettenstruktur.
- Die Draufsicht zeigt die breite Zehenbox und die großzügige Slip-on-Öffnung.
- Die Detailansicht zeigt das leichte, umlaufende Kragenband mit gerundeter
  freier Kante und tangential weichem Übergang in das Upper.
- Sohlensilhouette, Toe Rocker, Seitenwaben und Upper-Sohlen-Anschluss bleiben
  visuell auf dem V6/V6.1-Konzeptstand.

## Bewusste Vereinfachungen und Grenzen

- Das Bild ist ein KI-erzeugtes Formkonzept, keine maßhaltige CAD- oder
  Wandstärkenprüfung.
- Die freigegebenen 5,0 mm Bandbreite, 2,6 mm lokale Zielwand und ungefähr
  1,0 mm Kantenradius stehen ausschließlich in `design-spec.yaml`.
- Die exakte Öffnungsweite, Krümmung, Sohlenpassung und TPU-Flexibilität werden
  erst in der parametrischen Geometrie und am Coupon geprüft.
- Das Konzept legt weder Slicerpfade noch die spätere Fuzzy-/Infill-Oberfläche
  fest; es definiert die glatte geometrische Grundhülle.

## Erzeugungsnachweis

Modus: eingebautes `image_gen`, präzise Objektbearbeitung mit dem vorhandenen
Barfußschuh-Konzeptbild als Formreferenz.

Prompt:

> Using the existing black barefoot-shoe image as the design reference, create
> a landscape industrial-design concept sheet for the same low, wide-toe,
> zero-drop slip-on. Replace only the porous upper with a fully closed, smooth,
> softly flowing matte-black TPU freeform upper. Remove voxel, honeycomb, hole,
> perforation, ripple and faceted artifacts from the upper. Add a subtle
> continuous comfort band around the opening, visually about 5 mm wide,
> slightly thicker than the skin, with a rounded bullnose free edge and smooth
> tangent transitions. Show a large three-quarter view, a top view and a collar
> close-up. Preserve outsole silhouette, toe rocker, sole/lip geometry and
> sole-only honeycomb texture. Keep the opening generous. No labels, logos,
> feet, laces, fabric, pores, vents, sharp rim or bulky padding.
