#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

out="exports/DRAFT/STL"
logs="exports/DRAFT/logs"
mkdir -p "$out" "$logs"

parts=(
  camera_fork_fit_coupon
  camera_fit_frame_coupon
  camera_ball_test_pin
  camera_ball_socket_coupon
  camera_2020_slider_fork
  camera_short_socket_arm
  camera_front_shell
  camera_back_cover_ball
  camera_window_inner_bezel
  camera_window_outer_wedge
  camera_window_clamp_frame
  led_profile_clip_17x8
  roof_cassette_corner_locator
  exhaust_camera_baffle_120
  corner_gusset_3way
  flat_t_bracket
  panel_retainer_clip
  turn_clip
  turn_clip_spacer
  service_panel_120_ports
  fan_adapter_120_to_100
  fan_guard_120
  cable_grommet_half_A
  cable_grommet_half_B
)

for part in "${parts[@]}"; do
  openscad \
    -o "$out/DRAFT_${part}.stl" \
    -D "PART=\"${part}\"" \
    kobra3max_enclosure.scad \
    >"$logs/${part}.log" 2>&1
  printf '%s\n' "$part"
done

mkdir -p "preview/DRAFT"
ALSOFT_DRIVERS=null blender -b \
  --python render_complete_enclosure_blender.py \
  -- --output "preview/DRAFT/kobra3max_enclosure_complete.png" \
  >"$logs/complete_preview.log" 2>&1
printf '%s\n' "complete_preview"
