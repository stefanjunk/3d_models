"""Model groups. Each module owns five numbered product concepts."""

from .group_a import build as build_group_a
from .group_b import build as build_group_b
from .group_c import build as build_group_c
from .group_d import build as build_group_d

__all__ = ["build_group_a", "build_group_b", "build_group_c", "build_group_d"]
