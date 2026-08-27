#!/usr/bin/env bash
set -euo pipefail

# One-time, fail-closed migration to the self-contained product layout.
# Run from the repository root. Existing destinations are never overwritten.

move_path() {
  local source_path="$1"
  local destination_path="$2"

  if [[ ! -e "$source_path" ]]; then
    printf 'missing source: %s\n' "$source_path" >&2
    exit 1
  fi
  if [[ -e "$destination_path" ]]; then
    printf 'destination already exists: %s\n' "$destination_path" >&2
    exit 1
  fi

  mkdir -p "$(dirname "$destination_path")"
  mv -- "$source_path" "$destination_path"
}

copy_file() {
  local source_path="$1"
  local destination_path="$2"

  if [[ ! -f "$source_path" ]]; then
    printf 'missing file to copy: %s\n' "$source_path" >&2
    exit 1
  fi
  if [[ -e "$destination_path" ]]; then
    printf 'copy destination already exists: %s\n' "$destination_path" >&2
    exit 1
  fi

  mkdir -p "$(dirname "$destination_path")"
  cp -a -- "$source_path" "$destination_path"
}

make_system_product() {
  local index="$1"
  local product_slug="$2"
  local artifact_slug="$3"
  local destination="products/furniture-systems/$product_slug"

  if [[ -e "$destination" ]]; then
    printf 'system-product destination already exists: %s\n' "$destination" >&2
    exit 1
  fi

  mkdir -p "$destination/exports/step" "$destination/exports/stl" "$destination/previews"
  cp -a -- systemmoebel_top20_cad/config "$destination/config"
  cp -a -- systemmoebel_top20_cad/systemmoebel_top20 "$destination/systemmoebel_top20"
  cp -a -- systemmoebel_top20_cad/reports "$destination/reports"
  cp -a -- \
    systemmoebel_top20_cad/BOM.md \
    systemmoebel_top20_cad/FIT-AND-TEST.md \
    systemmoebel_top20_cad/PRINTING.md \
    systemmoebel_top20_cad/README.md \
    systemmoebel_top20_cad/design-spec.yaml \
    systemmoebel_top20_cad/generate.py \
    systemmoebel_top20_cad/render_previews.py \
    systemmoebel_top20_cad/requirements.txt \
    systemmoebel_top20_cad/validate_group.py \
    "$destination/"
  cp -a -- "systemmoebel_top20_cad/exports/step/${artifact_slug}.step" "$destination/exports/step/"
  cp -a -- "systemmoebel_top20_cad/exports/stl/${artifact_slug}.stl" "$destination/exports/stl/"
  cp -a -- "systemmoebel_top20_cad/previews/${artifact_slug}.png" "$destination/previews/"

  printf '%02d %s\n' "$index" "$destination"
}

mkdir -p \
  products/organization-storage \
  products/printer-workshop \
  products/home-kitchen-garden \
  products/toys-games \
  products/art-decor \
  products/wearables \
  products/furniture-systems \
  research/third-party \
  research/concepts \
  archive/local-tool-state \
  archive/legacy-suites

# Organization and storage products.
move_path organizer/drawer-inlay products/organization-storage/mm-org-001-drawerfit-modular
move_path organizer/nameform-bookends products/organization-storage/mm-per-001-nameform-bookends
move_path organizer/shelffit-mini-bins products/organization-storage/mm-org-002-shelffit-mini-bins
move_path organizer/desk-drawer products/organization-storage/mm-org-003-modern-carbon-desk-organizer
move_path organizer/bathroom/premium-parametric-over-toilet-shelf products/organization-storage/mm-bth-001-premium-over-toilet-shelf
move_path organizer/bathroom/toilettpaper_stand products/organization-storage/mm-bth-002-toilet-paper-fifo-system
mkdir -p products/organization-storage/mm-bth-002-toilet-paper-fifo-system/history
move_path organizer/bathroom/ZEN_KINTSUGI_WAVE_FIFO_5R_v2.1.0_DRAFT_REVIEW_LITE products/organization-storage/mm-bth-002-toilet-paper-fifo-system/history/zen-kintsugi-v2.1.0-draft-review-lite
move_path organizer/bathroom/ZEN_KINTSUGI_WAVE_FIFO_5R_v2.1.0_DRAFT_REVIEW_LITE.zip products/organization-storage/mm-bth-002-toilet-paper-fifo-system/history/zen-kintsugi-v2.1.0-draft-review-lite.zip
move_path organizer/nozzle-box products/printer-workshop/mm-mkr-001-cybervault-nozzle-case
move_path walls products/organization-storage/mm-wall-001-honeycomb-wood-wall-shelf
move_path organizer/external research/third-party/organization-storage

# Printer and workshop products.
move_path 3d-printing_addons/Kobra3Max_Gehaeuse_CAD_v1 products/printer-workshop/mm-tool-001-kobra3max-enclosure
move_path 3d-printing_addons/filament_box products/printer-workshop/mm-tool-002-filament-drybox-system
move_path camera_mount products/printer-workshop/mm-tool-003-kobra3max-camera-arm
move_path claw_hammer products/printer-workshop/mm-tool-004-claw-hammer-mesh
move_path mouse_jiggler products/printer-workshop/unregistered-magnetic-mouse-jiggler

move_path 3d-printing_addons/Anycubic-Kobra-3-Max-Poop-Bin-metriMade-R1 products/printer-workshop/unregistered-kobra3max-poop-bin
move_path 3d-printing_addons/Anycubic-Kobra-3-Max-Poop-Bin-metriMade-R1.zip products/printer-workshop/unregistered-kobra3max-poop-bin/legacy-package-r1.zip

mkdir -p products/printer-workshop/unregistered-kobra3max-purge-catcher/history
move_path 3d-printing_addons/Anycubic-Kobra-3-Max-Purge-Catcher-metriMade-R5 products/printer-workshop/unregistered-kobra3max-purge-catcher/current
move_path 3d-printing_addons/Anycubic-Kobra-3-Max-Purge-Catcher-metriMade-R5.zip products/printer-workshop/unregistered-kobra3max-purge-catcher/current-package-r5.zip
move_path 3d-printing_addons/Anycubic-Kobra-3-Max-Purge-Catcher-metriMade-R2 products/printer-workshop/unregistered-kobra3max-purge-catcher/history/r2
move_path 3d-printing_addons/Anycubic-Kobra-3-Max-Purge-Catcher-metriMade-R2.zip products/printer-workshop/unregistered-kobra3max-purge-catcher/history/r2.zip
move_path 3d-printing_addons/Anycubic-Kobra-3-Max-Purge-Catcher-metriMade-R3 products/printer-workshop/unregistered-kobra3max-purge-catcher/history/r3
move_path 3d-printing_addons/Anycubic-Kobra-3-Max-Purge-Catcher-metriMade-R3.zip products/printer-workshop/unregistered-kobra3max-purge-catcher/history/r3.zip
move_path 3d-printing_addons/Anycubic-Kobra-3-Max-Purge-Catcher-metriMade-R4 products/printer-workshop/unregistered-kobra3max-purge-catcher/history/r4
move_path 3d-printing_addons/Anycubic-Kobra-3-Max-Purge-Catcher-metriMade-R4.zip products/printer-workshop/unregistered-kobra3max-purge-catcher/history/r4.zip

mkdir -p products/printer-workshop/unregistered-kobra3max-fan-cage/history
move_path 3d-printing_addons/Anycubic_Kobra_3_Max_Metrimade_Fan_Cage_R1 products/printer-workshop/unregistered-kobra3max-fan-cage/current
move_path '3d-printing_addons/Anycubic_Kobra_3_Max_Metrimade_Fan_Cage_R1 (1)' products/printer-workshop/unregistered-kobra3max-fan-cage/history/import-copy-1

for destination in \
  products/printer-workshop/mm-tool-001-kobra3max-enclosure \
  products/printer-workshop/mm-tool-002-filament-drybox-system \
  products/printer-workshop/mm-tool-003-kobra3max-camera-arm \
  products/printer-workshop/unregistered-kobra3max-poop-bin \
  products/printer-workshop/unregistered-kobra3max-purge-catcher \
  products/printer-workshop/unregistered-kobra3max-fan-cage
do
  mkdir -p "$destination/profiles/imported"
  cp -a -- '3d-printing_addons/Anycubic Kobra 3 Max 0.4 hardened steel nozzle.anycubic_printer' "$destination/profiles/imported/"
  cp -a -- '3d-printing_addons/Anycubic Kobra 3 Max 0.4 hardened steel.anycubic_printer' "$destination/profiles/imported/"
  for source_path in 3d-printing_addons/*.anycubic_filament 3d-printing_addons/*presets.zip; do
    if [[ -e "$source_path" ]]; then
      cp -a -- "$source_path" "$destination/profiles/imported/"
    fi
  done
done

move_path 3d-printing_addons/AnycubicSlicerNext archive/local-tool-state/anycubic-slicer-next
move_path 3d-printing_addons/external research/third-party/printer-workshop
move_path '3d-printing_addons/Anycubic Kobra 3 Max 0.4 hardened steel nozzle.anycubic_printer' archive/local-tool-state/anycubic-kobra3max-hardened-nozzle-profile.anycubic_printer
move_path '3d-printing_addons/Anycubic Kobra 3 Max 0.4 hardened steel.anycubic_printer' archive/local-tool-state/anycubic-kobra3max-hardened-profile.anycubic_printer
mkdir -p archive/local-tool-state/anycubic-presets
for source_path in 3d-printing_addons/*.anycubic_filament 3d-printing_addons/*presets.zip; do
  if [[ -e "$source_path" ]]; then
    move_path "$source_path" "archive/local-tool-state/anycubic-presets/$(basename "$source_path")"
  fi
done
move_path 3d-printing_addons/Kobra3Max_Gehaeuse_CAD_v1.zip products/printer-workshop/mm-tool-001-kobra3max-enclosure/legacy-package-v1.zip
move_path '3d-printing_addons/Anycubic_Kobra_3_Max_Metrimade_Fan_Cage_R1.zip' products/printer-workshop/unregistered-kobra3max-fan-cage/current-package-r1.zip
move_path '3d-printing_addons/Anycubic_Kobra_3_Max_Metrimade_Fan_Cage_R1 (1).zip' products/printer-workshop/unregistered-kobra3max-fan-cage/history/import-copy-1.zip
mkdir -p products/printer-workshop/unregistered-kobra3max-fan-cage/current/imported-root-exports
move_path 3d-printing_addons/printhead_cover_fit_frame_D52.stl products/printer-workshop/unregistered-kobra3max-fan-cage/current/imported-root-exports/printhead_cover_fit_frame_D52.stl
move_path 3d-printing_addons/printhead_cover_metrimade_D52_multicolor.3mf products/printer-workshop/unregistered-kobra3max-fan-cage/current/imported-root-exports/printhead_cover_metrimade_D52_multicolor.3mf
move_path 3d-printing_addons/printhead_cover_singlecolor_D52.stl products/printer-workshop/unregistered-kobra3max-fan-cage/current/imported-root-exports/printhead_cover_singlecolor_D52.stl

# Home, kitchen, and garden products.
move_path cup products/home-kitchen-garden/mm-home-001-cup-and-measuring-spoon
move_path garden products/home-kitchen-garden/mm-gar-001-rainwater-filter-well
move_path bowls products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray
move_path household products/home-kitchen-garden/unregistered-shower-drain-hairtrap
move_path deco/duftspender products/home-kitchen-garden/unregistered-aroma-diffuser

# Toys and games.
move_path blasters products/toys-games/mm-toy-001-rubber-ball-toy-popper
move_path boats/fisher_boat products/toys-games/mm-boat-001-fisher-boat
move_path boats/fisher_boat_detailed products/toys-games/mm-boat-002-fisher-boat-detailed
move_path boats/flapping_submarine products/toys-games/mm-boat-003-flapping-tail-submarine
move_path boats/rocket_boat products/toys-games/mm-boat-004-rocket-boat
move_path boats/toy_boat products/toys-games/mm-boat-005-toy-boat
move_path boats/duck_boat products/toys-games/unregistered-duck-boat
move_path boats/external research/third-party/boats
move_path dice_tower products/toys-games/mm-hob-001-polygonal-dice-tower
move_path puzzles/parametric_labyrinth_gift_box products/toys-games/mm-puz-001-parametric-labyrinth-gift-box
move_path puzzles/puzzle-box products/toys-games/mm-puz-002-mystery-puzzle-box
move_path puzzles/external research/third-party/puzzles
mkdir -p research/concepts/puzzles
for source_path in puzzles/*.png; do
  if [[ -e "$source_path" ]]; then
    move_path "$source_path" "research/concepts/puzzles/$(basename "$source_path")"
  fi
done

# Decorative and mesh products.
move_path Fox products/art-decor/mm-art-001-fox-mesh-collection
move_path Opel_Grandland_2018 products/art-decor/mm-auto-001-opel-grandland-2018-mesh
move_path Plants products/art-decor/mm-art-002-plant-mesh
move_path Unicorn products/art-decor/mm-art-003-unicorn-mesh-collection
move_path art/marble_tile products/art-decor/mm-dec-001-marble-tile
move_path art/roman_pillar products/art-decor/mm-dec-002-roman-pillar
move_path art/external_models research/third-party/art-models
move_path capybara products/art-decor/mm-art-004-capybara-mesh-collection
move_path fish products/art-decor/mm-art-005-fish-mesh-collection
move_path mouse products/art-decor/mm-art-006-mouse-mesh-collection
move_path racehorse products/art-decor/mm-art-007-racehorse-mesh-collection
move_path sportscar products/art-decor/mm-art-008-sports-car-mesh
move_path whale products/art-decor/mm-art-009-whale-mesh-collection

# Wearables.
move_path accessoires/honeycomb-hair-clip-r6-final\(1\) products/wearables/mm-acc-001-honeycomb-hair-clip
move_path 'accessoires/honeycomb-hair-clip-r6-final(1).zip' products/wearables/mm-acc-001-honeycomb-hair-clip/legacy-package-r6.zip
move_path barefoot products/wearables/mm-sho-001-barefoot-shoe-collection

# Third-party-only collections are research inputs, not products.
move_path clips research/third-party/clips
move_path dough_cutter research/third-party/dough-cutters
move_path fidgets research/third-party/fidgets
move_path gravity_knife research/third-party/gravity-knife-fidgets
move_path music research/third-party/music-boxes
move_path shoes research/third-party/shoes
move_path stamps research/third-party/stamps

# Split the legacy system-furniture suite into self-contained SKU folders.
move_path systemmoebel_top20_cad/products/alex-inventory-workplace-tray-v0.2.0 products/furniture-systems/mm-sys-001-alex-inventory-workplace-tray
move_path systemmoebel_top20_cad/products/bror-tool-shadow-tray-v0.2.0 products/furniture-systems/mm-sys-002-bror-tool-shadow-tray
make_system_product 3 mm-sys-003-pax-asymmetric-accessory-grid 03_pax_asymmetric_accessory_grid
make_system_product 4 mm-sys-004-billy-collection-riser 04_billy_collection_riser
make_system_product 5 mm-sys-005-bror-shadow-board-workflow-cluster 05_bror_shadow_board_workflow_cluster
make_system_product 6 mm-sys-006-kallax-boardgame-matrix 06_kallax_boardgame_matrix
make_system_product 7 mm-sys-007-platsa-collection-cells 07_platsa_collection_cells
make_system_product 8 mm-sys-008-skadis-precision-tool-cluster 08_skadis_workflow_cluster
make_system_product 9 mm-sys-009-besta-passive-media-topology 09_besta_media_topology
make_system_product 10 mm-sys-010-omar-ventilated-shelf-deck 10_omar_shelf_deck
make_system_product 11 mm-sys-011-boaxel-cleaning-accessory-dock 11_boaxel_light_cleaning_docking_rail
make_system_product 12 mm-sys-012-besta-controller-and-media-tray 12_besta_controller_media_drawer_tray
make_system_product 13 mm-sys-013-trofast-adult-workshop-insert 13_trofast_adult_workshop_insert
make_system_product 14 mm-sys-014-kallax-creative-material-cassette 14_kallax_creative_material_cassette
make_system_product 15 mm-sys-015-boaxel-basket-microsorter 15_boaxel_basket_microsorter
make_system_product 16 mm-sys-016-malm-fold-size-drawer-dividers 16_malm_fold_size_dividers
make_system_product 17 mm-sys-017-ivar-no-drill-side-inventory-rail 17_ivar_no_drill_side_inventory_rail
make_system_product 18 mm-sys-018-billy-collection-display-matrix 18_billy_collection_display_matrix
make_system_product 19 mm-sys-019-lagkapten-alex-reversible-cable-rail 19_lagkapten_alex_reversible_cable_rail
make_system_product 20 mm-sys-020-lack-leg-two-pocket-mini-dock 20_lack_leg_two_pocket_mini_dock
move_path systemmoebel_top20_cad archive/legacy-suites/systemmoebel-top20-cad

# Repository infrastructure.
move_path market_research research/market
move_path metrimade-watermark tools/metrimade-watermark
if [[ -e JuSt-Innovation-Wasserzeichen-JSI-WM-001-R1.zip ]]; then
  move_path JuSt-Innovation-Wasserzeichen-JSI-WM-001-R1.zip tools/metrimade-watermark/releases/legacy/JuSt-Innovation-Wasserzeichen-JSI-WM-001-R1.zip
fi

# Remove legacy grouping directories only when they are empty.
rmdir -- 3d-printing_addons
rmdir -- accessoires
rmdir -- art
rmdir -- boats
rmdir -- deco
rmdir -- organizer/bathroom
rmdir -- organizer
rmdir -- puzzles

printf 'product restructuring completed\n'
