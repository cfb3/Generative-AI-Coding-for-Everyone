# Generative AI: Coding for Everyone

A physics-based bouncing ball simulation built with Python and pygame. This project demonstrates how generative AI can be used as a collaborative coding partner to build interactive software — from a single-file prototype to a fully architected, tested application.

## What It Does

An interactive simulation where balls bounce around the screen with realistic physics:

- **Elastic collisions** with mass-based momentum transfer — bigger balls hit harder
- **Variable sizes and speeds** — each ball gets a random radius and velocity
- **Surface friction** that gradually slows balls to a stop
- **Gravity mode** — toggle gravity on to watch balls fall, bounce with decay, and roll to a stop on a grassy surface
- **Left wall boost** — balls accelerate when bouncing off the left wall (with a speed cap), indicated by an orange wall glow
- **Slingshot spawning** — click and drag to launch balls with a specific speed and direction
- **Shockwave** — Shift+click to send a radial burst that pushes all nearby balls
- **Ball editor** — pause the simulation and click a ball to edit its speed and direction
- **Energy display** — a status bar tracks the total kinetic energy in the system in real time

## Running the Simulation

**Requirements:** Python 3.12+, pygame

```bash
pip install pygame
python -m skunk
```

> **Having trouble?** If this doesn't work on your system, just ask Claude or ChatGPT to help you get it running!

## Controls

| Input | Action |
|---|---|
| Left click + drag | Slingshot spawn (purple ball) |
| Middle click + drag | Slingshot spawn (gold ball) |
| Shift + Left click | Shockwave |
| Space | Pause / Resume |
| G | Toggle gravity |
| R | Reset |
| Click ball (when paused) | Open ball editor panel |

## Architecture

The codebase follows a layered architecture with strict separation of concerns:

```
skunk/
├── physics/           ← Pure math, zero pygame dependency
│   ├── vector2d.py    Immutable 2D vector (frozen dataclass)
│   ├── collision.py   Circle overlap detection + elastic resolution
│   └── forces.py      Friction, gravity, air resistance, wall boost, shockwave
├── model/             ← Simulation state, zero pygame dependency
│   ├── ball.py        Ball entity (position, velocity, radius, mass)
│   └── simulation.py  Manages all balls, orchestrates physics each tick
├── gui/               ← All rendering and input handling
│   ├── app.py         Main loop + event dispatch
│   ├── renderer.py    Backgrounds, balls, grass tufts
│   ├── effects.py     Wall glow, shockwave burst lines, slingshot visual
│   ├── controls.py    Buttons + status bar with energy display
│   └── panel.py       Ball editor overlay (visible only when paused)
└── constants.py       All tunable parameters in one place
```

**Key design principles:**
- Physics and model layers have **no pygame imports** — they are pure Python and fully testable in isolation
- GUI layer only **reads** simulation state and renders — it never computes physics
- All tunable values (friction, gravity, speed caps, colors) live in `constants.py`

## Tests

144 pytest tests cover the physics and model layers:

```bash
pip install pytest
python -m pytest tests/ -v
```

Test coverage includes:
- Vector arithmetic, magnitude, normalization, dot product, angles
- Collision detection edge cases and elastic resolution with conservation laws
- All force calculations (friction, gravity, air resistance, wall boost, shockwave)
- Ball model properties, wall bounce logic, and factory methods
- Simulation state management (spawn, remove, reset, gravity, pause, shockwave, energy)

## Built With

- **Python 3.12+**
- **pygame** — rendering and input
- **pytest** — testing
- **Claude Code** — AI-assisted development
