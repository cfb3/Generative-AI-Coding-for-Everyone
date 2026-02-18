"""Main application – pygame game loop for the bouncing ball simulation."""

from __future__ import annotations

import pygame

from skunk.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    PLAY_AREA_HEIGHT,
    COLOR_BALL_LEFT,
    COLOR_BALL_OTHER,
)
from skunk.physics.vector2d import Vector2D
from skunk.model.simulation import Simulation
from skunk.gui.renderer import draw_background, draw_balls, draw_grass, draw_effects
from skunk.gui.effects import draw_slingshot
from skunk.gui.controls import Button, create_buttons, draw_status_bar
from skunk.gui.panel import BallPanel


SLINGSHOT_SCALE = 0.03  # drag pixels → velocity


def main() -> None:
    """Entry point for the bouncing ball simulation."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Skunk – Bouncing Ball Sim")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 13)

    sim = Simulation()
    # Spawn one initial ball going diagonal
    sim.spawn_ball(
        Vector2D(30.0, 30.0),
        COLOR_BALL_LEFT,
        Vector2D(2.0, 1.5),
    )

    buttons = create_buttons()
    panel = BallPanel()

    dragging = False
    drag_start: tuple[int, int] | None = None
    drag_button = 1  # 1=left, 2=middle
    drag_color = COLOR_BALL_LEFT

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        # Update hover states
        for btn in buttons.values():
            btn.update_hover(mouse_pos)
        panel.update_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # --- Keyboard ---
            if event.type == pygame.KEYDOWN:
                # Let panel consume keys first
                if panel.handle_key(event):
                    continue
                if event.key == pygame.K_SPACE:
                    sim.toggle_pause()
                    buttons["pause"].label = "Resume" if sim.paused else "Pause"
                    if not sim.paused:
                        panel.select(None)
                elif event.key == pygame.K_g:
                    sim.toggle_gravity()
                    buttons["gravity"].label = (
                        "Gravity On" if sim.gravity_on else "Gravity Off"
                    )
                elif event.key == pygame.K_r:
                    sim.reset()
                    panel.select(None)
                    buttons["pause"].label = "Pause"
                    buttons["gravity"].label = "Gravity Off"
                    sim.spawn_ball(
                        Vector2D(30.0, 30.0),
                        COLOR_BALL_LEFT,
                        Vector2D(2.0, 1.5),
                    )

            # --- Mouse button down ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Status bar button clicks
                if my >= PLAY_AREA_HEIGHT:
                    if buttons["pause"].is_clicked(event.pos):
                        sim.toggle_pause()
                        buttons["pause"].label = (
                            "Resume" if sim.paused else "Pause"
                        )
                        if not sim.paused:
                            panel.select(None)
                    elif buttons["reset"].is_clicked(event.pos):
                        sim.reset()
                        panel.select(None)
                        buttons["pause"].label = "Pause"
                        buttons["gravity"].label = "Gravity Off"
                        sim.spawn_ball(
                            Vector2D(30.0, 30.0),
                            COLOR_BALL_LEFT,
                            Vector2D(2.0, 1.5),
                        )
                    elif buttons["gravity"].is_clicked(event.pos):
                        sim.toggle_gravity()
                        buttons["gravity"].label = (
                            "Gravity On" if sim.gravity_on else "Gravity Off"
                        )
                    continue

                # Panel click
                if panel.handle_click(event.pos):
                    continue

                # Left click
                if event.button == 1:
                    mods = pygame.key.get_mods()
                    # Shift+click = shockwave
                    if mods & pygame.KMOD_SHIFT:
                        sim.apply_shockwave(Vector2D(float(mx), float(my)))
                        continue

                    # When paused, click on ball to select
                    if sim.paused:
                        hit = sim.ball_at(Vector2D(float(mx), float(my)))
                        if hit:
                            panel.select(hit)
                            continue
                        else:
                            panel.select(None)

                    # Start slingshot drag
                    dragging = True
                    drag_start = (mx, my)
                    drag_button = 1
                    drag_color = COLOR_BALL_LEFT

                # Middle click
                elif event.button == 2:
                    dragging = True
                    drag_start = (mx, my)
                    drag_button = 2
                    drag_color = COLOR_BALL_OTHER

            # --- Mouse button up ---
            if event.type == pygame.MOUSEBUTTONUP:
                if dragging and event.button in (1, 2) and drag_start is not None:
                    mx, my = event.pos
                    # Clamp to play area
                    my = min(my, PLAY_AREA_HEIGHT - 1)
                    dx = mx - drag_start[0]
                    dy = my - drag_start[1]
                    dist = (dx * dx + dy * dy) ** 0.5
                    if dist > 10:
                        # Slingshot velocity (opposite of drag direction)
                        vel = Vector2D(
                            -dx * SLINGSHOT_SCALE,
                            -dy * SLINGSHOT_SCALE,
                        )
                    else:
                        vel = None  # random velocity
                    spawn_pos = Vector2D(
                        float(drag_start[0]),
                        float(drag_start[1]),
                    )
                    sim.spawn_ball(spawn_pos, drag_color, vel)
                    dragging = False
                    drag_start = None

        # --- Update ---
        sim.update()

        # --- Render ---
        draw_background(screen, sim.gravity_on)
        draw_balls(screen, sim)
        if sim.gravity_on:
            draw_grass(screen)
        draw_effects(screen, sim)

        # Slingshot visual
        if dragging and drag_start is not None:
            draw_slingshot(screen, drag_start, mouse_pos)

        draw_status_bar(screen, sim, buttons, font)

        if panel.visible:
            panel.draw(screen, font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
