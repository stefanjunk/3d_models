# Gate 0A — requirements review

Status: approved for corrective implementation `MM-ORG-003 · 2.0.0-draft.2`; the 2026-09-05 owner review keeps the original product intent and rejects draft.1's implementation.

The MVP launch trio already has controlled parametric 3MF candidates. Its remaining work is physical/slicer qualification, which the user explicitly deferred. Portfolio priority therefore moves to the first geometry-changing P1 item: a smaller common-printer derivative of PORT-004.

| Area | Decision | Source |
|---|---|---|
| Product | Compact two-drawer organizer with removable six-bin sorter | inferred from PORT-004 and v1.1.2 |
| Envelope | 210 × 193.2 × 173 mm assembled, including 3.2 mm proud fascia | corrected measured envelope for 220 mm printers |
| Parts | housing, two identical drawers, removable sorter, two coupons | recommended |
| Printer | 220 × 220 × 250 mm, 0.4 mm nozzle, 0.20 mm layers | recommended common-printer contract |
| Material | ordinary PLA / supplier-specific Tough PLA, indoor | recommended |
| Texture | 3.2 mm directional tow cue, 0.80 mm wide × 0.24 mm deep; 2.4/3.2/4.0 mm vertical coupon | owner correction plus surface-texture representation ladder |
| Optimization | protected thin shells/ribs; no global dense relief or lossy decimation | recommended |
| Risk | normal-functional; no load rating | inferred and bounded |
| Validation | deterministic source/geometry/3MF checks now; physical print/fit/appearance later | user-stated |

Open assumptions remain parameterized instead of being hidden: exact contents, printer/material profile and measured clearances. They do not block a digital draft because the model includes fit and texture coupons and does not claim physical qualification.
