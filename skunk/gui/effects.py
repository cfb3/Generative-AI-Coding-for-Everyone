"""Visual effects helpers – wall glow, shockwave bursts, slingshot line."""

from __future__ import annotations

import math

import pygame

from skunk.constants import (
    COLOR_WALL_GLOW,
    COLOR_SHOCKWAVE,
    COLOR_SLINGSHOT_LINE,
    PLAY_AREA_HEIGHT,
)


def draw_wall_glow(
    surface: pygame.Surface,
    timer: float,
    max_timer: float,
) -> None:
    """Draw a semi-transparent orange vertical strip on the left wall.

    Alpha fades linearly as *timer* decreases toward 0.
    """
    if timer <= 0:
        return
    alpha = int(180 * (timer / max_timer))
    width = 18
    glow = pygame.Surface((width, PLAY_AREA_HEIGHT), pygame.SRCALPHA)
    glow.fill((*COLOR_WALL_GLOW, alpha))
    surface.blit(glow, (0, 0))


def draw_shockwave_burst(
    surface: pygame.Surface,
    origin: tuple[int, int],
    age: int,
    max_age: int,
) -> None:
    """Draw radial burst lines expanding outward from *origin*."""
    if age >= max_age:
        return
    progress = age / max_age
    alpha = int(255 * (1.0 - progress))
    radius = int(40 + 260 * progress)
    num_rays = 24
    color = (*COLOR_SHOCKWAVE, alpha)
    thickness = max(1, int(3 * (1.0 - progress)))
    burst_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for i in range(num_rays):
        angle = (2 * math.pi * i) / num_rays
        inner_r = int(radius * 0.3)
        dx_inner = math.cos(angle) * inner_r
        dy_inner = math.sin(angle) * inner_r
        dx_outer = math.cos(angle) * radius
        dy_outer = math.sin(angle) * radius
        start = (int(origin[0] + dx_inner), int(origin[1] + dy_inner))
        end = (int(origin[0] + dx_outer), int(origin[1] + dy_outer))
        pygame.draw.line(burst_surf, color, start, end, thickness)
    surface.blit(burst_surf, (0, 0))


def draw_slingshot(
    surface: pygame.Surface,
    start_pos: tuple[int, int],
    current_pos: tuple[int, int],
) -> None:
    """Draw slingshot line from click point to cursor with arrow and speed indicator."""
    dx = current_pos[0] - start_pos[0]
    dy = current_pos[1] - start_pos[1]
    dist = math.hypot(dx, dy)
    if dist < 5:
        return

    # Thicker/brighter line for faster launches
    speed_factor = min(dist / 200, 1.0)
    thickness = max(2, int(2 + 4 * speed_factor))
    brightness = int(155 + 100 * speed_factor)
    color = (brightness, brightness, int(80 + 80 * speed_factor))

    pygame.draw.line(surface, color, start_pos, current_pos, thickness)

    # Arrow head pointing in launch direction (opposite of drag)
    angle = math.atan2(-dy, -dx)
    arrow_len = 14
    arrow_spread = 0.4
    tip = start_pos
    left = (
        int(tip[0] - arrow_len * math.cos(angle - arrow_spread)),
        int(tip[1] - arrow_len * math.sin(angle - arrow_spread)),
    )
    right = (
        int(tip[0] - arrow_len * math.cos(angle + arrow_spread)),
        int(tip[1] - arrow_len * math.sin(angle + arrow_spread)),
    )
    pygame.draw.polygon(surface, color, [tip, left, right])
