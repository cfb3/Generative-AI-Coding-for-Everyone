"""UI buttons and status bar for the simulation."""

from __future__ import annotations

import pygame

from skunk.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    STATUS_BAR_HEIGHT,
    PLAY_AREA_HEIGHT,
    COLOR_STATUS_BG,
    COLOR_STATUS_TEXT,
    COLOR_BUTTON_BG,
    COLOR_BUTTON_TEXT,
    COLOR_BUTTON_HOVER,
    COLOR_ENERGY_BAR,
)


class Button:
    """A clickable rectangle with a text label."""

    def __init__(self, x: int, y: int, w: int, h: int, label: str) -> None:
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.hovered = False

    def update_hover(self, mouse_pos: tuple[int, int]) -> None:
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        color = COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON_BG
        pygame.draw.rect(surface, color, self.rect, border_radius=4)
        text_surf = font.render(self.label, True, COLOR_BUTTON_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


def create_buttons() -> dict[str, Button]:
    """Create the standard control buttons positioned in the status bar."""
    y = PLAY_AREA_HEIGHT + 4
    h = STATUS_BAR_HEIGHT - 8
    w = 80
    gap = 8
    # Right-aligned buttons
    x_start = WINDOW_WIDTH - (3 * w + 2 * gap + 10)
    return {
        "pause": Button(x_start, y, w, h, "Pause"),
        "reset": Button(x_start + w + gap, y, w, h, "Reset"),
        "gravity": Button(x_start + 2 * (w + gap), y, w, h, "Gravity Off"),
    }


def draw_status_bar(
    surface: pygame.Surface,
    simulation,
    buttons: dict[str, Button],
    font: pygame.font.Font,
) -> None:
    """Draw the dark status bar at the bottom with energy display and buttons."""
    bar_rect = pygame.Rect(0, PLAY_AREA_HEIGHT, WINDOW_WIDTH, STATUS_BAR_HEIGHT)
    pygame.draw.rect(surface, COLOR_STATUS_BG, bar_rect)

    # Energy display
    energy = simulation.total_energy
    energy_text = f"Energy: {energy:,.0f}"
    text_surf = font.render(energy_text, True, COLOR_STATUS_TEXT)
    surface.blit(text_surf, (10, PLAY_AREA_HEIGHT + 4))

    # Energy bar
    bar_x = 10
    bar_y = PLAY_AREA_HEIGHT + 18
    bar_w = 140
    bar_h = 6
    pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
    fill_w = min(bar_w, int(bar_w * min(energy / 50000, 1.0)))
    if fill_w > 0:
        pygame.draw.rect(surface, COLOR_ENERGY_BAR, (bar_x, bar_y, fill_w, bar_h))

    # Ball count
    count_text = f"Balls: {len(simulation.balls)}"
    count_surf = font.render(count_text, True, COLOR_STATUS_TEXT)
    surface.blit(count_surf, (170, PLAY_AREA_HEIGHT + 8))

    # Buttons
    for btn in buttons.values():
        btn.draw(surface, font)
