#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p STL
parts=(rail_286 rail_143 rail_test_coupon rail_splice_pin rail_end_stop corner_gusset_3way flat_t_bracket base_anchor turn_clip turn_clip_spacer panel_knob panel_retainer_clip front_panel_shelf service_panel_120_ports service_panel_blank fan_adapter_120_to_100 fan_guard_120 cable_grommet_half_A cable_grommet_half_B)
for part in "${parts[@]}"; do
  openscad -o "STL/${part}.stl" -D "PART=\"${part}\"" kobra3max_enclosure.scad >/tmp/openscad_${part}.log 2>&1
  echo "$part"
done
