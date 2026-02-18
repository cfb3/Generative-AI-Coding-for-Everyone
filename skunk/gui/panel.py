"""Ball editing side panel – visible when paused and a ball is selected."""

from __future__ import annotations

import math

import pygame

from skunk.constants import (
    WINDOW_WIDTH,
    PLAY_AREA_HEIGHT,
    COLOR_PANEL_BG,
    COLOR_PANEL_TEXT,
    COLOR_BUTTON_BG,
    COLOR_BUTTON_HOVER,
    COLOR_BUTTON_TEXT,
)
from skunk.physics.vector2d import Vector2D
from skunk.model.ball import Ball


PANEL_WIDTH = 200
PANEL_X = WINDOW_WIDTH - PANEL_WIDTH
PANEL_PAD = 12
FIELD_HEIGHT = 24
ROW_GAP = 32


class EditField:
    """A simple click-to-edit numeric field."""

    def __init__(self, label: str, y: int, editable: bool = True) -> None:
        self.label = label
        self.y = y
        self.editable = editable
        self.active = False
        self.buffer = ""
        self.rect = pygame.Rect(
            PANEL_X + PANEL_PAD + 80,
            y,
            PANEL_WIDTH - PANEL_PAD * 2 - 80,
            FIELD_HEIGHT,
        )

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        value: str,
    ) -> None:
        # Label
        label_surf = font.render(f"{self.label}:", True, COLOR_PANEL_TEXT)
        surface.blit(label_surf, (PANEL_X + PANEL_PAD, self.y + 3))
        # Field background
        bg_color = (70, 70, 90) if self.active else (50, 50, 65)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=3)
        if self.editable:
            pygame.draw.rect(surface, (100, 100, 130), self.rect, 1, border_radius=3)
        # Value text
        display = self.buffer if self.active else value
        val_surf = font.render(display, True, COLOR_PANEL_TEXT)
        surface.blit(val_surf, (self.rect.x + 4, self.y + 3))


class PlusMinusButton:
    """Small +/- button next to an edit field."""

    def __init__(self, x: int, y: int, label: str) -> None:
        self.rect = pygame.Rect(x, y, 20, FIELD_HEIGHT)
        self.label = label
        self.hovered = False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        color = COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON_BG
        pygame.draw.rect(surface, color, self.rect, border_radius=3)
        t = font.render(self.label, True, COLOR_BUTTON_TEXT)
        tr = t.get_rect(center=self.rect.center)
        surface.blit(t, tr)

    def update_hover(self, mouse_pos: tuple[int, int]) -> None:
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


class BallPanel:
    """Side panel for editing a selected ball's properties."""

    def __init__(self) -> None:
        self.selected_ball: Ball | None = None
        base_y = 60
        self.speed_field = EditField("Speed", base_y, editable=True)
        self.angle_field = EditField("Angle", base_y + ROW_GAP, editable=True)
        self.radius_field = EditField("Radius", base_y + ROW_GAP * 2, editable=False)
        self.mass_field = EditField("Mass", base_y + ROW_GAP * 3, editable=False)
        self.fields = [
            self.speed_field,
            self.angle_field,
            self.radius_field,
            self.mass_field,
        ]
        # +/- buttons for speed and angle
        btn_x_minus = PANEL_X + PANEL_PAD + 80
        btn_x_plus = PANEL_X + PANEL_WIDTH - PANEL_PAD - 20
        self.speed_minus = PlusMinusButton(btn_x_minus - 24, base_y, "-")
        self.speed_plus = PlusMinusButton(btn_x_plus + 4, base_y, "+")
        self.angle_minus = PlusMinusButton(btn_x_minus - 24, base_y + ROW_GAP, "-")
        self.angle_plus = PlusMinusButton(btn_x_plus + 4, base_y + ROW_GAP, "+")
        self.pm_buttons = [
            self.speed_minus,
            self.speed_plus,
            self.angle_minus,
            self.angle_plus,
        ]

    @property
    def visible(self) -> bool:
        return self.selected_ball is not None

    def select(self, ball: Ball | None) -> None:
        self.selected_ball = ball
        for f in self.fields:
            f.active = False
            f.buffer = ""

    def handle_click(self, pos: tuple[int, int]) -> bool:
        """Handle a mouse click. Returns True if the panel consumed it."""
        if not self.visible:
            return False
        if pos[0] < PANEL_X:
            return False

        ball = self.selected_ball

        # +/- buttons
        if self.speed_minus.is_clicked(pos) and ball:
            spd = max(0.1, ball.speed - 0.2)
            self._set_ball_speed(ball, spd)
            return True
        if self.speed_plus.is_clicked(pos) and ball:
            spd = ball.speed + 0.2
            self._set_ball_speed(ball, spd)
            return True
        if self.angle_minus.is_clicked(pos) and ball:
            self._rotate_ball(ball, -10)
            return True
        if self.angle_plus.is_clicked(pos) and ball:
            self._rotate_ball(ball, 10)
            return True

        # Editable field clicks
        for f in self.fields:
            if f.editable and f.rect.collidepoint(pos):
                # Deactivate others
                for f2 in self.fields:
                    f2.active = False
                    f2.buffer = ""
                f.active = True
                f.buffer = ""
                return True

        return True  # consumed click (on panel area)

    def handle_key(self, event: pygame.event.Event) -> bool:
        """Handle keyboard input for active fields. Returns True if consumed."""
        if not self.visible or self.selected_ball is None:
            return False
        for f in self.fields:
            if f.active:
                if event.key == pygame.K_RETURN:
                    self._confirm_field(f)
                    return True
                elif event.key == pygame.K_ESCAPE:
                    f.active = False
                    f.buffer = ""
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    f.buffer = f.buffer[:-1]
                    return True
                elif event.unicode and (event.unicode.isdigit() or event.unicode in ".-"):
                    f.buffer += event.unicode
                    return True
        return False

    def _confirm_field(self, field: EditField) -> None:
        ball = self.selected_ball
        if ball is None or not field.buffer:
            field.active = False
            field.buffer = ""
            return
        try:
            val = float(field.buffer)
        except ValueError:
            field.active = False
            field.buffer = ""
            return
        if field is self.speed_field:
            self._set_ball_speed(ball, max(0.0, val))
        elif field is self.angle_field:
            self._set_ball_angle(ball, val)
        field.active = False
        field.buffer = ""

    def _set_ball_speed(self, ball: Ball, speed: float) -> None:
        direction = ball.velocity.normalized()
        if direction.magnitude == 0:
            direction = Vector2D(1.0, 0.0)
        ball.velocity = direction * speed

    def _set_ball_angle(self, ball: Ball, degrees: float) -> None:
        rad = math.radians(degrees)
        speed = ball.speed
        if speed == 0:
            speed = 0.5
        ball.velocity = Vector2D.from_angle(rad, speed)

    def _rotate_ball(self, ball: Ball, delta_deg: float) -> None:
        current_deg = ball.velocity.angle_deg()
        self._set_ball_angle(ball, current_deg + delta_deg)

    def update_hover(self, mouse_pos: tuple[int, int]) -> None:
        for btn in self.pm_buttons:
            btn.update_hover(mouse_pos)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        if not self.visible or self.selected_ball is None:
            return
        ball = self.selected_ball
        # Semi-transparent background
        panel_surf = pygame.Surface((PANEL_WIDTH, PLAY_AREA_HEIGHT), pygame.SRCALPHA)
        panel_surf.fill(COLOR_PANEL_BG)
        surface.blit(panel_surf, (PANEL_X, 0))

        # Title
        title = font.render("Ball Editor", True, COLOR_PANEL_TEXT)
        surface.blit(title, (PANEL_X + PANEL_PAD, 10))

        # Color swatch
        pygame.draw.circle(surface, ball.color, (PANEL_X + PANEL_WIDTH - 30, 18), 10)
        pygame.draw.circle(
            surface, COLOR_PANEL_TEXT, (PANEL_X + PANEL_WIDTH - 30, 18), 10, 1
        )

        # Fields
        self.speed_field.draw(surface, font, f"{ball.speed:.2f}")
        self.angle_field.draw(surface, font, f"{ball.velocity.angle_deg():.1f}")
        self.radius_field.draw(surface, font, f"{ball.radius:.1f}")
        self.mass_field.draw(surface, font, f"{ball.mass:.0f}")

        # +/- buttons
        for btn in self.pm_buttons:
            btn.draw(surface, font)
