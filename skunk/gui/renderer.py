"""Main renderer – draws balls, backgrounds, grass, and visual effects."""

from __future__ import annotations

import random

import pygame
import pygame.gfxdraw

from skunk.constants import (
    WINDOW_WIDTH,
    PLAY_AREA_HEIGHT,
    COLOR_BG_SPACE,
    COLOR_BG_SKY,
    COLOR_GRASS,
    COLOR_GRASS_DARK,
    COLOR_GROUND,
)
from skunk.gui.effects import draw_wall_glow, draw_shockwave_burst
from skunk.model.simulation import Simulation


# Pre-generate grass tuft positions so they don't jitter each frame.
_grass_tufts: list[tuple[int, int, int]] | None = None


def _generate_grass_tufts() -> list[tuple[int, int, int]]:
    """Generate random tuft positions: (x, height, offset)."""
    tufts = []
    rng = random.Random(42)  # fixed seed for stable tufts
    x = 0
    while x < WINDOW_WIDTH:
        h = rng.randint(6, 16)
        offset = rng.randint(-2, 2)
        tufts.append((x, h, offset))
        x += rng.randint(3, 8)
    return tufts


def _ensure_grass_tufts() -> list[tuple[int, int, int]]:
    global _grass_tufts
    if _grass_tufts is None:
        _grass_tufts = _generate_grass_tufts()
    return _grass_tufts


def draw_background(surface: pygame.Surface, gravity_on: bool) -> None:
    """Fill the play area background."""
    if gravity_on:
        surface.fill(COLOR_BG_SKY, (0, 0, WINDOW_WIDTH, PLAY_AREA_HEIGHT))
    else:
        surface.fill(COLOR_BG_SPACE, (0, 0, WINDOW_WIDTH, PLAY_AREA_HEIGHT))


def draw_balls(surface: pygame.Surface, simulation: Simulation) -> None:
    """Draw all balls as anti-aliased filled circles."""
    for ball in simulation.balls:
        cx = int(ball.position.x)
        cy = int(ball.position.y)
        r = int(ball.radius)
        if r < 1:
            r = 1
        pygame.gfxdraw.aacircle(surface, cx, cy, r, ball.color)
        pygame.gfxdraw.filled_circle(surface, cx, cy, r, ball.color)


def draw_grass(surface: pygame.Surface) -> None:
    """Draw small green triangular tufts along the bottom of the play area."""
    tufts = _ensure_grass_tufts()
    ground_y = PLAY_AREA_HEIGHT
    # Thin ground strip
    pygame.draw.rect(surface, COLOR_GROUND, (0, ground_y - 4, WINDOW_WIDTH, 4))
    for x, h, offset in tufts:
        bx = x + offset
        # Each tuft is a small triangle pointing up
        tip = (bx, ground_y - 4 - h)
        left = (bx - 3, ground_y - 4)
        right = (bx + 3, ground_y - 4)
        color = COLOR_GRASS if (x % 2 == 0) else COLOR_GRASS_DARK
        pygame.draw.polygon(surface, color, [tip, left, right])


def draw_effects(surface: pygame.Surface, simulation: Simulation) -> None:
    """Draw wall glow and shockwave effects."""
    draw_wall_glow(
        surface,
        simulation.wall_glow_timer,
        simulation.WALL_GLOW_DURATION,
    )
    for effect in simulation.shockwave_effects:
        origin = effect["origin"]
        draw_shockwave_burst(
            surface,
            (int(origin.x), int(origin.y)),
            effect["age"],
            simulation.SHOCKWAVE_VISUAL_DURATION,
        )
