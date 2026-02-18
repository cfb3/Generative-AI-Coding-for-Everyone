"""Simulation state manager – owns the list of balls and orchestrates physics.

No pygame dependency.  The GUI reads simulation state to render; it never
drives physics directly.
"""

from __future__ import annotations

from skunk.physics.vector2d import Vector2D
from skunk.physics.collision import detect_collision, resolve_collision
from skunk.physics.forces import (
    apply_surface_friction,
    apply_gravity,
    apply_air_resistance,
    apply_floor_friction,
    apply_bounce_restitution,
    compute_wall_boost,
    compute_shockwave_impulse,
)
from skunk.model.ball import Ball
from skunk.constants import (
    WINDOW_WIDTH,
    PLAY_AREA_HEIGHT,
    COLOR_BALL_LEFT,
    MIN_RADIUS,
    MAX_RADIUS,
)


class Simulation:
    """Top-level simulation state.

    Attributes
    ----------
    balls : list[Ball]
        All active balls.
    gravity_on : bool
        Whether gravity mode is active.
    paused : bool
        Whether the simulation is paused.
    wall_glow_timer : float
        Frames remaining for the left-wall glow effect (0 = off).
    shockwave_effects : list[dict]
        Active shockwave visuals ``{"origin": Vector2D, "age": int}``.
    """

    WALL_GLOW_DURATION = 30  # frames (~0.5 s at 60 FPS)
    SHOCKWAVE_VISUAL_DURATION = 20  # frames

    def __init__(self) -> None:
        self.balls: list[Ball] = []
        self.gravity_on: bool = False
        self.paused: bool = False
        self.wall_glow_timer: float = 0.0
        self.shockwave_effects: list[dict] = []
        self._initial_balls: list[tuple] = []

    # --- ball management ---

    def spawn_ball(
        self,
        position: Vector2D,
        color: tuple[int, int, int] = COLOR_BALL_LEFT,
        velocity: Vector2D | None = None,
    ) -> Ball | None:
        """Create a ball if it wouldn't overlap existing ones.

        Parameters
        ----------
        position : Vector2D
            Desired spawn centre.
        color : tuple
            RGB colour.
        velocity : Vector2D | None
            Explicit velocity (slingshot) or None for random.

        Returns
        -------
        Ball | None
            The new ball, or None if it would overlap.
        """
        test_radius = (MIN_RADIUS + MAX_RADIUS) / 2  # conservative check
        for b in self.balls:
            if position.distance_to(b.position) < test_radius + b.radius:
                return None

        ball = Ball.create_random(position, color, velocity)
        # Re-check with actual radius
        for b in self.balls:
            if position.distance_to(b.position) < ball.radius + b.radius:
                return None

        self.balls.append(ball)
        self._save_initial_state(ball)
        return ball

    def remove_ball(self, ball: Ball) -> None:
        """Remove a ball from the simulation."""
        if ball in self.balls:
            self.balls.remove(ball)

    def reset(self) -> None:
        """Clear all balls and reset state."""
        self.balls.clear()
        self.gravity_on = False
        self.paused = False
        self.wall_glow_timer = 0.0
        self.shockwave_effects.clear()
        self._initial_balls.clear()

    # --- physics tick ---

    def update(self) -> None:
        """Advance the simulation by one frame.

        Does nothing when paused.
        """
        if self.paused:
            return

        # Apply forces and move each ball
        for ball in self.balls:
            if self.gravity_on:
                ball.velocity = apply_gravity(ball.velocity)
                ball.velocity = apply_air_resistance(ball.velocity)
            else:
                ball.velocity = apply_surface_friction(ball.velocity, ball.mass)

            ball.update_position()

            # Wall collisions
            if self.gravity_on:
                hit_left, hit_floor = ball.handle_wall_bounce_gravity(
                    WINDOW_WIDTH, PLAY_AREA_HEIGHT
                )
                if hit_floor:
                    ball.velocity = apply_bounce_restitution(ball.velocity)
                    ball.velocity = apply_floor_friction(ball.velocity)
            else:
                hit_left = ball.handle_wall_bounce(
                    WINDOW_WIDTH, PLAY_AREA_HEIGHT
                )

            if hit_left:
                ball.velocity = compute_wall_boost(ball.velocity)
                self.wall_glow_timer = self.WALL_GLOW_DURATION

            ball.clamp_speed()

        # Pairwise collisions
        n = len(self.balls)
        for i in range(n):
            for j in range(i + 1, n):
                a, b = self.balls[i], self.balls[j]
                if detect_collision(a.position, a.radius, b.position, b.radius):
                    va, vb, pa, pb = resolve_collision(
                        a.position, a.velocity, a.mass, a.radius,
                        b.position, b.velocity, b.mass, b.radius,
                    )
                    a.velocity = va
                    b.velocity = vb
                    a.position = pa
                    b.position = pb

        # Decay timers
        if self.wall_glow_timer > 0:
            self.wall_glow_timer -= 1

        aged = []
        for effect in self.shockwave_effects:
            effect["age"] += 1
            if effect["age"] < self.SHOCKWAVE_VISUAL_DURATION:
                aged.append(effect)
        self.shockwave_effects = aged

    # --- user actions ---

    def apply_shockwave(self, origin: Vector2D) -> None:
        """Trigger a shockwave from *origin*, adding impulse to all balls."""
        for ball in self.balls:
            impulse = compute_shockwave_impulse(ball.position, origin)
            ball.apply_impulse(impulse)
            ball.clamp_speed()
        self.shockwave_effects.append({"origin": origin, "age": 0})

    def toggle_gravity(self) -> None:
        """Toggle gravity mode on/off."""
        self.gravity_on = not self.gravity_on

    def toggle_pause(self) -> None:
        """Toggle paused state."""
        self.paused = not self.paused

    # --- queries ---

    @property
    def total_energy(self) -> float:
        """Sum of kinetic energy of all balls."""
        return sum(b.kinetic_energy for b in self.balls)

    def ball_at(self, pos: Vector2D) -> Ball | None:
        """Return the ball under *pos*, or None."""
        for ball in self.balls:
            if pos.distance_to(ball.position) <= ball.radius:
                return ball
        return None

    # --- internal ---

    def _save_initial_state(self, ball: Ball) -> None:
        """Snapshot for potential future use."""
        self._initial_balls.append(
            (ball.position, ball.velocity, ball.radius, ball.color)
        )
