#!/usr/bin/env python3
"""
bouncing_balls.py

Pygame application: 800x450 "Bouncing Balls"
- White background, anti-aliased rendering via pygame.gfxdraw
- 40px diameter balls, move diagonally at 1 px per step
- 60 FPS main loop
- Edge bounce, pairwise collisions with specified rules
- Spawn on mouse click; left = #4B2E83, other buttons = #B7A57A
- Do not spawn if new ball would overlap existing ones
- Python 3.12+
"""

import sys
import random
import pygame
import pygame.gfxdraw

WIDTH = 800
HEIGHT = 450
FPS = 60
DIAMETER = 40
RADIUS = DIAMETER // 2
SPEED = 1  # pixels per animation step

COLOR_BG = (255, 255, 255)
COLOR_LEFT = tuple(int("4B2E83"[i:i+2], 16) for i in (0, 2, 4))
COLOR_OTHER = tuple(int("B7A57A"[i:i+2], 16) for i in (0, 2, 4))


class Ball:
    __slots__ = ("x", "y", "vx", "vy", "color")

    def __init__(self, x: float, y: float, vx: int, vy: int, color: tuple[int, int, int]):
        self.x = float(x)
        self.y = float(y)
        self.vx = int(vx)
        self.vy = int(vy)
        self.color = color

    def move(self):
        self.x += self.vx * SPEED
        self.y += self.vy * SPEED

    def check_wall(self):
        if self.x - RADIUS <= 0 and self.vx < 0:
            self.vx *= -1
            self.x = RADIUS
        elif self.x + RADIUS >= WIDTH and self.vx > 0:
            self.vx *= -1
            self.x = WIDTH - RADIUS

        if self.y - RADIUS <= 0 and self.vy < 0:
            self.vy *= -1
            self.y = RADIUS
        elif self.y + RADIUS >= HEIGHT and self.vy > 0:
            self.vy *= -1
            self.y = HEIGHT - RADIUS

    def draw(self, surf: pygame.Surface):
        xi = int(round(self.x))
        yi = int(round(self.y))
        pygame.gfxdraw.filled_circle(surf, xi, yi, RADIUS, self.color)
        pygame.gfxdraw.aacircle(surf, xi, yi, RADIUS, self.color)


def distance_sq(b1: Ball, b2: Ball) -> float:
    dx = b1.x - b2.x
    dy = b1.y - b2.y
    return dx * dx + dy * dy


def handle_collision(b1: Ball, b2: Ball):
    # Called when distance between centers <= DIAMETER
    vx_same = b1.vx == b2.vx
    vy_same = b1.vy == b2.vy

    if vx_same:
        b1.vy *= -1
        b2.vy *= -1

    if vy_same:
        b1.vx *= -1
        b2.vx *= -1

    if not vx_same and not vy_same:
        b1.vx *= -1
        b1.vy *= -1
        b2.vx *= -1
        b2.vy *= -1


def spawn_ball_at(balls: list[Ball], x: int, y: int, color: tuple[int, int, int]) -> bool:
    # Do not spawn if overlapping any existing ball (distance <= DIAMETER)
    for b in balls:
        dx = b.x - x
        dy = b.y - y
        if dx * dx + dy * dy <= DIAMETER * DIAMETER:
            return False

    vx = random.choice((-1, 1))
    vy = random.choice((-1, 1))
    balls.append(Ball(x, y, vx, vy, color))
    return True


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bouncing Balls")
    clock = pygame.time.Clock()

    balls: list[Ball] = []
    # Start with one ball in the upper-left corner (centered at radius, radius)
    balls.append(Ball(RADIUS, RADIUS, 1, 1, COLOR_LEFT))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                color = COLOR_LEFT if event.button == 1 else COLOR_OTHER
                spawn_ball_at(balls, mx, my, color)

        # Movement & wall check
        for b in balls:
            b.move()
            b.check_wall()

        # Pairwise collision checks
        n = len(balls)
        if n >= 2:
            for i in range(n):
                bi = balls[i]
                for j in range(i + 1, n):
                    bj = balls[j]
                    if distance_sq(bi, bj) <= DIAMETER * DIAMETER:
                        handle_collision(bi, bj)

        # Draw
        screen.fill(COLOR_BG)
        for b in balls:
            b.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
