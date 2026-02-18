"""Force and impulse calculations for the simulation.

Every function is a pure computation – accepts values, returns values.
No state mutation, no pygame.
"""

from __future__ import annotations

import math

from skunk.physics.vector2d import Vector2D
from skunk.constants import (
    SURFACE_FRICTION,
    GRAVITY_ACCEL,
    BOUNCE_RESTITUTION,
    FLOOR_FRICTION,
    AIR_RESISTANCE,
    LEFT_WALL_BOOST,
    MAX_SPEED_CAP,
    SHOCKWAVE_STRENGTH,
    SHOCKWAVE_RADIUS,
)


def apply_surface_friction(velocity: Vector2D, mass: float) -> Vector2D:
    """Apply surface friction in no-gravity mode.

    Heavier objects have slightly more friction (they press harder on the
    surface).  The model: ``v_new = v * SURFACE_FRICTION ^ (mass_factor)``
    where ``mass_factor = sqrt(mass)`` gives a noticeable but not extreme
    difference between light and heavy balls.

    Parameters
    ----------
    velocity : Vector2D
        Current velocity.
    mass : float
        Ball mass (> 0).

    Returns
    -------
    Vector2D
        Velocity after one frame of friction.
    """
    factor = SURFACE_FRICTION ** math.sqrt(mass)
    return velocity * factor


def apply_gravity(velocity: Vector2D) -> Vector2D:
    """Add one frame of gravitational acceleration (downward).

    Parameters
    ----------
    velocity : Vector2D
        Current velocity.

    Returns
    -------
    Vector2D
        Velocity with gravity applied.
    """
    return velocity + Vector2D(0.0, GRAVITY_ACCEL)


def apply_air_resistance(velocity: Vector2D) -> Vector2D:
    """Apply a small drag factor to limit runaway speed in gravity mode.

    Parameters
    ----------
    velocity : Vector2D
        Current velocity.

    Returns
    -------
    Vector2D
        Velocity after air drag.
    """
    return velocity * AIR_RESISTANCE


def apply_floor_friction(velocity: Vector2D) -> Vector2D:
    """Apply floor friction to the horizontal component while rolling.

    Only the x-component is damped; the y-component is untouched so that
    normal bouncing isn't affected.

    Parameters
    ----------
    velocity : Vector2D
        Current velocity (ball must be on the floor).

    Returns
    -------
    Vector2D
        Velocity with horizontal friction applied.
    """
    return Vector2D(velocity.x * FLOOR_FRICTION, velocity.y)


def apply_bounce_restitution(velocity: Vector2D) -> Vector2D:
    """Reduce the vertical component after a ground bounce.

    Parameters
    ----------
    velocity : Vector2D
        Velocity immediately after the y-component has been flipped.

    Returns
    -------
    Vector2D
        Velocity with reduced vertical energy.
    """
    return Vector2D(velocity.x, velocity.y * BOUNCE_RESTITUTION)


def compute_wall_boost(velocity: Vector2D) -> Vector2D:
    """Compute velocity after a left-wall boost.

    The x-component is multiplied by ``LEFT_WALL_BOOST`` but the total
    speed is capped at ``MAX_SPEED_CAP`` so that repeated bounces
    don't produce infinite speed.

    Parameters
    ----------
    velocity : Vector2D
        Velocity right after the wall bounce (vx should already be positive).

    Returns
    -------
    Vector2D
        Boosted and capped velocity.
    """
    # Don't boost if already at or above the cap.
    if velocity.magnitude >= MAX_SPEED_CAP:
        return velocity.clamped(MAX_SPEED_CAP)
    boosted = Vector2D(velocity.x * LEFT_WALL_BOOST, velocity.y)
    return boosted.clamped(MAX_SPEED_CAP)


def compute_shockwave_impulse(
    ball_pos: Vector2D,
    shockwave_origin: Vector2D,
) -> Vector2D:
    """Compute the impulse vector a shockwave applies to a ball.

    Force is proportional to ``1 / distance`` (capped at a minimum
    distance of 1 px to avoid division by zero) and directed radially
    outward from the shockwave origin.  Balls beyond ``SHOCKWAVE_RADIUS``
    receive zero impulse.

    Parameters
    ----------
    ball_pos : Vector2D
        Centre of the ball.
    shockwave_origin : Vector2D
        Where the user triggered the shockwave.

    Returns
    -------
    Vector2D
        Impulse to add to the ball's velocity.
    """
    delta = ball_pos - shockwave_origin
    dist = delta.magnitude
    if dist > SHOCKWAVE_RADIUS:
        return Vector2D(0.0, 0.0)
    safe_dist = max(dist, 1.0)
    strength = SHOCKWAVE_STRENGTH / safe_dist
    return delta.normalized() * strength
