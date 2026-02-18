"""Tests for skunk.model.ball.Ball."""

import math
import pytest
from unittest.mock import patch
from skunk.physics.vector2d import Vector2D
from skunk.model.ball import Ball
from skunk.constants import (
    MASS_DENSITY,
    MAX_SPEED_CAP,
    WINDOW_WIDTH,
    PLAY_AREA_HEIGHT,
    MIN_RADIUS,
    MAX_RADIUS,
    MIN_SPEED,
    MAX_SPEED,
)


@pytest.fixture
def simple_ball():
    return Ball(
        position=Vector2D(100, 100),
        velocity=Vector2D(3, 4),
        radius=10.0,
        color=(255, 0, 0),
    )


class TestCreation:
    def test_position_stored(self, simple_ball):
        assert simple_ball.position == Vector2D(100, 100)

    def test_velocity_stored(self, simple_ball):
        assert simple_ball.velocity == Vector2D(3, 4)

    def test_radius_stored(self, simple_ball):
        assert simple_ball.radius == 10.0

    def test_mass_from_density(self, simple_ball):
        expected = MASS_DENSITY * math.pi * 10.0 * 10.0
        assert simple_ball.mass == pytest.approx(expected)

    def test_color_stored(self, simple_ball):
        assert simple_ball.color == (255, 0, 0)


class TestDerivedProperties:
    def test_speed(self, simple_ball):
        assert simple_ball.speed == pytest.approx(5.0)

    def test_kinetic_energy(self, simple_ball):
        expected = 0.5 * simple_ball.mass * simple_ball.velocity.magnitude_sq
        assert simple_ball.kinetic_energy == pytest.approx(expected)

    def test_kinetic_energy_zero_when_stationary(self):
        b = Ball(Vector2D(0, 0), Vector2D(0, 0), 10, (0, 0, 0))
        assert b.kinetic_energy == 0.0

    def test_momentum_direction(self, simple_ball):
        p = simple_ball.momentum
        # momentum should be in same direction as velocity
        assert p.x == pytest.approx(3 * simple_ball.mass)
        assert p.y == pytest.approx(4 * simple_ball.mass)


class TestMutation:
    def test_update_position(self, simple_ball):
        simple_ball.update_position()
        assert simple_ball.position == Vector2D(103, 104)

    def test_apply_impulse(self, simple_ball):
        simple_ball.apply_impulse(Vector2D(10, -5))
        assert simple_ball.velocity == Vector2D(13, -1)

    def test_clamp_speed_under_limit(self, simple_ball):
        simple_ball.clamp_speed(100)
        assert simple_ball.velocity == Vector2D(3, 4)

    def test_clamp_speed_over_limit(self):
        b = Ball(Vector2D(0, 0), Vector2D(30, 40), 10, (0, 0, 0))
        b.clamp_speed(5.0)
        assert b.speed == pytest.approx(5.0)

    def test_clamp_speed_default(self):
        b = Ball(Vector2D(0, 0), Vector2D(300, 400), 10, (0, 0, 0))
        b.clamp_speed()
        assert b.speed == pytest.approx(MAX_SPEED_CAP)


class TestWallBounce:
    def test_left_wall_bounce(self):
        b = Ball(Vector2D(5, 100), Vector2D(-10, 0), 10, (0, 0, 0))
        hit_left = b.handle_wall_bounce()
        assert hit_left is True
        assert b.velocity.x > 0

    def test_right_wall_bounce(self):
        b = Ball(Vector2D(WINDOW_WIDTH - 5, 100), Vector2D(10, 0), 10, (0, 0, 0))
        hit_left = b.handle_wall_bounce()
        assert hit_left is False
        assert b.velocity.x < 0

    def test_top_wall_bounce(self):
        b = Ball(Vector2D(100, 5), Vector2D(0, -10), 10, (0, 0, 0))
        b.handle_wall_bounce()
        assert b.velocity.y > 0

    def test_bottom_wall_bounce(self):
        b = Ball(Vector2D(100, PLAY_AREA_HEIGHT - 5), Vector2D(0, 10), 10, (0, 0, 0))
        b.handle_wall_bounce()
        assert b.velocity.y < 0

    def test_no_bounce_when_moving_away(self):
        b = Ball(Vector2D(5, 100), Vector2D(10, 0), 10, (0, 0, 0))
        hit_left = b.handle_wall_bounce()
        assert hit_left is False
        assert b.velocity.x == pytest.approx(10)

    def test_gravity_bounce_returns_floor_flag(self):
        b = Ball(
            Vector2D(100, PLAY_AREA_HEIGHT - 5),
            Vector2D(0, 10),
            10,
            (0, 0, 0),
        )
        hit_left, hit_floor = b.handle_wall_bounce_gravity()
        assert hit_floor is True
        assert b.velocity.y < 0


class TestIsOnFloor:
    def test_on_floor(self):
        b = Ball(Vector2D(100, PLAY_AREA_HEIGHT - 10), Vector2D(0, 0), 10, (0, 0, 0))
        assert b.is_on_floor is True

    def test_not_on_floor(self):
        b = Ball(Vector2D(100, 100), Vector2D(0, 0), 10, (0, 0, 0))
        assert b.is_on_floor is False


class TestCreateRandom:
    def test_returns_ball(self):
        b = Ball.create_random(Vector2D(100, 100), (255, 0, 0))
        assert isinstance(b, Ball)

    def test_position_set(self):
        b = Ball.create_random(Vector2D(42, 99), (0, 0, 0))
        assert b.position == Vector2D(42, 99)

    def test_radius_in_range(self):
        for _ in range(20):
            b = Ball.create_random(Vector2D(100, 100), (0, 0, 0))
            assert MIN_RADIUS <= b.radius <= MAX_RADIUS

    def test_speed_in_range(self):
        for _ in range(20):
            b = Ball.create_random(Vector2D(100, 100), (0, 0, 0))
            assert MIN_SPEED <= b.speed <= MAX_SPEED + 0.01

    def test_explicit_velocity(self):
        v = Vector2D(7, -3)
        b = Ball.create_random(Vector2D(50, 50), (0, 0, 0), velocity=v)
        assert b.velocity == v

    def test_color_set(self):
        b = Ball.create_random(Vector2D(50, 50), (1, 2, 3))
        assert b.color == (1, 2, 3)
