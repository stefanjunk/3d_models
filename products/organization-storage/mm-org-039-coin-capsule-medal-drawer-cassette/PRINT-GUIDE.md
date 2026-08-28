# Print guide

1. Use only protective capsules containing sacrificial, inert, or low-value contents during validation. Do not place a bare coin or medal against printed PLA. Measure actual capsule outer width/diameter and height with calipers; do not rely only on the advertised coin diameter.
2. Print `exports/3mf/DRAFT-MM-ORG-039-fit-label-and-mark-gauges-0.1.0-draft.1.3mf` first. It contains the exact three-interface gauge, one square adapter, one round adapter, and separate R2 Full and Micro identity coupons.
3. Test the measured `67 x 67 mm` large square target, `50 x 50 x 6.25 mm` square target, and `46 mm` round target only in their matching openings. A capsule must enter under gravity or light fingertip pressure and leave without levering, wedging, haze, stress marks, or edge bites. Reject the complete kit if any intended capsule fails.
4. Test a `34 x 7.5 mm` paper label in each adapter bay. It must insert and lift without tearing, curling, transfer marks, or contact with a bare collectible. Check that the Full and Micro coupons print completely and remain readable.
5. Cycle a sacrificial protective capsule through the selected adapter 100 times under strong oblique-light inspection. Then seat and lift the adapter repeatedly in one host-cell position. Stop if either part scratches, wedges, rocks excessively, cracks, or delaminates.
6. Choose one complete package: `exports/3mf/DRAFT-MM-ORG-039-collectorgrid-square-50-kit-0.1.0-draft.1.3mf` or `exports/3mf/DRAFT-MM-ORG-039-collectorgrid-round-46-kit-0.1.0-draft.1.3mf`. Both contain one host and six matching adapters. The validated orientation is base-down with generated support disabled.
7. Before printing, inspect the final layer preview for first-layer placement, perimeter continuity, open-lattice rails, bridges, seams, tool assignment, and clear access notches. Use the named Kobra 3 Max machine/process profiles and the supplied `slicer-profiles/MM-ORG-039 Conservative Anycubic PLA 12.8.json` filament profile, or independently revalidate any changed setup.
8. After cooling, load six encapsulated inert weights matching the intended masses. Confirm every capsule lifts through its front notch, the host remains flat, the drawer clears the loaded height, and rails/walls survive 100 drawer cycles plus 20 removal/replacement cycles per position.
9. Inspect every capsule-contact edge, adapter, label bay, host rail, and identity recess. Stop use if an edge is sharp, cracked, visibly abrasive, or delaminated. Keep the PLA product below `40 °C` and outside child-use contexts.

Exact conservative-PLA planning evidence:

- Fit, label, and mark gauges: `5,998 s` (`1 h 39 min 58 s`), approximately `41.0 g`, G-code SHA-256 `52b592b6ecf0d6ff8297281aa49f12289d827d6454d9f95d02e17af42f387f4d`.
- Square-50 six-adapter kit: `14,934 s` (`4 h 08 min 54 s`), approximately `109.5 g`, G-code SHA-256 `4bcfa3c77354ce4cb5586aa47e77f8cfb086f9d70f124f724a1f9dcebf9947bf`.
- Round-46 six-adapter kit: `16,383 s` (`4 h 33 min 03 s`), approximately `120.2 g`, G-code SHA-256 `60277eeec412b61a70b703b082f87e7ef81a54c1e40b40dfa5cc5a4ae8242c72`.

Supplied G-code is local validation evidence for the named Anycubic Kobra 3 Max, process, and conservative PLA profiles. It is not authorization to upload or start a printer.
