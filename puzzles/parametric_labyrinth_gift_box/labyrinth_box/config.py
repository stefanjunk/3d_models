"""User-facing parameters for the labyrinth gift box."""

from dataclasses import dataclass
from typing import Literal


MazeLocation = Literal["inner", "outer"]


@dataclass(frozen=True, slots=True)
class BoxConfig:
    """All dimensions are millimeters and describe finished-model geometry."""

    cavity_diameter: float = 40.0
    cavity_length: float = 80.0
    difficulty: int = 5
    maze_location: MazeLocation = "inner"
    seed: int = 20260805

    inner_wall: float = 3.2
    outer_wall: float = 3.2
    bottom_thickness: float = 2.4
    cap_thickness: float = 2.4
    radial_clearance: float = 0.35
    axial_clearance: float = 0.5

    channel_width: float = 2.0
    channel_depth: float = 1.2
    follower_clearance: float = 0.25
    follower_tip_clearance: float = 0.2
    maze_margin: float = 4.0

    minimum_wall: float = 1.6
    minimum_web: float = 1.2
    minimum_feature: float = 0.8

    angular_facets: int = 96
    stl_tolerance: float = 0.08
    stl_angular_tolerance: float = 0.15
