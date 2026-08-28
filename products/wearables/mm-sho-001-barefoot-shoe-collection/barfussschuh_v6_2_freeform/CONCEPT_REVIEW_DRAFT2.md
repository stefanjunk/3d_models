# V6.2 Freeform-Upper – Konzeptprüfung Draft 2

Status: `APPROVED`

Anforderungen freigegeben durch Stefan am 2026-08-28.

Konzept freigegeben durch Stefan am 2026-08-28 mit der ausdrücklichen
Chat-Bestätigung `yes, approved`.

Spezifikationsrevision: `6.2.0-draft.2`

Konzeptbild: `previews/concept-v6.2.0-draft.2.png`

SHA-256: `18d2643250238dd3f82bf6527fe6eec787b1870fdffa8fb1d0da26124c960ca7`

## Zuordnung zur Draft-2-Komfortkorrektur

- Die hintere Öffnungsgrenze liegt weiter vorn, sodass zwischen Öffnung und
  äußerem Fersenabschluss eine etwa 15,2 mm lange Materialreserve vorgesehen
  werden kann.
- Der Fersenanstieg verteilt sich über 10 % der Schuhlänge und läuft ohne die
  zwei Spitzen des verworfenen Draft-1-CAD-Modells aus.
- Vorderkante und ungefähre Breite der Öffnung bleiben erhalten.
- Das ungefähr 5,0 mm breite Kragenband läuft geschlossen um die Öffnung, ist
  nur leicht stärker als die Upper-Haut und besitzt eine weich gerundete freie
  Kante.
- Die geschlossene Upper-Haut bleibt glatt, freiformig und ohne Voxel-,
  Waben-, Loch- oder Facettenstruktur.
- Breite Zehenbox, Toe Rocker, Sohlensilhouette, Lippengeometrie und die nur an
  der Sohle gezeigte Wabenstruktur bleiben auf dem V6/V6.1-Konzeptstand.

## Bewusste Grenzen

- Das Bild ist ein KI-erzeugtes Formkonzept und keine maßhaltige CAD-Prüfung.
- Öffnungszentrum `20,6 %`, Längsradius `40,0 mm`, Bandbreite `5,0 mm`, lokale
  Zielwand `2,6 mm` und Zielradius der freien Kante `ungefähr 1,0 mm` sind in
  `design-spec.yaml` und `parameters.yaml` festgelegt.
- Die tatsächliche Fersenreserve, Öffnungsweite, Tangentialität, Wandstärke,
  Sohlenpassung und TPU-Flexibilität müssen nach der Konzeptfreigabe
  deterministisch am CAD-Modell und am Coupon geprüft werden.
- Druckfreigabe, Slicerprofil, Materialverträglichkeit und Tragekomfort bleiben
  bis zu den jeweiligen digitalen und physischen Nachweisen gesperrt.

## Erzeugungsnachweis

Modus: eingebautes `image_gen`, präzise Objektbearbeitung des
Draft-1-Konzeptbilds.

Prompt:

> Edit Image 1 only in the collar and rear-upper geometry. Move the rear
> boundary of the foot opening clearly forward so the shoe retains a smooth
> continuous heel counter with approximately 15 mm of longitudinal material
> reserve between the opening and the exterior heel end. Redistribute the heel
> rise over a longer gentle sweep. Make the opening boundary one continuous
> rounded curve with no peaks, ears, notches, corners, cusps or spikes. Keep a
> subtle continuous comfort band around the entire opening, visually about
> 5 mm wide, only slightly thicker than the upper skin, with a softly rounded
> bullnose free edge and tangent transitions; it must look flexible and
> skin-friendly, never bulky or padded. Preserve the clean concept-sheet
> layout with a large three-quarter view, top view and collar close-up. Keep
> the front opening boundary, generous width, broad toe box, toe rocker,
> outsole/lip geometry, sole-only honeycomb and matte-black material unchanged.
> No text, labels, logos, feet, laces, upper pores or holes, voxel artifacts,
> facets, ripples, sharp rim, pointed rear peaks or bulky cushioning.
