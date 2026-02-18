"""Collision detection and resolution for circular bodies.

All functions are pure – they accept positions, velocities, radii, and
masses as arguments and return new velocities/positions.  No side effects,
no pygame, fully testable in isolation.
"""

from __future__ import annotations

from skunk.physics.vector2d import Vector2D


def detect_collision(
    pos_a: Vector2D,
    radius_a: float,
    pos_b: Vector2D,
    radius_b: float,
) -> bool:
    """Return True when two circles overlap (distance < sum of radii).

    Parameters
    ----------
    pos_a, pos_b : Vector2D
        Centre positions of the two circles.
    radius_a, radius_b : float
        Radii of the two circles.
    """
    min_dist = radius_a + radius_b
    return pos_a.distance_sq_to(pos_b) < min_dist * min_dist


def resolve_collision(
    pos_a: Vector2D,
    vel_a: Vector2D,
    mass_a: float,
    radius_a: float,
    pos_b: Vector2D,
    vel_b: Vector2D,
    mass_b: float,
    radius_b: float,
) -> tuple[Vector2D, Vector2D, Vector2D, Vector2D]:
    """Compute post-collision velocities and separated positions.

    Uses the standard 2-D elastic collision formula so that momentum and
    kinetic energy are both conserved.  Also pushes the two circles apart
    along the collision normal so they no longer overlap (prevents the
    "stuck together" bug).

    Parameters
    ----------
    pos_a, pos_b : Vector2D
        Pre-collision centre positions.
    vel_a, vel_b : Vector2D
        Pre-collision velocities.
    mass_a, mass_b : float
        Masses (> 0).
    radius_a, radius_b : float
        Radii (> 0).

    Returns
    -------
    (new_vel_a, new_vel_b, new_pos_a, new_pos_b)
        Post-collision velocities and separated positions.
    """
    normal = pos_a - pos_b
    dist = normal.magnitude
    if dist == 0:
        # Perfectly overlapping – nudge apart along an arbitrary axis.
        normal = Vector2D(1.0, 0.0)
        dist = 1.0

    # Unit normal from B → A
    n = normal.normalized()

    # Relative velocity of A w.r.t. B along the collision normal
    rel_vel = vel_a - vel_b
    vel_along_normal = rel_vel.dot(n)

    # Don't resolve if objects are already moving apart.
    if vel_along_normal > 0:
        # Still separate them to fix overlap.
        overlap = (radius_a + radius_b) - dist
        if overlap > 0:
            correction = n * (overlap / 2 + 0.5)
            pos_a = pos_a + correction
            pos_b = pos_b - correction
        return vel_a, vel_b, pos_a, pos_b

    # 2-D elastic collision impulse
    total_mass = mass_a + mass_b
    impulse = (2 * vel_along_normal) / total_mass

    new_vel_a = vel_a - n * (impulse * mass_b)
    new_vel_b = vel_b + n * (impulse * mass_a)

    # Separate overlapping circles
    overlap = (radius_a + radius_b) - dist
    if overlap > 0:
        correction = n * (overlap / 2 + 0.5)
        pos_a = pos_a + correction
        pos_b = pos_b - correction

    return new_vel_a, new_vel_b, pos_a, pos_b
