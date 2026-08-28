# Decomposition

| Component | Source of truth | Quantity | Interface |
|---|---|---:|---|
| Smooth carrier | `model-parameters.json` | 6 | 1.6 mm upper front edge enters cap |
| Engraved cap | parameters + normalized CSV + grid glyphs | 6 unique | 1.9 mm U-slot, left/center/right offset |
| Slot gauge | parameters | 1 optional | 1.8/1.9/2.0 mm candidate slots |
| Carrier fit key | parameters | 1 optional | exact 1.6 mm carrier thickness |
| Windowed carrier | parameters | optimization-only | same cap interface; not selected |
| Batch importer | CSV + glyph normalizer | digital tool | normalized JSON and hash report |
| Nesting layout | parameters + batch JSON | digital tool | 14 non-overlapping objects |

No purchased component or external font/mesh/vector asset is embedded. The customer supplies records, qualified outer sleeves and shelf/box.
