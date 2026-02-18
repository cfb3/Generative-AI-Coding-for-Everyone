"""Ball entity – the core simulation object.

No pygame dependency.  The Ball knows its physical state and can apply
forces / update its position, but it does not know how to draw itself.
"""

from __future__ import annotations

import math
import random

from skunk.physics.vector2d import Vector2D
from skunk.constants import (
    MIN_RADIUS,
    MAX_RADIUS,
    MIN_SPEED,
    MAX_SPEED,
    MASS_DENSITY,
    PLAY_AREA_HEIGHT,
    WINDOW_WIDTH,
    MAX_SPEED_CAP,
)


class Ball:
    """A circular body with position, velocity, radius, and derived mass.

    Parameters
    ----------
    position : Vector2D
        Centre of the ball in screen coordinates.
    velocity : Vector2D
        Current velocity in px/frame.
    radius : float
        Radius in pixels.
    color : tuple[int, int, int]
        RGB fill colour.
    """

    __slots__ = ("position", "velocity", "radius", "mass", "color")

    def __init__(
        self,
        position: Vector2D,
        velocity: Vector2D,
        radius: float,
        color: tuple[int, int, int],
    ) -> None:
        self.position = position
        self.velocity = velocity
        self.radius = float(radius)
        self.mass: float = MASS_DENSITY * math.pi * self.radius * self.radius
        self.color = color

    # --- derived properties ---

    @property
    def speed(self) -> float:
        """Scalar speed (magnitude of velocity)."""
        return self.velocity.magnitude

    @property
    def kinetic_energy(self) -> float:
        """½ m v² – useful for the energy display."""
        return 0.5 * self.mass * self.velocity.magnitude_sq

    @property
    def momentum(self) -> Vector2D:
        """Momentum vector m·v."""
        return self.velocity * self.mass

    # --- mutation helpers ---

    def update_position(self) -> None:
        """Advance the ball by one frame of its current velocity."""
        self.position = self.position + self.velocity

    def apply_impulse(self, impulse: Vector2D) -> None:
        """Add an instantaneous change in velocity."""
        self.velocity = self.velocity + impulse

    def clamp_speed(self, max_speed: float = MAX_SPEED_CAP) -> None:
        """Ensure the ball doesn't exceed *max_speed*."""
        self.velocity = self.velocity.clamped(max_speed)

    def handle_wall_bounce(
        self, width: int = WINDOW_WIDTH, height: int = PLAY_AREA_HEIGHT
    ) -> bool:
        """Bounce off the play-area edges.  Return True if the left wall was hit.

        Parameters
        ----------
        width : int
            Right boundary in pixels.
        height : int
            Bottom boundary in pixels (excludes status bar).

        Returns
        -------
        bool
            True when the ball bounced off the **left** wall (caller may
            apply a boost).
        """
        hit_left = False
        px, py = self.position.x, self.position.y
        vx, vy = self.velocity.x, self.velocity.y

        if px - self.radius <= 0 and vx < 0:
            vx = -vx
            px = self.radius
            hit_left = True
        elif px + self.radius >= width and vx > 0:
            vx = -vx
            px = width - self.radius

        if py - self.radius <= 0 and vy < 0:
            vy = -vy
            py = self.radius
        elif py + self.radius >= height and vy > 0:
            vy = -vy
            py = height - self.radius

        self.position = Vector2D(px, py)
        self.velocity = Vector2D(vx, vy)
        return hit_left

    def handle_wall_bounce_gravity(
        self, width: int = WINDOW_WIDTH, height: int = PLAY_AREA_HEIGHT
    ) -> tuple[bool, bool]:
        """Wall bounce variant for gravity mode.

        Returns
        -------
        (hit_left, hit_floor)
            Flags so the caller can apply boost / restitution.
        """
        hit_left = False
        hit_floor = False
        px, py = self.position.x, self.position.y
        vx, vy = self.velocity.x, self.velocity.y

        if px - self.radius <= 0 and vx < 0:
            vx = -vx
            px = self.radius
            hit_left = True
        elif px + self.radius >= width and vx > 0:
            vx = -vx
            px = width - self.radius

        if py - self.radius <= 0 and vy < 0:
            vy = -vy
            py = self.radius
        elif py + self.radius >= height and vy > 0:
            vy = -vy
            py = height - self.radius
            hit_floor = True

        self.position = Vector2D(px, py)
        self.velocity = Vector2D(vx, vy)
        return hit_left, hit_floor

    @property
    def is_on_floor(self) -> bool:
        """True when the ball is resting on (or very near) the floor."""
        return self.position.y + self.radius >= PLAY_AREA_HEIGHT - 1

    # --- factory ---

    @classmethod
    def create_random(
        cls,
        position: Vector2D,
        color: tuple[int, int, int],
        velocity: Vector2D | None = None,
    ) -> Ball:
        """Create a ball with random radius and velocity direction.

        Parameters
        ----------
        position : Vector2D
            Spawn location.
        color : tuple
            RGB colour.
        velocity : Vector2D | None
            If provided, use this exact velocity (e.g. from slingshot).
            Otherwise pick a random direction and speed.
        """
        radius = random.uniform(MIN_RADIUS, MAX_RADIUS)
        if velocity is None:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(MIN_SPEED, MAX_SPEED)
            velocity = Vector2D.from_angle(angle, speed)
        return cls(position, velocity, radius, color)

    def __repr__(self) -> str:
        return (
            f"Ball(pos={self.position}, vel={self.velocity}, "
            f"r={self.radius:.1f}, m={self.mass:.1f})"
        )
