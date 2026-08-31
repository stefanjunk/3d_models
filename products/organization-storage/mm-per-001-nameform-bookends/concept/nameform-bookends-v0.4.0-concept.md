# NameForm 0.4.0 concept review

Status: `PENDING HUMAN APPROVAL`

Asset: `nameform-bookends-v0.4.0-concept.png`

SHA-256: `14e21a1e86c3a2f1fa28ef2939c9fd0987a3434713476126039911bf8dfa57bc`

This Gate 0B image communicates the approved 0.4.0 appearance and architecture.
It is not dimensional evidence, production CAD, a strength result, or proof of
printability.

## Correspondence to the approved requirements

| Concept feature | Approved requirement |
|---|---|
| Large `STE` and `FAN` bodies define the front silhouette | Letter-dominant facade; no rectangular front wing |
| Narrow but readable gaps and open counters | 1.8 mm nominal spacing with at least 1.2 mm finished gap |
| Irregular wood relief is visible on the letter fronts | Candidate C on glyph fronts, direct full-master sampling, 0.6 mm depth, 0.45 mm grid |
| Flat local rear tabs join adjacent glyphs | 2.4 mm connector web beginning 6.0 mm behind the glyph front |
| Rear and section views show no full backplate | Connector only holds the letters; counters and negative space stay open |
| Side blades and inward feet remain behind/beside the names | Retained 0.3.0 functional book load path, visually subordinate from the front |

## Deliberate simplifications and ambiguity

- The generated image does not encode millimetres. Exact 122 mm cap height,
  6.0/2.4 mm depth hierarchy, and 1.8/1.2 mm gap limits remain controlled by
  `design-spec.yaml` and later CAD assertions.
- The small flat bridges are drawn slightly lighter and more visible than the
  final target so their construction can be reviewed. Production CAD must push
  them to the 6 mm setback and pass the straight-front visibility gate.
- The pictured grain is an appearance proxy. Production geometry must reuse
  candidate C's registered 16-bit source, physical period, seam blend, phase,
  relief depth, and direct-sampling path rather than extracting relief from this
  render.
- The exposed glyph flanks are conceptual. Their shallower relief remains
  subject to the planned glyph/connector coupon and gap keep-outs.
- The image shows the default `STE | FAN` configuration only. Other names must
  pass font, width, bridge-connectivity, and gap sweeps separately.

## Generation route and final prompt summary

Built-in Imagegen was used in edit mode with the 0.3.0 wood-textured pair as the
reference target. The final focused edit preserved the three-view sheet,
lettering, wood-textured fronts, side blades, feet, lighting, and proportions
while replacing round connector rods with thin flat local rear tabs/web. The
prompt explicitly prohibited a plaque, full back panel, counter filling,
merged glyph fronts, smooth letter fronts, extra text, logos, and watermarks.
