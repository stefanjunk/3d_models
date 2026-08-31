# Product preflight and purpose audit — 2026-08-31

## Outcome

- Products audited: **108**
- Explicit `PURPOSE.md` documents: **108**
- Retrospective preflight document sets: **108**
- Older/legacy entries moved into product-local `archive/`: **42**
- Roots requiring human review because of pre-existing dirty or ambiguous content: **3**

Every preflight is a current retrospective assessment of repository evidence,
not a reconstruction of the state before design began. A `HOLD` is an explicit
result, not a validation failure of the document.

## Root review exceptions

- `home-kitchen-garden/mm-bth-003-linear-shower-drain-hair-trap`: The older v1_3 tree remains outside archive because all_panels.3mf had a pre-existing local modification; moving it would mix unrelated user content into this commit.
- `printer-workshop/unregistered-kobra3max-fan-cage`: The root contains an untracked R1 import plus current and redesign-v2 work. Their ownership/currentness is ambiguous, so no active or untracked content was moved.
- `wearables/mm-sho-001-barefoot-shoe-collection`: The root contains a pre-existing untracked 90 MiB duplicate named barfussschuh_v6_1_fitfix (2); the v6.1 pair was left in place to avoid absorbing user-owned binary content.

## Archive move verification

- None.

## Product scorecards

| Product | Complexity | Readiness | Criticality | Lane | Release | Root status |
|---|---:|---:|---:|---:|---|---|
| `art-decor/mm-art-001-fox-mesh-collection` | C0 (13.0) | R1 | K0 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `art-decor/mm-art-002-plant-mesh` | C0 (13.0) | R1 | K0 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `art-decor/mm-art-003-unicorn-mesh-collection` | C0 (13.0) | R1 | K0 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `art-decor/mm-art-004-capybara-mesh-collection` | C0 (13.0) | R1 | K0 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `art-decor/mm-art-005-fish-mesh-collection` | C0 (13.0) | R1 | K0 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `art-decor/mm-art-006-mouse-mesh-collection` | C0 (13.0) | R1 | K0 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `art-decor/mm-art-007-racehorse-mesh-collection` | C0 (13.0) | R2 | K0 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `art-decor/mm-art-008-sports-car-mesh` | C0 (13.0) | R1 | K0 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `art-decor/mm-art-009-whale-mesh-collection` | C0 (13.0) | R1 | K0 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `art-decor/mm-art-010-modular-city-map-wall-panel` | C2 (31.5) | R0 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `art-decor/mm-art-011-modular-topographic-relief-wall-panel` | C2 (31.5) | R0 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `art-decor/mm-auto-001-opel-grandland-2018-mesh` | C1 (15.5) | R1 | K0 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `art-decor/mm-dec-001-marble-tile` | C2 (37.5) | R1 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `art-decor/mm-dec-002-roman-pillar` | C3 (42.8) | R1 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-001-alex-inventory-workplace-tray` | C2 (39.0) | R1 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-002-bror-tool-shadow-tray` | C2 (39.0) | R1 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-003-pax-asymmetric-accessory-grid` | C3 (40.0) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-004-billy-collection-riser` | C3 (40.0) | R2 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-005-bror-shadow-board-workflow-cluster` | C3 (49.2) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-006-kallax-boardgame-matrix` | C3 (40.0) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-007-platsa-collection-cells` | C3 (40.0) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-008-skadis-precision-tool-cluster` | C3 (49.2) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-009-besta-passive-media-topology` | C3 (40.0) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-010-omar-ventilated-shelf-deck` | C3 (40.0) | R2 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-011-boaxel-cleaning-accessory-dock` | C3 (40.0) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-012-besta-controller-and-media-tray` | C3 (40.0) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-013-trofast-adult-workshop-insert` | C3 (40.0) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-014-kallax-creative-material-cassette` | C3 (40.0) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-015-boaxel-basket-microsorter` | C3 (40.0) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-016-malm-fold-size-drawer-dividers` | C3 (40.0) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-017-ivar-no-drill-side-inventory-rail` | C3 (40.0) | R2 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-018-billy-collection-display-matrix` | C3 (40.0) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-019-lagkapten-alex-reversible-cable-rail` | C3 (40.0) | R2 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `furniture-systems/mm-sys-020-lack-leg-two-pocket-mini-dock` | C3 (40.0) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `home-kitchen-garden/mm-bth-003-linear-shower-drain-hair-trap` | C3 (44.2) | R2 | K2 | E | HOLD | REVIEW_REQUIRED |
| `home-kitchen-garden/mm-dec-003-sunflower-bowl-tray` | C3 (44.5) | R1 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `home-kitchen-garden/mm-gar-001-rainwater-filter-well` | C2 (38.5) | R2 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `home-kitchen-garden/mm-home-001-cup-and-measuring-spoon` | C2 (26.0) | R1 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `home-kitchen-garden/unregistered-aroma-diffuser` | C2 (39.2) | R0 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `home-kitchen-garden/unregistered-shower-drain-hairtrap` | C2 (39.2) | R0 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-bth-001-premium-over-toilet-shelf` | C3 (42.2) | R2 | K3 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-bth-002-toilet-paper-fifo-system` | C3 (42.2) | R2 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-001-drawerfit-modular` | C3 (42.5) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-002-shelffit-mini-bins` | C2 (37.2) | R2 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-003-modern-carbon-desk-organizer` | C3 (42.5) | R1 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-004-modular-desktop-tray-system` | C2 (34.8) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-005-desk-edge-cable-clip-kit` | C2 (34.8) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-006-charging-cable-docking-bar` | C3 (42.5) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-007-adjustable-passive-phone-stand` | C3 (47.2) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-008-custom-lipstick-tube-grid` | C2 (34.8) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-009-tapered-drawer-perimeter-filler-rail-set` | C2 (37.2) | R2 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-010-personalized-pen-stationery-caddy` | C2 (34.8) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-011-crochet-hook-diameter-rack` | C2 (34.8) | R2 | K1 | C | GO_WITH_CONTROLS | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-012-stationery-refill-inventory-tray` | C2 (34.8) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-013-photo-postcard-archive-drawer-divider` | C2 (37.2) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-014-embroidery-floss-project-palette-dock` | C2 (34.8) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-015-adapter-dongle-drawer-cassette` | C2 (34.8) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-016-stencil-ruler-bookmark-set` | C2 (34.8) | R2 | K1 | C | GO_WITH_CONTROLS | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-017-modular-pocket-emptying-tray` | C2 (34.8) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-018-drawer-measurement-gauge-kit` | C2 (37.2) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-019-label-tape-cartridge-rack` | C2 (34.8) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-020-belt-scarf-shelf-comb` | C2 (37.2) | R2 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-021-eyeglass-case-shelf-corral` | C2 (37.2) | R1 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-022-labelable-small-parts-bin-set` | C2 (34.8) | R1 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-023-page-holder-thumb-tool` | C3 (41.0) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-024-deep-shelf-pull-tab-bin-front` | C2 (37.2) | R2 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-025-adjustable-vertical-makeup-palette-organizer` | C3 (40.0) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-026-personalized-desk-nameplate` | C3 (46.5) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-027-vinyl-record-divider-label-set` | C2 (39.8) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-028-craft-stamp-die-index-rack` | C2 (37.2) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-029-craft-night-modular-personal-supply-caddy` | C2 (37.2) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-030-irregular-corner-drawer-organizer-infill` | C2 (34.8) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-031-pageharbor-shelf-side-ereader-book-dock` | C2 (37.2) | R2 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-032-pairpin-thread-bobbin-rack` | C2 (34.8) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-033-diamond-painting-tray-staging-rack` | C2 (34.8) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-034-snap-on-journal-pen-loop` | C3 (47.2) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-035-stamp-and-ink-pad-desk-organizer` | C2 (37.2) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-036-deep-drawer-height-riser-platform` | C2 (37.2) | R2 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-037-sewing-bobbin-presser-foot-drawer-cassette` | C3 (43.5) | R1 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-038-milestone-photo-card-desk-display-block` | C2 (37.2) | R1 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-org-039-coin-capsule-medal-drawer-cassette` | C2 (37.2) | R1 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-per-001-nameform-bookends` | C3 (41.25) | R3 | K1 | C | GO_WITH_CONTROLS | CLEAN_OR_NO_VERSION_CONFLICT |
| `organization-storage/mm-wall-001-honeycomb-wood-wall-shelf` | C2 (39.8) | R2 | K3 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `printer-workshop/mm-mkr-001-cybervault-nozzle-case` | C3 (54.2) | R2 | K1 | C | GO_WITH_CONTROLS | CLEAN_OR_NO_VERSION_CONFLICT |
| `printer-workshop/mm-tool-001-kobra3max-enclosure` | C4 (61.0) | R2 | K3 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `printer-workshop/mm-tool-002-filament-drybox-system` | C4 (61.8) | R1 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `printer-workshop/mm-tool-003-kobra3max-camera-arm` | C3 (56.0) | R1 | K3 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `printer-workshop/mm-tool-004-claw-hammer-mesh` | C3 (57.8) | R1 | K0 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `printer-workshop/unregistered-kobra3max-fan-cage` | C4 (64.2) | R2 | K3 | E | HOLD | REVIEW_REQUIRED |
| `printer-workshop/unregistered-kobra3max-poop-bin` | C3 (54.2) | R0 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `printer-workshop/unregistered-kobra3max-purge-catcher` | C3 (56.8) | R2 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `printer-workshop/unregistered-magnetic-mouse-jiggler` | C3 (59.2) | R0 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `toys-games/mm-boat-001-fisher-boat` | C3 (49.2) | R1 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `toys-games/mm-boat-002-fisher-boat-detailed` | C3 (49.2) | R1 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `toys-games/mm-boat-003-flapping-tail-submarine` | C3 (57.5) | R2 | K3 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `toys-games/mm-boat-004-rocket-boat` | C3 (47.5) | R1 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `toys-games/mm-boat-005-toy-boat` | C3 (49.2) | R1 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `toys-games/mm-drn-001-openquad-cf5-fpv-quadcopter` | C3 (52.5) | R0 | K3 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `toys-games/mm-hob-001-polygonal-dice-tower` | C3 (46.5) | R2 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `toys-games/mm-puz-001-parametric-labyrinth-gift-box` | C3 (44.0) | R1 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `toys-games/mm-puz-002-mystery-puzzle-box` | C3 (44.0) | R2 | K1 | C | GO_WITH_CONTROLS | CLEAN_OR_NO_VERSION_CONFLICT |
| `toys-games/mm-rov-001-tethys-mini-rov` | C3 (56.8) | R0 | K3 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `toys-games/mm-toy-001-rubber-ball-toy-popper` | C3 (52.8) | R1 | K3 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `toys-games/mm-toy-002-trailcam-cf10-rc-camera-rover` | C3 (52.5) | R2 | K3 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `toys-games/mm-toy-003-trailcam-b2-balance-rover` | C3 (59.2) | R2 | K3 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `toys-games/unregistered-duck-boat` | C3 (44.0) | R0 | K1 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `wearables/mm-acc-001-honeycomb-hair-clip` | C5 (83.0) | R2 | K2 | E | HOLD | CLEAN_OR_NO_VERSION_CONFLICT |
| `wearables/mm-sho-001-barefoot-shoe-collection` | C5 (85.5) | R2 | K3 | E | HOLD | REVIEW_REQUIRED |
