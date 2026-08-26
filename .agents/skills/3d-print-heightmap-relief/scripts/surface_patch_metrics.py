#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math


def cylinder(args):
    theta = args.width_mm / args.radius_mm
    return {
        "surface": "cylinder",
        "radius_mm": args.radius_mm,
        "desired_arc_width_mm": args.width_mm,
        "angular_span_rad": theta,
        "angular_span_deg": math.degrees(theta),
        "full_circumference_mm": 2 * math.pi * args.radius_mm,
        "rule": "Map image X by arc length s=R*theta, not raw degrees.",
    }


def rounded_rect(args):
    w, d, r = args.width_mm, args.depth_mm, args.corner_radius_mm
    if r < 0 or 2*r > min(w, d):
        raise ValueError("corner radius must satisfy 0 <= 2r <= min(width, depth)")
    straight = 2 * (w - 2*r) + 2 * (d - 2*r)
    arcs = 2 * math.pi * r
    return {
        "surface": "rounded-rectangle perimeter",
        "width_mm": w,
        "depth_mm": d,
        "corner_radius_mm": r,
        "straight_length_mm": straight,
        "corner_arc_length_total_mm": arcs,
        "perimeter_mm": straight + arcs,
        "rule": "Use accumulated perimeter distance in millimetres across flats and fillet arcs.",
    }


def sphere(args):
    phi = math.radians(args.latitude_deg)
    lon_scale = args.radius_mm * abs(math.cos(phi))
    lat_scale = args.radius_mm
    result = {
        "surface": "sphere",
        "radius_mm": args.radius_mm,
        "latitude_deg": args.latitude_deg,
        "mm_per_radian_longitude_local": lon_scale,
        "mm_per_radian_latitude": lat_scale,
        "longitude_scale_relative_to_equator": abs(math.cos(phi)),
        "rule": "Longitude metric shrinks by cos(latitude); keep recognizable subjects away from poles.",
    }
    if args.width_mm is not None:
        if lon_scale < 1e-9:
            result["width_warning"] = "Longitude scale is near zero at the pole; do not place a recognizable patch here."
        else:
            result["approx_longitude_span_deg_for_width"] = math.degrees(args.width_mm / lon_scale)
    if args.height_mm is not None:
        result["approx_latitude_span_deg_for_height"] = math.degrees(args.height_mm / lat_scale)
    return result


def ellipsoid(args):
    a,b,c = args.a_mm,args.b_mm,args.c_mm
    lam = math.radians(args.longitude_deg)
    phi = math.radians(args.latitude_deg)
    dlam = (-a*math.cos(phi)*math.sin(lam), b*math.cos(phi)*math.cos(lam), 0.0)
    dphi = (-a*math.sin(phi)*math.cos(lam), -b*math.sin(phi)*math.sin(lam), c*math.cos(phi))
    norm_lam = math.sqrt(sum(v*v for v in dlam))
    norm_phi = math.sqrt(sum(v*v for v in dphi))
    dot = sum(x*y for x,y in zip(dlam,dphi))
    cos_angle = dot/(norm_lam*norm_phi) if norm_lam*norm_phi else 0.0
    result = {
        "surface": "ellipsoid",
        "semi_axes_mm": [a,b,c],
        "longitude_deg": args.longitude_deg,
        "latitude_deg": args.latitude_deg,
        "mm_per_radian_u_local": norm_lam,
        "mm_per_radian_v_local": norm_phi,
        "local_parameter_axis_cosine": cos_angle,
        "local_parameter_axis_angle_deg": math.degrees(math.acos(max(-1.0,min(1.0,cos_angle)))) if norm_lam*norm_phi else None,
        "rule": "Ellipsoid UV scale and orthogonality vary with position; use a bounded patch and verify real surface lengths.",
    }
    if args.width_mm is not None and norm_lam > 1e-9:
        result["approx_u_span_deg_for_width"] = math.degrees(args.width_mm/norm_lam)
    if args.height_mm is not None and norm_phi > 1e-9:
        result["approx_v_span_deg_for_height"] = math.degrees(args.height_mm/norm_phi)
    return result


def main() -> int:
    p = argparse.ArgumentParser(description="Compute physical mapping metrics for common curved surfaces.")
    sub = p.add_subparsers(dest="surface", required=True)
    q=sub.add_parser("cylinder"); q.add_argument("--radius-mm",type=float,required=True); q.add_argument("--width-mm",type=float,required=True); q.set_defaults(func=cylinder)
    q=sub.add_parser("rounded-rect"); q.add_argument("--width-mm",type=float,required=True); q.add_argument("--depth-mm",type=float,required=True); q.add_argument("--corner-radius-mm",type=float,required=True); q.set_defaults(func=rounded_rect)
    q=sub.add_parser("sphere"); q.add_argument("--radius-mm",type=float,required=True); q.add_argument("--latitude-deg",type=float,default=0.0); q.add_argument("--width-mm",type=float); q.add_argument("--height-mm",type=float); q.set_defaults(func=sphere)
    q=sub.add_parser("ellipsoid"); q.add_argument("--a-mm",type=float,required=True); q.add_argument("--b-mm",type=float,required=True); q.add_argument("--c-mm",type=float,required=True); q.add_argument("--longitude-deg",type=float,default=0.0); q.add_argument("--latitude-deg",type=float,default=0.0); q.add_argument("--width-mm",type=float); q.add_argument("--height-mm",type=float); q.set_defaults(func=ellipsoid)
    args=p.parse_args()
    result=args.func(args)
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
