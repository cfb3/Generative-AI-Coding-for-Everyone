"""Immutable 2-D vector used throughout the physics and model layers.

Design notes
------------
* Immutable (frozen dataclass) so vectors can be keys, cached, etc.
* Every arithmetic method returns a *new* Vector2D – no mutation.
* Zero pygame dependency – pure math.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Vector2D:
    """A two-component vector for positions, velocities, and forces.

    Parameters
    ----------
    x : float
        Horizontal component (positive → right).
    y : float
        Vertical component (positive → down, matching screen coords).
    """

    x: float = 0.0
    y: float = 0.0

    # --- arithmetic ---

    def __add__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector2D:
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vector2D:
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Vector2D:
        return Vector2D(self.x / scalar, self.y / scalar)

    def __neg__(self) -> Vector2D:
        return Vector2D(-self.x, -self.y)

    # --- geometric helpers ---

    @property
    def magnitude(self) -> float:
        """Euclidean length of the vector."""
        return math.hypot(self.x, self.y)

    @property
    def magnitude_sq(self) -> float:
        """Squared length – avoids a sqrt when only comparison is needed."""
        return self.x * self.x + self.y * self.y

    def normalized(self) -> Vector2D:
        """Return a unit vector in the same direction.

        Returns the zero vector if this vector has zero magnitude.
        """
        mag = self.magnitude
        if mag == 0:
            return Vector2D(0.0, 0.0)
        return Vector2D(self.x / mag, self.y / mag)

    def dot(self, other: Vector2D) -> float:
        """Dot product with *other*."""
        return self.x * other.x + self.y * other.y

    def angle_rad(self) -> float:
        """Angle in radians measured counter-clockwise from the +x axis."""
        return math.atan2(self.y, self.x)

    def angle_deg(self) -> float:
        """Angle in degrees measured counter-clockwise from the +x axis."""
        return math.degrees(self.angle_rad())

    def distance_to(self, other: Vector2D) -> float:
        """Euclidean distance to *other*."""
        return (self - other).magnitude

    def distance_sq_to(self, other: Vector2D) -> float:
        """Squared distance – avoids sqrt."""
        return (self - other).magnitude_sq

    @staticmethod
    def from_angle(angle_rad: float, magnitude: float = 1.0) -> Vector2D:
        """Create a vector from an angle (radians) and magnitude."""
        return Vector2D(math.cos(angle_rad) * magnitude,
                        math.sin(angle_rad) * magnitude)

    def clamped(self, max_magnitude: float) -> Vector2D:
        """Return this vector capped at *max_magnitude* length."""
        if self.magnitude_sq <= max_magnitude * max_magnitude:
            return self
        return self.normalized() * max_magnitude

    def __repr__(self) -> str:
        return f"Vector2D({self.x:.3f}, {self.y:.3f})"
