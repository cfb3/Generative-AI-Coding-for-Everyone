"""Physics subpackage – pure math, no pygame dependency."""

from skunk.physics.vector2d import Vector2D
from skunk.physics.collision import detect_collision, resolve_collision
from skunk.physics.forces import (
    apply_surface_friction,
    apply_gravity,
    apply_air_resistance,
    apply_floor_friction,
    compute_wall_boost,
    compute_shockwave_impulse,
)

__all__ = [
    "Vector2D",
    "detect_collision",
    "resolve_collision",
    "apply_surface_friction",
    "apply_gravity",
    "apply_air_resistance",
    "apply_floor_friction",
    "compute_wall_boost",
    "compute_shockwave_impulse",
]
