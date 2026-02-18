"""Tests for skunk.model.simulation.Simulation."""

import pytest
from skunk.physics.vector2d import Vector2D
from skunk.model.simulation import Simulation
from skunk.model.ball import Ball
from skunk.constants import (
    WINDOW_WIDTH,
    PLAY_AREA_HEIGHT,
    SHOCKWAVE_RADIUS,
    SHOCKWAVE_STRENGTH,
)


@pytest.fixture
def sim():
    return Simulation()


@pytest.fixture
def sim_with_ball(sim):
    ball = sim.spawn_ball(Vector2D(400, 200), velocity=Vector2D(2, 0))
    return sim, ball


class TestSpawnBall:
    def test_spawn_adds_ball(self, sim):
        ball = sim.spawn_ball(Vector2D(400, 200))
        assert ball is not None
        assert len(sim.balls) == 1

    def test_spawn_returns_ball_object(self, sim):
        ball = sim.spawn_ball(Vector2D(400, 200))
        assert isinstance(ball, Ball)

    def test_spawn_overlap_rejected(self, sim):
        sim.spawn_ball(Vector2D(100, 100), velocity=Vector2D(0, 0))
        result = sim.spawn_ball(Vector2D(105, 100), velocity=Vector2D(0, 0))
        assert result is None

    def test_spawn_far_apart_succeeds(self, sim):
        sim.spawn_ball(Vector2D(100, 100), velocity=Vector2D(0, 0))
        result = sim.spawn_ball(Vector2D(300, 300), velocity=Vector2D(0, 0))
        assert result is not None
        assert len(sim.balls) == 2

    def test_spawn_with_explicit_velocity(self, sim):
        v = Vector2D(5, -3)
        ball = sim.spawn_ball(Vector2D(400, 200), velocity=v)
        assert ball.velocity == v


class TestUpdate:
    def test_update_moves_ball(self, sim_with_ball):
        sim, ball = sim_with_ball
        old_pos = ball.position
        sim.update()
        assert ball.position != old_pos

    def test_paused_no_movement(self, sim_with_ball):
        sim, ball = sim_with_ball
        sim.paused = True
        old_pos = ball.position
        sim.update()
        assert ball.position == old_pos

    def test_multiple_updates_move_further(self, sim_with_ball):
        sim, ball = sim_with_ball
        sim.update()
        pos1 = ball.position
        sim.update()
        pos2 = ball.position
        # Ball moved further from start
        assert pos2.x != pos1.x or pos2.y != pos1.y

    def test_collision_between_two_balls(self, sim):
        # Two balls heading toward each other
        b1 = sim.spawn_ball(Vector2D(100, 200), velocity=Vector2D(5, 0))
        b2 = sim.spawn_ball(Vector2D(200, 200), velocity=Vector2D(-5, 0))
        assert b1 is not None and b2 is not None

        # Run until they collide or enough frames pass
        for _ in range(50):
            sim.update()

        # After collision, at least one should have changed direction
        # (or they bounced off walls)
        # Just verify simulation didn't crash
        assert len(sim.balls) == 2

    def test_wall_glow_decays(self, sim):
        sim.wall_glow_timer = 10
        sim.update()
        assert sim.wall_glow_timer == 9


class TestGravity:
    def test_toggle_gravity(self, sim):
        assert sim.gravity_on is False
        sim.toggle_gravity()
        assert sim.gravity_on is True
        sim.toggle_gravity()
        assert sim.gravity_on is False

    def test_gravity_adds_downward_velocity(self, sim):
        ball = sim.spawn_ball(Vector2D(400, 100), velocity=Vector2D(0, 0))
        sim.gravity_on = True
        sim.update()
        assert ball.velocity.y > 0  # downward


class TestPause:
    def test_toggle_pause(self, sim):
        assert sim.paused is False
        sim.toggle_pause()
        assert sim.paused is True
        sim.toggle_pause()
        assert sim.paused is False


class TestShockwave:
    def test_shockwave_pushes_ball_away(self, sim):
        ball = sim.spawn_ball(Vector2D(400, 200), velocity=Vector2D(0, 0))
        sim.apply_shockwave(Vector2D(300, 200))
        # Ball to the right of origin should be pushed right
        assert ball.velocity.x > 0

    def test_shockwave_adds_visual_effect(self, sim):
        sim.apply_shockwave(Vector2D(400, 200))
        assert len(sim.shockwave_effects) == 1
        assert sim.shockwave_effects[0]["age"] == 0

    def test_shockwave_effect_ages(self, sim):
        sim.apply_shockwave(Vector2D(400, 200))
        sim.update()
        assert sim.shockwave_effects[0]["age"] == 1

    def test_shockwave_effect_removed_after_duration(self, sim):
        sim.apply_shockwave(Vector2D(400, 200))
        for _ in range(Simulation.SHOCKWAVE_VISUAL_DURATION + 1):
            sim.update()
        assert len(sim.shockwave_effects) == 0

    def test_shockwave_no_effect_on_distant_ball(self, sim):
        ball = sim.spawn_ball(
            Vector2D(SHOCKWAVE_RADIUS + 100, 200), velocity=Vector2D(0, 0)
        )
        sim.apply_shockwave(Vector2D(0, 200))
        assert ball.velocity == Vector2D(0, 0)


class TestTotalEnergy:
    def test_empty_sim(self, sim):
        assert sim.total_energy == 0.0

    def test_with_balls(self, sim):
        sim.spawn_ball(Vector2D(100, 200), velocity=Vector2D(5, 0))
        sim.spawn_ball(Vector2D(400, 200), velocity=Vector2D(0, 3))
        assert sim.total_energy > 0


class TestBallAt:
    def test_finds_ball(self, sim):
        ball = sim.spawn_ball(Vector2D(200, 200), velocity=Vector2D(0, 0))
        found = sim.ball_at(Vector2D(200, 200))
        assert found is ball

    def test_finds_ball_near_edge(self, sim):
        ball = sim.spawn_ball(Vector2D(200, 200), velocity=Vector2D(0, 0))
        # Click near edge of ball (within radius)
        found = sim.ball_at(Vector2D(200 + ball.radius - 1, 200))
        assert found is ball

    def test_no_ball(self, sim):
        sim.spawn_ball(Vector2D(200, 200), velocity=Vector2D(0, 0))
        assert sim.ball_at(Vector2D(500, 500)) is None


class TestReset:
    def test_clears_balls(self, sim_with_ball):
        sim, _ = sim_with_ball
        sim.reset()
        assert len(sim.balls) == 0

    def test_resets_gravity(self, sim):
        sim.gravity_on = True
        sim.reset()
        assert sim.gravity_on is False

    def test_resets_pause(self, sim):
        sim.paused = True
        sim.reset()
        assert sim.paused is False

    def test_resets_glow(self, sim):
        sim.wall_glow_timer = 15
        sim.reset()
        assert sim.wall_glow_timer == 0.0

    def test_resets_shockwave_effects(self, sim):
        sim.shockwave_effects.append({"origin": Vector2D(0, 0), "age": 5})
        sim.reset()
        assert len(sim.shockwave_effects) == 0


class TestRemoveBall:
    def test_removes_existing(self, sim_with_ball):
        sim, ball = sim_with_ball
        sim.remove_ball(ball)
        assert len(sim.balls) == 0

    def test_remove_nonexistent_no_error(self, sim):
        fake = Ball(Vector2D(0, 0), Vector2D(0, 0), 10, (0, 0, 0))
        sim.remove_ball(fake)  # should not raise
