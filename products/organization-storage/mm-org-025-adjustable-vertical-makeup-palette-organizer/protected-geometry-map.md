# Protected geometry map

| Geometry | Authority | Protected relation |
|---|---|---|
| Grid positions | `base.slot_count`, `base.slot_pitch_mm` | 16 stations, 11.5 mm pitch, centered |
| Production slot | `base.slot_width_mm`, `base.slot_length_mm` | 2.9 × 10.0 mm through both full-height rails |
| Divider tongue | divider thickness and foot length | 2.4 × 9.4 mm section, 8.0 mm insertion depth |
| Nominal clearance | slot minus tongue | 0.5 mm across thickness; 0.6 mm along tongue |
| Coupon series | `coupon.candidate_slot_widths_mm` | 2.7/2.9/3.1 mm brackets production |
| Default layout | `divider.default_slot_indices` | 0/2/4/6/8/11/15 |
| Retrieval margin | clear lane minus supported thickness | minimum 1.0 mm |
| Portfolio envelope | retained SKU-007 row | no more than 225 × 110 × 135 mm |

Do not decimate or remesh protected slots, tongues, rail top faces, or palette-contact frame edges. Regenerate from parameters after any interface change.
