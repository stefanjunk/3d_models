# V6.2 Freeform-Upper – Konzeptprüfung Draft 3

Status: `APPROVED`

Anforderungen freigegeben durch Stefan am 2026-08-28 mit `freigegeben`.

Konzept freigegeben durch Stefan am 2026-08-28 mit `freigegebene`.

Spezifikationsrevision: `6.2.0-draft.3`

Konzeptbild: `previews/concept-v6.2.0-draft.3.png`

SHA-256: `cfc1678a8f7eb647946e2ac5366718310cdc0ad7b42a7cf51a5ef9f48aa5c1ca`

## Zuordnung zu den freigegebenen Korrekturen

- Die große Dreiviertelansicht zeigt einen vollständig geschlossenen
  Zehenabschluss ohne Tunnel, U-Ausschnitt oder dunkle Innenöffnung.
- Die kleine Stirnansicht zeigt einen geschlossenen Fersenabschluss unterhalb
  der unveränderten Kragenöffnung.
- In der Seitenansicht fällt die Upper-Scheitellinie ab der vorderen
  Kragenkante ruhig zum Vorderfuß ab und bildet keinen zweiten Hochpunkt über
  dem Kragen.
- Breite Zehenbox, Außenplanform, Kragenöffnung, dezentes Kragenband und die
  glatte nicht-voxelartige Formensprache bleiben erhalten.

## Bewusste Grenzen

- Das Bild ist eine KI-gestützte Formvisualisierung und keine maßhaltige
  CAD-Prüfung.
- Die AI-Darstellung vereinfacht die V6.1-Sohlen-/Lippen-Trennlinie. Deren
  exakte Kontur wird im CAD nicht aus dem Bild abgeleitet, sondern bleibt über
  den bestehenden PCHIP-Schnittstellenvertrag geschützt.
- Zielöffnung `0,0 mm`, Endwand mindestens `1,4 mm`, Blendelänge `8,0 mm` und
  Centerline-Grenze `z <= 52,25 mm` bleiben ausschließlich in
  `design-spec.yaml` maßgeblich.
- Mesh-Topologie, Selbstschnittfreiheit, Endwand, Krümmungsfairness und die
  tatsächliche Volumenreduktion müssen nach Konzeptfreigabe deterministisch am
  Produktionsmodell geprüft werden.

## Erzeugungsnachweis

Modus: eingebautes `image_gen`, präzise Objektbearbeitung der aktuellen
Draft-2-Dreiviertel-, Seiten- und Heckansichten.

Kernanweisung:

> Close the visible tunnel/U-shaped aperture at both the toe end and heel end.
> Lower the midfoot/vamp ridge directly in front of the collar so the upper
> centerline never rises above the front collar height and descends in one calm
> continuous sweep. Preserve the collar, broad toe box, sole interface, outer
> plan silhouette, total length and smooth non-voxel freeform character.
