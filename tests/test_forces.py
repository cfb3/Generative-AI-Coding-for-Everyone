"""Tests for skunk.physics.forces — all force/impulse functions."""

import math
import pytest
from skunk.physics.vector2d import Vector2D
from skunk.physics.forces import (
    apply_surface_friction,
    apply_gravity,
    apply_air_resistance,
    apply_floor_friction,
    apply_bounce_restitution,
    compute_wall_boost,
    compute_shockwave_impulse,
)
from skunk.constants import (
    SURFACE_FRICTION,
    GRAVITY_ACCEL,
    AIR_RESISTANCE,
    FLOOR_FRICTION,
    BOUNCE_RESTITUTION,
    LEFT_WALL_BOOST,
    MAX_SPEED_CAP,
    SHOCKWAVE_STRENGTH,
    SHOCKWAVE_RADIUS,
)


class TestSurfaceFriction:
    def test_reduces_speed(self):
        v = Vector2D(10, 0)
        result = apply_surface_friction(v, 1.0)
        assert result.magnitude < v.magnitude

    def test_heavier_mass_more_friction(self):
        v = Vector2D(10, 5)
        light = apply_surface_friction(v, 1.0)
        heavy = apply_surface_friction(v, 4.0)
        assert heavy.magnitude < light.magnitude

    def test_zero_velocity_stays_zero(self):
        result = apply_surface_friction(Vector2D(0, 0), 1.0)
        assert result == Vector2D(0, 0)

    def test_correct_formula(self):
        v = Vector2D(10, 0)
        mass = 4.0
        expected_factor = SURFACE_FRICTION ** math.sqrt(mass)
        result = apply_surface_friction(v, mass)
        assert result.x == pytest.approx(10 * expected_factor)


class TestGravity:
    def test_adds_downward_velocity(self):
        v = Vector2D(5, 0)
        result = apply_gravity(v)
        assert result.y == pytest.approx(GRAVITY_ACCEL)
        assert result.x == pytest.approx(5.0)

    def test_accumulates(self):
        v = Vector2D(0, 0)
        v = apply_gravity(v)
        v = apply_gravity(v)
        assert v.y == pytest.approx(2 * GRAVITY_ACCEL)

    def test_doesnt_affect_x(self):
        v = Vector2D(7, 3)
        result = apply_gravity(v)
        assert result.x == pytest.approx(7.0)


class TestAirResistance:
    def test_reduces_speed(self):
        v = Vector2D(10, 10)
        result = apply_air_resistance(v)
        assert result.magnitude < v.magnitude

    def test_correct_factor(self):
        v = Vector2D(10, 5)
        result = apply_air_resistance(v)
        assert result.x == pytest.approx(10 * AIR_RESISTANCE)
        assert result.y == pytest.approx(5 * AIR_RESISTANCE)


class TestFloorFriction:
    def test_reduces_x(self):
        v = Vector2D(10, -5)
        result = apply_floor_friction(v)
        assert abs(result.x) < abs(v.x)

    def test_y_unchanged(self):
        v = Vector2D(10, -5)
        result = apply_floor_friction(v)
        assert result.y == pytest.approx(v.y)

    def test_correct_factor(self):
        v = Vector2D(10, 3)
        result = apply_floor_friction(v)
        assert result.x == pytest.approx(10 * FLOOR_FRICTION)


class TestBounceRestitution:
    def test_reduces_vertical_speed(self):
        v = Vector2D(5, -10)
        result = apply_bounce_restitution(v)
        assert abs(result.y) < abs(v.y)

    def test_x_unchanged(self):
        v = Vector2D(5, -10)
        result = apply_bounce_restitution(v)
        assert result.x == pytest.approx(5.0)

    def test_correct_factor(self):
        v = Vector2D(0, -10)
        result = apply_bounce_restitution(v)
        assert result.y == pytest.approx(-10 * BOUNCE_RESTITUTION)


class TestWallBoost:
    def test_increases_x_speed(self):
        v = Vector2D(2, 1)
        result = compute_wall_boost(v)
        assert abs(result.x) > abs(v.x)

    def test_correct_multiplier(self):
        v = Vector2D(2, 0)
        result = compute_wall_boost(v)
        assert result.x == pytest.approx(2 * LEFT_WALL_BOOST)

    def test_respects_speed_cap(self):
        v = Vector2D(MAX_SPEED_CAP, 0)
        result = compute_wall_boost(v)
        assert result.magnitude <= MAX_SPEED_CAP + 0.001

    def test_high_speed_capped(self):
        v = Vector2D(100, 100)
        result = compute_wall_boost(v)
        assert result.magnitude == pytest.approx(MAX_SPEED_CAP, abs=0.01)


class TestShockwaveImpulse:
    def test_direction_away_from_origin(self):
        ball = Vector2D(100, 0)
        origin = Vector2D(0, 0)
        impulse = compute_shockwave_impulse(ball, origin)
        assert impulse.x > 0  # pushed right (away)
        assert impulse.y == pytest.approx(0.0, abs=1e-6)

    def test_falls_off_with_distance(self):
        origin = Vector2D(0, 0)
        near = compute_shockwave_impulse(Vector2D(10, 0), origin)
        far = compute_shockwave_impulse(Vector2D(100, 0), origin)
        assert near.magnitude > far.magnitude

    def test_zero_beyond_radius(self):
        origin = Vector2D(0, 0)
        beyond = compute_shockwave_impulse(
            Vector2D(SHOCKWAVE_RADIUS + 1, 0), origin
        )
        assert beyond == Vector2D(0, 0)

    def test_at_boundary_still_has_impulse(self):
        origin = Vector2D(0, 0)
        at_boundary = compute_shockwave_impulse(
            Vector2D(SHOCKWAVE_RADIUS - 1, 0), origin
        )
        assert at_boundary.magnitude > 0

    def test_same_position_doesnt_crash(self):
        origin = Vector2D(50, 50)
        impulse = compute_shockwave_impulse(origin, origin)
        # dist=0, safe_dist=1, should return zero-direction * strength
        assert impulse == Vector2D(0, 0)  # zero vector normalized is zero

    def test_diagonal_direction(self):
        ball = Vector2D(10, 10)
        origin = Vector2D(0, 0)
        impulse = compute_shockwave_impulse(ball, origin)
        # Should point in the (1,1) direction (roughly equal x and y)
        assert impulse.x == pytest.approx(impulse.y, abs=0.01)
        assert impulse.x > 0
